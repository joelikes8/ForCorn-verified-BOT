#!/usr/bin/env python3
"""
Complete Discord Bot

This is a completely standalone Discord bot that does not import
any other modules from the project. This avoids import cycles and 
port conflicts with the web application.
"""
import os
import sys
import json
import logging
import random
import string
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("bot")

# Print a clear header
print("="*80)
print("COMPLETE DISCORD BOT - WORKFLOW MODE")
print("This is a standalone bot with no web application dependencies")
print("="*80)

# Load environment variables from .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Loaded environment variables from .env file")
except ImportError:
    logger.warning("python-dotenv not installed, skipping .env loading")

# Check for Discord token
TOKEN = os.environ.get('DISCORD_TOKEN')
if not TOKEN:
    logger.critical("DISCORD_TOKEN environment variable is not set")
    logger.critical("Please set your Discord bot token in the .env file or Secrets tab")
    sys.exit(1)

# Set up data directory for JSON storage
os.makedirs('data', exist_ok=True)

# Server config storage
SERVER_CONFIG_FILE = 'data/server_configs.json'
TICKETS_COUNTER_FILE = 'data/tickets_counter.json'
BLACKLISTED_GROUPS_FILE = 'data/blacklisted_groups.json'

# Helper functions for JSON storage
def load_json_file(file_path, default=None):
    """Load data from a JSON file"""
    if default is None:
        default = {}
    
    if not os.path.exists(file_path):
        return default
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return default

