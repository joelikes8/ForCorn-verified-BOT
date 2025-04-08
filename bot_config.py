import os
import json
from pathlib import Path
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class BotConfig:
    """
    A simplified config class for the Discord bot that doesn't depend on Flask.
    This class uses JSON files for storage instead of a database to avoid Flask dependencies.
    """
    def __init__(self):
        # Create data directory
        self.data_directory = Path("data")
        self.data_directory.mkdir(exist_ok=True)
        
        # File paths for various configuration data
        self.server_configs_file = self.data_directory / "server_configs.json"
        self.verification_codes_file = self.data_directory / "verification_codes.json"
        self.blacklisted_groups_file = self.data_directory / "blacklisted_groups.json"
        self.tickets_counter_file = self.data_directory / "tickets_counter.json"
        
        # Load data from files or create empty defaults
        self.server_configs = self._load_or_create(self.server_configs_file, {})
        self.verification_codes = self._load_or_create(self.verification_codes_file, {})
        self.blacklisted_groups = self._load_or_create(self.blacklisted_groups_file, {})
        self.tickets_counter = self._load_or_create(self.tickets_counter_file, {})
        
    def _load_or_create(self, file_path, default_data):
        """Helper method to load JSON data from a file or create with defaults"""
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse {file_path}. Creating new file.")
                with open(file_path, 'w') as f:
                    json.dump(default_data, f, indent=2)
                return default_data
        else:
            with open(file_path, 'w') as f:
                json.dump(default_data, f, indent=2)
            return default_data
            
    def _save_to_file(self, file_path, data):
        """Helper method to save data to a JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
    def get_server_config(self, guild_id):
        """Get configuration for a specific server"""
        str_guild_id = str(guild_id)
        
        # Create default config if it doesn't exist
        if str_guild_id not in self.server_configs:
            self.server_configs[str_guild_id] = {
                "group_id": None,
                "verified_role": None,
                "mod_role": None,
                "admin_role": None,
                "anti_raid": False,
                "logs_channel": None,
                "ticket_category": None,
                "ticket_logs_channel": None,
                "blacklisted_groups": []
            }
            self._save_to_file(self.server_configs_file, self.server_configs)
            
        return self.server_configs[str_guild_id]
    
    def update_server_config(self, guild_id, key, value):
        """Update a specific configuration value for a server"""
        str_guild_id = str(guild_id)
        
        # Special case for Roblox token
        if key == "roblox_token":
            if "roblox_tokens" not in self.server_configs:
                self.server_configs["roblox_tokens"] = {}
            
            self.server_configs["roblox_tokens"][str_guild_id] = {
                "token": value,
                "updated_at": datetime.utcnow().isoformat()
            }
            self._save_to_file(self.server_configs_file, self.server_configs)
            logger.info(f"Updated Roblox token for user {guild_id}")
            return
        
        # Handle special case for blacklisted groups
        if key == "blacklisted_groups":
            # Make sure server config exists
            if str_guild_id not in self.server_configs:
                self.get_server_config(guild_id)
            
            # Update blacklisted groups
            self.server_configs[str_guild_id]["blacklisted_groups"] = value
            self._save_to_file(self.server_configs_file, self.server_configs)
            logger.info(f"Updated blacklisted groups for guild {guild_id}")
            return
        
        # Otherwise update the guild config
        if str_guild_id not in self.server_configs:
            self.get_server_config(guild_id)
        
        # Update the value if the key is valid
        if key in self.server_configs[str_guild_id]:
            self.server_configs[str_guild_id][key] = value
            self._save_to_file(self.server_configs_file, self.server_configs)
            logger.info(f"Updated {key} for guild {guild_id}")
        else:
            logger.warning(f"Unknown config key: {key}")
    
    def get_next_ticket_number(self, guild_id):
        """Get the next ticket number for a server"""
        str_guild_id = str(guild_id)
        
        # Initialize counter if it doesn't exist
        if str_guild_id not in self.tickets_counter:
            self.tickets_counter[str_guild_id] = 0
        
        # Increment the counter and save
        self.tickets_counter[str_guild_id] += 1
        self._save_to_file(self.tickets_counter_file, self.tickets_counter)
        
        return self.tickets_counter[str_guild_id]
    
    def add_verification_code(self, user_id, code, roblox_username):
        """Store a verification code for a user"""
        str_user_id = str(user_id)
        
        # Add the verification code
        self.verification_codes[str_user_id] = {
            "code": code,
            "roblox_username": roblox_username,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Save to file
        self._save_to_file(self.verification_codes_file, self.verification_codes)
        logger.info(f"Added verification code for user {user_id}")
    
    def get_verification_code(self, user_id):
        """Get the verification code for a user"""
        str_user_id = str(user_id)
        
        if str_user_id in self.verification_codes:
            return {
                "code": self.verification_codes[str_user_id]["code"],
                "roblox_username": self.verification_codes[str_user_id]["roblox_username"]
            }
        
        return None
    
    def remove_verification_code(self, user_id):
        """Remove the verification code for a user"""
        str_user_id = str(user_id)
        
        if str_user_id in self.verification_codes:
            del self.verification_codes[str_user_id]
            self._save_to_file(self.verification_codes_file, self.verification_codes)
            logger.info(f"Removed verification code for user {user_id}")