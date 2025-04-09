"""
Reaction Actions Cog - Discord message reaction-based quick actions

This cog integrates the reaction_actions module with the Discord.py bot
and provides commands for creating and managing reaction-based quick actions.
"""

import os
import json
import logging
import discord
from discord import app_commands
from discord.ext import commands

# Import our reaction actions handler
from reaction_actions import ReactionActionHandler

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reaction_actions_cog")

class ReactionActionsCog(commands.Cog):
    """Cog for handling reaction-based quick actions"""
    
    def __init__(self, bot):
        self.bot = bot
        # Initialize the reaction handler
        self.handler = ReactionActionHandler(bot)
        # Save the handler to the bot for access from other cogs/events
        self.bot.reaction_handler = self.handler
        
        logger.info("ReactionActionsCog initialized")
    
    # === Event Listeners ===
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handle reaction add events"""
        # Ignore bot's own reactions
        if payload.user_id == self.bot.user.id:
            return
        
        # Check if this is a message we're tracking
        if payload.message_id in self.handler.active_messages:
            # Get the necessary objects
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                return
            
            channel = guild.get_channel(payload.channel_id)
            if not channel:
                return
            
            try:
                message = await channel.fetch_message(payload.message_id)
                user = guild.get_member(payload.user_id)
                
                if not message or not user:
                    return
                
                # Find the reaction
                for reaction in message.reactions:
                    if str(reaction.emoji) == str(payload.emoji):
                        await self.handler.handle_reaction_add(reaction, user)
                        break
            except Exception as e:
                logger.error(f"Error handling reaction: {e}")
    
    # === Commands ===
    
    @app_commands.command(
        name="setup_reactions",
        description="Set up a message with reaction quick actions"
    )
    @app_commands.describe(
        message_id="The ID of the message to add reactions to",
        action_type="The type of action for this message (ticket, approval, moderation, all)"
    )
    @app_commands.choices(action_type=[
        app_commands.Choice(name="Ticket Creation", value="ticket"),
        app_commands.Choice(name="Approval/Denial", value="approval"),
        app_commands.Choice(name="Moderation Actions", value="moderation"),
        app_commands.Choice(name="All Actions", value="all")
    ])
    async def setup_reactions(self, interaction: discord.Interaction, message_id: str, action_type: str):
        """Set up a message with reaction quick actions
        
        Args:
            interaction: Discord interaction object
            message_id: ID of the message to add reactions to
            action_type: Type of action for this message
        """
        # Check permissions
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "You need the 'Manage Messages' permission to use this command.",
                ephemeral=True
            )
            return
        
        try:
            # Convert message ID to int
            msg_id = int(message_id)
            
            # Try to fetch the message
            try:
                message = await interaction.channel.fetch_message(msg_id)
            except Exception:
                await interaction.response.send_message(
                    "Could not find that message in this channel.",
                    ephemeral=True
                )
                return
            
            # Set up allowed reactions based on action type
            allowed_reactions = []
            data = {}
            
            if action_type.lower() == "ticket":
                allowed_reactions = ["🎫"]
                
                # Get mod roles for ticket permissions
                mod_roles = []
                for role in interaction.guild.roles:
                    if (role.permissions.manage_messages or 
                        role.permissions.administrator or
                        "mod" in role.name.lower() or
                        "admin" in role.name.lower()):
                        mod_roles.append(role.id)
                
                data["mod_roles"] = mod_roles
                
            elif action_type.lower() == "approval":
                allowed_reactions = ["✅", "❌"]
                
                # Add target user info if it's a request
                if message.embeds and len(message.mentions) > 0:
                    data["target_user_id"] = message.mentions[0].id
                
            elif action_type.lower() == "moderation":
                allowed_reactions = ["📌", "🗑️", "⏰", "⚠️", "🔨"]
                
                # Add mod log channel if exists
                mod_log = None
                for channel in interaction.guild.channels:
                    if isinstance(channel, discord.TextChannel) and (
                        channel.permissions_for(interaction.guild.me).send_messages and
                        ("mod-log" in channel.name.lower() or 
                         "mod_log" in channel.name.lower() or
                         "modlog" in channel.name.lower())):
                        mod_log = channel.id
                        break
                
                if mod_log:
                    data["log_channel_id"] = mod_log
                
            elif action_type.lower() == "all":
                allowed_reactions = list(self.handler.actions.keys())
            else:
                await interaction.response.send_message(
                    "Invalid action type. Use 'ticket', 'approval', 'moderation', or 'all'.",
                    ephemeral=True
                )
                return
            
            # Register the message
            self.handler.register_message(
                message_id=msg_id,
                channel_id=interaction.channel.id,
                author_id=message.author.id,
                guild_id=interaction.guild.id,
                action_type=action_type.lower(),
                allowed_reactions=allowed_reactions,
                data=data
            )
            
            # Add the reactions to the message
            for emoji in allowed_reactions:
                await message.add_reaction(emoji)
            
            await interaction.response.send_message(
                f"Message has been set up with reaction quick actions for '{action_type}'.",
                ephemeral=True
            )
            
        except ValueError:
            await interaction.response.send_message(
                "Invalid message ID. Please provide a valid message ID.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error setting up reactions: {e}")
            await interaction.response.send_message(
                f"An error occurred: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(
        name="create_ticket_panel",
        description="Create a ticket panel with reaction support"
    )
    @app_commands.describe(
        channel="The channel to send the ticket panel to",
        title="The title for the ticket panel",
        description="The description for the ticket panel"
    )
    async def create_ticket_panel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel = None,
        title: str = "Support Tickets",
        description: str = "React with 🎫 to create a support ticket"
    ):
        """Create a ticket panel with reaction support
        
        Args:
            interaction: Discord interaction object
            channel: Channel to send the panel to (optional)
            title: Title for the panel (optional)
            description: Description for the panel (optional)
        """
        # Check permissions
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message(
                "You need the 'Manage Channels' permission to use this command.",
                ephemeral=True
            )
            return
        
        try:
            target_channel = channel or interaction.channel
            
            # Create the ticket panel embed
            embed = discord.Embed(
                title=title,
                description=description,
                color=discord.Color.blue()
            )
            
            # Add instructions
            embed.add_field(
                name="How to create a ticket",
                value="React with 🎫 below to create a support ticket.",
                inline=False
            )
            
            # Add footer
            embed.set_footer(text=f"Ticket system for {interaction.guild.name}")
            
            # Send the message
            panel_message = await target_channel.send(embed=embed)
            
            # Register the message
            mod_roles = []
            for role in interaction.guild.roles:
                if (role.permissions.manage_messages or 
                    role.permissions.administrator or
                    "mod" in role.name.lower() or
                    "admin" in role.name.lower()):
                    mod_roles.append(role.id)
            
            self.handler.register_message(
                message_id=panel_message.id,
                channel_id=target_channel.id,
                author_id=interaction.user.id,
                guild_id=interaction.guild.id,
                action_type="ticket",
                allowed_reactions=["🎫"],
                data={"mod_roles": mod_roles}
            )
            
            # Add the reaction
            await panel_message.add_reaction("🎫")
            
            await interaction.response.send_message(
                f"Ticket panel created in {target_channel.mention}!",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error creating ticket panel: {e}")
            await interaction.response.send_message(
                f"An error occurred: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(
        name="create_approval_panel",
        description="Create a panel for approving or denying requests"
    )
    @app_commands.describe(
        title="Title for the approval panel",
        description="Description of what's being approved",
        target_user="The user who is making the request",
        approve_action="What happens on approval",
        role="Role to assign if approved (only needed for 'assign_role' action)"
    )
    @app_commands.choices(approve_action=[
        app_commands.Choice(name="Assign Role", value="assign_role"),
        app_commands.Choice(name="Send Notification", value="notify"),
        app_commands.Choice(name="None", value="none")
    ])
    async def create_approval_panel(
        self, 
        interaction: discord.Interaction,
        title: str,
        description: str,
        target_user: discord.Member,
        approve_action: str = "none",
        role: discord.Role = None
    ):
        """Create a panel for approving or denying requests
        
        Args:
            interaction: Discord interaction object
            title: Title for the approval panel
            description: Description of what's being approved
            target_user: The user who is making the request
            approve_action: Action to take on approval
            role: Role to assign if approved (only for assign_role action)
        """
        # Check permissions
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "You need the 'Manage Roles' permission to use this command.",
                ephemeral=True
            )
            return
        
        try:
            # Validate role for assign_role action
            if approve_action == "assign_role" and not role:
                await interaction.response.send_message(
                    "You need to specify a role when using the 'assign_role' action.",
                    ephemeral=True
                )
                return
            
            # Create the approval panel embed
            embed = discord.Embed(
                title=title,
                description=description,
                color=discord.Color.gold()
            )
            
            # Add user information
            embed.add_field(
                name="Requestor",
                value=f"{target_user.mention} ({target_user.name})",
                inline=True
            )
            
            embed.add_field(
                name="Requested",
                value=f"<t:{int(discord.utils.utcnow().timestamp())}:R>",
                inline=True
            )
            
            # Add instructions
            embed.add_field(
                name="Instructions",
                value=(
                    "React with ✅ to approve this request\n"
                    "React with ❌ to deny this request"
                ),
                inline=False
            )
            
            # Add footer
            embed.set_footer(text=f"Requested by {target_user.name}")
            
            # Send the message
            panel_message = await interaction.channel.send(embed=embed)
            
            # Prepare data for the handler
            data = {
                "target_user_id": target_user.id,
                "approval_action": approve_action,
                "denial_action": "notify"
            }
            
            # Add role ID if using assign_role
            if approve_action == "assign_role" and role:
                data["role_id"] = role.id
            
            # Register the message
            self.handler.register_message(
                message_id=panel_message.id,
                channel_id=interaction.channel.id,
                author_id=interaction.user.id,
                guild_id=interaction.guild.id,
                action_type="approval",
                allowed_reactions=["✅", "❌"],
                data=data
            )
            
            # Add the reactions
            await panel_message.add_reaction("✅")
            await panel_message.add_reaction("❌")
            
            await interaction.response.send_message(
                "Approval panel created!",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error creating approval panel: {e}")
            await interaction.response.send_message(
                f"An error occurred: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(
        name="reaction_actions_help",
        description="Get help with reaction-based quick actions"
    )
    async def reaction_actions_help(self, interaction: discord.Interaction):
        """Get help with reaction-based quick actions
        
        Args:
            interaction: Discord interaction object
        """
        embed = discord.Embed(
            title="Reaction Quick Actions Help",
            description="This bot supports reaction-based quick actions for various tasks.",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Available Reactions",
            value=(
                "🎫 - Create a support ticket\n"
                "✅ - Approve a request\n"
                "❌ - Deny a request\n"
                "🔒 - Close a ticket\n"
                "📌 - Pin a message\n"
                "🗑️ - Delete a message (mod only)\n"
                "⏰ - Timeout the user (mod only)\n"
                "⚠️ - Warn the user (mod only)\n"
                "🔨 - Kick the user (mod only)"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Commands",
            value=(
                "/setup_reactions - Set up reactions on an existing message\n"
                "/create_ticket_panel - Create a ticket panel with reaction support\n"
                "/create_approval_panel - Create a panel for approving/denying requests\n"
                "/reaction_actions_help - Show this help message"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Required Permissions",
            value=(
                "Manage Messages - For setting up reactions and moderation actions\n"
                "Manage Channels - For creating ticket panels\n"
                "Manage Roles - For approval panels with role assignment"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    """Add the cog to the bot"""
    await bot.add_cog(ReactionActionsCog(bot))
    # Sync commands to make them available immediately
    bot.tree.sync()
    logger.info("ReactionActionsCog added to bot")