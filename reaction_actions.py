#!/usr/bin/env python3
"""
Reaction-Based Quick Actions for Discord Bot

This module provides functionality for reacting to Discord message reactions.
Users can trigger actions by adding specific emoji reactions to bot messages.

Features:
- Ticket management via reactions
- Message moderation (delete, pin)
- User actions (kick, timeout)
- Message approvals/disapprovals
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Union, Optional, Any, Tuple

# Import discord.py - required for the reaction handling
try:
    import discord
    from discord.ext import commands
except ImportError:
    # Provide friendly error message
    print("ERROR: discord.py package is not installed!")
    print("Please install it using: pip install discord.py")
    # Define empty classes for type hinting to prevent errors
    class discord:
        class Client: pass
        class Interaction: pass
        class TextChannel: pass
        class Role: pass
        class Member: pass
        class Permissions: pass
        class Embed: pass
        class Color: pass
        class ButtonStyle: pass
        class ui:
            class View: pass
            class Button: pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("reaction_actions")

# Default reaction actions configuration
DEFAULT_ACTIONS = {
    "🎫": "create_ticket",      # Create a ticket
    "✅": "approve_request",    # Approve a request
    "❌": "deny_request",       # Deny a request
    "🔒": "close_ticket",       # Close a ticket
    "📌": "pin_message",        # Pin message
    "🗑️": "delete_message",     # Delete message (mod only)
    "⏰": "timeout_user",       # Timeout the message author (mod only)
    "⚠️": "warn_user",          # Warn the message author (mod only)
    "🔨": "kick_user"           # Kick the message author (mod only)
}

# Data storage for reaction handlers
DATA_DIR = "data"
REACTION_CONFIG_FILE = os.path.join(DATA_DIR, "reaction_config.json")
ACTIVE_HANDLERS_FILE = os.path.join(DATA_DIR, "active_reaction_handlers.json")

class ReactionActionHandler:
    """Handles message reaction-based actions"""
    
    def __init__(self, bot):
        """Initialize the reaction handler
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        self.actions = DEFAULT_ACTIONS.copy()
        self.active_messages = {}
        
        # Ensure data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Load existing configuration
        self._load_config()
        self._load_active_handlers()
    
    def _load_config(self) -> None:
        """Load reaction action configuration from file"""
        if not os.path.exists(REACTION_CONFIG_FILE):
            logger.info("No reaction configuration file found, using defaults")
            return
        
        try:
            with open(REACTION_CONFIG_FILE, 'r') as f:
                custom_actions = json.load(f)
                # Merge with defaults, allowing custom overrides
                self.actions.update(custom_actions)
                logger.info(f"Loaded custom reaction configuration with {len(custom_actions)} actions")
        except Exception as e:
            logger.error(f"Error loading reaction configuration: {e}")
    
    def _save_config(self) -> None:
        """Save the current reaction action configuration to file"""
        try:
            with open(REACTION_CONFIG_FILE, 'w') as f:
                json.dump(self.actions, f, indent=2)
                logger.info("Saved reaction configuration")
        except Exception as e:
            logger.error(f"Error saving reaction configuration: {e}")
    
    def _load_active_handlers(self) -> None:
        """Load active message handlers from file"""
        if not os.path.exists(ACTIVE_HANDLERS_FILE):
            logger.info("No active reaction handlers file found")
            return
        
        try:
            with open(ACTIVE_HANDLERS_FILE, 'r') as f:
                handlers_data = json.load(f)
                
                # Convert string keys back to integers for message IDs
                self.active_messages = {
                    int(message_id): message_data 
                    for message_id, message_data in handlers_data.items()
                }
                
                logger.info(f"Loaded {len(self.active_messages)} active reaction handlers")
        except Exception as e:
            logger.error(f"Error loading active reaction handlers: {e}")
            self.active_messages = {}
    
    def _save_active_handlers(self) -> None:
        """Save the current active message handlers to file"""
        try:
            # Convert to a serializable format (message IDs to strings)
            handlers_data = {
                str(message_id): message_data
                for message_id, message_data in self.active_messages.items()
            }
            
            with open(ACTIVE_HANDLERS_FILE, 'w') as f:
                json.dump(handlers_data, f, indent=2)
                logger.info(f"Saved {len(self.active_messages)} active reaction handlers")
        except Exception as e:
            logger.error(f"Error saving active reaction handlers: {e}")
    
    def register_message(self, message_id: int, channel_id: int, 
                         author_id: int, guild_id: int, 
                         action_type: str, allowed_reactions: Optional[List[str]] = None,
                         data: Optional[Dict[str, Any]] = None) -> None:
        """Register a message for reaction handling
        
        Args:
            message_id: Discord message ID
            channel_id: Discord channel ID
            author_id: Message author's user ID
            guild_id: Discord guild (server) ID
            action_type: Type of action (e.g., "ticket", "approval", "moderation")
            allowed_reactions: List of allowed emoji reactions, if None uses all
            data: Additional data for handling reactions
        """
        if allowed_reactions is None:
            allowed_reactions = list(self.actions.keys())
        
        if data is None:
            data = {}
        
        self.active_messages[message_id] = {
            "channel_id": channel_id,
            "author_id": author_id,
            "guild_id": guild_id,
            "action_type": action_type,
            "allowed_reactions": allowed_reactions,
            "created_at": datetime.now().isoformat(),
            "data": data
        }
        
        self._save_active_handlers()
        logger.info(f"Registered message {message_id} for reaction handling of type '{action_type}'")
    
    def unregister_message(self, message_id: int) -> bool:
        """Unregister a message from reaction handling
        
        Args:
            message_id: Discord message ID
            
        Returns:
            bool: True if message was unregistered, False if not found
        """
        if message_id in self.active_messages:
            del self.active_messages[message_id]
            self._save_active_handlers()
            logger.info(f"Unregistered message {message_id} from reaction handling")
            return True
        
        logger.debug(f"Message {message_id} not found in active handlers")
        return False
    
    async def handle_reaction_add(self, reaction, user) -> None:
        """Handle a reaction being added to a message
        
        Args:
            reaction: Discord reaction object
            user: Discord user who added the reaction
        """
        # Ignore bot's own reactions
        if user.bot:
            return
        
        message_id = reaction.message.id
        if message_id not in self.active_messages:
            return
        
        # Check if this reaction is allowed for this message
        handler_data = self.active_messages[message_id]
        emoji = str(reaction.emoji)
        
        if emoji not in handler_data["allowed_reactions"]:
            logger.debug(f"Reaction {emoji} not in allowed reactions for message {message_id}")
            return
        
        if emoji not in self.actions:
            logger.debug(f"Reaction {emoji} not configured with an action")
            return
        
        action_name = self.actions[emoji]
        logger.info(f"Processing reaction action '{action_name}' from user {user.name} on message {message_id}")
        
        # Get the message if not cached
        if not hasattr(reaction, "message") or not reaction.message:
            try:
                channel = self.bot.get_channel(handler_data["channel_id"])
                if not channel:
                    logger.error(f"Could not find channel {handler_data['channel_id']}")
                    return
                
                reaction.message = await channel.fetch_message(message_id)
            except Exception as e:
                logger.error(f"Error fetching message {message_id}: {e}")
                return
        
        # Process the action based on action type and emoji
        await self._process_action(action_name, reaction, user, handler_data)
    
    async def _process_action(self, action_name: str, reaction, user, handler_data: Dict[str, Any]) -> None:
        """Process a specific reaction action
        
        Args:
            action_name: Name of the action to perform
            reaction: Discord reaction object
            user: Discord user who added the reaction
            handler_data: Handler data for the message
        """
        # Get action method
        action_method = getattr(self, action_name, None)
        if not action_method:
            logger.warning(f"Action method '{action_name}' not implemented")
            return
        
        # Check permissions if needed
        if action_name in ["delete_message", "pin_message", "timeout_user", "kick_user", "warn_user"]:
            if not await self._check_mod_permissions(user, reaction.message.guild):
                # Remove the reaction if user doesn't have permission
                try:
                    await reaction.remove(user)
                except Exception as e:
                    logger.error(f"Error removing unauthorized reaction: {e}")
                return
        
        try:
            # Call the action method
            await action_method(reaction, user, handler_data)
        except Exception as e:
            logger.error(f"Error processing action '{action_name}': {e}")
    
    async def _check_mod_permissions(self, user, guild) -> bool:
        """Check if user has moderator permissions
        
        Args:
            user: Discord user to check
            guild: Discord guild (server)
            
        Returns:
            bool: True if user has moderator permissions
        """
        # Get member object
        member = guild.get_member(user.id)
        if not member:
            return False
        
        # Check for admin or manage messages permission
        return (
            member.guild_permissions.administrator or
            member.guild_permissions.manage_messages or
            member.guild_permissions.manage_guild
        )
    
    # ===== Action Methods =====
    
    async def create_ticket(self, reaction, user, handler_data: Dict[str, Any]) -> None:
        """Create a support ticket from a reaction
        
        Args:
            reaction: Discord reaction object
            user: Discord user who added the reaction
            handler_data: Handler data for the message
        """
        message = reaction.message
        guild = message.guild
        
        # Check if we already have a ticket
        ticket_category = None
        for category in guild.categories:
            if category.name.lower() == "tickets":
                ticket_category = category
                break
        
        if not ticket_category:
            # Try to create the category
            try:
                ticket_category = await guild.create_category("Tickets")
                logger.info(f"Created Tickets category in guild {guild.id}")
            except Exception as e:
                logger.error(f"Could not create Tickets category: {e}")
                await user.send("Could not create a ticket. The server doesn't have a Tickets category.")
                return
        
        # Create a ticket channel with permissions for the user
        ticket_number = 1
        # Try to find the next ticket number by checking existing channels
        for channel in ticket_category.channels:
            if channel.name.startswith("ticket-"):
                try:
                    channel_number = int(channel.name.split("-")[1])
                    ticket_number = max(ticket_number, channel_number + 1)
                except (ValueError, IndexError):
                    pass
        
        # Create overwrites for the channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        # Add overwrites for moderator roles if in handler_data
        if "mod_roles" in handler_data.get("data", {}):
            for role_id in handler_data["data"]["mod_roles"]:
                role = guild.get_role(int(role_id))
                if role:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        # Create the ticket channel
        try:
            channel = await ticket_category.create_text_channel(
                f"ticket-{ticket_number}",
                overwrites=overwrites,
                topic=f"Support ticket #{ticket_number} created by {user.name}"
            )
            
            # Send initial message in the ticket channel
            embed = discord.Embed(
                title=f"Ticket #{ticket_number}",
                description=f"Support ticket created by {user.mention}",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Instructions",
                value="Please describe your issue or question, and a staff member will assist you shortly.",
                inline=False
            )
            
            # Add close button
            class CloseButton(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)
                
                @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒")
                async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user == user or await self._check_mod_permissions(interaction.user, guild):
                        await interaction.response.send_message("Closing ticket...")
                        await asyncio.sleep(1)
                        await channel.delete()
                    else:
                        await interaction.response.send_message(
                            "You don't have permission to close this ticket.",
                            ephemeral=True
                        )
            
            await channel.send(embed=embed, view=CloseButton())
            
            # Send confirmation to user
            try:
                await user.send(f"Ticket created! Check {channel.mention} to continue.")
            except discord.Forbidden:
                # User has DMs disabled
                pass
            
            logger.info(f"Created ticket channel {channel.name} for user {user.name}")
            
            # Remove the reaction
            try:
                await reaction.remove(user)
            except Exception as e:
                logger.error(f"Error removing reaction: {e}")
                
        except Exception as e:
            logger.error(f"Error creating ticket channel: {e}")
            await user.send(f"There was an error creating your ticket: {e}")
    
    async def approve_request(self, reaction, user, handler_data: Dict[str, Any]) -> None:
        """Approve a pending request
        
        Args:
            reaction: Discord reaction object
            user: Discord user who added the reaction
            handler_data: Handler data for the message
        """
        message = reaction.message
        
        # Update the message with approved status
        try:
            embed = message.embeds[0] if message.embeds else None
            if embed:
                embed.color = discord.Color.green()
                embed.add_field(
                    name="Status",
                    value=f"✅ Approved by {user.mention}",
                    inline=False
                )
                await message.edit(embed=embed)
            else:
                await message.channel.send(f"Request approved by {user.mention}")
            
            logger.info(f"Request in message {message.id} approved by {user.name}")
            
            # Process approval actions if specified
            if "approval_action" in handler_data.get("data", {}):
                action = handler_data["data"]["approval_action"]
                
                # Verify the user who should get the role
                target_user_id = handler_data["data"].get("target_user_id")
                if target_user_id and action == "assign_role":
                    role_id = handler_data["data"].get("role_id")
                    if role_id:
                        guild = message.guild
                        member = guild.get_member(int(target_user_id))
                        role = guild.get_role(int(role_id))
                        
                        if member and role:
                            try:
                                await member.add_roles(role)
                                logger.info(f"Assigned role {role.name} to user {member.name}")
                            except Exception as e:
                                logger.error(f"Error assigning role: {e}")
            
            # Unregister the message from reaction handling
            self.unregister_message(message.id)
            
        except Exception as e:
            logger.error(f"Error processing approval: {e}")
    
    async def deny_request(self, reaction, user, handler_data: Dict[str, Any]) -> None:
        """Deny a pending request
        
        Args:
            reaction: Discord reaction object
            user: Discord user who added the reaction
            handler_data: Handler data for the message
        """
        message = reaction.message
        
        # Update the message with denied status
        try:
            embed = message.embeds[0] if message.embeds else None
            if embed:
                embed.color = discord.Color.red()
                embed.add_field(
                    name="Status",
                    value=f"❌ Denied by {user.mention}",
                    inline=False
                )
                await message.edit(embed=embed)
            else:
                await message.channel.send(f"Request denied by {user.mention}")
            
            logger.info(f"Request in message {message.id} denied by {user.name}")
            
            # Process denial actions if specified
            if "denial_action" in handler_data.get("data", {}):
                action = handler_data["data"]["denial_action"]
                
                # Notify the target user
                target_user_id = handler_data["data"].get("target_user_id")
                if target_user_id and action == "notify":
                    guild = message.guild
                    member = guild.get_member(int(target_user_id))
                    
                    if member:
                        try:
                            await member.send(f"Your request has been denied by {user.name}.")
                            logger.info(f"Notified user {member.name} about denial")
                        except Exception as e:
                            logger.error(f"Error notifying user: {e}")
            
            # Unregister the message from reaction handling
            self.unregister_message(message.id)
            
        except Exception as e:
            logger.error(f"Error processing denial: {e}")
    
    async def close_ticket(self, reaction, user, handler_data: Dict[str, Any]) -> None:
        """Close a ticket channel
        
        Args:
            reaction: Discord reaction object
            user: Discord user who added the reaction
            handler_data: Handler data for the message
        """
        message = reaction.message
        channel = message.channel
        
        # Check if this is a ticket channel
        if not channel.name.startswith("ticket-"):
            return
        
        # Check if user is allowed to close the ticket
        creator_id = handler_data.get("data", {}).get("creator_id")
        if creator_id and int(creator_id) != user.id and not await self._check_mod_permissions(user, message.guild):
            try:
                await reaction.remove(user)
            except Exception:
                pass
            return
        
        # Close the ticket by archiving or deleting
        try:
            # First, send a closing message
            embed = discord.Embed(
                title="Ticket Closed",
                description=f"This ticket has been closed by {user.mention}",
                color=discord.Color.orange()
            )
            await channel.send(embed=embed)
            
            # Archive strategy depends on whether this is a thread or channel
            if isinstance(channel, discord.Thread):
                await channel.edit(archived=True, locked=True)
                logger.info(f"Archived ticket thread {channel.name}")
            else:
                # Rename the channel to indicate it's closed
                try:
                    await channel.edit(name=f"closed-{channel.name.split('-')[1]}")
                    logger.info(f"Renamed ticket channel to {channel.name}")
                except Exception as e:
                    logger.error(f"Error renaming channel: {e}")
                
                # Delete after a delay
                if handler_data.get("data", {}).get("delete_on_close", False):
                    await asyncio.sleep(5)
                    await channel.delete()
                    logger.info(f"Deleted ticket channel {channel.name}")
            
            # Unregister the message
            self.unregister_message(message.id)
            
        except Exception as e:
            logger.error(f"Error closing ticket: {e}")
    
    async def pin_message(self, reaction, user, handler_data: Dict[str, Any]) -> None:
        """Pin a message to the channel
        
        Args:
            reaction: Discord reaction object
            user: Discord user who added the reaction
            handler_data: Handler data for the message
        """
        message = reaction.message
        
        try:
            # Pin the message
            await message.pin()
            logger.info(f"Message {message.id} pinned by {user.name}")
            
            # Unregister the message
            self.unregister_message(message.id)
            
        except Exception as e:
            logger.error(f"Error pinning message: {e}")
    
    async def delete_message(self, reaction, user, handler_data: Dict[str, Any]) -> None:
        """Delete a message (moderator only)
        
        Args:
            reaction: Discord reaction object
            user: Discord user who added the reaction
            handler_data: Handler data for the message
        """
        message = reaction.message
        
        try:
            # Delete the message
            await message.delete()
            logger.info(f"Message {message.id} deleted by {user.name}")
            
            # Unregister the message
            self.unregister_message(message.id)
            
            # Log the deletion in a mod-log channel if configured
            log_channel_id = handler_data.get("data", {}).get("log_channel_id")
            if log_channel_id:
                log_channel = self.bot.get_channel(int(log_channel_id))
                if log_channel:
                    embed = discord.Embed(
                        title="Message Deleted",
                        description=f"A message from {message.author.mention} was deleted by {user.mention}",
                        color=discord.Color.red()
                    )
                    
                    # Add message content if available
                    if message.content:
                        embed.add_field(
                            name="Content",
                            value=message.content[:1024] if len(message.content) > 1024 else message.content,
                            inline=False
                        )
                    
                    await log_channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
    
    async def timeout_user(self, reaction, user, handler_data: Dict[str, Any]) -> None:
        """Timeout the message author (moderator only)
        
        Args:
            reaction: Discord reaction object
            user: Discord user who added the reaction
            handler_data: Handler data for the message
        """
        message = reaction.message
        target_user = message.author
        guild = message.guild
        
        # Get the member object
        member = guild.get_member(target_user.id)
        if not member:
            return
        
        # Get timeout duration from handler data or use default
        duration_mins = handler_data.get("data", {}).get("timeout_duration_mins", 60)
        duration = timedelta(minutes=duration_mins)
        
        try:
            # Timeout the user
            await member.timeout(duration, reason=f"Timed out by {user.name}")
            logger.info(f"User {member.name} timed out for {duration_mins} minutes by {user.name}")
            
            # Send notification
            embed = discord.Embed(
                title="User Timed Out",
                description=f"{member.mention} has been timed out for {duration_mins} minutes by {user.mention}",
                color=discord.Color.orange()
            )
            await message.channel.send(embed=embed, delete_after=10)
            
            # Unregister the message
            self.unregister_message(message.id)
            
        except Exception as e:
            logger.error(f"Error timing out user: {e}")
    
    async def warn_user(self, reaction, user, handler_data: Dict[str, Any]) -> None:
        """Warn the message author (moderator only)
        
        Args:
            reaction: Discord reaction object
            user: Discord user who added the reaction
            handler_data: Handler data for the message
        """
        message = reaction.message
        target_user = message.author
        
        try:
            # Send warning message
            warn_embed = discord.Embed(
                title="User Warned",
                description=f"{target_user.mention} has been warned by {user.mention}",
                color=discord.Color.gold()
            )
            
            warn_reason = handler_data.get("data", {}).get("warn_reason", "Inappropriate content")
            warn_embed.add_field(
                name="Reason",
                value=warn_reason,
                inline=False
            )
            
            await message.channel.send(embed=warn_embed, delete_after=10)
            logger.info(f"User {target_user.name} warned by {user.name}")
            
            # Try to DM the user
            try:
                dm_embed = discord.Embed(
                    title="Warning",
                    description=f"You have received a warning in {message.guild.name}",
                    color=discord.Color.gold()
                )
                dm_embed.add_field(
                    name="Reason",
                    value=warn_reason,
                    inline=False
                )
                
                await target_user.send(embed=dm_embed)
            except Exception as e:
                logger.error(f"Error sending DM to warned user: {e}")
            
            # Unregister the message
            self.unregister_message(message.id)
            
        except Exception as e:
            logger.error(f"Error warning user: {e}")
    
    async def kick_user(self, reaction, user, handler_data: Dict[str, Any]) -> None:
        """Kick the message author (moderator only)
        
        Args:
            reaction: Discord reaction object
            user: Discord user who added the reaction
            handler_data: Handler data for the message
        """
        message = reaction.message
        target_user = message.author
        guild = message.guild
        
        # Get the member object
        member = guild.get_member(target_user.id)
        if not member:
            return
        
        # Get kick reason from handler data or use default
        kick_reason = handler_data.get("data", {}).get("kick_reason", f"Kicked by {user.name}")
        
        try:
            # Kick the user
            await member.kick(reason=kick_reason)
            logger.info(f"User {member.name} kicked by {user.name}")
            
            # Send notification
            embed = discord.Embed(
                title="User Kicked",
                description=f"{member.name} has been kicked by {user.mention}",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Reason",
                value=kick_reason,
                inline=False
            )
            
            await message.channel.send(embed=embed)
            
            # Unregister the message
            self.unregister_message(message.id)
            
        except Exception as e:
            logger.error(f"Error kicking user: {e}")

