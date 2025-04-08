#!/usr/bin/env python3
"""
Discord bot runner script

This script runs the Discord bot without any database dependencies.
It's designed to be used in a dedicated workflow.
"""

import os
import sys
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("discord_bot")

# Load environment variables
load_dotenv()

# Check for Discord token
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    logger.error("DISCORD_TOKEN not found in environment variables")
    sys.exit(1)

# Force the use of SQLite for any database operations
os.environ["DATABASE_URL"] = "sqlite:///bot.db"
logger.info("Set DATABASE_URL to use SQLite")

# Create bot with all intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Event triggered when the bot is connected"""
    logger.info(f"Bot logged in as {bot.user.name}")
    logger.info(f"Bot ID: {bot.user.id}")
    logger.info(f"Connected to {len(bot.guilds)} servers")
    
    # Set custom status
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="for commands"
    ))
    
    logger.info("Bot is fully ready!")

@bot.tree.command(name="ping", description="Check if the bot is online")
async def ping(interaction: discord.Interaction):
    """Simple ping command to check if the bot is working"""
    await interaction.response.send_message("Pong! Bot is online!")

@bot.event
async def on_guild_join(guild):
    """Handles when the bot joins a new server"""
    logger.info(f"Joined new server: {guild.name} (ID: {guild.id})")
    
    # Find a channel to send the welcome message
    target_channel = None
    if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
        target_channel = guild.system_channel
    else:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                target_channel = channel
                break
    
    if target_channel:
        embed = discord.Embed(
            title="Thanks for adding ForCorn Bot!",
            description="This is a simple bot setup for demonstration purposes.",
            color=discord.Color.blue()
        )
        try:
            await target_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Could not send welcome message: {e}")

def main():
    """Main function to run the bot"""
    logger.info("Starting Discord bot...")
    try:
        # Try to sync commands with Discord
        @bot.event
        async def on_connect():
            try:
                synced = await bot.tree.sync()
                logger.info(f"Synced {len(synced)} command(s)")
            except Exception as e:
                logger.error(f"Failed to sync commands: {e}")
        
        # Run the bot
        bot.run(TOKEN)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()