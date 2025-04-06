from datetime import datetime
from app import db


class Guild(db.Model):
    """Model for Discord server (guild) configurations"""
    id = db.Column(db.BigInteger, primary_key=True)  # Discord Guild ID
    group_id = db.Column(db.String(20), nullable=True)  # Roblox Group ID
    anti_raid = db.Column(db.Boolean, default=False)
    logs_channel_id = db.Column(db.BigInteger, nullable=True)
    ticket_category_id = db.Column(db.BigInteger, nullable=True)
    ticket_logs_channel_id = db.Column(db.BigInteger, nullable=True)
    verified_role_id = db.Column(db.BigInteger, nullable=True)
    mod_role_id = db.Column(db.BigInteger, nullable=True)
    admin_role_id = db.Column(db.BigInteger, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RobloxVerification(db.Model):
    """Model for storing Discord to Roblox user verification"""
    id = db.Column(db.Integer, primary_key=True)
    discord_id = db.Column(db.BigInteger, unique=True, nullable=False)  # Discord User ID
    roblox_id = db.Column(db.BigInteger, nullable=False)  # Roblox User ID
    roblox_username = db.Column(db.String(50), nullable=False)  # Roblox Username
    verified_at = db.Column(db.DateTime, default=datetime.utcnow)


class VerificationCode(db.Model):
    """Model for temporary verification codes"""
    id = db.Column(db.Integer, primary_key=True)
    discord_id = db.Column(db.BigInteger, unique=True, nullable=False)  # Discord User ID
    roblox_username = db.Column(db.String(50), nullable=False)  # Roblox Username
    code = db.Column(db.String(10), nullable=False)  # Verification Code
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BlacklistedGroup(db.Model):
    """Model for blacklisted Roblox groups"""
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.BigInteger, nullable=False)  # Discord Guild ID
    group_id = db.Column(db.String(20), nullable=False)  # Roblox Group ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('guild_id', 'group_id', name='unique_blacklisted_group'),)


class Ticket(db.Model):
    """Model for support tickets"""
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.BigInteger, nullable=False)  # Discord Guild ID
    channel_id = db.Column(db.BigInteger, nullable=False)  # Discord Channel ID
    creator_id = db.Column(db.BigInteger, nullable=False)  # Discord User ID of creator
    ticket_number = db.Column(db.Integer, nullable=False)  # Ticket number
    status = db.Column(db.String(20), default="open")  # open, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)


class RobloxToken(db.Model):
    """Model for storing encrypted Roblox API tokens for ranking"""
    id = db.Column(db.Integer, primary_key=True)
    discord_id = db.Column(db.BigInteger, unique=True, nullable=False)  # Discord User ID
    encrypted_token = db.Column(db.Text, nullable=False)  # Encrypted Roblox token
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ModerationLog(db.Model):
    """Model for storing moderation action logs"""
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.BigInteger, nullable=False)  # Discord Guild ID
    target_id = db.Column(db.BigInteger, nullable=False)  # Target Discord User ID
    moderator_id = db.Column(db.BigInteger, nullable=False)  # Moderator Discord User ID
    action = db.Column(db.String(20), nullable=False)  # ban, kick, timeout, etc.
    reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)