#!/usr/bin/env python3
"""
Standalone Discord Bot

This is a completely standalone Discord bot script that doesn't import
any other modules from the project. It's solely purpose is to run 
as an isolated Discord bot in the discord_bot workflow.

It also includes a minimal HTTP server for Render.com deployment
to satisfy the port binding requirements.
"""

import os
import sys
import logging
import traceback
import threading
import random
import string
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler

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
    
    # Ensure commands are synced, with extra safety checks
    try:
        # First try syncing without clearing
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} global command(s)")
        
        # If no commands were synced, try a more aggressive approach
        if len(synced) < 10:  # We should have at least 10 commands
            logger.warning(f"Only {len(synced)} commands synced. Attempting recovery...")
            
            # Try force sync to all guilds
            for guild in bot.guilds:
                guild_id = guild.id
                try:
                    # Force sync to this guild
                    guild_commands = await bot.tree.sync(guild=discord.Object(id=guild_id))
                    logger.info(f"Force synced {len(guild_commands)} commands to guild {guild.name} (ID: {guild_id})")
                except Exception as e:
                    logger.error(f"Failed to force sync commands to guild {guild.name}: {e}")
            
            # Try global sync one more time
            synced = await bot.tree.sync()
            logger.info(f"Re-synced {len(synced)} global command(s) after recovery attempt")
        else:
            # Normal guild sync if initial sync was successful
            for guild in bot.guilds:
                guild_id = guild.id
                try:
                    guild_commands = await bot.tree.sync(guild=discord.Object(id=guild_id))
                    logger.info(f"Synced {len(guild_commands)} commands to guild {guild.name} (ID: {guild_id})")
                except Exception as e:
                    logger.error(f"Failed to sync commands to guild {guild.name}: {e}")
        
        logger.info("All commands should now be available. If commands are still missing, they may take up to an hour to propagate through Discord's systems.")
        
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")
        logger.error(traceback.format_exc())
    
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
    
    # Generate a simple verification code
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
    
    # Create a simple button for verification
    class VerifyButton(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)  # 5 minute timeout
        
        @discord.ui.button(label="Verify", style=discord.ButtonStyle.green)
        async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            # Disable the button
            button.disabled = True
            await interaction.response.edit_message(view=self)
            
            await interaction.followup.send(
                f"Verification for **{roblox_username}** started! In the standalone version, this would verify your account.",
                ephemeral=True
            )
    
    await interaction.followup.send(embed=embed, view=VerifyButton(), ephemeral=True)
    logger.info(f"Sent verification request to {interaction.user.name} for Roblox username: {roblox_username}")

@bot.tree.command(name="ticket", description="Create a support ticket")
async def ticket(interaction: discord.Interaction):
    """Create a support ticket"""
    await interaction.response.defer(ephemeral=True)
    
    try:
        # Check if ticket system is set up
        ticket_category = None
        # In the full implementation, you'd get this from config
        
        if not ticket_category:
            embed = discord.Embed(
                title="Ticket System",
                description="The ticket system would create a support ticket here.",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Standalone Mode Notice",
                value="In standalone mode, ticket creation is simulated. In the full version, this would create a private ticket channel.",
                inline=False
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

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
    
    embed.add_field(
        name="Features",
        value="• Roblox account verification\n"
              "• Support tickets system\n"
              "• Group rank management\n"
              "• Advanced moderation tools",
        inline=False
    )
    
    embed.set_footer(text="Running in standalone mode")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rank", description="Rank a user in the Roblox group")
@app_commands.describe(
    roblox_username="The Roblox username to rank",
    rank_name="The name of the rank to give (leave empty to view current rank)"
)
async def rank(interaction: discord.Interaction, roblox_username: str, rank_name: str = None):
    """Rank a user in the Roblox group (standalone simulation)"""
    await interaction.response.defer(ephemeral=False)
    
    embed = discord.Embed(
        title="Rank Command (Standalone Mode)",
        description=f"In the full version, this would check or change the rank for **{roblox_username}**.",
        color=discord.Color.blue()
    )
    
    if rank_name:
        embed.add_field(
            name="Requested Action",
            value=f"Change rank to: **{rank_name}**",
            inline=False
        )
    else:
        embed.add_field(
            name="Requested Action",
            value=f"View current rank for: **{roblox_username}**",
            inline=False
        )
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode. The actual rank command requires database access and Roblox API connectivity.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed)
    
@bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.describe(
    member="The member to kick",
    reason="The reason for kicking the member"
)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    """Kick a member from the server"""
    await interaction.response.defer(ephemeral=True)
    
    # Check if user has kick permissions
    if not interaction.user.guild_permissions.kick_members:
        await interaction.followup.send("You don't have permission to kick members.", ephemeral=True)
        return
    
    # In standalone mode, just simulate the kick
    embed = discord.Embed(
        title="Moderation Action (Standalone Mode)",
        description=f"In the full version, this would kick **{member.name}** from the server.",
        color=discord.Color.orange()
    )
    
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode. No actual kick was performed.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.describe(
    member="The member to ban",
    reason="The reason for banning the member"
)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    """Ban a member from the server"""
    await interaction.response.defer(ephemeral=True)
    
    # Check if user has ban permissions
    if not interaction.user.guild_permissions.ban_members:
        await interaction.followup.send("You don't have permission to ban members.", ephemeral=True)
        return
    
    # In standalone mode, just simulate the ban
    embed = discord.Embed(
        title="Moderation Action (Standalone Mode)",
        description=f"In the full version, this would ban **{member.name}** from the server.",
        color=discord.Color.red()
    )
    
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode. No actual ban was performed.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="timeout", description="Timeout a member")
@app_commands.describe(
    member="The member to timeout",
    duration="Duration in minutes (max 40320 minutes / 28 days)",
    reason="The reason for timing out the member"
)
async def timeout(
    interaction: discord.Interaction, 
    member: discord.Member, 
    duration: int, 
    reason: str = None
):
    """Timeout a member for a specified duration"""
    await interaction.response.defer(ephemeral=True)
    
    # Check if user has timeout permissions
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.followup.send("You don't have permission to timeout members.", ephemeral=True)
        return
    
    # In standalone mode, just simulate the timeout
    embed = discord.Embed(
        title="Moderation Action (Standalone Mode)",
        description=f"In the full version, this would timeout **{member.name}** for {duration} minutes.",
        color=discord.Color.orange()
    )
    
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
    
    embed.add_field(
        name="Duration",
        value=f"{duration} minutes",
        inline=False
    )
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode. No actual timeout was performed.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="closeticket", description="Close a ticket channel")
async def closeticket(interaction: discord.Interaction):
    """Close a ticket channel"""
    await interaction.response.defer(ephemeral=True)
    
    # Check if the channel is a ticket (in standalone mode, just simulate)
    embed = discord.Embed(
        title="Ticket Action (Standalone Mode)",
        description="In the full version, this would close the current ticket.",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode. No actual ticket was closed.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="update", description="Update your nickname with your current Roblox group rank")
async def update(interaction: discord.Interaction):
    """Update your Discord nickname with your current Roblox group rank"""
    await interaction.response.defer(ephemeral=True)
    
    embed = discord.Embed(
        title="Nickname Update (Standalone Mode)",
        description="In the full version, this would update your nickname with your Roblox group rank.",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode. No actual nickname update was performed.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="setupid", description="Set up the Roblox group ID for the server")
