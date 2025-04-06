import random
import string
import discord
import logging
from discord import Embed, Color
import aiohttp

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
    def __init__(self, roblox_api):
        self.roblox_api = roblox_api
    
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
            description=f"Please verify your Roblox account by following these steps:",
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
            # Import the database models here to avoid circular imports
            from app import db, app
            from models import RobloxVerification
            
            # Get user info and check if the code is in their profile
            user_id = await self.roblox_api.get_user_id_from_username(roblox_username)
            if not user_id:
                return False, "Could not find that Roblox username."
            
            # Get the user's profile description
            description = await self.roblox_api.get_user_description(user_id)
            
            if code in description:
                # Store the verification in the database - using app context properly
                with app.app_context():
                    # Check if there's already a verification record
                    existing_verification = RobloxVerification.query.filter_by(discord_id=member.id).first()
                    
                    if existing_verification:
                        # Update existing record
                        existing_verification.roblox_id = user_id
                        existing_verification.roblox_username = roblox_username
                    else:
                        # Create new record
                        new_verification = RobloxVerification(
                            discord_id=member.id,
                            roblox_id=user_id,
                            roblox_username=roblox_username
                        )
                        db.session.add(new_verification)
                    
                    db.session.commit()
                
                logger.info(f"User {member.id} verified as Roblox user {roblox_username} (ID: {user_id})")
                return True, user_id
            else:
                return False, "Verification code not found in your profile. Please make sure you added it correctly."
        
        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            return False, "An error occurred while verifying your account. Please try again later."
    
    async def update_nickname(self, member, roblox_username, group_id=None):
        """Update the nickname of a member based on their Roblox info"""
        try:
            # Import the database models here to avoid circular imports
            from app import app
            from models import RobloxVerification
            
            # Get the Roblox user ID from database if verified, else from username
            user_id = None
            with app.app_context():
                verification = RobloxVerification.query.filter_by(discord_id=member.id).first()
                
                if verification:
                    user_id = verification.roblox_id
                    roblox_username = verification.roblox_username
            
            # If not found in database, try to get from API
            if not user_id:
                user_id = await self.roblox_api.get_user_id_from_username(roblox_username)
                if not user_id:
                    return False, "Could not find that Roblox username."
            
            # Default format without group rank
            new_nickname = f"{roblox_username}"
            
            # If group_id is provided, get the user's rank
            if group_id:
                # Get group rank
                rank_name = await self.roblox_api.get_user_group_rank(user_id, group_id)
                if rank_name:
                    new_nickname = f"[{rank_name}] {roblox_username}"
            
            # Update the nickname
            try:
                await member.edit(nick=new_nickname)
                return True, new_nickname
            except discord.Forbidden:
                return False, "I don't have permission to change the nickname."
            
        except Exception as e:
            logger.error(f"Error updating nickname: {e}")
            return False, "An error occurred while updating your nickname."
