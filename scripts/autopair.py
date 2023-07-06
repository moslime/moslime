#!/usr/bin/python3

# This script will replace /etc/bluetooth/main.conf with a very slim version that includes TemporaryTimeout = 300
# which is needed to keep the trackers in the scan cache long enough to pair all of them. It *should* restore the
# file to how it was before but if it cant't for some reason, it creates a backup called bluetooth-main.conf.bak

import bluepy
import os
import time
import json

ref_config = {
  "addresses": [],
  "slime_ip": "127.0.0.1",
  "slime_port": 6969,
  "tps": 150
}

print("This script will temporarily modify /etc/bluetooth/main.conf but will restore it once it's done.")
input("If you're fine with this, press enter to coninue. If not, press Ctrl+C")
print("A backup of main.conf will be stored in the current directory just in case.")
os.system("cp /etc/bluetooth/main.conf ./bluetooth-main.conf.bak") # Make backup of /etc/bluetooth/main.conf for later restoration
time.sleep(2)
print("Stopping bluetoothd...")
os.system("systemctl stop bluetooth")
print("Modifying /etc/bluetooth/main.conf")
mainconf = open("/etc/bluetooth/main.conf", "w")
mainconf.write("[General]\nTemporaryTimeout = 300\n[Policy]\nAutoEnable=true\n")
mainconf.close()
print("Starting bluetoothd...")
os.system("systemctl start bluetooth")

try:
  orig_config = json.load(open('moslime.json')) # load moslime.json to get ip, port, tps
  ref_config['slime_ip'] = orig_config['slime_ip']
  ref_config['slime_port'] = orig_config['slime_port']
  ref_config['tps'] = orig_config['tps']
except:
  print("Existing moslime.json not found. Will generate new config.")

scanner = bluepy.btle.Scanner()
print("Ignore the power messages. They're normal")
os.system("bluetoothctl power off")
time.sleep(1)
os.system("bluetoothctl power on")
time.sleep(1)
input("Turn all your trackers off if they aren't already, turn them on then press enter to start scanning.")
print("Start LE scan")
try: #scan fails every other time for some reason so if it fails we just scan again lol
 devices = scanner.scan()
except:
 devices = scanner.scan()
paired = 0

print("Start normal scan")
os.system("bluetoothctl --timeout 10 scan on") # the above scan is only a BTLE scan and devices discovered like that can't be paired to so we need to do a normal scan too

for device in devices:
   try:
    if "QM-SS1" in device.getValueText(9):
      print("Pairing to: " + device.getValueText(9) + " - " + device.addr)
      time.sleep(.1)
      os.system("bluetoothctl pair " + device.addr)
      time.sleep(3)
      os.system("bluetoothctl disconnect " + device.addr) #the trackers stay connected after being paired so we disconnect before pairing the next one
      time.sleep(5)
      print("Adding " + device.addr + " to config")
      ref_config['addresses'].append(device.addr)
      paired += 1
   except:
      print() #do nothing if bt device isn't a tracker

# This was meant to test the pairing but sometimes it fails even if pairing was successful. Need to figure out a different way to test
#print("If you see any errors, let this script finish, run 'Remove all devices' in the main menu then try pairing again.")
#time.sleep(1)
#for device in devices:
#    if "3c:38:f4" in device.addr:
#      os.system("bluetoothctl connect " + device.addr)
#      time.sleep(1)
#print()
#print("All of your trackers should be blinking green. If one or more aren't, run remove in the main menu and try again.")
#print("Disconnecting all in 10s")

print("Paired to " + str(paired) + " trackers. Restoring main.conf and restarting bluetooth.")
os.system("systemctl stop bluetooth")
os.system("cp bluetooth-main.conf.bak /etc/bluetooth/main.conf")
os.system("systemctl start bluetooth")
time.sleep(1)

print("Writing config to moslime.json")
with open("moslime.json", "w") as f:
  json.dump(ref_config, f, indent=4)

print("All done, if you haven't already set the IP in moslime.json, do that now then try running MoSlime. If trackers fail to connect, try removing all paired devices then run pairing again.")


