#!/usr/bin/env bash
# Script to configure Pi 5 for X11 compatibility with PyQt5 applications

echo "Configuring Pi 5 for X11 compatibility..."

# Check if running on Pi 5
if ! grep -q "Raspberry Pi 5" /proc/cpuinfo 2>/dev/null; then
    echo "Warning: This script is designed for Raspberry Pi 5"
fi

# Install X11 session if not present
echo "Installing X11 session components..."
sudo apt update
sudo apt install -y xserver-xorg-video-fbdev xserver-xorg-video-fbturbo

# Create X11 session configuration
echo "Creating X11 session configuration..."
sudo tee /etc/X11/xorg.conf.d/99-pi5-compatibility.conf > /dev/null <<EOF
Section "Device"
    Identifier "VideoCard0"
    Driver "fbdev"
    Option "fbdev" "/dev/fb0"
EndSection

Section "Screen"
    Identifier "Screen0"
    Device "VideoCard0"
    Monitor "Monitor0"
    DefaultDepth 24
    SubSection "Display"
        Depth 24
        Modes "1920x1080"
    EndSubSection
EndSection
EOF

# Set environment variables for all users
echo "Setting up environment variables..."
sudo tee /etc/environment > /dev/null <<EOF
QT_QPA_PLATFORM=xcb
QT_X11_NO_MITSHM=1
QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu-sandbox"
EOF

# Create a desktop file to force X11 session
echo "Creating desktop session file..."
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/pi-webswitcher-x11.desktop <<EOF
[Desktop Entry]
Type=Application
Name=Pi Web Switcher (X11)
Comment=Force X11 session for Pi Web Switcher
Exec=export QT_QPA_PLATFORM=xcb && export QT_X11_NO_MITSHM=1
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

echo "Configuration complete!"
echo "Please reboot your Pi 5 for changes to take effect."
echo "After reboot, try running: ./scripts/run_pi5.sh"
