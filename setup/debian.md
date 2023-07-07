# Ubuntu / Debian Setup

## Prerequisites 
- Any recent Ubuntu or Debian-based OS. It can be installed in a VM as long as the VM has usb passthrough but if you have a second computer or laptop you should install it there for performance reasons.
   - If installing in a VM, it's recommended that you go with a lightweight distro. I've personally tested [antiX](https://antixlinux.com/) and it seems to work very well. I'd suggest using the base image.
- A Bluetooth card that supports Bluetooth 4.2 or higher (you can check by running `hciconfig -a` in a terminal and looking at HCI/LMP version)
  - If you're using a VM, make sure the bluetooth card can be connected to it though USB passthrough. The whole card needs to be connected; stuff like bluetooth passthrough in VMware won't work. Also keep in mind that unless you plug in a second bluetooth card, you'll lose bluetooth on your host OS while you have the VM running.
  - *Technically* the minimum required version is 4.0 but it seems like versions below 4.2 have issues with multiple connections.

## Instructions
1. Run the following commands in a terminal (will be made into a simple script later):
```
sudo apt update
sudo apt upgrade -y # if asked about modifying files, just press Y then enter
sudo apt install libglib2.0-dev python3-pip git bluez bluez-tools -y
git clone https://github.com/lmore377/moslime
cd moslime
sudo pip3 install -r requirements.txt # read note at the bottom
```
 - If you get  an error about breaking system packages at the `pip3` command, just add `--break-system-packages` to it. This won't actually break anything.
2. Continue by following the instructions here: [first-time-and-usage.md](setup/first-time-and-usage.md)
