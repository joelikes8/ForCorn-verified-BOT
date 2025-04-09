# ForCorn Discord Bot Command Guide

This guide provides information about all available commands in the ForCorn Discord bot and how to run the bot.

## Running the Bot

There are two ways to run the Discord bot:

1. **Using the workflow (recommended)**
   - The discord_bot workflow should automatically start the bot
   - If it's running a web server instead, you can manually start the bot using:
   ```
   ./run_bot.sh
   ```

2. **Running manually**
   - You can run the bot directly with:
   ```
   python standalone_discord_bot.py
   ```
   - This will start the Discord bot with all 20 commands

## Available Commands

### General
- `/ping` - Check if the bot is responding
- `/help` - Display a list of available commands
- `/about` - Show information about the bot

### Verification
- `/verify <roblox_username>` - Verify your Roblox account
- `/update` - Update your nickname with your Roblox rank
- `/background <roblox_username>` - Check if a user is in blacklisted groups

### Tickets
- `/ticket` - Create a support ticket
- `/closeticket` - Close an open ticket channel
- `/sendticket [channel]` - Send the ticket panel to a channel

### Group Management
- `/rank <roblox_username> [rank_name]` - View or change a user's rank in the Roblox group
- `/setupid <group_id>` - Set the Roblox group ID for the server
- `/ranksetup <group_id>` - Set up the Roblox group ID for ranking
- `/setuptoken <token>` - Configure the Roblox API token for ranking

### Moderation
- `/kick <member> [reason]` - Kick a member from the server
- `/ban <member> [reason]` - Ban a member from the server
- `/timeout <member> <duration> [reason]` - Apply a timeout to a member
- `/antiraid <action>` - Toggle anti-raid protection

### Server Setup
- `/setup_roles [verified_role] [mod_role] [admin_role]` - Configure verification and moderation roles
- `/blacklistedgroups <group_id>` - Add a Roblox group to the blacklist
- `/removeblacklist <group_id>` - Remove a Roblox group from the blacklist

## Troubleshooting

If the bot doesn't start or commands are missing:

1. Check if the bot is already running with:
   ```
   ps aux | grep python
   ```

2. If multiple instances are running, kill them first:
   ```
   pkill -f "python.*discord" || true
   ```

3. Then start the bot using the run_bot.sh script:
   ```
   ./run_bot.sh
   ```

4. If commands are still missing, it may take up to an hour for Discord to fully register all commands.