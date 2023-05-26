![moslime](moslime_logo.png)
Bring your Mocopi™ trackers into SteamVR™!

Built on the battle-tested algorithms and runtime of SlimeVR™, this project aims to improve and extend the Mocopi™ on PC experience. No first-party app required.

## Disclaimers
This third-party software is deemed alpha quality, provided as is, and without warranty.
Mocopi™ is a trademark owned by the Sony Corporation®. MoSlime is not endorsed by the Sony Corporation nor SlimeVR™, nor are they affiliated with the MoSlime developers.
This software does not modify the firmware of your Mocopi™ trackers and should not break them. However, only use this software if you agree to assume the risks therein.

## Requirements
 - Any VM or bare-metal Linux system with Bluetooth® and BlueZ as the Bluetooth® stack. This system can be seperate from the system that is running SlimeVR™.
 - Python 3 with bluepy and scipy installed `pip3 install bluepy scipy`

## Usage - Please read the steps in their entirety as the process is currently time sensitive!
1. Turn on all of the trackers and pair them to your computer. You can either do this by using your distros Bluetooth® manager or via `bluetoothctl`.
2. Take note of the MAC addresses for all of your trackers. They should start with `3C:38:F4`. If you have a tracker that starts with something different, please let us know!
3. Turn off all of the trackers, then disable and re-enable Bluetooth®.
4. Download moslime.py and open it in your favorite text editor. At the top, put the MAC addresses of your trackers in `tracker_addrs` and change `UDP_IP` to the IP address of the computer running SlimeVR™. You can put as few or as many trackers as you like. However, performance might degrade after 6 trackers.
5. Start the SlimeVR™ server and wait a few seconds for it to fully loaded. If you want to use other trackers with SlimeVR™, don't turn them on until after you have MoSlime set up. Note: Any Mocopi™ tracker can be used on any body part. The plastic cover is purely cosmetic!
6. Run `python3 moslime.py`, then immediately turn all the trackers back on. You can either do this manually or by plugging in the case, waiting for the trackers to light up then quickly unplugging it.
7. You should see the lights on the trackers illuminate green one by one as they connect in the terminal. While they are connecting, leave the trackers in the case on a flat and stable surface. DO NOT touch them!
8. Once you see `Safe to start tracking` in the terminal, make sure all trackers appear in SlimeVR™. They should show up as IMU Tracker 1, IMU Tracker 2, etc.
9. Shake each Mocopi™ individually and note which IMU Tracker slot glows in SlimeVR™. This is your tracker designation until you assign it a body part and/or different name.
10. [Optional]: At this point you can also turn on any additional SlimeVR™ trackers and use them alongside the Mocopi™s. Make sure you always start MoSlime first. This will be an issue fixed in the future.

## Note
If you somehow accidentally close SlimeVR™, you'll need to do steps 6-8 again (make sure you turn the trackers off and restart bluetooth)

## Troubleshooting
 - If trackers are refusing to connect, try stopping the script (mash Ctrl+C till it stops), turn off all the trackers, restart Bluetooth® and do steps 6-8 again.
 - If you see `Safe to start tracking` but no trackers in SlimeVR™, make sure you have the correct IP address and that both computers are on the same network.
 - If your Linux PC is a desktop and range/performance seems really bad, make sure you have your WiFi/BT antenna connected. Alternatively, you can also use an external Bluetooth® dongle but your mileage may vary. 

## Tested Bluetooth® adapters
 - [SENA UD100](http://www.senanetworks.com/ud100-g03.html)
 - [Intel® 8265NGW - Combo WiFi/BT card](https://www.intel.com/content/www/us/en/products/sku/94150/intel-dual-band-wirelessac-8265/specifications.html)
 - Raspberry Pi 3B/3B+/4B (3B and 3B+ struggle a bit, it may be a good idea to lower the TPS in moslime.py)

## Contributors
 - [@lmore377](https://github.com/lmore377) - Original Bluetooth® reverse-engineering work, Python code, quaternion correction math
 - [@PlatinumVsReality](https://github.com/PlatinumVsReality) - Python Slime packet 17 code, Rust code, web interface, graphics, moral support
 - [@itstait](https://github.com/itstait) - Helped optimize multithreading (trust me it used to be much worse)

## Resources
 - https://github.com/lmore377/mocopi-reverse-engineering - Initial reverse engineering work
 - https://github.com/SlimeVR/SlimeVR-Tracker-ESP - Used to figure out networking / packet structure
 - https://github.com/carl-anders/slimevr-wrangler - Used to figure out networking / packet structure
 - https://www.creativefabrica.com/product/coffeecake/ - Font used for the logo. Special thanks to Khurasan!
 - https://www.dafont.com/dripping.font - Additional font used, Dripping by Woodcutter
