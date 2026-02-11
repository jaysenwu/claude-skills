# SQL Server View Export Skill

A Claude Code skill for exporting views from Microsoft SQL Server to CSV format using direct Python connection.

## Features

- **List Views**: Display all views in a SQL Server database
- **Search Views**: Find views by keyword (schema or view name)
- **Export Single View**: Export one view to CSV with configurable output path
- **Batch Export**: Export multiple views to separate CSV files in one command

## Quick Start

### 1. Prerequisites

Install required Python packages:
```bash
pip install pyodbc pandas
```

Install Microsoft ODBC Driver 18 for SQL Server:
- **Windows**: [Download here](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- **macOS**: `brew install msodbcsql18`
- **Linux**: See [troubleshooting.md](references/troubleshooting.md) for instructions

### 2. Configuration

Create a `.env` file in your working directory:

```bash
SQL_SERVER=localhost
SQL_DATABASE=MyDatabase
SQL_USER=sa
SQL_PASSWORD=YourPassword
SQL_PORT=1433
TRUST_SERVER_CERTIFICATE=Yes
OUTPUT_DIR=./exports
```

See [env-template.txt](references/env-template.txt) for a complete template.

### 3. Usage

The skill is automatically available in Claude Code. Just ask Claude to:
- "List all SQL Server views"
- "Search for views containing 'sales'"
- "Export the dbo.CustomerView to CSV"
- "Batch export dbo.SalesView and dbo.ProductView"

## Manual Usage

You can also run the scripts directly:

### Windows (PowerShell)
```powershell
# List all views
~\.claude\skills\sqlserver-view-export\scripts\sqlserver_view_export.ps1 list

# Search for views
~\.claude\skills\sqlserver-view-export\scripts\sqlserver_view_export.ps1 search sales

# Export single view
~\.claude\skills\sqlserver-view-export\scripts\sqlserver_view_export.ps1 export dbo.CustomerView

# Batch export
~\.claude\skills\sqlserver-view-export\scripts\sqlserver_view_export.ps1 batch-export dbo.View1 dbo.View2
```

### macOS/Linux
```bash
# List all views
~/.claude/skills/sqlserver-view-export/scripts/sqlserver_view_export.sh list

# Export view
~/.claude/skills/sqlserver-view-export/scripts/sqlserver_view_export.sh export dbo.CustomerView
```

## Directory Structure

```
sqlserver-view-export/
├── SKILL.md                          # Main skill documentation
├── README.md                         # This file
├── scripts/
│   ├── sqlserver_view_export.py     # Main Python script
│   ├── sqlserver_view_export.bat    # Windows CMD wrapper
│   ├── sqlserver_view_export.ps1    # Windows PowerShell wrapper
│   └── sqlserver_view_export.sh     # macOS/Linux wrapper
└── references/
    ├── env-template.txt             # Configuration template
    └── troubleshooting.md           # Troubleshooting guide
```

## How It Works

1. **Direct Python Connection**: Uses `pyodbc` to connect directly to SQL Server (no MCP server required)
2. **View Discovery**: Queries system views (`sys.views`, `sys.schemas`) to list available views
3. **Efficient Export**: Uses `pandas` for fast CSV export with proper encoding
4. **Multi-Platform**: Works on Windows, macOS, and Linux with appropriate wrappers

## Differences from mssql-mcp Skill

| Feature | sqlserver-view-export | mssql-mcp |
|---------|----------------------|-----------|
| **Architecture** | Direct Python connection | MCP server |
| **Setup** | Python + pyodbc | Node.js + MCP server |
| **Focus** | View listing & CSV export | Full SQL operations (CRUD) |
| **Use Case** | Quick data exports | Database management |
| **Dependencies** | pyodbc, pandas | @modelcontextprotocol/server-mssql |

## Authentication

**Supported**: SQL Server Authentication (username/password)
**Not Supported**: Windows Authentication (may be added in future)

To enable SQL Server Authentication:
1. Open SQL Server Management Studio (SSMS)
2. Server Properties → Security
3. Enable "SQL Server and Windows Authentication mode"
4. Restart SQL Server service

## CSV Output

- **Encoding**: UTF-8 with BOM (Excel-compatible)
- **Headers**: Column names in first row
- **NULL values**: Empty cells
- **Special characters**: Properly escaped
- **Large datasets**: Efficiently handled by pandas

## Troubleshooting

See [troubleshooting.md](references/troubleshooting.md) for detailed guidance on:
- ODBC driver installation
- Connection issues
- Certificate errors
- Authentication problems
- Performance optimization

## Security Considerations

- Never commit `.env` files to version control
- Use strong passwords for SQL Server authentication
- Consider read-only database roles for export users
- Use `TRUST_SERVER_CERTIFICATE=No` in production with valid SSL certificates
- Store credentials securely with appropriate file permissions

## Performance Tips

For large views (>1M rows):
- Export may take several minutes
- Consider filtering in the view definition
- Monitor memory usage
- Use batch export for multiple views

## Contributing

To modify this skill:
1. Edit files in `C:\Users\JSW023\.claude\skills\sqlserver-view-export\`
2. Test changes with your SQL Server instance
3. Update documentation as needed

## License

This skill is part of Claude Code and follows the same license terms.

## Support

For issues and questions:
- Check [troubleshooting.md](references/troubleshooting.md)
- Review [SKILL.md](SKILL.md) for usage instructions
- Consult the [Microsoft ODBC Driver documentation](https://learn.microsoft.com/en-us/sql/connect/odbc/)
