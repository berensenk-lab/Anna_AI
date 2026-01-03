# Filename: personality/controls.py
"""
Dynamic control variables for AI functionality.
These variables can be modified at runtime to enable/disable features.
Control methods are available in BASE.core.control_methods
Change values in this file to set defaults at startup.

REFACTORED: Simplified continuous thinking configuration
"""

# === SYSTEM EXECUTIONS ===

# ========================================================================
# MASTER PROCESSING CONTROLS
# ========================================================================

SLOW_MODE = False # Enable for slower agent processing and responses
DELAY_TIMER = 10  # Timeout for prompt processing (seconds)

# === EMERGENCY STOP ===
# Global kill switch to immediately halt all agent operations
# If encountered in input from any source, the agent will cease all actions
# This should be a string that is unlikely to be used in normal conversation,
# appear in search results, etc. Recommended: Something easy to speak when using voice input.
KILL_COMMAND = "shut down sleep now"

# === CONTINUOUS AUTONOMOUS THINKING ===
# Single system for all background cognitive processing
# Handles reactive (responding to events) and proactive (self-initiated) thinking

ENABLE_CONTINUOUS_THINKING = True  # Master toggle for autonomous cognitive loop

CHAT_ENGAGEMENT = False

# Thinking pace configuration
MIN_PROACTIVE_INTERVAL = 5.0   # Minimum seconds between self-initiated thoughts
MAX_PROACTIVE_INTERVAL = 15.0  # Force a thought after this much silence
MAX_CONSECUTIVE_PROACTIVE = 200 # Max autonomous thoughts before needing external input

# === AUTO-RESPONSE (GUI/CLI specific) ===
# Separate from continuous thinking - this is for explicit user-facing responses
AUTO_RESPOND = False              # Enable automatic responses when no user input detected
AUTO_RESPOND_INTERVAL = 60        # Time interval (seconds) to trigger auto-response

# Streaming configuration
USE_STREAMING = True  # Enable streaming response generation

# ========================================================================
# COGNITIVE LOOP CONTROLS
# ========================================================================

# Enable continuous autonomous thinking
ENABLE_CONTINUOUS_THINKING = False

# Auto-restart cognitive loop after crashes
# - True: Auto-restart up to 3 times with exponential backoff
# - False: Stop completely on first error, require manual restart
AUTO_RESTART = True

# === PROCESSING RATE LIMITING ===
# Limit how fast the agent can think/process
LIMIT_PROCESSING = False  # Enable processing rate limiting
PROCESSING_DELAY = 10     # Seconds between processing cycles when LIMIT_PROCESSING enabled

# === SPEAKING RATE LIMITING ===
# Limit how often the agent can speak (independent of thinking speed)
LIMIT_SPEAKING = False     # Enable speaking rate limiting
SPEAKING_DELAY = 30       # Minimum seconds between spoken responses when LIMIT_SPEAKING enabled

# DEPRECATED: Old combined control (kept for backwards compatibility)
SLOW_MODE = False
DELAY_TIMER = 30
RESPONSE_DELAY_TIMER = 60


# ========================================================================
# INTERNAL TOOL CONTROLS
# ========================================================================

# === VOLUME CONTROLS ===
VOICE_VOLUME = 1.0              # Set TTS voice volume (1.0 = 100%)
SOUND_EFFECT_VOLUME = 1.0       # Set sound effects volume (1.0 = 100%)

# === MEMORY CONTEXT ===
USE_BASE_MEMORY = True         # Use BASE memory system (document embeddings)
USE_LONG_MEMORY = True         # Use long-term memory context (embedded conversation summaries of past days)
USE_SHORT_MEMORY = True        # Use short-term memory context (No embeddings, today's conversation entries)

# === PROMPT COMPONENTS ===
# USE_SYSTEM_PROMPT = False       # Include system/personality prompt

# === MEMORY MANAGEMENT ===
SAVE_MEMORY = True             # Save conversations to memory system
MEMORY_LENGTH = 25             # Number of recent interactions to keep
MAX_LONG_TERM_MEMORIES = 1
MAX_BASE_MEMORIES = 1

# === AVATAR ABILITIES ===
AVATAR_SPEECH = True           # Enable text-to-speech output
USE_CUSTOM_VOICE = True       # Use custom voice model instead of standard system TTS (requires AVATAR_SPEECH enabled)

# Game State - Master Control (automatically managed by control system)
PLAYING_GAME = False  # Auto-set to True when ANY game is selected

# === INTELLIGENT TOOL USE ===
INTELLIGENT_TOOL_SELECTION = False
USE_AI_TOOL_VERIFICATION = False
TOOL_SELECTION_THRESHOLD = 0.3

# === OUTPUT ACTIONS ===
ENABLE_CONTENT_FILTER = False  # Master toggle
USE_AI_CONTENT_FILTER = False  # AI semantic check (slower)
CONTENT_FILTER_INCOMING = False  # Filter all incoming data
CONTENT_FILTER_OUTGOING = False  # Filter all outgoing responses
CONTENT_FILTER_CONTEXT = False  # Filter context in prompts

