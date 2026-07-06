# Getting Started with Lobby Display

This guide covers using the web interface to manage your digital signage content.

## Accessing the Web Interface

Open a web browser and navigate to:

- `http://lobby-display.local:5000` (mDNS, if supported)
- `http://[your-pi-ip]:5000` (IP address)

The dashboard shows your device name, current playlist, and quick actions.

## Uploading Images

1. Click **Upload** in the navigation menu
2. (Optional) Select a playlist to add images to automatically
3. Drag and drop images or click to browse
4. Click **Upload**

Supported formats: PNG, JPG, JPEG, GIF, BMP, WebP

### Tips

- Images are automatically optimized for display
- Name your files descriptively for easier playlist management
- Upload multiple images at once

## Creating Playlists

Playlists allow you to organize content into different sets (e.g., "Morning", "Event Mode", "Default").

### Create a New Playlist

1. Go to **Playlists**
2. Enter a name in the "Create New Playlist" section
3. Click **Create**

### Add Images to a Playlist

1. Click **Edit** next to a playlist
2. In the "Add Images" section, select images from the dropdown
3. Click **Add Selected**

### Reorder Images

1. Open a playlist for editing
2. Images are displayed in order
3. Drag and drop to reorder (or use the save button after manual ordering)

### Remove Images

Click **Remove** next to any image in the playlist editor.

## Setting Image Duration

### Global Default

1. Go to **Settings**
2. Change "Default Duration (seconds)"
3. Click **Save Settings**

This applies to all images that don't have a custom duration.

### Per-Image Duration

1. Edit a playlist
2. Each image has a duration field (in seconds)
3. Enter a custom value or leave blank to use the global default
4. Click **Save Changes**

## Switching Playlists

To change what's currently displaying:

1. Go to **Playlists**
2. Click **Set Active** next to the desired playlist

The display will immediately switch to the new playlist.

## Configuring Display Settings

### Device Name

Change the display name to easily identify it on your network:

1. Go to **Settings**
2. Change "Display Name"
3. Save

The mDNS address updates automatically (e.g., `http://conference-room.local:5000`).

### Screen Rotation

**Software Rotation** (immediate, no reboot):

- Settings → Rotation → Select angle → Save

**Hardware Rotation** (better performance, requires reboot):

- Edit `/boot/config.txt`:
  - display_rotate=0 # 0, 1 (90°), 2 (180°), or 3 (270°)
- Reboot: `sudo reboot`

### Resolution

Select the output resolution in Settings. Common options:

- 1920x1080 (1080p)
- 1280x720 (720p)
- 1024x768

## Managing the Display

### Start/Stop from Web

The web interface shows current service status. To control from the command line:

```bash
# Check status
sudo systemctl status lobby-web
sudo systemctl status lobby-display

# Stop display (blank screen)
sudo systemctl stop lobby-display

# Start display
sudo systemctl start lobby-display

# Restart both
sudo systemctl restart lobby-web lobby-display
```

## Reboot System

From the terminal:

```bash
sudo reboot
```

## Best Practices

### Organizing Content

- Create playlists for different times of day or events
- Use descriptive names: "Lobby-Morning", "Lobby-Afternoon", "Event-OpenHouse"
- Keep a "Default" playlist as fallback

### Image Preparation

- Use high-quality images (the display will scale them)
- Recommended resolution: 1920x1080 or higher
- Aspect ratio: Match your display (usually 16:9)

### Performance

- For best performance with 90°/270° rotation, use hardware rotation in `/boot/config.txt`
- Limit individual image file sizes for faster loading
- The Pi 3 handles 1080p well; Pi 4/5 can do 4K

### Backup

Your data is stored in `/opt/lobby-display/`:

- `uploads/` - Image files
- `database.db` - Playlists and metadata
- `config.json` - Settings

Back up this directory to preserve your content.

## Troubleshooting

### Images not showing

- Check that images uploaded successfully (Upload page shows file list)
- Verify the playlist has images and is set as active
- Check display service is running:

    ```bash
    sudo systemctl status lobby-display
    ```

### Web interface inaccessible

- Verify services are running:

    ```bash
    sudo systemctl status lobby-web
    ```

- Check network connection on Pi:

    ```bash
    ping google.com
    ```

- Try accessing via IP instead of hostname

### Display shows black screen

- No images in active playlist
- Display service not running
- Check logs:

    ```bash
    sudo journalctl -u lobby-display -n 50
    ```

### Keyboard Shortcuts (Physical Display)

When viewing the physical display:

- **ESC** - Exit display (if running in foreground)
- **Space** - Advance to next image immediately
For installation instructions, see [install.md](install.md).
For technical details, see the [README](./README.md).
