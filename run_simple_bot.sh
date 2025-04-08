#!/bin/bash
# Run the simple Discord bot

# Override DATABASE_URL to avoid PostgreSQL errors
unset DATABASE_URL

# Run the simple Discord bot that does not use the database
python simple_discord_bot.py
