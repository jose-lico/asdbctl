#!/usr/bin/python3
"""
Apple Studio Display Brightness Applet
System tray applet for controlling Apple Studio Display brightness via asdbctl.
"""

import subprocess
import signal
import sys

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GLib


ASDBCTL_PATH = '/usr/bin/asdbctl'
POLL_INTERVAL_MS = 5000
APPINDICATOR_ID = 'asdbctl-brightness'


class BrightnessApplet:
    def __init__(self):
        self.current_brightness = 0
        self.display_connected = False

        self.indicator = AppIndicator3.Indicator.new(
            APPINDICATOR_ID,
            'display-brightness-symbolic',
            AppIndicator3.IndicatorCategory.HARDWARE
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)

        self.build_menu()

        self.check_display()
        GLib.timeout_add(POLL_INTERVAL_MS, self.check_display)

    def build_menu(self):
        self.menu = Gtk.Menu()

        # Brightness label
        self.brightness_label = Gtk.MenuItem(label="Brightness: --%")
        self.brightness_label.set_sensitive(False)
        self.menu.append(self.brightness_label)

        self.menu.append(Gtk.SeparatorMenuItem())

        # Increment/Decrement buttons
        inc_item = Gtk.MenuItem(label="+5%")
        inc_item.connect('activate', self.on_increment)
        self.menu.append(inc_item)

        dec_item = Gtk.MenuItem(label="-5%")
        dec_item.connect('activate', self.on_decrement)
        self.menu.append(dec_item)

        self.menu.append(Gtk.SeparatorMenuItem())

        # Preset buttons
        for preset in [25, 50, 75, 100]:
            item = Gtk.MenuItem(label=f"{preset}%")
            item.connect('activate', self.on_preset_clicked, preset)
            self.menu.append(item)

        self.menu.append(Gtk.SeparatorMenuItem())

        # Quit
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect('activate', self.on_quit)
        self.menu.append(quit_item)

        self.menu.show_all()
        self.indicator.set_menu(self.menu)

    def run_asdbctl(self, *args):
        try:
            result = subprocess.run(
                [ASDBCTL_PATH] + list(args),
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0, result.stdout.strip()
        except subprocess.TimeoutExpired:
            return False, ""
        except Exception as e:
            print(f"Error running asdbctl: {e}", file=sys.stderr)
            return False, ""

    def get_brightness(self):
        success, output = self.run_asdbctl('get')
        if success and output:
            try:
                parts = output.split()
                if len(parts) >= 2:
                    return int(parts[1])
            except (ValueError, IndexError):
                pass
        return None

    def set_brightness(self, value):
        value = max(0, min(100, int(value)))
        success, _ = self.run_asdbctl('set', str(value))
        if success:
            self.current_brightness = value
            self.update_ui()
        return success

    def check_display(self):
        brightness = self.get_brightness()
        was_connected = self.display_connected
        self.display_connected = brightness is not None

        if self.display_connected:
            self.current_brightness = brightness
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            self.update_ui()
        else:
            self.indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)

        if was_connected != self.display_connected:
            status = "connected" if self.display_connected else "disconnected"
            print(f"Apple Studio Display {status}", file=sys.stderr)

        return True

    def update_ui(self):
        self.brightness_label.set_label(f"Brightness: {self.current_brightness}%")

    def on_increment(self, item):
        new_value = min(100, self.current_brightness + 5)
        self.set_brightness(new_value)

    def on_decrement(self, item):
        new_value = max(0, self.current_brightness - 5)
        self.set_brightness(new_value)

    def on_preset_clicked(self, item, value):
        self.set_brightness(value)

    def on_quit(self, item):
        Gtk.main_quit()

    def run(self):
        Gtk.main()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    applet = BrightnessApplet()
    applet.run()


if __name__ == '__main__':
    main()
