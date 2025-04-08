# Render.com Deployment Instructions

## Overview
This document provides instructions for deploying the ForCorn Discord bot on Render.com.

## Modified Bot Script
We've updated `standalone_discord_bot.py` to include a minimal HTTP server that satisfies Render.com's port binding requirements. This server:
- Starts only when the `PORT` environment variable is detected (which Render sets automatically)
- Runs in a separate thread alongside the Discord bot
- Provides a simple status page showing the bot's connection state
- Doesn't interfere with the Discord bot's functionality

## Render.yaml Configuration
Here's the recommended configuration for your render.yaml file:

```yaml
services:
  # Discord Bot Service (as web service to avoid port binding issues)
  - type: web
    name: forcorn-discord-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python standalone_discord_bot.py
    envVars:
      - key: DISCORD_TOKEN
        sync: false
      - key: DATABASE_URL
        fromDatabase:
          name: forcorn-bot-db
          property: connectionString
      - key: BOT_ONLY_MODE
        value: "true"
      - key: DISCORD_BOT_WORKFLOW
        value: "true" 
      - key: NO_WEB_SERVER
        value: "true"
      - key: PYTHON_VERSION
        value: 3.10.0
      - key: PYTHONPATH
        value: "."
      - key: PYTHON_UNBUFFERED
        value: "1"

databases:
  - name: forcorn-bot-db
    databaseName: forcornbot
    user: forcorn
    plan: free
```

## Important Notes
1. Notice that we're using `type: web` instead of `type: worker` - this ensures that Render expects a port to be bound
2. The start command uses our new `standalone_discord_bot.py` script which includes the HTTP server
3. We've added environment variables to enable bot-only mode and disable the web server component
4. You'll need to set your `DISCORD_TOKEN` in the Render dashboard or through their CLI

## Manual Deployment (if not using render.yaml)
1. Create a new Web Service in the Render dashboard
2. Connect your GitHub repository
3. Set the build command to: `pip install -r requirements.txt`
4. Set the start command to: `python standalone_discord_bot.py`
5. Add the environment variables listed in the render.yaml configuration above
6. Deploy the service

After deployment, your bot should connect to Discord and the status page should be accessible at your Render service URL.