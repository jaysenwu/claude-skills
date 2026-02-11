---
name: sqlserver-view-export
description: "Export views from MS SQL Server to CSV format with direct Python connection. Use when the user wants to: connect to SQL Server, list SQL Server views, search for views, export view data to CSV, download SQL Server view data, batch export multiple views, or any mention of SQL Server with view export/listing/searching."
---

# SQL Server View Export

Export views from Microsoft SQL Server to CSV format using a direct Python connection. List available views, search by keyword, and perform single or batch exports.

## Prerequisites

A `.env` file in the current working directory with:

```
SQL_SERVER=localhost
SQL_DATABASE=MyDatabase
SQL_USER=sa
SQL_PASSWORD=YourPassword
SQL_PORT=1433
TRUST_SERVER_CERTIFICATE=Yes
OUTPUT_DIR=./exports
```

See `references/env-template.txt` for a complete configuration template.

**Required Python packages:**
- `pyodbc` - SQL Server connectivity
- `pandas` - CSV export and data manipulation

**System requirements:**
- Microsoft ODBC Driver 17 or 18 for SQL Server
- Python 3.7+

See `references/troubleshooting.md` for installation instructions and common issues.

## Workflow

### List views
1. Verify `.env` exists in the working directory. If missing, ask the user to create one using the template in `references/env-template.txt`
2. Run the list command using the appropriate wrapper for your OS:

**macOS/Linux:**
```bash
~/.claude/skills/sqlserver-view-export/scripts/sqlserver_view_export.sh list [--env /path/to/.env]
```

**Windows (PowerShell):**
```powershell
~\.claude\skills\sqlserver-view-export\scripts\sqlserver_view_export.ps1 list [--env /path/to/.env]
```

**Windows (Command Prompt):**
```cmd
%USERPROFILE%\.claude\skills\sqlserver-view-export\scripts\sqlserver_view_export.bat list [--env /path/to/.env]
```

3. Display the results to the user in a readable format

### Search views
1. If the user wants to find views by keyword, use the `search` subcommand
2. Verify `.env` exists in the working directory

**macOS/Linux:**
```bash
~/.claude/skills/sqlserver-view-export/scripts/sqlserver_view_export.sh search <keyword> [--env /path/to/.env]
```

**Windows (PowerShell):**
```powershell
~\.claude\skills\sqlserver-view-export\scripts\sqlserver_view_export.ps1 search <keyword> [--env /path/to/.env]
```

3. Display the matching views to the user

### Export single view
1. If the user has not specified a view name, ask for it
2. Verify `.env` exists in the working directory
3. Run the export script:

**macOS/Linux:**
```bash
~/.claude/skills/sqlserver-view-export/scripts/sqlserver_view_export.sh export <view_name> [output_file] [--env /path/to/.env]
```

**Windows (PowerShell):**
```powershell
~\.claude\skills\sqlserver-view-export\scripts\sqlserver_view_export.ps1 export <view_name> [output_file] [--env /path/to/.env]
```

**Windows (Command Prompt):**
```cmd
%USERPROFILE%\.claude\skills\sqlserver-view-export\scripts\sqlserver_view_export.bat export <view_name> [output_file] [--env /path/to/.env]
```

4. Report results to the user: row count and output file path

### Batch export multiple views
1. If the user wants to export multiple views at once, use the `batch-export` subcommand
2. Verify `.env` exists in the working directory
3. Run the batch export:

**macOS/Linux:**
```bash
~/.claude/skills/sqlserver-view-export/scripts/sqlserver_view_export.sh batch-export <view1> <view2> ... [--env /path/to/.env]
```

**Windows (PowerShell):**
```powershell
~\.claude\skills\sqlserver-view-export\scripts\sqlserver_view_export.ps1 batch-export <view1> <view2> ... [--env /path/to/.env]
```

4. Report summary: successful exports, failed exports, output directory

## Commands

### `list`

