#!/usr/bin/env bash
# ATTEMPT to upgrade Pi 4 SD card for Pi 5 compatibility
# WARNING: This may not work and could break the system

echo "WARNING: This script attempts to upgrade a Pi 4 SD card for Pi 5."
echo "This may not work and could break your system."
echo "Recommended: Use a fresh Pi 5 OS installation instead."
echo ""
read -p "Do you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo "Attempting to upgrade system for Pi 5 compatibility..."

# Update package lists
echo "Updating package lists..."
sudo apt update

# Try to upgrade to Bookworm (may fail)
echo "Attempting to upgrade to Bookworm..."
sudo apt full-upgrade -y

# Install Pi 5 specific packages
echo "Installing Pi 5 specific packages..."
sudo apt install -y \
    raspberrypi-kernel \
    raspberrypi-bootloader \
    raspberrypi-firmware \
    xserver-xorg-video-fbdev

# Update firmware
echo "Updating firmware..."
sudo rpi-update

# Set Pi 5 compatibility flags
echo "Setting Pi 5 compatibility environment variables..."
sudo tee -a /etc/environment << 'EOF'
QT_QPA_PLATFORM=xcb
QT_X11_NO_MITSHM=1
QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu-sandbox"
EOF

echo "Upgrade attempt complete."
echo "REBOOT REQUIRED. After reboot, test with: ./scripts/run_pi5.sh"
echo "If it still doesn't work, you'll need a fresh Pi 5 OS installation."
