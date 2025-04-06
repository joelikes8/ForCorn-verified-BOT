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
        
        # Flag to enable simulation mode instead of real API calls
        # Set to False to use real API calls
        self.simulation_mode = False
        logger.info("Using real Roblox API for all operations")
        
        # Simulate some group roles for testing
        self.simulated_roles = {
            # For any group ID, return these roles
            "default": [
                {"id": 1, "name": "Guest", "rank": 1},
                {"id": 2, "name": "Member", "rank": 2},
                {"id": 3, "name": "Admin", "rank": 3},
                {"id": 4, "name": "Officer", "rank": 4},
                {"id": 5, "name": "Manager", "rank": 5},
                {"id": 6, "name": "Owner", "rank": 6}
            ]
        }
        
        # Simulate user data
        self.simulated_users = {}
    
    async def make_request(self, url, method="GET", headers=None, data=None, params=None, token=None):
        """Make a request to the Roblox API"""
        if headers is None:
            headers = {}
        
        # Add common headers
        # These can help with some connectivity issues
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Roblox Discord Bot"
        headers["Accept"] = "application/json, text/plain, */*"
        
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
        
        # Use a non-standard port for the request
        # This can help bypass some network restrictions
        url_parts = url.split('://')
        if len(url_parts) > 1:
            scheme = url_parts[0]
            host_path = url_parts[1].split('/', 1)
            host = host_path[0]
            path = host_path[1] if len(host_path) > 1 else ""
            
            # Use https scheme for better compatibility
            modified_url = f"https://{host}/{path}"
            url = modified_url
        
        try:
            logger.info(f"Making {method} request to {url}")
            # Use a longer timeout for stability
            timeout = aiohttp.ClientTimeout(total=30)
            
            # Configure SSL context to be less strict if needed
            ssl_context = None
            try:
                import ssl
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            except ImportError:
                logger.warning("Could not import ssl module")
            
            conn = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
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
        
        # Add more headers to simulate a real browser
        headers = {
            "Cookie": f".ROBLOSECURITY={token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Roblox Discord Bot",
            "Accept": "application/json, text/plain, */*",
            "Connection": "keep-alive",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://www.roblox.com/"
        }
        
        # Configure SSL context to be less strict
        ssl_context = None
        try:
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        except ImportError:
            logger.warning("Could not import ssl module")
        
        # Use a longer timeout for stability
        timeout = aiohttp.ClientTimeout(total=30)
        
        # Try multiple different endpoints in order
        endpoints = [
            f"{self.base_url}/csrf-token",
            "https://auth.roblox.com/v2/logout", 
            "https://accountsettings.roblox.com/v1/email",
            "https://auth.roblox.com/v1/account/pin",
            "https://economy.roblox.com/v1/user/currency"
        ]
        
        conn = aiohttp.TCPConnector(ssl=ssl_context)
        
        try:
            async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
                # Try each endpoint until we get a token
                for i, endpoint in enumerate(endpoints):
                    logger.info(f"Attempting to get CSRF token from endpoint {i+1}: {endpoint}")
                    try:
                        async with session.post(endpoint, headers=headers) as response:
                            # Roblox returns 403 with a CSRF token when the endpoint is hit without a CSRF token
                            if response.status == 403:
                                csrf_token = response.headers.get("x-csrf-token")
                                if csrf_token:
                                    logger.info(f"Successfully obtained CSRF token from endpoint {i+1}")
                                    return csrf_token
                            
                            logger.warning(f"No CSRF token from endpoint {i+1}, status: {response.status}")
                    except Exception as e:
                        logger.warning(f"Error trying endpoint {i+1}: {e}")
                
                # If we've tried all endpoints and none worked, return a fallback token
                logger.error("Failed to get CSRF token from any endpoint")
                
                # Try a direct get to the site to see if we can connect at all
                try:
                    async with session.get("https://www.roblox.com/", headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Roblox Discord Bot"
                    }) as test_response:
                        if test_response.status == 200:
                            logger.info("Successfully connected to Roblox site, but couldn't get CSRF token")
                        else:
                            logger.error(f"Could not connect to Roblox site: status {test_response.status}")
                except Exception as e:
                    logger.error(f"Error connecting to Roblox site: {e}")
                
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
            
        # If in simulation mode, simulate user ID generation
        if self.simulation_mode:
            # Generate a consistent user ID from the username
            import hashlib
            # Create a hash of the username and use first 10 digits as the ID
            hash_obj = hashlib.md5(username.encode())
            user_id = int(hash_obj.hexdigest(), 16) % 10000000000
            
            logger.info(f"SIMULATION: Generating user ID {user_id} for username {username}")
            
            # Store in the simulated users dictionary
            self.simulated_users[username] = {
                "id": user_id,
                "name": username,
                "displayName": username,
                "groups": []  # No groups by default
            }
            
            # Cache the result
            self.username_to_id_cache[username] = user_id
            self.id_to_username_cache[user_id] = username
            return user_id
        
        # If not in simulation mode, use the real API
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
        # If in simulation mode, return simulated group info
        if self.simulation_mode:
            logger.info(f"SIMULATION: Getting info for group {group_id}")
            return {
                "id": int(group_id),
                "name": f"Simulated Group {group_id}",
                "description": "This is a simulated group for testing purposes",
                "owner": {
                    "id": 1234567890,
                    "username": "SimulatedOwner"
                },
                "memberCount": 42,
                "created": "2023-01-01T00:00:00Z"
            }
            
        # If not in simulation mode, use the real API
        url = f"{self.groups_base_url}/v1/groups/{group_id}"
        return await self.make_request(url)
    
    async def get_user_groups(self, user_id):
        """Get all groups a user is in"""
        # If in simulation mode, check/create simulated user groups
        if self.simulation_mode:
            logger.info(f"SIMULATION: Getting groups for user {user_id}")
            
            # Find the username for this user ID to get their data
            username = None
            for name, data in self.simulated_users.items():
                if data.get("id") == user_id:
                    username = name
                    break
            
            # If user doesn't exist in simulation, create a new user entry
            if not username:
                username = f"SimUser{user_id}"
                self.simulated_users[username] = {
                    "id": user_id,
                    "name": username,
                    "displayName": username,
                    "groups": []
                }
            
            # If user doesn't have groups yet, add them to the default group
            user_data = self.simulated_users[username]
            if not user_data.get("groups"):
                # Add this user to the default group with default role
                user_data["groups"] = [
                    {
                        "group": {
                            "id": 123456,
                            "name": "Default Simulated Group",
                            "memberCount": 42
                        },
                        "role": {
                            "id": 2,  # Member role ID
                            "name": "Member",
                            "rank": 2
                        }
                    }
                ]
                self.simulated_users[username] = user_data
                
            # Format the response to match Roblox API format
            return user_data.get("groups", [])
            
        # If not in simulation mode, use the real API
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
        # If in simulation mode, use simulated ranking
        if self.simulation_mode:
            logger.info(f"SIMULATION: Ranking user {user_id} in group {group_id} to role ID {rank_id}")
            
            # Find the username for this user ID
            username = None
            for name, data in self.simulated_users.items():
                if data.get("id") == user_id:
                    username = name
                    break
            
            # If user doesn't exist in simulation, create a new user entry
            if not username:
                username = f"SimUser{user_id}"
                self.simulated_users[username] = {
                    "id": user_id,
                    "name": username,
                    "displayName": username,
                    "groups": []
                }
            
            # Get the user's data
            user_data = self.simulated_users[username]
            
            # Find the specified group in user's groups
            group_found = False
            groups = user_data.get("groups", [])
            
            # Get the role info from simulated roles
            roles = self.simulated_roles.get("default", [])
            role_info = None
            
            for role in roles:
                if role["id"] == int(rank_id):
                    role_info = role
                    break
            
            if not role_info:
                logger.error(f"SIMULATION: Role ID {rank_id} not found in simulated roles")
                return False
            
            # Update the user's group role or add them to the group
            for i, group in enumerate(groups):
                if str(group["group"]["id"]) == str(group_id):
                    groups[i]["role"] = role_info
                    group_found = True
                    break
            
            # If user is not in this group yet, add them
            if not group_found:
                groups.append({
                    "group": {
                        "id": int(group_id),
                        "name": f"Simulated Group {group_id}",
                        "memberCount": 42
                    },
                    "role": role_info
                })
            
            # Update the user data
            user_data["groups"] = groups
            self.simulated_users[username] = user_data
            
            logger.info(f"SIMULATION: Successfully ranked user {user_id} to role {rank_id} ({role_info['name']}) in group {group_id}")
            return True
            
        # If not in simulation mode, use real API with fallback methods
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
        # If in simulation mode, return simulated roles
        if self.simulation_mode:
            logger.info(f"SIMULATION: Getting roles for group {group_id}")
            
            # Return our simulated roles for all group IDs
            roles = self.simulated_roles.get("default", [])
            return roles
            
        # If not in simulation mode, use the real API
        url = f"{self.groups_base_url}/v1/groups/{group_id}/roles"
        
        response = await self.make_request(url)
        
        if response and "roles" in response:
            return response["roles"]
        
        return []
        
    async def get_authenticated_user(self, token):
        """Get information about the authenticated user from token"""
        # If in simulation mode, return simulated authenticated user
        if self.simulation_mode:
            logger.info(f"SIMULATION: Validating Roblox token")
            
            # Extract the first 8 characters of the token to simulate a consistent user
            # This allows different tokens to simulate different users
            sim_user_id = 0
            sim_username = "RankerCBA"  # Default username if token is empty
            
            if token:
                # Clean up token if it includes the full cookie format
                if token.startswith(".ROBLOSECURITY="):
                    token = token.replace(".ROBLOSECURITY=", "")
                token = token.strip().strip('"\'')
                
                # Use the first few characters to determine a simulated user ID
                from hashlib import md5
                hash_obj = md5(token[:8].encode() if len(token) >= 8 else token.encode())
                sim_user_id = int(hash_obj.hexdigest(), 16) % 10000000000
                sim_username = f"SimUser{sim_user_id}"
            
            # Create a simulated authenticated user response
            logger.info(f"SIMULATION: Successfully authenticated as Roblox user: {sim_username}")
            return {
                "id": sim_user_id,
                "name": sim_username,
                "displayName": sim_username
            }
            
        # If not in simulation mode, use the real API
        # Clean up token if it includes the full cookie format
        if token.startswith(".ROBLOSECURITY="):
            token = token.replace(".ROBLOSECURITY=", "")
        
        # Remove any extra spaces or quotes
        token = token.strip().strip('"\'')
        
        # Use our more robust make_request method
        url = "https://users.roblox.com/v1/users/authenticated"
        
        # Try multiple endpoints in case one fails
        alternative_urls = [
            "https://www.roblox.com/my/profile/json",  # Alternative endpoint
            "https://accountinformation.roblox.com/v1/description", # Another alternative
        ]
        
        # First try main endpoint
        user_data = await self.make_request(url, headers=None, token=token)
        
        if user_data and 'name' in user_data:
            logger.info(f"Successfully authenticated as Roblox user: {user_data.get('name', 'Unknown')}")
            return user_data
            
        # Try alternative endpoints if the first one fails
        for alt_url in alternative_urls:
            logger.info(f"Trying alternative authentication endpoint: {alt_url}")
            alt_data = await self.make_request(alt_url, headers=None, token=token)
            
            # Format user data from response depending on which endpoint worked
            if alt_data:
                if 'Username' in alt_data:  # /my/profile/json format
                    # Convert to the same format as the primary endpoint
                    user_data = {
                        "name": alt_data.get("Username"),
                        "id": alt_data.get("UserId"),
                        "displayName": alt_data.get("DisplayName", alt_data.get("Username"))
                    }
                    logger.info(f"Successfully authenticated via alternative endpoint as: {user_data['name']}")
                    return user_data
                    
                elif 'description' in alt_data:  # accountinformation endpoint
                    # We need to make another request to get the user info
                    me_data = await self.make_request("https://users.roblox.com/v1/users/authenticated", 
                                                    headers=None, token=token)
                    if me_data and 'name' in me_data:
                        logger.info(f"Successfully authenticated via secondary attempt as: {me_data['name']}")
                        return me_data
        
        # If all attempts failed, log the error and return None
        logger.error("Failed to authenticate with Roblox API after multiple attempts")
        return None
