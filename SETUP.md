# AI VTUBER AGENT SETUP GUIDE

Complete installation and configuration guide for the VTuber AI Agent system with RTX 50-series GPU support.

---

## TABLE OF CONTENTS

1. [System Requirements](#system-requirements)
2. [Quick Start Guide](#quick-start-guide)
3. [Python Installation](#python-installation)
4. [Virtual Audio Cable Installation](#virtual-audio-cable-installation)
5. [Agent Installation](#agent-installation)
6. [Optional Tools and Extensions](#optional-tools-and-extensions)
7. [GPU Package Setup (RTX 50-Series)](#gpu-package-setup-rtx-50-series)
8. [Ollama Installation](#ollama-installation)
9. [Warudo Installation](#warudo-installation)
10. [VRoid Studio Installation](#vroid-studio-installation)
11. [Verification & Testing](#verification--testing)
12. [Troubleshooting](#troubleshooting)
13. [Common Issues](#common-issues)

---

## SYSTEM REQUIREMENTS

### Minimum Hardware
- **CPU**: Intel i5-8400 / AMD Ryzen 5 2600 or better
- **RAM**: 16GB DDR4 (32GB recommended for multiple agents)
- **Storage**: 50GB free SSD space
- **GPU**: NVIDIA RTX 50-series (5060 Ti, 5070, 5080, 5090)
  - RTX 40/30-series compatible with standard PyTorch installation
  - Minimum 8GB VRAM (12GB+ recommended)

### Software Requirements
- **OS**: Windows 10/11 (64-bit)
- **GPU Drivers**: NVIDIA Game Ready Driver 566.03 or newer
- **Visual Studio**: Build Tools 2019/2022 (for PyAudio compilation)
- **Virtual Audio**: VB-Audio Cable (required for TTS and lip sync)
- **Internet**: Required for initial model downloads

### Disk Space Breakdown
- Python environment: ~5GB
- PyTorch + CUDA libraries: ~10GB
- Whisper models: ~3GB per model
- XTTS models: ~2GB
- Ollama models: 5-20GB depending on selection
- Warudo: ~5GB
- VRoid Studio: ~2GB
- Virtual audio cables: ~10MB (negligible)

---

## QUICK START GUIDE

### For Experienced Users

```batch
# 1. Install Python 3.11.9

# 2. Install Virtual Audio Cables
# Download and install VB-Audio Cable from https://vb-audio.com/Cable/
# Run installer as Administrator, restart computer
# Optional: Install Tala cables for multiple agents from
# https://github.com/Essence-Platform/TalaVirtualAudioCables-Public

# 3. Clone Anna_AI from GitHub
git clone https://github.com/KryptykBioz/Anna_AI.git
cd Anna_AI

# 4. Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# 5. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install transformers==4.38.2

# 6. Copy GPU packages from working Anna_AI instance (RTX 50-series only)
# If this is your first Anna_AI install, follow full GPU setup instructions
python copy_gpu_packages.py

# 7. Configure .env file
copy .env.example .env
# Edit .env with your settings
# Ensure TTS_OUTPUT_DEVICE=CABLE Input (VB-Audio Virtual Cable)

# 8. Launch
.\gui_start.bat

# 9. Configure Warudo for lip sync
# Warudo → Settings → Audio → Lip Sync Input: CABLE Output (VB-Audio)

# 10. Optional: Load Anna.vrm into Warudo
# File location: Anna_AI\personality\avatar\Anna.vrm

# 11. Optional: Install additional tools
# Repository: https://github.com/KryptykBioz/AI_Agent_Tools
git clone https://github.com/KryptykBioz/AI_Agent_Tools.git
# Follow tool-specific installation instructions
```

Continue reading for detailed step-by-step instructions.

---

## PYTHON INSTALLATION

### Step 1: Download Python 3.11.9

**[Warning] Critical Version Requirement**: This system requires Python **3.11.9** specifically. Newer versions may have compatibility issues with TTS and transformers.

1. Visit: https://www.python.org/downloads/release/python-3119/
2. Scroll to "Files" section
3. Download: **Windows installer (64-bit)**
   - File: `python-3.11.9-amd64.exe`

### Step 2: Install Python

1. Run the installer as Administrator
2. **[Critical]** Check "Add Python 3.11 to PATH"
3. Click "Customize installation"
4. Ensure these options are selected:
   - pip
   - tcl/tk and IDLE
   - Python test suite
   - py launcher
5. Click "Next"
6. Advanced Options:
   - [x] Install for all users
   - [x] Add Python to environment variables
   - [x] Precompile standard library
   - Install location: `C:\Python311` (recommended)
7. Click "Install"

### Step 3: Verify Installation

Open Command Prompt and run:

```batch
python --version
pip --version
```

Expected output:
```
Python 3.11.9
pip 24.x.x from C:\Python311\Lib\site-packages\pip (python 3.11)
```

### Step 4: Install Visual Studio Build Tools

Required for compiling PyAudio and other C extensions.

1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run installer
3. Select "Desktop development with C++"
4. Install (requires ~7GB disk space)
5. Restart computer after installation

---

## VIRTUAL AUDIO CABLE INSTALLATION

### Why Virtual Audio Cables Are Required

Anna_AI's TTS system and Warudo lip sync animation require virtual audio cables to route audio internally without playing through physical speakers. This enables:

**Core Functionality**:
- **TTS Audio Routing**: Send generated speech to Warudo without external playback
- **Lip Sync Animation**: Warudo captures TTS audio for real-time lip movement
- **Silent Operation**: Agent speaks through avatar without disturbing you
- **Audio Isolation**: Separate agent audio from system sounds

**Multiple Agent Support**:
- Each agent requires a dedicated virtual cable
- Prevents audio conflicts between simultaneous agents
- Enables running multiple VTuber personalities at once

### Virtual Cable Overview

**VB-Audio Virtual Cable** (Primary):
- Source: https://vb-audio.com/Cable/
- Provides: 1 virtual cable (CABLE Input/Output)
- Use: First agent (Anna_AI)
- License: Donationware (free to use, donation appreciated)

**Tala Virtual Audio Cables** (Additional):
- Source: https://github.com/Essence-Platform/TalaVirtualAudioCables-Public
- Provides: 2 additional cables (CABLE-A, CABLE-B)
- Use: Second and third agents
- License: Free

**Cable Assignment**:
```
Agent 1 (Anna_AI)    → CABLE Input/Output
Agent 2 (Second AI)  → CABLE-A Input/Output
Agent 3 (Third AI)   → CABLE-B Input/Output
```

### Step 1: Install VB-Audio Virtual Cable

**Download VB-Audio Cable**:

1. Visit: https://vb-audio.com/Cable/
2. Click "Download" → "VBCABLE_Driver_Pack43.zip"
3. Extract ZIP file to temporary location
4. File size: ~2MB

**Install Primary Cable**:

```batch
# Navigate to extracted folder
cd C:\Downloads\VBCABLE_Driver_Pack43

# Run installer as Administrator
# Right-click VBCABLE_Setup_x64.exe → Run as administrator
```

**Installation Steps**:
1. Click "Install Driver"
2. Windows will show driver installation dialog
3. Click "Install" when prompted
4. Wait for "Installation successful" message
5. Click "OK"
6. **Restart computer** (required for driver activation)

**Verify Installation**:

After restart:
```
1. Right-click speaker icon in taskbar
2. Select "Open Sound settings"
3. Scroll to "Advanced sound options"
4. Click "App volume and device preferences"
5. Check available devices:
   - Should see "CABLE Input (VB-Audio Virtual Cable)"
   - Should see "CABLE Output (VB-Audio Virtual Cable)"
```

### Step 2: Install Tala Virtual Audio Cables (Optional)

**[Note]**: Only install if running multiple agents simultaneously. Single agent users can skip this step.

**Download Tala Cables**:

1. Visit: https://github.com/Essence-Platform/TalaVirtualAudioCables-Public
2. Click "Releases" (right side)
3. Download latest release: `TalaVirtualAudioCables.zip`
4. Extract to temporary location
5. File size: ~5MB

**Install Additional Cables**:

```batch
# Navigate to extracted folder
cd C:\Downloads\TalaVirtualAudioCables

# Run installer as Administrator
# Right-click Install_Cables.exe → Run as administrator
```

**Installation Steps**:
1. Installer will add CABLE-A and CABLE-B
2. Click "Install" for each cable prompt
3. Wait for completion message
4. **Restart computer** (required)

**Verify Additional Cables**:

After restart:
```
Windows Settings → Sound → Advanced sound options
Should now see:
- CABLE Input/Output (VB-Audio)
- CABLE-A Input/Output (Tala)
- CABLE-B Input/Output (Tala)
```

### Step 3: Configure Windows Audio Settings

**Set Default Devices**:

[Warning] Do NOT set virtual cables as default system devices.

```
1. Right-click speaker icon → "Open Sound settings"
2. Output device: Keep as physical speakers/headphones
3. Input device: Keep as physical microphone
4. Virtual cables will be assigned per-application
```

**Application-Specific Audio**:

Anna_AI will programmatically route audio to virtual cables. Manual configuration:

```
1. Open "App volume and device preferences"
2. Find "Anna_AI" or "python.exe" (when agent is running)
3. Output: Select "CABLE Input (VB-Audio Virtual Cable)"
4. Keep input as physical microphone
```

**Warudo Audio Input**:

Configure Warudo to receive from virtual cable:

```
1. Open Warudo
2. Settings → Audio
3. Lip Sync Input Device: "CABLE Output (VB-Audio Virtual Cable)"
4. Enable "Lip Sync"
5. Adjust sensitivity (start with 50%)
```

### Step 4: Test Virtual Cable Setup

**Test Cable Routing**:

```batch
# Activate Anna_AI environment
cd C:\Projects\Anna_AI
.\venv\Scripts\activate

# Run audio test script (if available)
python test_audio_routing.py

# Or test manually with TTS
python -c "from TTS.api import TTS; import sounddevice as sd; tts = TTS('tts_models/en/ljspeech/tacotron2-DDC'); wav = tts.tts('Testing virtual cable'); sd.play(wav, 22050, device='CABLE Input'); sd.wait()"
```

**Expected Behavior**:
- No audio plays through speakers
- Warudo's VU meter shows audio input
- Avatar's mouth moves with speech
- No errors in console

**Troubleshooting Test**:

If audio plays through speakers:
```python
# List audio devices
import sounddevice as sd
print(sd.query_devices())

# Find CABLE Input index
# Set as output device
sd.default.device = [None, CABLE_INDEX]
```

### Virtual Cable Configuration in Agent

**Agent Audio Configuration**:

Anna_AI should have virtual cable settings in config file. Check `personality/config.py` or `.env`:

```python
# Audio device configuration
AUDIO_OUTPUT_DEVICE = "CABLE Input (VB-Audio Virtual Cable)"
AUDIO_INPUT_DEVICE = None  # Use default microphone

# Alternative: Use device index
AUDIO_OUTPUT_INDEX = 5  # Find with sounddevice.query_devices()
```

**Environment Variables** (`.env`):

```env
# Virtual Cable Settings
TTS_OUTPUT_DEVICE=CABLE Input (VB-Audio Virtual Cable)
TTS_SAMPLE_RATE=22050
ENABLE_LIP_SYNC=true

# Warudo Integration
WARUDO_LIP_SYNC_SOURCE=CABLE Output (VB-Audio Virtual Cable)
```

**Manual Device Selection**:

If agent doesn't auto-detect cable:

```python
import sounddevice as sd

# List all devices
devices = sd.query_devices()
for i, device in enumerate(devices):
    print(f"{i}: {device['name']}")

# Set output to CABLE Input
cable_index = 5  # Your CABLE Input index
sd.default.device = [None, cable_index]
```

### Multiple Agent Setup

**Cable Assignment Strategy**:

```
Agent Directory          Virtual Cable              Warudo Instance
────────────────────────────────────────────────────────────────────
Anna_AI/                 CABLE Input/Output         Warudo (Port 7890)
SecondAgent_AI/          CABLE-A Input/Output       Warudo (Port 7891)
ThirdAgent_AI/           CABLE-B Input/Output       Warudo (Port 7892)
```

**Configure Each Agent**:

**Anna_AI (`.env`)**:
```env
TTS_OUTPUT_DEVICE=CABLE Input (VB-Audio Virtual Cable)
WARUDO_PORT=7890
```

**SecondAgent_AI (`.env`)**:
```env
TTS_OUTPUT_DEVICE=CABLE-A Input (Tala Virtual Cable)
WARUDO_PORT=7891
```

**ThirdAgent_AI (`.env`)**:
```env
TTS_OUTPUT_DEVICE=CABLE-B Input (Tala Virtual Cable)
WARUDO_PORT=7892
```

**Configure Each Warudo Instance**:

```
Warudo Instance 1:
- Port: 7890
- Lip Sync Input: CABLE Output (VB-Audio)
- Character: Anna.vrm

Warudo Instance 2:
- Port: 7891
- Lip Sync Input: CABLE-A Output (Tala)
- Character: SecondAgent.vrm

Warudo Instance 3:
- Port: 7892
- Lip Sync Input: CABLE-B Output (Tala)
- Character: ThirdAgent.vrm
```

**Launch Multiple Agents**:

```batch
# Terminal 1: Anna_AI
cd C:\Projects\Anna_AI
.\venv\Scripts\activate
python main.py

# Terminal 2: SecondAgent_AI
cd C:\Projects\SecondAgent_AI
.\venv\Scripts\activate
python main.py

# Terminal 3: ThirdAgent_AI
cd C:\Projects\ThirdAgent_AI
.\venv\Scripts\activate
python main.py
```

### Virtual Cable Management

**View Active Cables**:

```
Control Panel → Sound → Playback (tab)
Should show:
- CABLE Input (VB-Audio Virtual Cable)
- CABLE-A Input (Tala Virtual Cable)
- CABLE-B Input (Tala Virtual Cable)

Control Panel → Sound → Recording (tab)
Should show:
- CABLE Output (VB-Audio Virtual Cable)
- CABLE-A Output (Tala Virtual Cable)
- CABLE-B Output (Tala Virtual Cable)
```

**Disable Unused Cables**:

To reduce system overhead when not using multiple agents:

```
1. Control Panel → Sound
2. Right-click unused cable
3. Select "Disable"
4. Re-enable when needed
```

**Uninstall Cables**:

**VB-Audio Cable**:
```
1. Navigate to installation folder
2. Run VBCABLE_Setup_x64.exe as Administrator
3. Click "Remove Driver"
4. Restart computer
```

**Tala Cables**:
```
1. Control Panel → Programs → Uninstall a program
2. Find "Tala Virtual Audio Cables"
3. Click "Uninstall"
4. Restart computer
```

### Common Virtual Cable Issues

**Issue**: No audio in Warudo, avatar doesn't lip sync

**Solutions**:
1. Verify cable installation:
   ```
   Control Panel → Sound → Playback
   Ensure CABLE Input shows "Working"
   ```

2. Check agent output device:
   ```python
   import sounddevice as sd
   print(sd.query_devices())
   # Verify CABLE Input is listed
   ```

3. Verify Warudo input setting:
   ```
   Warudo → Settings → Audio → Lip Sync Input Device
   Must match agent's output cable
   ```

4. Test cable directly:
   ```
   Play audio to CABLE Input in system settings
   Should see activity in CABLE Output
   ```

**Issue**: Audio plays through speakers instead of cable

**Solution**: Force device selection in code:
```python
import sounddevice as sd

# Find CABLE Input index
devices = sd.query_devices()
cable_idx = None
for i, dev in enumerate(devices):
    if "CABLE Input" in dev['name'] and dev['max_output_channels'] > 0:
        cable_idx = i
        break

# Set as default output
sd.default.device = [None, cable_idx]
```

**Issue**: Multiple agents conflict or audio cuts out

**Solution**: Ensure each agent uses different cable:
```
Agent 1 → CABLE Input/Output
Agent 2 → CABLE-A Input/Output
Agent 3 → CABLE-B Input/Output
```

**Issue**: Crackling or distorted audio through virtual cable

**Solutions**:
1. Increase buffer size:
   ```python
   sd.default.latency = 'high'
   sd.default.blocksize = 2048
   ```

2. Match sample rates:
   ```
   Agent TTS: 22050 Hz
   Virtual Cable: 22050 Hz (set in Windows)
   Warudo Input: 22050 Hz
   ```

3. Reduce CPU load:
   - Lower Whisper model size
   - Reduce Ollama context window
   - Lower Warudo graphics quality

**Issue**: Virtual cable not detected after Windows update

**Solution**: Reinstall driver:
```
1. Uninstall current cable driver
2. Restart computer
3. Reinstall from original installer
4. Restart again
```

### Performance Considerations

**CPU Impact**:
- Each virtual cable: ~1-2% CPU overhead
- Negligible for modern CPUs
- Impact increases with number of active cables

**Latency**:
- Virtual cable latency: <10ms
- Total lip sync latency: 50-100ms (acceptable)
- Lower buffer size = less latency, higher CPU usage

**Optimization Tips**:
- Disable unused cables when not needed
- Use single cable for single agent
- Match sample rates across chain
- Increase buffer for stability over latency

### Alternative Audio Routing

**VoiceMeeter** (Advanced Users):

VoiceMeeter provides more routing options but is more complex:
- Download: https://vb-audio.com/Voicemeeter/
- Supports mixing multiple sources
- Requires manual configuration
- Recommended only for advanced setups

**Not Recommended**:
- Windows Stereo Mix (insufficient isolation)
- Third-party screen recorders (high latency)
- Hardware loopback cables (defeats purpose)

---

## AGENT INSTALLATION

### Project Source

Anna_AI is available on GitHub: **https://github.com/KryptykBioz/Anna_AI**

The repository includes:
- Complete agent framework code
- Pre-configured personality system
- Anna character avatar files (`personality/avatar/`)
- Warudo integration blueprints
- Example configurations and scripts

**Optional Tools Repository**: https://github.com/KryptykBioz/AI_Agent_Tools
- Additional functionality and integrations
- Extended features and utilities
- Community-contributed extensions
- Installed separately (see [Optional Tools and Extensions](#optional-tools-and-extensions))

### Step 1: Obtain Agent Files

**Method 1: Download ZIP** (Recommended)
```batch
# Download ZIP from GitHub
# https://github.com/KryptykBioz/Anna_AI/archive/refs/heads/main.zip

# Extract to C:\Projects\Anna_AI\
# Verify directory structure is intact
```

**Method 2: Git Clone**
```batch
# Navigate to your projects directory
cd C:\Projects

# Clone from GitHub
git clone https://github.com/KryptykBioz/Anna_AI.git
cd Anna_AI

# Verify avatar files are present
dir personality\avatar
# Should show: anna_model.vroid, Anna.vrm, and JSON files
```

### Step 2: Create Virtual Environment

```batch
# Ensure you're in the agent directory
cd Anna_AI

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Your prompt should now show (venv)
```

**[Note]**: Always activate the virtual environment before running the agent (automatic with START.bat) or installing packages.

### Step 3: Upgrade Pip

```batch
python -m pip install --upgrade pip
```

### Step 4: Install Base Dependencies

```batch
# Install all requirements except GPU packages
pip install -r requirements.txt
```

This installs:
- Core AI/ML packages (numpy, pillow)
- Audio processing (sounddevice, soundfile, pyttsx3)
- Speech recognition (faster-whisper, vosk)
- TTS system (TTS package)
- Discord integration (discord.py)
- Web utilities (requests, beautifulsoup4)
- GUI components (pygame, PyAutoGUI)
- Utilities (colorama, python-dotenv)

**Installation time**: 5-10 minutes depending on internet speed.

**Optional Tools**: Additional functionality (screen capture, automation, etc.) can be installed from the AI_Agent_Tools repository. See [Optional Tools and Extensions](#optional-tools-and-extensions) for details.

### Step 5: Install Locked Transformers Version

```batch
# [Critical] Install specific transformers version
pip install transformers==4.38.2
```

**[Warning]**: Do NOT upgrade transformers beyond 4.38.2. Newer versions break XTTS compatibility due to BeamSearchScorer API changes.

### Step 6: Configure Environment Variables

```batch
# Copy example environment file
copy .env.example .env

# Edit .env with your preferred text editor
notepad .env
```

Required configurations in `.env`:
```env
# Discord Bot Token (if using Discord integration)
DISCORD_TOKEN=your_discord_bot_token_here

# API Keys (if using external services)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Agent Settings
AGENT_NAME=Anna
VOICE_MODEL=tts_models/multilingual/multi-dataset/xtts_v2
WHISPER_MODEL=medium

# Virtual Audio Cable (REQUIRED for lip sync)
TTS_OUTPUT_DEVICE=CABLE Input (VB-Audio Virtual Cable)
ENABLE_LIP_SYNC=true
TTS_SAMPLE_RATE=22050

# GPU Settings
CUDA_VISIBLE_DEVICES=0
TORCH_CUDA_ARCH_LIST=12.0

# Performance
MAX_MEMORY_GB=8
ENABLE_GPU=true
```

### Understanding Anna's Avatar Files

Anna_AI includes pre-configured avatar assets in `personality\avatar\`:

**Character Files**:
```
anna_model.vroid
├── Purpose: Editable VRoid Studio project
├── Use: Open in VRoid Studio to modify appearance
├── Contains: Hair, face, outfit, expression configurations
└── Size: ~50-100MB

Anna.vrm
├── Purpose: Exported VRM ready for Warudo
├── Use: Import directly into Warudo (no modification needed)
├── Contains: Optimized 3D model with expressions and physics
└── Size: ~20-50MB
```

**Warudo Configuration Files** (if included):
```
warudo_blueprint.json
├── Purpose: Scene logic and behavior programming
├── Use: Import into Warudo Blueprints tab
├── Contains: Animation triggers, expression mappings, event handlers
└── Configuration: Pre-set for Anna's personality

warudo_animations.json
├── Purpose: Animation sequences and timings
├── Use: Import into Character Animations tab
├── Contains: Idle behaviors, gestures, reaction animations
└── Optimization: Tuned for natural movement
```

**File Workflow**:
```
1. Want to modify appearance?
   → Open anna_model.vroid in VRoid Studio
   → Make changes
   → Export new VRM
   → Import to Warudo

2. Want to use existing avatar?
   → Import Anna.vrm directly to Warudo
   → Skip VRoid Studio entirely

3. Want optimized animations?
   → Load warudo_blueprint.json in Warudo
   → Load warudo_animations.json in Warudo
   → Animations sync with agent code
```

**Integration with Agent Code**:
The Anna_AI agent references these configurations:
- Expression IDs match Anna.vrm blend shapes
- Animation names match warudo_animations.json
- Blueprint triggers match agent event system
- All pre-tested and calibrated together

---

## OPTIONAL TOOLS AND EXTENSIONS

### AI Agent Tools Repository

Anna_AI supports optional tools and extensions that enhance functionality. These are maintained in a separate repository to keep the base installation lightweight.

**Repository**: https://github.com/KryptykBioz/AI_Agent_Tools

### What's Included

The AI Agent Tools repository contains:
Modular tool packages for additional API connectors and service integrations

### Installation

**Step 1: Clone Tools Repository**

```batch
# Navigate to your projects directory
cd C:\Projects

# Clone the tools repository
git clone https://github.com/KryptykBioz/AI_Agent_Tools.git

# Verify download
dir AI_Agent_Tools
```

**Step 2: Review Available Tools**

```batch
cd AI_Agent_Tools

# List available tools
dir /b

# Read the tools README
type README.md
```

### Tool Integration

**Method 1: Direct Import**

Copy tool modules to Anna_AI's tools/installed directory:
```batch
# Example: Copy screen capture tool
xcopy "C:\Projects\AI_Agent_Tools\screen_capture" "C:\Projects\Anna_AI\BASE\tools\installed\screen_capture" /E /I /H /Y
```

### Tool Configuration

Most tool-specific configuration is located in their internal config and information files


### Updating Tools

Keep tools repository updated separately from Anna_AI:

```batch
cd C:\Projects\AI_Agent_Tools
git pull origin main

# Review changelog
type CHANGELOG.md

# Update dependencies if needed
pip install -r requirements.txt --upgrade
```

### Tool Dependencies

Some tools may require additional system packages

### Tool Development

To create custom tools:

1. **Fork AI_Agent_Tools repository**
2. **Create tool directory**:
   ```
   AI_Agent_Tools/
   └── my_custom_tool/
       ├── __init__.py
       ├── tool_module.py
       ├── requirements.txt
       └── README.md
   ```

3. **Document tool**:
   - Purpose and functionality
   - Installation instructions
   - Dependencies
   - Configuration options
   - Usage examples

4. **Test with Anna_AI**:
   ```batch
   cd C:\Projects\Anna_AI
   .\venv\Scripts\activate
   python test_custom_tool.py
   ```

5. **Submit pull request** to share with community

### Tool Support

For tool-specific issues:
- Check tool's README.md
- Review AI_Agent_Tools repository issues
- Ensure tool version compatibility with Anna_AI
- Verify all dependencies installed

For Anna_AI integration issues:
- Check Anna_AI repository issues
- Verify tool configuration in .env
- Test tool in isolation before integration

---

## GPU PACKAGE SETUP (RTX 50-SERIES)

### Understanding the RTX 50-Series Challenge

**Why can't we use pip for GPU packages?**

The NVIDIA RTX 50-series (Blackwell architecture, compute capability sm_120) was released after most PyPI packages were built. Standard PyTorch wheels from PyPI only support up to sm_89 (RTX 40-series). Installing via pip will give you:
- CPU-only PyTorch, OR
- GPU build without sm_120 support (won't utilize your 50-series GPU)

**Solutions**:
1. **For derivative agents**: Copy pre-built packages from working Anna_AI installation
2. **For first Anna_AI installation**: 
   - Use Method 2 (Manual Copy) from another working 50-series system
   - OR build PyTorch from source with sm_120 support
   - OR use standard PyPI packages (RTX 40-series and older will work)

**[Important]**: If this is your first Anna_AI installation on an RTX 50-series GPU and you don't have access to another working installation, you'll need to either:
- Build PyTorch from source with CUDA 12.8+ and sm_120 support
- Use a pre-built PyTorch wheel from community sources
- Temporarily use CPU mode and upgrade GPU packages later

For RTX 40/30-series users, skip to "RTX 40/30-Series Users" section below.

### What Packages Need Copying?

**Critical GPU Packages**:
1. `torch/` and `torch-*.dist-info/` - Custom PyTorch with sm_120 support
2. `torchaudio/` and `torchaudio-*.dist-info/` - Audio processing on GPU
3. `torchvision/` and `torchvision-*.dist-info/` - Vision models support
4. `ctranslate2/` and `ctranslate2-*.dist-info/` - **[Critical]** Enables Whisper int8 GPU inference
5. All `nvidia-*` folders - CUDA runtime libraries (cublas, cudnn, etc.)
6. `pyaudio/` and `PyAudio-*.dist-info/` - Custom Windows wheel (if available)

### Method 1: Automated Copy Script (Recommended)

**[Note]**: The `copy_gpu_packages.py` script may be included in Anna_AI repository. If not present, use Method 2 (Manual Copy) below.

```batch
# Verify script exists
dir copy_gpu_packages.py

# If present, ensure source Anna_AI venv is activated and working
cd C:\Projects\Anna_AI
.\venv\Scripts\activate
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
# Should print: CUDA: True
deactivate

# For new agent installations based on Anna_AI:
# If creating a derivative agent, copy GPU packages from working Anna_AI
# Switch to new agent and run copy script
cd C:\Projects\YourNewAgent_AI
.\venv\Scripts\activate
python path\to\copy_gpu_packages.py

# For first-time Anna_AI installation:
# Follow Method 2 (Manual Copy) or build from source
```

The script will:
1. Locate source site-packages directory
2. Identify all GPU-related packages
3. Copy them to target venv
4. Verify integrity
5. Test CUDA availability

### Method 2: Manual Copy

If the script fails or is unavailable:

```batch
# Define paths (adjust to your installation)
set SOURCE=C:\Projects\Anna_AI\venv\Lib\site-packages
set DEST=C:\Projects\YourAgent_AI\venv\Lib\site-packages

# Copy PyTorch packages
xcopy "%SOURCE%\torch" "%DEST%\torch" /E /I /H /Y
xcopy "%SOURCE%\torch-*.dist-info" "%DEST%\" /E /I /H /Y

xcopy "%SOURCE%\torchaudio" "%DEST%\torchaudio" /E /I /H /Y
xcopy "%SOURCE%\torchaudio-*.dist-info" "%DEST%\" /E /I /H /Y

xcopy "%SOURCE%\torchvision" "%DEST%\torchvision" /E /I /H /Y
xcopy "%SOURCE%\torchvision-*.dist-info" "%DEST%\" /E /I /H /Y

# Copy CTranslate2 (CRITICAL for Whisper)
xcopy "%SOURCE%\ctranslate2" "%DEST%\ctranslate2" /E /I /H /Y
xcopy "%SOURCE%\ctranslate2-*.dist-info" "%DEST%\" /E /I /H /Y

# Copy ALL NVIDIA packages
for /d %i in ("%SOURCE%\nvidia*") do xcopy "%i" "%DEST%\%~nxi" /E /I /H /Y

# Copy PyAudio if custom-built
xcopy "%SOURCE%\pyaudio" "%DEST%\pyaudio" /E /I /H /Y
xcopy "%SOURCE%\PyAudio-*.dist-info" "%DEST%\" /E /I /H /Y
```

**[Note]**: This copies ~8-10GB of data. Ensure you have sufficient disk space.

### Verification Steps

After copying, verify GPU support:

```batch
# Test PyTorch CUDA
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}'); print(f'GPU name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

Expected output:
```
PyTorch version: 2.10.0a0+gitd4493c5
CUDA available: True
CUDA version: 12.8
GPU name: NVIDIA GeForce RTX 5060 Ti
```

```batch
# Test CTranslate2 (critical for Whisper)
python -c "from faster_whisper import WhisperModel; print('CTranslate2: OK')"
```

Expected output:
```
CTranslate2: OK
```

```batch
# Test TorchAudio
python -c "import torchaudio; print(f'TorchAudio version: {torchaudio.__version__}')"
```

If any test fails, see [Troubleshooting](#troubleshooting) section.

### RTX 40/30-Series Users

If you have RTX 40-series or earlier, you can use standard PyPI packages:

```batch
# Install PyTorch with CUDA 12.1 support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# CTranslate2 should work from PyPI
pip install ctranslate2

# Verify
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

---

## OLLAMA INSTALLATION

Ollama provides local LLM inference for advanced reasoning and conversational capabilities.

### Step 1: Download Ollama

1. Visit: https://ollama.com/download
2. Download "Ollama for Windows"
3. File size: ~500MB

### Step 2: Install Ollama

1. Run `OllamaSetup.exe` as Administrator
2. Follow installation wizard
3. Default installation path: `C:\Users\YourUsername\AppData\Local\Programs\Ollama`
4. Ollama will start automatically after installation

### Step 3: Verify Ollama Service

```batch
# Check if Ollama is running
ollama --version
```

Expected output:
```
ollama version 0.x.x
```

### Step 4: Download Models

Recommended models for VTuber agents:

**For General Use (8GB+ VRAM)**:
```batch
# Llama 3.1 8B - Excellent balance of speed and quality
ollama pull llama3.1:8b

# Mistral 7B - Fast inference, good for real-time responses
ollama pull mistral:7b

# Phi-3 Mini - Lightweight option for lower VRAM
ollama pull phi3:mini
```

**For High-End GPUs (16GB+ VRAM)**:
```batch
# Llama 3.1 70B - Best quality for roleplay and reasoning
ollama pull llama3.1:70b

# Mixtral 8x7B - Excellent for complex tasks
ollama pull mixtral:8x7b
```

**Model Storage**:
- Default location: `C:\Users\YourUsername\.ollama\models`
- Each model: 4-40GB depending on size

### Step 5: Test Model

```batch
# Interactive test
ollama run llama3.1:8b

# Type a message to test
> Hello! How are you?

# Exit with /bye
> /bye
```

### Step 6: Configure Agent to Use Ollama

Edit your agent's configuration file (e.g., `personality/config.py`):

```python
OLLAMA_CONFIG = {
    "enabled": True,
    "base_url": "http://localhost:11434",
    "model": "llama3.1:8b",
    "temperature": 0.8,
    "max_tokens": 2048,
    "stream": True
}
```

### Ollama Management Commands

```batch
# List installed models
ollama list

# Remove a model
ollama rm modelname:tag

# Update Ollama
# Download latest installer and reinstall

# Stop Ollama service
net stop ollama

# Start Ollama service
net start ollama

# View logs
type "%USERPROFILE%\.ollama\logs\server.log"
```

### Ollama API Usage in Agent

Example integration code:

```python
import requests
import json

def query_ollama(prompt, model="llama3.1:8b"):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.8,
            "top_p": 0.9,
            "max_tokens": 2048
        }
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Ollama error: {response.status_code}")
```

### Performance Optimization

**For RTX 50-Series**:
```batch
# Enable flash attention (if supported by model)
ollama run llama3.1:8b --flash-attention

# Adjust context window
ollama run llama3.1:8b --ctx-size 8192

# Set GPU layers (offload entire model to GPU)
ollama run llama3.1:8b --gpu-layers 999
```

**Memory Management**:
- Models load on first use and stay in VRAM
- Automatically unload after 5 minutes of inactivity
- Force unload: `ollama stop modelname:tag`

---

## WARUDO INSTALLATION

Warudo is a professional VTuber application for real-time character animation and streaming.

### Step 1: System Requirements Check

**Minimum**:
- GPU: NVIDIA GTX 1060 6GB / AMD RX 580 8GB
- RAM: 8GB
- CPU: Intel i5-6500 / AMD Ryzen 5 1600

**Recommended**:
- GPU: NVIDIA RTX 3060 12GB or better
- RAM: 16GB
- CPU: Intel i7-9700K / AMD Ryzen 7 3700X

### Step 2: Download Warudo

**Official Release**:
1. Visit: https://warudo.app/
2. Click "Download"
3. Choose "Windows" version
4. File size: ~2-3GB

**Steam Version** (Alternative):
1. Open Steam
2. Search "Warudo"
3. Free to download

### Step 3: Install Warudo

**Standalone Installer**:
1. Run `WarudoSetup.exe` as Administrator
2. Choose installation directory (default: `C:\Program Files\Warudo`)
3. Complete installation (~5GB disk space required)
4. Launch Warudo from Desktop shortcut

**Steam Version**:
1. Install through Steam library
2. Launch from Steam

### Step 4: Initial Setup

1. **First Launch**:
   - Allow firewall access for network features
   - Choose graphics quality preset (Ultra for RTX 50-series)
   - Set resolution (1920x1080 recommended)

2. **Create Profile**:
   - Click "New Scene"
   - Name your project (e.g., "Anna_Stream")

3. **Import Anna's Character**:
   
   **Method 1: Use Pre-Configured Anna.vrm** (Recommended)
   ```
   - Click "Add Asset" → "Character"
   - Click "Import VRM"
   - Navigate to: C:\Projects\Anna_AI\personality\avatar\
   - Select "Anna.vrm"
   - Click "Open"
   - Character loads instantly with all settings
   ```

   **Method 2: Import Custom Character**
   ```
   - Click "Add Asset" → "Character"
   - Choose source:
     - VRM file (from VRoid Studio export)
     - Built-in sample characters
     - Imported FBX/Unity character
   ```

### Step 4.5: Load Anna's Warudo Configuration (Optional)

Anna_AI includes pre-configured Warudo files for optimal performance:

**Blueprint File** (Scene Logic):
```
Location: Anna_AI\personality\avatar\warudo_blueprint.json
Purpose: Pre-configured scene behaviors, animations, triggers

To Load:
1. In Warudo, click "Blueprints" tab
2. Click "Import Blueprint"
3. Navigate to: C:\Projects\Anna_AI\personality\avatar\
4. Select "warudo_blueprint.json"
5. Click "Open"
6. Blueprint loads with:
   - Animation triggers
   - Expression mappings
   - Gesture controls
   - Event handlers
```

**Animation Profile** (Movement Settings):
```
Location: Anna_AI\personality\avatar\warudo_animations.json
Purpose: Custom animation sequences and idle behaviors

To Load:
1. In Warudo, select Anna character
2. Click "Animations" tab
3. Click "Import Profile"
4. Navigate to: C:\Projects\Anna_AI\personality\avatar\
5. Select "warudo_animations.json"
6. Animations load:
   - Idle variations
   - Gesture library
   - Transition timings
   - Reaction animations
```

**Configuration Benefits**:
- Optimized for Anna's personality
- Pre-tested animation sequences
- Calibrated expression timings
- Tested with Anna_AI agent code

**Manual Setup** (if JSON files not present):
- Continue to Step 5 for manual configuration

### Step 5: Configure Tracking

**Audio Input for Lip Sync** (REQUIRED):

Before configuring face tracking, set up audio input from virtual cable:

1. Go to Warudo → "Settings" → "Audio"
2. Configure:
   ```
   Lip Sync Enabled: ✓ Check
   Lip Sync Input Device: CABLE Output (VB-Audio Virtual Cable)
   Sensitivity: 50% (adjust as needed)
   Smoothing: 0.3 (adjust for natural movement)
   ```
3. Test:
   - Run Anna_AI agent
   - Agent speaks through TTS
   - Warudo's audio VU meter shows activity
   - Avatar's mouth moves with speech

**Troubleshooting Audio**:
- No VU meter activity → Check cable installation
- Avatar mouth doesn't move → Increase sensitivity
- Jittery movement → Increase smoothing
- Wrong audio source → Verify cable selection matches agent output

**Face Tracking**:
1. Go to "Character" → "Face Tracking"
2. Choose tracking method:
   - **Webcam**: Standard webcam tracking
   - **iPhone/iPad**: ARKit face tracking (requires Warudo Link app)
   - **Media Pipe**: CPU-based tracking (no special hardware)
3. Calibrate tracking:
   - Center face in camera
   - Click "Calibrate"
   - Make various expressions to train

**Body Tracking** (Optional):
1. Options:
   - **Leap Motion**: Hand tracking controller
   - **Perception Neuron**: Full-body mocap suit
   - **Keyboard/Mouse**: Manual animation triggers
2. Connect device and calibrate in settings

### Step 6: Scene Setup

**Basic Scene Components**:
1. **Camera**:
   - Add → "Camera"
   - Position for desired framing
   - Set FOV (40-60 typical)

2. **Lighting**:
   - Add → "Light" → "Directional Light"
   - Adjust intensity and color
   - Add rim lighting for depth

3. **Background**:
   - Add → "Environment" → "Image/Video"
   - Or use built-in sky boxes
   - Green screen option for OBS chroma key

### Step 7: Integrate with Agent

**Pre-Configured Integration**:

If using Anna's included avatar files and Warudo configuration, the agent code in `Anna_AI\BASE\` is already configured to work with:
- Expression IDs from Anna.vrm
- Animation names from warudo_animations.json
- Blueprint triggers from warudo_blueprint.json

**WebSocket Connection**:

Warudo supports external control via WebSocket API.

1. Enable API in Warudo:
   - Settings → "Network" → "Enable WebSocket Server"
   - Note the port (default: 7890)
   - Set authentication key (optional)

2. Agent Integration Code:

The Anna_AI agent includes a Warudo controller module. Check the tools directory for the implementation.

### Step 8: OBS Studio Integration

For streaming your VTuber:

1. Open OBS Studio
2. Add Source → "Game Capture"
3. Select "Warudo" application
4. Configure:
   - Mode: "Capture specific window"
   - Window: "Warudo"
   - Allow Transparency: Check (if using green screen)
5. Resize and position as desired

**Performance Tips**:
- Run Warudo in "Preview Mode" for lower resource usage
- Disable shadows if experiencing lag
- Reduce texture quality for older GPUs

### Warudo Advanced Features

**Blueprints** (Visual Scripting):
- Create custom behaviors without coding
- React to chat commands
- Trigger animations on events

**Props System**:
- Add objects to scene
- Attach to character
- Animate props with timeline

**Post-Processing Effects**:
- Bloom
- Color grading
- Depth of field
- Custom shaders

---

## VROID STUDIO INSTALLATION

VRoid Studio is a free character creator for making VTuber avatars.

### Loading Anna's Pre-Configured Avatar

Anna_AI comes with pre-configured avatar files in `Anna_AI\personality\avatar\`:
- `anna_model.vroid` - Editable VRoid Studio project file
- `Anna.vrm` - Exported VRM file ready for Warudo
- Warudo blueprint and animation JSON files

**Quick Setup (Use Existing Avatar)**:
1. Skip to [Warudo Installation](#warudo-installation)
2. Import `Anna.vrm` directly into Warudo
3. Load included blueprint/animation profiles

**Custom Setup (Modify Avatar)**:
1. Install VRoid Studio (follow steps below)
2. Open `anna_model.vroid` in VRoid Studio
3. Customize appearance as desired
4. Export new VRM file
5. Import to Warudo

### Step 1: Download VRoid Studio

1. Visit: https://vroid.com/en/studio
2. Click "Download for Windows"
3. Create a Pixiv account (required)
4. Accept terms and download
5. File size: ~300MB installer

### Step 2: Install VRoid Studio

1. Run `vroid_studio_setup.exe`
2. Choose installation language
3. Accept license agreement
4. Choose installation directory (default: `C:\Program Files\VRoid Studio`)
5. Create desktop shortcut
6. Launch VRoid Studio

### Step 3: First-Time Setup

1. **Login**:
   - Sign in with Pixiv account
   - Or use Google/Twitter login

2. **Language Settings**:
   - Choose "English" (or preferred language)

3. **Project Location**:
   - Set default project save location
   - Recommended: `Documents\VRoid\Projects`

### Step 4: Creating Your First Character

**Option A: Load Anna's Pre-Made Character**

Anna_AI includes a fully configured character in `Anna_AI\personality\avatar\anna_model.vroid`.

1. **Open Existing Project**:
   - Launch VRoid Studio
   - Click "Open" (not "New")
   - Navigate to: `C:\Projects\Anna_AI\personality\avatar\`
   - Select `anna_model.vroid`
   - Click "Open"

2. **Character Loads with All Settings**:
   - Hair style and colors pre-configured
   - Face customization complete
   - Outfit designed
   - Expressions calibrated
   - Physics tuned

3. **Explore the Character**:
   - Click through tabs to see customizations
   - Test expressions in preview
   - View physics simulation

4. **Make Modifications** (Optional):
   - Change hair color: Hair tab → Color picker
   - Adjust outfit: Outfit tab → Color/Pattern
   - Modify face: Face tab → Feature adjustments
   - Add accessories: Accessories tab

5. **Save Changes**:
   - File → Save (overwrites anna_model.vroid)
   - Or File → Save As (create new variant)

**Option B: Create From Scratch**

If you want to create a completely new character:

**Quick Start Method**:
1. Click "New"
2. Choose preset:
   - **Female**: Anime-style female base
   - **Male**: Anime-style male base
   - **Customize**: Start from scratch
3. Name your character

**Character Customization Tabs**:

1. **Face**:
   - Face shape (round, oval, angular)
   - Eye shape, size, color
   - Eyebrow style and position
   - Nose and mouth shape
   - Skin tone and makeup

2. **Hair**:
   - Hairstyle presets
   - Custom hair drawing
   - Hair color and highlights
   - Procedural hair editing
   - Accessories (clips, ribbons)

3. **Body**:
   - Height and proportions
   - Muscle definition
   - Breast size (female)
   - Overall body shape

4. **Outfit**:
   - Top (shirts, jackets, dresses)
   - Bottom (pants, skirts)
   - Shoes
   - Accessories (glasses, jewelry)
   - Custom textures

5. **Texture Editing**:
   - Paint directly on model
   - Import custom textures
   - Adjust materials (glossiness, metallic)

### Step 5: Advanced Customization

**Hair Editor**:
```
1. Click "Hair" → "Edit Procedural Hair"
2. Select hair group to edit
3. Adjust parameters:
   - Thickness
   - Length
   - Waviness
   - Gravity effect
4. Add highlights:
   - Click "Add Highlight Layer"
   - Choose color and blend mode
5. Physics settings:
   - Stiffness (how rigid)
   - Inertia (bounce effect)
```

**Outfit Design**:
```
1. Click "Outfit" → "Customize"
2. Choose garment to edit
3. Options:
   - Preset variations
   - Color customization
   - Pattern overlay
   - Custom texture painting
4. Save as preset for reuse
```

**Face Expression Setup**:
```
1. Go to "Face" → "Expression Editor"
2. Create custom expressions:
   - Happy, sad, angry, surprised
   - Blush levels
   - Eye animations (blink, wink)
3. Adjust blend shape weights
4. Test expressions with preview
```

### Step 6: Exporting for Warudo

**Option A: Use Pre-Exported Anna.vrm** (Fastest)

Anna_AI includes a ready-to-use VRM file at `Anna_AI\personality\avatar\Anna.vrm`. You can skip the export process and use this file directly in Warudo.

**Advantages**:
- Pre-optimized for performance
- Expressions already configured
- Physics tuned for Warudo
- No export wait time

**Proceed to**: [Warudo Installation](#warudo-installation) to load this file.

---

**Option B: Export Modified or New Character**

If you modified anna_model.vroid or created a new character, export it:

**Export as VRM**:
1. Click "Camera/Exporter" tab (camera icon)
2. Click "Export" → "Export as VRM"
3. Configure export settings:

```
Model Information:
- Title: [Your character name]
- Version: 1.0
- Author: [Your name]
- Contact: [Optional email]

Permission Settings:
- Avatar Personalization: Allow
- Violent Usage: Disallow
- Sexual Usage: Disallow
- Commercial Usage: [Your choice]
- Redistribution: Disallow (recommended)

Technical Settings:
- Reduce Polygon Count: Check (for better performance)
- Export Blend Shapes: Check (required for expressions)
- Export Shadows: Check
- Texture Size: 2048x2048 (or 4096x4096 for high quality)
```

4. Click "Export"
5. Choose save location: `Documents\VRoid\Exports\YourCharacter.vrm`
6. Export time: 30-60 seconds

**File Size**:
- Typical VRM: 20-50MB
- High-quality: 50-100MB
- Optimized: 10-20MB

### Step 7: Import to Warudo

**Using Anna's Pre-Exported VRM**:
1. Open Warudo
2. Click "Add Asset" → "Character"
3. Click "Import VRM"
4. Navigate to: `C:\Projects\Anna_AI\personality\avatar\Anna.vrm`
5. Click "Open"
6. Character loads with all customizations
7. Proceed to load Warudo configuration files (see [Warudo Installation](#warudo-installation))

**Using Your Custom Export**:
1. Open Warudo
2. Click "Add Asset" → "Character"
3. Click "Import VRM"
4. Navigate to your exported VRM file location
5. Click "Open"
6. Character loads with your customizations

**Post-Import Setup**:
1. Adjust character position and scale
2. Test facial expressions (should match VRoid setup)
3. Configure physics (hair, clothes)
4. Calibrate face tracking for your character

### Step 8: Optimization Tips

**Performance Optimization**:
- **Polygon Count**: Keep under 50,000 for smooth performance
  - Go to "Body" → "Polygon Reduction"
  - Target: 30,000-40,000 polygons
  
- **Texture Resolution**: Balance quality and file size
  - 2048x2048: Good balance
  - 4096x4096: High quality (larger file)
  - 1024x1024: Performance mode (lower quality)

- **Physics Objects**: Limit for better FPS
  - Reduce hair groups
  - Simplify cloth physics

**Quality Improvements**:
- Use high-resolution textures for close-ups
- Add subsurface scattering for realistic skin
- Fine-tune expression blend shapes
- Add custom makeup and details

### VRoid Studio Tips & Tricks

**Hair Design**:
- Use multiple layers for depth
- Mix procedural and custom strands
- Add highlights for anime effect
- Adjust physics for natural movement

**Outfit Coordination**:
- Save favorite combinations as presets
- Use color theory for pleasing palettes
- Add accessories sparingly
- Test in different lighting conditions

**Expression Range**:
- Create 8-10 core expressions
- Test with face tracking
- Adjust blend shape intensities
- Save expression presets

**Troubleshooting Common Issues**:

**Character looks flat**:
- Add hair highlights
- Increase eye shine
- Add rim lighting in Warudo

**Hair clips through body**:
- Adjust hair collision settings
- Reduce hair length
- Modify hair physics parameters

**Expressions don't work in Warudo**:
- Re-export with "Export Blend Shapes" checked
- Verify expression names match standard VRM format
- Check VRM version compatibility

---

## VERIFICATION & TESTING

### Complete System Test

Run this comprehensive test script to verify all components:

```batch
# Save as test_system.bat
@echo off
echo ====================================
echo VTUBER AI AGENT SYSTEM TEST
echo ====================================
echo.

echo [1/8] Testing Python installation...
python --version
if %errorlevel% neq 0 (
    echo [FAIL] Python not found
    exit /b 1
)
echo [PASS] Python OK
echo.

echo [2/8] Testing Virtual Audio Cable...
python -c "import sounddevice as sd; devices = sd.query_devices(); cable_found = any('CABLE Input' in d['name'] for d in devices); assert cable_found, 'Virtual cable not found'; print('Virtual Cable: OK')"
if %errorlevel% neq 0 (
    echo [FAIL] Virtual cable not detected
    exit /b 1
)
echo [PASS] Virtual Cable OK
echo.

echo [3/8] Testing PyTorch GPU support...
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); assert torch.cuda.is_available(), 'GPU not detected'"
if %errorlevel% neq 0 (
    echo [FAIL] GPU not detected
    exit /b 1
)
echo [PASS] PyTorch GPU OK
echo.

echo [4/8] Testing CTranslate2...
python -c "from faster_whisper import WhisperModel; print('CTranslate2: OK')"
if %errorlevel% neq 0 (
    echo [FAIL] CTranslate2 not working
    exit /b 1
)
echo [PASS] CTranslate2 OK
echo.

echo [5/8] Testing TTS system...
python -c "from TTS.api import TTS; print('TTS: OK')"
if %errorlevel% neq 0 (
    echo [FAIL] TTS not working
    exit /b 1
)
echo [PASS] TTS OK
echo.

echo [6/8] Testing Ollama connection...
curl -s http://localhost:11434/api/tags > nul
if %errorlevel% neq 0 (
    echo [WARN] Ollama not running (optional)
) else (
    echo [PASS] Ollama OK
)
echo.

echo [7/8] Testing audio devices...
python -c "import sounddevice as sd; print(f'Input devices: {len(sd.query_devices())}'); assert len(sd.query_devices()) > 0"
if %errorlevel% neq 0 (
    echo [FAIL] No audio devices found
    exit /b 1
)
echo [PASS] Audio devices OK
echo.

echo [8/8] Testing Discord integration...
python -c "import discord; print('Discord.py: OK')"
if %errorlevel% neq 0 (
    echo [FAIL] Discord.py not installed
    exit /b 1
)
echo [PASS] Discord.py OK
echo.

echo ====================================
echo ALL TESTS PASSED
echo ====================================
echo.
echo System ready to run!
pause
```

### Manual Component Tests

**Test 0: Virtual Audio Cable**
```python
import sounddevice as sd

# List all audio devices
devices = sd.query_devices()
print("Available Audio Devices:")
for i, device in enumerate(devices):
    print(f"{i}: {device['name']}")
    if "CABLE" in device['name']:
        print(f"   → Virtual cable detected: {device['name']}")

# Verify CABLE Input exists
cable_found = any("CABLE Input" in d['name'] for d in devices)
assert cable_found, "Virtual cable not installed"
print("\n✓ Virtual cable verified")
```

**Test 1: Whisper Speech Recognition**
```python
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cuda", compute_type="int8")
segments, info = model.transcribe("test_audio.wav")

for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
```

**Test 2: XTTS Voice Synthesis**
```python
from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
tts.tts_to_file(
    text="Hello! Testing the text-to-speech system.",
    file_path="output.wav",
    speaker_wav="reference_voice.wav",
    language="en"
)
```

**Test 3: Ollama Integration**
```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "llama3.1:8b", "prompt": "Hello!", "stream": False}
)
print(response.json()["response"])
```

**Test 4: GPU Memory Check**
```python
import torch

print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"VRAM Total: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
print(f"VRAM Allocated: {torch.cuda.memory_allocated(0) / 1e9:.2f} GB")
print(f"VRAM Reserved: {torch.cuda.memory_reserved(0) / 1e9:.2f} GB")
```

### Performance Benchmarks

Expected performance on RTX 5060 Ti (16GB VRAM):

| Component | Metric | Expected Performance |
|-----------|--------|---------------------|
| Whisper Medium | Transcription Speed | 5-8x real-time |
| XTTS Voice Synthesis | Generation Time | 1-2 seconds for 10s audio |
| Ollama Llama3.1 8B | Tokens/Second | 40-60 tokens/s |
| Warudo | FPS (1080p) | 60+ FPS |
| Face Tracking | Latency | <50ms |

---

## TROUBLESHOOTING

### Python Issues

**Problem**: `python` command not recognized
```batch
# Solution 1: Add Python to PATH manually
setx PATH "%PATH%;C:\Python311;C:\Python311\Scripts"

# Solution 2: Use py launcher
py --version
py -m pip install package_name
```

**Problem**: Permission denied errors
```batch
# Run Command Prompt as Administrator
# Or install packages with --user flag
pip install --user package_name
```

**Problem**: SSL certificate errors during pip install
```batch
# Update pip and certificates
python -m pip install --upgrade pip certifi
```

### GPU Issues

**Problem**: CUDA not available (torch.cuda.is_available() returns False)

**Solution 1**: Verify NVIDIA drivers
```batch
nvidia-smi
```
Should show driver version 566.03 or newer.

**Solution 2**: Reinstall CUDA toolkit
```batch
# Download CUDA 12.8 from NVIDIA website
# https://developer.nvidia.com/cuda-downloads
```

**Solution 3**: Check PyTorch installation
```python
import torch
print(torch.__version__)  # Should show 2.10.0a0+gitd4493c5 or similar
print(torch.version.cuda)  # Should show 12.8 or similar
```

**Problem**: GPU runs out of memory

**Solution**: Adjust batch sizes and model precision
```python
# In your config
WHISPER_CONFIG = {
    "compute_type": "int8",  # Use int8 instead of float16
    "beam_size": 3           # Reduce from default 5
}

TTS_CONFIG = {
    "batch_size": 1,         # Process one at a time
    "precision": "fp16"      # Use half precision
}
```

**Problem**: CTranslate2 import error

**Solution**: Ensure proper package copy
```batch
# Re-copy from Anna_AI
xcopy "C:\Projects\Anna_AI\venv\Lib\site-packages\ctranslate2" "C:\Projects\YourAgent_AI\venv\Lib\site-packages\ctranslate2" /E /I /H /Y
```

### Transformers Version Issues

**Problem**: XTTS fails with BeamSearchScorer error

**Error Message**:
```
AttributeError: 'BeamSearchScorer' object has no attribute 'max_length'
```

**Solution**: Downgrade transformers
```batch
pip uninstall transformers
pip install transformers==4.38.2
```

**Problem**: Transformers won't downgrade

**Solution**: Force reinstall
```batch
pip install --force-reinstall --no-cache-dir transformers==4.38.2
```

### Audio Issues

**Problem**: No microphone detected

**Solution 1**: Check Windows sound settings
```
Settings → System → Sound → Input → Choose device
```

**Solution 2**: List audio devices
```python
import sounddevice as sd
print(sd.query_devices())
```

**Solution 3**: Set default device in code
```python
import sounddevice as sd
sd.default.device = 1  # Try different device indices
```

**Problem**: PyAudio installation fails

**Solution**: Use pre-built wheel
```batch
# Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# Install local wheel
pip install PyAudio-0.2.14-cp311-cp311-win_amd64.whl
```

**Problem**: Virtual cable not detected

**Solution 1**: Verify installation
```
Control Panel → Sound → Playback tab
Should show: CABLE Input (VB-Audio Virtual Cable)

Control Panel → Sound → Recording tab
Should show: CABLE Output (VB-Audio Virtual Cable)
```

**Solution 2**: Reinstall driver
```batch
# Navigate to VB-Audio installation folder
cd C:\Program Files\VB\CABLE
# Run setup as Administrator
VBCABLE_Setup_x64.exe
# Click "Install Driver"
# Restart computer
```

**Solution 3**: Check driver status
```
Device Manager → Sound, video and game controllers
Look for: VB-Audio Virtual Cable
Status should be: "This device is working properly"
```

**Problem**: TTS audio plays through speakers instead of virtual cable

**Solution 1**: Force device in code
```python
import sounddevice as sd

# Find CABLE Input index
devices = sd.query_devices()
cable_idx = None
for i, dev in enumerate(devices):
    if "CABLE Input" in dev['name'] and dev['max_output_channels'] > 0:
        cable_idx = i
        break

# Set as output
sd.default.device = [None, cable_idx]
```

**Solution 2**: Verify .env configuration
```env
TTS_OUTPUT_DEVICE=CABLE Input (VB-Audio Virtual Cable)
# Exact name must match device name in Windows
```

**Solution 3**: Check application audio routing
```
Windows Settings → Sound → App volume and device preferences
Find Python.exe or Anna_AI
Output: CABLE Input (VB-Audio Virtual Cable)
```

**Problem**: Warudo doesn't detect lip sync audio

**Solution 1**: Verify Warudo audio input
```
Warudo → Settings → Audio
Lip Sync Input Device: CABLE Output (VB-Audio Virtual Cable)
Ensure "Lip Sync" is enabled
```

**Solution 2**: Test cable routing
```
Windows Sound Settings → Sound Control Panel
Playback tab → CABLE Input → Properties → Listen tab
Check "Listen to this device"
Playback through this device: [Your speakers]
Speak through agent → Should hear audio through speakers
Uncheck when done testing
```

**Solution 3**: Increase sensitivity
```
Warudo → Settings → Audio
Lip Sync Sensitivity: Increase to 70-80%
Test with agent speech
```

**Problem**: Multiple agents audio conflicts

**Solution**: Ensure each agent uses different cable
```
Anna_AI .env:
TTS_OUTPUT_DEVICE=CABLE Input (VB-Audio Virtual Cable)

SecondAgent_AI .env:
TTS_OUTPUT_DEVICE=CABLE-A Input (Tala Virtual Cable)

ThirdAgent_AI .env:
TTS_OUTPUT_DEVICE=CABLE-B Input (Tala Virtual Cable)

Each Warudo instance must match:
Warudo 1 → CABLE Output
Warudo 2 → CABLE-A Output
Warudo 3 → CABLE-B Output
```

**Problem**: Crackling or distorted audio through cable

**Solution 1**: Increase buffer size
```python
import sounddevice as sd
sd.default.latency = 'high'
sd.default.blocksize = 2048
```

**Solution 2**: Match sample rates
```
Right-click CABLE Input → Properties → Advanced
Default Format: 2 channel, 16 bit, 22050 Hz

Agent .env:
TTS_SAMPLE_RATE=22050
```

**Solution 3**: Reduce system load
```
Close unnecessary applications
Lower Warudo graphics quality
Use smaller Whisper model
Reduce Ollama context window
```

### Ollama Issues

**Problem**: Ollama service won't start

**Solution 1**: Check if already running
```batch
tasklist | findstr ollama
```

**Solution 2**: Restart service
```batch
net stop ollama
net start ollama
```

**Solution 3**: Check logs
```batch
type "%USERPROFILE%\.ollama\logs\server.log"
```

**Problem**: Model download fails

**Solution**: Manually download model
```batch
# Download from official source
# Place in: C:\Users\YourUsername\.ollama\models\
```

**Problem**: Connection refused errors

**Solution**: Check firewall settings
```batch
# Add firewall rule for Ollama
netsh advfirewall firewall add rule name="Ollama" dir=in action=allow protocol=TCP localport=11434
```

### Warudo Issues

**Problem**: Character doesn't load

**Solution 1**: Verify VRM file integrity
```
- Re-export from VRoid Studio
- Check file size (should be >5MB)
- Ensure VRM 0.0 format (not VRM 1.0)
```

**Solution 2**: Update Warudo
```
- Check for updates in Warudo
- Reinstall if necessary
```

**Problem**: Face tracking not working

**Solution 1**: Camera permissions
```
Settings → Privacy → Camera → Allow apps to access camera
```

**Solution 2**: Recalibrate tracking
```
Warudo → Character → Face Tracking → Calibrate
```

**Solution 3**: Try different tracking method
```
Switch from Webcam to Media Pipe (CPU-based)
```

**Problem**: Low FPS in Warudo

**Solution**: Reduce quality settings
```
Settings → Graphics:
- Quality: Medium
- Shadows: Low
- Anti-aliasing: Off
- Post-processing: Minimal
```

### VRoid Studio Issues

**Problem**: Export fails

**Solution**: Reduce model complexity
```
Body → Polygon Reduction → Target: 30,000
Hair → Reduce hair groups to <10
```

**Problem**: Textures look wrong in Warudo

**Solution**: Re-export with correct settings
```
Export → Texture Size: 2048x2048
Export → Format: VRM 0.0
```

**Problem**: Expressions don't work

**Solution**: Verify blend shape export
```
Export → Advanced → Export Blend Shapes: Check
Export → Include Expression Morphs: Check
```

### Network Issues

**Problem**: Discord bot won't connect

**Solution 1**: Verify token
```python
# In .env file
DISCORD_TOKEN=your_actual_token_here  # No quotes or extra spaces
```

**Solution 2**: Check Discord developer portal
```
- Verify bot has required intents enabled
- Ensure bot is invited to server with correct permissions
```

**Problem**: WebSocket connection to Warudo fails

**Solution**: Check network settings
```batch
# Test connection
curl http://localhost:7890

# Verify Warudo WebSocket is enabled
Warudo → Settings → Network → Enable WebSocket Server
```

---

## COMMON ISSUES

### "ModuleNotFoundError" Errors

Always activate virtual environment before running:
```batch
cd YourAgent_AI
.\venv\Scripts\activate
python your_script.py
```

### Virtual Environment Not Working

Recreate virtual environment:
```batch
rmdir /s /q venv
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Slow Performance

**Check GPU usage**:
```batch
nvidia-smi
```

**Optimize settings**:
- Reduce Whisper model size (large → medium → base)
- Use int8 compute type instead of float16
- Reduce Ollama context window
- Lower Warudo graphics quality

### Memory Leaks

**Restart agent periodically**:
```python
# Add to main loop
import psutil
import os

process = psutil.Process(os.getpid())
if process.memory_info().rss > 8 * 1024**3:  # 8GB
    print("Memory limit reached, restarting...")
    # Implement graceful restart
```

### Models Not Loading

**Clear cache**:
```batch
# Clear HuggingFace cache
rmdir /s /q "%USERPROFILE%\.cache\huggingface"

# Clear Ollama cache
ollama rm --all
ollama pull llama3.1:8b
```

### Agent Freezes or Crashes

**Enable debug logging**:
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_debug.log'),
        logging.StreamHandler()
    ]
)
```

**Check logs**:
- Python errors: `agent_debug.log`
- Ollama errors: `%USERPROFILE%\.ollama\logs\server.log`
- Warudo errors: `%LOCALAPPDATA%\Warudo\logs\`

---

## ADDITIONAL RESOURCES

### Documentation Links

- **Anna_AI Repository**: https://github.com/KryptykBioz/Anna_AI
- **AI Agent Tools**: https://github.com/KryptykBioz/AI_Agent_Tools
- **VB-Audio Virtual Cable**: https://vb-audio.com/Cable/
- **Tala Virtual Cables**: https://github.com/Essence-Platform/TalaVirtualAudioCables-Public
- **Python**: https://docs.python.org/3.11/
- **PyTorch**: https://pytorch.org/docs/stable/index.html
- **Transformers**: https://huggingface.co/docs/transformers/
- **Faster Whisper**: https://github.com/SYSTRAN/faster-whisper
- **Coqui TTS**: https://docs.coqui.ai/en/latest/
- **Discord.py**: https://discordpy.readthedocs.io/
- **Ollama**: https://github.com/ollama/ollama/tree/main/docs
- **Warudo**: https://docs.warudo.app/
- **VRoid Studio**: https://vroid.com/en/studio

### Community Support

- **Discord**: [Your community Discord server]
- **GitHub Issues**: [Your repository]/issues
- **Reddit**: r/VirtualYoutubers, r/VTuberTech

### Update Policy

- **Agent Framework**: Check for updates monthly
- **Python Packages**: Update cautiously, test thoroughly
- **GPU Drivers**: Update quarterly or when issues arise
- **Ollama**: Update when new features are needed
- **Warudo**: Update when stable releases available
- **VRoid Studio**: Update for new features

---

## CHANGELOG

### Version 1.0.0 (2025-01-02)
- Initial release
- RTX 50-series GPU support documented
- Comprehensive installation instructions
- Ollama, Warudo, VRoid Studio integration guides
- Troubleshooting section added

---

## SUPPORT

For technical support:
1. Check this SETUP.md file
2. Review troubleshooting section
3. Check project README.md
4. Search existing GitHub issues
5. Create new issue with:
   - Error message (full text)
   - Python version: `python --version`
   - PyTorch version: `python -c "import torch; print(torch.__version__)"`
   - GPU info: `nvidia-smi`
   - Steps to reproduce

---

**[Note]**: This setup guide is maintained for RTX 50-series GPU compatibility. For other GPU architectures, standard PyPI packages may be used without the special GPU package copy procedure.

**Last Updated**: January 2, 2026
**Compatible With**: Python 3.11.9, PyTorch 2.10.0a0, Transformers 4.38.2