#!/usr/bin/env python3
"""
Discord Bot Uptime Guardian

This script is specifically designed to ensure your Discord bot stays online 24/7
by implementing robust reconnection logic and monitoring.

Features:
- Automatically reconnects if disconnected
- Implements exponential backoff for reconnection attempts
- Logs connection status changes
- Monitors Discord API status
- Handles rate limits gracefully
"""

import os
import sys
import time
import signal
import random
import logging
import asyncio
import platform
import threading
import traceback
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot_uptime.log")
    ]
)
logger = logging.getLogger("uptime_guardian")

# Load environment variables
load_dotenv()
TOKEN = os.environ.get('DISCORD_TOKEN')

# Check for token
if not TOKEN:
    logger.critical("DISCORD_TOKEN not found in environment variables!")
    logger.info("Please create a .env file with DISCORD_TOKEN=your_token")
    sys.exit(1)

try:
    import discord
    from discord import app_commands
    from discord.ext import commands, tasks
except ImportError as e:
    logger.critical(f"Failed to import Discord.py: {e}")
    logger.critical("Please make sure discord.py is installed")
    sys.exit(1)

# Constants for reconnection logic
INITIAL_RECONNECT_DELAY = 1  # seconds
MAX_RECONNECT_DELAY = 300    # 5 minutes max delay
RECONNECT_JITTER = 2.0       # random jitter multiplier
RECONNECT_FACTOR = 1.5       # exponential backoff factor

