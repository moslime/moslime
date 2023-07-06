## Raspberry Pi Setup
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
6. SSH into the Pi using the username/password: `moslime/moslime`  You *should* be able to use `moslime.local` for the address but if that doesn't work, just check your router settings or use a network scanner to get the IP address of your Pi.
7. Once you're logged in, you should be presented with the launcher. From here, all the options should be pretty self explanitory.

   After following the above setup, you just need to pair your trackers (either manually using bluetoothctl or using the experimental auto-pair included in this image) then run 'Edit MoSlime Configuration' to put the IP address of the PC running SlimeVR. 

## DIY Image
If you don't trust the image provided (understandable), you can create your own build. Just run these commands in a fresh raspbian lite image:
```
sudo apt install git libglib2.0-dev
git clone https://github.com/lmore377/moslime
cd moslime
sudo pip3 install -r requirements.txt` (if you get a "externally-managed-enviroment" error, add `--break-system-packages` to the command. don't worry this won't *actually* break anything)
cd ..
cp moslime/raspi/launcher.sh ./
./launcher.sh
```
Once the launcher runs, just run update in it and that should get everything situated. I'd recommend adding it to the end of .bashrc so that way it autoruns when you SSH in.
If you want to try auto-pair on a DIY build, make sure you edit `/etc/bluetooth/main.conf` and add `TemporaryTimeout = 300` somwhere in there.
