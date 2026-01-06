# Filename: personality/controls.py
"""
Dynamic control variables for AI functionality.
These variables can be modified at runtime to enable/disable features.
Control methods are available in BASE.core.control_manager

ARCHITECTURE:
- Core agent controls defined here
- Tool controls (USE_XTTS, USE_GPT_SOVITS, etc.) dynamically created from information.json
- Dynamic creation happens in BASE.core.dynamic_control_initializer
- Run initializer BEFORE GUI to ensure all tool controls exist

Change values in this file to set defaults at startup.
"""

# ========================================================================
# EMERGENCY CONTROLS
# ========================================================================

# Global kill switch to immediately halt all agent operations
# If encountered in input from any source, the agent will cease all actions
# Recommended: Something easy to speak when using voice input
KILL_COMMAND = "shut down sleep now"

# ========================================================================
# COGNITIVE LOOP CONTROLS
# ========================================================================

# Continuous autonomous thinking system
# Handles reactive (responding to events) and proactive (self-initiated) thinking
ENABLE_CONTINUOUS_THINKING = False  # Master toggle for autonomous cognitive loop

# Thinking pace configuration
MIN_PROACTIVE_INTERVAL = 5.0   # Minimum seconds between self-initiated thoughts
MAX_PROACTIVE_INTERVAL = 15.0  # Force a thought after this much silence
MAX_CONSECUTIVE_PROACTIVE = 200 # Max autonomous thoughts before needing external input

# Chat engagement (respond to unaddressed chat messages)
CHAT_ENGAGEMENT = False

# Auto-restart cognitive loop after crashes
# - True: Auto-restart up to 3 times with exponential backoff
# - False: Stop completely on first error, require manual restart
AUTO_RESTART = False

# ========================================================================
# RATE LIMITING
# ========================================================================

# Processing rate limiting (how fast agent can think)
LIMIT_PROCESSING = False  # Enable processing rate limiting
PROCESSING_DELAY = 10     # Seconds between processing cycles when enabled

# Speaking rate limiting (how often agent can speak)
LIMIT_SPEAKING = False     # Enable speaking rate limiting
SPEAKING_DELAY = 30       # Minimum seconds between spoken responses when enabled

# ========================================================================
# AUTO-RESPONSE (GUI/CLI)
# ========================================================================

# Automatic responses when no user input detected
AUTO_RESPOND = False              # Enable automatic responses
AUTO_RESPOND_INTERVAL = 60        # Time interval (seconds) to trigger auto-response

# Auto-prompts (background checks)
AUTO_PROMPT = False               # Enable periodic background checks
AUTO_PROMPT_INTERVAL = 300        # Auto-prompt interval in seconds

# ========================================================================
# STREAMING
# ========================================================================

# Enable streaming response generation
USE_STREAMING = False
STREAM_RESPONSES = False

# ========================================================================
# MEMORY SYSTEM
# ========================================================================

# Memory context layers
USE_BASE_MEMORY = True         # BASE memory (document embeddings)
USE_LONG_MEMORY = True         # Long-term memory (embedded conversation summaries)
USE_SHORT_MEMORY = True        # Short-term memory (today's conversation entries)

# Memory management
SAVE_MEMORY = True             # Save conversations to memory system
USE_MEMORY = True              # Enable memory system
MEMORY_LENGTH = 25             # Number of recent interactions to keep
MAX_LONG_TERM_MEMORIES = 1     # Max long-term memory results per query
MAX_BASE_MEMORIES = 1          # Max base memory results per query

# ========================================================================
# TOOL CONTROLS - DYNAMICALLY CREATED
# ========================================================================
# 
# Tool control variables (USE_XTTS, USE_GPT_SOVITS, USE_WHISPER, etc.)
# are automatically created by BASE.core.dynamic_control_initializer
# 
# Internal tools (TTS, voice input):
#   - Created from BASE/tools/internal/*/information.json
#   - Mutual exclusivity enforced by service_type
#   - Highest priority tool enabled by default
# 
# External tools (web search, integrations):
#   - Created from BASE/tools/installed/*/information.json
#   - Defaults from control_variable_value field
# 
# Examples of dynamically created controls:
#   USE_GPT_SOVITS = True   (priority=15, highest in 'tts')
#   USE_XTTS = False        (priority=10)
#   USE_PYTTSX3 = False     (priority=5)
#   USE_SILERO_VAD = True   (priority=12, highest in 'voice_input')
#   USE_WHISPER = False     (priority=10)
#   USE_VOSK = False        (priority=5)
#   USE_WEB_SEARCH = True   (external tool)
#   USE_TWITCH = False      (external tool)
# 
# To add a new tool control:
#   1. Add tool directory to tools/internal/ or tools/installed/
#   2. Include information.json with control_variable_name
#   3. Restart agent - control variable created automatically
# 
# DO NOT manually define tool controls here - they are created dynamically!
#
# ========================================================================

# ========================================================================
# TOOL INTELLIGENCE
# ========================================================================

# Intelligent tool selection and verification
INTELLIGENT_TOOL_SELECTION = False
USE_AI_TOOL_VERIFICATION = False
TOOL_SELECTION_THRESHOLD = 0.3

# ========================================================================
# CONTENT FILTERING
# ========================================================================

