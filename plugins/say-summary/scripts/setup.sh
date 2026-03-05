#!/bin/bash
# Setup script for say-summary plugin
# Creates a virtualenv and installs required Python dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"

echo "Setting up say-summary plugin..."

# Check if python3 is available and is version 3.10+
if ! python3 -c 'import sys; assert sys.version_info >= (3, 10)' &>/dev/null; then
    echo "Error: Python 3.10+ is required. Please install a compatible version of Python 3."
    exit 1
fi

# Create virtualenv if it doesn't exist
if [ ! -d "${VENV_DIR}" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "${VENV_DIR}"
fi

# Activate and install dependencies
echo "Installing dependencies..."
"${VENV_DIR}/bin/pip" install --upgrade pip
"${VENV_DIR}/bin/pip" install -r "${SCRIPT_DIR}/../requirements.txt"

echo ""
echo "Done! Plugin is ready to use."
echo "Note: This plugin requires macOS (uses the 'say' command for TTS)."
