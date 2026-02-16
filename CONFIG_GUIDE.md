# Anna_AI Configuration Guide

Complete reference for configuring Anna_AI agent behavior and performance.

## Configuration Files Overview

| File | Purpose | Edit Frequency |
|------|---------|-----------------|
| `personality/bot_info.py` | Agent personality, models, voice | Often |
| `config.json` | Application settings, Ollama connection | Sometimes |
| `.env` | Ollama server optimization | Rarely (performance tuning only) |
| `personality/controls.py` | Feature toggles, debugging | Rarely |

---

## personality/bot_info.py - Agent Configuration

This is the **primary configuration file**. Edit here for most customization.

### Identity Section

```python
# How the agent identifies itself
agentname = "Anna"                  # Display name in conversations
username = "Sir"                    # How agent addresses the user
game_username = "Player"            # In-game reference name
```

### Model Selection

```python
# Each model handles different tasks
# All must be available in: ollama list

thoughtmodel = "gemma3:12b-it-q4_K_M"       # Internal reasoning
responsemodel = "gemma3:12b-it-q4_K_M"      # User-facing responses
toolmodel = "gemma3:12b-it-q4_K_M"          # Function/tool execution
actionmodel = "gemma3:12b-it-q4_K_M"        # Game action decisions
visionmodel = "gemma3:12b-it-q4_K_M"        # Image analysis
embedmodel = "nomic-embed-text:latest"      # Text embeddings (for memory)
```

**Model Selection Guide**:

**For best performance (faster):**
```python
thoughtmodel = "gemma2:6b-it-q4_K_M"
responsemodel = "gemma2:6b-it-q4_K_M"
# Uses half the VRAM, ~3x faster
```

**For best quality (slower):**
```python
thoughtmodel = "gemma3:12b-it-q4_K_M"
responsemodel = "gemma3:12b-it-q4_K_M"
# Uses full VRAM, more intelligent responses
```

**Available Models** (download first with `ollama pull`):
- `gemma3:12b-it-q4_K_M` - Best quality, 7GB (recommended)
- `gemma2:6b-it-q4_K_M` - Balanced, 3.5GB (faster)
- `qwen3-vl:8b-instruct-q4_K_M` - Vision-capable, 5GB
- `phi:2.5-instruct-q4_K_M` - Lightweight, 2GB (speed)
- `mistral:7b-instruct-q4_K_M` - Balanced, 4GB

### Voice & Audio

```python
# TTS Voice selection
voiceIndex = 1                      # 0-9 for different voices, try different numbers

# Virtual audio cable routing
vb_cable_name = "CABLE Input"       # Must match Windows device name exactly
# For multiple agents: "CABLE-A Input", "CABLE-B Input", etc.

# Audio output behavior
audio_enabled = True
speak_responses = True              # Agent speaks its responses
speak_thoughts = False              # Agent speaks internal thoughts (usually off)
```

**Finding your VB-Cable name**:
```
Windows Settings → Sound → Advanced sound options → App volume and device preferences
Look for: "CABLE Input (VB-Audio Virtual Cable)"
Use exact name in vb_cable_name
```

### Multi-Agent Configuration

For running multiple agents simultaneously:

```python
# Must be unique per agent
agentname = "Anna"                  # Different for each agent
group_chat_port = 54321             # Unique port: 54321, 54322, 54323...
vb_cable_name = "CABLE Input"       # Different per agent: CABLE, CABLE-A, CABLE-B
```

### Memory Configuration

```python
# How agent remembers past conversations
use_memory = True
memory_type = "vector"              # or "semantic"
memory_length = 25                  # Number of messages to remember
memory_save_interval = 10           # Save every N interactions
```

---

## config.json - Application Settings

JSON configuration for application-level behavior.

### Ollama Connection

```json
{
  "ollama": {
    "endpoint": "http://localhost:11434",   # Ollama server location
    "temperature": 0.85,                     # Creativity (0=deterministic, 1=creative)
    "max_tokens": 1000,                      # Max response length
    "num_ctx": 3000,                         # Context window size
    "top_p": 0.9,                            # Nucleus sampling
    "top_k": 40,                             # Top-k sampling
    "repeat_penalty": 1.1,                   # Penalize repetition
    "request_timeout": 300                   # Request timeout seconds
  }
}
```

**Temperature Tuning**:
- `0.1-0.3`: Focused, deterministic (good for factual info)
- `0.5-0.7`: Balanced
- `0.8-1.0`: Creative, varied responses

**Context Window** (num_ctx):
- Larger = more conversation history remembered, slower
- Smaller = faster, less context
- Match to model capabilities (usually 2048-8192)

### Bot Settings

```json
{
  "bot": {
    "name": "Anna",
    "username": "Master",
    "personality": "helpful and friendly",
    "max_response_time": 30,        # Seconds
    "auto_respond": false,          # Auto-generate responses
    "verbose_logging": false        # Debug output
  }
}
```

