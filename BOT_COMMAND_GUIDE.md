# ForCorn Discord Bot Command Guide

This guide explains how to run the Discord bot and what commands are available.

## Running the Bot

There are several ways to run the Discord bot:

### Method 1: Using the Workflow System (Recommended)

In the Replit interface, click on "Run" to start both the web application and Discord bot workflows.

If you need to run only the Discord bot workflow, use the workflow selector in the top panel and choose "discord_bot".

### Method 2: Running the Bot Manually

If you need to run the bot manually, use one of these commands:

```bash
# Option 1: Using the workflow-specific bot (recommended for manual starting)
./start_workflow_bot.sh

# Option 2: Using the standalone bot script
python standalone_discord_bot.py

# Option 3: Using the workflow runner
python discord_bot_workflow_runner.py
```

## Available Commands

The bot supports the following slash commands:

### `/ping`
A simple command to check if the bot is responsive.

### `/blacklist <group_id>`
Add a Roblox group to the blacklist.
- **group_id**: The ID of the Roblox group to blacklist

### `/unblacklist <group_id>`
Remove a Roblox group from the blacklist.
- **group_id**: The ID of the Roblox group to remove from the blacklist

### `/background <roblox_username>`
Check if a Roblox user is in any blacklisted groups.
- **roblox_username**: The Roblox username to check

## Troubleshooting

If you encounter issues with the bot:

1. Check that the DISCORD_TOKEN environment variable is set correctly
2. Make sure you're using one of the recommended methods to start the bot
3. Check the logs for any error messages
4. If the bot fails to start due to port conflicts, use the workflow-specific bot (`start_workflow_bot.sh`) which uses port 9000 instead of 5000

## Additional Information

- The bot stores blacklisted groups in the `data/blacklisted_groups.json` file
- The background check command uses the Roblox API to verify if a user is in any blacklisted groups
- The bot uses Discord slash commands, which may take a few minutes to register with Discord when first added to a server