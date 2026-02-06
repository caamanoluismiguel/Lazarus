# Project Lazarus — Gear 360 Resurrection

**A fully offline PWA that resurrects the discontinued Samsung Gear 360 (SM-C200, 2016).**

Controls the camera, previews live content, stitches dual-fisheye images into equirectangular 360° photos, and processes video—all directly in the browser with zero backend.

![License](https://img.shields.io/badge/license-MIT-blue)
![Platform](https://img.shields.io/badge/platform-Android%20Chrome-green)
![Camera](https://img.shields.io/badge/camera-SM--C200-red)

---

## Features

- **Camera Control** — Full OSC API client: connect, capture photos, record video, browse files
- **Real-Time Stitching** — WebGL shader converts dual-fisheye → equirectangular with live preview
- **Calibration Mode** — Fine-tune lens offset (±5px), blend width, FOV, and circle radius per camera unit
- **360° Export** — Saves 4096×2048 JPEG with XMP GPano metadata (auto-detected by Google Photos, Facebook, VR viewers)
- **Video Processing** — FFmpeg.wasm with v360 filter for on-device video stitching
- **Fully Offline** — Service Worker caches everything; works without internet after first load

## Quick Start

### Option A: GitHub Pages (Easiest)

1. Fork this repo
2. Go to **Settings → Pages → Source: Deploy from branch → `main` / `root`**
3. Your app is live at `https://yourusername.github.io/project-lazarus/`

### Option B: Local

```bash
# Any static server works. Example with Python:
cd project-lazarus
python3 -m http.server 8080

# Or Node:
npx serve .
```

Open `http://localhost:8080` in Chrome.

## Phone Setup (One-Time)

The Gear 360 serves content over HTTP, but Chrome requires HTTPS. You need to whitelist the camera's IP:

1. Open Chrome on your Android phone
2. Navigate to:
   ```
   chrome://flags/#unsafely-treat-insecure-origin-as-secure
   ```
3. In the text field, enter:
   ```
   http://192.168.107.1
   ```
4. Set the flag to **Enabled**
5. Tap **Relaunch**

This persists across restarts. It only affects the camera's IP—no other sites are affected.

## Usage

1. **Turn on your Gear 360** and wait for the Wi-Fi LED
2. On your phone, **connect to the camera's Wi-Fi** network (e.g., `Gear 360(XXXX)`)
3. Open the PWA in Chrome
4. Tap **Connect** in the Camera tab
5. Capture a photo → it loads into the **Stitch** tab automatically
6. Adjust calibration if needed → tap **Save 360°**
7. The image downloads to your phone with proper 360° metadata

## How the Stitching Works

The SM-C200 outputs a single image containing two circular fisheye projections side-by-side. The WebGL fragment shader:

1. Maps each output pixel to spherical coordinates (longitude, latitude)
2. Converts to a 3D direction vector on the unit sphere
3. Projects back into the appropriate fisheye circle using equidistant projection
4. Blends in the overlap zone with a smooth cosine weight

The calibration sliders adjust the assumed center of each fisheye circle to compensate for manufacturing tolerances.

## Video Processing

The Video Lab uses [FFmpeg.wasm](https://github.com/ffmpegwasm/ffmpeg.wasm) to run the `v360` filter entirely on-device:

```
v360=dfisheye:equirect:ih_fov=195:iv_fov=195
```

**Note:** For the multithreaded FFmpeg build (faster), the server must send these headers:
```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

GitHub Pages does **not** send these headers, so video processing falls back to single-threaded mode. For full speed, self-host with the headers configured (see `_headers` file or use Cloudflare Pages / Vercel).

## Repo Structure

```
project-lazarus/
├── index.html          # Complete app (single file, ~1650 lines)
├── manifest.json       # PWA manifest
├── sw.js               # Service Worker for offline caching
├── favicon.png         # Browser tab icon
├── .nojekyll           # Tells GitHub Pages to skip Jekyll processing
├── _headers            # Cloudflare Pages header config (optional)
├── icons/
│   ├── icon-192.png    # PWA icon
│   ├── icon-512.png    # PWA icon (large)
│   └── icon-512-maskable.png  # Android adaptive icon
└── README.md
```

## Hosting with Full Headers (Optional)

If you want multithreaded FFmpeg, deploy to a platform that supports custom headers:

**Cloudflare Pages** — Uses the `_headers` file in this repo automatically.

**Vercel** — Add to `vercel.json`:
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "Cross-Origin-Opener-Policy", "value": "same-origin" },
        { "key": "Cross-Origin-Embedder-Policy", "value": "require-corp" }
      ]
    }
  ]
}
```

**Nginx:**
```nginx
add_header Cross-Origin-Opener-Policy "same-origin" always;
add_header Cross-Origin-Embedder-Policy "require-corp" always;
```

## Compatibility

| Device | Status | Notes |
|--------|--------|-------|
| Samsung S21 (Android 14) | ✅ Primary target | Full support |
| Pixel 7+ | ✅ Works | Tested |
| Any Android Chrome 100+ | ✅ Works | Need Chrome flag |
| iOS Safari | ⚠️ Partial | No FFmpeg (no SharedArrayBuffer), stitch works |
| Desktop Chrome | ✅ Works | With Vite proxy for camera access |

## Camera Compatibility

Designed for the **Samsung Gear 360 SM-C200 (2016)**. The 2017 model (SM-R210) uses a different API and is not yet supported.

## License

MIT