### Warudo Integration (Optional)

For avatar animation:

```json
{
  "warudo": {
    "websocket_url": "ws://127.0.0.1:19190",
    "enabled": true,
    "auto_connect": true,
    "auto_idle": true,              # Idle animation when not speaking
    "idle_timeout": 30              # Seconds before idle
  }
}
```

### Features

```json
{
  "features": {
    "use_warudo": true,             # Avatar animation
    "use_sound_effects": true,      # SFX on actions
    "use_custom_voice": true,       # TTS voice
    "continuous_thinking": true,    # Agent thinks before responding
    "tool_use": true                # Can execute functions
  }
}
```

---

## .env - Ollama Server Optimization

Advanced performance tuning. Only modify if experiencing performance issues.

### Recommended Defaults

```bash
# Performance
OLLAMA_NUM_PARALLEL=1               # Single request processing
OLLAMA_CONTEXT_LENGTH=8192          # Context window (match num_ctx in config.json)
OLLAMA_FLASH_ATTENTION=true         # GPU optimization
OLLAMA_KEEP_ALIVE=24h               # Keep models loaded 24 hours

# GPU
CUDA_VISIBLE_DEVICES=0              # Use first GPU
OLLAMA_GPU_OVERHEAD=1024            # GPU memory overhead

# API
OLLAMA_HOST=0.0.0.0:11434           # Listen on all interfaces
OLLAMA_ORIGINS=*                    # Allow all API origins

# Model Loading
OLLAMA_MAX_LOADED_MODELS=2          # Load up to 2 models simultaneously
```

### Performance Profiles

**Profile: Speed (Fastest)**
```bash
OLLAMA_CONTEXT_LENGTH=2048          # Reduce context
OLLAMA_NUM_PARALLEL=1
OLLAMA_FLASH_ATTENTION=true
OLLAMA_KEEP_ALIVE=1h                # Unload after 1 hour
OLLAMA_MAX_LOADED_MODELS=1
```

**Profile: Balanced (Recommended)**
```bash
OLLAMA_CONTEXT_LENGTH=8192
OLLAMA_NUM_PARALLEL=1
OLLAMA_FLASH_ATTENTION=true
OLLAMA_KEEP_ALIVE=24h
OLLAMA_MAX_LOADED_MODELS=2
```

**Profile: Quality (Best Responses)**
```bash
OLLAMA_CONTEXT_LENGTH=16384         # Full context
OLLAMA_NUM_PARALLEL=1
OLLAMA_FLASH_ATTENTION=true
OLLAMA_KEEP_ALIVE=24h
OLLAMA_MAX_LOADED_MODELS=3          # Load multiple models
```

**Profile: Low VRAM (8GB GPU)**
```bash
OLLAMA_CONTEXT_LENGTH=4096
OLLAMA_GPU_OVERHEAD=512
OLLAMA_MAX_LOADED_MODELS=1
OLLAMA_KEEP_ALIVE=1h
```

### Variable Reference

| Setting | Range | Effect |
|---------|-------|--------|
| `OLLAMA_CONTEXT_LENGTH` | 1024-32768 | Larger = more history, slower |
| `OLLAMA_NUM_PARALLEL` | 1+ | How many requests simultaneously |
| `OLLAMA_KEEP_ALIVE` | 0-∞ | How long to keep models in VRAM |
| `OLLAMA_GPU_OVERHEAD` | 256-2048 | GPU memory reserved for OS |
| `CUDA_VISIBLE_DEVICES` | 0-7 | Which GPU to use (0=first GPU) |

---

## personality/controls.py - Feature Toggles

Enable/disable agent features and debugging.

### Core Features

```python
# Agent behavior
ENABLE_CONTINUOUS_THINKING = True   # Agent thinks before responding
AUTO_RESPOND = False                # Automatically generate responses
USE_STREAMING = True                # Stream responses in real-time

# Tools & Integrations
ENABLE_TOOL_USE = True              # Agent can call functions
ENABLE_WEB_SEARCH = False           # Agent can search the web
ENABLE_IMAGE_ANALYSIS = False       # Agent can see images
```

### Memory Systems

```python
# Memory management
USE_BASE_MEMORY = True              # Static personality/knowledge
USE_LONG_MEMORY = True              # Long-term conversation history
USE_SHORT_MEMORY = True             # Recent context
SAVE_MEMORY = True                  # Persist memory to disk

MEMORY_LENGTH = 25                  # Messages to remember
MEMORY_UPDATE_INTERVAL = 5          # Update memory every N interactions
```

### Avatar & Voice