# Discord event handlers for integrating with a Discord.py bot

def setup(bot):
    """Set up the reaction actions module for a Discord.py bot
    
    Args:
        bot: Discord.py bot instance
    """
    # Create the reaction handler
    handler = ReactionActionHandler(bot)
    
    # Store it on the bot for access from commands
    bot.reaction_handler = handler
    
    # Register event listeners
    @bot.event
    async def on_raw_reaction_add(payload):
        """Handle reaction add events"""
        # Ignore bot's own reactions
        if payload.user_id == bot.user.id:
            return
        
        # Check if this is a message we're tracking
        if payload.message_id in handler.active_messages:
            # Get the necessary objects
            guild = bot.get_guild(payload.guild_id)
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
                        await handler.handle_reaction_add(reaction, user)
                        break
            except Exception as e:
                logger.error(f"Error handling reaction: {e}")
    
    # Command for setting up a reaction message
    @bot.tree.command(
        name="setup_reactions",
        description="Set up a message with reaction quick actions"
    )
    @discord.app_commands.describe(
        message_id="The ID of the message to add reactions to",
        action_type="The type of action for this message (ticket, approval, moderation)"
    )
    async def setup_reactions(interaction: discord.Interaction, message_id: str, action_type: str):
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
                if message.embeds and message.mentions:
                    data["target_user_id"] = message.mentions[0].id
                
            elif action_type.lower() == "moderation":
                allowed_reactions = ["📌", "🗑️", "⏰", "⚠️", "🔨"]
                
                # Add mod log channel if exists
                mod_log = None
                for channel in interaction.guild.channels:
                    if (channel.permissions_for(interaction.guild.me).send_messages and
                        ("mod-log" in channel.name.lower() or 
                         "mod_log" in channel.name.lower() or
                         "modlog" in channel.name.lower())):
                        mod_log = channel.id
                        break
                
                if mod_log:
                    data["log_channel_id"] = mod_log
                
            elif action_type.lower() == "all":
                allowed_reactions = list(handler.actions.keys())
            else:
                await interaction.response.send_message(
                    "Invalid action type. Use 'ticket', 'approval', 'moderation', or 'all'.",
                    ephemeral=True
                )
                return
            
            # Register the message
            handler.register_message(
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
    
    # Command for creating a reaction-based ticket panel
    @bot.tree.command(
        name="create_ticket_panel",
        description="Create a ticket panel with reaction support"
    )
    @discord.app_commands.describe(
        channel="The channel to send the ticket panel to",
        title="The title for the ticket panel",
        description="The description for the ticket panel"
    )
    async def create_ticket_panel(
        interaction: discord.Interaction,
        channel: discord.TextChannel = None,
        title: str = "Support Tickets",
        description: str = "React with 🎫 to create a support ticket"
    ):
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
            
            handler.register_message(
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

if __name__ == "__main__":
    print("This module should be imported and used with a Discord bot.")