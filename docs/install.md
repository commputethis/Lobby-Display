# Installation Guide

This guide covers installing Lobby Display on your Raspberry Pi.

## Prerequisites

- Raspberry Pi 3, 4, or 5
- Raspberry Pi OS (32-bit or 64-bit) installed and configured
- Network connection (Ethernet or WiFi)
- HDMI display connected

## Determine Your Architecture

Before downloading, check if you're running 32-bit or 64-bit OS:

```bash
uname -m
```

- `armv7l` = 32-bit (use `armhf` AppImage)
- `aarch64` = 64-bit (use `aarch64` AppImage)

## Step 1: Download the AppImage

### Option A: Download from Releases (Recommended)

```bash
# For 64-bit systems (most common)
wget https://github.com/yourusername/lobby-display/releases/download/v1.0.0/lobby-display-1.0.0-aarch64.AppImage

# For 32-bit systems
wget https://github.com/yourusername/lobby-display/releases/download/v1.0.0/lobby-display-1.0.0-armhf.AppImage
```

### Option B: Build from Source

If you prefer to build your own AppImage:

```bash
git clone https://github.com/yourusername/lobby-display.git
cd lobby-display
chmod +x build.sh
./build.sh
```

The AppImage will be created in the project root directory.

## Step 2: Make Executable

```bash
chmod +x lobby-display-1.0.0-aarch64.AppImage
```

### Step 3: Install System Services

Run the AppImage with the `--install` flag. This creates the data directory and systemd services:

```bash
./lobby-display-1.0.0-aarch64.AppImage --install
```

You will see output similar to:

```text
Installing Lobby Display...
Installed for user: pi
Start with: sudo systemctl start lobby-web lobby-display
Web interface: http://192.168.1.100:5000
```

## Step 4: Start the Services

```bash
sudo systemctl start lobby-web lobby-display
```

To verify they're running:

```bash
sudo systemctl status lobby-web
sudo systemctl status lobby-display
```

Both should show `active (running)`.

## Step 5: Enable Auto-Start (Optional)

To automatically start on boot:

```bash
sudo systemctl enable lobby-web lobby-display
```

## Step 6: Access the Web Interface

Open a web browser on any device on your network:

- Via mDNS: `http://lobby-display.local:5000`
- Via IP: `http://[your-pi-ip-address]:5000`

To find your Pi's IP address:

```bash
hostname -I
```

## Troubleshooting

### Services fail to start

Check logs:

```bash
sudo journalctl -u lobby-web -n 50
sudo journalctl -u lobby-display -n 50
```

### Port 5000 already in use

Change the port in the service file or stop the conflicting service.

### Cannot access web interface

- Verify the Pi is on the same network as your computer
- Check firewall settings: `sudo ufw status` (if using UFW)
- Try accessing via IP address instead of mDNS hostname

### mDNS not working (can't use .local address)

Access via IP address instead. mDNS requires:

- macOS/iOS: Works natively
- Linux: Install `avahi-daemon (sudo apt install avahi-daemon)`
- Windows: Install Bonjour Print Services

## Updating

To update to a new version:

1. Download the new AppImage
2. Run with `--install` flag:

    ````bash
    `./lobby-display-1.1.0-aarch64.AppImage --install
    ````

3. Restart services:

    ```bash
    sudo systemctl restart lobby-web lobby-display
    ```

Your data (uploads, playlists, settings) in `/opt/lobby-display/` will be preserved.

## Uninstallation

To completely remove Lobby Display:

```bash
# Stop and disable services
sudo systemctl stop lobby-web lobby-display
sudo systemctl disable lobby-web lobby-display

# Remove service files
sudo rm /etc/systemd/system/lobby-web.service
sudo rm /etc/systemd/system/lobby-display.service
sudo systemctl daemon-reload

# Remove data directory (WARNING: This deletes all uploaded images)
sudo rm -rf /opt/lobby-display

# Remove AppImage (manual)
rm lobby-display-*.AppImage
```

## Next Steps

See [GETTING_STARTED.md](./gettingstarted.md) for instructions on using the web interface to upload images and create playlists.
