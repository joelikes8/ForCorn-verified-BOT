import random
import string
import discord
import logging
from discord import Embed, Color
import aiohttp
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# List of verification GIF URLs
VERIFICATION_GIFS = [
    "https://c.tenor.com/y1SeYAd2Wh4AAAAC/robot-verification.gif",
    "https://c.tenor.com/yNKjZ6OkfEUAAAAd/security-check.gif",
    "https://c.tenor.com/n8UHAHrHm3AAAAAC/captcha-robot.gif",
    "https://c.tenor.com/QlG9HBfigDkAAAAC/discord-verification.gif",
    "https://c.tenor.com/BDyYKJt9qNAAAAAC/verification-verify.gif"
]

class VerificationSystem:
    def __init__(self, bot, roblox_api, config):
        self.bot = bot
        self.roblox_api = roblox_api
        self.config = config
        # Mapping of rank names to standardized codes
        self.rank_codes = {
            # Military ranks (general structure)
            "Owner": "OWN",
            "Co-Owner": "COWN",
            "President": "PRES",
            "Vice President": "VPRES",
            "Commander in Chief": "CIC",
            "Commander": "CMD",
            "Chief of Defence Staff": "CDS",
            "Chief of Staff": "COS",
            "Executive Officer": "XO",
            "Director": "DIR",
            "General": "GEN",
            "Lieutenant General": "LTGEN",
            "Major General": "MJGEN",
            "Brigadier General": "BGEN",
            "Colonel": "COL",
            "Lieutenant Colonel": "LTCOL",
            "Major": "MAJ",
            "Captain": "CAPT",
            "Lieutenant": "LT",
            "Second Lieutenant": "2LT",
            "Officer Cadet": "OCDT",
            "Warrant Officer": "WO",
            "Staff Sergeant": "SSGT",
            "Sergeant": "SGT",
            "Corporal": "CPL",
            "Lance Corporal": "LCPL",
            "Private First Class": "PFC",
            "Private": "PVT",
            "Recruit": "RCT",
            # Admin ranks
            "Administrator": "ADMN",
            "Moderator": "MOD",
            "Trial Moderator": "TMOD",
            "Developer": "DEV",
            "Builder": "BLDR",
            # Default fallback for any other ranks
            "Member": "MBR"
        }
        
        # Keep track of verified users in memory
        self.verified_users = {}
        self._load_verified_users()
    
    def _load_verified_users(self):
        """Load verified users from a JSON file if it exists"""
        try:
            with open("data/verified_users.json", "r") as f:
                self.verified_users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If the file doesn't exist or is not valid JSON, use an empty dict
            self.verified_users = {}
    
    def _save_verified_users(self):
        """Save verified users to a JSON file"""
        with open("data/verified_users.json", "w") as f:
            json.dump(self.verified_users, f, indent=2)
    
    def get_rank_code(self, rank_name):
        """Convert a rank name to a standardized code"""
        if not rank_name:
            return None
            
        # Check for exact match first
        if rank_name in self.rank_codes:
            return self.rank_codes[rank_name]
        
        # Check for partial matches
        for known_rank, code in self.rank_codes.items():
            if known_rank.lower() in rank_name.lower() or rank_name.lower() in known_rank.lower():
                return code
        
        # If no match found, use first 3-4 characters of the rank name as a code
        if len(rank_name) >= 4:
            return rank_name[:4].upper()
        else:
            return rank_name.upper()
    
    def generate_verification_code(self, length=6):
        """Generate a random verification code"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    def get_random_verification_gif(self):
        """Get a random verification GIF URL"""
        return random.choice(VERIFICATION_GIFS)
    
    async def create_verification_embed(self, roblox_username, code):
        """Create an embed for verification"""
        embed = Embed(
            title="Roblox Verification",
            description="Please verify your Roblox account by following these steps:",
            color=Color.blue()
        )
        
        # Add steps
        embed.add_field(
            name="Step 1",
            value=f"Go to your Roblox profile: https://www.roblox.com/users/profile",
            inline=False
        )
        embed.add_field(
            name="Step 2", 
            value="Add the following code to your 'About Me' section:",
            inline=False
        )
        embed.add_field(
            name="Verification Code", 
            value=f"```{code}```",
            inline=False
        )
        embed.add_field(
            name="Step 3",
            value="Click the 'Verify' button below to complete verification.",
            inline=False
        )
        
        # Add footer and random GIF
        embed.set_footer(text="This verification helps us connect your Discord account to your Roblox account.")
        embed.set_image(url=self.get_random_verification_gif())
        
        return embed
    
    async def verify_user(self, member, roblox_username, code):
        """Check if the verification code is in the user's Roblox profile"""
        try:
            # Get user info and check if the code is in their profile
            user_id = await self.roblox_api.get_user_id_from_username(roblox_username)
            if not user_id:
                return False, "Could not find that Roblox username."
            
            # Get the user's profile description
            description = await self.roblox_api.get_user_description(user_id)
            
            if code in description:
                # Store the verification in memory and in the JSON file
                str_discord_id = str(member.id)
                self.verified_users[str_discord_id] = {
                    "roblox_id": user_id,
                    "roblox_username": roblox_username,
                    "verified_at": datetime.utcnow().isoformat()
                }
                
                # Save to file
                self._save_verified_users()
                
                logger.info(f"User {member.id} verified as Roblox user {roblox_username} (ID: {user_id})")
                return True, user_id
            else:
                return False, "Verification code not found in your profile. Please make sure you added it correctly."
        
        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            return False, "An error occurred while verifying your account. Please try again later."
    
    async def update_nickname(self, member, roblox_username=None, group_id=None):
        """Update the nickname of a member based on their Roblox info"""
        try:
            # Get the Roblox user ID from our records if verified
            user_id = None
            str_discord_id = str(member.id)
            
            if str_discord_id in self.verified_users:
                user_id = self.verified_users[str_discord_id]["roblox_id"]
                roblox_username = self.verified_users[str_discord_id]["roblox_username"]
            
            # If not found in our records, try to get from API
            if not user_id and roblox_username:
                user_id = await self.roblox_api.get_user_id_from_username(roblox_username)
                if not user_id:
                    return False, "Could not find that Roblox username."
            
            # If we still don't have a user ID or username, we can't proceed
            if not user_id or not roblox_username:
                return False, "You must be verified first. Use /verify to verify your Roblox account."
            
            # Default format without group rank
            new_nickname = f"{roblox_username}"
            rank_name = None
            
            # If group_id is provided, get the user's rank
            if group_id:
                # Get group rank
                rank_name = await self.roblox_api.get_user_group_rank(user_id, group_id)
                if rank_name:
                    # Convert rank name to standardized code
                    rank_code = self.get_rank_code(rank_name)
                    new_nickname = f"[{rank_code}] {roblox_username}"
            
            # Discord has a 32 character nickname limit
            if len(new_nickname) > 32:
                # Truncate the username to fit within the limit
                rank_code = self.get_rank_code(rank_name) if rank_name else None
                code_length = len(rank_code) + 3 if rank_code else 0  # 3 for [ ]
                
                max_username_length = 32 - code_length
                truncated_username = roblox_username[:max_username_length]
                
                if rank_code:
                    new_nickname = f"[{rank_code}] {truncated_username}"
                else:
                    new_nickname = truncated_username
                
                logger.info(f"Nickname truncated from '{roblox_username}' to '{truncated_username}' due to Discord's 32 character limit")
            
            # Update the nickname
            try:
                await member.edit(nick=new_nickname)
                return True, new_nickname
            except discord.Forbidden:
                return False, "I don't have permission to change the nickname."
            
        except Exception as e:
            logger.error(f"Error updating nickname: {e}")
            return False, "An error occurred while updating your nickname."