#!/usr/bin/env python3
"""
Standalone Discord Bot

This is a completely standalone Discord bot script that doesn't import
any other modules from the project. It's solely purpose is to run 
as an isolated Discord bot in the discord_bot workflow.
"""

import os
import sys
import logging
import traceback
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("standalone_bot")

# Print an obvious message about isolation mode
print("="*80)
print("STARTING DISCORD BOT IN COMPLETE ISOLATION MODE")
print("This script does not import ANY other project modules")
print("="*80)

logger.info("Starting standalone Discord bot...")

# Load environment variables
try:
    load_dotenv()
    logger.info("Loaded environment variables from .env file")
except Exception as e:
    logger.warning(f"Could not load .env file: {e}")

# Check for Discord token
TOKEN = os.environ.get('DISCORD_TOKEN')
if not TOKEN:
    logger.critical("DISCORD_TOKEN not found in environment variables!")
    logger.critical("Please set your Discord bot token in the Secrets tab or .env file")
    sys.exit(1)

try:
    import discord
    from discord import app_commands
    from discord.ext import commands
except ImportError as e:
    logger.critical(f"Failed to import Discord.py: {e}")
    logger.critical("Please make sure discord.py is installed")
    sys.exit(1)

# Create bot instance with necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    """Event triggered when the bot is connected and ready"""
    logger.info(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    logger.info(f"Connected to {len(bot.guilds)} guild(s)")
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="for commands"
        )
    )
    
    # Sync commands
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")
    
    logger.info("Bot is ready!")

@bot.event
async def on_guild_join(guild):
    """Event triggered when the bot joins a new server"""
    logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")
    
    # Find suitable channel for welcome message
    welcome_channel = None
    if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
        welcome_channel = guild.system_channel
    else:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                welcome_channel = channel
                break
    
    if welcome_channel:
        try:
            # Send welcome message
            embed = discord.Embed(
                title="ForCorn Bot",
                description="Thanks for adding me to your server!",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Commands",
                value="Use `/help` to see available commands!",
                inline=False
            )
            await welcome_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")

@bot.tree.command(name="ping", description="Check if the bot is responding")
async def ping(interaction: discord.Interaction):
    """Simple ping command to test if the bot is working"""
    await interaction.response.send_message(
        f"Pong! Bot is online with a latency of {round(bot.latency * 1000)}ms"
    )

@bot.tree.command(name="help", description="Get help with bot commands")
async def help_command(interaction: discord.Interaction):
    """Help command showing available commands"""
    embed = discord.Embed(
        title="ForCorn Bot Commands",
        description="Here are the available commands:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="General",
        value="`/ping` - Check if bot is responding\n"
              "`/help` - Show this help message\n"
              "`/about` - About this bot",
        inline=False
    )
    
    embed.set_footer(text="Running in standalone mode")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="about", description="About the ForCorn bot")
async def about(interaction: discord.Interaction):
    """About command with bot information"""
    embed = discord.Embed(
        title="About ForCorn Bot",
        description="A Discord bot for Roblox group management",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Version", value="1.0.0", inline=True)
    embed.add_field(name="Servers", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Made with", value="Discord.py", inline=True)
    
    embed.set_footer(text="Running in standalone mode")
    await interaction.response.send_message(embed=embed)

# Main function to be imported by other scripts
def main():
    logger.info("Running standalone Discord bot...")
    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        logger.critical("Invalid Discord token - please check your DISCORD_TOKEN")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Error running bot: {e}")
        logger.critical(traceback.format_exc())
        sys.exit(1)

# Direct execution
if __name__ == "__main__":
    main()