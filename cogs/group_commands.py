import discord
from discord import app_commands
from discord.ext import commands
from discord import Embed, Color
import logging
from datetime import datetime
from utils.roblox_api import RobloxAPI
from app import db

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
        
        # Check if this is a guild interaction and user has proper permissions
        if not interaction.guild:
            await interaction.followup.send("This command can only be used in a server.", ephemeral=True)
            return
            
        # Get the member object instead of just the user
        member = interaction.guild.get_member(interaction.user.id)
        if not member:
            try:
                member = await interaction.guild.fetch_member(interaction.user.id)
            except discord.errors.NotFound:
                await interaction.followup.send("Could not verify your server permissions.", ephemeral=True)
                return
                
        # Check admin permissions with the member object
        if not member.guild_permissions.administrator:
            await interaction.followup.send("You need administrator permissions to use this command.", ephemeral=True)
            return
        
        try:
            # Save in database first to establish connection between group and guild
            from app import app, db
            from models import Guild
            
            with app.app_context():
                guild_record = Guild.query.get(interaction.guild.id)
                if guild_record:
                    guild_record.group_id = group_id
                    logger.info(f"Updated group ID for guild {interaction.guild.id} to {group_id}")
                else:
                    new_guild = Guild(id=interaction.guild.id, group_id=group_id)
                    db.session.add(new_guild)
                    logger.info(f"Created new guild record with group ID {group_id}")
                db.session.commit()
            
            # Validate group ID
            group_info = await self.roblox_api.get_group_info(group_id)
            
            if not group_info:
                # Try an alternative API to get basic group info
                await interaction.followup.send("Could not verify group details from Roblox API, but the ID has been saved.", ephemeral=True)
                # Still update the server config
                self.bot.config.update_server_config(interaction.guild.id, "group_id", group_id)
                return
            
            # Update server config
            self.bot.config.update_server_config(interaction.guild.id, "group_id", group_id)
            
            # Create success embed
            embed = Embed(
                title="Group Setup Successful ✅",
                description=f"Successfully set up the group for this server.",
                color=Color.green()
            )
            
            embed.add_field(name="Group Name", value=group_info.get("name", "Unknown"))
            embed.add_field(name="Group ID", value=group_id)
            embed.add_field(name="Member Count", value=str(group_info.get("memberCount", "Unknown")), inline=False)
            
            # Add a reminder to set up the token if not already set
            guild_id = interaction.guild.id
            from app import app
            from models import RobloxToken
            
            token_exists = False
            with app.app_context():
                # Check if a token exists for this guild
                token_exists = RobloxToken.query.filter_by(discord_id=guild_id).first() is not None
                
                # If not found for guild, check for owner
                if not token_exists:
                    owner_id = interaction.guild.owner_id
                    token_exists = RobloxToken.query.filter_by(discord_id=owner_id).first() is not None
            
            if not token_exists:
                embed.add_field(
                    name="Next Step: Set Up Token ⚠️",
                    value="For ranking to work, the server owner needs to set up a Roblox API token using the `/setuptoken` command in DMs.",
                    inline=False
                )
            
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
            
            # Store the token both for the user and associated guild
            from app import app
            from models import RobloxToken
            
            try:
                with app.app_context():
                    # First store for the user who ran the command
                    user_token = RobloxToken.query.filter_by(discord_id=interaction.user.id).first()
                    if user_token:
                        user_token.encrypted_token = token
                        user_token.updated_at = datetime.utcnow()
                        logger.info(f"Updated token for user {interaction.user.id}")
                    else:
                        new_token = RobloxToken(discord_id=interaction.user.id, encrypted_token=token)
                        db.session.add(new_token)
                        logger.info(f"Added new token for user {interaction.user.id}")
                    
                    db.session.commit()
                    
                # Also use the config method for any guilds they own
                for guild in self.bot.guilds:
                    if interaction.user.id == guild.owner_id:
                        self.bot.config.update_server_config(guild.id, "roblox_token", token)
                        logger.info(f"Stored token for guild {guild.id} owner {interaction.user.id}")
                        
                        # Also store directly for the guild ID
                        with app.app_context():
                            guild_token = RobloxToken.query.filter_by(discord_id=guild.id).first()
                            if guild_token:
                                guild_token.encrypted_token = token
                                guild_token.updated_at = datetime.utcnow()
                            else:
                                new_guild_token = RobloxToken(discord_id=guild.id, encrypted_token=token)
                                db.session.add(new_guild_token)
                            
                            db.session.commit()
                            logger.info(f"Stored token directly with guild ID {guild.id}")
            except Exception as e:
                logger.error(f"Error storing Roblox token: {e}")
            
            # Create success embed
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
            
            # Check if they are a guild owner before setting up the token
            is_guild_owner = False
            for guild in self.bot.guilds:
                if interaction.user.id == guild.owner_id:
                    is_guild_owner = True
                    break
                    
            if not is_guild_owner:
                await interaction.followup.send(
                    "You need to be the owner of at least one server where the bot is present to use this command.",
                    ephemeral=True
                )
                return
                
            # If we got here, they are a guild owner and token setup was successful
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"Roblox token set by {interaction.user.name} (ID: {interaction.user.id}) for Roblox account: {roblox_username}")
            
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
        
        # Check if interaction is in a guild
        if not interaction.guild:
            await interaction.followup.send("This command can only be used in a server.", ephemeral=True)
            return
            
        # Check if user has permission to rank
        # Get the member object instead of just the user
        member = interaction.guild.get_member(interaction.user.id)
        if not member:
            try:
                member = await interaction.guild.fetch_member(interaction.user.id)
            except discord.errors.NotFound:
                await interaction.followup.send("Could not verify your server permissions.", ephemeral=True)
                return
                
        # Now check permissions with the member object
        if rank_name and not member.guild_permissions.manage_roles:
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
            from models import RobloxToken, Guild
            
            # First try with guild ID
            guild_id = interaction.guild.id
            
            try:
                with app.app_context():
                    # Look for tokens associated with any user who has set up a token for this guild
                    token_entry = None
                    
                    # First check all tokens in the database
                    all_tokens = RobloxToken.query.all()
                    for token in all_tokens:
                        logger.info(f"Found token for user ID: {token.discord_id}")
                    
                    # Try guild ID first
                    token_entry = RobloxToken.query.filter_by(discord_id=guild_id).first()
                    
                    # If not found, try the owner ID
                    if not token_entry:
                        owner_id = interaction.guild.owner_id
                        token_entry = RobloxToken.query.filter_by(discord_id=owner_id).first()
                        logger.info(f"Checked owner ID {owner_id} for token: {'Found' if token_entry else 'Not found'}")
                    
                    # If still not found, check if we have a token linked to this guild
                    if not token_entry:
                        guild_data = Guild.query.get(guild_id)
                        if guild_data:
                            logger.info(f"Guild data found for {guild_id}, group_id: {guild_data.group_id}")
                    
                    roblox_token = token_entry.encrypted_token if token_entry else None
                    logger.info(f"Retrieved Roblox token for guild {guild_id}: {'Found' if token_entry else 'Not found'}")
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
            
            # Detailed logging for debugging
            logger.info(f"Rank command result - success: {success}, user: {roblox_username}, target role: {target_role['name']}")
            
            if success:
                embed = Embed(
                    title="Rank Changed Successfully ✅",
                    description=f"Successfully ranked **{roblox_username}**.",
                    color=Color.green()
                )
                embed.add_field(name="Previous Rank", value=current_rank or "No Rank")
                embed.add_field(name="New Rank", value=target_role["name"])
                
                # If in simulation mode, add a note
                if hasattr(self.roblox_api, 'simulation_mode') and self.roblox_api.simulation_mode:
                    embed.set_footer(text="Note: This is running in simulation mode (Roblox API unavailable)")
                
                await interaction.followup.send(embed=embed)
                logger.info(f"User {roblox_username} ranked to {target_role['name']} by {interaction.user.name}")
            else:
                # Create more detailed error message
                error_message = "Failed to rank the user. "
                
                # Check if we're in simulation mode but it still failed (should be rare)
                if hasattr(self.roblox_api, 'simulation_mode') and self.roblox_api.simulation_mode:
                    error_message += "Simulation failed. This is unexpected - please check logs."
                else:
                    error_message += "Please check the following:\n"
                    error_message += "• The group ID is correct\n"
                    error_message += "• The Roblox token is valid\n"
                    error_message += "• The account has permission to rank in this group\n"
                    error_message += "• The target rank is valid for this user"
                
                await interaction.followup.send(
                    error_message,
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
