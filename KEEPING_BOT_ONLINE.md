# Keeping Your Discord Bot Online 24/7

This guide explains how to keep your Discord bot online continuously, even when facing interruptions or disconnects. The provided scripts and methods ensure maximum uptime for your Discord bot.

## Primary Discord Bot Script

The primary Discord bot script is `final_discord_bot.py`. This script contains all 20 commands and runs completely isolated from the web application to prevent port conflicts.

## Running Methods

### Method 1: Direct Execution

For testing and development, you can run the bot directly using:

```bash
python discord_bot_only_run.py
```

This script provides a clean setup that shows the bot as properly online in Discord with the status "ForCorn Bot | /help".

### Method 2: Using the Launcher Script

For improved reliability, use the launcher script:

```bash
bash run_discord_bot.sh
```

This script sets the proper environment variables and provides visual confirmation when the bot starts.

### Method 3: Workflow (Recommended for 24/7 Operation)

The most reliable method for 24/7 operation is using the configured workflow. Replit automatically restarts this workflow if it stops for any reason.

## Key Features for 24/7 Uptime

### 1. Automatic Reconnection

The Discord bot is configured with automatic reconnection logic. If the connection to Discord is lost, the bot will:

1. Detect the disconnection
2. Log the error
3. Attempt to reconnect with progressive backoff
4. Resume normal operation once reconnected

### 2. Proper Status Display

The bot is configured to consistently display as "Online" in Discord with the appropriate status message. This is achieved through:

```python
activity = discord.Activity(type=discord.ActivityType.watching, name="ForCorn Bot | /help")
client = discord.Client(intents=intents, activity=activity, status=discord.Status.online)
```

### 3. Separate HTTP Server

For cloud hosting platforms that require port binding (like Render.com), the bot includes a minimal HTTP server that:

- Runs on a separate thread
- Binds to a different port than the web application (9000 instead of 5000)
- Provides a simple status page showing the bot is online

### 4. Error Handling and Logging

Comprehensive error handling ensures the bot can recover from most error conditions:

- All commands have try/except blocks
- Critical errors are logged with detailed information
- Non-critical errors are handled gracefully without crashing the bot

## Hosting Options

### Option 1: Replit (Current Configuration)

Keep the "discord_bot" workflow running. Replit will automatically restart the bot if it crashes or if the Replit instance is restarted.

### Option 2: Render.com (Alternative)

The project includes a `render.yaml` configuration for Render.com hosting, which provides similar 24/7 uptime guarantees.

## Monitoring Bot Uptime

You can verify your bot is staying online by:

1. Checking the Discord server's member list - the bot should appear with the green "Online" status
2. Using the `/ping` command periodically to confirm the bot is responsive
3. Monitoring the console logs for connection messages and heartbeat signals

## Troubleshooting

If the bot goes offline:

1. Check the logs for any error messages
2. Ensure the `DISCORD_TOKEN` environment variable is correctly set
3. Verify there are no IP restrictions or rate limits from Discord
4. Restart the workflow or hosting service

## Advanced: Keeping a Remote Bot Online

For hosting on services like Render.com:

1. Use the included `keep_bot_online.py` script which periodically pings the bot's HTTP endpoint
2. Configure a monitoring service (like UptimeRobot) to ping the bot's status endpoint
3. Use Render.com's built-in health checks to restart the service if it becomes unresponsive