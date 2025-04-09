#!/usr/bin/env python3
"""
Simple Discord Bot Runner

This script runs a basic Discord bot that shows as online and logged in
but doesn't attempt to implement all the commands.
"""

import os
import sys
import logging
import discord
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("simple_discord_bot")

# Load environment variables
load_dotenv()
TOKEN = os.environ.get('DISCORD_TOKEN')

# Check if we have a token
if not TOKEN:
    logger.error("No Discord token found in environment variables!")
    logger.info("Make sure you have a .env file with DISCORD_TOKEN set")
    sys.exit(1)

# Set up the Discord client with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create a client instance with a status showing "Online"
activity = discord.Activity(
    type=discord.ActivityType.watching,
    name="ForCorn Bot | /help"
)
client = discord.Client(
    intents=intents,
    activity=activity,
    status=discord.Status.online
)

@client.event
async def on_ready():
    """Called when the bot has connected to Discord successfully"""
    logger.info(f"Logged in as {client.user.name} (ID: {client.user.id})")
    logger.info(f"Connected to {len(client.guilds)} servers")
    logger.info(f"Bot is showing as: ONLINE")
    logger.info("Bot is now running! Press CTRL+C to exit.")

@client.event
async def on_message(message):
    """Handle incoming messages (not used in this simple version)"""
    # Don't respond to our own messages
    if message.author == client.user:
        return
    
    # Very basic response to messages that mention the bot
    if client.user.mentioned_in(message):
        await message.channel.send("Hello! Use `/help` for a list of commands.")

def main():
    """Main entry point for the bot"""
    try:
        # Print a very obvious header
        print("\n" + "="*60)
        print(" SIMPLE DISCORD BOT - LOGGED IN AND ONLINE ".center(60, "="))
        print("="*60)
        print(f"Token starts with: {TOKEN[:5]}...")
        print(f"Python version: {sys.version}")
        print("="*60 + "\n")
        
        # Run the bot with the token
        client.run(TOKEN, log_handler=None)
    except Exception as e:
        logger.error(f"Error running the bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()