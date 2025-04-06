# Roblox Group Management Discord Bot

A Discord bot for Roblox group management with verification, ranking, and moderation features.

## Features

- **Verification System**: Link Discord users to Roblox accounts with secure verification codes
- **Group Rank Management**: Check and update user ranks in Roblox groups
- **Nickname Formatting**: Automatically format Discord nicknames with group ranks
- **Blacklisted Group Detection**: Check if users are in blacklisted Roblox groups
- **Ticket System**: Create support tickets for user assistance
- **Moderation Features**: Basic moderation commands with anti-raid protection

## Setup

1. Clone this repository
2. Install required packages: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your Discord bot token
4. Run the bot: `python main.py`

## Commands

### Verification Commands
- `/verify [roblox_username]` - Verify your Roblox account
- `/background [roblox_username]` - Check if a user is in blacklisted groups
- `/blacklistedgroups [action] [group_id]` - Manage blacklisted groups

### Group Commands
- `/setupid [group_id]` - Set up the Roblox group ID for the server
- `/ranksetup [group_id]` - Alias for setupid
- `/setuptoken [token]` - Set up the Roblox API token for ranking (DM only!)
- `/rank [roblox_username] [rank_name]` - Rank a user in the Roblox group

### Ticket Commands
- `/ticket` - Create a support ticket
- `/sendticket [channel]` - Send the ticket panel to a channel
- `/closeticket` - Close a ticket channel

### Moderation Commands
- `/kick [member] [reason]` - Kick a member from the server
- `/ban [member] [reason] [delete_days]` - Ban a member from the server
- `/timeout [member] [duration] [reason]` - Timeout a member
- `/antiraid [action]` - Toggle anti-raid protection
- `/setup_roles [verified_role] [mod_role] [admin_role]` - Set up roles for the bot

## Security

- Sensitive commands like `/setuptoken` are restricted to DMs
- Permission checks for all moderation commands
- Secure storage of verification codes and tokens

## Requirements

- Python 3.8+
- discord.py
- aiohttp
- python-dotenv
