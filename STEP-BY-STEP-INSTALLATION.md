# Step-by-Step Installation Guide with Screenshots

## STEP 1: Install VB-Audio Virtual Cable

### What You'll Do
Download a small driver, run an installer, click a few buttons, restart your computer. Takes 10 minutes total.

### Part 1A: Download the File

**Do this:**
1. Open your web browser
2. Go to: https://vb-audio.com/Cable/
3. Look for the blue "Download" button
4. Click it
5. You'll get a file: `VBCABLE_Driver_Pack43.zip` (~2MB)
6. Save it to your Downloads folder

**Expected Result:**
- File is in your Downloads folder
- File size: ~2 MB
- Filename: `VBCABLE_Driver_Pack43.zip`

### Part 1B: Extract the ZIP File

**Do this:**
1. Open File Explorer (Windows key + E)
2. Navigate to: `C:\Users\beren\Downloads`
3. Find: `VBCABLE_Driver_Pack43.zip`
4. Right-click on it
5. Select: "Extract All..."
6. Choose extraction location: `C:\Users\beren\Downloads\VBCABLE`
7. Click "Extract"
8. Wait for extraction to complete (should be instant)

**Expected Result:**
- New folder created: `VBCABLE_Driver_Pack43`
- Inside you'll see several files including `VBCABLE_Setup_x64.exe`

### Part 1C: Run the Installer

**IMPORTANT**: Must run as Administrator

**Do this:**
1. Open the extracted folder: `VBCABLE_Driver_Pack43`
2. Find: `VBCABLE_Setup_x64.exe` (the executable file)
3. **Right-click** on it
4. Select: **"Run as administrator"**
5. Click "Yes" when Windows asks "Do you want to allow this app..."

**Expected Result:**
- Installer window opens
- You see options like "Install Driver" button

### Part 1D: Install the Driver

**Do this:**
1. In the installer window, click the button: **"Install Driver"**
2. Windows will show a driver installation dialog
3. Click **"Install"** button
4. Wait for the installation to complete
5. You should see a message: **"Installation successful"**
6. Click **"OK"**
7. Close the installer window

**Expected Result:**
- Message says "Installation successful"
- Installer closes
- Virtual cable driver is now installed

### Part 1E: Restart Your Computer

**CRITICAL**: Virtual audio drivers need a restart to activate

**Do this:**
1. Click Windows Start button
2. Click the power icon
3. Select: **"Restart"**
4. Wait for computer to restart
5. Log back in

**Expected Result:**
- Computer restarts
- You're back at your desktop
- Virtual cable is now active

---

## STEP 2: Verify VB-Audio Installation

### Check if Installation Worked

**Do this:**
1. Right-click the speaker icon in taskbar (bottom right corner)
2. Select: **"Open Sound settings"**
3. A settings window opens
4. Scroll down to find: **"Advanced sound options"**
5. Click on **"Advanced sound options"**
6. Look for **"App volume and device preferences"** (near bottom)
7. Click on it

**Expected Result:**
You should see a window with audio devices listed.

### Look for CABLE Devices

**Do this:**
1. In the "App volume and device preferences" window
2. Look at the list of devices
3. Find entries that contain **"CABLE"**

**You should see:**
- CABLE Input (VB-Audio Virtual Cable)
- CABLE Output (VB-Audio Virtual Cable)

**If you see both**: ✓ VB-Audio is installed correctly!

**If you DON'T see them**:
- Go back and restart your computer again
- Drivers sometimes take a second restart to activate
- Then check again

### Verify in Device Manager (Optional Double-Check)

**Do this:**
1. Right-click Windows Start button
2. Select: **"Device Manager"**
3. Look for section: **"Sound, video and game controllers"**
4. Click the arrow to expand it
5. Look for: **"VB-Audio Cable"**

**If you see it**: ✓ Installation verified!

---

## STEP 3: Download and Install Warudo

### Part 3A: Download Warudo

You have 2 options. **Steam is easier.**

#### Option A: Steam (Recommended)

