# Project Lazarus — Gear 360 SM-C200 Resurrection

> Desktop Edition v3.0 · Built for Mac mini M4

A complete web app that brings the Samsung Gear 360 (SM-C200) back from the dead. Control the camera, stitch dual-fisheye photos into 4K equirectangular 360° images, and process videos — all from your Mac.

---

## What's In The Box

```
lazarus/
├── Lazarus.html            ← The app (single-file, runs in browser)
├── lazarus-server.py       ← Python proxy server (routes to camera)
├── start-lazarus.command   ← Double-click launcher for macOS
└── README.md               ← You're reading this
```

---

## Quick Start (3 Steps)

### 1. Download & Place Files

Put all 4 files in a folder. We recommend:

```bash
mkdir ~/lazarus
```

Move `Lazarus.html`, `lazarus-server.py`, `start-lazarus.command`, and `README.md` into `~/lazarus/`.

### 2. Make the Launcher Executable (One Time)

Open Terminal and run:

```bash
chmod +x ~/lazarus/start-lazarus.command
```

This only needs to be done once. After this, you can double-click the file in Finder.

### 3. Launch

**Option A — Double-click in Finder:**
Navigate to `~/lazarus/` and double-click `start-lazarus.command`. It starts the server and opens your browser automatically.

**Option B — Terminal:**
```bash
cd ~/lazarus
python3 lazarus-server.py
```
Then open http://localhost:8080 in Safari or Chrome.

---

## Connecting to the Gear 360

The in-app wizard walks you through this, but here's the full guide:

### Step 1: Power On the Camera

- Hold the **power button** for 2 seconds
- Wait for the OLED screen to show **"Connect to..."**
- If it shows a different mode, press the **Menu** button on top to cycle to Wi-Fi/connection mode

### Step 2: Connect Mac Wi-Fi to Camera

- Click the **Wi-Fi icon** in the Mac menu bar
- Look for a network named like: `Gear 360(XXXX).OSC`
- The password is the **8-digit number** on line 2 of the camera's OLED display

> **Note:** Your Mac will lose internet while connected to the camera. That's expected — the camera creates its own isolated Wi-Fi network.

> **Tip:** If the password isn't visible, turn the camera off and on again. It generates a new password each session.

### Step 3: Start the Server

Double-click `start-lazarus.command` or run `python3 lazarus-server.py` in Terminal.

### Step 4: Open the App

The browser opens automatically with the double-click launcher. If using Terminal, navigate to:

```
http://localhost:8080
```

### Step 5: Connect in the App

Click the **⚡ Connect** button in the Camera tab. You should see battery and storage stats populate.

---

## Features

### 📷 Camera Control
- **Connect** to Gear 360 via OSC API
- **Photo capture** (click or press `Space`)
- **Video recording** (start with `R`)
- **File browser** — list and download images from the camera
- **Live stats** — battery, storage, session ID

### 🧩 Dual-Fisheye Stitcher
- **WebGL shader** stitches dual-fisheye images into equirectangular projection
- **Drag & drop** images directly onto the viewport
- **5 calibration sliders** — X/Y offset, blend width, FOV, radius
- **Save calibration** — persists in browser localStorage
- **4K export** (4096×2048) with XMP 360° metadata
- Google Photos, Facebook, YouTube all recognize the 360° metadata automatically

