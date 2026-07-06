# Troubleshooting Guide

Common issues and their solutions.

## Installation Issues

### "chown: invalid user: 'pi:pi'"

**Cause**: Hardcoded username doesn't exist on your system.

**Solution**: The AppRun now uses `$(whoami)` to detect the current user automatically. If you're using an older AppImage, update to the latest version or manually edit the service files to use your username.

### AppImage won't run (permission denied)

**Cause**: File not marked as executable.

**Solution**:

```bash
chmod +x lobby-display-*.AppImage
```

### "No such file or directory" when running AppImage

**Cause**: 32-bit/64-bit mismatch or corrupted download.

**Solution**:

1. Verify architecture: uname -m (should be aarch64 for 64-bit)
2. Re-download the correct AppImage
3. Check file integrity: ls -lh (should be >10MB)

## Service Issues

### Services fail to start (status=1/FAILURE)

**Check logs**:

```bash
sudo journalctl -u lobby-web -n 50
sudo journalctl -u lobby-display -n 50
```

### "ModuleNotFoundError: No module named 'flask'"

**Cause**: Python packages not found in AppImage.

**Solutions**:

1. Verify Python version detection in AppRun:

    ```bash
    python3 --version  # Should output 3.x.x
    ```

    The AppRun should auto-detect this. If not, hardcode it:

    ```bash
    PYTHON_VERSION="3.13"  # Replace with your version
    ```

2. Check package location:

    ```bash
    ./lobby-display-*.AppImage --appimage-extract
    ls squashfs-root/usr/lib/ | grep -i flask
    ```

    If empty, the build failed to include packages. Rebuild.

3. Add direct lib path to AppRun:

    ```bash
    export PYTHONPATH="$APP_DIR/usr/lib:$PYTHONPATH"
    ```

### Web service starts but display fails

**Symptoms**: Can access web UI, but HDMI screen is black.

**Check**:

```bash
sudo journalctl -u lobby-display -n 20
```

**Common causes**:

1. No X11 display:
    - Display service requires X11 or framebuffer
    - If running headless, you need a virtual framebuffer:

      ```bash
      sudo apt install xvfb
      # Modify service to use: ExecStartPre=/usr/bin/Xvfb :0 -screen 0 1920x1080x24
      ```

2. Wrong DISPLAY variable:
    - Check: `echo $DISPLAY` (should be `:0`)
    - Update service file if needed
3. Images not found:
    - Check `/opt/lobby-display/uploads/` exists and has files
    - Verify permissions: 

      ```bash
      ls -la /opt/lobby-display/
      ```

### "Address already in use" (Port 5000)

**Cause**: Another service using port 5000.

**Solution**:

```bash
# Find what's using port 5000
sudo lsof -i :5000

# Kill it or change Lobby Display port in app.py:
# app.run(host='0.0.0.0', port=5001)  # Change to 5001
```

## Web Interface Issues

### Cannot access web interface

**Test connectivity**:

```bash
# From the Pi
curl http://localhost:5000

# From another computer
ping [pi-ip-address]
```

**Check firewall**:

```bash
sudo ufw status
# If active, allow port 5000:
sudo ufw allow 5000/tcp
```

**Verify service is listening**:

```bash
sudo ss -tlnp | grep 5000
```

### mDNS not working (.local address unavailable)

**Test mDNS**:

```bash
# From another computer on same network
ping lobby-display.local
```

## Platform-specific fixes:

**Linux**: Install avahi

```bash
sudo apt install avahi-daemon
```

**Windows**: Install Bonjour Print Services from Apple, or use IP address

**macOS/iOS**: Should work natively

**Alternative**: Use IP address instead of .local

### Images upload but don't display

**Check**:

1. Image in uploads folder:

    ```bash
    ls -la /opt/lobby-display/uploads/
    ```

2. Database entry:

    ```bash
    sqlite3 /opt/lobby-display/database.db "SELECT * FROM images;"
    ```

3. Playlist assignment:
    - Go to Playlists → Edit → verify images are listed
4. Active playlist:
    - Check that correct playlist is set as active

### Display Issues

#### Images appear rotated incorrectly

**Software rotation (immediate)**:

- Settings → Rotation → Save

**Hardware rotation (requires reboot, better performance)**:

```bash
sudo nano /boot/config.txt
# Add: display_rotate=1  (for 90 degrees)
sudo reboot
```

#### Poor image quality or performance

**For Pi 3**:

- Use 720p resolution instead of 1080p
- Reduce fade transitions (Settings)
- Optimize images before upload (compress JPGs)

**For Pi 4/5**:

- Should handle 1080p fine
- Enable hardware rotation for better performance

#### Black screen with "No Images" text

**Cause**: Active playlist is empty or no playlist selected.

**Solution**:

1. Upload images
2. Create playlist and add images
3. Set playlist as active
4. Or check that default playlist has images

### Build Issues

#### "ModuleNotFoundError" during build

**Cause**: Missing system dependencies.

**Solution**:

```bash
sudo apt install -y python3-dev python3-venv libsdl2-dev
```

#### AppImage not created

**Check**:

```bash
# Run build with full output
./build.sh 2>&1 | tee build.log

# Check for errors
tail -50 build.log
```

#### Large AppImage size

**Reduce size by adding to build.sh before appimagetool**:

```bash
# Remove unnecessary files
find AppDir -name "*.pyc" -delete
find AppDir -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
rm -rf AppDir/usr/lib/python*/site-packages/pip*
rm -rf AppDir/usr/lib/python*/site-packages/setuptools*
```

### Data Recovery

#### Accidentally deleted images

**Check if in playlist**:

Images in playlists reference database entries. If database entry exists but file missing, re-upload with same filename.

#### Corrupted database

**Backup first**:

```bash
sudo cp /opt/lobby-display/database.db ~/database-backup.db
```

**Reset database** (WARNING: loses playlists):

```bash
sudo systemctl stop lobby-web
sudo rm /opt/lobby-display/database.db
sudo systemctl start lobby-web
# Default playlist will be recreated
```

#### Full reset

**Remove all data**:

```bash
sudo systemctl stop lobby-web lobby-display
sudo rm -rf /opt/lobby-display/*
sudo systemctl start lobby-web lobby-display
```

### Getting More Help

#### Enable Debug Mode

Temporarily run services in foreground with debug output:

```bash
# Stop services
sudo systemctl stop lobby-web lobby-display

# Run web server with debug
cd /opt/lobby-display
sudo python3 app.py

# In another terminal, run display
sudo python3 display.py
```

#### Collect System Information

When reporting issues, include:

```bash
# System info
uname -a
python3 --version

# Service status
sudo systemctl status lobby-web
sudo systemctl status lobby-display

# Recent logs
sudo journalctl -u lobby-web --since "1 hour ago"
sudo journalctl -u lobby-display --since "1 hour ago"

# Disk space
df -h

# Memory
free -h
```

### Still Stuck?

1. Check GitHub Issues
2. Open a new issue with:
    - Description of problem
    - Steps to reproduce
    - Error messages/logs
    - System information (Pi model, OS version)

### Quick Fixes Reference

| Problem | Quick Fix |
| - | - |
| Can't access web UI | Use IP: `http://[pi-ip]:5000` |
| Black screen | Check active playlist has images |
| Services won't start | Check logs: `journalctl -u lobby-web` |
| Wrong rotation | Edit `/boot/config.txt`, reboot |
| Forgot password | No password needed, it's local |
