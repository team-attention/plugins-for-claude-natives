#!/bin/bash
# Setup script for say-summary plugin
# Installs required Python dependencies

set -e

echo "Installing say-summary plugin dependencies..."

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install Python 3 first."
    exit 1
fi

# Install claude-agent-sdk
pip3 install --user claude-agent-sdk

echo "Done! Plugin is ready to use."
echo ""
echo "Note: This plugin requires macOS (uses the 'say' command for TTS)."
