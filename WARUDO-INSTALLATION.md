# Warudo Installation & Setup Guide

## What is Warudo?

Warudo is a 3D avatar animation software that:
- Displays your agent as a 3D character on screen
- Animates lips in sync with TTS speech
- Supports custom VRM avatars
- Runs on Windows/Mac
- Integrates with Anna AI via WebSocket

**Result**: Your agent has a visible, animated 3D avatar that speaks and responds to you.

---

## Prerequisites

✓ VB-Audio Virtual Cable installed (see `VB-AUDIO-INSTALLATION.md`)
✓ Anna AI running and responding
✓ RTX 4060 GPU (Warudo works with integrated graphics too, but slower)

---

## Step 1: Download Warudo

### Option A: Steam (Recommended)

1. Visit: https://store.steampowered.com/app/2704600/Warudo/
2. Click "Add to Library"
3. Click "Install"
4. Wait for installation (5-10 minutes, ~5GB)
5. Click "Play"

### Option B: Direct Download

1. Visit: https://warudo.app/download
2. Click "Windows Download"
3. Run installer
4. Follow installation wizard
5. Choose installation location (default is fine)

---

## Step 2: Initial Warudo Setup

### First Launch

1. Launch Warudo (from Steam or desktop shortcut)
2. You'll see the startup wizard
3. Create account or sign in (free account)
4. Accept terms

### Graphics Configuration

```
Settings → Graphics
- Quality: High (adjust down if GPU overheating)
- Resolution: 1920×1080 (adjust to your monitor)
- Anti-aliasing: MSAA 2x
- V-Sync: On
- Frame Rate: 60 FPS
```

**GPU Settings** (for RTX 4060):
- Quality: High is fine
- If performance drops, use Medium or Fast
- MSAA can be reduced to 1x or None

---

## Step 3: Audio Configuration

### Setup Lip Sync Input

This is critical - it allows Warudo to animate lips based on TTS audio.

```
Warudo Menu → Settings → Audio
- Lip Sync Input: CABLE Output (VB-Audio Virtual Cable)
- Sample Rate: 48000 Hz
- Buffer Size: 512 (or 1024 if crackling)
```

**Important**: You must select **CABLE Output**, not CABLE Input.

Why? Audio flow:
1. Anna AI sends speech to CABLE Input
2. Windows routes CABLE Input → CABLE Output
3. Warudo listens to CABLE Output
4. Warudo sees lips moving → Animates character

---

## Step 4: Network Configuration

This allows Anna AI to communicate with Warudo.

```
Warudo Menu → Settings → Network
- Enable WebSocket Server: [✓] Check this
- Port: 19190 (don't change this)
- Enable External Connections: [✓] Check this
```

**Verify**: You should see "WebSocket Server: Running on Port 19190"

---

## Step 5: Load Anna Avatar

Anna AI comes with a pre-made VRM avatar ready to use.

### Import Anna.vrm

```
Warudo Menu → File → Import Model
- Navigate to: C:\Users\beren\Anna_AI\personality\avatar\Anna.vrm
- Click "Open"
- Wait for character to load (10-30 seconds)
```

You should now see a 3D character in the center of Warudo.

### Adjust Character

Once loaded:
- **Move**: Right-click and drag to pan
- **Zoom**: Mouse wheel to zoom in/out
- **Rotate**: Left-click and drag to rotate

---

## Step 6: Verify Lip Sync

Test that everything is connected properly.

### Test Procedure

1. Keep Warudo open
2. Launch Anna AI: `START-OPTIMIZED.bat`
3. Wait for Anna AI GUI to appear
4. In Anna AI chat, type: "Hello, this is a test message"
5. Send message

### Expected Results

- ✓ Agent responds in chat
- ✓ TTS voice plays
- ✓ Warudo character's lips move
- ✓ Lips move in sync with speech

### If Lips Don't Move

**Problem**: Lip sync not working

**Solution 1**: Check audio routing
```
1. Open Windows Volume Mixer
2. Start Anna AI
3. Agent should speak
4. Look for "python.exe" or "Anna AI"
5. Verify output device is "CABLE Input"
```

**Solution 2**: Check Warudo settings
```
Warudo → Settings → Audio
- Lip Sync Input: CABLE Output (not CABLE Input!)
- Buffer Size: 1024 (increase if crackling)
```

**Solution 3**: Restart Warudo
```
Close Warudo completely
Reopen it
Check Network settings: WebSocket running on 19190?
```

---

## Step 7: Customize Character (Optional)

You can modify the avatar using VRoid Studio.

### Use Existing Avatar

The included `Anna.vrm` is ready to use. You can keep it as-is.

### Create Custom Avatar

1. Download VRoid Studio: https://vroid.com/studio
2. Create or import character
3. Customize appearance
4. Export as VRM 0.0 (not VRM 1.0)
5. Save to: `C:\Users\beren\Anna_AI\personality\avatar\YourName.vrm`
6. Import into Warudo as shown in Step 5

---

