#!/usr/bin/env python3
"""
Simple Discord Bot

A simplified version of the Discord bot that runs independently
without any database dependencies or complex functionality.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("discord_bot")

try:
    import discord
    from discord import app_commands
    from discord.ext import commands
except ImportError as e:
    logger.error(f"Failed to import Discord library: {e}")
    logger.error("Make sure discord.py is installed: pip install discord.py")
    sys.exit(1)

# Load environment variables
try:
    load_dotenv()
    logger.info("Loaded environment variables from .env")
except Exception as e:
    logger.warning(f"Could not load .env file: {e}")

# Get Discord token
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    logger.error("DISCORD_TOKEN not found in environment variables")
    logger.error("Please make sure you have added your bot token to the .env file")
    sys.exit(1)

# Create bot instance with all intents
intents = discord.Intents.default()
intents.message_content = True  # This is required to read message content
intents.members = True  # This is required to see server members
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Event triggered when the bot is connected and ready"""
    logger.info(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    logger.info(f"Connected to {len(bot.guilds)} server(s)")
    
    # Set custom status
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="for /ping commands"
    ))
    
    # Sync commands with Discord
    try:
        await bot.tree.sync()
        logger.info("Synced commands with Discord")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")
    
    logger.info("Bot is ready!")

@bot.event
async def on_guild_join(guild):
    """Handle when the bot joins a new server"""
    logger.info(f"Joined new server: {guild.name} (ID: {guild.id})")
    
    # Try to find a suitable channel to send welcome message
    channel = None
    if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
        channel = guild.system_channel
    else:
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).send_messages:
                channel = ch
                break
    
    if channel:
        embed = discord.Embed(
            title="ForCorn Bot",
            description="Thanks for adding me! I'm a simple demonstration bot.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Commands", value="Try using `/ping` to test if I'm working!")
        
        try:
            await channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")

@bot.tree.command(name="ping", description="Check if the bot is responding")
async def ping_command(interaction: discord.Interaction):
    """Simple ping command to test if the bot is working"""
    await interaction.response.send_message("Pong! Bot is online and responding!")

@bot.tree.command(name="info", description="Get information about the bot")
async def info_command(interaction: discord.Interaction):
    """Command to show information about the bot"""
    embed = discord.Embed(
        title="ForCorn Bot Info",
        description="A multi-purpose Discord bot for Roblox group management",
        color=discord.Color.blue()
    )
    embed.add_field(name="Version", value="1.0.0", inline=True)
    embed.add_field(name="Servers", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Developer", value="ForCorn Team", inline=True)
    
    await interaction.response.send_message(embed=embed)

def run_bot():
    """Run the Discord bot"""
    logger.info("Starting Discord bot...")
    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        logger.error("Invalid Discord token. Please check your DISCORD_TOKEN environment variable.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Initializing simple Discord bot...")
    run_bot()