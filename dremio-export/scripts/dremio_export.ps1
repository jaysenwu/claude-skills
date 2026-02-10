# PowerShell wrapper script for dremio_export.py that finds the correct Python installation

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScript = Join-Path $ScriptDir "dremio_export.py"

# Function to check if a Python executable has requests installed
function Test-PythonHasRequests {
    param($PythonPath)

    try {
        $result = & $PythonPath -c "import requests" 2>&1
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

# Try different Python installations in order of preference
$PythonCandidates = @(
    "python",
    "py",
    "python3",
    "C:\Python3\python.exe",
    "C:\Python39\python.exe",
    "C:\Python310\python.exe",
    "C:\Python311\python.exe",
    "C:\Python312\python.exe",
    "C:\Program Files\Python3\python.exe",
    "C:\Program Files\Python39\python.exe",
    "C:\Program Files\Python310\python.exe",
    "C:\Program Files\Python311\python.exe",
    "C:\Program Files\Python312\python.exe"
)

$PythonBin = $null
$TriedPythons = @()

foreach ($candidate in $PythonCandidates) {
    # Check if the command exists
    $pythonPath = Get-Command $candidate -ErrorAction SilentlyContinue

    if ($pythonPath) {
        $actualPath = $pythonPath.Source
        if (Test-PythonHasRequests $actualPath) {
            $PythonBin = $actualPath
            break
        }
        else {
            $TriedPythons += "$actualPath (requests not installed)"
        }
    }
}

# If no Python with requests found, show error
if (-not $PythonBin) {
    Write-Host "ERROR: No Python installation with 'requests' package found." -ForegroundColor Red
    Write-Host ""

    if ($TriedPythons.Count -gt 0) {
        Write-Host "Tried the following Python installations:" -ForegroundColor Yellow
        foreach ($tried in $TriedPythons) {
            Write-Host "  - $tried"
        }
        Write-Host ""
    }

    Write-Host "Please install the requests package:" -ForegroundColor Yellow
    Write-Host "  pip install requests"
    Write-Host ""
    Write-Host "Or if using Python from Microsoft Store:" -ForegroundColor Yellow
    Write-Host "  python -m pip install requests"
    exit 1
}

# Run the Python script with the correct interpreter
& $PythonBin $PythonScript $args
