#!/usr/bin/env bash
# Script to set up Pi Web Switcher on a fresh Pi 5 installation

echo "Setting up Pi Web Switcher on Raspberry Pi 5..."

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Pi 5 compatible packages
echo "Installing Pi 5 compatible packages..."
sudo apt install -y \
    python3-pyqt5 \
    python3-pyqt5.qtwebengine \
    python3-pip \
    python3-venv \
    python3-yaml \
    xserver-xorg-video-fbdev \
    xserver-xorg-video-fbturbo

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements-pi.txt

# Set up environment variables for Pi 5
echo "Setting up Pi 5 environment variables..."
cat >> ~/.bashrc << 'EOF'

# Pi 5 compatibility settings
export QT_QPA_PLATFORM=xcb
export QT_X11_NO_MITSHM=1
export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu-sandbox"
EOF

# Make scripts executable
chmod +x scripts/*.sh

echo "Setup complete!"
echo "To run the application: ./scripts/run_pi5.sh"
echo "Or for development: ./scripts/run_dev_pi.sh"
