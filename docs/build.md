# Building from Source

This guide covers building the Lobby Display AppImage from source code.

## Prerequisites

### Required Software

- Raspberry Pi OS (64-bit recommended) or any Debian-based Linux
- Python 3.11 or newer
- Git

### Install Build Dependencies

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv wget git
```

## Clone the Repository

```bash
git clone https://github.com/yourusername/lobby-display.git
cd lobby-display
```

## Project Structure

lobby-display/  
├── build.sh              # Main build script  
├── src/                  # Source code  
│   ├── app.py           # Flask web application  
│   ├── display.py       # Slideshow display service  
│   ├── mdns.py          # mDNS broadcaster  
│   ├── AppRun           # AppImage entry point  
│   ├── lobby-display.desktop  
│   ├── lobby-display.png (optional)  
│   ├── templates/       # HTML templates  
│   └── static/          # Static assets  
└── docs/                # Documentation  

## Build Process

### Step 1: Make Scripts Executable

```bash
chmod +x src/AppRun
chmod +x build.sh
```

### Step 2: Run the Build

```bash
./build.sh
```

The build script will:

1. Create a Python virtual environment (`build_venv/`)
2. Install dependencies (Flask, Pillow, Pygame, Zeroconf)
3. Create `AppDir/` structure
4. Copy Python interpreter and packages
5. Copy application source files
6. Download `appimagetool` (if not present)
7. Build the AppImage
8. Clean up temporary directories

### Step 3: Verify Output

```bash
ls -lh *.AppImage
```

You should see:

- `lobby-display-1.0.0-aarch64.AppImage` (or `armhf` for 32-bit)

File size should be approximately 50-150 MB depending on included packages.

## Build Options

### For 32-bit Systems (ARMHF)

Edit `build.sh` and change:

```bash
ARCH="armhf"  # instead of "aarch64"
```

And download the appropriate appimagetool:

```bash
wget "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-armhf.AppImage"
```

### Custom Python Version

If your system has a specific Python version, the build should auto-detect it. However, if you need to force a specific version:

```bash
# Create venv with specific Python
python3.11 -m venv build_venv
```

Then modify `AppRun` to match:

```bash
PYTHON_VERSION="3.11"  # Hardcode instead of auto-detect
```

### Development Build (No AppImage)

For faster testing during development, run the application directly:

```bash
cd src
python3 -m venv venv
source venv/bin/activate
pip install flask pillow pygame zeroconf

# Run web server
python3 app.py

# In another terminal, run display
python3 display.py
```

This is useful for testing changes before building the full AppImage.

## Troubleshooting Builds

### "No module named 'flask'" in AppImage

The Python packages aren't being found. Check:

- `AppDir/usr/lib/` contains the packages
- `AppRun` PYTHONPATH matches your Python version
- See TROUBLESHOOTING.md for more details

### appimagetool download fails

Download manually:

```bash
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-aarch64.AppImage
chmod +x appimagetool-aarch64.AppImage
```

Then re-run `build.sh`.

### Build takes too long

The first build downloads and installs all dependencies. Subsequent builds are faster if you keep `build_venv/`, but the script cleans it up by default. Comment out the cleanup line in `build.sh` for faster iterative builds:

```bash
# Comment this out for faster rebuilds
# rm -rf AppDir build_venv
```

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/build.yml`:

```yaml
name: Build AppImage

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup QEMU
        uses: docker/setup-qemu-action@v2
        with:
          platforms: arm64
      
      - name: Build
        uses: uraimo/run-on-arch-action@v2
        with:
          arch: aarch64
          distro: bullseye
          run: |
            apt-get update
            apt-get install -y python3-pip python3-venv wget
            ./build.sh
      
      - name: Upload Artifact
        uses: actions/upload-artifact@v3
        with:
          name: lobby-display-appimage
          path: "*.AppImage"
```

### Packaging for Distribution

#### Create Release Checklist

1. Update version in `build.sh`
2. Update CHANGELOG.md
3. Run full build and test
4. Create GitHub release with AppImage attached
5. Update documentation links

#### Version Numbering

Follow semantic versioning:

- 1.0.0 - Major release
- 1.1.0 - New features
- 1.1.1 - Bug fixes

Update VERSION in build.sh:

```bash
VERSION="1.1.0"
```

## Advanced Build Options

### Custom AppImage Name

Modify the output filename in `build.sh`:

```bash
./appimagetool-aarch64.AppImage AppDir "my-custom-name-${VERSION}.AppImage"
```

### Include Additional Python Packages

Add to the pip install line in `build.sh`:

```bash
pip install flask pillow pygame zeroconf my-custom-package
```

### Exclude Unnecessary Files

Add to `build.sh` before appimagetool runs to reduce size:

```bash
# Remove unnecessary files
find AppDir -name "*.pyc" -delete
find AppDir -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
```

## Next Steps

After building:

- Test the AppImage:

    ```bash
    ./lobby-display-1.0.0-aarch64.AppImage --install`
    ```

- See [install.md](./install.md) for installation
- See [gettingstarted.md](./gettingstarted.md) for usage

## Getting Help

- Open an issue on GitHub
- Check [troubleshooting.md](./troubleshooting.md)
- Review existing build logs:

    ```bash
    ./build.sh 2>&1 | tee build.log
    ```
