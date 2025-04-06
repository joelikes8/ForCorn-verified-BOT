import os
import logging
import aiohttp
from aiohttp.client_exceptions import ClientError

logger = logging.getLogger(__name__)

class RobloxAPI:
    def __init__(self):
        self.base_url = "https://api.roblox.com"
        self.users_base_url = "https://users.roblox.com"
        self.groups_base_url = "https://groups.roblox.com"
        self.thumbnails_base_url = "https://thumbnails.roblox.com"
        
        # Cache for user IDs and usernames
        self.username_to_id_cache = {}
        self.id_to_username_cache = {}
    
    async def make_request(self, url, method="GET", headers=None, data=None, params=None, token=None):
        """Make a request to the Roblox API"""
        if headers is None:
            headers = {}
        
        if token:
            # Clean up token if it includes the full cookie format
            if token.startswith(".ROBLOSECURITY="):
                token = token.replace(".ROBLOSECURITY=", "")
            
            # Remove any extra spaces or quotes
            token = token.strip().strip('"\'')
            
            headers["Cookie"] = f".ROBLOSECURITY={token}"
            csrf_token = await self.get_csrf_token(token)
            if csrf_token:
                headers["X-CSRF-TOKEN"] = csrf_token
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"Error {response.status} from Roblox API: {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Request to {url} failed: {e}")
            return None
    
    async def get_csrf_token(self, token):
        """Get CSRF token for Roblox API requests that require authentication"""
        # Clean up token if it includes the full cookie format
        if token.startswith(".ROBLOSECURITY="):
            token = token.replace(".ROBLOSECURITY=", "")
        
        # Remove any extra spaces or quotes
        token = token.strip().strip('"\'')
        
        headers = {"Cookie": f".ROBLOSECURITY={token}"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/csrf-token",
                    headers=headers
                ) as response:
                    if response.status == 403:
                        csrf_token = response.headers.get("x-csrf-token")
                        if csrf_token:
                            logger.info("Successfully obtained CSRF token")
                            return csrf_token
                    logger.error(f"Failed to get CSRF token: Status {response.status}")
                    return ""
        except Exception as e:
            logger.error(f"Failed to get CSRF token: {e}")
            return ""
    
    async def get_user_id_from_username(self, username):
        """Get a user's ID from their username"""
        # Check cache first
        if username in self.username_to_id_cache:
            return self.username_to_id_cache[username]
        
        url = f"{self.users_base_url}/v1/usernames/users"
        data = {
            "usernames": [username],
            "excludeBannedUsers": True
        }
        
        response = await self.make_request(url, method="POST", data=data)
        
        if response and "data" in response and len(response["data"]) > 0:
            user_id = response["data"][0]["id"]
            # Cache the result
            self.username_to_id_cache[username] = user_id
            self.id_to_username_cache[user_id] = username
            return user_id
        
        return None
    
    async def get_username_from_id(self, user_id):
        """Get a user's username from their ID"""
        # Check cache first
        if user_id in self.id_to_username_cache:
            return self.id_to_username_cache[user_id]
        
        url = f"{self.users_base_url}/v1/users/{user_id}"
        
        response = await self.make_request(url)
        
        if response and "name" in response:
            username = response["name"]
            # Cache the result
            self.id_to_username_cache[user_id] = username
            self.username_to_id_cache[username] = user_id
            return username
        
        return None
    
    async def get_user_description(self, user_id):
        """Get a user's profile description"""
        url = f"{self.users_base_url}/v1/users/{user_id}"
        
        response = await self.make_request(url)
        
        if response and "description" in response:
            return response["description"]
        
        return ""
    
    async def get_user_thumbnail(self, user_id, size="420x420", format="png", is_circular=False):
        """Get a user's thumbnail URL"""
        url = f"{self.thumbnails_base_url}/v1/users/avatar"
        params = {
            "userIds": user_id,
            "size": size,
            "format": format,
            "isCircular": is_circular
        }
        
        response = await self.make_request(url, params=params)
        
        if response and "data" in response and len(response["data"]) > 0:
            return response["data"][0].get("imageUrl")
        
        return None
    
    async def get_group_info(self, group_id):
        """Get information about a group"""
        url = f"{self.groups_base_url}/v1/groups/{group_id}"
        
        return await self.make_request(url)
    
    async def get_user_groups(self, user_id):
        """Get all groups a user is in"""
        url = f"{self.groups_base_url}/v2/users/{user_id}/groups/roles"
        
        response = await self.make_request(url)
        
        if response and "data" in response:
            return response["data"]
        
        return []
    
    async def get_user_group_rank(self, user_id, group_id):
        """Get a user's rank in a specific group"""
        user_groups = await self.get_user_groups(user_id)
        
        for group in user_groups:
            if str(group["group"]["id"]) == str(group_id):
                return group["role"]["name"]
        
        return None
    
    async def is_user_in_group(self, user_id, group_id):
        """Check if a user is in a specific group"""
        user_groups = await self.get_user_groups(user_id)
        
        for group in user_groups:
            if str(group["group"]["id"]) == str(group_id):
                return True
        
        return False
    
    async def rank_user_in_group(self, user_id, group_id, rank_id, token):
        """Change a user's rank in a group"""
        url = f"{self.groups_base_url}/v1/groups/{group_id}/users/{user_id}"
        data = {"roleId": rank_id}
        
        response = await self.make_request(url, method="PATCH", data=data, token=token)
        
        return response is not None
    
    async def get_group_roles(self, group_id):
        """Get all roles in a group"""
        url = f"{self.groups_base_url}/v1/groups/{group_id}/roles"
        
        response = await self.make_request(url)
        
        if response and "roles" in response:
            return response["roles"]
        
        return []
        
    async def get_authenticated_user(self, token):
        """Get information about the authenticated user from token"""
        # Clean up token if it includes the full cookie format
        if token.startswith(".ROBLOSECURITY="):
            token = token.replace(".ROBLOSECURITY=", "")
        
        # Remove any extra spaces or quotes
        token = token.strip().strip('"\'')
        
        url = "https://users.roblox.com/v1/users/authenticated"
        headers = {"Cookie": f".ROBLOSECURITY={token}"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        logger.info(f"Successfully authenticated as Roblox user: {user_data.get('name', 'Unknown')}")
                        return user_data
                    else:
                        logger.error(f"Failed to get authenticated user: HTTP {response.status}")
                        # Log more details for debugging
                        error_text = await response.text()
                        logger.error(f"Error response: {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error getting authenticated user: {e}")
            return None