# OpenCV Vision Configuration
USE_OPENCV_VISION = False  # Set to True to enable

# Optional: Performance tuning
opencv_vision_fps = 15              # Capture frame rate (1-60)
opencv_vision_interval = 5.0        # Analysis interval in seconds
opencv_vision_width = 1024          # Capture width (smaller = faster)
opencv_vision_height = 768          # Capture height
opencv_vision_change_threshold = 50000  # Change detection sensitivity

# ========================================================================
# EXTERNAL TOOL CONTROLS
# ========================================================================

# # === GROUP CHAT CONTEXT ===
# IN_DISCORD_CHAT = False        # Enable Discord chat integration
# IN_YOUTUBE_CHAT = False        # Include YouTube chat context
# IN_TWITCH_CHAT = False         # Include Twitch chat context

# # === TWITCH SPECIFIC ===
# TWITCH_CHANNEL = ""            # Twitch channel to monitor (e.g., "shroud")
# TWITCH_OAUTH_TOKEN = ""        # OAuth token for authenticated mode (optional)
# TWITCH_NICKNAME = ""           # Bot nickname for Twitch (optional, uses justinfan if empty)
# TWITCH_SEND_MESSAGES = False   # Enable sending messages to Twitch chat
# TWITCH_MESSAGE_COOLDOWN = 3    # Cooldown between messages (seconds)
# TWITCH_LOG_MESSAGES = False     # Log Twitch chat messages for debugging

# # === DISCORD SPECIFIC ===
# DISCORD_RESPOND_TO_MENTIONS = False    # Respond when bot is mentioned
# DISCORD_RESPOND_TO_REPLIES = False     # Respond when messages reply to bot
# DISCORD_RESPOND_TO_DMS = False         # Respond to direct messages
# DISCORD_RESPOND_IN_THREADS = False     # Respond in thread conversations
# DISCORD_AUTO_REACT = False            # Automatically react to messages
# DISCORD_TYPING_INDICATOR = False       # Show typing indicator while generating response
# DISCORD_MESSAGE_HISTORY_LIMIT = 10    # Number of previous messages to include as context
# DISCORD_MAX_MESSAGE_LENGTH = 2000     # Maximum message length (Discord limit)
# DISCORD_SPLIT_LONG_MESSAGES = False    # Split messages longer than max length
# DISCORD_INCLUDE_EMBEDS = False        # Include embed content in context
# DISCORD_INCLUDE_ATTACHMENTS = False    # Process message attachments (images, files)
# DISCORD_COMMAND_COOLDOWN = 3          # Cooldown between commands (seconds)
# DISCORD_LOG_MESSAGES = False           # Log Discord messages for debugging

# # === CODING SPECIFIC ===
# CODING_SERVER_URL = "http://localhost:3000"  # VS Code extension server URL
# CODING_TIMEOUT = 30            # Timeout for coding requests (seconds)

# Individual Game Controls (only one can be True at a time)
# PLAYING_MINECRAFT = False
# PLAYING_LEAGUE = False


# ========================================================================
# LIVE EDITING CONTROLS
# ========================================================================

# Tool Hot-Reload: Reload individual tools via GUI buttons
# - Click reload button on any tool panel
# - Tool stops, reloads code, restarts with state preserved
# - Useful for rapid tool development iteration
ENABLE_TOOL_HOT_RELOAD = True

# Core Hot-Reload: Auto-reload prompt constructors on file save
# - Watches prompt constructor files for changes
# - Automatically reloads when you save edits
# - Useful for rapid prompt engineering iteration
# - Requires 'watchdog' package: pip install watchdog
ENABLE_CORE_HOT_RELOAD = True

# Hot-reload configuration
ENABLE_HOT_RELOAD = True  # Master switch
ENABLE_FILE_WATCHING = True  # Auto-reload on file change (dev mode)
HOT_RELOAD_DEBOUNCE = 2.0  # Seconds to wait before reload (prevents spam)

# ========================================================================
# LOGGING AND DISPLAY CONTROLS
# ========================================================================

LOG_TOOL_EXECUTION = True      # Log tool usage details and all tool returns
LOG_PROMPT_CONSTRUCTION = False  # Log complete constructed user prompts

LOG_REACTIVE_PROMPT = True
LOG_REFLECTIVE_PROMPT = True
LOG_PROACTIVE_PROMPT = True
LOG_RESPONSIVE_PROMPT = True
LOG_ACTION_PROMPT = True

LOG_RESPONSE_PROCESSING = True  # Log complete agent responses (entire response, before extracting direct response)
LOG_SYSTEM_INFORMATION = True # Log all default system information not included in a different category
SHOW_CHAT = False              # Choose if chat messages from live chat are printed to output

LOG_CODING_EXECUTION = False     # Log coding tool operations
LOG_DISCORD_EXECUTION = False    # Log Discord-specific operations

LOG_MINECRAFT_EXECUTION = False  # Log Minecraft-specific operations
# Note: Control methods (toggle_feature, set_feature, etc.) are available in:
# from BASE.core.control_methods import ControlManager