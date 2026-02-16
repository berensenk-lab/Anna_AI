# Anna_AI Quick Start Guide

## ⚡ 30-Second Start

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Anna_AI
cd C:\Users\beren\Anna_AI
START.bat
```

Agent UI will open at `http://localhost:8000` (if configured).

---

## 🔧 Full Setup (First Time Only)

### 1. Validate Your Setup

```bash
cd C:\Users\beren\Anna_AI
startup-check.bat
```

This checks:
- ✅ Virtual environment exists
- ✅ Python packages installed
- ✅ Ollama service running
- ✅ GPU/CUDA available
- ✅ Configuration files in place

### 2. Create Virtual Environment (if needed)

```bash
cd C:\Users\beren\Anna_AI
py -3.11 -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Agent

Edit `personality/bot_info.py`:

```python
agentname = "Anna"              # Agent name
username = "Sir"                # How agent addresses you
thoughtmodel = "gemma3:12b-it-q4_K_M"    # Model for thinking
responsemodel = "gemma3:12b-it-q4_K_M"   # Model for responses
vb_cable_name = "CABLE Input"   # Virtual audio cable name
```

### 4. Ensure Models Downloaded

```bash
ollama pull gemma3:12b-it-q4_K_M
ollama pull nomic-embed-text:latest
```

### 5. Start Services

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Anna_AI (wait for Ollama to start first)
cd C:\Users\beren\Anna_AI
START.bat
```

---

## 📋 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | i5-8400 | i7-12700K |
| **RAM** | 16GB | 32GB |
| **GPU** | RTX 3060 (8GB VRAM) | RTX 4070 (12GB VRAM) |
| **Disk** | 50GB SSD | 100GB SSD |
| **Python** | 3.11.9 | 3.11.9 |

---

## 🚀 Daily Workflow

### Start Anna_AI

```bash
# Terminal 1: Ollama server
ollama serve

# Terminal 2: Anna AI agent
cd C:\Users\beren\Anna_AI
START.bat
```

### Stop Anna_AI

```bash
# Close the GUI window, or press Ctrl+C in terminals
```

### Check Status

```bash
# Verify Ollama
curl http://localhost:11434/api/tags

# List models
ollama list
```

---

## ⚙️ Common Configuration Changes

### Change Agent Personality

Edit `personality/bot_info.py`:

```python
agentname = "MyAgent"
username = "MyName"
```

Restart: `START.bat`

### Change Voice

Edit `personality/bot_info.py`:

```python
voiceIndex = 2  # 0-9 for different TTS voices
```

Restart: `START.bat`

### Improve Response Speed

Edit `.env`:

```bash
OLLAMA_CONTEXT_LENGTH=4096    # Reduce from 8192
OLLAMA_NUM_PARALLEL=1
OLLAMA_KEEP_ALIVE=24h
```

Restart Ollama: `net stop ollama && net start ollama`

### Improve Response Quality

Edit `.env`:

```bash
OLLAMA_CONTEXT_LENGTH=8192    # Increase context
OLLAMA_FLASH_ATTENTION=true   # Enable optimizations
```

Restart Ollama and `START.bat`

---

## 🔧 Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| **"Ollama not found"** | Run `ollama serve` in separate terminal |
| **"Virtual env not found"** | Run `py -3.11 -m venv venv` |
| **"Module not found"** | Run `pip install -r requirements.txt` |
| **"GUI won't start"** | Run `startup-check.bat` to diagnose |
| **"Slow responses"** | Check Ollama logs, reduce context window |
| **"No audio"** | Install VB-Cable from https://vb-audio.com/Cable/ |

---

## 📚 More Information

- **Setup & Installation**: See `DEVELOPMENT.md`
- **Configuration Guide**: See `CONFIG_GUIDE.md`
- **Troubleshooting**: See `DEVELOPMENT.md` → Troubleshooting
- **Tools Integration**: See `documentation/` directory
- **GPU Optimization**: See `SETUP.md` (from project)

---

## 🎯 Next Steps

1. ✅ Run `startup-check.bat`
2. ✅ Start Ollama: `ollama serve`
3. ✅ Start agent: `START.bat`
4. ✅ Customize in `personality/bot_info.py`
5. ✅ Add tools from `AI_Agent_Tools/`

---

**Questions?** Check `DEVELOPMENT.md` or see documentation in `documentation/` directory.
