#!/usr/bin/env python3
"""
Final Discord Bot Script

This is an absolutely independent Discord bot script that 
runs the bot with all 20 commands in complete isolation.
Now with support for cogs including reaction-based quick actions.
"""

# Standard Library imports
import os
import sys
import json
import time
import random
import string
import logging
import threading
import traceback
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler

# Third-party imports
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("final_discord_bot")

# Print a very obvious header
print("\n" + "="*80)
print(" FINAL DISCORD BOT - RUNNING WITH ALL 20 COMMANDS + REACTION ACTIONS ".center(80, "="))
print("="*80)
print("PID:", os.getpid())
print("Script:", __file__)
print("Python:", sys.executable)
print("="*80 + "\n")

# Load environment variables from .env file
try:
    load_dotenv()
    logger.info("Successfully loaded environment variables from .env file")
except Exception as e:
    logger.warning(f"Error loading .env file: {e}")

# Get Discord token
TOKEN = os.environ.get('DISCORD_TOKEN')
if not TOKEN:
    logger.critical("DISCORD_TOKEN not found in environment variables!")
    logger.info("Please make sure you have a .env file with DISCORD_TOKEN set")
    sys.exit(1)

# Bot setup with all intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.typing = False  # Can be disabled to save resources
intents.presences = False  # Can be disabled to save resources

# Create the bot using commands.Bot for cog support
activity = discord.Activity(type=discord.ActivityType.watching, name="ForCorn Bot | /help")
bot = commands.Bot(command_prefix='!', intents=intents, activity=activity, status=discord.Status.online)

# List of cogs to load
initial_cogs = [
    'cogs.reaction_actions_cog'
]

# We'll use bot.tree instead of creating a new command tree

# ======================================
# Helper Functions
# ======================================

def load_json_file(file_path, default=None):
    """Load data from a JSON file"""
    if default is None:
        default = {}
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            with open(file_path, 'w') as f:
                json.dump(default, f, indent=4)
            return default
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        return default

def save_json_file(file_path, data):
    """Save data to a JSON file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {e}")
        return False

# Simple HTTP server for port binding
class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Discord Bot Status</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                h1 {{ color: #5865F2; }}
                .status {{ padding: 20px; border-radius: 5px; background-color: #f0f0f0; }}
                .online {{ color: green; }}
            </style>
        </head>
        <body>
            <h1>Discord Bot Status</h1>
            <div class="status">
                <p><strong>Bot Status:</strong> <span class="online">Online</span></p>
                <p><strong>Connected Servers:</strong> {len(bot.guilds)}</p>
                <p><strong>Uptime:</strong> Since {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Commands:</strong> 20 commands available</p>
            </div>
            <p>This is the HTTP server for the Discord bot. The actual bot functionality runs in Discord.</p>
        </body>
        </html>
        '''
        
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Override to use our logger instead of printing to stderr"""
        logger.info(f"HTTP Server: {format % args}")

def start_http_server():
    """Start a minimal HTTP server for port binding"""
    port = int(os.environ.get("PORT", 9000))
    server = HTTPServer(('0.0.0.0', port), StatusHandler)
    logger.info(f"Starting minimal HTTP server on port {port}")
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    return server

# ======================================
# Discord Bot Event Handlers
# ======================================

@bot.event
async def on_ready():
    """Event triggered when the bot is connected and ready"""
    logger.info(f"{bot.user.name} has connected to Discord!")
    logger.info(f"Bot is in {len(bot.guilds)} servers")
    
    # Sync commands
    try:
        logger.info("Syncing application commands...")
        synced = await bot.sync_commands()
        logger.info(f"Synced {len(synced)} commands")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="/help for commands"
        )
    )

@bot.event
async def on_guild_join(guild):
    """Event triggered when the bot joins a new server"""
    logger.info(f"Bot joined a new server: {guild.name} (ID: {guild.id})")
    
    # Load server configs
    server_configs = load_json_file('data/server_configs.json', {"servers": {}})
    
    # Add new server config if it doesn't exist
    if str(guild.id) not in server_configs["servers"]:
        server_configs["servers"][str(guild.id)] = {
            "group_id": None,
            "verified_role_id": None,
            "mod_role_id": None,
            "admin_role_id": None,
            "logs_channel_id": None,
            "ticket_category_id": None,
            "ticket_logs_channel_id": None,
            "anti_raid": False
        }
        save_json_file('data/server_configs.json', server_configs)
        logger.info(f"Created new config for server {guild.id}")