### 🎬 Video Lab
- **FFmpeg.wasm** processes dual-fisheye video to equirectangular 360°
- Runs **entirely in the browser** — video never leaves your Mac
- Uses `v360` filter with your calibration settings
- Requires SharedArrayBuffer (provided by server's COOP/COEP headers)

---

## Keyboard Shortcuts

| Key | Action |
|------|--------|
| `1` | Switch to Camera tab |
| `2` | Switch to Stitch tab |
| `3` | Switch to Video Lab tab |
| `Space` | Capture photo (when connected) |
| `R` | Start recording video |
| `⌘S` | Save stitched 360° image |
| `Esc` | Close setup wizard |

---

## Architecture

```
┌──────────┐        ┌──────────────────┐        ┌────────────┐
│  Browser  │──────▶│  lazarus-server   │──────▶│  Gear 360  │
│ :8080     │◀──────│  (Python proxy)   │◀──────│ 192.168.   │
│           │       │  + CORS headers   │       │  107.1     │
│ Lazarus   │       │  + COOP/COEP      │       │            │
│  .html    │       │                   │       │  OSC API   │
└──────────┘        └──────────────────┘        └────────────┘
```

**Why a proxy?** The Gear 360's HTTP server doesn't send CORS headers and can't be modified. Browsers block cross-origin requests from any HTTPS page (like GitHub Pages) to the camera's HTTP server. The Python proxy makes everything same-origin — the browser talks to localhost, the proxy talks to the camera. Zero restrictions.

The proxy also injects:
- **CORS headers** — `Access-Control-Allow-Origin: *`
- **COOP/COEP headers** — enables `SharedArrayBuffer` for FFmpeg.wasm multi-threading

---

## Python Requirements

**Python 3** — that's it. No pip packages needed.

macOS comes with Python 3 pre-installed on recent versions. To check:

```bash
python3 --version
```

If not installed:
- **Homebrew:** `brew install python`
- **Direct:** https://www.python.org/downloads/macos/

---

## Troubleshooting

### "Camera not reachable"
1. Is the Gear 360 powered on and in Wi-Fi mode?
2. Is your Mac connected to the camera's Wi-Fi network (not your home Wi-Fi)?
3. Try: `ping 192.168.107.1` in Terminal — you should get responses
4. Turn camera off/on and reconnect

### "Port 8080 already in use"
Another instance of the server (or another app) is using port 8080:
```bash
# Find what's using it
lsof -i :8080

# Kill it
kill -9 <PID>
```

### Video Lab shows "SharedArrayBuffer unavailable"
This means the COOP/COEP headers aren't being sent. Make sure you're accessing the app through `http://localhost:8080` (served by the proxy), not opening the HTML file directly.

### Exported 360° image not recognized
The exporter injects Google's XMP GPano metadata. If a platform doesn't recognize it:
- **Google Photos:** Upload via web — it auto-detects
- **Facebook:** Upload as photo — it auto-detects
- **YouTube:** Only for video uploads
- **Instagram:** Does not support 360°

### Camera session expires
The Gear 360 closes inactive sessions after a while. Just click **Connect** again.

### Can I use Chrome or Safari?
Both work. Safari may not support `SharedArrayBuffer` even with COOP/COEP headers, so the Video Lab might not work in Safari. Chrome is recommended for full functionality.

---

## Camera Reference

### Gear 360 SM-C200 Specs
- **Sensors:** 2× 15MP CMOS
- **Photo resolution:** 7776×3888 (dual-fisheye)
- **Video:** 3840×1920 @ 30fps
- **Storage:** microSD (up to 200GB)
- **Battery:** 1350mAh
- **API:** Open Spherical Camera (OSC) v1

### OSC Endpoints Used
- `GET /osc/info` — Camera model, firmware
- `POST /osc/commands/execute` — All camera operations
  - `camera.startSession` — Open connection
  - `camera.takePicture` — Capture photo
  - `camera._startCapture` — Begin video
  - `camera._stopCapture` — End video
  - `camera.listImages` — Browse files
  - `camera.getImage` — Download file
  - `camera.getOptions` — Battery, storage

---

## Files Explained

### `Lazarus.html`
The entire app in a single HTML file. Contains:
- CSS (desktop layout with sidebar navigation)
- HTML (camera controls, stitch viewport, video lab)
- JavaScript (OSC client, WebGL stitch engine, FFmpeg.wasm integration)
- Three.js loaded from CDN

### `lazarus-server.py`
~120 lines of Python. No dependencies beyond the standard library. Handles:
- Static file serving (serves `Lazarus.html` at `/`)
- Request proxying (`/osc/*` → `http://192.168.107.1/osc/*`)
- CORS and COOP/COEP header injection
- Minimal logging (camera requests shown with 📡)

### `start-lazarus.command`
macOS double-clickable shell script. It:
1. Checks Python 3 is installed
2. Checks all files exist
3. Checks port 8080 is free
4. Starts the server
5. Opens your default browser to `http://localhost:8080`

---

## License

This project resurrects abandoned hardware. Samsung discontinued the Gear 360 Manager app. The camera still works — it just needed someone to talk to it.

Built with love for hardware that deserves better.
