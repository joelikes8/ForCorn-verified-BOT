#!/bin/bash
# Run completely isolated Discord bot
# This script avoids any interaction with the web application

echo "Starting completely isolated Discord bot..."

# Run only the isolated script directly - no other imports
python completely_isolated_bot.py
