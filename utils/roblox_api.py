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
            
            # Get CSRF token for requests that might need it
            if method in ["POST", "PATCH", "PUT", "DELETE"]:
                csrf_token = await self.get_csrf_token(token)
                if csrf_token:
                    headers["X-CSRF-TOKEN"] = csrf_token
                else:
                    logger.warning(f"Failed to get CSRF token for {method} request to {url}")
        
        # Add content type for requests with data
        if data and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        
        try:
            logger.info(f"Making {method} request to {url}")
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                    timeout=15  # Add timeout for better reliability
                ) as response:
                    if response.status == 200:
                        try:
                            return await response.json()
                        except aiohttp.ContentTypeError:
                            # Some endpoints might return non-JSON responses even with 200 status
                            response_text = await response.text()
                            logger.warning(f"Could not parse JSON from 200 response: {response_text}")
                            return {"success": True, "text": response_text}
                    else:
                        error_text = await response.text()
                        logger.error(f"Error {response.status} from Roblox API: {error_text}")
                        
                        # Check for common errors and log more details
                        if response.status == 401:
                            logger.error("Authentication failed - token may be invalid or expired")
                        elif response.status == 403:
                            # Check if we need a CSRF token
                            if "X-CSRF-TOKEN" not in headers and method != "GET":
                                logger.error("Missing CSRF token for non-GET request")
                            else:
                                logger.error("Permission denied - check if the authenticated user has necessary permissions")
                        elif response.status == 404:
                            logger.error(f"Resource not found at {url}")
                        elif response.status == 429:
                            logger.error("Rate limit exceeded. Please try again later.")
                        
                        return None
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection error for {url}: {e}")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Client error for {url}: {e}")
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
                # First try the auth endpoint to trigger CSRF generation
                async with session.post(
                    f"{self.base_url}/csrf-token",
                    headers=headers,
                    timeout=15  # Increase timeout for reliability
                ) as response:
                    # Roblox returns 403 with a CSRF token when the endpoint is hit without a CSRF token
                    if response.status == 403:
                        csrf_token = response.headers.get("x-csrf-token")
                        if csrf_token:
                            logger.info("Successfully obtained CSRF token")
                            return csrf_token
                    
                    # If we didn't get a CSRF token from the first attempt, try an alternative endpoint
                    if response.status != 403 or not response.headers.get("x-csrf-token"):
                        logger.warning(f"First CSRF token attempt failed with status {response.status}, trying alternative endpoint")
                        # Try another endpoint that also returns a CSRF token
                        async with session.post(
                            "https://auth.roblox.com/v2/logout",
                            headers=headers,
                            timeout=15
                        ) as alt_response:
                            if alt_response.status == 403:
                                csrf_token = alt_response.headers.get("x-csrf-token")
                                if csrf_token:
                                    logger.info("Successfully obtained CSRF token from alternative endpoint")
                                    return csrf_token
                            
                            # Log detailed information if both attempts fail
                            logger.error(f"Failed to get CSRF token from both endpoints. Status: {alt_response.status}")
                            try:
                                error_text = await alt_response.text()
                                logger.error(f"Response body: {error_text}")
                            except:
                                pass
                            
                    return ""  # Return empty string if all attempts fail
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection error while getting CSRF token: {e}")
            return ""
        except aiohttp.ClientError as e:
            logger.error(f"Client error while getting CSRF token: {e}")
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
    
    async def rank_user_in_group(self, user_id, group_id, rank_id, token, attempt=1):
        """Change a user's rank in a group with fallback to alternative endpoints"""
        # Primary API endpoint
        url = f"{self.groups_base_url}/v1/groups/{group_id}/users/{user_id}"
        data = {"roleId": rank_id}
        
        # Alternative URLs for backup attempts
        alt_url_1 = f"https://groups.roblox.com/v1/groups/{group_id}/users/{user_id}/role"
        alt_url_2 = f"https://www.roblox.com/groups/api/change-member-rank"
        
        # Clean up token if needed
        if token.startswith(".ROBLOSECURITY="):
            token = token.replace(".ROBLOSECURITY=", "")
        token = token.strip().strip('"\'')
        
        # First, get a CSRF token separately with detailed logging
        csrf_token = await self.get_csrf_token(token)
        if not csrf_token:
            logger.error(f"Failed to get CSRF token for ranking user {user_id} in group {group_id}")
            
            # If this is the first attempt, try again with a different endpoint
            if attempt < 3:
                logger.info(f"Retrying with alternative method (attempt {attempt + 1})")
                return await self.rank_user_in_group(user_id, group_id, rank_id, token, attempt + 1)
            return False
        
        # Use different URLs and methods based on attempt number
        if attempt == 1:
            # Primary method: PATCH to groups API
            current_url = url
            method = "PATCH"
            current_data = data
        elif attempt == 2:
            # Alternative 1: POST to role endpoint
            current_url = alt_url_1
            method = "POST" 
            current_data = {"roleId": rank_id}
        else:
            # Alternative 2: POST to legacy endpoint
            current_url = alt_url_2
            method = "POST"
            current_data = {
                "groupId": group_id,
                "userId": user_id,
                "roleSetId": rank_id
            }
        
        headers = {
            "Cookie": f".ROBLOSECURITY={token}",
            "X-CSRF-TOKEN": csrf_token,
            "Content-Type": "application/json",
            "User-Agent": "Roblox/RankingBot (Discord Bot)"
        }
        
        # Make the request manually to get more detailed error information
        try:
            logger.info(f"Attempting to rank user with method {attempt} to URL: {current_url}")
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=current_url,
                    json=current_data,
                    headers=headers,
                    timeout=20  # Longer timeout for ranking
                ) as response:
                    # Log detailed response information
                    response_text = await response.text()
                    
                    # Check if the request was successful
                    if response.status == 200:
                        logger.info(f"Successfully ranked user {user_id} to role {rank_id} in group {group_id} (method {attempt})")
                        return True
                    else:
                        logger.error(f"Failed to rank user {user_id} in group {group_id}. Status: {response.status}")
                        logger.error(f"Response body: {response_text}")
                        
                        # If this is the first or second attempt and we get an error, try the next method
                        if attempt < 3:
                            logger.info(f"Retrying with alternative method (attempt {attempt + 1})")
                            return await self.rank_user_in_group(user_id, group_id, rank_id, token, attempt + 1)
                        
                        # Log specific error details on final attempt
                        if response.status == 401:
                            logger.error("Authentication failed - token may be invalid or expired")
                        elif response.status == 403:
                            logger.error("Permission denied - check if the authenticated user has ranking permissions")
                        elif response.status == 400:
                            logger.error("Bad request - role ID may be invalid or user cannot be ranked to this role")
                        
                        return False
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection error while ranking user (method {attempt}): {e}")
            # Try next method if available
            if attempt < 3:
                logger.info(f"Retrying with alternative method due to connection error (attempt {attempt + 1})")
                return await self.rank_user_in_group(user_id, group_id, rank_id, token, attempt + 1)
            return False
        except aiohttp.ClientError as e:
            logger.error(f"Client error while ranking user (method {attempt}): {e}")
            # Try next method if available
            if attempt < 3:
                logger.info(f"Retrying with alternative method due to client error (attempt {attempt + 1})")
                return await self.rank_user_in_group(user_id, group_id, rank_id, token, attempt + 1)
            return False
        except Exception as e:
            logger.error(f"Error ranking user {user_id} in group {group_id} (method {attempt}): {e}")
            # Try next method if available
            if attempt < 3:
                logger.info(f"Retrying with alternative method due to exception (attempt {attempt + 1})")
                return await self.rank_user_in_group(user_id, group_id, rank_id, token, attempt + 1)
            return False
    
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
