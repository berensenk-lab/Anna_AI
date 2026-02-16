# Anna_AI Development & Troubleshooting Guide

## Quick Navigation

- **Getting started?** → See `QUICK_START.md`
- **Configuring agent?** → See `CONFIG_GUIDE.md`
- **Something broken?** → Jump to [Troubleshooting](#troubleshooting)
- **First time setup?** → See [Initial Setup](#initial-setup)

---

## Initial Setup

### Step 1: Validate Environment

```bash
cd C:\Users\beren\Anna_AI
startup-check.bat
```

Expected output: All checks pass (green [OK] marks)

### Step 2: Create Virtual Environment

```bash
py -3.11 -m venv venv
```

**Why Python 3.11.9?** Specific version for GPU compatibility and package stability.

### Step 3: Activate & Install

```bash
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
pip install transformers==4.38.2
```

Installation time: 10-20 minutes

### Step 4: Download Models

```bash
ollama pull gemma3:12b-it-q4_K_M
ollama pull nomic-embed-text:latest
```

Model sizes:
- gemma3: ~7GB
- nomic-embed-text: ~275MB

### Step 5: Configure

Edit `personality/bot_info.py`:

```python
agentname = "Anna"
username = "Sir"
thoughtmodel = "gemma3:12b-it-q4_K_M"
responsemodel = "gemma3:12b-it-q4_K_M"
vb_cable_name = "CABLE Input"
```

### Step 6: Start

```bash
# Terminal 1
ollama serve

# Terminal 2
cd C:\Users\beren\Anna_AI
START.bat
```

---

## Configuration Guide

### bot_info.py - Agent Personality

```python
# Identity
agentname = "Anna"          # Agent name (shown in messages)
username = "Sir"            # How agent addresses user
game_username = "Player"    # In-game reference

# Models (must match ollama list output)
thoughtmodel = "gemma3:12b-it-q4_K_M"       # For internal reasoning
responsemodel = "gemma3:12b-it-q4_K_M"      # For user responses
toolmodel = "gemma3:12b-it-q4_K_M"          # For function calls
actionmodel = "gemma3:12b-it-q4_K_M"        # For game actions
visionmodel = "gemma3:12b-it-q4_K_M"        # For image analysis
embedmodel = "nomic-embed-text:latest"      # For embeddings

# Voice
voiceIndex = 1              # 0-9 for different voices

# Audio
vb_cable_name = "CABLE Input"               # Must match Windows device exactly

# Multi-agent (unique per agent)
group_chat_port = 54321     # 54322, 54323 for additional agents
```

### config.json - Application Settings

```json
{
  "ollama": {
    "endpoint": "http://localhost:11434",   # Ollama server
    "temperature": 0.85,                     # Creativity (0-1)
    "max_tokens": 1000,                      # Response length
    "num_ctx": 3000                          # Context window
  },
  "bot": {
    "name": "Anna",
    "username": "Master"
  },
  "warudo": {
    "websocket_url": "ws://127.0.0.1:19190",
    "enabled": true,
    "auto_connect": true
  }
}
```

### .env - Ollama Server Optimization

```bash
# Performance
OLLAMA_NUM_PARALLEL=1                       # Single request processing
OLLAMA_CONTEXT_LENGTH=8192                  # Context window size
OLLAMA_FLASH_ATTENTION=true                 # Fast attention computation
OLLAMA_KEEP_ALIVE=24h                       # Keep models loaded
OLLAMA_MAX_LOADED_MODELS=2                  # Load multiple models

# GPU
CUDA_VISIBLE_DEVICES=0                      # Use first GPU

# API
OLLAMA_HOST=0.0.0.0:11434                   # Listen on all interfaces
OLLAMA_ORIGINS=*                            # Allow all API origins
```

**For 8GB VRAM (lower-end GPU):**

```bash
OLLAMA_CONTEXT_LENGTH=4096
OLLAMA_GPU_OVERHEAD=512
OLLAMA_MAX_LOADED_MODELS=1
```

**For 16GB+ VRAM (high-end GPU):**

```bash
OLLAMA_CONTEXT_LENGTH=16384
OLLAMA_GPU_OVERHEAD=2048
OLLAMA_MAX_LOADED_MODELS=3
```

### controls.py - Feature Toggles

```python
# Core features
ENABLE_CONTINUOUS_THINKING = True
AUTO_RESPOND = False
USE_STREAMING = True

# Memory
USE_BASE_MEMORY = True
USE_LONG_MEMORY = True
USE_SHORT_MEMORY = True
SAVE_MEMORY = True
MEMORY_LENGTH = 25

# Avatar
AVATAR_SPEECH = True
USE_CUSTOM_VOICE = True

# Audio
VOICE_VOLUME = 1.0
SOUND_EFFECT_VOLUME = 1.0

# Debugging
LOG_TOOL_EXECUTION = False
LOG_PROMPT_CONSTRUCTION = False
```

---

## File Structure

```
C:\Users\beren\Anna_AI\
│
├── START.bat                    ← Main startup script
├── startup-check.bat            ← Validation script
├── minecraft_bot_start.bat      ← Minecraft integration
│
├── QUICK_START.md              ← You are here →
├── CONFIG_GUIDE.md             ← Configuration options
├── DEVELOPMENT.md              ← This file
│
├── requirements.txt            ← Python dependencies
├── .env.example                ← Environment template
├── .env                        ← Environment (create from .env.example)
│
├── personality/
│   ├── bot_info.py            ← Agent configuration (EDIT THIS)
│   ├── controls.py            ← Feature toggles (optional)
│   ├── avatar/                ← VRM avatars for Warudo
│   ├── base_memory/           ← Personality training data
│   └── voice/                 ← Voice samples
│
├── BASE/
│   ├── interface/
│   │   └── gui_interface.py   ← Main GUI entry point
│   ├── tools/                 ← Tool integrations
│   ├── logs/                  ← Application logs
│   └── ...
│
├── AI_Agent_Tools/            ← Optional tools (clone separately)
├── documentation/             ← Project documentation
│
└── venv/                       ← Virtual environment (created by you)
```

**What to Edit:**
- ✅ `personality/bot_info.py` - Agent settings
- ✅ `config.json` - Ollama settings
- ✅ `.env` - Performance tuning
- ❌ Don't edit other files unless you know what you're doing

---

## Running Anna_AI

### Standard Start

```bash
# Terminal 1: Ollama server
cd C:\Users\beren\Anna_AI
ollama serve

# Terminal 2: Anna AI (wait 5 seconds for Ollama to start)
cd C:\Users\beren\Anna_AI
START.bat
```

### With Minecraft

```bash
# Terminal 1
ollama serve

# Terminal 2
cd C:\Users\beren\Anna_AI
minecraft_bot_start.bat
```

### Troubleshooting Run

```bash
# First, validate setup
startup-check.bat

# If validation passes, start normally
START.bat
```

---

## Troubleshooting

### Startup Issues

#### "Virtual environment not found"

**Problem**: `startup-check.bat` shows `[ERROR] Virtual environment not found`

**Solution**:

```bash
cd C:\Users\beren\Anna_AI
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Prevention**: Don't delete `venv/` directory

---

#### "Ollama API not responding"

**Problem**: `startup-check.bat` shows `[WARN] Ollama API not responding`

**Solution 1: Start Ollama service**

```bash
# In a separate terminal
ollama serve
```

Or:

```bash
# Via Windows Services
net start ollama
```

**Solution 2: Check if already running**

```bash
tasklist | findstr ollama
```

If found, Ollama is running. Wait 10 seconds for startup to complete.

**Solution 3: Verify endpoint**

Check `config.json`:

```json
{
  "ollama": {
    "endpoint": "http://localhost:11434"
  }
}
```

Should be exactly `http://localhost:11434` (not `ollama:11434` or other variants)

---

#### "Python module not found"

**Problem**: GUI fails to start with `ModuleNotFoundError`

**Solution**:

```bash
cd C:\Users\beren\Anna_AI
venv\Scripts\activate
pip install -r requirements.txt
```

Then restart `START.bat`

---

### Runtime Issues

#### "Agent responds slowly"

**Problem**: Takes >10 seconds to respond

**Diagnosis**:

```bash
# Check Ollama logs
type %USERPROFILE%\.ollama\logs\server.log | tail -20

# Check GPU usage
nvidia-smi
```

**Quick fixes**:

1. **Reduce context window** (in `.env`):

   ```bash
   OLLAMA_CONTEXT_LENGTH=4096  # Reduce from 8192
   ```

2. **Close other applications** using GPU

3. **Check available VRAM**:

   ```bash
   nvidia-smi
   ```

   Models need space for context. If VRAM is full, reduce context window.

4. **Use smaller model** (optional):

   ```bash
   # Download smaller model
   ollama pull gemma2:6b-it-q4_K_M
   
   # Edit bot_info.py
   thoughtmodel = "gemma2:6b-it-q4_K_M"
   responsemodel = "gemma2:6b-it-q4_K_M"
   ```

---

#### "No voice output"

**Problem**: Agent doesn't speak, no audio from virtual cable

**Checklist**:

```bash
# 1. Check VB-Cable installation
# Windows Settings → Sound → Check for "CABLE Input/Output"

# 2. Verify bot_info.py
# Open personality/bot_info.py
# Ensure: vb_cable_name = "CABLE Input"

# 3. Test audio system
# Windows Settings → Sound → Sound settings
# Play a test sound
```

**Solution**:

1. Install VB-Cable from https://vb-audio.com/Cable/
2. Restart computer after installation
3. Verify device name matches in `bot_info.py`
4. Restart `START.bat`

---

#### "Agent disconnects from Ollama"

**Problem**: Agent starts, then connection error after a few interactions

**Diagnosis**:

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Check Ollama logs
type %USERPROFILE%\.ollama\logs\server.log | findstr "error"
```

**Solutions**:

1. **Increase keep-alive** (in `.env`):

   ```bash
   OLLAMA_KEEP_ALIVE=24h  # Keep models loaded longer
   ```

2. **Restart Ollama**:

   ```bash
   net stop ollama
   net start ollama
   ```

3. **Increase Ollama timeout** (in `config.json`):

   ```json
   {
     "ollama": {
       "request_timeout": 300
     }
   }
   ```

---

### Configuration Issues

#### "Agent uses wrong model"

**Problem**: Configured one model, but agent uses different one

**Solution**:

1. Open `personality/bot_info.py`
2. Verify model names exactly match `ollama list` output:

   ```bash
   ollama list
   ```

   Output example:

   ```
   NAME                            SIZE
   gemma3:12b-it-q4_K_M           7.2 GB
   nomic-embed-text:latest         275 MB
   ```

3. Update `bot_info.py` with exact names:

   ```python
   thoughtmodel = "gemma3:12b-it-q4_K_M"
   responsemodel = "gemma3:12b-it-q4_K_M"
   ```

4. Save and restart `START.bat`

---

#### "Wrong agent name displayed"

**Problem**: Agent shows as "TestAgent" but configured as "Anna"

**Solution**:

1. Open `personality/bot_info.py`
2. Update:

   ```python
   agentname = "Anna"
   ```

3. Also check `config.json`:

   ```json
   {
     "bot": {
       "name": "Anna"
     }
   }
   ```

4. Save and restart `START.bat`

---

#### "Settings not applying"

**Problem**: Changed `.env` but no effect

**Solution**:

Ollama doesn't reload `.env` while running. Must restart:

```bash
# Stop Ollama service
net stop ollama

# Start Ollama service
net start ollama

# Or restart the process
taskkill /IM ollama.exe /F
ollama serve
```

Then restart `START.bat`

---

### GPU & Hardware Issues

#### "CUDA not available"

**Problem**: `startup-check.bat` shows CUDA: Not available

**Diagnosis**:

```bash
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

**Solutions**:

1. **Update GPU drivers**:
   - Go to: https://www.nvidia.com/Download/index.aspx
   - Download latest driver for your GPU
   - Minimum version: 566.03

2. **Reinstall PyTorch with CUDA**:

   ```bash
   venv\Scripts\activate
   pip uninstall torch torchvision torchaudio
   pip cache purge
   pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu126
   ```

3. **Check PATH includes CUDA**:

   ```bash
   echo %PATH% | findstr CUDA
   ```

   Should show CUDA bin directory. If not, add:

   ```bash
   setx PATH "%PATH%;C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64"
   ```

---

#### "Out of memory errors"

**Problem**: VRAM exhausted, model crashes

**Quick fixes**:

```bash
# Reduce context window (.env)
OLLAMA_CONTEXT_LENGTH=4096

# Restart Ollama
net stop ollama
net start ollama
```

**Check VRAM usage**:

```bash
nvidia-smi
```

Look for "Memory-Usage" column.

**Permanent fix** (if model > VRAM):

Use smaller model:

```bash
ollama pull gemma2:6b-it-q4_K_M
```

Update `bot_info.py` to use smaller model.

---

### Multi-Agent Setup

#### Running multiple agents simultaneously

**Configuration**:

Each agent needs:
- Unique `agentname`
- Unique `group_chat_port`
- Unique `vb_cable_name`

**Agent 1** (`C:\Users\beren\Anna_AI`):

```python
# personality/bot_info.py
agentname = "Anna"
vb_cable_name = "CABLE Input"
group_chat_port = 54321
```

**Agent 2** (separate directory, e.g., `C:\Users\beren\Anna_AI_2`):

```python
agentname = "Aria"
vb_cable_name = "CABLE-A Input"
group_chat_port = 54322
```

**Requirements**:
- Install additional virtual audio cables (Tala)
- Each agent needs separate Python venv
- Each agent needs separate terminal for Ollama communication

---

## Performance Optimization

### For Speed (Faster Responses)

```bash
# .env settings
OLLAMA_NUM_PARALLEL=1
OLLAMA_CONTEXT_LENGTH=4096      # Reduce context
OLLAMA_FLASH_ATTENTION=true
OLLAMA_KEEP_ALIVE=1h             # Unload models faster

# config.json
"max_tokens": 500                # Shorter responses
"temperature": 0.3               # More focused
```

### For Quality (Better Responses)

```bash
# .env settings
OLLAMA_CONTEXT_LENGTH=8192       # Increase context
OLLAMA_KEEP_ALIVE=24h            # Keep models loaded
OLLAMA_MAX_LOADED_MODELS=2       # Load multiple models

# config.json
"max_tokens": 1000               # Longer responses
"temperature": 0.85              # More creative
```

### For Memory (Lower VRAM Usage)

```bash
# .env settings
OLLAMA_CONTEXT_LENGTH=2048
OLLAMA_GPU_OVERHEAD=256
OLLAMA_MAX_LOADED_MODELS=1

# Use smaller models
ollama pull gemma2:6b-it-q4_K_M
ollama pull phi:2.5-instruct-q4_K_M
```

---

## Logging & Debugging

### Enable Debug Logging

Edit `personality/controls.py`:

```python
LOG_TOOL_EXECUTION = True
LOG_PROMPT_CONSTRUCTION = True
LOG_RESPONSE_PROCESSING = True
LOG_SYSTEM_INFORMATION = True
```

Restart `START.bat` and watch console output for detailed logs.

### View Ollama Logs

```bash
# Windows
type %USERPROFILE%\.ollama\logs\server.log | tail -50

# Or view in text editor
notepad %USERPROFILE%\.ollama\logs\server.log
```

### Check GPU Usage While Running

```bash
# In separate terminal (while agent is running)
nvidia-smi -l 1          # Update every 1 second
```

Watch:
- **Memory-Usage** column (should match model size)
- **GPU-Util** column (should show 80-100% when processing)

---

## Common Solutions Reference

| Issue | Command |
|-------|---------|
| Validate setup | `startup-check.bat` |
| Recreate venv | `rmdir /s /q venv && py -3.11 -m venv venv` |
| Reinstall packages | `pip install -r requirements.txt` |
| Download model | `ollama pull gemma3:12b-it-q4_K_M` |
| List models | `ollama list` |
| Check Ollama | `curl http://localhost:11434/api/tags` |
| Restart Ollama | `net stop ollama && net start ollama` |
| Check GPU | `nvidia-smi` |
| Update GPU driver | https://www.nvidia.com/Download/index.aspx |

---

## When to Restart What

| Change | Restart |
|--------|---------|
| `.env` file | Ollama service (`net stop ollama && net start ollama`) |
| `config.json` | `START.bat` |
| `bot_info.py` | `START.bat` |
| `controls.py` | `START.bat` |
| GPU driver | Computer |
| Python packages | `START.bat` |

---

## Support Resources

- **Ollama Documentation**: https://github.com/ollama/ollama
- **Python Docs**: https://docs.python.org/3.11/
- **PyTorch**: https://pytorch.org/docs/
- **Project GitHub**: https://github.com/KryptykBioz/Anna_AI

---

## Still Stuck?

1. Run `startup-check.bat` - diagnoses most issues
2. Check logs: `%USERPROFILE%\.ollama\logs\server.log`
3. Review this guide's Troubleshooting section
4. Check project documentation/ folder
5. Review GitHub issues for similar problems

---

**Last Updated**: 2026-02-16  
**Version**: 1.0
