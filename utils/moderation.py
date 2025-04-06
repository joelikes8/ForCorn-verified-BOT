import discord
import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ModerationSystem:
    def __init__(self, bot):
        self.bot = bot
        self.recent_joins = {}  # guild_id: {timestamp: count}
        self.recent_messages = {}  # guild_id: {user_id: {timestamp: count}}
        self.recent_actions = {}  # guild_id: {user_id: {action: timestamp}}
        self.raid_detection_enabled = {}  # guild_id: bool
        
    async def log_action(self, guild, moderator, action, target, reason=None):
        """Log a moderation action to a logging channel if configured"""
        server_config = self.bot.config.get_server_config(guild.id)
        log_channel_id = server_config.get("log_channel")
        
        if not log_channel_id:
            return
        
        log_channel = guild.get_channel(int(log_channel_id))
        if not log_channel:
            return
        
        embed = discord.Embed(
            title=f"{action} Action",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Target", value=f"{target} (ID: {target.id})")
        embed.add_field(name="Moderator", value=f"{moderator} (ID: {moderator.id})")
        
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        
        embed.set_footer(text=f"Action ID: {discord.utils.utcnow().timestamp()}")
        
        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to log moderation action: {e}")
    
    async def check_permissions(self, member, target):
        """Check if a member has permission to moderate a target"""
        # Cannot moderate yourself
        if member.id == target.id:
            return False, "You cannot moderate yourself."
        
        # Cannot moderate higher roles
        if member.top_role <= target.top_role:
            return False, "You cannot moderate a member with higher or equal roles."
        
        # Cannot moderate the server owner
        if target.id == target.guild.owner_id:
            return False, "You cannot moderate the server owner."
        
        return True, None
    
    async def kick_member(self, guild, moderator, target, reason=None):
        """Kick a member from the server"""
        # Check permissions
        can_moderate, error = await self.check_permissions(moderator, target)
        if not can_moderate:
            return False, error
        
        try:
            await target.kick(reason=f"Kicked by {moderator}: {reason}")
            await self.log_action(guild, moderator, "Kick", target, reason)
            return True, f"Successfully kicked {target.display_name}."
        except discord.Forbidden:
            return False, "I don't have permission to kick that member."
        except Exception as e:
            logger.error(f"Error kicking member: {e}")
            return False, "An error occurred while trying to kick the member."
    
    async def ban_member(self, guild, moderator, target, reason=None, delete_days=1):
        """Ban a member from the server"""
        # Check permissions
        can_moderate, error = await self.check_permissions(moderator, target)
        if not can_moderate:
            return False, error
        
        try:
            await guild.ban(target, reason=f"Banned by {moderator}: {reason}", delete_message_days=delete_days)
            await self.log_action(guild, moderator, "Ban", target, reason)
            return True, f"Successfully banned {target.display_name}."
        except discord.Forbidden:
            return False, "I don't have permission to ban that member."
        except Exception as e:
            logger.error(f"Error banning member: {e}")
            return False, "An error occurred while trying to ban the member."
    
    async def timeout_member(self, guild, moderator, target, duration, reason=None):
        """Timeout a member"""
        # Check permissions
        can_moderate, error = await self.check_permissions(moderator, target)
        if not can_moderate:
            return False, error
        
        try:
            # Convert duration to timedelta
            duration_seconds = duration * 60  # minutes to seconds
            until = discord.utils.utcnow() + timedelta(seconds=duration_seconds)
            
            await target.timeout(until, reason=f"Timed out by {moderator}: {reason}")
            await self.log_action(guild, moderator, "Timeout", target, f"{reason} (Duration: {duration} minutes)")
            return True, f"Successfully timed out {target.display_name} for {duration} minutes."
        except discord.Forbidden:
            return False, "I don't have permission to timeout that member."
        except Exception as e:
            logger.error(f"Error timing out member: {e}")
            return False, "An error occurred while trying to timeout the member."
    
    async def setup_anti_raid(self, guild):
        """Setup anti-raid protection for a guild"""
        self.raid_detection_enabled[guild.id] = True
        return True, "Anti-raid protection has been enabled for this server."
    
    async def disable_anti_raid(self, guild):
        """Disable anti-raid protection for a guild"""
        self.raid_detection_enabled[guild.id] = False
        return True, "Anti-raid protection has been disabled for this server."
    
    async def on_member_join(self, member):
        """Handle member join events for raid detection"""
        guild = member.guild
        
        # Skip if raid detection is not enabled
        if not self.raid_detection_enabled.get(guild.id, False):
            return
        
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Initialize if needed
        if guild.id not in self.recent_joins:
            self.recent_joins[guild.id] = {}
        
        # Clean old data
        self.recent_joins[guild.id] = {ts: count for ts, count in self.recent_joins[guild.id].items() 
                                       if ts > minute_ago.timestamp()}
        
        # Add current join
        current_ts = now.timestamp()
        self.recent_joins[guild.id][current_ts] = self.recent_joins[guild.id].get(current_ts, 0) + 1
        
        # Count recent joins
        recent_join_count = sum(self.recent_joins[guild.id].values())
        
        # If more than 10 joins in a minute, potential raid
        if recent_join_count > 10:
            logger.warning(f"Potential raid detected in {guild.name}: {recent_join_count} joins in the last minute")
            
            # Get server config for logging channel
            server_config = self.bot.config.get_server_config(guild.id)
            log_channel_id = server_config.get("log_channel")
            
            if log_channel_id:
                log_channel = guild.get_channel(int(log_channel_id))
                if log_channel:
                    embed = discord.Embed(
                        title="⚠️ Potential Raid Detected",
                        description=f"Detected {recent_join_count} members joining in the last minute.",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Latest Join", value=f"{member.mention} ({member.id})")
                    embed.set_footer(text="Consider enabling verification or locking down channels.")
                    
                    await log_channel.send(embed=embed)
    
    async def on_message(self, message):
        """Handle message events for spam detection"""
        # Skip if not in a guild or if author is a bot
        if not message.guild or message.author.bot:
            return
        
        guild = message.guild
        author = message.author
        
        # Skip if raid detection is not enabled
        if not self.raid_detection_enabled.get(guild.id, False):
            return
        
        now = datetime.now()
        ten_seconds_ago = now - timedelta(seconds=10)
        
        # Initialize if needed
        if guild.id not in self.recent_messages:
            self.recent_messages[guild.id] = {}
        
        if author.id not in self.recent_messages[guild.id]:
            self.recent_messages[guild.id][author.id] = {}
        
        # Clean old data
        self.recent_messages[guild.id][author.id] = {
            ts: count for ts, count in self.recent_messages[guild.id][author.id].items() 
            if ts > ten_seconds_ago.timestamp()
        }
        
        # Add current message
        current_ts = now.timestamp()
        self.recent_messages[guild.id][author.id][current_ts] = self.recent_messages[guild.id][author.id].get(current_ts, 0) + 1
        
        # Count recent messages
        recent_message_count = sum(self.recent_messages[guild.id][author.id].values())
        
        # If more than 5 messages in 10 seconds, warn for spam
        if recent_message_count > 5:
            logger.warning(f"Potential spam detected from {author.name} in {guild.name}: {recent_message_count} messages in 10 seconds")
            
            # Track this action to avoid duplicate warnings
            if guild.id not in self.recent_actions:
                self.recent_actions[guild.id] = {}
            
            if author.id not in self.recent_actions[guild.id]:
                self.recent_actions[guild.id][author.id] = {}
            
            # Check if we've warned this user recently
            last_warn = self.recent_actions[guild.id][author.id].get("spam_warn", 0)
            if now.timestamp() - last_warn > 60:  # Only warn once per minute
                self.recent_actions[guild.id][author.id]["spam_warn"] = now.timestamp()
                
                try:
                    await message.channel.send(
                        f"{author.mention} Please slow down! You're sending messages too quickly.",
                        delete_after=10
                    )
                except Exception as e:
                    logger.error(f"Failed to send spam warning: {e}")