```python
# Voice & TTS
AVATAR_SPEECH = True                # Avatar speaks responses
USE_CUSTOM_VOICE = True             # Use configured TTS voice
VOICE_VOLUME = 1.0                  # Volume level (0-1)

# Sound effects
ENABLE_SOUND_EFFECTS = True
SOUND_EFFECT_VOLUME = 1.0           # SFX volume (0-1)
```

### Debugging

```python
# Enable detailed logging (helps troubleshooting)
LOG_TOOL_EXECUTION = False
LOG_PROMPT_CONSTRUCTION = False
LOG_RESPONSE_PROCESSING = False
LOG_SYSTEM_INFORMATION = False
DEBUG_MODE = False
```

---

## Example Configurations

### Gaming Bot

For Minecraft or game integration:

```python
# bot_info.py
agentname = "GameMaster"
game_username = "Player"
thoughtmodel = "gemma3:12b-it-q4_K_M"    # Smart gameplay decisions
responsemodel = "gemma3:12b-it-q4_K_M"
```

```json
// config.json
{
  "bot": {
    "personality": "knowledgeable gaming expert"
  },
  "features": {
    "tool_use": true,
    "continuous_thinking": true
  }
}
```

### Speed-Optimized

For fast responses with lower VRAM:

```python
# bot_info.py
thoughtmodel = "gemma2:6b-it-q4_K_M"     # Lighter model
responsemodel = "gemma2:6b-it-q4_K_M"
```

```bash
# .env
OLLAMA_CONTEXT_LENGTH=4096
OLLAMA_MAX_LOADED_MODELS=1
OLLAMA_KEEP_ALIVE=1h
```

```json
// config.json
{
  "ollama": {
    "temperature": 0.3,
    "max_tokens": 500
  }
}
```

### Quality-Focused

For best responses (higher VRAM required):

```python
# bot_info.py
thoughtmodel = "gemma3:12b-it-q4_K_M"    # Largest model
responsemodel = "gemma3:12b-it-q4_K_M"
```

```bash
# .env
OLLAMA_CONTEXT_LENGTH=16384
OLLAMA_MAX_LOADED_MODELS=3
OLLAMA_KEEP_ALIVE=24h
```

```json
// config.json
{
  "ollama": {
    "temperature": 0.85,
    "max_tokens": 2000,
    "num_ctx": 8192
  }
}
```

---

## Common Configuration Changes

### Change Agent Name

In `bot_info.py`:
```python
agentname = "MyAgent"
username = "MyName"
```

Then restart `START.bat`

### Change Voice

In `bot_info.py`:
```python
voiceIndex = 2          # Try 0-9 to find different voices
```

Restart `START.bat`

### Improve Response Quality

In `.env`:
```bash
OLLAMA_CONTEXT_LENGTH=8192     # Increase context
OLLAMA_KEEP_ALIVE=24h          # Keep models loaded
```

In `config.json`:
```json
"temperature": 0.85,
"max_tokens": 1000
```

Restart Ollama and `START.bat`

### Speed Up Responses

In `.env`:
```bash
OLLAMA_CONTEXT_LENGTH=4096     # Reduce context
```

In `config.json`:
```json
"temperature": 0.3,
"max_tokens": 500
```

Restart Ollama and `START.bat`

### Enable Debugging

In `personality/controls.py`:
```python
LOG_TOOL_EXECUTION = True
LOG_PROMPT_CONSTRUCTION = True
DEBUG_MODE = True
```

Restart `START.bat` and watch console for detailed output

---

## Configuration Precedence

Settings are applied in this order (later overrides earlier):

1. **Built-in defaults** (lowest priority)
2. **config.json**
3. **.env** (Ollama settings only)
4. **bot_info.py**
5. **Runtime overrides** (if any)

Example: If you set temperature in both `config.json` and as runtime parameter, runtime wins.

---

## Resetting to Defaults

### Reset Single File

```bash
# Delete and let app recreate with defaults
del config.json
del .env

# Or rename and edit manually
ren config.json config.json.bak
```

### Full Reset

```bash
cd C:\Users\beren\Anna_AI

# Backup custom personality if you have one
copy personality\bot_info.py personality\bot_info.py.bak

# Remove all config
del config.json
del .env
del personality\bot_info.py

# Restart to regenerate defaults
START.bat
```

---

## Testing Configuration Changes

After changing configuration:

1. **For .env changes**: Restart Ollama
   ```bash
   net stop ollama && net start ollama
   ```

2. **For bot_info.py/config.json**: Restart agent
   ```bash
   # Close START.bat, then run it again
   ```

3. **Verify changes**:
   ```bash
   # Run startup-check.bat to validate
   startup-check.bat
   ```

---

## Support

- **Questions?** Check `QUICK_START.md` or `DEVELOPMENT.md`
- **Problems?** Run `startup-check.bat`
- **Troubleshooting?** See `DEVELOPMENT.md` → Troubleshooting section

---

**Last Updated**: 2026-02-16  
**Version**: 1.0