# Content filter system
ENABLE_CONTENT_FILTER = False  # Master toggle
USE_AI_CONTENT_FILTER = False  # AI semantic check (slower)
CONTENT_FILTER_INCOMING = False  # Filter all incoming data
CONTENT_FILTER_OUTGOING = False  # Filter all outgoing responses
CONTENT_FILTER_CONTEXT = False  # Filter context in prompts

# ========================================================================
# VOLUME CONTROLS
# ========================================================================

# Voice volume (0.0 to 1.0)
VOICE_VOLUME = 1.0

# Sound effects volume (0.0 to 1.0)
SOUND_EFFECT_VOLUME = 1.0

# Master toggle for avatar speech (auto-enabled if any TTS tool is active)
AVATAR_SPEECH = True

# ========================================================================
# VISION SYSTEMS
# ========================================================================

# OpenCV Vision Configuration
USE_OPENCV_VISION = False  # Set to True to enable

# Performance tuning
opencv_vision_fps = 15              # Capture frame rate (1-60)
opencv_vision_interval = 5.0        # Analysis interval in seconds
opencv_vision_width = 1024          # Capture width (smaller = faster)
opencv_vision_height = 768          # Capture height
opencv_vision_change_threshold = 50000  # Change detection sensitivity

# ========================================================================
# MULTI-AGENT SYSTEMS
# ========================================================================

# Voice Hub for multi-agent voice interaction
# When True:
# - Agent connects to shared Voice Hub for speech recognition
# - Single GPU instance shared across all agents (memory efficient)
# - Agents can hear each other speak (injected to thought buffer)
# - User speech broadcast to all connected agents
# When False:
# - Agent uses local voice processing
# - Each agent loads own voice recognition instance
GROUP_CHAT = False

# Game state (automatically managed)
PLAYING_GAME = False  # Auto-set to True when ANY game is selected

# ========================================================================
# HOT RELOAD & LIVE EDITING
# ========================================================================

# Tool Hot-Reload: Reload individual tools via GUI buttons
ENABLE_TOOL_HOT_RELOAD = False

# Core Hot-Reload: Auto-reload prompt constructors on file save
# Requires 'watchdog' package: pip install watchdog
ENABLE_CORE_HOT_RELOAD = False

# Hot-reload configuration
ENABLE_HOT_RELOAD = False  # Master switch
ENABLE_FILE_WATCHING = False  # Auto-reload on file change (dev mode)
HOT_RELOAD_DEBOUNCE = 2.0  # Seconds to wait before reload (prevents spam)

# ========================================================================
# THOUGHT BUFFER & PROCESSING
# ========================================================================

# Enable thought buffer processing
USE_THOUGHT_BUFFER = True

# ========================================================================
# LOGGING AND DISPLAY
# ========================================================================

# Tool and execution logging
LOG_TOOL_EXECUTION = True      # Log tool usage details and returns
LOG_PROMPT_CONSTRUCTION = False  # Log complete constructed prompts

# Prompt type logging
LOG_REACTIVE_PROMPT = True     # Log reactive (event-driven) prompts
LOG_REFLECTIVE_PROMPT = True   # Log reflective (analysis) prompts
LOG_PROACTIVE_PROMPT = True    # Log proactive (self-initiated) prompts
LOG_RESPONSIVE_PROMPT = True   # Log responsive (reply) prompts
LOG_ACTION_PROMPT = True       # Log action execution prompts

# Response and system logging
LOG_RESPONSE_PROCESSING = True  # Log complete agent responses
LOG_SYSTEM_INFORMATION = True   # Log system information
SHOW_CHAT = False               # Print live chat messages to output

# Specialized logging
LOG_CODING_EXECUTION = False    # Log coding tool operations
LOG_DISCORD_EXECUTION = False   # Log Discord operations
LOG_MINECRAFT_EXECUTION = False # Log Minecraft operations

# ========================================================================
# PERFORMANCE SETTINGS
# ========================================================================

# LLM settings
MAX_TOKENS = 2000      # Maximum tokens for LLM responses
TEMPERATURE = 0.7      # Temperature for LLM sampling (0.0-2.0)

# Legacy compatibility
SLOW_MODE = False      # Deprecated: Use LIMIT_PROCESSING instead
DELAY_TIMER = 10       # Deprecated: Use PROCESSING_DELAY instead

# ========================================================================
# NOTES
# ========================================================================
#
# Dynamic Tool Controls:
#   Tool controls (USE_*) are created automatically by:
#   BASE.core.dynamic_control_initializer.initialize_dynamic_controls()
#
#   This must run BEFORE GUI initialization to ensure all controls exist.
#
# Adding New Tools:
#   1. Create tool directory in tools/internal/ or tools/installed/
#   2. Add information.json with control_variable_name and priority
#   3. Restart agent - control appears automatically in GUI
#
# Mutual Exclusivity (Internal Tools):
#   - Only one TTS tool can be active (gpt_sovits OR xtts OR pyttsx3)
#   - Only one voice_input tool can be active (silero_vad OR whisper OR vosk)
#   - Enforced by control manager and GUI
#
# Priority System (Internal Tools):
#   - Highest priority tool in each service_type enabled by default
#   - Example: gpt_sovits (priority=15) > xtts (priority=10) > pyttsx3 (priority=5)
#
# ========================================================================