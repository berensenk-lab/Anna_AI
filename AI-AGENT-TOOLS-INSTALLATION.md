# AI Agent Tools Installation Guide

## Overview

The AI Agent Tools repository contains optional extensions for Anna AI. These tools add specialized functionality like game integration, chat platforms, vision, and more.

**Location**: `C:\Users\beren\AI_Agent_Tools`

**Available**: Already downloaded ✓

---

## Available Tools (24 Total)

### Chat & Social Integration
- **discord_chat** — Join Discord servers and respond to chat
- **twitch_chat** — Monitor and respond in Twitch streams
- **youtube_chat** — Join YouTube live chat sessions
- **group_chat** — Multi-agent communication system

### Search & Information
- **bing_search** — Search using Bing
- **duckduckgo_search** — Privacy-focused search
- **web_fetch** — Download and parse web pages
- **wiki_search** — Search Wikipedia

### Utilities
- **calculator** — Advanced math calculations
- **dice_roller** — Random dice rolls and generators
- **reminders** — Set reminders and alarms
- **calendar** — Calendar management
- **memory_search** — Search agent memory
- **screenshot_vision** — Analyze screen content

### Gaming
- **minecraft** — Minecraft bot control
- **minecraft_spectator** — Watch Minecraft gameplay
- **league_of_legends** — League of Legends integration
- **game_vision** — Analyze game screens
- **game_guide** — In-game assistance

### Vision & Graphics
- **opencv_vision** — Computer vision analysis
- **warudo** — Warudo avatar control (already integrated)
- **unity_animation** — Unity game animation

### Advanced
- **coding_VS_Code** — Execute code in VS Code
- **mcp_bridge** — Model Context Protocol bridge
- **sound_effects** — Trigger sound effects

---

## Installation Priority

### Tier 1 (Recommended for Everyone)
1. **sound_effects** — Agent can make sounds
2. **discord_chat** — (if you use Discord)
3. **twitch_chat** — (if you stream on Twitch)

### Tier 2 (Nice to Have)
- web_fetch, wiki_search, calculator, reminders
- discord_chat, twitch_chat (if not already)

### Tier 3 (Specialized)
- Game-specific tools (minecraft, league_of_legends)
- Vision tools (opencv_vision, game_vision)

### Tier 4 (Advanced)
- coding_VS_Code, mcp_bridge, unity_animation

---

## How to Install Tools

### Method 1: Automatic Installation (Recommended)

Most tools integrate automatically by copying to Anna AI:

```powershell
cd C:\Users\beren\AI_Agent_Tools

# Copy all tools to Anna AI (this creates the tools structure)
Copy-Item -Path "." -Destination "C:\Users\beren\Anna_AI\BASE\tools\installed" -Recurse -Force
```

This copies all tools at once. Anna AI will auto-discover them.

### Method 2: Manual Installation (Selective)

Copy only the tools you want:

```powershell
cd C:\Users\beren\AI_Agent_Tools

# Copy specific tool
Copy-Item -Path "discord_chat" -Destination "C:\Users\beren\Anna_AI\BASE\tools\installed\discord_chat" -Recurse

# Copy another
Copy-Item -Path "sound_effects" -Destination "C:\Users\beren\Anna_AI\BASE\tools\installed\sound_effects" -Recurse
```

### Verify Installation

```powershell
# Check if tools directory exists
Get-ChildItem "C:\Users\beren\Anna_AI\BASE\tools\installed"

# Should see tool folders
```

---

## Tool-Specific Setup

### Discord Chat

**Prerequisites**:
1. Discord server where you have permissions
2. Discord bot token

**Setup**:
```
1. Go to: https://discord.com/developers/applications
2. Create New Application
3. Go to Bot section → Add Bot
4. Copy token
5. Edit .env:
   DISCORD_BOT_TOKEN=your_token_here
6. Invite bot to server:
   https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot
```

**Enable in controls.py**:
```python
USE_DISCORD = True
```

### Twitch Chat

**Prerequisites**:
1. Twitch account
2. OAuth token

**Setup**:
```
1. Go to: https://twitchapps.com/tmi/
2. Authorize with Twitch
3. Copy the OAuth token
4. Edit .env:
   TWITCH_OAUTH_TOKEN=oauth:your_token_here
   TWITCH_CHANNEL=your_channel_name
5. Bot username auto-detected
```

**Enable in controls.py**:
```python
USE_TWITCH = True
```

### YouTube Chat

**Prerequisites**:
1. YouTube channel
2. Google API key
3. YouTube API enabled

**Setup**:
```
1. Go to: https://console.cloud.google.com/apis/
2. Create New Project
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials
5. Copy API key
6. Edit .env:
   YOUTUBE_API_KEY=your_key_here
```

**Enable in controls.py**:
```python
USE_YOUTUBE = True
```

### Sound Effects

**Prerequisites**: None (works out of the box)

**Setup**:
```
1. Copy WAV/MP3 files to:
   C:\Users\beren\Anna_AI\BASE\tools\installed\sound_effects\effects\
2. Enable in controls.py:
   USE_SOUND_EFFECTS = True
3. Agent can now trigger sounds
```

**Example sounds included**: Various notification and ambient sounds

