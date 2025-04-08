#!/bin/bash
# Script to run the Discord bot in a separate workflow

# Force using SQLite instead of PostgreSQL
export DATABASE_URL=sqlite:///bot.db

# Run the independent Discord bot script
python run_discord_bot.py
