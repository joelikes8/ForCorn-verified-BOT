import logging
import discord
from discord import Embed, Color

logger = logging.getLogger(__name__)

class BlacklistSystem:
    def __init__(self, roblox_api, config):
        self.roblox_api = roblox_api
        self.config = config
    
    async def add_blacklisted_group(self, guild_id, group_id):
        """Add a group to the blacklist"""
        try:
            # Validate group ID exists
            group_info = await self.roblox_api.get_group_info(group_id)
            if not group_info:
                return False, "Invalid group ID. Please check the ID and try again."
            
            # Get server config
            server_config = self.config.get_server_config(guild_id)
            
            # Check if group is already blacklisted
            if str(group_id) in server_config.get("blacklisted_groups", []):
                return False, f"Group '{group_info['name']}' is already blacklisted."
            
            # Add to blacklist
            blacklisted_groups = server_config.get("blacklisted_groups", [])
            blacklisted_groups.append(str(group_id))
            
            # Update config
            self.config.update_server_config(guild_id, "blacklisted_groups", blacklisted_groups)
            
            return True, f"Added '{group_info['name']}' (ID: {group_id}) to the blacklisted groups."
        
        except Exception as e:
            logger.error(f"Error adding blacklisted group: {e}")
            return False, "An error occurred while adding the group to the blacklist."
    
    async def remove_blacklisted_group(self, guild_id, group_id):
        """Remove a group from the blacklist"""
        try:
            # Get server config
            server_config = self.config.get_server_config(guild_id)
            
            # Check if group is blacklisted
            blacklisted_groups = server_config.get("blacklisted_groups", [])
            
            if str(group_id) not in blacklisted_groups:
                return False, "This group is not in the blacklist."
            
            # Remove from blacklist
            blacklisted_groups.remove(str(group_id))
            
            # Update config
            self.config.update_server_config(guild_id, "blacklisted_groups", blacklisted_groups)
            
            # Try to get group name for the response
            group_info = await self.roblox_api.get_group_info(group_id)
            group_name = group_info["name"] if group_info else str(group_id)
            
            return True, f"Removed '{group_name}' (ID: {group_id}) from the blacklisted groups."
        
        except Exception as e:
            logger.error(f"Error removing blacklisted group: {e}")
            return False, "An error occurred while removing the group from the blacklist."
    
    async def list_blacklisted_groups(self, guild_id):
        """List all blacklisted groups"""
        try:
            # Get server config
            server_config = self.config.get_server_config(guild_id)
            
            # Get blacklisted groups
            blacklisted_groups = server_config.get("blacklisted_groups", [])
            
            if not blacklisted_groups:
                return [], "No groups are currently blacklisted."
            
            # Get group names
            groups_info = []
            for group_id in blacklisted_groups:
                group_info = await self.roblox_api.get_group_info(group_id)
                if group_info:
                    groups_info.append({
                        "id": group_id,
                        "name": group_info["name"]
                    })
                else:
                    groups_info.append({
                        "id": group_id,
                        "name": "Unknown Group"
                    })
            
            return groups_info, f"Found {len(groups_info)} blacklisted groups."
        
        except Exception as e:
            logger.error(f"Error listing blacklisted groups: {e}")
            return [], "An error occurred while listing the blacklisted groups."
    
    async def check_user_blacklisted_groups(self, guild_id, roblox_username):
        """Check if a user is in any blacklisted groups"""
        try:
            # Get user ID
            user_id = await self.roblox_api.get_user_id_from_username(roblox_username)
            if not user_id:
                return False, [], "Could not find that Roblox username."
            
            # Get server config
            server_config = self.config.get_server_config(guild_id)
            
            # Get blacklisted groups
            blacklisted_groups = server_config.get("blacklisted_groups", [])
            
            if not blacklisted_groups:
                return True, [], "No groups are currently blacklisted."
            
            # Get user's groups
            user_groups = await self.roblox_api.get_user_groups(user_id)
            
            # Check for blacklisted groups
            blacklisted_user_groups = []
            for group in user_groups:
                group_id = str(group["group"]["id"])
                if group_id in blacklisted_groups:
                    blacklisted_user_groups.append({
                        "id": group_id,
                        "name": group["group"]["name"],
                        "url": f"https://www.roblox.com/groups/{group_id}"
                    })
            
            if blacklisted_user_groups:
                return False, blacklisted_user_groups, f"User is in {len(blacklisted_user_groups)} blacklisted groups."
            else:
                return True, [], "User is not in any blacklisted groups."
        
        except Exception as e:
            logger.error(f"Error checking user blacklisted groups: {e}")
            return False, [], "An error occurred while checking the user's groups."
    
    def create_blacklist_embed(self, username, blacklisted_groups):
        """Create an embed for blacklisted groups"""
        embed = Embed(
            title="Blacklisted Groups Check",
            description=f"User **{username}** is in the following blacklisted groups:",
            color=Color.red()
        )
        
        for i, group in enumerate(blacklisted_groups):
            embed.add_field(
                name=f"{i+1}. {group['name']}",
                value=f"Group ID: {group['id']}\n[Group Link]({group['url']})",
                inline=False
            )
        
        embed.set_footer(text="Please leave these groups and try again.")
        
        return embed