**Do this:**
1. Open Steam (or download from https://steampowered.com)
2. Search for: "Warudo"
3. Click on the Warudo app
4. Click: **"Add to Library"** (or "Install" if already in library)
5. Click: **"Install"**
6. Choose location (default is fine): Click "Next"
7. Wait for installation (takes 5-10 minutes, ~5GB)

**Progress indicator:**
- You'll see a progress bar
- Don't close Steam while installing
- Installation is complete when progress bar shows 100%

**Expected Result:**
- File size downloaded: ~5GB
- Status shows: "Installed"
- You can now click "Play"

#### Option B: Direct Download

**Do this:**
1. Go to: https://warudo.app/download
2. Click: **"Windows Download"**
3. Installer downloads (~500MB)
4. Run the installer
5. Click "Install"
6. Choose location (default is fine)
7. Wait for installation

### Part 3B: Launch Warudo

**Do this:**
1. If using Steam:
   - Steam will show "Play" button
   - Click **"Play"**
2. If direct download:
   - Look for Warudo shortcut on desktop or Start menu
   - Double-click to launch

**Expected Result:**
- Warudo window opens
- You might see a loading screen
- Then a welcome/setup screen

---

## STEP 4: Configure Warudo Settings

### Part 4A: Open Settings

**Do this:**
1. Warudo window is open
2. Look for: **"Settings"** (usually in menu bar or gear icon)
3. Click **"Settings"**

**Expected Result:**
- Settings window/menu appears

### Part 4B: Configure Audio for Lip Sync

**Do this:**
1. In Settings, find: **"Audio"** section
2. Look for: **"Lip Sync Input"** setting
3. Click the dropdown menu
4. Select: **"CABLE Output (VB-Audio Virtual Cable)"**
   - Must be CABLE Output (not Input!)
5. Also set:
   - Sample Rate: 48000 Hz
   - Buffer Size: 512 (or 1024 if you hear crackling)

**Expected Result:**
- Lip Sync Input shows: "CABLE Output"
- Settings saved

### Part 4C: Configure Network for Communication

**Do this:**
1. In Settings, find: **"Network"** section
2. Look for: **"Enable WebSocket Server"**
3. Make sure it's **checked** [✓]
4. Verify Port is set to: **19190** (don't change this)
5. Look for: **"Enable External Connections"**
6. Make sure it's **checked** [✓]

**Expected Result:**
- WebSocket Server status shows: "Running on Port 19190"
- Both settings are enabled

### Part 4D: Configure Graphics (Optional)

**Do this:**
1. In Settings, find: **"Graphics"** section
2. Set Quality to: **"High"** (RTX 4060 can handle this)
3. Resolution: **1920×1080** (or your monitor resolution)
4. Anti-aliasing: **MSAA 2x**
5. V-Sync: **On**

**Expected Result:**
- Graphics settings configured
- These will help Warudo run smoothly

---

## STEP 5: Load Anna Avatar

### Part 5A: Import the Avatar Model

**Do this:**
1. Warudo is open and configured
2. Look for menu: **"File"** or similar
3. Select: **"Import Model"** or **"Load Model"**
4. A file browser opens
5. Navigate to: `C:\Users\beren\Anna_AI\personality\avatar\`
6. Look for and select: **`Anna.vrm`**
7. Click **"Open"** or **"Import"**

**Expected Result:**
- File dialog closes
- Warudo loads the model (takes 10-30 seconds)

### Part 5B: Verify Avatar Loaded

**Do this:**
1. Wait 10-30 seconds for loading
2. Look at the center of Warudo window
3. You should see a 3D character (Anna) appear

**Expected Result:**
- 3D character visible in center
- Character appears to be standing still
- You can see her face, hair, clothes

### Part 5C: Adjust View (Optional)

**Do this:**
1. Right-click and drag: to move camera around character
2. Mouse wheel: to zoom in/out
3. Left-click and drag: to rotate character

**Expected Result:**
- You can see all angles of the character
- Character looks good from different angles

---

## STEP 6: Configure API Tokens (Optional)

### Only Do This If You Want Discord/Twitch/YouTube Integration

### Part 6A: Edit .env File

**Do this:**
1. Open File Explorer
2. Navigate to: `C:\Users\beren\Anna_AI\`
3. Find: `.env` file (might not show by default)
4. Right-click on it
5. Select: **"Open with"** → **"Notepad"**

**Expected Result:**
- Notepad opens with .env file content
- You see many lines with configuration

### Part 6B: Add Discord Bot Token (If You Want Discord)

**Do this:**
1. Find this line: `DISCORD_BOT_TOKEN=`
2. After the `=` sign, paste your Discord bot token
3. Should look like:
   ```
   DISCORD_BOT_TOKEN=MTk4NjIyNDgzNzY4OTAxNTU2.abc123...
   ```

**To get Discord token:**
1. Go to: https://discord.com/developers/applications
2. Click: "New Application"
3. Name it: "Anna"
4. Go to "Bot" section
5. Click: "Add Bot"
6. Under TOKEN, click: "Copy"
7. Paste into .env file

**Expected Result:**
- DISCORD_BOT_TOKEN has your actual token
- Not empty, not placeholder text

### Part 6C: Add Twitch Token (If You Want Twitch)

**Do this:**
1. Find this line: `TWITCH_OAUTH_TOKEN=`
2. Go to: https://twitchapps.com/tmi/
3. Click: "Connect with Twitch"
4. Authorize
5. Copy the token (should start with `oauth:`)
6. Paste after the `=` sign

**Also set**:
```
TWITCH_CHANNEL=your_channel_name
```

**Expected Result:**
- TWITCH_OAUTH_TOKEN has your token
- TWITCH_CHANNEL has your channel name

### Part 6D: Add YouTube API Key (If You Want YouTube)

**Do this:**
1. Find this line: `YOUTUBE_API_KEY=`
2. Go to: https://console.cloud.google.com/apis/
3. Create New Project
4. Enable: YouTube Data API v3
5. Create OAuth 2.0 credentials
6. Copy API key
7. Paste after the `=` sign

**Expected Result:**
- YOUTUBE_API_KEY has your key
- Not empty

### Part 6E: Save and Close

**Do this:**
1. Notepad window has your edits
2. Press: **Ctrl+S** to save
3. Close Notepad
4. Your .env file is now configured

**Expected Result:**
- File saved
- Notepad closed
- Tokens are stored securely

---

## STEP 7: Install AI Agent Tools (Optional)

### Part 7A: Open PowerShell

**Do this:**
1. Press: **Windows key + X**
2. Select: **"Windows PowerShell (Admin)"** or **"Terminal (Admin)"**
3. Wait for window to open

**Expected Result:**
- PowerShell window opens
- Shows: `C:\Users\beren>`

### Part 7B: Copy Sound Effects Tool (Recommended)

**Do this:**
1. Paste this command and press Enter:
```powershell
Copy-Item "C:\Users\beren\AI_Agent_Tools\sound_effects" -Destination "C:\Users\beren\Anna_AI\BASE\tools\installed\" -Recurse -Force
```

**Expected Result:**
- Command completes (no error message)
- Sound effects tool is copied

### Part 7C: Copy Discord Chat Tool (If You Want It)

**Do this:**
1. Paste this command and press Enter:
```powershell
Copy-Item "C:\Users\beren\AI_Agent_Tools\discord_chat" -Destination "C:\Users\beren\Anna_AI\BASE\tools\installed\" -Recurse -Force
```

**Expected Result:**
- Command completes
- Discord tool is copied

### Part 7D: Copy Web Fetch Tool (Recommended)

**Do this:**
1. Paste this command and press Enter:
```powershell
Copy-Item "C:\Users\beren\AI_Agent_Tools\web_fetch" -Destination "C:\Users\beren\Anna_AI\BASE\tools\installed\" -Recurse -Force
```

**Expected Result:**
- Command completes
- Web fetch tool is copied

### Part 7E: Enable Tools in controls.py

**Do this:**
1. Open File Explorer
2. Navigate to: `C:\Users\beren\Anna_AI\personality\`
3. Open: `controls.py` with Notepad
4. Find these lines:
   ```python
   USE_SOUND_EFFECTS = False
   USE_DISCORD = False
   USE_WEB_FETCH = False
   ```
5. Change `False` to `True`:
   ```python
   USE_SOUND_EFFECTS = True
   USE_DISCORD = True
   USE_WEB_FETCH = True
   ```
6. Save: **Ctrl+S**

**Expected Result:**
- Tools are enabled
- File saved

---

## STEP 8: Final System Test

### Part 8A: Start Ollama (Required)

**Do this:**
1. Open PowerShell or Command Prompt
2. Type: `ollama serve`
3. Press Enter
4. Keep this window open

**Expected Result:**
- Shows: "Listening on 127.0.0.1:11434"
- Window stays open (don't close it)

### Part 8B: Start Warudo

**Do this:**
1. Launch Warudo (from Steam or desktop)
2. Make sure avatar is loaded (Anna visible)
3. Verify Network settings:
   - WebSocket Server: Running
   - Port: 19190

**Expected Result:**
- Warudo window open
- Avatar visible
- Network status shows "Running"

### Part 8C: Start Anna AI

**Do this:**
1. Open File Explorer
2. Navigate to: `C:\Users\beren\Anna_AI\`
3. Double-click: `START-OPTIMIZED.bat`
4. Anna AI GUI opens

**Expected Result:**
- GUI window appears
- Shows status: "Ready"
- Chat input box visible

### Part 8D: Test the System

**Do this:**
1. In Anna AI chat box, type: `"Hello Anna, can you hear me?"`
2. Click Send (or press Enter)
3. Wait 5 seconds

**Watch for:**
1. ✓ Agent responds in chat
2. ✓ Agent voice plays (audio)
3. ✓ Warudo character's lips move in sync with speech

**Expected Result - All Three Happen**:
- Chat shows response
- You hear voice
- Lips move on avatar

### If Everything Works ✓

**Congratulations!**
Your Anna AI is now:
- ✓ Thinking (processing text)
- ✓ Speaking (TTS audio)
- ✓ Animated (3D avatar)
- ✓ Fully functional

---

## Troubleshooting

### If VB-Audio Not Showing

**Problem**: CABLE devices don't appear after restart

**Solution**:
1. Restart computer again (sometimes needs 2 restarts)
2. Check Device Manager for "VB-Audio Cable"
3. If still missing, reinstall:
   - Download again from https://vb-audio.com/Cable/
   - Run installer as admin again
   - Restart again

### If Warudo Won't Start

**Problem**: Warudo crashes or won't open

**Solution**:
1. Make sure GPU drivers are updated
2. Download latest from NVIDIA: https://www.nvidia.com/Download/
3. Restart computer
4. Try launching Warudo again

### If Lips Don't Move

**Problem**: Avatar loads but lips don't sync

**Solution**:
1. Check Warudo Audio settings:
   - Lip Sync Input: CABLE Output (not Input!)
   - Try restarting Warudo
2. Check that agent is actually speaking:
   - Listen for audio from agent
   - If no audio, VB-Audio might not be set in bot_info.py

### If Agent Doesn't Respond

**Problem**: Chat sends but no response

**Solution**:
1. Is Ollama running? (should see window open)
2. Run system check: `system-check.bat`
3. Check logs in: `BASE\logs\` folder
4. Restart Anna AI

---

## When Stuck

**If anything doesn't work:**

1. Tell me exactly which step you're on
2. Tell me what happened (error message? nothing happened?)
3. I'll provide specific fix
4. We'll solve it together

**You're not alone in this - let's get it working!**

---

**Status**: Ready to follow these steps  
**Time Estimate**: 1-2 hours total  
**Difficulty**: Easy (mostly clicking buttons)

**Next**: Tell me when you're starting, and which step you need help with!
