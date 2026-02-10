---
name: dremio-export
description: "Export data from Dremio Software (self-hosted) to CSV, list available views, and search for views by keyword. Use when the user wants to: export Dremio data to CSV, query Dremio views or tables, download data from Dremio, list Dremio views, show available Dremio views, search for Dremio views, find a Dremio view, or any mention of Dremio with data export/listing/searching."
---

# Dremio Export

Export data from a self-hosted Dremio Software instance to CSV, list available views, and search for views by keyword.

## Prerequisites

A `.env` file in the current working directory with:

```
DREMIO_BASE_URL=http://localhost:9047
DREMIO_API_KEY=your_personal_access_token
```

Python 3 with the `requests` package must be installed. The wrapper script will automatically detect the correct Python installation.

## Workflow

### Export (default)
1. If the user has not specified a view name, ask for it
2. Verify `.env` exists in the working directory. If missing, ask the user to create one (a `.env.example` template may exist in the project)
3. Run the export script using the appropriate wrapper for your OS:

**macOS/Linux:**
```bash
~/.claude/skills/dremio-export/scripts/dremio_export.sh export "<view_name>" [output_file] [--env /path/to/.env] [--timeout 300]
```

**Windows (PowerShell):**
```powershell
~\.claude\skills\dremio-export\scripts\dremio_export.ps1 export "<view_name>" [output_file] [--env /path/to/.env] [--timeout 300]
```

**Windows (Command Prompt):**
```cmd
%USERPROFILE%\.claude\skills\dremio-export\scripts\dremio_export.bat export "<view_name>" [output_file] [--env /path/to/.env] [--timeout 300]
```

Note: The `export` subcommand is optional for backward compatibility — `dremio_export.sh my_space.my_view` still works.

4. Report results to the user: row count, column count, output file path

### List views
1. If the user wants to browse available views, use the `list` subcommand
2. Verify `.env` exists in the working directory

**macOS/Linux:**
```bash
~/.claude/skills/dremio-export/scripts/dremio_export.sh list [path] [--recursive] [--env /path/to/.env]
```

**Windows (PowerShell):**
```powershell
~\.claude\skills\dremio-export\scripts\dremio_export.ps1 list [path] [--recursive] [--env /path/to/.env]
```

3. Display the results to the user in a readable format

### Search views
1. If the user wants to find a view by keyword, use the `search` subcommand
2. Verify `.env` exists in the working directory

**macOS/Linux:**
```bash
~/.claude/skills/dremio-export/scripts/dremio_export.sh search <keyword> [--env /path/to/.env]
```

**Windows (PowerShell):**
```powershell
~\.claude\skills\dremio-export\scripts\dremio_export.ps1 search <keyword> [--env /path/to/.env]
```

3. Display the matching views to the user

## Commands

### `export` (default)

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `view_name` | Yes | — | Dremio view path, e.g. `my_space.my_view` |
| `output_file` | No | `{view_name}.csv` | Output CSV file path |
| `--env` | No | `.env` | Path to `.env` file |
| `--timeout` | No | `300` | Query timeout in seconds |

### `list`

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `path` | No | (root) | Container path (space/folder), e.g. `my_space` |
| `--recursive`, `-r` | No | `false` | Recursively list all items in sub-containers |
| `--env` | No | `.env` | Path to `.env` file |

### `search`

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `keyword` | Yes | — | Search keyword (matches view and schema names) |
| `--env` | No | `.env` | Path to `.env` file |

## Examples

### macOS/Linux

Basic export:
```bash
~/.claude/skills/dremio-export/scripts/dremio_export.sh export my_space.sales_data
```

Custom output path:
```bash
~/.claude/skills/dremio-export/scripts/dremio_export.sh export my_space.sales_data sales_export.csv
```

Nested view with spaces:
```bash
~/.claude/skills/dremio-export/scripts/dremio_export.sh export '"My Space"."Q4 Report"' q4_report.csv
```

List root spaces/sources:
```bash
~/.claude/skills/dremio-export/scripts/dremio_export.sh list
```

List views in a specific space:
```bash
~/.claude/skills/dremio-export/scripts/dremio_export.sh list my_space
```

Recursively list all views:
```bash
~/.claude/skills/dremio-export/scripts/dremio_export.sh list my_space --recursive
```

Search for views containing "sales":
```bash
~/.claude/skills/dremio-export/scripts/dremio_export.sh search sales
```

### Windows (PowerShell)

Basic export:
```powershell
~\.claude\skills\dremio-export\scripts\dremio_export.ps1 export my_space.sales_data
```

Custom output path:
```powershell
~\.claude\skills\dremio-export\scripts\dremio_export.ps1 export my_space.sales_data sales_export.csv
```

List views in a space:
```powershell
~\.claude\skills\dremio-export\scripts\dremio_export.ps1 list my_space
```

Search for views:
```powershell
~\.claude\skills\dremio-export\scripts\dremio_export.ps1 search sales
```

### Windows (Command Prompt)

Basic export:
```cmd
%USERPROFILE%\.claude\skills\dremio-export\scripts\dremio_export.bat export my_space.sales_data
```

Custom output path:
```cmd
%USERPROFILE%\.claude\skills\dremio-export\scripts\dremio_export.bat export my_space.sales_data sales_export.csv
```

## Error Handling

The script exits with clear messages for:
- **Missing `.env` or variables**: tells user which variables are missing
- **Connection errors**: suggests checking `DREMIO_BASE_URL` and that Dremio is running
- **Auth failures**: suggests checking `DREMIO_API_KEY`
- **Query failures**: shows Dremio's error message (e.g. table not found)
- **Timeouts**: shows elapsed time and suggests increasing `--timeout`

## Troubleshooting

### Python and requests package

The wrapper scripts automatically detect the correct Python installation:

**macOS/Linux** (`dremio_export.sh`):
1. Homebrew Python: `/opt/homebrew/bin/python3`
2. User-installed Python: `/usr/local/bin/python3`
3. System Python: `/usr/bin/python3`
4. Default Python: `python3` in PATH

**Windows** (`dremio_export.bat` or `dremio_export.ps1`):
1. Default Python: `python` or `py` in PATH
2. Standard installations: `C:\Python3X\python.exe`
3. Program Files installations: `C:\Program Files\Python3X\python.exe`

The scripts test each Python installation for the `requests` package and use the first one that has it installed.

If the wrapper cannot find a suitable Python installation, it will show:
- Which Python installations it found
- Which ones are missing the `requests` package
- Instructions to install `requests`

**Installing requests:**

macOS with Homebrew Python:
```bash
/opt/homebrew/bin/python3 -m pip install --break-system-packages requests
```

Windows:
```cmd
pip install requests
# or
python -m pip install requests
```

### Windows-specific notes

1. **PowerShell Execution Policy**: If you get an execution policy error when running `.ps1` scripts, you may need to allow script execution:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Path separators**: Windows uses backslashes (`\`) instead of forward slashes (`/`) in paths

3. **Home directory**:
   - Windows: `%USERPROFILE%` or `~` (in PowerShell)
   - macOS/Linux: `~` or `$HOME`
