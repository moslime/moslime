## Raspberry Pi Setup - not ready yet, just adding documentation
For ease of use, we are providing a ready to use Raspberry Pi image. We **highly** recommend using a Raspberry Pi 4B or better but this should work on the 3B and 3B+.

## Prerequisites
- Raspberry Pi 3B or better (preferably a Pi 4B or 400)
- An SD card or USB drive that's 4GB or bigger
- An ethernet connection for the Pi is ***highly*** recommended

## Steps
1. Download the latest moslime.img from the [releases section](https://github.com/lmore377/moslime/releases).
2. Download the [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
3. Open the Imager, click Choose OS, Use Custom, then select the moslime.img you downloaded.
4. Click Choose Storage and select the drive you're using for your Raspberry Pi\
  4a. It's ***highly*** recommended that you use ethernet, but if you really want to use Wi-Fi, click the settings cog, enable "Configure wireless LAN" then enter your Wi-Fi details. Keep in mind this will have a big performance impact (mainly latency).
5. Click Write then let the image write to the SD card. When it finishes, plug the SD card/USB drive into the Pi then connect ethernet and power.
6. After about 45s, open a web browser and copy/paste this link into a new tab: (Not implemented yet, just use step 6b for now)\
   `http://moslime.local:8888/?term=xterm-256color&hostname=192.168.1.127&username=moslime&password=bW9zbGltZQ==#fontsize=20`\
  6a. If you get a "ERR_NAME_NOT_RESOLVED" error, go into your router settings to get the IP address of the Pi then just replace `moslime.local` with the IP\
  6b. If the web client just isn't connecting at all, just SSH into the Pi with this username/password: `moslime/moslime`
7. Once you're logged in, you should be presented with the launcher. From here, all the options should be pretty self explanitory.

   After following the above setup, you just need to pair your trackers (there's an experimental auto-pair included in this image) then run 'Edit MoSlime Configuration' to put the IP address of the PC running SlimeVR. 
