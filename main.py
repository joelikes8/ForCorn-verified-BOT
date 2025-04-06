import os
import asyncio
import logging
import discord
from discord import app_commands
from dotenv import load_dotenv
from discord.ext import commands
from cogs.verification_commands import VerificationCommands
from cogs.group_commands import GroupCommands
from cogs.ticket_commands import TicketCommands
from cogs.moderation_commands import ModerationCommands
from config import Config
from app import app, db

# Import models to ensure they're registered with SQLAlchemy
import models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize bot with intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class RobloxGroupBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',  # Fallback prefix
            intents=intents,
            help_command=None
        )
        self.config = Config()
        
    async def setup_hook(self):
        # Load all cogs
        await self.add_cog(VerificationCommands(self))
        await self.add_cog(GroupCommands(self))
        await self.add_cog(TicketCommands(self))
        await self.add_cog(ModerationCommands(self))
        
        # Sync commands with Discord
        logger.info("Syncing commands with Discord...")
        await self.tree.sync()
        
    async def on_ready(self):
        logger.info(f"Bot is ready! Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, 
                name="for /verify commands"
            )
        )

async def main():
    # Get token from environment variable
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("No token found. Please set the DISCORD_TOKEN environment variable.")
        return
    
    # Create and start the bot
    bot = RobloxGroupBot()
    
    # Error handling for the connection
    try:
        await bot.start(token)
    except discord.errors.LoginFailure:
        logger.error("Invalid token. Please check your DISCORD_TOKEN.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if bot.is_closed():
            logger.info("Bot has been closed.")

if __name__ == "__main__":
    asyncio.run(main())
