# ForCorn Discord Bot Command Guide

This guide provides detailed information about all 20 commands available in the ForCorn Discord bot.

## General Commands

### 1. `/ping`
**Description:** Check if the bot is responding and view connection latency.  
**Usage:** `/ping`  
**Example Response:** `Pong! Bot is online with a latency of 42ms`

### 2. `/help`
**Description:** Display a list of all available commands.  
**Usage:** `/help`  
**Example Response:** *Sends an embed with categorized commands and descriptions*

### 3. `/about`
**Description:** Display information about the bot.  
**Usage:** `/about`  
**Example Response:** *Sends an embed with bot version, server count, and feature list*

## Verification Commands

### 4. `/verify <roblox_username>`
**Description:** Verify your Roblox account with your Discord account.  
**Usage:** `/verify JohnDoe123`  
**Parameters:**
- `roblox_username`: Your Roblox username

**Process:**
1. The bot generates a verification code
2. You add this code to your Roblox profile
3. Click the verification button
4. The bot checks your profile and completes verification

### 5. `/update`
**Description:** Update your server nickname to match your Roblox username and rank.  
**Usage:** `/update`  
**Example Response:** `Your nickname has been updated to [Owner] JohnDoe123`

### 6. `/background <roblox_username>`
**Description:** Check if a Roblox user is in any blacklisted groups.  
**Usage:** `/background JohnDoe123`  
**Parameters:**
- `roblox_username`: The Roblox username to check

**Example Response:** `User is not in any blacklisted groups` or `⚠️ User is in blacklisted groups: [Group1, Group2]`

## Ticket Commands

### 7. `/ticket`
**Description:** Create a support ticket.  
**Usage:** `/ticket`  
**Result:** Creates a private channel for support communication

### 8. `/closeticket`
**Description:** Close an active support ticket.  
**Usage:** `/closeticket`  
**Note:** Must be used in an active ticket channel

### 9. `/sendticket [channel]`
**Description:** Send a ticket panel button to a channel.  
**Usage:** `/sendticket #support-tickets`  
**Parameters:**
- `channel`: (Optional) The channel to send the panel to. Defaults to current channel.

**Result:** Sends an embed with a button that users can click to create tickets

## Group Management Commands

### 10. `/rank <roblox_username> [rank_name]`
**Description:** View or change a user's rank in the Roblox group.  
**Usage:** `/rank JohnDoe123 Member`  
**Parameters:**
- `roblox_username`: The Roblox username to rank
- `rank_name`: (Optional) The rank name to give. If omitted, shows current rank.

**Example Response:** `JohnDoe123's rank is now Member` or `JohnDoe123's current rank is Member`

### 11. `/setupid <group_id>`
**Description:** Set up the Roblox group ID for the server.  
**Usage:** `/setupid 12345678`  
**Parameters:**
- `group_id`: The ID of your Roblox group

**Example Response:** `Group ID has been set to 12345678`

### 12. `/ranksetup <group_id>`
**Description:** Set up the Roblox group ID specifically for ranking.  
**Usage:** `/ranksetup 12345678`  
**Parameters:**
- `group_id`: The ID of your Roblox group for ranking

**Example Response:** `Ranking group ID has been set to 12345678`

### 13. `/setuptoken <token>`
**Description:** Set up the Roblox API token for ranking.  
**Usage:** `/setuptoken YOUR_API_TOKEN`  
**Parameters:**
- `token`: Your Roblox API token

**Example Response:** `API token has been set successfully`

## Moderation Commands

### 14. `/kick <member> [reason]`
**Description:** Kick a member from the server.  
**Usage:** `/kick @User Disrupting chat`  
**Parameters:**
- `member`: The Discord member to kick
- `reason`: (Optional) The reason for the kick

**Example Response:** `Kicked @User for reason: Disrupting chat`

### 15. `/ban <member> [reason]`
**Description:** Ban a member from the server.  
**Usage:** `/ban @User Repeated violations`  
**Parameters:**
- `member`: The Discord member to ban
- `reason`: (Optional) The reason for the ban

**Example Response:** `Banned @User for reason: Repeated violations`

### 16. `/timeout <member> <duration> [reason]`
**Description:** Timeout (mute) a member for a specified duration.  
**Usage:** `/timeout @User 1h Spamming`  
**Parameters:**
- `member`: The Discord member to timeout
- `duration`: Duration format like "1h", "30m", "1d" (h=hours, m=minutes, d=days)
- `reason`: (Optional) The reason for the timeout

**Example Response:** `@User has been timed out for 1 hour. Reason: Spamming`

### 17. `/antiraid <action>`
**Description:** Toggle anti-raid protection.  
**Usage:** `/antiraid enable`  
**Parameters:**
- `action`: Either "enable" or "disable"

**Example Response:** `Anti-raid protection has been enabled`

## Server Setup Commands

### 18. `/setup_roles [verified_role] [mod_role] [admin_role]`
**Description:** Set up verification and moderation roles.  
**Usage:** `/setup_roles @Verified @Moderator @Administrator`  
**Parameters:**
- `verified_role`: (Optional) The role given to verified members
- `mod_role`: (Optional) The role with moderation permissions
- `admin_role`: (Optional) The role with admin permissions

**Example Response:** `Roles have been configured successfully`

### 19. `/blacklistedgroups <group_id>`
**Description:** Add a Roblox group to the blacklist.  
**Usage:** `/blacklistedgroups 87654321`  
**Parameters:**
- `group_id`: The ID of the Roblox group to blacklist

**Example Response:** `Added group 87654321 to the blacklist`

### 20. `/removeblacklist <group_id>`
**Description:** Remove a Roblox group from the blacklist.  
**Usage:** `/removeblacklist 87654321`  
**Parameters:**
- `group_id`: The ID of the Roblox group to remove from the blacklist

**Example Response:** `Removed group 87654321 from the blacklist`

## Permissions

Commands are restricted based on role permissions:

- **General Commands (1-3)**: Available to all users
- **Verification Commands (4-6)**: Available to all users
- **Ticket Commands (7-9)**: 
  - Creating tickets: All users
  - Closing tickets: Ticket creator, moderators, admins
  - Sending ticket panel: Moderators, admins
- **Group Management Commands (10-13)**: Administrators only
- **Moderation Commands (14-17)**: Moderators, administrators
- **Server Setup Commands (18-20)**: Administrators only

## Troubleshooting

If commands aren't working:

1. Make sure the bot has the necessary permissions in your server
2. Verify that you have the correct roles to use restricted commands
3. Check if the bot is online (use `/ping`)
4. Try using `/help` to see if commands are properly registered
5. If specific functionality isn't working, ensure you've set up the required configuration (Group IDs, API tokens, etc.)