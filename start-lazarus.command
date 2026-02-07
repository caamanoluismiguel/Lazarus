#!/bin/bash
# ═══════════════════════════════════════════════════════
# Project Lazarus — One-Click Launcher for macOS
# Double-click this file in Finder to start everything.
# ═══════════════════════════════════════════════════════

# Go to the folder where this script lives
cd "$(dirname "$0")"

clear
echo ""
echo "  ┌─────────────────────────────────────────┐"
echo "  │       PROJECT LAZARUS — Starting...      │"
echo "  └─────────────────────────────────────────┘"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "  ⚠  Python 3 not found!"
    echo "     Install it: https://www.python.org/downloads/"
    echo ""
    echo "  Press any key to close..."
    read -n 1
    exit 1
fi

# Check files exist
if [ ! -f "Lazarus.html" ] && [ ! -f "index.html" ]; then
    echo "  ⚠  Lazarus.html not found in $(pwd)"
    echo "     Make sure all files are in the same folder."
    echo ""
    echo "  Press any key to close..."
    read -n 1
    exit 1
fi

if [ ! -f "lazarus-server.py" ]; then
    echo "  ⚠  lazarus-server.py not found in $(pwd)"
    echo ""
    echo "  Press any key to close..."
    read -n 1
    exit 1
fi

# Check if port 8080 is already in use
if lsof -i :8080 &> /dev/null; then
    echo "  ⚠  Port 8080 already in use."
    echo "     Another Lazarus server might be running."
    echo "     Opening browser anyway..."
    echo ""
    sleep 1
    open "http://localhost:8080"
    echo "  Press any key to close..."
    read -n 1
    exit 0
fi

echo "  ✓ Python 3 found: $(python3 --version 2>&1)"
echo "  ✓ Files found in $(pwd)"
echo ""
echo "  Starting server on http://localhost:8080"
echo "  Opening browser..."
echo ""

# Open browser after a short delay (give server time to start)
(sleep 1.5 && open "http://localhost:8080") &

# Start the server (this blocks until Ctrl+C)
python3 lazarus-server.py

echo ""
echo "  Server stopped. You can close this window."
echo "  Press any key to close..."
read -n 1
