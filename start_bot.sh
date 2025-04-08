#!/bin/bash

# This script launches the Discord bot directly
set -e

# Print some debug information
echo "Starting Discord bot..."
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"

# Launch the Discord bot
python main.py
