#!/usr/bin/python
import re
from os import setsid
from subprocess import call, check_output, Popen, PIPE
from PySide2.QtCore import QThread
from PySide2.QtWidgets import QSystemTrayIcon, QApplication
from PySide2.QtGui import QIcon
from pyudev import MonitorObserver, Context, Monitor
import sys

#
# Config
#

# Name of the touchpad device
touchscreen_name = 'FTSC1000:00 2808:1015'
touchpad_name = 'HTX USB HID Device HTX HID Device Touchpad'

# Touchpad config

# NOTE: Tapping automatically disables itself after screen rotation
enable_tapping = True

#
# Constants
#

# Mappings from `monitor-sensor` orientations
ORIENTATIONS = {
    'normal': 'normal',
    'bottom-up': 'inverted',
    'right-up': 'right',
    'left-up': 'left',
}

# Touch matrices
MATRICES = {
    'normal': [1, 0, 0, 0, 1, 0, 0, 0, 1],
    'inverted': [-1, 0, 1, 0, -1, 1, 0, 0, 1],
    'left': [0, -1, 1, 1, 0, 0, 0, 0, 1],
    'right': [0, 1, 0, -1, 0, 1, 0, 0, 1],
}

MODE_KEYBOARD = 0
MODE_TABLET = 1

#
#  Global flags
#

locked = False
mode = MODE_TABLET

#
# Global variables
#

context = Context()
monitor = Monitor.from_netlink(context)

#
# Global functions
#

def mode_tablet():
    global mode
    mode = MODE_TABLET

    print('Mode: tablet')

def mode_keyboard():
    global mode, locked
    mode = MODE_KEYBOARD
    locked = False

    print('Mode: keyboard')
    print('forcing orientation: right')

    rotate('right')

    if enable_tapping:
        call('xinput set-prop ' + touchpad_id + ' \'libinput Tapping Enabled\' 1', shell=True)

def rotate(orientation):
    print('orientation: ' + orientation)

    matrix = str.join(' ', [str(i) for i in MATRICES[orientation]])
    call('xrandr --output ' + monitor_name + ' --rotate ' + orientation, shell=True)
    call('xinput set-prop ' + touchscreen_id + ' "Coordinate Transformation Matrix" ' + matrix, shell=True)

def get_device_id(device_name):
    devices = check_output('xinput list', shell=True).decode('unicode_escape')
    pattern = re.compile(device_name + ' *\tid=(\d+)')
    return re.findall(pattern, devices)[0]

#
# QT Widgets
#

class TrayIcon:
    def __init__(self):
        self.icons = {
            True: QIcon('icons/rotate_disabled.png'),
            False: QIcon('icons/rotate_enabled.png'),
        }

        self.tray = QSystemTrayIcon()
        self.tray.activated.connect(self.action)
        self.tray.setIcon(self.icons[locked])
        self.tray.show()

    def action(self, signal):
        global locked
        locked = not locked

        # Change icon accordingly
        self.tray.setIcon(locked)

#
# Workers
#

class RotationWorker(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.pattern = re.compile('orientation(?: changed)?: ([^)\n]+)')

    def run(self):
        global locked, mode

        with Popen('monitor-sensor', stdout=PIPE, bufsize=1, universal_newlines=True, preexec_fn=setsid) as p:
            for line in p.stdout:
                matches = re.findall(self.pattern, line)

                if not locked and mode == MODE_TABLET:
                    if len(matches) > 0 and matches[0] is not 'undefined':
                        if matches[0] in ORIENTATIONS:
                            orientation = ORIENTATIONS[matches[0]]
                            rotate(orientation)


class UdevWorker(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.daemon = True

    def udev_action(self, action, device):
        if 'DEVNAME' in device:
            if device.get('DEVNAME') == touchpad_devname:
                if action == 'add':
                    mode_keyboard()

                if action == 'remove':
                    mode_tablet()

    def run(self):
        observer = MonitorObserver(monitor, self.udev_action)
        observer.daemon = True
        observer.start()


#
# Main
#

# Get device ids and names
touchscreen_id = get_device_id(touchscreen_name)
touchpad_id = get_device_id(touchpad_name)
touchpad_devname = '/dev/input/event' + touchpad_id

print('touchscreen: ', touchscreen_id)
print('touchpad: ', touchpad_id)

# Get connected monitor name
# TODO: Use xrandr to auto-detect
monitor_name = 'DSI1'

# Run the app
if __name__ == "__main__":
    app = QApplication(sys.argv)

    tray = TrayIcon()

    udev = UdevWorker()
    udev.start()

    rotator = RotationWorker()
    rotator.start()

    sys.exit(app.exec_())
