#!/bin/bash
# Run script for Rick and Morty Tactical RTS

# Ensure we're in the project root directory
cd "$(dirname "$0")"

# Check if Python is installed
if ! command -v python3 &>/dev/null; then
    echo "Error: Python 3 is required but not installed"
    exit 1
fi

# Check if requirements are installed
echo "Checking dependencies..."
if ! python3 -c "import pygame, numpy, pymunk, pynput" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the game
echo "Starting Rick and Morty Tactical RTS..."
python3 src/main.py
