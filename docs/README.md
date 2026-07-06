# Lobby Display

A standalone digital signage solution for Raspberry Pi that operates entirely without external servers or internet connectivity. Perfect for lobbies, conference rooms, retail displays, or any environment needing rotating visual content.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Fully Standalone** - No cloud services, no subscriptions, no internet required
- **Web-Based Management** - Upload images and manage playlists from any device on your network
- **Multiple Playlists** - Create different content sets and switch between them instantly
- **Per-Image Timing** - Set custom durations for individual images or use global defaults
- **mDNS Discovery** - Access displays by name (e.g., `http://lobby-display.local:5000`)
- **Software Rotation** - 0°, 90°, 180°, 270° rotation support
- **AppImage Distribution** - Single executable file, no dependency installation

## Supported Hardware

| Device | 32-bit OS | 64-bit OS |
| -------- | ----------- | ----------- |
| Raspberry Pi 3 | ✅ | ✅ |
| Raspberry Pi 4 | ✅ | ✅ (recommended) |
| Raspberry Pi 5 | ✅ | ✅ (recommended) |

## Quick Start

```bash
# Download the latest AppImage
wget https://github.com/commputethis/lobby-display/releases/download/v1.0.0/lobby-display-1.0.0-aarch64.AppImage

# Make executable and install
chmod +x lobby-display-1.0.0-aarch64.AppImage
./lobby-display-1.0.0-aarch64.AppImage --install

# Start services
sudo systemctl start lobby-web lobby-display

# Access web interface
# http://lobby-display.local:5000 (or your Pi's IP address)
```

## Architecture

```text
┌─────────────────────────────────────┐
│  Raspberry Pi                       │
│  ┌─────────────┐   ┌─────────────┐  │
│  │ Web Server  │   │   Display   │  │
│  │  (Flask)    │   │  (Pygame)   │  │
│  │   :5000     │   │   HDMI Out  │  │
│  └──────┬──────┘   └─────────────┘  │
│         │                           │
│    Web UI for management            │
│    (upload, playlists, settings)    │
└─────────────────────────────────────┘
```

## Documentation

- [Installation Guide](./install.md) - Detailed installation instructions
- [Getting Started](./gettingstarted.md) - Using the web interface, creating playlists, managing content
- Building from Source - See [build.md](./build.md) for instructions on creating your own AppImage from source.

License
MIT License - See LICENSE file for details.