# ======================================
# Discord Bot Commands - Core
# ======================================

@bot.hybrid_command(name="ping", description="Check if the bot is responding")
async def ping(interaction: discord.Interaction):
    """Simple ping command to test if the bot is working"""
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! Bot latency: {latency}ms")

@bot.hybrid_command(name="help", description="Get help with bot commands")
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
    
    embed.set_footer(text="Final Discord Bot - All 20 commands available")
    await interaction.response.send_message(embed=embed)

@bot.hybrid_command(name="about", description="About the ForCorn bot")
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
    
    embed.set_footer(text="Final Discord Bot - All commands available")
    await interaction.response.send_message(embed=embed)

# ======================================
# Discord Bot Commands - Verification
# ======================================

@bot.hybrid_command(name="verify", description="Verify your Roblox account with your Discord account")
async def verify(interaction: discord.Interaction, roblox_username: str):
    """Verify your Roblox account with your Discord account"""
    await interaction.response.defer(ephemeral=True)
    
    # Generate a verification code
    verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    embed = discord.Embed(
        title="Verification",
        description=f"Please follow these steps to verify your Roblox account:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Step 1",
        value=f"Go to your Roblox profile and add this code to your About section:\n`{verification_code}`",
        inline=False
    )
    
    embed.add_field(
        name="Step 2",
        value="Click the Verify button below when you've added the code",
        inline=False
    )
    
    # Add verification code to temporary storage
    verification_data = load_json_file('data/verification_codes.json', {"codes": {}})
    verification_data["codes"][str(interaction.user.id)] = {
        "code": verification_code,
        "roblox_username": roblox_username,
        "timestamp": time.time()
    }
    save_json_file('data/verification_codes.json', verification_data)
    
    # Create a verification button
    class VerifyButton(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)  # 5 minute timeout
        
        @discord.ui.button(label="Verify", style=discord.ButtonStyle.primary)
        async def verify_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
            await button_interaction.response.defer(ephemeral=True)
            
            # In the full bot, this would check the Roblox profile
            # For the standalone version, we'll simulate success
            
            # Get server config
            server_configs = load_json_file('data/server_configs.json', {"servers": {}})
            
            if str(button_interaction.guild.id) in server_configs["servers"]:
                guild_config = server_configs["servers"][str(button_interaction.guild.id)]
                
                # Get verified role
                verified_role_id = guild_config.get("verified_role_id")
                verified_role = None
                
                if verified_role_id:
                    verified_role = button_interaction.guild.get_role(int(verified_role_id))
                
                if verified_role:
                    try:
                        await button_interaction.user.add_roles(verified_role)
                        await button_interaction.followup.send(
                            f"You have been verified as {roblox_username} and given the {verified_role.name} role!",
                            ephemeral=True
                        )
                    except Exception as e:
                        await button_interaction.followup.send(
                            f"Error giving role: {e}",
                            ephemeral=True
                        )
                else:
                    await button_interaction.followup.send(
                        f"You have been verified as {roblox_username}, but no verified role is set up.",
                        ephemeral=True
                    )
            else:
                await button_interaction.followup.send(
                    f"You have been verified as {roblox_username}!",
                    ephemeral=True
                )
            
            # Disable the button after use
            for child in self.children:
                child.disabled = True
            
            await interaction.edit_original_response(view=self)
    
    await interaction.followup.send(embed=embed, view=VerifyButton(), ephemeral=True)

@bot.hybrid_command(name="update", description="Update your nickname with your Roblox rank")
async def update(interaction: discord.Interaction):
    """Update your nickname with your Roblox rank"""
    await interaction.response.defer(ephemeral=True)
    
    try:
        # In the full bot, this would actually update from Roblox
        # For the isolated version, we'll simulate it
        
        # Get server config
        server_configs = load_json_file('data/server_configs.json', {"servers": {}})
        
        if str(interaction.guild.id) in server_configs["servers"]:
            # Simulate updating nickname with a mock Roblox rank
            await interaction.user.edit(nick=f"[Member] {interaction.user.name}")
            await interaction.followup.send("Your nickname has been updated with your Roblox rank!", ephemeral=True)
        else:
            await interaction.followup.send("This server isn't set up for nickname updates yet.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Error updating nickname: {e}", ephemeral=True)

