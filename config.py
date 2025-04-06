import os
import json
from pathlib import Path
import logging
from app import db, app
from datetime import datetime

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        # For backward compatibility, keep track of the old paths
        self.data_directory = Path("data")
        self.verification_codes = {}  # Keep in memory for now
        
        # Create data directory if it doesn't exist (for compatibility)
        self.data_directory.mkdir(exist_ok=True)
        
    def get_server_config(self, guild_id):
        """Get configuration for a specific server"""
        from models import Guild
        
        # Convert to int if it's a string
        if isinstance(guild_id, str):
            guild_id = int(guild_id)
            
        # Use Flask application context for database operations
        with app.app_context():
            # Check if guild exists in database
            guild = Guild.query.get(guild_id)
            
            # If not, create a new entry
            if not guild:
                guild = Guild(id=guild_id)
                db.session.add(guild)
                db.session.commit()
                logger.info(f"Created new guild configuration for {guild_id}")
            
            # Convert DB model to dict for compatibility
            config = {
                "group_id": guild.group_id,
                "verified_role": guild.verified_role_id,
                "mod_role": guild.mod_role_id,
                "admin_role": guild.admin_role_id,
                "anti_raid": guild.anti_raid,
                "logs_channel": guild.logs_channel_id,
                "ticket_category": guild.ticket_category_id,
                "ticket_logs_channel": guild.ticket_logs_channel_id
            }
            
            # Load blacklisted groups
            from models import BlacklistedGroup
            blacklisted_groups = BlacklistedGroup.query.filter_by(guild_id=guild_id).all()
            config["blacklisted_groups"] = [group.group_id for group in blacklisted_groups]
            
            return config
    
    def update_server_config(self, guild_id, key, value):
        """Update a specific configuration value for a server"""
        from models import Guild, BlacklistedGroup, RobloxToken
        
        # Convert to int if it's a string
        if isinstance(guild_id, str):
            guild_id = int(guild_id)
        
        # Special case for Roblox token
        if key == "roblox_token":
            with app.app_context():
                # Handle token through RobloxToken model
                discord_id = guild_id  # In this case, the guild_id is the Discord user ID
                
                existing_token = RobloxToken.query.filter_by(discord_id=discord_id).first()
                if existing_token:
                    existing_token.encrypted_token = value
                    existing_token.updated_at = datetime.utcnow()
                else:
                    new_token = RobloxToken(discord_id=discord_id, encrypted_token=value)
                    db.session.add(new_token)
                
                db.session.commit()
                logger.info(f"Updated Roblox token for user {discord_id}")
                return
            
        # Use Flask application context for database operations
        with app.app_context():
            # Handle special case for blacklisted groups
            if key == "blacklisted_groups":
                # First delete all existing blacklisted groups
                BlacklistedGroup.query.filter_by(guild_id=guild_id).delete()
                
                # Then add the new ones
                for group_id in value:
                    blacklisted_group = BlacklistedGroup(
                        guild_id=guild_id,
                        group_id=group_id
                    )
                    db.session.add(blacklisted_group)
                
                db.session.commit()
                logger.info(f"Updated blacklisted groups for guild {guild_id}")
                return
            
            # Otherwise update the guild config
            guild = Guild.query.get(guild_id)
            if not guild:
                guild = Guild(id=guild_id)
                db.session.add(guild)
            
            # Map the key to the actual column name
            column_mapping = {
                "group_id": "group_id",
                "verified_role": "verified_role_id",
                "mod_role": "mod_role_id",
                "admin_role": "admin_role_id",
                "anti_raid": "anti_raid",
                "logs_channel": "logs_channel_id",
                "ticket_category": "ticket_category_id",
                "ticket_logs_channel": "ticket_logs_channel_id"
            }
            
            # Update the appropriate column
            if key in column_mapping:
                setattr(guild, column_mapping[key], value)
                db.session.commit()
                logger.info(f"Updated {key} for guild {guild_id}")
            else:
                logger.warning(f"Unknown config key: {key}")
    
    def get_next_ticket_number(self, guild_id):
        """Get the next ticket number for a server"""
        from models import Ticket
        
        # Convert to int if it's a string
        if isinstance(guild_id, str):
            guild_id = int(guild_id)
        
        # Use Flask application context for database operations
        with app.app_context():
            # Get the highest ticket number for this guild
            highest_ticket = Ticket.query.filter_by(guild_id=guild_id).order_by(
                Ticket.ticket_number.desc()
            ).first()
            
            next_number = 1
            if highest_ticket:
                next_number = highest_ticket.ticket_number + 1
                
            return next_number
    
    def add_verification_code(self, user_id, code, roblox_username):
        """Store a verification code for a user"""
        from models import VerificationCode
        
        # Convert to int if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
        
        # Use Flask application context for database operations
        with app.app_context():
            # Check if code already exists
            existing_code = VerificationCode.query.filter_by(discord_id=user_id).first()
            if existing_code:
                existing_code.code = code
                existing_code.roblox_username = roblox_username
                existing_code.created_at = datetime.utcnow()
            else:
                new_code = VerificationCode(
                    discord_id=user_id,
                    code=code,
                    roblox_username=roblox_username
                )
                db.session.add(new_code)
            
            db.session.commit()
            logger.info(f"Added verification code for user {user_id}")
        
        # Also store in memory for quicker access
        self.verification_codes[str(user_id)] = {
            "code": code,
            "roblox_username": roblox_username
        }
    
    def get_verification_code(self, user_id):
        """Get the verification code for a user"""
        # First try to get from memory cache
        if str(user_id) in self.verification_codes:
            return self.verification_codes[str(user_id)]
        
        # Otherwise get from database
        from models import VerificationCode
        
        # Convert to int if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
        
        # Use Flask application context for database operations
        with app.app_context():
            code_entry = VerificationCode.query.filter_by(discord_id=user_id).first()
            if code_entry:
                code_data = {
                    "code": code_entry.code,
                    "roblox_username": code_entry.roblox_username
                }
                # Update memory cache
                self.verification_codes[str(user_id)] = code_data
                return code_data
            
            return None
    
    def remove_verification_code(self, user_id):
        """Remove the verification code for a user"""
        from models import VerificationCode
        
        # Remove from memory cache
        if str(user_id) in self.verification_codes:
            del self.verification_codes[str(user_id)]
        
        # Use Flask application context for database operations
        with app.app_context():
            # Remove from database
            if isinstance(user_id, str):
                user_id = int(user_id)
                
            VerificationCode.query.filter_by(discord_id=user_id).delete()
            db.session.commit()
            logger.info(f"Removed verification code for user {user_id}")
