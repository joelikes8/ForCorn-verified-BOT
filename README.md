# ForCorn Discord Bot

A comprehensive Discord bot for Roblox group management, providing advanced authentication, ranking, and server moderation tools with robust API integration and user-friendly nickname standardization.

## Features

- **Roblox Authentication**: Verify Discord users with their Roblox accounts
- **Group Management**: Set up Roblox group ID and manage group ranks directly from Discord
- **Moderation Tools**: Kick, ban, and timeout members with ease
- **Anti-Raid Protection**: Advanced protection against server raids
- **Ticket System**: Support ticket management for user assistance
- **Blacklist System**: Maintain a list of blacklisted Roblox groups

## Setup Instructions

1. Clone this repository
2. Install dependencies with pip
3. Set up environment variables:
   - DISCORD_TOKEN: Your Discord bot token
   - DATABASE_URL: Database connection URL
4. Run the bot: python main.py

## Commands

- /verify <roblox_username>: Verify Roblox account with Discord
- /setupid <group_id>: Set up Roblox group ID for the server
- /setuptoken <token>: Set up Roblox API token for ranking (DM only)
- /rank <roblox_username> [rank_name]: Rank a user in the Roblox group
- /kick <member> [reason]: Kick a member from the server
- /ban <member> [reason] [delete_days]: Ban a member from the server
- /timeout <member> <duration> [reason]: Timeout a member
- /antiraid <action>: Toggle anti-raid protection
- /ticket: Create a support ticket
- /sendticket <channel>: Send the ticket panel to a channel
- /closeticket: Close a ticket channel
- /update: Update nickname with current Roblox group rank

## Web Interface

The bot also includes a basic web interface for status monitoring accessible at port 5000.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
