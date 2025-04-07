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

def main():
    # Create the bot
    bot = RobloxGroupBot()
    
    # Get token from environment variable
    token = os.environ.get('DISCORD_TOKEN')
    
    if not token:
        logger.error("No Discord token found. Please set the DISCORD_TOKEN environment variable.")
        logger.info("You can set it in the .env file or export it in your terminal.")
        return
        
    # Run the bot with the token
    bot.run(token)

if __name__ == "__main__":
    main()
