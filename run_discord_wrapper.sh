#!/bin/bash
# Run the Discord bot using the main wrapper

# Set environment variable to indicate we want to run the Discord bot
export DISCORD_BOT_WORKFLOW=true

# Unset DATABASE_URL to avoid PostgreSQL errors
unset DATABASE_URL

# Run through the wrapper
python main_wrapper.py