@app_commands.describe(group_id="The Roblox group ID")
async def setupid(interaction: discord.Interaction, group_id: str):
    """Set up the Roblox group ID for the server"""
    await interaction.response.defer(ephemeral=True)
    
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("You need administrator permissions to use this command.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="Group Setup (Standalone Mode)",
        description=f"In the full version, this would set up Roblox group **{group_id}** for this server.",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Group ID",
        value=group_id,
        inline=False
    )
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode. No actual group setup was performed.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="ranksetup", description="Set up the Roblox group ID for ranking")
@app_commands.describe(group_id="The Roblox group ID")
async def ranksetup(interaction: discord.Interaction, group_id: str):
    """Set up the Roblox group ID for ranking users"""
    await interaction.response.defer(ephemeral=True)
    
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("You need administrator permissions to use this command.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="Rank Setup (Standalone Mode)",
        description=f"In the full version, this would set up Roblox group **{group_id}** for ranking users.",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Group ID",
        value=group_id,
        inline=False
    )
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode. No actual rank setup was performed.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="setuptoken", description="Set up the Roblox API token for ranking")
@app_commands.describe(token="Your Roblox API token (this will be encrypted)")
async def setuptoken(interaction: discord.Interaction, token: str):
    """Set up the Roblox API token for ranking users"""
    await interaction.response.defer(ephemeral=True)
    
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("You need administrator permissions to use this command.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="API Token Setup (Standalone Mode)",
        description="In the full version, this would securely store your encrypted API token.",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Security Notice",
        value="Your token would be encrypted before storage and never stored in plain text.",
        inline=False
    )
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode. No actual token was stored.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="setup_roles", description="Set up verification and moderation roles")
@app_commands.describe(
    verified_role="The role to assign to verified users",
    mod_role="The role with moderation permissions",
    admin_role="The role with admin permissions"
)
async def setup_roles(
    interaction: discord.Interaction, 
    verified_role: discord.Role = None,
    mod_role: discord.Role = None,
    admin_role: discord.Role = None
):
    """Set up verification and moderation roles"""
    await interaction.response.defer(ephemeral=True)
    
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("You need administrator permissions to use this command.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="Role Setup (Standalone Mode)",
        description="In the full version, this would configure server roles.",
        color=discord.Color.blue()
    )
    
    if verified_role:
        embed.add_field(
            name="Verified Role",
            value=f"Set to {verified_role.mention}",
            inline=False
        )
    
    if mod_role:
        embed.add_field(
            name="Moderator Role",
            value=f"Set to {mod_role.mention}",
            inline=False
        )
    
    if admin_role:
        embed.add_field(
            name="Admin Role",
            value=f"Set to {admin_role.mention}",
            inline=False
        )
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode. No actual role setup was performed.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="antiraid", description="Toggle anti-raid protection")
@app_commands.describe(
    action="Enable or disable anti-raid protection"
)
@app_commands.choices(action=[
    app_commands.Choice(name="enable", value="enable"),
    app_commands.Choice(name="disable", value="disable")
])
async def antiraid(interaction: discord.Interaction, action: str):
    """Toggle anti-raid protection"""
    await interaction.response.defer(ephemeral=True)
    
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("You need administrator permissions to use this command.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="Anti-Raid Protection (Standalone Mode)",
        description=f"In the full version, this would {action} anti-raid protection.",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Action",
        value=f"Anti-raid protection would be {action}d",
        inline=False
    )
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode. No actual changes were made to anti-raid settings.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="sendticket", description="Send the ticket panel to a channel")
@app_commands.describe(
    channel="The channel to send the ticket panel to"
)
async def sendticket(interaction: discord.Interaction, channel: discord.TextChannel = None):
    """Send the ticket panel to a channel"""
    await interaction.response.defer(ephemeral=True)
    
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("You need administrator permissions to use this command.", ephemeral=True)
        return
    
    target_channel = channel or interaction.channel
    
    embed = discord.Embed(
        title="Ticket Panel (Standalone Mode)",
        description=f"In the full version, this would send a ticket panel to {target_channel.mention}.",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode. No actual ticket panel was sent.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="blacklistedgroups", description="Add a Roblox group to the blacklist")
