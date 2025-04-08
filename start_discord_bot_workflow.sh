#!/bin/bash
# Start the Discord bot workflow

# Force use of SQLite
export DATABASE_URL=sqlite:///bot.db

# Call main.py with an argument to indicate we want to run the bot
python main.py --discord-bot
