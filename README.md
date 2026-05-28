# Helix Preset Viewer

A free, open-source visualizer for Line 6 Helix / HX Stomp / HX Effects preset files (`.hlx`).

Upload a preset file to explore its signal chain, block parameters, snapshots, footswitch assignments, IR slots, and MIDI/controller mappings — all in your browser, no account required.

![Screenshot placeholder](https://github.com/adman234/helix-viewer)

---

## Features

- **Signal chain visualization** — see DSP 1 and DSP 2 blocks laid out in order, including parallel A/B paths
- **Block details** — friendly model names, categories, and all parameter values with hover tooltips
- **Snapshot switching** — click any snapshot to preview how blocks change state across snapshots
- **Toggle blocks on/off** — change block state within the active snapshot
- **Remove blocks / DSPs** — soft-mark blocks for removal (shown with strikethrough); removed blocks are excluded when exporting
- **Export modified preset** — download the modified `.hlx` file with your changes applied
- **HX Stomp compatibility check** — block count banner warns when a preset exceeds the Stomp's 6-block limit
- **IR slot viewer** — see which impulse response slots are used and their UUIDs
- **MIDI / controller assignments** — view CC and controller mappings
- **Footswitch assignments** — see which footswitch controls each block
- **Print view** — print-friendly layout via browser print (`Ctrl+P`)
- **Session restore** — last loaded preset is saved in local storage and restored on next visit

---

## How to Use

1. **Open the app** in your browser (see deployment options below).
2. **Drop a `.hlx` file** onto the upload area, or click **Choose File** to browse.
3. The signal chain, block details, snapshots, and other sections load automatically.

### Working with blocks

- **Click a block chip** in the signal chain to scroll to its detail card.
- **ON / OFF button** — toggles the block in the active snapshot without affecting other snapshots.
- **Remove button** — marks the block for removal on export (strikethrough). Click **Undo Remove** to restore it. The block stays in view until you export.
- **Remove DSP** — marks an entire DSP path for removal. The chain collapses to a stub; click **Restore DSP** to undo.

### Snapshots

- Click any snapshot card to switch the active snapshot. Block states in the signal chain update to reflect that snapshot.
- The active snapshot is shown with an amber dot indicator.

### Exporting

Click **Export .hlx** to download the preset with your changes applied:
- Toggled ON/OFF states are saved.
- Removed blocks and DSPs are permanently deleted from the exported file.

---

## Deployment

### Docker (recommended)

Clone the repo and run with Docker Compose:

```bash
git clone https://github.com/adman234/helix-viewer.git
cd helix-viewer
docker compose up -d
```

The app will be available at `http://localhost:7860`.

Uploaded preset files are saved to `./uploads/` on the host.

### Unraid

Use the docker-compose above, or add the container manually:

- **Image:** `ghcr.io/adman234/helix-viewer:latest`
- **Port:** `7860:80`

### Running locally (no Docker)

Open `html/index.html` directly in any modern browser. The upload persistence backend won't be available, but all other features work fully client-side.

---

## Privacy

Preset files are parsed entirely in your browser — no data is sent to any external server. If the backend upload service is running (Docker deployment), uploaded files are saved locally to the `/uploads` directory on your own host only.

---

## Legal

This project is not affiliated with, endorsed by, or connected to Line 6, Inc. or Yamaha Corporation in any way. "Helix", "HX Stomp", "HX Edit", and related names are trademarks of their respective owners. Preset files are the property of their creators. Use at your own risk.

---

## Support

If you find this useful, you can [buy me a coffee](https://ko-fi.com/adman234).

Found a bug? [Open an issue](https://github.com/adman234/helix-viewer/issues/new).