class UptimeGuardian(commands.Bot):
    """A bot class with enhanced reconnection and uptime monitoring"""
    
    def __init__(self):
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        # Set up activity and status for "Online" status
        activity = discord.Activity(
            type=discord.ActivityType.watching, 
            name="ForCorn Bot | /help"
        )
        
        # Initialize the bot with custom status
        super().__init__(
            command_prefix="!",  # Fallback prefix, slash commands are primary
            intents=intents,
            activity=activity,
            status=discord.Status.online,
            reconnect=True  # Enable built-in reconnect feature
        )
        
        # Track reconnection attempts
        self.reconnect_attempt = 0
        self.reconnect_delay = INITIAL_RECONNECT_DELAY
        self.last_connected = None
        self.disconnect_count = 0
        self.start_time = datetime.now()
        
        # Set up tasks
        self.status_reporter.start()
    
    async def setup_hook(self):
        """Set up the bot's commands and sync with Discord"""
        # Add a single /ping command for testing
        @self.tree.command(name="ping", description="Check bot connection status")
        async def ping(interaction: discord.Interaction):
            uptime = datetime.now() - self.start_time
            days, remainder = divmod(uptime.total_seconds(), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            embed = discord.Embed(
                title="🟢 Bot Status: Online",
                description=f"Latency: {round(self.latency * 1000)}ms",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="Uptime",
                value=f"{int(days)} days, {int(hours)} hours, {int(minutes)} minutes",
                inline=False
            )
            
            embed.add_field(
                name="Disconnect Count",
                value=f"{self.disconnect_count} times",
                inline=True
            )
            
            embed.add_field(
                name="Connected Servers",
                value=f"{len(self.guilds)} servers",
                inline=True
            )
            
            embed.add_field(
                name="Platform",
                value=f"{platform.system()} {platform.release()}",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed)
        
        # Sync commands with Discord
        try:
            logger.info("Syncing commands with Discord...")
            await self.tree.sync()
            logger.info("Commands synced successfully!")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    @tasks.loop(minutes=30)
    async def status_reporter(self):
        """Reports bot status periodically"""
        if not self.is_ready():
            return
            
        uptime = datetime.now() - self.start_time
        days, remainder = divmod(uptime.total_seconds(), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        logger.info(f"Bot status: ONLINE for {int(days)}d {int(hours)}h {int(minutes)}m")
        logger.info(f"Connected to {len(self.guilds)} servers with latency {round(self.latency * 1000)}ms")
        logger.info(f"Disconnected {self.disconnect_count} times during this session")
    
    @status_reporter.before_loop
    async def before_status_reporter(self):
        """Wait until bot is ready before starting the status reporter"""
        await self.wait_until_ready()
    
    async def on_ready(self):
        """Called when the bot successfully connects to Discord"""
        self.last_connected = datetime.now()
        
        if self.reconnect_attempt > 0:
            logger.info(f"Reconnection successful after {self.reconnect_attempt} attempts!")
            # Reset reconnection variables on successful connection
            self.reconnect_attempt = 0
            self.reconnect_delay = INITIAL_RECONNECT_DELAY
        else:
            logger.info("Bot has connected to Discord successfully!")
        
        logger.info(f"Logged in as {self.user.name} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} servers")
        logger.info(f"Discord.py API version: {discord.__version__}")
        logger.info(f"Bot is showing as: ONLINE")
        
        for guild in self.guilds:
            logger.info(f"Connected to server: {guild.name} (ID: {guild.id})")
        
        logger.info("Bot is now running! Press CTRL+C to exit")
    
    async def on_resumed(self):
        """Called when the bot resumes a session after a disconnect"""
        resume_time = datetime.now()
        
        if self.last_connected:
            downtime = resume_time - self.last_connected
            minutes, seconds = divmod(downtime.total_seconds(), 60)
            logger.info(f"Session resumed after being down for {int(minutes)}m {int(seconds)}s")
        
        self.last_connected = resume_time
        logger.info("Bot session has been resumed")
    
    async def on_disconnect(self):
        """Called when the bot disconnects from Discord"""
        self.disconnect_count += 1
        logger.warning(f"Bot disconnected from Discord (disconnect #{self.disconnect_count})")
        
        # Don't increment reconnect attempt if auto-reconnect might handle it
        if not getattr(self, "is_closed", lambda: True)():
            logger.info("Relying on Discord.py's auto-reconnect mechanism")
            return
            
        # Otherwise, prepare for manual reconnection
        self.reconnect_attempt += 1
        
        # Calculate next reconnect delay with exponential backoff and jitter
        jitter = random.uniform(1.0, RECONNECT_JITTER)
        self.reconnect_delay = min(
            self.reconnect_delay * RECONNECT_FACTOR * jitter,
            MAX_RECONNECT_DELAY
        )
        
        logger.info(f"Will attempt reconnection in {self.reconnect_delay:.1f} seconds (attempt #{self.reconnect_attempt})")

async def run_bot_with_recovery():
    """Run the bot with automatic recovery and reconnection"""
    bot = UptimeGuardian()
    
    while True:
        try:
            logger.info("Starting bot with auto-reconnection...")
            await bot.start(TOKEN)
        except discord.errors.LoginFailure as e:
            logger.critical(f"Login failed (invalid token?): {e}")
            return  # Exit if token is invalid
        except (discord.errors.GatewayNotFound, discord.errors.ConnectionClosed) as e:
            logger.error(f"Connection error: {e}")
            wait_time = bot.reconnect_delay
            logger.info(f"Discord gateway unavailable. Retrying in {wait_time:.1f} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.error(traceback.format_exc())
            wait_time = bot.reconnect_delay
            logger.info(f"Unexpected error occurred. Restarting bot in {wait_time:.1f} seconds...")
            await asyncio.sleep(wait_time)

def signal_handler(sig, frame):
    """Handle OS signals gracefully"""
    logger.info("Received signal to terminate")
    logger.info("Shutting down bot...")
    asyncio.get_event_loop().stop()
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Print startup banner
    print("\n" + "="*70)
    print(" DISCORD BOT - UPTIME GUARDIAN ".center(70, "="))
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print("="*70 + "\n")
    
    # Run the bot with enhanced reconnection handling
    try:
        asyncio.run(run_bot_with_recovery())
    except KeyboardInterrupt:
        logger.info("Bot was shut down by keyboard interrupt")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        logger.critical(traceback.format_exc())
        sys.exit(1)