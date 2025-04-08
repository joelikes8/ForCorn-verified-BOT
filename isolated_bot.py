"""
Isolated Discord bot script

This script runs a completely isolated Discord bot without any dependencies
on the Flask application. It's designed to be used in a dedicated workflow
without interfering with the web app.
"""

import os
import logging
import sys
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("discord_bot")

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    logger.error("No Discord token found in environment variables!")
    sys.exit(1)

# Import bot components
from bot_config import BotConfig
from utils.roblox_api import RobloxAPI
from utils.verification_isolated import VerificationSystem
from utils.moderation import ModerationSystem
from utils.ticket_system import TicketSystem
from utils.blacklist import BlacklistSystem

# Create bot instance with all intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize configuration
config = BotConfig()
roblox_api = RobloxAPI()

# Initialize utility systems
verification_system = VerificationSystem(bot, roblox_api, config)
moderation_system = ModerationSystem(bot)
ticket_system = TicketSystem(bot, config)
blacklist_system = BlacklistSystem(roblox_api, config)

# Import command cogs
try:
    from cogs.verification_commands import VerificationCommands
    from cogs.moderation_commands import ModerationCommands
    from cogs.ticket_commands import TicketCommands
    from cogs.group_commands import GroupCommands
except Exception as e:
    logger.error(f"Error importing cogs: {e}")

@bot.event
async def on_ready():
    """Event triggered when the bot is connected and ready"""
    logger.info(f"Bot connected as {bot.user.name} (ID: {bot.user.id})")
    
    # Sync commands with Discord
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")
    
    # Set bot status
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="for /verify commands"
    ))
    
    logger.info("Bot is ready!")

@bot.event
async def on_guild_join(guild):
    """Event triggered when the bot joins a new server"""
    logger.info(f"Joined new server: {guild.name} (ID: {guild.id})")
    
    # Try to find a general or system channel to send welcome message
    target_channel = None
    if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
        target_channel = guild.system_channel
    else:
        # Look for a general channel
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                if "general" in channel.name.lower() or "chat" in channel.name.lower():
                    target_channel = channel
                    break
        
        # If no general channel found, use the first text channel where we can send messages
        if not target_channel:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    target_channel = channel
                    break
    
    if target_channel:
        embed = discord.Embed(
            title="Thanks for adding ForCorn Bot!",
            description=(
                "ForCorn Bot provides Roblox verification, ticket system, "
                "and moderation tools for your Discord server.\n\n"
                "Use `/setuproles` to set up verification and moderation roles.\n"
                "Use `/verify` to verify Roblox accounts.\n"
                "Use `/sendticket` to set up the ticket system."
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Use /help for more information")
        
        try:
            await target_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")

@bot.event
async def on_error(event, *args, **kwargs):
    """Global error handler for bot events"""
    logger.error(f"Error in event {event}: {sys.exc_info()[1]}")

@bot.event 
async def on_command_error(ctx, error):
    """Error handler for command errors"""
    if isinstance(error, commands.CommandNotFound):
        return
    
    logger.error(f"Command error: {error}")
    
    try:
        await ctx.send(f"An error occurred: {error}")
    except:
        pass

def main():
    """Main function to run the bot"""
    # Add command cogs
    try:
        bot.add_cog(VerificationCommands(bot, verification_system, blacklist_system, roblox_api))
        bot.add_cog(ModerationCommands(bot, moderation_system))
        bot.add_cog(TicketCommands(bot, ticket_system))
        bot.add_cog(GroupCommands(bot, roblox_api, config))
        logger.info("Added command cogs")
    except Exception as e:
        logger.error(f"Error adding cogs: {e}")
    
    # Run the bot
    bot.run(TOKEN, log_handler=None)  # log_handler=None to avoid duplicate logs

if __name__ == "__main__":
    logger.info("Starting isolated Discord bot...")
    main()