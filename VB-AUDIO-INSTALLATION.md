# VB-Audio Virtual Cable Installation Guide

## Why You Need This

Your Anna AI can now speak (via TTS), but without a virtual audio cable, the sound goes nowhere. Virtual audio cables allow:

- **TTS Audio Routing**: Send generated speech to Warudo without playing through speakers
- **Lip Sync Animation**: Warudo captures audio for real-time mouth movement
- **Silent Operation**: Agent speaks through avatar without disturbing you
- **Multiple Agents**: Each agent gets its own cable

---

## Quick Install

### Step 1: Download VB-Audio Virtual Cable

1. Visit: https://vb-audio.com/Cable/
2. Click "Download" button
3. You'll get: `VBCABLE_Driver_Pack43.zip` (~2MB)
4. Extract to temporary folder (e.g., `C:\Downloads`)

### Step 2: Install the Driver

1. Open the extracted folder
2. **Right-click `VBCABLE_Setup_x64.exe`**
3. Select **"Run as administrator"**
4. Click "Install Driver"
5. Windows will ask permission → Click "Install"
6. Wait for "Installation successful" message
7. Click "OK"

### Step 3: Restart Computer

**IMPORTANT**: Restart your computer for the driver to activate. Virtual audio drivers require a system restart.

```
Restart Now or Restart Later
```

### Step 4: Verify Installation

After restart:

1. Right-click the speaker icon in taskbar
2. Select "Open Sound settings"
3. Scroll to "Advanced sound options"
4. Click "App volume and device preferences"
5. Look for:
   - **CABLE Input (VB-Audio Virtual Cable)**
   - **CABLE Output (VB-Audio Virtual Cable)**

If you see both, installation is successful ✓

---

## Configuration for Anna AI

### Step 1: Update bot_info.py

Edit: `C:\Users\beren\Anna_AI\personality\bot_info.py`

Find this line:
```python
vb_cable_name = "CABLE Input"
```

Verify it says exactly: `"CABLE Input"` (case-sensitive)

### Step 2: Test Audio Routing

```powershell
cd C:\Users\beren\Anna_AI
.\venv\Scripts\python.exe -c "import sounddevice as sd; devices = sd.query_devices(); print([d['name'] for d in devices if 'CABLE' in d['name']])"
```

You should see:
```
['CABLE Input', 'CABLE Output']
```

If CABLE doesn't appear, restart your computer again.

### Step 3: Windows Audio Settings

**DO NOT** set virtual cables as default system audio!

```
Windows Settings → Sound → Volume
- Output device: Keep as your speakers/headphones
- Input device: Keep as your microphone
```

Virtual cables are assigned per-application by Anna AI automatically.

---

## For Multiple Agents (Optional)

If running 2-3 agents simultaneously, install Tala Virtual Cables for extra cables:

1. Visit: https://github.com/Essence-Platform/TalaVirtualAudioCables-Public
2. Click "Releases"
3. Download latest: `TalaVirtualAudioCables.zip`
4. Extract and run installer as administrator
5. **Restart computer**

This gives you:
- **Agent 1**: CABLE Input/Output (VB-Audio)
- **Agent 2**: CABLE-A Input/Output (Tala)
- **Agent 3**: CABLE-B Input/Output (Tala)

---

## Troubleshooting

### CABLE devices not appearing after restart

**Solution 1**: Reinstall the driver
```powershell
# Right-click VBCABLE_Setup_x64.exe → Run as administrator
# Click "Install Driver" again
# Restart
```

**Solution 2**: Check Device Manager
```
1. Right-click Start → Device Manager
2. Look for "Sound, video and game controllers"
3. Expand it
4. Should see "VB-Audio Cable"
5. If not, restart computer again
```

**Solution 3**: Reinstall Windows audio drivers
```
Device Manager → Sound devices → Right-click → Update driver
```

### Audio not routing to Warudo

**Check in bot_info.py**:
```python
vb_cable_name = "CABLE Input"  # Exact match required
```

**Verify device name**:
```powershell
.\venv\Scripts\python.exe -c "import sounddevice as sd; print([d for d in sd.query_devices()])"
```

Look for exact name including spaces and capitalization.

### Crackling or choppy audio

**Lower buffer size in Windows**:
```
1. Right-click CABLE Input → Properties → Advanced
2. Set to: 2 channel, 16 bit, 44100 Hz
3. Apply
```

---

## Next Steps

After VB-Audio is installed and verified:

1. ✓ VB-Audio Virtual Cable installed
2. Next → Install Warudo (for 3D avatar)
3. Next → Configure lip sync
4. Next → Start using Anna AI with voice

See `WARUDO_INSTALLATION.md` for next steps.

---

## What It Enables

With VB-Audio installed, Anna AI can now:

- ✓ Generate speech using TTS
- ✓ Route audio to Warudo silently
- ✓ Support lip sync animation
- ✓ Run multiple agents without audio conflicts
- ✓ Keep audio from disturbing your work

**Status**: 🟢 Ready for Warudo installation
