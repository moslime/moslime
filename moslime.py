#!/usr/bin/python
from bluepy import btle
import time
import threading
import moslime_common as mc
import socket
import os
import traceback

CMD_UUID = "0000ff00-0000-1000-8000-00805f9b34fb"  # BLE UUID to send commands to

os.system("clear")
TRACKER_ADDRESSES, AUTODISCOVER, AUTOSTART, SLIME_IP, SLIME_PORT = mc.cfg_from_json("moslime.json")
print()

class trackerHandler:
    pcounter = 0
    connToSlime = False
    global SLIME_IP
    global SLIME_PORT
    def __init__(self, puckMAC):
        self.trackerMac = puckMAC
        self.sock = mc.create_sock()
        self.stat_cnt = 0

    def setup_bt(self):
        while True:
            try:
                print("Connecting to MAC: " + str(self.trackerMac))
                self.puck = btle.Peripheral(self.trackerMac)
                self.puck.setMTU(40)
                self.puckCMD = self.puck.getServiceByUUID(CMD_UUID).getCharacteristics()[1]
                self.puckName = self.puck.readCharacteristic(0x0003).decode("utf-8")
                self.puck.setDelegate(NotificationHandler(self.trackerMac, self.puckName, self.sock, self.pcounter))
                print("Connected to tracker MAC: " + str(self.trackerMac) + " / " + self.puckName)
                time.sleep(2)
                self.puckCMD.write(bytearray(b"\x7e\x03\x18\xd6\x01\x00\x00"), True)
            except Exception as e:
                print(str(self.trackerMac) + " EX: " + str(e))
                time.sleep(3)
                continue
            break

    def start(self):
        # Don't do anything until SlimeVR is connected
        while not self.connToSlime:
            try:
                self.send_handshake()
                time.sleep(1)
                data, src = self.sock.recvfrom(1024)
                if "Hey OVR =D" in str(data.decode("utf-8")):
                    self.connToSlime = True
                    print("Connected tracker " + str(self.trackerMac) + " / " + self.puckName + " to SlimeVR")
                    self.pcounter += 1  
            except Exception as e:
                continue
        self.get_status()

        while True:
            try:
                self.puck.waitForNotifications(0)
                self.stat_cnt += 1
                if self.stat_cnt == 6000: # Gets tracker status around every 2 minutes
                    self.stat_cnt = 0
                    self.get_status()
            except Exception as e:
                # If waitForNotifications fails, we can safely assume the tracker disconnected.
                # Reset the packet counter and try to reconnect.
                print("Tracker " + str(self.trackerMac) + " / " + self.puckName + " disconnected. Attempting reconnect.")
                print("Disconnect reason: " + str(e))
                self.setup_bt()
                self.send_handshake()
                time.sleep(3)
                continue

    def send_handshake(self):
        fw = self.puck.readCharacteristic(0x0046) # Pulls FW version from tracker
        self.pcounter = 0
        handshake = mc.build_handshake(self.trackerMac, fw, self.pcounter)
        self.pcounter += 1
        self.sock.sendto(handshake, (SLIME_IP, SLIME_PORT))
        s_info = mc.build_sensor_info(self.pcounter)
        self.pcounter += 1
        self.sock.sendto(s_info, (SLIME_IP, SLIME_PORT))

    def get_status(self):
        self.puckCMD.write(bytearray(b"\x7e\x02\x09\x02\x9a\xda"), True)