### Calculator

**Prerequisites**: None (built-in)

**Enable in controls.py**:
```python
USE_CALCULATOR = True
```

Allows agent to perform complex math calculations.

### Web Fetch

**Prerequisites**: None

**Enable in controls.py**:
```python
USE_WEB_FETCH = True
```

Allows agent to download and parse web pages.

### Minecraft Bot

**Prerequisites**:
1. Minecraft Java Edition
2. Server or realm access
3. server.properties and auth set up

**Setup**: See `C:\Users\beren\AI_Agent_Tools\minecraft\README.md`

### Vision Tools

**Prerequisites**:
- opencv_vision: OpenCV installed (`pip install opencv-python`)
- game_vision: OpenCV + game running
- screenshot_vision: Built-in

**Enable in controls.py**:
```python
USE_OPENCV_VISION = True
USE_GAME_VISION = True
USE_SCREENSHOT_VISION = True
```

---

## Adding Tools to Your Agent

### Step 1: Install the Tool Files

Copy tool folder to:
```
C:\Users\beren\Anna_AI\BASE\tools\installed\[tool_name]
```

### Step 2: Enable in controls.py

Add/modify in `personality/controls.py`:
```python
USE_[TOOL_NAME] = True
```

Examples:
```python
USE_DISCORD = True
USE_SOUND_EFFECTS = True
USE_WEB_FETCH = True
```

### Step 3: Configure in .env (if needed)

Some tools need API keys:
```
DISCORD_BOT_TOKEN=your_token
TWITCH_OAUTH_TOKEN=oauth:your_token
YOUTUBE_API_KEY=your_key
```

### Step 4: Restart Anna AI

```powershell
# Stop if running
# Restart: START-OPTIMIZED.bat
```

Anna AI will auto-discover and load the new tools.

---

## Verifying Tools Are Loaded

### Check GUI

1. Launch Anna AI: `START-OPTIMIZED.bat`
2. Look at the Tools tab in GUI
3. Should see installed tools listed

### Check Console

```powershell
# Look for messages like:
# [TOOLS] Discovered: discord_chat
# [TOOLS] Discovered: sound_effects
```

### Test Tool

Send message to agent using a tool:
```
Example: "Play a sound effect"
or: "Search for Python documentation"
```

If agent responds and uses the tool, it's working ✓

---

## Recommended Installation

For a complete setup, I recommend:

### Essential (Start Here)
- ✓ sound_effects — Agent can make sounds
- ✓ discord_chat — If using Discord

### Nice to Have
- web_fetch — Download pages
- calculator — Do math
- reminders — Set alarms

### Optional
- Game tools (only if you play games)
- Vision tools (only if streaming/recording)

### Installation Command

```powershell
# Install essential + recommended tools
cd C:\Users\beren\Anna_AI\BASE\tools\installed

Copy-Item C:\Users\beren\AI_Agent_Tools\sound_effects . -Recurse
Copy-Item C:\Users\beren\AI_Agent_Tools\discord_chat . -Recurse
Copy-Item C:\Users\beren\AI_Agent_Tools\web_fetch . -Recurse
Copy-Item C:\Users\beren\AI_Agent_Tools\calculator . -Recurse
Copy-Item C:\Users\beren\AI_Agent_Tools\reminders . -Recurse
```

---

## Troubleshooting

### Tools Not Appearing in GUI

**Solution 1**: Verify files copied correctly
```powershell
dir C:\Users\beren\Anna_AI\BASE\tools\installed\
```

Should see tool folders listed.

**Solution 2**: Check tool structure
```powershell
# Each tool must have:
# - tool.py (main code)
# - information.json (metadata)

dir C:\Users\beren\Anna_AI\BASE\tools\installed\discord_chat
```

Should show both files.

**Solution 3**: Restart Anna AI
```powershell
# Close GUI completely
# Restart: START-OPTIMIZED.bat
```

### Tool Doesn't Work When Called

**Check controls.py**:
```python
# Verify tool is enabled
USE_DISCORD = True
USE_SOUND_EFFECTS = True
```

**Check .env (if needed)**:
```
DISCORD_BOT_TOKEN=your_actual_token  # Not empty
```

**Check logs**:
```
C:\Users\beren\Anna_AI\BASE\logs\
Look for error messages
```

### API Keys Not Working

**Solution 1**: Verify format
```
Discord: token should be long string
Twitch: should start with "oauth:"
YouTube: should be alphanumeric key
```

**Solution 2**: Restart Anna AI after .env changes
```powershell
# .env changes require restart
```

**Solution 3**: Generate new token
```
Some APIs expire or get revoked
Generate a fresh token and update .env
```

---

## Current Status

✓ AI Agent Tools downloaded  
✓ 24 tools available  
✓ Ready to install selectively  

**Next Steps**:
1. Decide which tools you want
2. Copy tool folders
3. Enable in controls.py
4. Configure API keys in .env (if needed)
5. Restart Anna AI

---

**Recommendation**: Start with `sound_effects` and `discord_chat` if you use Discord. These add the most value without complexity.

For more details on each tool, see individual README files in:
```
C:\Users\beren\AI_Agent_Tools\[tool_name]\README.md
```
