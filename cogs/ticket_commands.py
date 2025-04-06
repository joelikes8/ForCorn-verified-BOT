import discord
from discord import app_commands
from discord.ext import commands
from discord import Embed, Color
import logging
from utils.ticket_system import TicketSystem

logger = logging.getLogger(__name__)

class TicketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_system = TicketSystem(bot, bot.config)
    
    @app_commands.command(name="ticket", description="Create a support ticket")
    async def ticket(self, interaction: discord.Interaction):
        """Create a support ticket"""
        await interaction.response.defer(ephemeral=True)
        
        # Create a ticket channel
        ticket_channel = await self.ticket_system.create_ticket(interaction)
        
        if not ticket_channel:
            # Error message already sent in create_ticket
            return
        
        logger.info(f"Ticket created by {interaction.user.name} (ID: {interaction.user.id})")
    
    @app_commands.command(name="sendticket", description="Send the ticket panel to a channel")
    @app_commands.describe(channel="The channel to send the ticket panel to")
    async def sendticket(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Send the ticket panel to a channel"""
        await interaction.response.defer(ephemeral=True)
        
        # Check if user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("You need administrator permissions to use this command.", ephemeral=True)
            return
        
        # Send the ticket panel
        success = await self.ticket_system.send_ticket_panel(channel)
        
        if success:
            await interaction.followup.send(f"Ticket panel sent to {channel.mention}!", ephemeral=True)
            logger.info(f"Ticket panel sent to {channel.name} by {interaction.user.name} (ID: {interaction.user.id})")
        else:
            await interaction.followup.send("Failed to send ticket panel. Please check my permissions.", ephemeral=True)
    
    @app_commands.command(name="closeticket", description="Close a ticket channel")
    async def closeticket(self, interaction: discord.Interaction):
        """Close a ticket channel"""
        # Check if the channel is a ticket
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("This command can only be used in ticket channels.", ephemeral=True)
            return
        
        # Close the ticket
        await self.ticket_system.close_ticket(interaction, interaction.channel)
