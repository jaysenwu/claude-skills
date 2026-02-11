# Troubleshooting Guide: SQL Server View Export

## Common Issues and Solutions

### 1. ODBC Driver Not Found

**Error:**
```
ERROR: 'pyodbc' package not found. Install with: pip install pyodbc
```
or
```
ERROR: Failed to connect to SQL Server
Error details: ('01000', "[01000] [unixODBC][Driver Manager]Can't open lib 'ODBC Driver 18 for SQL Server'")
```

**Solution:**

#### Windows:
1. Download and install [Microsoft ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
2. Alternatively, install ODBC Driver 17:
   ```
   https://www.microsoft.com/en-us/download/details.aspx?id=56567
   ```
3. Update the script to use Driver 17 if needed:
   - Edit `sqlserver_view_export.py`
   - Change `ODBC Driver 18 for SQL Server` to `ODBC Driver 17 for SQL Server`

#### macOS:
```bash
brew install unixodbc
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew install msodbcsql18
```

#### Linux (Ubuntu/Debian):
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
```

---

### 2. Connection Timeout or Refused

**Error:**
```
ERROR: Failed to connect to SQL Server
Error details: ('08001', '[08001] [Microsoft][ODBC Driver 18 for SQL Server]...')
```

**Solutions:**

1. **Check SQL Server is Running:**
   - Open SQL Server Configuration Manager
   - Verify SQL Server service is running
   - Check TCP/IP protocol is enabled

2. **Verify Server Name:**
   - For named instances: `ServerName\InstanceName`
   - For default instance: `ServerName` or `ServerName,1433`
   - Test connection: `ping ServerName`

3. **Check Firewall:**
   - Windows Firewall may block SQL Server port 1433
   - Add inbound rule for port 1433
   - Or add exception for `sqlservr.exe`

4. **Enable Remote Connections:**
   - Open SQL Server Management Studio (SSMS)
   - Right-click server → Properties → Connections
   - Check "Allow remote connections to this server"

---

### 3. Certificate Verification Errors

**Error:**
```
[Microsoft][ODBC Driver 18 for SQL Server]SSL Provider: The certificate chain was issued by an authority that is not trusted
```

**Solution:**

In your `.env` file, set:
```
TRUST_SERVER_CERTIFICATE=Yes
```

This is common in development environments with self-signed certificates.

For production, use proper SSL certificates and set:
```
TRUST_SERVER_CERTIFICATE=No
```

---

### 4. Authentication Failures

**Error:**
```
ERROR: Failed to connect to SQL Server
Error details: ('28000', "[28000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Login failed for user 'username'")
```

**Solutions:**

1. **Check SQL Server Authentication Mode:**
   - Open SSMS
   - Right-click server → Properties → Security
   - Ensure "SQL Server and Windows Authentication mode" is enabled
   - Restart SQL Server service after changing

2. **Verify User Credentials:**
   - Test login in SSMS with same credentials
   - Check username and password in `.env` file
   - Ensure user has access to the target database

3. **For Windows Authentication:**
   - Windows Authentication requires `Trusted_Connection=Yes` in connection string
   - Currently not supported by this script (SQL auth only)
   - Consider using SQL Server authentication instead

---

### 5. View Not Found

**Error:**
```
ERROR: Failed to query view 'dbo.MyView': ('42S02', "[42S02] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]Invalid object name 'dbo.MyView'.")
```

**Solutions:**

1. **Check View Name:**
   - Use `list` command to see all available views
   - Verify schema name (e.g., `dbo.ViewName` not just `ViewName`)

2. **Verify Database:**
   - Ensure you're connected to the correct database in `.env`
   - Views in other databases won't be visible

3. **Check Permissions:**
   - User must have SELECT permission on the view
   - Grant permission in SSMS:
     ```sql
     GRANT SELECT ON dbo.ViewName TO [username];
     ```

---

### 6. Permission Denied

**Error:**
```
ERROR: Failed to list views: ('42000', "[42000] [Microsoft][ODBC Driver 18 for SQL Server][SQL Server]SELECT permission denied on object 'views'...")
```

**Solution:**

Grant necessary permissions to the user:

```sql
-- Grant permission to read system views
GRANT VIEW DEFINITION TO [username];

-- Or assign db_datareader role
ALTER ROLE db_datareader ADD MEMBER [username];
```

---

### 7. Large Dataset Export Issues

**Symptoms:**
- Export hangs or runs very slowly
- Out of memory errors
- CSV file is incomplete

**Solutions:**

1. **Check View Row Count:**
   ```sql
   SELECT COUNT(*) FROM dbo.YourView;
   ```

2. **For Large Views (>1M rows):**
   - Export in chunks using WHERE clauses
   - Consider adding indexes to the underlying tables
   - Increase available memory

3. **Optimize pandas Usage:**
   - Script already uses efficient pandas.read_sql()
   - For extremely large datasets, consider using chunksize parameter

---

### 8. CSV Encoding Issues

**Symptoms:**
- Special characters appear as � or gibberish
- Excel doesn't display non-ASCII characters correctly

**Solution:**

The script uses `utf-8-sig` encoding (UTF-8 with BOM) for Excel compatibility. If issues persist:

1. **Open CSV in Excel:**
   - Use "Data" → "From Text/CSV"
   - Select "UTF-8" as encoding
   - This preserves special characters

2. **For Other Applications:**
   - Most modern applications support UTF-8
   - Verify the application's import settings

---

### 9. Port Number Issues

**Error:**
```
ERROR: Failed to connect to SQL Server
[Server name is invalid or not reachable]
```

**Solution:**

1. **Find SQL Server Port:**
   ```powershell
   # In SQL Server Configuration Manager
   # Navigate to: SQL Server Network Configuration → Protocols for [INSTANCE]
   # Double-click TCP/IP → IP Addresses tab
   # Look for TCP Dynamic Ports or TCP Port
   ```

2. **For Dynamic Ports:**
   - Named instances often use dynamic ports
   - Use SQL Server Browser service
   - Or specify port explicitly: `ServerName\InstanceName,PortNumber`

3. **Update .env File:**
   ```
   SQL_SERVER=myserver\SQLEXPRESS
   SQL_PORT=1433
   ```
   or
   ```
   SQL_SERVER=myserver\SQLEXPRESS,49152
   ```

---

## Performance Tips

### 1. Index Underlying Tables
```sql
-- Create indexes on frequently filtered columns
CREATE INDEX IX_ColumnName ON TableName(ColumnName);
```

### 2. Limit Export Columns
Modify the script query to select only needed columns:
```python
query = f"SELECT col1, col2, col3 FROM {full_name}"
```

### 3. Use Views Wisely
- Avoid SELECT * in view definitions
- Pre-filter data in the view when possible
- Consider materialized views for large datasets

---

## Getting Help

### Check ODBC Driver Version
```python
import pyodbc
print(pyodbc.drivers())
```

### Test Connection String
```python
import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost,1433;"
    "DATABASE=MyDB;"
    "UID=sa;"
    "PWD=password;"
    "TrustServerCertificate=Yes;"
)

try:
    conn = pyodbc.connect(conn_str)
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
```

### Enable Verbose Logging
Add to the top of the Python script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Additional Resources

- [Microsoft ODBC Driver Documentation](https://learn.microsoft.com/en-us/sql/connect/odbc/microsoft-odbc-driver-for-sql-server)
- [pyodbc Documentation](https://github.com/mkleehammer/pyodbc/wiki)
- [SQL Server Connection Strings](https://www.connectionstrings.com/sql-server/)
- [pandas DataFrame.to_csv Documentation](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html)
