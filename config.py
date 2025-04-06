import os
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        self.data_directory = Path("data")
        self.server_configs = {}
        self.verification_codes = {}
        self.tickets_counter = {}
        
        # Create data directory if it doesn't exist
        self.data_directory.mkdir(exist_ok=True)
        
        # Load existing configurations if available
        self.server_config_path = self.data_directory / "server_configs.json"
        self.tickets_counter_path = self.data_directory / "tickets_counter.json"
        
        self.load_config()
    
    def load_config(self):
        """Load configuration from files"""
        try:
            if self.server_config_path.exists():
                with open(self.server_config_path, 'r') as f:
                    self.server_configs = json.load(f)
                    logger.info("Loaded server configurations")
            
            if self.tickets_counter_path.exists():
                with open(self.tickets_counter_path, 'r') as f:
                    self.tickets_counter = json.load(f)
                    logger.info("Loaded tickets counter")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    def save_config(self):
        """Save configuration to files"""
        try:
            with open(self.server_config_path, 'w') as f:
                json.dump(self.server_configs, f)
            
            with open(self.tickets_counter_path, 'w') as f:
                json.dump(self.tickets_counter, f)
            
            logger.info("Saved configuration files")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def get_server_config(self, guild_id):
        """Get configuration for a specific server"""
        guild_id = str(guild_id)
        if guild_id not in self.server_configs:
            self.server_configs[guild_id] = {
                "group_id": None,
                "roblox_token": None,
                "blacklisted_groups": [],
                "ticket_channel": None,
                "verification_channel": None,
                "verified_role": None,
                "mod_role": None,
                "admin_role": None
            }
            self.save_config()
        
        return self.server_configs[guild_id]
    
    def update_server_config(self, guild_id, key, value):
        """Update a specific configuration value for a server"""
        guild_id = str(guild_id)
        if guild_id not in self.server_configs:
            self.get_server_config(guild_id)
        
        self.server_configs[guild_id][key] = value
        self.save_config()
    
    def get_next_ticket_number(self, guild_id):
        """Get the next ticket number for a server"""
        guild_id = str(guild_id)
        if guild_id not in self.tickets_counter:
            self.tickets_counter[guild_id] = 0
        
        self.tickets_counter[guild_id] += 1
        self.save_config()
        
        return self.tickets_counter[guild_id]
    
    def add_verification_code(self, user_id, code, roblox_username):
        """Store a verification code for a user"""
        self.verification_codes[str(user_id)] = {
            "code": code,
            "roblox_username": roblox_username
        }
    
    def get_verification_code(self, user_id):
        """Get the verification code for a user"""
        return self.verification_codes.get(str(user_id))
    
    def remove_verification_code(self, user_id):
        """Remove the verification code for a user"""
        if str(user_id) in self.verification_codes:
            del self.verification_codes[str(user_id)]
