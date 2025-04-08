# ForCorn Discord Bot Command Guide

## Running the Bot

If you're experiencing issues with commands not responding, follow these steps:

### Option 1: Run the Bot Directly (Recommended)

```bash
# Close any running processes first by clicking "Stop" in the Replit interface

# Then run the bot directly using our optimized script
./discord_bot_runner.sh
```

This script will automatically choose the best way to run the bot without conflicting with the web server.

### Option 2: Use the Simplified Bot Runner

```bash
python run_bot_only.py
```

### Option 3: Run the Standalone Bot Directly

```bash
python standalone_discord_bot.py
```

## Common Issues

### Commands Not Appearing in Discord

- New commands can take up to an hour to propagate through Discord's systems
- Make sure your bot has the proper intents enabled on the Discord Developer Portal

### Application Not Responding to Commands

- Check that you have the correct bot token in your `.env` file
- Make sure the bot is running (check for "Bot is ready!" message in the console)
- Verify that your Discord server has given proper permissions to the bot

### Port Conflicts

If you see errors about "Address already in use" for port 5000, it means both the web server and Discord bot are trying to use the same port. Use one of the methods above to run just the bot without the web server.

## Available Commands

The bot has approximately 20 commands, including:

### Verification
- `/verify <roblox_username>` - Verify your Roblox account
- `/update` - Update your nickname with your Roblox rank
- `/background <roblox_username>` - Check if user is in blacklisted groups

### Moderation
- `/kick <member> [reason]` - Kick a member
- `/ban <member> [reason]` - Ban a member
- `/timeout <member> <duration> [reason]` - Timeout a member
- `/antiraid <action>` - Toggle anti-raid protection

### Group Management
- `/blacklistedgroups <group_id>` - Add a Roblox group to the blacklist
- `/removeblacklist <group_id>` - Remove a Roblox group from the blacklist
- `/rank <roblox_username> [rank_name]` - View or change a user's rank
- `/setup_roles [verified_role] [mod_role] [admin_role]` - Set up verification and moderation roles

### Support System
- `/ticket` - Create a support ticket
- `/closeticket` - Close a ticket channel
- `/sendticket [channel]` - Send the ticket panel to a channel