# moslime
Make your questionable investment worth it by using Mocopi trackers with SlimeVR

This project aims to improve upon the Mocopi trackers by getting rid of the dependence on the mobile app and making them function as SlimeVR trackers. As an added bonus, you can assign the trackers to any body part (ex: using the head tracker as a chest tracker and the wrist trackers as knee trackers)\
The code is still in "pre-alpha how is this even working" stage so expect things to break. Everything is in python right now but there's plans to port over to rust once everything is stable.

## Requirements
 - Any linux system with bluetooth and BlueZ as the bluetooth stack (this system can be seperate from the system running SlimeVR, you might even be able to use a VM)
 - Python 3 with bluepy and scipy `pip3 install bluepy scipy`

## Usage - Read through the whole thing before following along
1. Turn on all the trackers and pair them to your computer. You can either do this using your distros bluetooth manager or `bluetoothctl` in a terminal
2. Get the MAC addresses for all of your trackers. They should start with `3C:38:F4` (if you have a tracker that starts with something different let us know)
3. Turn off all the trackers then disable and reenable bluetooth
4. Download moslime.py and open it up in your favorite text editor. At the top, put the MAC addresses of your trackers in `tracker_addrs` and change `UDP_IP` to the IP address of the computer running SlimeVR. You can put as few or as many trackers as you like (performance might degrade after 6 trackers)
5. Start the SlimeVR server and give it a few seconds to get fully loaded. If you want to use other trackers with slime, don't turn them on until after you have the mocopis connected.
6. Run `python3 moslime.py` then immediately turn all the trackers back on. You can either do this manually or by plugging in the case, waiting for the trackers to light up then quickly unplugging it.
7. You should see the trackers connecting in the terminal and they should go green. While this is happening, leave the trackers in the case on a table and don't touch them.
8. Once you see `Safe to start tracking` in the terminal, make sure all trackers appear in SlimeVR. If they do and they react to movement, you can now put them on and use the setup wizard built into SlimeVR to assign and calibrate them. At this point you can also turn on any additional SlimeVR trackers and use them alongside the mocopis.

## Notes
 - If you somehow accidentally close SlimeVR, you'll need to do steps 6-8 again (make sure you turn the trackers off and restart bluetooth)

## Troubleshooting
 - If trackers are refusing to connect, try stopping the script (mash Ctrl+C till it stops), turn off all the trackers, restart bluetooth and do steps 6-8 again.
 - If you see `Safe to start tracking` but no trackers in SlimeVR, make sure you have the correct IP address and that both computers are on the same network.
 - If your linux PC is a desktop and range/performance seems really bad, make sure you have your WiFi/BT antenna connected. Alternatively, you can also use an external bluetooth dongle but your mileage may vary. 

## Tested Bluetooth adapters
 - [SENA UD100](http://www.senanetworks.com/ud100-g03.html)
 - [Intel 8265NGW - Combo WiFi/BT card](https://www.intel.com/content/www/us/en/products/sku/94150/intel-dual-band-wirelessac-8265/specifications.html)
 - Raspberry Pi 3B onboard BT (The bluetooth chip can handle the connections but the pi itself struggles a bit)

## Resources
 - https://github.com/lmore377/mocopi-reverse-engineering - Initial reverse engineering work
