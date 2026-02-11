# Windows Setup Guide for Dremio Export Skill

This guide explains how to copy and use the dremio-export skill on Windows.

## Quick Setup

### 1. Copy the skill folder to Windows

Copy the entire `dremio-export` folder to your Windows Claude skills directory:

```
C:\Users\<YourUsername>\.claude\skills\dremio-export\
```

The folder structure should look like:
```
.claude\
└── skills\
    └── dremio-export\
        ├── SKILL.md
        ├── WINDOWS_SETUP.md (this file)
        └── scripts\
            ├── dremio_export.py
            ├── dremio_export.sh (for macOS/Linux)
            ├── dremio_export.bat (for Windows CMD)
            └── dremio_export.ps1 (for Windows PowerShell)
```

### 2. Install Python and requests package

Make sure you have Python installed on Windows:

**Option A: Microsoft Store (Recommended)**
1. Open Microsoft Store
2. Search for "Python 3.12" (or latest version)
3. Click Install

**Option B: Python.org**
1. Download from https://www.python.org/downloads/
2. Run installer and check "Add Python to PATH"

**Install the requests package:**
```cmd
pip install requests
```

### 3. Configure .env file

Create a `.env` file in your project directory:
```
DREMIO_BASE_URL=https://your-dremio-server.com
DREMIO_API_KEY=your_personal_access_token
```

### 4. Run the skill

**PowerShell (Recommended):**
```powershell
~\.claude\skills\dremio-export\scripts\dremio_export.ps1 "my_space.my_view"
```

**Command Prompt:**
```cmd
%USERPROFILE%\.claude\skills\dremio-export\scripts\dremio_export.bat "my_space.my_view"
```

## Key Differences from macOS/Linux

| Aspect | macOS/Linux | Windows |
|--------|-------------|---------|
| **Wrapper script** | `.sh` (bash) | `.bat` (CMD) or `.ps1` (PowerShell) |
| **Path separator** | `/` | `\` |
| **Home directory** | `~` or `$HOME` | `%USERPROFILE%` or `~` (PowerShell) |
| **Python command** | `python3` | `python` or `py` |
| **Skill directory** | `~/.claude/skills/` | `%USERPROFILE%\.claude\skills\` |

## Troubleshooting

### PowerShell execution policy error

If you see "script cannot be loaded because running scripts is disabled":

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python not found

1. Check if Python is installed: `python --version`
2. If not installed, install from Microsoft Store or Python.org
3. Make sure Python is in your PATH

### requests package not found

Install it with:
```cmd
python -m pip install requests
```

Or if you have multiple Python versions:
```cmd
py -3 -m pip install requests
```

## No Changes Needed

The following files work on both Windows and macOS/Linux without modification:
- `dremio_export.py` - The main Python script
- `SKILL.md` - Documentation (already includes Windows examples)
- `.env` file format

## Testing

Test the installation by running:

```powershell
# PowerShell
~\.claude\skills\dremio-export\scripts\dremio_export.ps1 --help
```

```cmd
rem Command Prompt
%USERPROFILE%\.claude\skills\dremio-export\scripts\dremio_export.bat --help
```

You should see usage information if everything is set up correctly.