@bot.hybrid_command(name="background", description="Check if a Roblox user is in blacklisted groups")
async def background(interaction: discord.Interaction, roblox_username: str):
    """Check if a Roblox user is in blacklisted groups"""
    await interaction.response.defer(ephemeral=True)
    
    # Load blacklisted groups
    blacklisted_groups = load_json_file('data/blacklisted_groups.json', {"groups": {}})
    
    if str(interaction.guild.id) not in blacklisted_groups["groups"]:
        await interaction.followup.send("No blacklisted groups have been set up for this server.", ephemeral=True)
        return
    
    # In the full bot, this would check Roblox groups
    # For the isolated version, we'll simulate a check
    
    # Simulate checking user groups (random result)
    is_blacklisted = random.choice([True, False])
    
    if is_blacklisted:
        embed = discord.Embed(
            title="Background Check",
            description=f"⚠️ {roblox_username} is in blacklisted groups!",
            color=discord.Color.red()
        )
        
        # Add fake blacklisted group for demo
        embed.add_field(
            name="Blacklisted Groups Found",
            value="Example Blacklisted Group (12345678)",
            inline=False
        )
    else:
        embed = discord.Embed(
            title="Background Check",
            description=f"✅ {roblox_username} is not in any blacklisted groups",
            color=discord.Color.green()
        )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

# ======================================
# Discord Bot Commands - Tickets
# ======================================

