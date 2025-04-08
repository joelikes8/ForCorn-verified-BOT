#!/bin/bash
# Run the standalone Discord bot directly
export DISCORD_BOT_WORKFLOW=true
export BOT_ONLY_MODE=true
export NO_WEB_SERVER=true
python standalone_discord_bot.py