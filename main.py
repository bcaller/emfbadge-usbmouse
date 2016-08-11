### Author: Ben Caller
### Description: Your badge is now a USB mouse. Tilt to move. A & B to click. Joystick scrolls.
### Category: Other
### License: GPLv3
### Appname: USB Mouse

import pyb
import buttons
import ugfx
from os import sep, remove
from imu import IMU


START = '# Mouse mode <'
INSERT_AFTER = 'm = "apps/home/main.py"'
BOOT_FILE = 'boot.py'
APP_DIR = 'apps/bcaller~usbmouse'
TILT_SENSITIVITY = 25
INSERT = '''

        import buttons
        buttons.init(['BTN_B'])
        if buttons.is_pressed('BTN_B'):
            pyb.usb_mode('VCP+HID')
            m = "%s/main.py"
# > Mouse mode
''' % APP_DIR


def is_installed():
    with open(BOOT_FILE) as f:
        for line in f.readlines():
            if START in line:
                return True
    return False


def install():
    tmp_file = BOOT_FILE + '.tmp'
    with open(BOOT_FILE) as original:
        with open(tmp_file, 'w') as tempfile:
            # Make modified boot.py
            for line in original.readlines():
                tempfile.write(line)
                if INSERT_AFTER in line:
                    tempfile.write(START)
                    tempfile.write(INSERT)                    
    # Overwrite old boot.py
    # This is necessary as pyb.usb_mode must be called inside boot.py
    # The usb_mode cannot be changed after pyb.main
    with open(tmp_file) as tempfile:
        with open(BOOT_FILE, 'w') as bootfile:
            for line in tempfile.readlines():
                bootfile.write(line)
    remove(tmp_file)


def click():
    # Button data is a bitmask
    return buttons.is_pressed('BTN_A') + 2 * buttons.is_pressed('BTN_B') + 4 * buttons.is_pressed('JOY_CENTER')


def joystick_scroll(factor=1):
    if buttons.is_pressed('JOY_UP'):
        return factor
    elif buttons.is_pressed('JOY_DOWN'):
        return -factor
    return 0


ugfx.init()
buttons.init()
if 'HID' in pyb.usb_mode():
    # HID mode rather than mass storage
    ugfx.area(0, 0, ugfx.width(), ugfx.height(), ugfx.BLACK)
    ugfx.text(30, 30, "USB Mouse mode by bcaller", ugfx.html_color(0xFF7C11))
    accelerometer = IMU()
    hid = pyb.USB_HID()
    transform = lambda a: int(a * TILT_SENSITIVITY)
    
    def mouse_update():
        accel = accelerometer.get_acceleration()
        # Buttons, x, y, scroll
        hid.send((click(), transform(accel['x']), transform(accel['y']), joystick_scroll()))
    
    while True:
        mouse_update()
        pyb.delay(20)
else:
    # Not a HID, press B and reset
    ugfx.area(0, 0, ugfx.width(), ugfx.height(), ugfx.BLACK)
    if not is_installed():
        install()
    ugfx.text(30, 30, "Hold B to restart in mouse mode", ugfx.html_color(0xFF7C11))
    while True:
        if buttons.is_pressed('BTN_B'):
            pyb.hard_reset()
        pyb.delay(10)
