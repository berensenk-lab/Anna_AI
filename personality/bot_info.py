# Filename: personality/bot_info.py
"""
Bot Identity and Model Configuration
"""
# ========================================================================
# BOT AND USER IDENTITY
# ========================================================================
# Bot's name (how it refers to itself)
agentname = "Anna"
# User's name (how bot refers to the user)
username = "Almoo"
# User's in-game username (for game-specific interactions)
game_username = "Player"

# ========================================================================
# MODEL CONFIGURATION
# ========================================================================

# PRIMARY MODELS (Fast - 2-6s each)
# Used for most cognitive operations
#
# thoughtmodel  : reasoning before acting — needs to understand code structure
# toolmodel     : decides which tool to call and how — critical for coding workflow
# actionmodel   : executes the action — needs precise, structured output
# responsemodel : generates the final reply shown to user — keep gemma3 for quality prose
#
# qwen2.5-coder:7b is used for thought/tool/action because:
#   - Purpose-built for code understanding and generation
#   - 7B fits comfortably on RTX 4060 8GB alongside gemma3:12b (which offloads to RAM)
#   - Significantly better at following structured tool-call formats than mistral-nemo
#   - Faster than mistral-nemo:12b, freeing VRAM headroom

thoughtmodel = "qwen2.5-coder:7b"
responsemodel = "qwen2.5:7b"
toolmodel = "qwen2.5-coder:7b"
actionmodel = "qwen2.5-coder:7b"

# SPECIALIZED MODELS
visionmodel = "qwen2.5:7b"
embedmodel = "nomic-embed-text:latest"

# ========================================================================
# ALTERNATIVE MODELS (swap in to experiment)
# ========================================================================
#
# If qwen2.5-coder:7b feels slow or hits VRAM limits, try:
#   thoughtmodel = "qwen2.5-coder:3b"   # lighter, still code-aware, ~2-3GB VRAM
#   toolmodel    = "qwen2.5-coder:3b"
#   actionmodel  = "qwen2.5-coder:3b"
#
# If you want even stronger coding at the cost of speed (close Chrome/Discord first):
#   thoughtmodel = "qwen2.5-coder:14b"  # needs ~10GB, will spill to RAM
#   toolmodel    = "qwen2.5-coder:14b"
#   actionmodel  = "qwen2.5-coder:14b"
#
# Other good code-focused 7B options:
#   "deepseek-coder:6.7b"               # strong at multi-file reasoning
#   "codellama:7b"                       # solid general coding, Meta model
#
# General-purpose fallback (previous config):
#   thoughtmodel = "mistral-nemo"        # 12B, good all-rounder, weaker on code
#   toolmodel    = "mistral-nemo"
#   actionmodel  = "mistral-nemo"
#
# Pull any model with: ollama pull <model_name>
# Check installed models with: ollama list

# ========================================================================
# VOICE CONFIGURATION
# ========================================================================
# Voice index (for pyttsx3 system voices)
# Use test_voices.py to find available voices and their indices
voiceIndex = 0
# VB-Cable audio output device name
# Used for routing TTS audio to virtual audio cable
# Must match exact device name in Windows Sound Settings
vb_cable_name = "CABLE Input"
# NOTE: TTS engine selection (XTTS, GPT-SoVITS, pyttsx3) is now controlled
# dynamically via personality/controls.py and tool priority system.
# See BASE/tools/internal/ for available TTS engines.

# ========================================================================
# MULTI-AGENT CONFIGURATION
# ========================================================================
# Group Chat Server Port
# Each agent instance needs a unique port for Voice Hub communication
# Examples: 54321 (first agent), 54322 (second agent), etc.
# Only used when GROUP_CHAT = True in controls.py
group_chat_port = 54321

# ========================================================================
# NOTES
# ========================================================================
#
# Model Selection:
#   - All models should be available in your Ollama installation
#   - Verify with: ollama list
#   - Pull models with: ollama pull <model_name>
#
# Voice Configuration:
#   - voiceIndex: Run tools/voice_test.py to find available system voices
#   - vb_cable_name: Check Windows Sound Settings > Playback Devices
#
# TTS Engine Selection:
#   - Controlled via personality/controls.py (dynamic tool system)
#   - Available engines: GPT-SoVITS, XTTS, pyttsx3
#   - Priority determines default: highest priority = enabled at startup
#
# Multi-Agent Setup:
#   - Each agent needs unique group_chat_port (54321, 54322, 54323, ...)
#   - Enable GROUP_CHAT in controls.py to activate Voice Hub
#   - First agent to start will spawn the Voice Hub server
#
# ========================================================================
