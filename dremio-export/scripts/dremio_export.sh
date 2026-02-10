#!/bin/bash
# Wrapper script for dremio_export.py that finds the correct Python installation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/dremio_export.py"

# Function to check if a Python executable has requests installed
has_requests() {
    "$1" -c "import requests" 2>/dev/null
    return $?
}

# Try different Python installations in order of preference
PYTHON_CANDIDATES=(
    "/opt/homebrew/bin/python3"
    "/usr/local/bin/python3"
    "/usr/bin/python3"
    "python3"
)

PYTHON_BIN=""
for candidate in "${PYTHON_CANDIDATES[@]}"; do
    if command -v "$candidate" >/dev/null 2>&1; then
        if has_requests "$candidate"; then
            PYTHON_BIN="$candidate"
            break
        fi
    fi
done

# If no Python with requests found, show error
if [ -z "$PYTHON_BIN" ]; then
    echo "ERROR: No Python installation with 'requests' package found."
    echo ""
    echo "Tried the following Python installations:"
    for candidate in "${PYTHON_CANDIDATES[@]}"; do
        if command -v "$candidate" >/dev/null 2>&1; then
            echo "  - $candidate (requests not installed)"
        fi
    done
    echo ""
    echo "Please install the requests package:"
    echo "  pip3 install requests"
    echo "Or on macOS with Homebrew Python:"
    echo "  /opt/homebrew/bin/python3 -m pip install --break-system-packages requests"
    exit 1
fi

# Run the Python script with the correct interpreter
exec "$PYTHON_BIN" "$PYTHON_SCRIPT" "$@"
