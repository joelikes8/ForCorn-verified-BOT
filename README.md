# ForCorn Discord Bot

A sophisticated Discord bot for Roblox group management, offering advanced interaction and moderation capabilities with robust deployment support.

## Features

- **Verification System**: Verify Discord users with their Roblox accounts
- **Group Management**: Manage Roblox group roles directly from Discord
- **Ticket System**: Create and manage support tickets
- **Moderation Tools**: Advanced moderation commands for server management
- **Blacklist System**: Block users from specific Roblox groups
- **Isolated Architecture**: Runs independently from web components

## Available Commands

The bot offers 20 slash commands including:

- `/verify` - Verify your Roblox account
- `/ticket` - Create a support ticket
- `/help` - Show available commands
- `/rank` - Rank a user in the Roblox group
- `/background` - Check if user is in blacklisted groups
- `/blacklistedgroups` - Add a Roblox group to the blacklist
- `/removeblacklist` - Remove a Roblox group from the blacklist
- And many more!

## Setup Instructions

1. Clone this repository
2. Install required dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your Discord token: `DISCORD_TOKEN=your_token_here`
4. Run the bot: `python standalone_discord_bot.py` or `./direct_bot_starter.sh`

## Deployment Notes

This bot supports multiple deployment methods:
- Standard Python execution
- Isolated runner with separate HTTP service
- Containerized deployment
- Render.com web service compatible

## Architecture

The bot uses a completely isolated architecture to avoid conflicts with web application components. It includes:

- Standalone operation mode
- Independent HTTP server for monitoring
- JSON-based configuration storage
- Discord.py command framework