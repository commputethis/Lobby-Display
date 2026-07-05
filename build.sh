#!/bin/bash
set -e

# Clean up on exit
trap 'echo "Cleaning up..."; rm -rf AppDir build_venv' EXIT

APP_NAME="lobby-display"
VERSION="1.0.0"
ARCH="aarch64"  # Changed for 64-bit
SRC_DIR="src"

echo "Building $APP_NAME AppImage..."

# Install build dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv wget

# Create AppDir structure
rm -rf AppDir
mkdir -p AppDir/usr/{bin,lib,share/lobby-display}
mkdir -p AppDir/usr/share/lobby-display/{templates,static}

# Create virtual environment
python3 -m venv build_venv
source build_venv/bin/activate

# Install Python packages
pip install flask pillow pygame zeroconf

# Copy Python and packages
cp build_venv/bin/python3 AppDir/usr/bin/
cp -r build_venv/lib/python3.*/site-packages/* AppDir/usr/lib/ 2>/dev/null || true

# Copy application files from src/
cp $SRC_DIR/app.py $SRC_DIR/display.py $SRC_DIR/mdns.py AppDir/usr/share/lobby-display/
cp -r $SRC_DIR/templates/* AppDir/usr/share/lobby-display/templates/
cp -r $SRC_DIR/static/* AppDir/usr/share/lobby-display/static/ 2>/dev/null || true

# Copy AppRun and desktop file from src/
cp $SRC_DIR/AppRun AppDir/
chmod +x AppDir/AppRun
cp $SRC_DIR/lobby-display.desktop AppDir/

# Copy icon file from src/ if it exists, otherwise use a default icon
cp $SRC_DIR/lobby-display.png AppDir/ 2>/dev/null || echo "Warning: No icon found, using default"

# Download appimagetool if not present
if [ ! -f appimagetool-aarch64.AppImage ]; then
    wget "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-aarch64.AppImage"
    chmod +x appimagetool-aarch64.AppImage
fi

# Build AppImage
./appimagetool-aarch64.AppImage AppDir "${APP_NAME}-${VERSION}-${ARCH}.AppImage"

echo ""
echo "Build complete: ${APP_NAME}-${VERSION}-${ARCH}.AppImage"
echo ""
echo "To install on target system:"
echo "  chmod +x ${APP_NAME}-${VERSION}-${ARCH}.AppImage"
echo "  ./${APP_NAME}-${VERSION}-${ARCH}.AppImage --install"