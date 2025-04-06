import random
import discord
from discord import app_commands
from discord.ext import commands
from discord import Embed, Color, ButtonStyle
import logging
import string
from utils.verification import VerificationSystem
from utils.roblox_api import RobloxAPI
from utils.blacklist import BlacklistSystem

logger = logging.getLogger(__name__)

class VerifyButton(discord.ui.View):
    def __init__(self, verification_system, roblox_username, code):
        super().__init__(timeout=600)  # 10 minute timeout
        self.verification_system = verification_system
        self.roblox_username = roblox_username
        self.code = code
    
    @discord.ui.button(label="Verify", style=ButtonStyle.success)
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Disable the button
        button.disabled = True
        await interaction.response.edit_message(view=self)
        
        # Perform verification
        member = interaction.user
        success, result = await self.verification_system.verify_user(member, self.roblox_username, self.code)
        
        if success:
            # Get server config
            server_config = self.verification_system.roblox_api.bot.config.get_server_config(interaction.guild.id)
            
            # Get the group ID if it exists
            group_id = server_config.get("group_id")
            
            # Update nickname
            nickname_success, nickname_result = await self.verification_system.update_nickname(
                member,
                self.roblox_username,
                group_id
            )
            
            # Assign verified role if configured
            verified_role_id = server_config.get("verified_role")
            if verified_role_id:
                verified_role = interaction.guild.get_role(int(verified_role_id))
                if verified_role:
                    try:
                        await member.add_roles(verified_role, reason="User verified with Roblox account")
                    except discord.Forbidden:
                        pass  # Ignore permission errors
            
            # Send success message
            embed = Embed(
                title="Verification Successful ✅",
                description=f"You have been verified as **{self.roblox_username}**!",
                color=Color.green()
            )
            
            if nickname_success:
                embed.add_field(name="Nickname", value=f"Your nickname has been updated to: **{nickname_result}**")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"User {member.name} (ID: {member.id}) verified as {self.roblox_username}")
        else:
            # Send failure message
            embed = Embed(
                title="Verification Failed ❌",
                description=result,
                color=Color.red()
            )
            embed.add_field(
                name="Try Again",
                value="Make sure the verification code is in your Roblox profile's About Me section and try again."
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"Verification failed for {member.name} (ID: {member.id}): {result}")

class VerificationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roblox_api = RobloxAPI()
        self.roblox_api.bot = bot  # Add bot reference to access config
        self.verification_system = VerificationSystem(self.roblox_api)
        self.blacklist_system = BlacklistSystem(self.roblox_api, bot.config)
    
    @app_commands.command(name="verify", description="Verify your Roblox account")
    @app_commands.describe(roblox_username="Your Roblox username")
    async def verify(self, interaction: discord.Interaction, roblox_username: str):
        """Verify your Roblox account with your Discord account"""
        await interaction.response.defer(ephemeral=True)
        
        member = interaction.user
        guild = interaction.guild
        
        # Check if user is already verified (has the verified role)
        server_config = self.bot.config.get_server_config(guild.id)
        verified_role_id = server_config.get("verified_role")
        
        if verified_role_id:
            verified_role = guild.get_role(int(verified_role_id))
            if verified_role and verified_role in member.roles:
                await interaction.followup.send(
                    "You are already verified! If you need to update your verification, please contact an administrator.",
                    ephemeral=True
                )
                return
        
        # Check if user is in any blacklisted groups
        is_clean, blacklisted_groups, message = await self.blacklist_system.check_user_blacklisted_groups(
            guild.id, roblox_username
        )
        
        if not is_clean and blacklisted_groups:
            # Create an embed with blacklisted groups
            embed = self.blacklist_system.create_blacklist_embed(roblox_username, blacklisted_groups)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Generate a verification code
        code = self.verification_system.generate_verification_code()
        
        # Store the verification code
        self.bot.config.add_verification_code(member.id, code, roblox_username)
        
        # Create and send the verification embed
        embed = await self.verification_system.create_verification_embed(roblox_username, code)
        
        # Create a view with the verify button
        view = VerifyButton(self.verification_system, roblox_username, code)
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        logger.info(f"Sent verification request to {member.name} (ID: {member.id}) for Roblox username: {roblox_username}")
    
    @app_commands.command(name="background", description="Check if a Roblox user is in any blacklisted groups")
    @app_commands.describe(roblox_username="The Roblox username to check")
    async def background(self, interaction: discord.Interaction, roblox_username: str):
        """Check if a Roblox user is in any blacklisted groups"""
        await interaction.response.defer(ephemeral=False)  # This can be public
        
        # Check if user is in any blacklisted groups
        is_clean, blacklisted_groups, message = await self.blacklist_system.check_user_blacklisted_groups(
            interaction.guild.id, roblox_username
        )
        
        if not is_clean and blacklisted_groups:
            # Create an embed with blacklisted groups
            embed = self.blacklist_system.create_blacklist_embed(roblox_username, blacklisted_groups)
            await interaction.followup.send(
                content=f"{interaction.user.mention}, user **{roblox_username}** is in blacklisted groups!",
                embed=embed
            )
        else:
            # User is not in any blacklisted groups
            embed = Embed(
                title="Background Check Passed ✅",
                description=f"User **{roblox_username}** is not in any blacklisted groups.",
                color=Color.green()
            )
            await interaction.followup.send(embed=embed)
        
        logger.info(f"Background check performed by {interaction.user.name} on {roblox_username}")
    
    @app_commands.command(name="blacklistedgroups", description="Add a Roblox group to the blacklist")
    @app_commands.describe(
        group_id="The Roblox group ID to blacklist"
    )
    async def blacklistedgroups(
        self, 
        interaction: discord.Interaction, 
        group_id: str = None
    ):
        """Add a Roblox group to the blacklist or list all blacklisted groups"""
        await interaction.response.defer(ephemeral=True)
        
        # Check if user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("You need administrator permissions to use this command.", ephemeral=True)
            return
        
        if group_id:
            # Add the group to the blacklist
            success, message = await self.blacklist_system.add_blacklisted_group(interaction.guild.id, group_id)
            await interaction.followup.send(message, ephemeral=True)
            logger.info(f"Added group {group_id} to blacklist by {interaction.user.name}")
        else:
            # No group ID provided, show the list of blacklisted groups
            groups, message = await self.blacklist_system.list_blacklisted_groups(interaction.guild.id)
            
            if not groups:
                await interaction.followup.send("No groups are currently blacklisted.", ephemeral=True)
                return
            
            # Create an embed with the list of blacklisted groups
            embed = Embed(
                title="Blacklisted Groups",
                description=f"There are {len(groups)} blacklisted groups:",
                color=Color.blue()
            )
            
            for i, group in enumerate(groups):
                embed.add_field(
                    name=f"{i+1}. {group['name']}",
                    value=f"Group ID: {group['id']} (use `/removeblacklist {group['id']}` to remove)",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"Listed blacklisted groups for {interaction.user.name}")
            
    @app_commands.command(name="removeblacklist", description="Remove a Roblox group from the blacklist")
    @app_commands.describe(
        group_id="The Roblox group ID to remove from the blacklist"
    )
    async def removeblacklist(
        self, 
        interaction: discord.Interaction, 
        group_id: str
    ):
        """Remove a Roblox group from the blacklist"""
        await interaction.response.defer(ephemeral=True)
        
        # Check if user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("You need administrator permissions to use this command.", ephemeral=True)
            return
        
        # Remove the group from the blacklist
        success, message = await self.blacklist_system.remove_blacklisted_group(interaction.guild.id, group_id)
        await interaction.followup.send(message, ephemeral=True)
        logger.info(f"Removed group {group_id} from blacklist by {interaction.user.name}")
        
