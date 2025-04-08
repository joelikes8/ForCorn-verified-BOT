# ForCorn Discord Bot

A comprehensive Discord bot for Roblox group management, offering advanced authentication, ranking, and server moderation tools with robust deployment configurations.

## Features

- **Roblox Verification**: Link Discord accounts to Roblox accounts with secure verification
- **Group Management**: Set up group IDs, manage rankings, and handle permissions
- **Moderation Tools**: Kick, ban, timeout users, and enable anti-raid protection
- **Ticket System**: Create and manage support tickets for your server

## Setup Instructions

### Prerequisites

1. A Discord Bot Token (get one from the Discord Developer Portal)
2. Python 3.8 or higher
3. PostgreSQL database (optional, SQLite fallback available)
### Environment Variables

Create a `.env` file based on the `.env.example` template with your Discord token.

### Running the Bot

The bot is designed to run in two different ways:

1. **Web + Bot**: Runs both the web interface and Discord bot
   - Use the "Start application" workflow on Replit
   - Or run `python main.py` elsewhere

2. **Bot Only**: Isolated mode with no web components
   - Use the "discord_bot" workflow on Replit
   - Or run `python run_discord_bot_only.py` elsewhere

### Deployment Options

This bot is configured for deployment on Render.com using the included `render.yaml`.

## Commands

### Verification Commands
- `/verify <roblox_username>` - Verify your Roblox account
- `/whois <discord_user>` - Check linked Roblox account

### Group Commands
- `/setupid <group_id>` - Set up Roblox group ID
- `/setuptoken <token>` - Set up Roblox API token (DM only)
- `/rank <roblox_username> <rank_name>` - Rank a user

### Moderation Commands
- `/kick <member> [reason]` - Kick a member
- `/ban <member> [reason] [delete_days]` - Ban a member
- `/timeout <member> <duration> [reason]` - Timeout a member
- `/antiraid <on|off>` - Toggle anti-raid protection
- `/setup_roles` - Set up verification and mod roles

### Ticket Commands
- `/ticket` - Create a support ticket
- `/sendticket <channel>` - Send ticket panel
- `/closeticket` - Close ticket channel