class NotificationHandler(btle.DefaultDelegate):
    global SLIME_IP
    global SLIME_PORT
    global TRACKER_ADDRESSES

    def __init__(self, tMAC, pName, inSock: socket, pcounter):
        btle.DefaultDelegate.__init__(self)
        self.tIndex = TRACKER_ADDRESSES.index(tMAC)
        self.trakID = tMAC
        self.ignorePackets = -40
        self.offset = (0, 0, 0, 0)
        self.lastCounter = 0
        self.sock = inSock
        self.pcounter = pcounter
        self.puckName = pName

    def handleNotification(self, svc, data):
        if svc == 73: # IMU data service
            try:
                # ignorePackets - We ignore a set number of packets to account for some quaternion funkiness
                # that comes from the trackers when starting 
                #
                # offset - The quaternion from the pucks is somewhat different from what SlimeVR expects
                # so we need to do an initial calibration to make everything happy  
                # 
                if self.ignorePackets == 0:
                    self.offset = mc.process_packet(data, calibrate=True) 
                    out = mc.process_packet(data, self.offset)
                    self.lastCounter = int(out.counter) - 78125
                    self.ignorePackets += 1
                elif self.ignorePackets < 0:
                    self.ignorePackets += 1
                    return

                out = mc.process_packet(data, self.offset)

                # Data packets from Mocopi trackers have a counter that increments by 78125 with every
                # packet sent. We can use this to detect packet drops, which can indicate connection issues.
                #
                if (out.counter - self.lastCounter) != 78125:
                    a = int((out.counter - self.lastCounter) / 78125)
                    print(str(a) + " packet(s) dropped on tracker " + str(self.trakID) + " / " + self.puckName)
                self.lastCounter = out.counter

                # Build and send rotation and acceleration packets
                rot = mc.build_rotation_packet(out.qw, out.qx, out.qy, out.qz, self.pcounter)
                self.pcounter += 1
                self.sock.sendto(rot, (SLIME_IP, SLIME_PORT))
                accel = mc.build_accel_packet(out.ax, out.ay, out.az, self.pcounter)
                self.pcounter += 1
                self.sock.sendto(accel, (SLIME_IP, SLIME_PORT))

            except Exception as e:
                if "unpack requires a buffer of 2 bytes" in str(e):
                    print("Following exception can be ignored:")
                print("class exception: " + str(e) + " trackerid: " + str(self.trakID))

        elif svc == 34: # Command response service
            if bytearray(b"\x7e\x07\x09") in data: # Battery Message response
                out = mc.calc_batt(data)
                batt = mc.build_battery_packet(out[0], out[1], self.pcounter)
                self.pcounter += 1
                self.sock.sendto(batt, (SLIME_IP, SLIME_PORT))

def trackerMain(mac, puckBTReady, allReady):
    handler = trackerHandler(mac)
    handler.setup_bt()
    puckBTReady.set()
    while not allReady.is_set():
        time.sleep(0.1)
    handler.start()

print("Restarting Bluetooth...")
os.system("bluetoothctl power off")
time.sleep(2)
print()
os.system("bluetoothctl power on")
time.sleep(2)
os.system("clear")

if AUTODISCOVER:
    SLIME_IP, SLIME_PORT = mc.find_slime()
print("SlimeVR Server: " + SLIME_IP + ":" + str(SLIME_PORT) + "\n")

msg = '''
If they are already on, turn them off and back on.
Do not touch your trackers until you see them all in SlimeVR.
If one or more trackers refuses to connect, you may need to re-pair it.

Press Ctrl+C at any time to quit.'''

if AUTOSTART:
    print('Connecting to trackers in 10 seconds. Turn on all your trackers and place them on a flat surface.' + msg)
    time.sleep(10)
else:
    print('Turn on all your trackers, place them on a flat surface and press enter.' + msg)
    input()

print("Connecting to " + str(len(TRACKER_ADDRESSES)) + " trackers.\n")

allReady = threading.Event()
for index, mac in enumerate(TRACKER_ADDRESSES):
    puckBTReady  = threading.Event()
    globals()["puck" + str(index) + "Thread"] = threading.Thread(target=trackerMain, args=(mac, puckBTReady, allReady,), daemon=True)
    globals()["puck" + str(index) + "Thread"].start()
    puckBTReady.wait()
    print()

allReady.set()
time.sleep(2)
print("All trackers are connected\n")

# Keep main alive until Ctrl + C
try:
    while True:
        time.sleep(999999999)

except KeyboardInterrupt:
    print("\nQuitting...")