## Configuration Files

### Check config.json

Verify Warudo integration settings:

```json
{
  "warudo": {
    "websocket_url": "ws://127.0.0.1:19190",
    "enabled": true,
    "auto_connect": true,
    "connection_timeout": 2.0
  }
}
```

Should match Warudo network port (19190).

### Check bot_info.py

```python
# Should have these set:
vb_cable_name = "CABLE Input"
use_warudo = True
```

---

## Troubleshooting

### Warudo Won't Start

**Solution 1**: Check GPU drivers
```
GPU: RTX 4060
Download latest drivers from NVIDIA
Minimum version: 566.03
```

**Solution 2**: Check disk space
```
Warudo needs ~5GB free space
Check: Settings → System → Storage
```

**Solution 3**: Reinstall Warudo
```
Steam: Right-click game → Properties → Installed Files → Verify
Direct: Uninstall → Reinstall
```

### Character Not Loading

**Problem**: Avatar doesn't appear in Warudo

**Solution 1**: Verify file integrity
```
File: C:\Users\beren\Anna_AI\personality\avatar\Anna.vrm
Size: Should be 10MB+
Re-export from VRoid if corrupted
```

**Solution 2**: Try another avatar
```
Search online for free VRM models
Download .vrm file
Import into Warudo → File → Import Model
```

**Solution 3**: Check Warudo logs
```
Logs folder: %LOCALAPPDATA%\Warudo\logs\
Look for error messages
Check if file format is VRM 0.0 (not 1.0)
```

### WebSocket Connection Failed

**Problem**: Anna AI can't communicate with Warudo

**Solution 1**: Verify network settings in Warudo
```
Warudo → Settings → Network
- Enable WebSocket Server: [✓]
- Port: 19190
- Status should show: "Running"
```

**Solution 2**: Check firewall
```
Windows Defender Firewall → Allow an app
Add: Warudo
Check: Private networks
```

**Solution 3**: Test connection manually
```powershell
cd C:\Users\beren\Anna_AI
.\venv\Scripts\python.exe -c "import requests; print(requests.get('http://localhost:19190', timeout=2).status_code)"
```

Should return `200` or connection response (not timeout).

### Lip Sync Timing Off

**Problem**: Lips don't move in sync with speech

**Solution 1**: Adjust buffer size
```
Warudo → Settings → Audio
- Buffer Size: 1024 (double current value)
- Lip Sync Sensitivity: 70-90%
```

**Solution 2**: Adjust sample rate
```
Windows Settings → Sound → CABLE Output Properties → Advanced
- Default Format: 2 channel, 16 bit, 48000 Hz
```

**Solution 3**: Check CPU/GPU load
```
Monitor performance: monitor-performance.py --continuous
GPU should be 30-50% utilized (not maxed out)
CPU should be <80%
```

If maxed out, lower Warudo graphics quality.

---

## Performance Optimization

### For RTX 4060

**Recommended Settings**:
```
Graphics Quality: High
Resolution: 1920×1080
Anti-aliasing: MSAA 2x
V-Sync: On
Frame Rate: 60 FPS
```

If you see stuttering or frame drops:
1. Lower to Medium quality
2. Reduce resolution to 1280×720
3. Lower anti-aliasing to 1x
4. Disable V-Sync

### Monitor Performance

```powershell
.\venv\Scripts\python.exe monitor-performance.py --continuous
```

Watch GPU usage:
- **Normal**: 30-50% with character moving
- **Idle**: 5-10% when character still
- **Problem**: 95-100% → Lower graphics quality

---

## Next Steps

### Fully Functional Setup Complete!

✓ Anna AI installed and running  
✓ GPU acceleration enabled  
✓ VB-Audio Virtual Cable installed  
✓ Warudo running with avatar  
✓ Lip sync configured  

### Optional Enhancements

1. **Download AI Agent Tools** (extra features)
   - Repository: https://github.com/KryptykBioz/AI_Agent_Tools
   - Tools: Game integration, chat platforms, vision, etc.

2. **Discord Integration**
   - Get Discord bot token
   - Configure in .env
   - Agent joins Discord servers

3. **Twitch Integration**
   - Get Twitch OAuth token
   - Configure in .env
   - Agent joins Twitch chat

4. **YouTube Integration**
   - Get YouTube API key
   - Configure in .env
   - Agent joins YouTube live chat

---

## Current Status

🟢 **All Core Features Active:**
- ✓ Python environment configured
- ✓ GPU PyTorch enabled (RTX 4060)
- ✓ VB-Audio Virtual Cable configured
- ✓ Warudo installed and running
- ✓ Avatar loaded with lip sync
- ✓ WebSocket communication working

🟡 **Optional Features Available:**
- ⏳ AI Agent Tools (not yet installed)
- ⏳ Discord integration (not yet configured)
- ⏳ Twitch integration (not yet configured)

---

**Warudo Status**: 🟢 Ready to Use

See `ANNA_AI_COMPLETE_SETUP.md` for full system overview.