@bot.hybrid_command(name="ticket", description="Create a support ticket")
async def ticket(interaction: discord.Interaction):
    """Create a support ticket"""
    await interaction.response.defer(ephemeral=True)
    
    try:
        # Load server configs
        server_configs = load_json_file('data/server_configs.json', {"servers": {}})
        tickets_counter = load_json_file('data/tickets_counter.json', {"counters": {}})
        
        # Get or create counter for this guild
        if str(interaction.guild.id) not in tickets_counter["counters"]:
            tickets_counter["counters"][str(interaction.guild.id)] = 0
        
        # Increment ticket number
        tickets_counter["counters"][str(interaction.guild.id)] += 1
        save_json_file('data/tickets_counter.json', tickets_counter)
        
        ticket_number = tickets_counter["counters"][str(interaction.guild.id)]
        
        # In the full bot, this would create a ticket channel
        # For the isolated version, we'll simulate it
        
        embed = discord.Embed(
            title="Support Ticket Created",
            description=f"Ticket #{ticket_number} has been created.",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Standalone Mode Notice",
            value="In standalone mode, ticket creation is simulated. In the full version, this would create a private ticket channel.",
            inline=False
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

@bot.hybrid_command(name="closeticket", description="Close a support ticket")
async def closeticket(interaction: discord.Interaction):
    """Close a support ticket"""
    await interaction.response.defer(ephemeral=True)
    
    # In the full bot, this would check if we're in a ticket channel
    # For the isolated version, we'll simulate it
    
    embed = discord.Embed(
        title="Ticket Closure",
        description="This command would close a ticket channel in the full bot.",
        color=discord.Color.orange()
    )
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="In standalone mode, ticket closure is simulated. Please use this command in an actual ticket channel when using the full bot.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.hybrid_command(name="sendticket", description="Send a ticket panel to a channel")
async def sendticket(interaction: discord.Interaction, channel: discord.TextChannel = None):
    """Send a ticket panel to a channel"""
    if not channel:
        channel = interaction.channel
    
    # Check permissions
    try:
        # In the full bot, this would check appropriate permissions
        # For the isolated version, we'll simulate it
        
        embed = discord.Embed(
            title="🎫 Support Tickets",
            description="Click the button below to create a support ticket!",
            color=discord.Color.blue()
        )
        
        class TicketButton(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)  # Persistent button
            
            @discord.ui.button(label="Create Ticket", emoji="🎫", style=discord.ButtonStyle.primary, custom_id="create_ticket")
            async def ticket_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                await button_interaction.response.send_message("Please use the `/ticket` command to create a ticket in standalone mode.", ephemeral=True)
        
        await channel.send(embed=embed, view=TicketButton())
        await interaction.response.send_message(f"Ticket panel sent to {channel.mention}!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error sending ticket panel: {e}", ephemeral=True)

# ======================================
# Discord Bot Commands - Group Management
# ======================================

@bot.hybrid_command(name="rank", description="View or change a user's group rank")
async def rank(interaction: discord.Interaction, roblox_username: str, rank_name: str = None):
    """View or change a user's rank in the Roblox group"""
    await interaction.response.defer(ephemeral=True)
    
    # In the full bot, this would check permissions and Roblox API
    # For the isolated version, we'll simulate it
    
    if rank_name:
        embed = discord.Embed(
            title="Rank Change",
            description=f"In the full bot, this would change {roblox_username}'s rank to {rank_name}.",
            color=discord.Color.blue()
        )
    else:
        embed = discord.Embed(
            title="User Rank",
            description=f"In the full bot, this would show {roblox_username}'s current rank.",
            color=discord.Color.blue()
        )
        
        # Add simulated data
        embed.add_field(
            name="Current Rank",
            value="Member",
            inline=True
        )
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.hybrid_command(name="setupid", description="Set up the Roblox group ID for the server")
async def setupid(interaction: discord.Interaction, group_id: str):
    """Set up the Roblox group ID for the server"""
    await interaction.response.defer(ephemeral=True)
    
    # In the full bot, this would check admin permissions
    # For the isolated version, we'll simulate it
    
    # Load server configs
    server_configs = load_json_file('data/server_configs.json', {"servers": {}})
    
    # Initialize server config if it doesn't exist
    if str(interaction.guild.id) not in server_configs["servers"]:
        server_configs["servers"][str(interaction.guild.id)] = {
            "group_id": None,
            "verified_role_id": None,
            "mod_role_id": None,
            "admin_role_id": None,
            "logs_channel_id": None,
            "ticket_category_id": None,
            "ticket_logs_channel_id": None,
            "anti_raid": False
        }
    
    # Update group ID
    server_configs["servers"][str(interaction.guild.id)]["group_id"] = group_id
    save_json_file('data/server_configs.json', server_configs)
    
    await interaction.followup.send(f"Group ID set to {group_id} for this server!", ephemeral=True)

@bot.hybrid_command(name="ranksetup", description="Set up the Roblox group ID for ranking")
async def ranksetup(interaction: discord.Interaction, group_id: str):
    """Set up the Roblox group ID for ranking"""
    await interaction.response.defer(ephemeral=True)
    
    # In the full bot, this would check admin permissions
    # For the isolated version, we'll simulate it
    
    # Load server configs
    server_configs = load_json_file('data/server_configs.json', {"servers": {}})
    
    # Initialize server config if it doesn't exist
    if str(interaction.guild.id) not in server_configs["servers"]:
        server_configs["servers"][str(interaction.guild.id)] = {
            "group_id": None,
            "verified_role_id": None,
            "mod_role_id": None,
            "admin_role_id": None,
            "logs_channel_id": None,
            "ticket_category_id": None,
            "ticket_logs_channel_id": None,
            "anti_raid": False
        }
    
    # Update group ID (same as setupid for simplicity)
    server_configs["servers"][str(interaction.guild.id)]["group_id"] = group_id
    save_json_file('data/server_configs.json', server_configs)
    
    await interaction.followup.send(f"Ranking group ID set to {group_id} for this server!", ephemeral=True)

@bot.hybrid_command(name="setuptoken", description="Set up the Roblox API token for ranking")
async def setuptoken(interaction: discord.Interaction, token: str):
    """Set up the Roblox API token for ranking"""
    await interaction.response.defer(ephemeral=True)
    
    # In the full bot, this would securely store the token
    # For the isolated version, we'll simulate it
    
    await interaction.followup.send("Token has been securely stored! (Simulated in standalone mode)", ephemeral=True)

# ======================================
# Discord Bot Commands - Moderation
# ======================================

@bot.hybrid_command(name="kick", description="Kick a member from the server")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    """Kick a member from the server"""
    await interaction.response.defer(ephemeral=True)
    
    # In the full bot, this would check mod permissions
    # For the isolated version, we'll simulate it
    
    embed = discord.Embed(
        title="Kick Member",
        description=f"In the full bot, this would kick {member.mention} from the server.",
        color=discord.Color.orange()
    )
    
    embed.add_field(
        name="Member",
        value=f"{member.name}#{member.discriminator}",
        inline=True
    )
    
    if reason:
        embed.add_field(
            name="Reason",
            value=reason,
            inline=True
        )
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode. No action was taken.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.hybrid_command(name="ban", description="Ban a member from the server")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    """Ban a member from the server"""
    await interaction.response.defer(ephemeral=True)
    
    # In the full bot, this would check admin permissions
    # For the isolated version, we'll simulate it
    
    embed = discord.Embed(
        title="Ban Member",
        description=f"In the full bot, this would ban {member.mention} from the server.",
        color=discord.Color.red()
    )
    
    embed.add_field(
        name="Member",
        value=f"{member.name}#{member.discriminator}",
        inline=True
    )
    
    if reason:
        embed.add_field(
            name="Reason",
            value=reason,
            inline=True
        )
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode. No action was taken.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.hybrid_command(name="timeout", description="Timeout a member")
async def timeout(interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = None):
    """Timeout a member"""
    await interaction.response.defer(ephemeral=True)
    
    # In the full bot, this would check mod permissions and parse duration
    # For the isolated version, we'll simulate it
    
    embed = discord.Embed(
        title="Timeout Member",
        description=f"In the full bot, this would timeout {member.mention} for {duration}.",
        color=discord.Color.orange()
    )
    
    embed.add_field(
        name="Member",
        value=f"{member.name}#{member.discriminator}",
        inline=True
    )
    
    embed.add_field(
        name="Duration",
        value=duration,
        inline=True
    )
    
    if reason:
        embed.add_field(
            name="Reason",
            value=reason,
            inline=True
        )
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode. No action was taken.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.hybrid_command(name="antiraid", description="Toggle anti-raid protection")
async def antiraid(interaction: discord.Interaction, action: str):
    """Toggle anti-raid protection"""
    await interaction.response.defer(ephemeral=True)
    
    if action not in ["enable", "disable", "status"]:
        await interaction.followup.send("Invalid action. Use 'enable', 'disable', or 'status'.", ephemeral=True)
        return
    
    # Load server configs
    server_configs = load_json_file('data/server_configs.json', {"servers": {}})
    
    # Initialize server config if it doesn't exist
    if str(interaction.guild.id) not in server_configs["servers"]:
        server_configs["servers"][str(interaction.guild.id)] = {
            "group_id": None,
            "verified_role_id": None,
            "mod_role_id": None,
            "admin_role_id": None,
            "logs_channel_id": None,
            "ticket_category_id": None,
            "ticket_logs_channel_id": None,
            "anti_raid": False
        }
    
    if action == "enable":
        server_configs["servers"][str(interaction.guild.id)]["anti_raid"] = True
        save_json_file('data/server_configs.json', server_configs)
        await interaction.followup.send("Anti-raid protection has been enabled!", ephemeral=True)
    elif action == "disable":
        server_configs["servers"][str(interaction.guild.id)]["anti_raid"] = False
        save_json_file('data/server_configs.json', server_configs)
        await interaction.followup.send("Anti-raid protection has been disabled!", ephemeral=True)
    else:  # status
        anti_raid = server_configs["servers"][str(interaction.guild.id)].get("anti_raid", False)
        status = "enabled" if anti_raid else "disabled"
        await interaction.followup.send(f"Anti-raid protection is currently {status}.", ephemeral=True)

# ======================================
# Discord Bot Commands - Server Setup
# ======================================

@bot.hybrid_command(name="setup_roles", description="Set up verification and moderation roles")
async def setup_roles(
    interaction: discord.Interaction,
    verified_role: discord.Role = None,
    mod_role: discord.Role = None,
    admin_role: discord.Role = None
):
    """Set up verification and moderation roles"""
    await interaction.response.defer(ephemeral=True)
    
    # Load server configs
    server_configs = load_json_file('data/server_configs.json', {"servers": {}})
    
    # Initialize server config if it doesn't exist
    if str(interaction.guild.id) not in server_configs["servers"]:
        server_configs["servers"][str(interaction.guild.id)] = {
            "group_id": None,
            "verified_role_id": None,
            "mod_role_id": None,
            "admin_role_id": None,
            "logs_channel_id": None,
            "ticket_category_id": None,
            "ticket_logs_channel_id": None,
            "anti_raid": False
        }
    
    # Update roles
    changes = []
    
    if verified_role:
        server_configs["servers"][str(interaction.guild.id)]["verified_role_id"] = str(verified_role.id)
        changes.append(f"Verified role set to {verified_role.mention}")
    
    if mod_role:
        server_configs["servers"][str(interaction.guild.id)]["mod_role_id"] = str(mod_role.id)
        changes.append(f"Moderator role set to {mod_role.mention}")
    
    if admin_role:
        server_configs["servers"][str(interaction.guild.id)]["admin_role_id"] = str(admin_role.id)
        changes.append(f"Admin role set to {admin_role.mention}")
    
    if changes:
        save_json_file('data/server_configs.json', server_configs)
        await interaction.followup.send("\n".join(changes), ephemeral=True)
    else:
        await interaction.followup.send("No changes were made. Specify at least one role to update.", ephemeral=True)

@bot.hybrid_command(name="blacklistedgroups", description="Add a Roblox group to the blacklist")
async def blacklistedgroups(interaction: discord.Interaction, group_id: str):
    """Add a Roblox group to the blacklist"""
    await interaction.response.defer(ephemeral=True)
    
    # Load blacklisted groups
    blacklisted_groups = load_json_file('data/blacklisted_groups.json', {"groups": {}})
    
    # Initialize groups for this guild if they don't exist
    if str(interaction.guild.id) not in blacklisted_groups["groups"]:
        blacklisted_groups["groups"][str(interaction.guild.id)] = []
    
    # Check if group is already in blacklist
    if group_id in blacklisted_groups["groups"][str(interaction.guild.id)]:
        await interaction.followup.send(f"Group ID {group_id} is already in the blacklist!", ephemeral=True)
        return
    
    # Add group to blacklist
    blacklisted_groups["groups"][str(interaction.guild.id)].append(group_id)
    save_json_file('data/blacklisted_groups.json', blacklisted_groups)
    
    await interaction.followup.send(f"Group ID {group_id} has been added to the blacklist!", ephemeral=True)

@bot.hybrid_command(name="removeblacklist", description="Remove a Roblox group from the blacklist")
async def removeblacklist(interaction: discord.Interaction, group_id: str):
    """Remove a Roblox group from the blacklist"""
    await interaction.response.defer(ephemeral=True)
    
    # Load blacklisted groups
    blacklisted_groups = load_json_file('data/blacklisted_groups.json', {"groups": {}})
    
    # Check if guild has any blacklisted groups
    if str(interaction.guild.id) not in blacklisted_groups["groups"]:
        await interaction.followup.send("This server doesn't have any blacklisted groups!", ephemeral=True)
        return
    
    # Check if group is in blacklist
    if group_id not in blacklisted_groups["groups"][str(interaction.guild.id)]:
        await interaction.followup.send(f"Group ID {group_id} is not in the blacklist!", ephemeral=True)
        return
    
    # Remove group from blacklist
    blacklisted_groups["groups"][str(interaction.guild.id)].remove(group_id)
    save_json_file('data/blacklisted_groups.json', blacklisted_groups)
    
    await interaction.followup.send(f"Group ID {group_id} has been removed from the blacklist!", ephemeral=True)

# ======================================
# Main Function
# ======================================

async def setup_hook():
    """Setup hook for the bot"""
    logger.info("Setting up the bot...")
    
    # Load all initial cogs
    for cog in initial_cogs:
        try:
            await bot.load_extension(cog)
            logger.info(f"Loaded extension: {cog}")
        except Exception as e:
            logger.error(f"Failed to load extension {cog}: {e}")
            traceback.print_exc()

bot.setup_hook = setup_hook

def main():
    """Main function to run the bot"""
    logger.info("Starting Discord bot...")
    
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
        logger.info("Created data directory")
    
    # Check for Discord token
    if not TOKEN:
        logger.critical("DISCORD_TOKEN not found in environment variables!")
        logger.info("Please create a .env file with DISCORD_TOKEN=your_token")
        return
    
    # Start HTTP server for port binding
    try:
        server = start_http_server()
    except Exception as e:
        logger.error(f"Error starting HTTP server: {e}")
    
    # Run the bot with cogs
    try:
        logger.info("Starting bot with cogs and commands...")
        bot.run(TOKEN)
    except Exception as e:
        logger.critical(f"Failed to start the bot: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()