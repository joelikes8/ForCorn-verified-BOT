import discord
from discord import app_commands
from discord.ext import commands
from discord import Embed, Color
import logging
from utils.roblox_api import RobloxAPI

logger = logging.getLogger(__name__)

class GroupCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roblox_api = RobloxAPI()
    
    @app_commands.command(name="setupid", description="Set up the Roblox group ID for the server")
    @app_commands.describe(group_id="The Roblox group ID")
    async def setupid(self, interaction: discord.Interaction, group_id: str):
        """Set up the Roblox group ID for the server"""
        await interaction.response.defer(ephemeral=True)
        
        # Check if user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("You need administrator permissions to use this command.", ephemeral=True)
            return
        
        try:
            # Validate group ID
            group_info = await self.roblox_api.get_group_info(group_id)
            
            if not group_info:
                await interaction.followup.send("Invalid group ID. Please check the ID and try again.", ephemeral=True)
                return
            
            # Update server config
            self.bot.config.update_server_config(interaction.guild.id, "group_id", group_id)
            
            # Create success embed
            embed = Embed(
                title="Group Setup Successful ✅",
                description=f"Successfully set up the group for this server.",
                color=Color.green()
            )
            
            embed.add_field(name="Group Name", value=group_info["name"])
            embed.add_field(name="Group ID", value=group_id)
            embed.add_field(name="Member Count", value=str(group_info.get("memberCount", "Unknown")), inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"Group ID set to {group_id} by {interaction.user.name} (ID: {interaction.user.id})")
            
        except Exception as e:
            logger.error(f"Error setting up group ID: {e}")
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="setuptoken", description="Set up the Roblox API token for ranking")
    @app_commands.describe(token="Your Roblox account cookie (send this in DMs only!)")
    async def setuptoken(self, interaction: discord.Interaction, token: str):
        """Set up the Roblox API token for ranking (only in DMs)"""
        # Check if command is being used in DMs
        if interaction.guild is not None:
            await interaction.response.send_message(
                "⚠️ For security reasons, please use this command in DMs only!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Clean up token if needed
            if token.startswith(".ROBLOSECURITY="):
                token = token.replace(".ROBLOSECURITY=", "")
            token = token.strip().strip('"\'')
            
            # First, check token format
            if len(token) < 100:  # Typically Roblox tokens are long strings
                await interaction.followup.send(
                    "The token format appears to be invalid. Make sure you're providing the entire .ROBLOSECURITY cookie value.\n\n"
                    "To get your Roblox cookie:\n"
                    "1. Go to roblox.com and login\n"
                    "2. Press F12 to open Developer Tools\n"
                    "3. Go to the 'Application' or 'Storage' tab\n"
                    "4. Look for 'Cookies' and then 'roblox.com'\n"
                    "5. Find the .ROBLOSECURITY cookie and copy its value",
                    ephemeral=True
                )
                return
            
            # Validate the token by trying to get the authenticated user
            logger.info(f"Attempting to validate Roblox token for user {interaction.user.name}")
            user_data = await self.roblox_api.get_authenticated_user(token)
            if not user_data:
                await interaction.followup.send(
                    "Failed to authenticate with the provided token. The token may be expired or invalid.\n\n"
                    "Please make sure you've copied the entire token value and try again.",
                    ephemeral=True
                )
                return
            
            if "name" not in user_data:
                await interaction.followup.send(
                    "Authentication succeeded but could not retrieve your Roblox username. Please try again.",
                    ephemeral=True
                )
                return
            
            # Get the Roblox username
            roblox_username = user_data["name"]
            roblox_display_name = user_data.get("displayName", roblox_username)
            roblox_id = user_data["id"]
            
            # Store the token
            for guild in self.bot.guilds:
                if interaction.user.id == guild.owner_id:
                    self.bot.config.update_server_config(guild.id, "roblox_token", token)
                    
                    embed = Embed(
                        title="Token Setup Successful ✅",
                        description=f"Successfully logged in as **{roblox_username}** (Display Name: {roblox_display_name}).",
                        color=Color.green()
                    )
                    
                    # Get the user's avatar
                    avatar_url = await self.roblox_api.get_user_thumbnail(roblox_id)
                    if avatar_url:
                        embed.set_thumbnail(url=avatar_url)
                    
                    embed.add_field(
                        name="Account Info",
                        value=f"**Username:** {roblox_username}\n**User ID:** {roblox_id}",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="Security Notice",
                        value="Your token has been securely stored. Never share your token with anyone else.",
                        inline=False
                    )
                    
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    logger.info(f"Roblox token set by {interaction.user.name} (ID: {interaction.user.id}) for Roblox account: {roblox_username}")
                    return
            
            await interaction.followup.send(
                "You need to be the owner of at least one server where the bot is present to use this command.",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error setting up token: {e}")
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="rank", description="Rank a user in the Roblox group")
    @app_commands.describe(
        roblox_username="The Roblox username to rank",
        rank_name="The name of the rank to give (leave empty to view current rank)"
    )
    async def rank(
        self, 
        interaction: discord.Interaction, 
        roblox_username: str,
        rank_name: str = None
    ):
        """Rank a user in the Roblox group"""
        await interaction.response.defer(ephemeral=False)  # This can be public
        
        # Check if user has permission to rank
        if not interaction.user.guild_permissions.manage_roles and rank_name:
            await interaction.followup.send("You need manage roles permission to rank users.", ephemeral=True)
            return
        
        # Get server config
        server_config = self.bot.config.get_server_config(interaction.guild.id)
        group_id = server_config.get("group_id")
        
        if not group_id:
            await interaction.followup.send(
                "No group ID has been set up. Please ask an administrator to set it up using /setupid.",
                ephemeral=True
            )
            return
        
        try:
            # Get Roblox user ID
            user_id = await self.roblox_api.get_user_id_from_username(roblox_username)
            
            if not user_id:
                await interaction.followup.send(f"Could not find Roblox user: {roblox_username}", ephemeral=True)
                return
            
            # Check if user is in the group
            is_in_group = await self.roblox_api.is_user_in_group(user_id, group_id)
            
            if not is_in_group:
                embed = Embed(
                    title="User Not in Group ❌",
                    description=f"User **{roblox_username}** is not in the group.",
                    color=Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Get current rank
            current_rank = await self.roblox_api.get_user_group_rank(user_id, group_id)
            
            # If no rank name is provided, just show current rank
            if not rank_name:
                embed = Embed(
                    title="User Rank Information",
                    description=f"Information about **{roblox_username}** in the group:",
                    color=Color.blue()
                )
                embed.add_field(name="Current Rank", value=current_rank or "No Rank")
                await interaction.followup.send(embed=embed)
                return
            
            # If rank name is provided, change the rank
            # Get token from database
            from app import app
            from models import RobloxToken
            
            # Get guild owner ID
            owner_id = interaction.guild.owner_id
            
            try:
                with app.app_context():
                    token_entry = RobloxToken.query.filter_by(discord_id=owner_id).first()
                    roblox_token = token_entry.encrypted_token if token_entry else None
                    logger.info(f"Retrieved Roblox token for guild owner {owner_id}: {'Found' if token_entry else 'Not found'}")
            except Exception as e:
                logger.error(f"Error retrieving Roblox token: {e}")
                roblox_token = None
            
            if not roblox_token:
                await interaction.followup.send(
                    "No Roblox API token has been set up. Please ask the server owner to set it up using /setuptoken in DMs.",
                    ephemeral=True
                )
                return
            
            # Get group roles
            group_roles = await self.roblox_api.get_group_roles(group_id)
            
            # Find the role with the given name
            target_role = None
            for role in group_roles:
                if role["name"].lower() == rank_name.lower():
                    target_role = role
                    break
            
            if not target_role:
                await interaction.followup.send(f"Could not find rank: {rank_name}", ephemeral=True)
                return
            
            # Change the rank
            success = await self.roblox_api.rank_user_in_group(
                user_id, 
                group_id, 
                target_role["id"], 
                roblox_token
            )
            
            if success:
                embed = Embed(
                    title="Rank Changed Successfully ✅",
                    description=f"Successfully ranked **{roblox_username}**.",
                    color=Color.green()
                )
                embed.add_field(name="Previous Rank", value=current_rank or "No Rank")
                embed.add_field(name="New Rank", value=target_role["name"])
                await interaction.followup.send(embed=embed)
                logger.info(f"User {roblox_username} ranked to {target_role['name']} by {interaction.user.name}")
            else:
                await interaction.followup.send(
                    "Failed to rank the user. Please check permissions and try again.",
                    ephemeral=True
                )
            
        except Exception as e:
            logger.error(f"Error ranking user: {e}")
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="ranksetup", description="Set up the Roblox group ID for ranking")
    @app_commands.describe(group_id="The Roblox group ID for ranking")
    async def ranksetup(self, interaction: discord.Interaction, group_id: str):
        """Alias for setupid command"""
        await self.setupid(interaction, group_id)
