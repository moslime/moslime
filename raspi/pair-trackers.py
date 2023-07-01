#!/usr/bin/python3

# Make sure you edit /etc/bluetooth/main.conf, add "TemporaryTimeout = 300" somewhere there, and run "service bluetooth restart"
# If you don't, bluez might clear out the scanned device list before all the trackers are paired
# This script will also attempt to write the addresses to moslime.json

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

orig_config = json.load(open('moslime/moslime.json')) # load moslime.json to get ip, port, tps
ref_config['slime_ip'] = orig_config['slime_ip']
ref_config['slime_port'] = orig_config['slime_port']
ref_config['tps'] = orig_config['tps']

scanner = bluepy.btle.Scanner()
print("Ignore the power messages. They're normal")
os.system("bluetoothctl power off")
time.sleep(1)
os.system("bluetoothctl power on")
time.sleep(1)
print("Start scan")
try: #scan fails every other time for some reason so if it fails we just scan again lol
 devices = scanner.scan()
except:
 devices = scanner.scan()
paired = 0

for device in devices:
   try:
    if "QM-SS1" in device.getValueText(9):
      print("Pairing to: " + device.getValueText(9) + " - " + device.addr)
      time.sleep(.1)
      os.system("bluetoothctl pair " + device.addr)
      time.sleep(.5)
      os.system("bluetoothctl disconnect " + device.addr)
      time.sleep(3)
      print("Adding " + device.addr + " to config")
      ref_config['addresses'].append(device.addr)
      paired += 1
   except:
      print()

os.system("clear")
print("Paired to " + str(paired) + " trackers. Restarting bluetooth.")

#Connecting this way sometimes fails even when pairing is successful so we need to figure out a different way to test the connection.
#print("If you see any errors, let this script finish, run 'Remove all devices' in the main menu then try pairing again.")
#time.sleep(1)
#for device in devices:
#    if "3c:38:f4" in device.addr:
#      os.system("bluetoothctl connect " + device.addr)
#      time.sleep(1)
#print()
#print("All of your trackers should be blinking green. If one or more aren't, run remove in the main menu and try again.")
#print("Disconnecting all in 10s")


time.sleep(1)
os.system("bluetoothctl power off")
time.sleep(1)
os.system("bluetoothctl power on")

print("Writing config to moslime.json")
with open("moslime/moslime.json", "w") as f:
  json.dump(ref_config, f, indent=4)

print("All done, try running MoSlime now. If trackers fail to connect, run 'Remove all BT devices' then try pairing again.")
print("Returning to main menu in 8s.")
time.sleep(8)

