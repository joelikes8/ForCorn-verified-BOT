#!/usr/bin/env python3
"""
Main entry point for the Discord bot

This script initializes and runs the Discord bot.
"""

import os
import sys
import logging
import asyncio
import discord
from discord.ext import commands
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("discord_bot")

# Import cogs
from cogs.verification_commands import VerificationCommands
from cogs.moderation_commands import ModerationCommands
from cogs.ticket_commands import TicketCommands
from cogs.group_commands import GroupCommands

# Import utility modules
from utils.roblox_api import RobloxAPI
from utils.verification import VerificationSystem
from utils.moderation import ModerationSystem
from utils.ticket_system import TicketSystem
from utils.blacklist import BlacklistSystem
from config import Config

# Check for Discord token
if not os.environ.get("DISCORD_TOKEN"):
    logger.critical("DISCORD_TOKEN environment variable is missing")
    sys.exit(1)

# Initialize bot with appropriate intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Initialize configuration and utility systems
config = Config()
roblox_api = RobloxAPI()
verification_system = VerificationSystem(roblox_api)
moderation_system = ModerationSystem(bot)
ticket_system = TicketSystem(bot, config)
blacklist_system = BlacklistSystem(roblox_api, config)

@bot.event
async def on_ready():
    """Event triggered when the bot is connected and ready"""
    logger.info(f"Bot connected as {bot.user.name} (ID: {bot.user.id})")
    logger.info(f"Connected to {len(bot.guilds)} servers")
    
    # Add cogs
    await bot.add_cog(VerificationCommands(bot, verification_system, roblox_api, blacklist_system))
    await bot.add_cog(ModerationCommands(bot, moderation_system))
    await bot.add_cog(TicketCommands(bot, ticket_system))
    await bot.add_cog(GroupCommands(bot, roblox_api, config))
    
    logger.info("All cogs have been loaded")
    
    # Set bot activity
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="for /verify commands"
    ))
    
    logger.info("Bot is fully ready")

@bot.event
async def on_guild_join(guild):
    """Event triggered when the bot joins a new server"""
    logger.info(f"Bot joined new server: {guild.name} (ID: {guild.id})")
    
    # Find a suitable channel to send welcome message
    target_channel = None
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            target_channel = channel
            break
    
    if target_channel:
        embed = discord.Embed(
            title="Thanks for adding ForCorn!",
            description=(
                "ForCorn is a powerful Roblox utility bot for Discord.\n\n"
                "**Key features:**\n"
                "• `/verify` - Link Discord and Roblox accounts\n"
                "• `/rank` - Manage Roblox group ranks\n"
                "• `/ticket` - Support ticket system\n"
                "• `/kick`, `/ban`, `/timeout` - Moderation commands\n\n"
                "Type `/help` to see all commands!"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Use /setuproles to configure roles for your server")
        await target_channel.send(embed=embed)

@bot.event
async def on_error(event, *args, **kwargs):
    """Global error handler for bot events"""
    logger.error(f"Error in event {event}: {sys.exc_info()[1]}")
    logger.error(traceback.format_exc())

@bot.event
async def on_command_error(ctx, error):
    """Error handler for command errors"""
    if isinstance(error, commands.CommandNotFound):
        return
    
    logger.error(f"Command error in {ctx.command}: {error}")
    await ctx.send(f"An error occurred: {error}")

def main():
    """Main function to run the bot"""
    try:
        # Run the bot with the token from environment variables
        token = os.environ.get("DISCORD_TOKEN")
        bot.run(token)
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        logger.critical(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()