# Filename: personality/bot_info.py

# Bot and User Information
agentname = "Anna"
username = "Sir"

# user's in-game username, for bot reference
game_username = "Player"

# PRIMARY MODELS (Fast - 2-6s each)
thoughtmodel = "gemma3:12b-it-q4_K_M"
responsemodel = "gemma3:12b-it-q4_K_M"
toolmodel = "gemma3:12b-it-q4_K_M"
actionmodel = "gemma3:12b-it-q4_K_M"

# ALTRNATIVES : 
# qwen3-vl:8b-instruct-q4_K_M
# qwen3-vl:8b-thinking-q4_K_M

# SPECIALIZED MODELS
visionmodel = "gemma3:12b-it-q4_K_M"
embedmodel = "nomic-embed-text:latest"

# OPTIONAL: Complex reasoning (use sparingly)
reasoning_model = "gemma3:12b-it-q4_K_M"

voiceIndex = 1

# VB-Cable for audio output (use exact device name)
vb_cable_name = "CABLE Input"

# GROUP CHAT CONFIGURATION
# Unique port for this agent's group chat server
# Each agent needs a different port (e.g., 54321, 54322, 54323, etc.)
group_chat_port = 54321