def save_json_file(file_path, data):
    """Save data to a JSON file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving to {file_path}: {e}")

# Load configurations
server_configs = load_json_file(SERVER_CONFIG_FILE)
tickets_counter = load_json_file(TICKETS_COUNTER_FILE)
blacklisted_groups = load_json_file(BLACKLISTED_GROUPS_FILE)

# Import Discord.py
try:
    import discord
    from discord import app_commands
    from discord.ext import commands
except ImportError:
    logger.critical("Failed to import discord.py")
    logger.critical("Please install discord.py with: pip install discord.py")
    sys.exit(1)

# Create Discord bot with all necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Simple handler for HTTP server (for port binding)
class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        response = f"""
        <html>
            <head>
                <title>Discord Bot Status</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                    .info {{ background-color: #e9f7fe; border-left: 4px solid #2196F3; padding: 15px; margin-bottom: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>ForCorn Discord Bot</h1>
                    <div class="info">
                        <p><strong>Status:</strong> Running</p>
                        <p><strong>Connected to:</strong> {len(bot.guilds) if bot.is_ready() else "Not connected"} servers</p>
                        <p><strong>Commands:</strong> 20 global commands available</p>
                        <p><strong>Mode:</strong> Standalone workflow</p>
                    </div>
                    <p>This is the HTTP status page for the Discord bot. The bot is running as a standalone service.</p>
                </div>
            </body>
        </html>
        """
        
        self.wfile.write(response.encode())
    
    def log_message(self, format, *args):
        logger.info(f"HTTP: {self.address_string()} - {format % args}")

# HTTP server for port binding
def start_http_server():
    """Start a minimal HTTP server for port binding"""
    # Use PORT from environment variable or default to 9000
    port = int(os.environ.get('PORT', 9000))
    
    try:
        server = HTTPServer(('0.0.0.0', port), StatusHandler)
        logger.info(f"Starting HTTP server on port {port}")
        
        # Run in a separate thread
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True  # Thread will exit when main thread exits
        server_thread.start()
        logger.info("HTTP server started successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to start HTTP server on port {port}: {e}")
        
        # Try alternative port if main port fails
        if port != 8080:
            try:
                port = 8080
                server = HTTPServer(('0.0.0.0', port), StatusHandler)
                logger.info(f"Starting HTTP server on alternative port {port}")
                
                server_thread = threading.Thread(target=server.serve_forever)
                server_thread.daemon = True
                server_thread.start()
                logger.info("HTTP server started successfully on alternative port")
                return True
            except Exception as e2:
                logger.error(f"Failed to start HTTP server on alternative port {port}: {e2}")
        
        return False

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
        # Try syncing global commands
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} global command(s)")
        
        # Sync to each guild
        for guild in bot.guilds:
            try:
                guild_commands = await bot.tree.sync(guild=discord.Object(id=guild.id))
                logger.info(f"Synced {len(guild_commands)} commands to guild {guild.name} (ID: {guild.id})")
            except Exception as e:
                logger.error(f"Failed to sync commands to guild {guild.name}: {e}")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")
    
    logger.info("Bot is ready!")

@bot.event
async def on_guild_join(guild):
    """Event triggered when the bot joins a new server"""
    logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")
    
    # Find a suitable channel for welcome message
    welcome_channel = None
    if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
        welcome_channel = guild.system_channel
    else:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                welcome_channel = channel
                break
    
    # Send welcome message
    if welcome_channel:
        embed = discord.Embed(
            title="ForCorn Bot",
            description="Thanks for adding me to your server!",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Commands",
            value="Use `/help` to see available commands",
            inline=False
        )
        try:
            await welcome_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")

# Define commands
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
    
    embed.add_field(
        name="Verification",
        value="`/verify <roblox_username>` - Verify your Roblox account\n"
              "`/update` - Update your nickname with your Roblox rank\n"
              "`/background <roblox_username>` - Check if user is in blacklisted groups",
        inline=False
    )
    
    embed.add_field(
        name="Tickets",
        value="`/ticket` - Create a support ticket\n"
              "`/closeticket` - Close a ticket channel\n"
              "`/sendticket [channel]` - Send the ticket panel to a channel",
        inline=False
    )
    
    embed.add_field(
        name="Group Management",
        value="`/rank <roblox_username> [rank_name]` - View or change a user's rank\n"
              "`/setupid <group_id>` - Set up the Roblox group ID for the server\n"
              "`/ranksetup <group_id>` - Set up the Roblox group ID for ranking\n"
              "`/setuptoken <token>` - Set up the Roblox API token for ranking",
        inline=False
    )
    
    embed.add_field(
        name="Moderation",
        value="`/kick <member> [reason]` - Kick a member from the server\n"
              "`/ban <member> [reason]` - Ban a member from the server\n"
              "`/timeout <member> <duration> [reason]` - Timeout a member\n"
              "`/antiraid <action>` - Toggle anti-raid protection",
        inline=False
    )
    
    embed.add_field(
        name="Server Setup",
        value="`/setup_roles [verified_role] [mod_role] [admin_role]` - Set up verification and moderation roles\n"
              "`/blacklistedgroups <group_id>` - Add a Roblox group to the blacklist\n"
              "`/removeblacklist <group_id>` - Remove a Roblox group from the blacklist",
        inline=False
    )
    
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
    
    embed.add_field(
        name="Features",
        value="• Roblox account verification\n"
              "• Support tickets system\n"
              "• Group rank management\n"
              "• Advanced moderation tools",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="verify", description="Verify your Roblox account")
@app_commands.describe(roblox_username="Your Roblox username")
async def verify(interaction: discord.Interaction, roblox_username: str):
    """Verify your Roblox account with your Discord account"""
    await interaction.response.defer(ephemeral=True)
    
    embed = discord.Embed(
        title="Verification Process",
        description=f"To verify as **{roblox_username}**, please follow these steps:",
        color=discord.Color.blue()
    )
    
    # Generate a verification code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    embed.add_field(
        name="Step 1",
        value=f"Go to your [Roblox Profile](https://www.roblox.com/users/profile)",
        inline=False
    )
    
    embed.add_field(
        name="Step 2",
        value="Click the pencil icon next to your display name to edit your profile",
        inline=False
    )
    
    embed.add_field(
        name="Step 3",
        value=f"Add this verification code to your About Me section:\n`{code}`",
        inline=False
    )
    
    embed.add_field(
        name="Step 4",
        value="Click the 'Verify' button below when done",
        inline=False
    )
    
    # Create verification button
    class VerifyButton(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)  # 5 minute timeout
        
        @discord.ui.button(label="Verify", style=discord.ButtonStyle.green)
        async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            # Disable the button to prevent multiple clicks
            button.disabled = True
            await interaction.response.edit_message(view=self)
            
            # In the full implementation, this would check the Roblox profile
            # and verify the user if the code is present
            await interaction.followup.send(
                f"Verification for **{roblox_username}** started! In the full version, this would verify your account.",
                ephemeral=True
            )
    
    await interaction.followup.send(embed=embed, view=VerifyButton(), ephemeral=True)

@bot.tree.command(name="ticket", description="Create a support ticket")
async def ticket(interaction: discord.Interaction):
    """Create a support ticket"""
    await interaction.response.defer(ephemeral=True)
    
    embed = discord.Embed(
        title="Ticket System",
        description="Support ticket functionality would create a new private channel here.",
        color=discord.Color.blue()
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="setupid", description="Set up the Roblox group ID for the server")
@app_commands.describe(group_id="The Roblox group ID to associate with this server")
async def setupid(interaction: discord.Interaction, group_id: str):
    """Set up the Roblox group ID for the server"""
    # Store in server config
    guild_id = str(interaction.guild.id)
    
    if guild_id not in server_configs:
        server_configs[guild_id] = {}
    
    server_configs[guild_id]["group_id"] = group_id
    save_json_file(SERVER_CONFIG_FILE, server_configs)
    
    await interaction.response.send_message(
        f"Roblox group ID set to `{group_id}` for this server.",
        ephemeral=True
    )

@bot.tree.command(name="blacklistedgroups", description="Add a Roblox group to the blacklist")
@app_commands.describe(group_id="The Roblox group ID to blacklist")
async def blacklistedgroups(interaction: discord.Interaction, group_id: str):
    """Add a Roblox group to the blacklist"""
    guild_id = str(interaction.guild.id)
    
    if guild_id not in blacklisted_groups:
        blacklisted_groups[guild_id] = []
    
    if group_id in blacklisted_groups[guild_id]:
        await interaction.response.send_message(
            f"Group ID `{group_id}` is already in the blacklist.",
            ephemeral=True
        )
        return
    
    blacklisted_groups[guild_id].append(group_id)
    save_json_file(BLACKLISTED_GROUPS_FILE, blacklisted_groups)
    
    await interaction.response.send_message(
        f"Added group ID `{group_id}` to the blacklist.",
        ephemeral=True
    )

@bot.tree.command(name="removeblacklist", description="Remove a Roblox group from the blacklist")
@app_commands.describe(group_id="The Roblox group ID to remove from the blacklist")
async def removeblacklist(interaction: discord.Interaction, group_id: str):
    """Remove a Roblox group from the blacklist"""
    guild_id = str(interaction.guild.id)
    
    if guild_id not in blacklisted_groups or group_id not in blacklisted_groups[guild_id]:
        await interaction.response.send_message(
            f"Group ID `{group_id}` is not in the blacklist.",
            ephemeral=True
        )
        return
    
    blacklisted_groups[guild_id].remove(group_id)
    save_json_file(BLACKLISTED_GROUPS_FILE, blacklisted_groups)
    
    await interaction.response.send_message(
        f"Removed group ID `{group_id}` from the blacklist.",
        ephemeral=True
    )

def main():
    """Main function to run the bot"""
    # First start the HTTP server for port binding
    start_http_server()
    
    # Then run the bot
    try:
        logger.info("Starting Discord bot...")
        bot.run(TOKEN)
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()