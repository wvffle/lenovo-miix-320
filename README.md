# Installing linux on Miix 320<sub><sup>-10ICR</sup></sub>
## Installing Ubuntu
Well, it is easy as it sounds. Just boot from USB and install it :)
Most of the things should work fine.

## Installing ArchLinux
It was a bit tough task as systemd-boot was a bit broken back then when I was installing it. Basically all the screen has been visited by alien artifacts.

After installing ArchLinux, on every boot I had to close the lid, wait couple of seconds and open it again to get to TTY or display manager. Fortunately after (a long time) some kernel updates, the bug is kind of fixed. I no longer have to perform the boot-up ritual anymore. The torn tty artifacts are still there but not for long. They just get fixed in a second so it doesn't bother me any more. 

What I did to install ArchLinux:
1. Install Ubuntu
2. Transform Ubuntu into ArchLinux with some scripts downloaded online
3. Fix grub
4. Fix package errors
5. Cleanup the system

I believe that archiso should work now but I have to test it.

# Auto screen rotation in Xorg KDE
My current DE is KDE and as far as I know there is no working auto-rotator for this device. So I decided to write my own.

It's available in `auto_rotate.py` and uses `xinput`, `xrandr` and `monitor-sensor` commands to detect and rotate screen + touchpad

## Configuration
### Device names
You can get device names with `xinput list`
- `touchscreen_name` - Device to rotate the touch matrix
- `touchpad_name` - Device to detect keyboard connection and fix tapping after screen rotation
```py
# Name of the touchpad device
touchscreen_name = 'FTSC1000:00 2808:1015'
touchpad_name = 'HTX USB HID Device HTX HID Device Touchpad'
```
### Touchpad config
- `enable_tapping` - Auto enable tapping after screen rotation
```py
# Touchpad config
enable_tapping = True
```
### `monitor-sensor` to `xinput` mappings
`monitor-sensor` and `xinput` have different orientation names. I'm unsure if iio names can differ between devices 
```py
# Mappings from `monitor-sensor` orientations
ORIENTATIONS = {
    'normal': 'normal',
    'bottom-up': 'inverted',
    'right-up': 'right',
    'left-up': 'left',
}
```
