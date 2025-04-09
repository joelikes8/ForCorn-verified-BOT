"""
Workflow-Specific Discord Bot

This is a special version of the Discord bot designed specifically for the 'discord_bot' workflow.
It does not import any Flask-related modules or attempt to start a web server on port 5000.
"""

import os
import sys
import json
import logging
import threading
import traceback
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import asyncio
import aiohttp
import discord
from discord import app_commands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("workflow_bot")

# Configuration constants
TOKEN = os.environ.get('DISCORD_TOKEN')
HTTP_PORT = int(os.environ.get('PORT', '9000'))  # Use port 9000 by default for the workflow
BLACKLISTED_GROUPS_FILE = 'data/blacklisted_groups.json'

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

def load_blacklisted_groups():
    """Load blacklisted groups from file"""
    if not os.path.exists(BLACKLISTED_GROUPS_FILE):
        return {}
    try:
        with open(BLACKLISTED_GROUPS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading blacklisted groups: {e}")
        return {}

def save_blacklisted_groups(blacklisted_groups):
    """Save blacklisted groups to file"""
    try:
        with open(BLACKLISTED_GROUPS_FILE, 'w') as f:
            json.dump(blacklisted_groups, f)
    except Exception as e:
        logger.error(f"Error saving blacklisted groups: {e}")

# Initialize blacklisted groups
blacklisted_groups = load_blacklisted_groups()

async def get_user_id_from_username(username):
    """Get Roblox user ID from username using Roblox API"""
    async with aiohttp.ClientSession() as session:
        try:
            url = f"https://api.roblox.com/users/get-by-username?username={username}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if "Id" in data:
                        return data["Id"]
                    logger.warning(f"User ID not found for {username}")
                    return None
                else:
                    logger.warning(f"Failed to get user ID for {username}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting user ID for {username}: {e}")
            return None

async def get_user_groups(user_id):
    """Get groups a user belongs to using Roblox API"""
    async with aiohttp.ClientSession() as session:
        try:
            url = f"https://groups.roblox.com/v2/users/{user_id}/groups/roles"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    logger.warning(f"Failed to get groups for user {user_id}: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting groups for user {user_id}: {e}")
            return []

@bot.event
async def on_ready():
    """Event triggered when the bot is connected and ready"""
    logger.info(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    logger.info(f'Connected to {len(bot.guilds)} servers')
    
    # Sync commands with Discord
    try:
        synced = await tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

@tree.command(name="ping", description="Check if the bot is responsive")
async def ping_command(interaction: discord.Interaction):
    """Simple ping command to test if the bot is working"""
    await interaction.response.send_message("Pong! Bot is working correctly.", ephemeral=True)

@tree.command(name="blacklist", description="Add a Roblox group to the blacklist")
async def blacklist_command(interaction: discord.Interaction, group_id: str):
    """Add a Roblox group to the blacklist"""
    # Defer the response to allow time for processing
    await interaction.response.defer(ephemeral=True)
    
    guild_id = str(interaction.guild_id)
    
    # Initialize guild in blacklist if not present
    if guild_id not in blacklisted_groups:
        blacklisted_groups[guild_id] = []
    
    # Check if already blacklisted
    group_id_str = str(group_id)
    if group_id_str in blacklisted_groups[guild_id]:
        await interaction.followup.send(f"Group with ID {group_id} is already blacklisted.", ephemeral=True)
        return
    
    # Add to blacklist
    blacklisted_groups[guild_id].append(group_id_str)
    save_blacklisted_groups(blacklisted_groups)
    
    await interaction.followup.send(f"Group with ID {group_id} has been added to the blacklist.", ephemeral=True)

@tree.command(name="unblacklist", description="Remove a Roblox group from the blacklist")
async def unblacklist_command(interaction: discord.Interaction, group_id: str):
    """Remove a Roblox group from the blacklist"""
    # Defer the response to allow time for processing
    await interaction.response.defer(ephemeral=True)
    
    guild_id = str(interaction.guild_id)
    
    # Check if the guild has any blacklisted groups
    if guild_id not in blacklisted_groups or not blacklisted_groups[guild_id]:
        await interaction.followup.send("This server doesn't have any blacklisted groups.", ephemeral=True)
        return
    
    # Check if the group is blacklisted
    group_id_str = str(group_id)
    if group_id_str not in blacklisted_groups[guild_id]:
        await interaction.followup.send(f"Group with ID {group_id} is not blacklisted.", ephemeral=True)
        return
    
    # Remove from blacklist
    blacklisted_groups[guild_id].remove(group_id_str)
    save_blacklisted_groups(blacklisted_groups)
    
    await interaction.followup.send(f"Group with ID {group_id} has been removed from the blacklist.", ephemeral=True)

@tree.command(name="background", description="Check if a Roblox user is in blacklisted groups")
async def background_command(interaction: discord.Interaction, roblox_username: str):
    """Check if a Roblox user is in any blacklisted groups"""
    # Defer the response to allow time for API requests
    await interaction.response.defer(ephemeral=True)
    
    guild_id = str(interaction.guild_id)
    
    # Check if the guild has any blacklisted groups
    if guild_id not in blacklisted_groups or not blacklisted_groups[guild_id]:
        await interaction.followup.send("This server doesn't have any blacklisted groups configured.", ephemeral=True)
        return
    
    # Get Roblox user ID from username
    user_id = await get_user_id_from_username(roblox_username)
    if not user_id:
        embed = discord.Embed(
            title="User Not Found",
            description=f"Could not find Roblox user with username **{roblox_username}**.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    # Get groups user is in
    user_groups = await get_user_groups(user_id)
    
    # Initialize variables
    flagged_groups = []
    user_group_ids = []
    
    # Extract group IDs
    for group_data in user_groups:
        group = group_data.get("group", {})
        group_id = str(group.get("id", ""))
        group_name = group.get("name", "Unknown Group")
        
        user_group_ids.append(group_id)
        
        # Check if this group is blacklisted
        if group_id in blacklisted_groups[guild_id]:
            flagged_groups.append((group_id, group_name))
    
    # Create response
    if flagged_groups:
        embed = discord.Embed(
            title="⚠️ Blacklisted Groups Detected",
            description=f"**{roblox_username}** is in the following blacklisted groups:",
            color=discord.Color.red()
        )
        
        for group_id, group_name in flagged_groups:
            embed.add_field(
                name=group_name,
                value=f"Group ID: {group_id}",
                inline=False
            )
    else:
        embed = discord.Embed(
            title="Background Check Passed",
            description=f"**{roblox_username}** is not in any blacklisted groups.",
            color=discord.Color.green()
        )
        
        # Add total group count
        if user_groups:
            embed.add_field(
                name="Group Membership",
                value=f"User is in {len(user_groups)} groups, none of which are blacklisted.",
                inline=False
            )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests with a simple status page"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        message = f"""
        <html>
        <head>
            <title>ForCorn Bot Status</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .status {{ padding: 20px; background-color: #f0f8ff; border-radius: 5px; }}
                .success {{ color: green; }}
            </style>
        </head>
        <body>
            <h1>ForCorn Discord Bot</h1>
            <div class="status">
                <h2>Bot Status: <span class="success">Running</span></h2>
                <p><strong>Connected as:</strong> {bot.user.name if bot and bot.user else 'Not connected'}</p>
                <p><strong>Servers:</strong> {len(bot.guilds) if bot else 0}</p>
                <p><strong>Running in workflow mode on port:</strong> {HTTP_PORT}</p>
                <p><strong>Started at:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            <p>This is a status page for the Discord bot. The bot is running in workflow mode.</p>
        </body>
        </html>
        """
        
        self.wfile.write(message.encode())

def start_http_server():
    """Start a minimal HTTP server for port binding"""
    try:
        server = HTTPServer(('0.0.0.0', HTTP_PORT), SimpleHandler)
        logger.info(f"Starting HTTP server on port {HTTP_PORT}")
        
        # Start in a separate thread so it doesn't block the bot
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        logger.info("HTTP server started successfully")
    except Exception as e:
        logger.error(f"Failed to start HTTP server on port {HTTP_PORT}: {e}")

def main():
    """Main function to run the bot"""
    # Make sure the data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Start the HTTP server for port binding
    start_http_server()
    
    # Run the bot
    try:
        logger.info("Starting Discord bot in workflow mode...")
        bot.run(TOKEN)
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        logger.critical(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()