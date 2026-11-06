# 🚀 Google Flow YouTube Shorts Automation Engine

Automate viral 9:16 vertical YouTube Shorts (20–28 seconds) using **Google Flow**, **`flow-mcp`**, and **Antigravity / Claude Desktop**, featuring:
- 🎨 **Consistent Character Storytelling** (Pixar/Disney 3D animation style)
- 🔁 **3-Second Episode Recap** (`[ PICHLI BAAR / RECAP ]`)
- 🎙️ **Studio-Mastered Urdu Voiceover** (`ur-PK-AsadNeural` with parametric EQ & compression)
- 🔤 **Frame-Accurate Roman Urdu Captions** (Impact 2-tone kinetic typography)
- 🔔 **Spoken & Captioned Subscribe CTA**

---

## ⚡ 1-Click Setup for Any Computer (Windows)

### Step 1: Clone the Repo
```bash
git clone https://github.com/YOUR_USERNAME/flow-mcp.git
cd flow-mcp
```

### Step 2: Run the 1-Click Installer
Double-click `setup.bat` (or run in terminal):
```cmd
setup.bat
```
This script automatically:
1. Verifies **Node.js** and **Python 3.10+**.
2. Installs **FFmpeg** & **Google Chrome** via `winget` (if not already installed).
3. Installs all npm and python dependencies (`edge-tts`).
4. Compiles the TypeScript codebase (`npm run build`).
5. Configures Antigravity's MCP server configuration automatically in `~/.gemini/config/mcp_config.json`.
6. Launches Chrome in its isolated profile for your one-time login.

### Step 3: One-Time Google Sign-In
1. In the Chrome window that opens, sign in to your Google Account.
2. Go to [flow.google.com](https://flow.google.com) and click **"New project"**.
3. Keep Chrome open (or minimized) in the background.

---

## 🤖 The "Daily Episode" Master Prompt (For Antigravity or Claude)

Once your setup is done, you don't need to write code. Open **Antigravity** (or Claude) and paste this prompt:

```text
Create Episode [X] of my continuous YouTube Shorts series about Leo the Clockmaker.

Requirements:
1. Format: 9:16 vertical video at 720p using Omni 1.1 Flash.
2. Character Consistency: Lock appearance using "asset:Leo the Clockmaker".
3. 3-Second Recap: Start with a 3.8s recap from the previous episode with the banner "[ PICHLI BAAR / RECAP ]".
4. Story Continuity: Continue directly from the previous episode's cliffhanger.
5. Voiceover: Natural Urdu documentary voice (ur-PK-AsadNeural) with studio mastering (highpass, EQ warmth, compression, -14 LUFS).
6. Captions: Frame-accurate Roman Urdu subtitles in bold 2-tone Impact font (Yellow/White with 4.5px black outline).
7. Call to Action: End with a spoken and captioned Subscribe CTA ("Aagay ki kahani jaan'nay ke liye abhi subscribe karein! 🔔").
```

---

## 📁 File Structure & Output Location
All finished episodes and raw assets are automatically saved to:
```
C:\Users\<username>\flow-mcp-out\
 ├── _cast\                      <- Permanent character portrait assets
 ├── Leo_Time_Freeze\            <- Episode 1 files & final MP4
 └── Leo_Episode_2\              <- Episode 2 files & final MP4
```

---

## 🏷️ Standard YouTube Shorts Upload Template

* **Title**: `[Title of Episode] ⏳😱 | Episode [X] #shorts`
* **Hashtags**: `#Shorts #AIAnimation #UrduStories #TimeFreeze #AnimationShorts #ViralShorts #StoryTime #RomanUrdu #GoogleFlow #Cartoon`
* **Pinned Comment**: *"Agar aap ke paas yeh jaadui ghadi hoti toh aap kya karte? Comment mein batao! Agla part kal aa raha hai, subscribe zaroor karna!"*
