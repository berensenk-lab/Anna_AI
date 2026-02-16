# Installation Checklist - Print or Reference This

## STEP 1: VB-Audio Virtual Cable Installation

- [ ] Step 1A: Download from https://vb-audio.com/Cable/
- [ ] Step 1B: Extract ZIP file to Downloads folder
- [ ] Step 1C: Right-click VBCABLE_Setup_x64.exe → Run as admin
- [ ] Step 1D: Click "Install Driver" button
- [ ] Step 1E: Restart computer

**Verification**:
- [ ] After restart, right-click speaker icon → Sound settings
- [ ] Look for "CABLE Input" and "CABLE Output" in device list
- [ ] ✓ If you see both, VB-Audio is installed!

**If stuck**: See "Troubleshooting" section in STEP-BY-STEP-INSTALLATION.md

---

## STEP 2: Warudo Installation

- [ ] Step 3A: Download Warudo
  - Option A (Easier): Steam https://store.steampowered.com/app/2704600/Warudo/
  - Option B: Direct https://warudo.app/download
- [ ] Step 3B: Install (takes 5-10 minutes, ~5GB)
- [ ] Step 3B: Click "Play" or launch Warudo

**Configuration**:
- [ ] Step 4B: Settings → Audio → Lip Sync Input: CABLE Output
- [ ] Step 4B: Settings → Audio → Sample Rate: 48000 Hz
- [ ] Step 4B: Settings → Audio → Buffer Size: 512 or 1024
- [ ] Step 4C: Settings → Network → Enable WebSocket Server [✓]
- [ ] Step 4C: Settings → Network → Port: 19190
- [ ] Step 4C: Settings → Network → Enable External Connections [✓]
- [ ] Step 4D: Settings → Graphics → Quality: High

**Avatar**:
- [ ] Step 5A: File → Import Model → Select Anna.vrm
  - Location: C:\Users\beren\Anna_AI\personality\avatar\Anna.vrm
- [ ] Step 5B: Avatar loads (wait 10-30 seconds)
- [ ] ✓ 3D character visible

**If stuck**: See "Troubleshooting" section in STEP-BY-STEP-INSTALLATION.md

---

## STEP 3: Configure API Tokens (Optional)

- [ ] Step 6A: Open .env file with Notepad
  - Location: C:\Users\beren\Anna_AI\.env

**Discord** (if you want it):
- [ ] Step 6B: Go to https://discord.com/developers/applications
- [ ] Step 6B: Create Application → Add Bot → Copy token
- [ ] Step 6B: Paste token after `DISCORD_BOT_TOKEN=`

**Twitch** (if you want it):
- [ ] Step 6C: Go to https://twitchapps.com/tmi/
- [ ] Step 6C: Authorize → Copy token
- [ ] Step 6C: Paste token after `TWITCH_OAUTH_TOKEN=`
- [ ] Step 6C: Set `TWITCH_CHANNEL=your_channel_name`

**YouTube** (if you want it):
- [ ] Step 6D: Go to https://console.cloud.google.com/apis/
- [ ] Step 6D: Create Project → Enable YouTube API → Copy key
- [ ] Step 6D: Paste key after `YOUTUBE_API_KEY=`

**Finish**:
- [ ] Step 6E: Save file (Ctrl+S)

---

## STEP 4: Install AI Agent Tools (Optional)

**Copy Tools**:
- [ ] Step 7B: Copy sound_effects tool
- [ ] Step 7C: Copy discord_chat tool (optional)
- [ ] Step 7D: Copy web_fetch tool

**Command to copy** (paste in PowerShell as admin):
```
Copy-Item "C:\Users\beren\AI_Agent_Tools\sound_effects" -Destination "C:\Users\beren\Anna_AI\BASE\tools\installed\" -Recurse -Force
Copy-Item "C:\Users\beren\AI_Agent_Tools\discord_chat" -Destination "C:\Users\beren\Anna_AI\BASE\tools\installed\" -Recurse -Force
Copy-Item "C:\Users\beren\AI_Agent_Tools\web_fetch" -Destination "C:\Users\beren\Anna_AI\BASE\tools\installed\" -Recurse -Force
```

**Enable Tools**:
- [ ] Step 7E: Open controls.py (C:\Users\beren\Anna_AI\personality\controls.py)
- [ ] Step 7E: Change `USE_SOUND_EFFECTS = False` to `True`
- [ ] Step 7E: Change `USE_DISCORD = False` to `True` (optional)
- [ ] Step 7E: Change `USE_WEB_FETCH = False` to `True`
- [ ] Step 7E: Save (Ctrl+S)

---

## STEP 5: Final System Test

**Start Everything**:
- [ ] Step 8A: Open PowerShell → Type: `ollama serve` → Press Enter
  - Keep this window open!
- [ ] Step 8B: Launch Warudo
  - Verify Network: WebSocket Server Running on 19190
  - Verify Avatar: Anna visible
- [ ] Step 8C: Double-click START-OPTIMIZED.bat
  - Anna AI GUI opens

**Test the System**:
- [ ] Step 8D: Type in chat: "Hello Anna, can you hear me?"
- [ ] Step 8D: Send message
- [ ] Watch for all three happening:
  1. ✓ Agent responds in chat
  2. ✓ You hear voice audio
  3. ✓ Warudo lips move with speech

**Success**: All three = System working perfectly! ✓

---

## Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| VB-Audio not showing | Restart computer again (sometimes needs 2 restarts) |
| Warudo won't start | Update GPU drivers from NVIDIA, restart |
| Lips don't move | Check Warudo Audio settings - Lip Sync Input should be CABLE Output |
| Agent doesn't respond | Make sure Ollama is running, check logs |
| Can't find files | Use File Explorer, navigate to exact paths given |
| Commands don't work | Make sure you're in PowerShell as admin (right-click PowerShell icon → Run as admin) |

---

## Support When Stuck

**Tell me**:
1. Which step number you're on (1, 2, 3, etc.)
2. What you see on screen
3. Any error messages
4. What you expected to happen

**I'll help you fix it immediately.**

---

## Time Estimate

- VB-Audio: 10 minutes
- Warudo: 20-30 minutes
- API Tokens: 5-15 minutes (optional)
- Tools: 5 minutes (optional)
- Testing: 5 minutes
- **Total: 45-75 minutes**

---

## Key Reminders

✓ VB-Audio setup requires computer restart  
✓ Warudo downloads ~5GB (make sure you have space)  
✓ Keep Ollama window open while Anna AI runs  
✓ API tokens go in .env file (not in code)  
✓ Tools are optional but sound_effects is recommended  

---

**Ready to start? Tell me when you're on STEP 1 and I'll guide you through it!**
