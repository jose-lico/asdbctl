#!/bin/bash
#
# Installation script for Apple Studio Display Brightness Applet
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing Apple Studio Display Brightness Applet..."
echo

# Check for required dependencies
echo "Checking dependencies..."
DEPS_TO_INSTALL=""
for pkg in python3-gi gir1.2-appindicator3-0.1; do
    if ! dpkg -s "$pkg" >/dev/null 2>&1; then
        DEPS_TO_INSTALL="$DEPS_TO_INSTALL $pkg"
    else
        echo "  $pkg is already installed"
    fi
done

if [ -n "$DEPS_TO_INSTALL" ]; then
    echo "Installing:$DEPS_TO_INSTALL"
    sudo apt-get install -y $DEPS_TO_INSTALL
fi

# Install udev rule for non-root access
echo
echo "Installing udev rule for non-root access..."
if [ -f "/etc/udev/rules.d/20-asd-backlight.rules" ]; then
    echo "  udev rule already exists, updating..."
fi
sudo cp "$SCRIPT_DIR/rules.d/20-asd-backlight.rules" /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
echo "  udev rule installed"

# Install the applet script
echo
echo "Installing applet script..."
sudo install -m 755 "$SCRIPT_DIR/asdbctl-applet.py" /usr/local/bin/asdbctl-applet
echo "  Installed to /usr/local/bin/asdbctl-applet"

# Install autostart entry
echo
echo "Installing autostart entry..."
mkdir -p ~/.config/autostart
cp "$SCRIPT_DIR/asdbctl-applet.desktop" ~/.config/autostart/
echo "  Installed to ~/.config/autostart/"

echo
echo "============================================"
echo "Installation complete!"
echo "============================================"
echo
echo "IMPORTANT: For the udev rule to take effect, you need to either:"
echo "  1. Unplug and replug the Apple Studio Display USB cable, OR"
echo "  2. Reboot your system"
echo
echo "To start the applet now (for testing):"
echo "  /usr/local/bin/asdbctl-applet &"
echo
echo "The applet will automatically start on next login."
echo "It will only appear in your topbar when an Apple Studio Display is connected."
