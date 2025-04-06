import discord
from discord import app_commands
from discord.ext import commands
from discord import Embed, Color
import logging
from utils.moderation import ModerationSystem

logger = logging.getLogger(__name__)

class ModerationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.moderation = ModerationSystem(bot)
        
        # Setup event listeners
        self.bot.add_listener(self.on_member_join, "on_member_join")
        self.bot.add_listener(self.on_message, "on_message")
    
    async def on_member_join(self, member):
        await self.moderation.on_member_join(member)
    
    async def on_message(self, message):
        await self.moderation.on_message(message)
    
    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(
        member="The member to kick",
        reason="The reason for kicking the member"
    )
    async def kick(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member,
        reason: str = None
    ):
        """Kick a member from the server"""
        await interaction.response.defer(ephemeral=True)
        
        # Check if user has kick permissions
        if not interaction.user.guild_permissions.kick_members:
            await interaction.followup.send("You don't have permission to kick members.", ephemeral=True)
            return
        
        # Kick the member
        success, message = await self.moderation.kick_member(
            interaction.guild,
            interaction.user,
            member,
            reason
        )
        
        if success:
            await interaction.followup.send(message, ephemeral=True)
            logger.info(f"Member {member.name} kicked by {interaction.user.name}: {reason}")
        else:
            await interaction.followup.send(message, ephemeral=True)
    
    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(
        member="The member to ban",
        reason="The reason for banning the member",
        delete_days="Number of days of messages to delete (0-7)"
    )
    async def ban(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member,
        reason: str = None,
        delete_days: int = 1
    ):
        """Ban a member from the server"""
        await interaction.response.defer(ephemeral=True)
        
        # Check if user has ban permissions
        if not interaction.user.guild_permissions.ban_members:
            await interaction.followup.send("You don't have permission to ban members.", ephemeral=True)
            return
        
        # Validate delete_days
        if delete_days < 0 or delete_days > 7:
            await interaction.followup.send("Delete days must be between 0 and 7.", ephemeral=True)
            return
        
        # Ban the member
        success, message = await self.moderation.ban_member(
            interaction.guild,
            interaction.user,
            member,
            reason,
            delete_days
        )
        
        if success:
            await interaction.followup.send(message, ephemeral=True)
            logger.info(f"Member {member.name} banned by {interaction.user.name}: {reason}")
        else:
            await interaction.followup.send(message, ephemeral=True)
    
    @app_commands.command(name="timeout", description="Timeout a member")
    @app_commands.describe(
        member="The member to timeout",
        duration="Timeout duration in minutes",
        reason="The reason for the timeout"
    )
    async def timeout(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member,
        duration: int,
        reason: str = None
    ):
        """Timeout a member"""
        await interaction.response.defer(ephemeral=True)
        
        # Check if user has moderate members permissions
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.followup.send("You don't have permission to timeout members.", ephemeral=True)
            return
        
        # Validate duration
        if duration < 1 or duration > 40320:  # Max is 28 days (40320 minutes)
            await interaction.followup.send("Duration must be between 1 minute and 28 days.", ephemeral=True)
            return
        
        # Timeout the member
        success, message = await self.moderation.timeout_member(
            interaction.guild,
            interaction.user,
            member,
            duration,
            reason
        )
        
        if success:
            await interaction.followup.send(message, ephemeral=True)
            logger.info(f"Member {member.name} timed out by {interaction.user.name} for {duration} minutes: {reason}")
        else:
            await interaction.followup.send(message, ephemeral=True)
    
    @app_commands.command(name="antiraid", description="Toggle anti-raid protection")
    @app_commands.describe(
        action="Enable or disable anti-raid protection"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="enable", value="enable"),
        app_commands.Choice(name="disable", value="disable")
    ])
    async def antiraid(self, interaction: discord.Interaction, action: str):
        """Toggle anti-raid protection"""
        await interaction.response.defer(ephemeral=True)
        
        # Check if user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("You need administrator permissions to use this command.", ephemeral=True)
            return
        
        if action == "enable":
            success, message = await self.moderation.setup_anti_raid(interaction.guild)
        else:
            success, message = await self.moderation.disable_anti_raid(interaction.guild)
        
        await interaction.followup.send(message, ephemeral=True)
        logger.info(f"Anti-raid protection {action}d by {interaction.user.name}")
    
    @app_commands.command(name="setup_roles", description="Set up verification and moderation roles")
    @app_commands.describe(
        verified_role="The role to assign to verified users",
        mod_role="The role with moderation permissions",
        admin_role="The role with admin permissions"
    )
    async def setup_roles(
        self, 
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
        
        # Update server config
        if verified_role:
            self.bot.config.update_server_config(interaction.guild.id, "verified_role", str(verified_role.id))
        
        if mod_role:
            self.bot.config.update_server_config(interaction.guild.id, "mod_role", str(mod_role.id))
        
        if admin_role:
            self.bot.config.update_server_config(interaction.guild.id, "admin_role", str(admin_role.id))
        
        # Create success embed
        embed = Embed(
            title="Role Setup Successful ✅",
            description="Successfully set up the roles for this server.",
            color=Color.green()
        )
        
        if verified_role:
            embed.add_field(name="Verified Role", value=verified_role.mention)
        
        if mod_role:
            embed.add_field(name="Moderator Role", value=mod_role.mention)
        
        if admin_role:
            embed.add_field(name="Admin Role", value=admin_role.mention)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        logger.info(f"Roles set up by {interaction.user.name}")