@app_commands.describe(
    group_id="The Roblox group ID to blacklist"
)
async def blacklistedgroups(interaction: discord.Interaction, group_id: str):
    """Add a Roblox group to the blacklist"""
    await interaction.response.defer(ephemeral=True)
    
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("You need administrator permissions to use this command.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="Blacklist Group (Standalone Mode)",
        description=f"In the full version, this would add Roblox group **{group_id}** to the blacklist.",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Group ID",
        value=group_id,
        inline=False
    )
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode. No actual group was blacklisted.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="removeblacklist", description="Remove a Roblox group from the blacklist")
@app_commands.describe(
    group_id="The Roblox group ID to remove from the blacklist"
)
async def removeblacklist(interaction: discord.Interaction, group_id: str):
    """Remove a Roblox group from the blacklist"""
    await interaction.response.defer(ephemeral=True)
    
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("You need administrator permissions to use this command.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="Remove Blacklisted Group (Standalone Mode)",
        description=f"In the full version, this would remove Roblox group **{group_id}** from the blacklist.",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Group ID",
        value=group_id,
        inline=False
    )
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode. No actual group was removed from the blacklist.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="background", description="Check if a Roblox user is in any blacklisted groups")
@app_commands.describe(
    roblox_username="The Roblox username to check"
)
async def background(interaction: discord.Interaction, roblox_username: str):
    """Check if a Roblox user is in any blacklisted groups"""
    await interaction.response.defer(ephemeral=True)
    
    embed = discord.Embed(
        title="Background Check (Standalone Mode)",
        description=f"In the full version, this would check if **{roblox_username}** is in any blacklisted groups.",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Username",
        value=roblox_username,
        inline=False
    )
    
    embed.add_field(
        name="Standalone Mode Notice",
        value="This is a simulation in standalone mode. No actual background check was performed.",
        inline=False
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

# Minimal HTTP server for Render.com port binding
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests with a simple status page"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Simple status page showing bot is running
        bot_status = "Unknown"
        if hasattr(bot, 'user') and bot.user:
            bot_status = f"Online as {bot.user.name}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ForCorn Discord Bot Status</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .status {{ padding: 20px; border-radius: 5px; background-color: #f0f0f0; }}
                .online {{ color: green; }}
                .header {{ background-color: #3498db; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>ForCorn Discord Bot</h1>
                </div>
                <div class="status">
                    <h2>Status: <span class="online">{bot_status}</span></h2>
                    <p>Connected to {len(bot.guilds) if hasattr(bot, 'guilds') else 0} Discord servers</p>
                    <p>This is a status page for the Discord bot. The bot is a separate process running alongside this web server.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Override log_message to use our logger"""
        logger.info(f"HTTP Server: {format%args}")

def start_http_server():
    """Start a minimal HTTP server for Render.com port binding"""
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 8080))
    
    # Try to use the specified port, but if it's in use, 
    # try some alternatives for Replit environment
    for attempt_port in [port, 9000, 9090, 7070, 6060]:
        try:
            server = HTTPServer(('0.0.0.0', attempt_port), SimpleHandler)
            logger.info(f"Starting HTTP server on port {attempt_port}")
            
            # Run server in a separate thread
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            logger.info(f"HTTP server thread started on port {attempt_port}")
            break
        except OSError as e:
            logger.warning(f"Port {attempt_port} is already in use, trying another port")
            if attempt_port == 6060:  # Last attempt
                logger.error("Failed to bind to any port for HTTP server")
                # Continue without HTTP server
                return

# Main function to be imported by other scripts
def main():
    logger.info("Running standalone Discord bot...")
    
    # Start HTTP server for Render.com port binding
    # Only start if PORT env var is set (Render.com sets this)
    if 'PORT' in os.environ:
        logger.info("PORT environment variable detected, starting HTTP server for Render.com")
        start_http_server()
    
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