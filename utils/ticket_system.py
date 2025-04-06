import discord
from discord import ButtonStyle, Embed, Color
import logging
import asyncio

logger = logging.getLogger(__name__)

class TicketView(discord.ui.View):
    def __init__(self, ticket_system):
        super().__init__(timeout=None)
        self.ticket_system = ticket_system
    
    @discord.ui.button(label="Create Ticket", style=ButtonStyle.success, custom_id="create_ticket")
    async def create_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.ticket_system.create_ticket(interaction)

class TicketClosingView(discord.ui.View):
    def __init__(self, ticket_system, ticket_channel):
        super().__init__(timeout=None)
        self.ticket_system = ticket_system
        self.ticket_channel = ticket_channel
    
    @discord.ui.button(label="Close Ticket", style=ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.ticket_system.close_ticket(interaction, self.ticket_channel)

class TicketSystem:
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.ticket_view = TicketView(self)
        
        # Register the persistent view
        bot.add_view(self.ticket_view)
    
    async def send_ticket_panel(self, channel):
        """Send the ticket panel to a channel"""
        embed = Embed(
            title="Support Tickets",
            description="Need assistance? Click the button below to create a ticket and our staff will help you as soon as possible.",
            color=Color.blue()
        )
        
        await channel.send(embed=embed, view=self.ticket_view)
        return True
    
    async def create_ticket(self, interaction):
        """Create a new ticket channel"""
        guild = interaction.guild
        user = interaction.user
        
        # Get server config
        server_config = self.config.get_server_config(guild.id)
        
        # Get the next ticket number
        ticket_number = self.config.get_next_ticket_number(guild.id)
        
        # Create ticket channel name
        channel_name = f"ticket-{ticket_number}"
        
        try:
            # Create permissions for the ticket channel
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                user: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True
                ),
                guild.me: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    manage_channels=True
                )
            }
            
            # Add additional role permissions if configured
            if server_config.get("mod_role"):
                mod_role = guild.get_role(int(server_config["mod_role"]))
                if mod_role:
                    overwrites[mod_role] = discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=True,
                        manage_messages=True
                    )
            
            if server_config.get("admin_role"):
                admin_role = guild.get_role(int(server_config["admin_role"]))
                if admin_role:
                    overwrites[admin_role] = discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=True,
                        manage_channels=True
                    )
            
            # Create the ticket channel
            ticket_channel = await guild.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                reason=f"Support ticket for {user.name}"
            )
            
            # Create the ticket embed
            ticket_embed = Embed(
                title=f"Ticket #{ticket_number}",
                description="Thank you for creating a ticket. Please describe your issue, and a staff member will assist you soon.",
                color=Color.green()
            )
            ticket_embed.add_field(name="Created by", value=user.mention)
            
            # Create a view with a close button
            close_view = TicketClosingView(self, ticket_channel)
            
            # Send the initial message in the ticket channel
            await ticket_channel.send(
                content=f"{user.mention} Welcome to your support ticket!",
                embed=ticket_embed,
                view=close_view
            )
            
            # Register the closing view to persist
            self.bot.add_view(close_view, message_id=None)
            
            # Respond to the interaction
            await interaction.response.send_message(
                f"Your ticket has been created: {ticket_channel.mention}",
                ephemeral=True
            )
            
            logger.info(f"Created ticket #{ticket_number} for {user.name} (ID: {user.id})")
            return ticket_channel
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to create channels. Please contact a server administrator.",
                ephemeral=True
            )
            return None
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            await interaction.response.send_message(
                "An error occurred while creating your ticket. Please try again later.",
                ephemeral=True
            )
            return None
    
    async def close_ticket(self, interaction, ticket_channel):
        """Close a ticket channel"""
        user = interaction.user
        
        # Check if user has permission to close the ticket
        if not (
            interaction.channel.permissions_for(user).manage_channels or
            ticket_channel.topic and str(user.id) in ticket_channel.topic
        ):
            await interaction.response.send_message(
                "You don't have permission to close this ticket.",
                ephemeral=True
            )
            return
        
        try:
            # Notify that the ticket is being closed
            await interaction.response.send_message("Closing this ticket in 5 seconds...")
            
            # Create a transcript of the ticket (simplified version)
            transcript = []
            async for message in ticket_channel.history(limit=100, oldest_first=True):
                time_str = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                transcript.append(f"[{time_str}] {message.author.name}: {message.content}")
            
            # Wait 5 seconds before closing
            await asyncio.sleep(5)
            
            # Delete the channel
            await ticket_channel.delete(reason=f"Ticket closed by {user.name}")
            
            logger.info(f"Closed ticket channel #{ticket_channel.name} by {user.name} (ID: {user.id})")
            
        except discord.Forbidden:
            await interaction.followup.send(
                "I don't have permission to delete this channel. Please contact a server administrator.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error closing ticket: {e}")
            await interaction.followup.send(
                "An error occurred while closing the ticket. Please try again later.",
                ephemeral=True
            )