List all views in the database.

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--env` | No | `.env` | Path to `.env` file |

### `search`

Search for views by keyword (matches schema or view name).

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `keyword` | Yes | — | Search keyword |
| `--env` | No | `.env` | Path to `.env` file |

### `export`

Export a single view to CSV.

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `view_name` | Yes | — | View name (e.g. `dbo.CustomerView`) |
| `output_file` | No | `{view_name}.csv` | Output CSV file path |
| `--env` | No | `.env` | Path to `.env` file |

### `batch-export`

Export multiple views to separate CSV files.

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `view_names` | Yes | — | Space-separated view names |
| `--env` | No | `.env` | Path to `.env` file |

## Examples

### macOS/Linux

List all views:
```bash
~/.claude/skills/sqlserver-view-export/scripts/sqlserver_view_export.sh list
```

Search for views containing "sales":
```bash
~/.claude/skills/sqlserver-view-export/scripts/sqlserver_view_export.sh search sales
```

Export single view:
```bash
~/.claude/skills/sqlserver-view-export/scripts/sqlserver_view_export.sh export dbo.CustomerView
```

Export with custom output path:
```bash
~/.claude/skills/sqlserver-view-export/scripts/sqlserver_view_export.sh export dbo.CustomerView customers.csv
```

Batch export multiple views:
```bash
~/.claude/skills/sqlserver-view-export/scripts/sqlserver_view_export.sh batch-export dbo.SalesView dbo.ProductView dbo.CustomerView
```

### Windows (PowerShell)

List all views:
```powershell
~\.claude\skills\sqlserver-view-export\scripts\sqlserver_view_export.ps1 list
```

Search for views:
```powershell
~\.claude\skills\sqlserver-view-export\scripts\sqlserver_view_export.ps1 search sales
```

Export single view:
```powershell
~\.claude\skills\sqlserver-view-export\scripts\sqlserver_view_export.ps1 export dbo.CustomerView
```

Batch export:
```powershell
~\.claude\skills\sqlserver-view-export\scripts\sqlserver_view_export.ps1 batch-export dbo.SalesView dbo.ProductView
```

### Windows (Command Prompt)

List all views:
```cmd
%USERPROFILE%\.claude\skills\sqlserver-view-export\scripts\sqlserver_view_export.bat list
```

Export single view:
```cmd
%USERPROFILE%\.claude\skills\sqlserver-view-export\scripts\sqlserver_view_export.bat export dbo.CustomerView
```

## Configuration

### Connection Parameters

**Required:**
- `SQL_SERVER` - Server hostname/IP (e.g., `localhost`, `192.168.1.100`, `myserver\SQLEXPRESS`)
- `SQL_DATABASE` - Database name
- `SQL_USER` - Username for SQL Server authentication
- `SQL_PASSWORD` - Password

**Optional:**
- `SQL_PORT` - Port number (default: `1433`)
- `TRUST_SERVER_CERTIFICATE` - `Yes` or `No` (default: `Yes` for self-signed certs)
- `OUTPUT_DIR` - Output directory for CSV files (default: `./exports`)

### Authentication

The script currently supports **SQL Server Authentication** only. Windows Authentication is not supported.

To enable SQL Server Authentication:
1. Open SQL Server Management Studio (SSMS)
2. Right-click server → Properties → Security
3. Select "SQL Server and Windows Authentication mode"
4. Restart SQL Server service

## Error Handling

The script provides clear error messages for:
- **Missing `.env` or variables**: Shows which variables are missing
- **ODBC driver not found**: Provides installation instructions
- **Connection errors**: Suggests checking server name, credentials, and firewall
- **View not found**: Shows available views with `list` command
- **Permission denied**: Explains required SQL Server permissions
- **Certificate errors**: Suggests using `TRUST_SERVER_CERTIFICATE=Yes`

## Troubleshooting

See `references/troubleshooting.md` for detailed troubleshooting guidance, including:
- ODBC driver installation (Windows, macOS, Linux)
- Connection timeout issues
- Certificate verification errors
- Authentication failures
- Permission problems
- Performance optimization tips

### Quick Fixes

**ODBC Driver Not Found (Windows):**
1. Download [Microsoft ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
2. Install the driver
3. Restart your terminal/IDE

**Connection Timeout:**
1. Verify SQL Server is running
2. Check TCP/IP protocol is enabled in SQL Server Configuration Manager
3. Verify firewall allows port 1433
4. Test with: `telnet <server> 1433`

**Certificate Error:**
Add to your `.env` file:
```
TRUST_SERVER_CERTIFICATE=Yes
```

**Missing Python Packages:**
```bash
pip install pyodbc pandas
```

## CSV Output Details

- **Encoding**: UTF-8 with BOM (Excel-compatible)
- **NULL values**: Exported as empty cells
- **Column headers**: Included in first row
- **File naming**: Auto-generated from view name (e.g., `CustomerView.csv`)
- **Output directory**: Configurable via `OUTPUT_DIR` in `.env`

## Performance Considerations

For large views (>1M rows):
- Export may take several minutes
- Consider filtering the view or adding WHERE clauses
- Monitor memory usage during export
- Use batch export for multiple small views rather than one large query

## Security Notes

- Store `.env` files securely with appropriate file permissions
- Never commit `.env` files to version control
- Use strong passwords for SQL Server authentication
- Consider using read-only database roles for export users
- Enable SSL/TLS in production environments
