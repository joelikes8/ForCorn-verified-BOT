#!/usr/bin/env python3
"""
Discord Bot Only

This script runs a Discord bot with absolutely no dependencies on the web application
or database components. It's meant to run as a completely separate service.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("discord_bot_only")

# Log that we're starting in isolated mode
logger.info("Starting Discord bot in completely isolated mode")

# Try to load environment variables from .env file
try:
    load_dotenv()
    logger.info("Loaded environment variables from .env file")
except Exception as e:
    logger.warning(f"Could not load .env file: {e}")

# Check for Discord token
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    logger.error("DISCORD_TOKEN not found in environment variables")
    logger.error("Please make sure you have added your bot token to the .env file or Secrets")
    sys.exit(1)

# Import Discord.py
try:
    import discord
    from discord import app_commands
    from discord.ext import commands
except ImportError:
    logger.error("Failed to import discord.py - please make sure it's installed")
    logger.error("Run: pip install discord.py")
    sys.exit(1)

# Create bot with intents
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    """Called when bot is connected and ready"""
    logger.info(f"Bot connected as {bot.user.name} (ID: {bot.user.id})")
    logger.info(f"Connected to {len(bot.guilds)} servers")
    
    # Set custom status
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="for commands"
    ))
    
    # Sync commands
    try:
        await bot.tree.sync()
        logger.info("Commands synchronized with Discord")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")
    
    logger.info("Bot is ready!")

@bot.tree.command(name="ping", description="Check if the bot is responding")
async def ping(interaction: discord.Interaction):
    """Simple ping command to test the bot"""
    await interaction.response.send_message("Pong! Bot is online and responding!")

@bot.tree.command(name="about", description="Information about this bot")
async def about(interaction: discord.Interaction):
    """Shows information about the bot"""
    embed = discord.Embed(
        title="ForCorn Bot",
        description="A Discord bot for Roblox group management",
        color=discord.Color.blue()
    )
    embed.add_field(name="Version", value="1.0.0", inline=True)
    embed.add_field(name="Servers", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Discord.py", value=discord.__version__, inline=True)
    embed.set_footer(text="Running in isolated mode")
    
    await interaction.response.send_message(embed=embed)

def main():
    """Main function to run the bot"""
    logger.info("Starting Discord bot...")
    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        logger.error("Invalid Discord token - please check your DISCORD_TOKEN")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()