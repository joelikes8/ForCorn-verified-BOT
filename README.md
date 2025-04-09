# ForCorn Discord Bot

A sophisticated Discord bot for Roblox group management, offering advanced interaction and moderation capabilities with robust deployment support and 24/7 uptime.

## Features

- **Verification System**: Verify Discord users with their Roblox accounts
- **Group Management**: Manage Roblox group roles directly from Discord
- **Ticket System**: Create and manage support tickets
- **Moderation Tools**: Advanced moderation commands for server management
- **Blacklist System**: Block users from specific Roblox groups
- **Isolated Architecture**: Runs independently from web components
- **24/7 Uptime**: Multiple options for keeping the bot online continuously
- **Status Dashboard**: Web interface showing bot uptime and statistics
- **Auto-Recovery**: Self-healing system that automatically restarts if disconnected

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

For a complete command guide, see [BOT_COMMAND_GUIDE.md](BOT_COMMAND_GUIDE.md).

## Setup Instructions

1. Clone this repository
2. Install required dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your Discord token: `DISCORD_TOKEN=your_token_here`
4. Run the bot using one of these methods:

### Basic Execution
```bash
python final_discord_bot.py
```

### 24/7 Uptime with Auto-Restart
```bash
./keep_bot_online.sh
```

### Web Dashboard for Hosted Environments
```bash
python persistent_bot.py
```

## Keeping the Bot Online 24/7

We've provided multiple scripts for ensuring your bot stays online:

1. **Replit Hosting**:
   - Use `./keep_bot_online.sh` for background execution with auto-restart

2. **Render.com Hosting**:
   - Deploy with `persistent_bot.py` for both bot functionality and status dashboard
   - Already configured in `render.yaml`

3. **Discord Bot Workflow**:
   - Uses the `discord_bot` workflow with our specialized runner

For detailed information on 24/7 hosting, see [KEEPING_BOT_ONLINE.md](KEEPING_BOT_ONLINE.md).

## Deployment Options

This bot supports multiple deployment methods:
- Standard Python execution with auto-restart capability
- Background process with logging and monitoring
- Web dashboard with status monitoring for hosted environments
- Render.com web service compatible (pre-configured)
- Replit workflow integration

## Architecture

The bot uses a completely isolated architecture to avoid conflicts with web application components, featuring:

- Standalone operation mode with process isolation
- Independent HTTP server for monitoring and status dashboard
- JSON-based configuration storage
- Discord.py command framework with 20 commands
- Self-healing monitor with rate-limited restarts

## Documentation

- [BOT_COMMAND_GUIDE.md](BOT_COMMAND_GUIDE.md) - Complete command reference
- [KEEPING_BOT_ONLINE.md](KEEPING_BOT_ONLINE.md) - Guide to keeping your bot online 24/7