# Filename: personality/bot_info.py

# Bot and User Information
agentname = "Anna"
username = "Sir"

# user's in-game username, for bot reference
game_username = "Player"

# PRIMARY MODELS (Fast - 2-6s each)
# thoughtmodel = "llama3.1:8b-instruct-q4_K_M"
# responsemodel = "llama3.1:8b-instruct-q4_K_M"
# toolmodel = "llama3.1:8b-instruct-q4_K_M"
thoughtmodel = "gemma3:12b-it-q4_K_M"
responsemodel = "gemma3:12b-it-q4_K_M"
toolmodel = "gemma3:12b-it-q4_K_M"
actionmodel = "gemma3:12b-it-q4_K_M"

# ALTRNATIVES : 
# qwen3-vl:8b-instruct-q4_K_M
# qwen3-vl:8b-thinking-q4_K_M

# SPECIALIZED MODELS
# visionmodel = "llama3.2-vision:11b-instruct-q4_K_M"
visionmodel = "gemma3:12b-it-q4_K_M"
embedmodel = "nomic-embed-text:latest"

# OPTIONAL: Complex reasoning (use sparingly)
reasoning_model = "gemma3:12b-it-q4_K_M"

voiceIndex = 1




