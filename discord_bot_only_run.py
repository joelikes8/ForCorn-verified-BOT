#!/usr/bin/env python3
"""
Discord Bot Runner - Standalone Runner

This is a completely independent script that runs only the Discord bot with the "logged in" status.
It runs independently from the web application.
"""

import os
import sys
import logging
import threading
import time
import discord
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("discord_bot_online")

# Print a very obvious header
print("\n" + "="*70)
print(" DISCORD BOT - LOGGED IN AND ONLINE ".center(70, "="))
print("="*70)
print("PID:", os.getpid())
print("Script:", __file__)
print("Python:", sys.executable)
print("="*70 + "\n")

# Load environment variables from .env file
load_dotenv()
TOKEN = os.environ.get('DISCORD_TOKEN')

if not TOKEN:
    logger.critical("DISCORD_TOKEN not found in environment variables!")
    logger.info("Please create a .env file with DISCORD_TOKEN=your_token")
    sys.exit(1)

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Set up activity and status for "Online" status
activity = discord.Activity(type=discord.ActivityType.watching, name="ForCorn Bot | /help")
client = discord.Client(intents=intents, activity=activity, status=discord.Status.online)

@client.event
async def on_ready():
    """Called when the bot has connected to Discord"""
    logger.info(f"Logged in as {client.user.name} (ID: {client.user.id})")
    logger.info(f"Connected to {len(client.guilds)} servers")
    logger.info("Bot is showing as: ONLINE")
    
    # Print server information
    for guild in client.guilds:
        logger.info(f"Connected to server: {guild.name} (ID: {guild.id})")
    
    logger.info("Bot is now running! CTRL+C to exit")

@client.event
async def on_message(message):
    """Handle message events"""
    # Don't respond to our own messages
    if message.author == client.user:
        return
    
    # Basic response when mentioned
    if client.user.mentioned_in(message):
        await message.channel.send("Hello! Use `/help` for a list of commands.")

def main():
    """Main function to run the bot"""
    try:
        logger.info("Starting Discord bot...")
        client.run(TOKEN)
    except Exception as e:
        logger.error(f"Error running the bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()