## First Time Setup
1. Turn on all of the trackers and pair them to your computer. You can either do this by using your distros Bluetooth manager or via `bluetoothctl`.\
   1a. There is an experimental autopair script in the scripts/ folder. If you're on a system with systemd (ubuntu, debian, steamdeck os, etc.), you can try that to pair your trackers by running `sudo python3 autopair.py` in the scripts folder. It will also generate a moslime.json with the MAC addresses prefilled. 
3. Take note of the MAC addresses for all of your trackers. They should start with `3C:38:F4`. If you have a tracker that starts with something different, please let us know!
4. Turn off all of the trackers, then disable and re-enable Bluetooth.
5. Download `moslime.py` and `moslime.json` then open `moslime.json` in your favorite text editor. In this file, put the MAC addresses of your trackers in `addresses` and change `slime_ip` to the IP address of the computer you're running SlimeVR on.

## Usage - Please read the steps in their entirety as the process is currently time sensitive!
1. Start the SlimeVR server and wait a few seconds for it to fully load. If you want to use other trackers with SlimeVR, don't turn them on until after you have MoSlime connected. Note: Any Mocopi tracker can be used on any body part. The plastic cover is purely cosmetic!
2. Run `python3 moslime.py`, then immediately turn all the trackers back on. You can either do this manually or by plugging in the case, waiting for the trackers to light up then quickly unplugging it.
3. You should see the lights on the trackers illuminate green one by one as they connect in the terminal. While they are connecting, leave the trackers in the case on a flat and stable surface. DO NOT touch them!
4. Once you see `Safe to start tracking` in the terminal, make sure all trackers appear in SlimeVR. They should show up as IMU Tracker 1, IMU Tracker 2, etc.\
 4a. [Optional]: At this point you can also turn on any additional SlimeVR trackers and use them alongside the Mocopis. Make sure you always start MoSlime first. This issue will be fixed in the future.
5. You can now put on your trackers. If you've never used SlimeVR before, just click on Setup Wizard on the lefthand side and follow the instructions. You can skip the Wi-Fi Settings step.

## Troubleshooting
 - If trackers are refusing to connect, try stopping the script (mash Ctrl+C till it stops), turn off all the trackers, restart Bluetooth and follow the Usage section again.
 - If your trackers are still refusing to connect, try unparing them, press the button on each tracker 10-15 times to factory reset them (they'll blink red and blue), then pair them again.
 - If you see `Safe to start tracking` but no trackers in SlimeVR, make sure you have the correct IP address and that both computers are on the same network.
 - If your Linux PC is a desktop and range/performance seems really bad, make sure you have your WiFi/BT antenna connected. Alternatively, you can also use an external Bluetooth dongle but your mileage may vary. 
