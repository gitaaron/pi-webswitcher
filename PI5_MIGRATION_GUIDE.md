# Pi 5 Migration Guide

## Problem
Your SD card was configured for Raspberry Pi 4 and is not compatible with Pi 5 hardware due to:
- Different OS requirements (Pi 5 needs Bookworm minimum)
- Different kernel and firmware
- Hardware-specific compiled libraries

## Solutions

### Option 1: Fresh Pi 5 Setup (RECOMMENDED)

1. **Get a new SD card** (8GB+ recommended)
2. **Download Raspberry Pi OS Bookworm** from [raspberrypi.org](https://www.raspberrypi.org/downloads/)
3. **Flash the new OS** using Raspberry Pi Imager
4. **Boot Pi 5** with the new SD card
5. **Copy your project** to the Pi 5:
   ```bash
   # On your development machine, create a backup
   tar -czf pi-webswitcher-backup.tar.gz /path/to/pi-webswitcher
   
   # Transfer to Pi 5 (via SCP, USB, etc.)
   scp pi-webswitcher-backup.tar.gz pi@your-pi5-ip:~/
   
   # On Pi 5, extract and setup
   tar -xzf pi-webswitcher-backup.tar.gz
   cd pi-webswitcher
   ./scripts/setup_pi5_fresh.sh
   ```

### Option 2: Try Upgrading Existing SD Card (RISKY)

**WARNING**: This may not work and could break your system.

1. **Backup your data first**
2. **Run the upgrade script**:
   ```bash
   ./scripts/upgrade_pi4_to_pi5.sh
   ```
3. **Reboot and test**

### Option 3: Manual Migration Steps

If you prefer to do it manually:

1. **Update OS to Bookworm**:
   ```bash
   sudo apt update
   sudo apt full-upgrade -y
   ```

2. **Install Pi 5 packages**:
   ```bash
   sudo apt install -y python3-pyqt5 python3-pyqt5.qtwebengine
   ```

3. **Set environment variables**:
   ```bash
   echo 'export QT_QPA_PLATFORM=xcb' >> ~/.bashrc
   echo 'export QT_X11_NO_MITSHM=1' >> ~/.bashrc
   echo 'export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu-sandbox"' >> ~/.bashrc
   ```

4. **Reboot and test**:
   ```bash
   ./scripts/run_pi5.sh
   ```

## Why This Happens

- **Pi 4**: Uses older OS versions (Bullseye, Buster)
- **Pi 5**: Requires Bookworm minimum due to new hardware
- **Libraries**: PyQt5/QtWebEngine compiled for specific ARM architecture
- **Kernel**: Different hardware requires different drivers

## Testing Your Setup

After migration, test with:
```bash
# Check OS version
cat /etc/os-release

# Check if PyQt5 works
python3 -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"

# Run your app
./scripts/run_pi5.sh
```

## Troubleshooting

If you still get errors:
1. Check OS version is Bookworm or newer
2. Verify PyQt5 packages are installed: `apt list --installed | grep pyqt5`
3. Try the compatibility flags in `run_pi5.sh`
4. Check system logs: `journalctl -f` while running the app
