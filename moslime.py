#!/usr/bin/python3
import json
from collections import namedtuple
from bluepy import btle
import socket
import time
import struct
import threading
import os

ref_config = {  # Reference config, used when moslime.json is missing
    "addresses": ["3C:38:F4:XX:XX:XX"] * 6,
    "autodiscovery": True,
    "slime_ip": "127.0.0.1",
    "slime_port": 6969,
    "tps": 150
}

try:
    f = open('moslime.json')
except:
    with open("moslime.json", "w") as f:
        json.dump(ref_config, f, indent=4)
    print("moslime.json not found. A new config file has been created, please edit it before attempting to run MoSlime again.")
    quit()

try:
    CONFIG = json.load(f)
except:
    print("There was an issue loading moslime.json. Please check that there aren't any stray commas or misspellings.")
    print("If this issue persists, delete moslime.json and run MoSlime again to regenerate the config.")
    quit()

try:
    TRACKER_ADDRESSES = CONFIG['addresses']
    AUTODISCOVER = CONFIG['autodiscovery']  # SlimeVR autodiscovery
    SLIME_IP = CONFIG['slime_ip']  # SlimeVR Server
    SLIME_PORT = CONFIG['slime_port']  # SlimeVR Server
    TPS = CONFIG['tps']  # SlimeVR packet frequency. Keep below 300 (above 300 has weird behavior)
except:
    ref_config['addresses'] = CONFIG['addresses']
    with open("moslime.json", "w") as f:
        json.dump(ref_config, f, indent=4)
    print("One or more options were missing from moslime.json. The file has been recreated and your MAC addresses have been copied over.")
    print("Please check the file then try running MoSlime again. If this issue persists, go to the support channel in the Discord.")
    quit()

PACKET_COUNTER = 0  # global packet counter. MUST be incremented every time a packet is sent or slime gets mad
CMD_UUID = '0000ff00-0000-1000-8000-00805f9b34fb'  # BLE UUID to send commands to
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Setup network socket
ALL_CONNECTED = False
MocopiPacket = namedtuple('MocopiPacket', 'sensor_id, qw, qx, qy, qz, ax, ay, az')  # container that holds the data of a given trackerID
for i in range(len(TRACKER_ADDRESSES)):
    globals()['sensor' + str(i) + 'data'] = MocopiPacket(0, 0, 0, 0, 0, 0, 0, 0)  # Create tracker data containers


def build_handshake():
    fw_string = "MoSlime"
    buffer = b'\x00\x00\x00\x03'  # packet 3 header
    buffer += struct.pack('>Q', PACKET_COUNTER)  # packet counter
    buffer += struct.pack('>I', 0)  # board ID
    buffer += struct.pack('>I', 0)  # IMU type
    buffer += struct.pack('>I', 0)  # MCU type
    buffer += struct.pack('>III', 0, 0, 0)  # IMU info
    buffer += struct.pack('>I', 0)  # Build
    buffer += struct.pack('B', len(fw_string))  # length of fw string
    buffer += struct.pack(str(len(fw_string)) + 's', fw_string.encode('UTF-8'))  # fw string
    buffer += struct.pack('6s', b'\x49\x4C\x4F\x56\x45\x50')  # MAC address
    buffer += struct.pack('B', 255)
    return buffer


def add_imu(trackerID):
    global PACKET_COUNTER
    buffer = b'\x00\x00\x00\x0f'  # packet 15 header
    buffer += struct.pack('>Q', PACKET_COUNTER)  # packet counter
    buffer += struct.pack('B', trackerID)  # tracker id (shown as IMU Tracker #x in SlimeVR)
    buffer += struct.pack('B', 0)  # sensor status
    buffer += struct.pack('B', 0)  # sensor type
    sock.sendto(buffer, (SLIME_IP, SLIME_PORT))
    print("Add IMU: " + str(trackerID))
    PACKET_COUNTER += 1


def build_rotation_packet(qw: float, qx: float, qy: float, qz: float, tracker_id: int):
    # qw,qx,qy,qz: parts of a quaternion / trackerID: Tracker ID
    buffer = b'\x00\x00\x00\x11'  # packet 17 header
    buffer += struct.pack('>Q', PACKET_COUNTER)  # packet counter
    buffer += struct.pack('B', tracker_id)  # tracker id (shown as IMU Tracker #x in SlimeVR)
    buffer += struct.pack('B', 1)  # data type (use is unknown)
    buffer += struct.pack('>ffff', -qx, qz, qy, qw)  # quaternion as x,z,y,w
    buffer += struct.pack('B', 0)  # calibration info (seems to not be used by SlimeVR currently)
    return buffer


def build_accel_packet(ax, ay, az, trackerID):
    buffer = b'\x00\x00\x00\x04'  # packet 4 header
    buffer += struct.pack('>Q', PACKET_COUNTER)  # packet counter
    buffer += struct.pack('>fff', ax, ay, az)  # acceleration as x y z
    buffer += struct.pack('B', trackerID)  # tracker id (shown as IMU Tracker #x in SlimeVR)
    return buffer


def sendCommand(tId, cmd):  # id: Tracker ID / cmd: Command to send
    if cmd == "start":  # Start tracker data stream
        globals()['cmd_ch_t' + str(tId)].write(bytearray(b'\x7e\x03\x18\xd6\x01\x00\x00'), True)
    else:
        print("Invalid command")


def interp(val_in):  # mocopi sends quat as a signed int from -8192to8192 but quats are -1to1. this scales down the mocopi data
    return (((val_in - -8192) * (1 - -1)) / (8192 - -8192)) + -1


def hexToQuat(bytes):
    return interp(int.from_bytes(bytes, byteorder='little', signed=True))


def hexToFloat(bytes):
    return struct.unpack('<e', bytes)[0]


def waitForNotif(num, mac):  # starts the notification listener for a given trackerID. should be ran on its own thread
    while True:
        try:
            globals()['t' + str(num)].waitForNotifications(0)
        except Exception as e:
            print("Tracker " + str(num) + " disconnected. Attempting reconnect.")
            connectTracker(mac, num, True)
            time.sleep(3)
            continue


def multiply(w1, x1, y1, z1, w2, x2, y2, z2):  # multiply a quat by another
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return w, x, y, z


def sendAllIMUs(mac_addrs):  # mac_addrs: Table of mac addresses. Just used to get the number of trackers
    global TPS, PACKET_COUNTER
    while True:
        for z in range(TPS):
            for i in range(len(mac_addrs)):
                sensor = globals()['sensor' + str(i) + 'data']
                rot = build_rotation_packet(sensor.qw, sensor.qx, sensor.qy, sensor.qz, i)
                sock.sendto(rot, (SLIME_IP, SLIME_PORT))
                PACKET_COUNTER += 1
                # Accel is still technically not ready yet (it doesn't rotate with the axes) but it's enough for features like tap detection
                accel = build_accel_packet(sensor.ax, sensor.ay, sensor.az, i)
                sock.sendto(accel, (SLIME_IP, SLIME_PORT))
                PACKET_COUNTER += 1
            time.sleep(1 / TPS)


def connectTracker(mac_addr, tId, retry):
    # mac_addr: Tracker MAC address / id: Tracker ID to send to slime (should be 0 for the first tracker, anything for additional trackers)
    while True:
        try:
            print("Connecting to MAC: " + str(mac_addr) + " ID: " + str(tId))
            globals()['t' + str(tId)] = btle.Peripheral(mac_addr)
            globals()['t' + str(tId)].setDelegate(NotificationHandler(tId))
            globals()['t' + str(tId)].setMTU(40)
            globals()['cmd_t' + str(tId)] = globals()['t' + str(tId)].getServiceByUUID(CMD_UUID)
            globals()['cmd_ch_t' + str(tId)] = globals()['cmd_t' + str(tId)].getCharacteristics()[1]
            time.sleep(.5)
            if retry:
                globals()['cmd_ch_t' + str(tId)].write(bytearray(b'\x7e\x03\x18\xd6\x01\x00\x00'), True)
        except Exception as e:
            print("Tracker " + str(tId) + " EX: " + str(e))
            time.sleep(3)
            continue
        break


def correctAccel(aX, aY, aZ):  # Used to correct accel data from the tracker (multiplying the tracker data by 0.12 makes it match the standard m/s^2)
    aX2 = aX * 0.12
    aY2 = aY * 0.12
    aZ2 = aZ * 0.12
    return aX2, aY2, aZ2


class NotificationHandler(btle.DefaultDelegate):  # takes in tracker data, applies any needed corrections and saves it to the container for a given trackerID
    ignorePackets = -10
    # When Mocopi trackers start they sometimes send a few packets that aren't IMU data so we just discard the first
    # 10 to be safe
    offset = (0, 0, 0, 0)
    lastCounter = 0

    def __init__(self, tID):
        btle.DefaultDelegate.__init__(self)
        print("Connected to tracker ID " + str(tID))
        self.trakID = tID

    def handleNotification(self, _, data):
        global ALL_CONNECTED
        if ALL_CONNECTED:  # Don't collect data until all trackers successfully connect
            try:
                # take in hex data and chop it up into usable stuff
                pw = hexToQuat(data[8:10])
                px = hexToQuat(data[10:12])
                py = hexToQuat(data[12:14])
                pz = hexToQuat(data[14:16])
                ax = hexToFloat(data[24:26])
                az = hexToFloat(data[26:28])
                ay = hexToFloat(data[28:30])
                if self.ignorePackets == 0:
                    # Once a number of packets have been discarded, we calculate the offset needed to make SlimeVR happy
                    self.offset = (pw, -px, -py, -pz)
                    self.ignorePackets += 1
                    self.lastCounter = int.from_bytes(data[1:8], "little")
                    return
                elif self.ignorePackets < 0:
                    self.ignorePackets += 1
                    self.lastCounter = int.from_bytes(data[1:8], "little")
                    return
                qwc, qxc, qyc, qzc = multiply(pw, px, py, pz, *self.offset)  # apply quat offset/correction
                axc, ayc, azc = correctAccel(ax, ay, az)  # apply accel offset
                globals()['sensor' + str(self.trakID) + 'data'] = MocopiPacket(self.trakID, qwc, qxc, qyc, qzc, axc, ayc,
                                                                               azc)  # store tracker data in its container
                if (int.from_bytes(data[1:8], "little") - self.lastCounter) != 78125:
                    print("Packet dropped on tracker " + str(self.trakID) + ", current packet num: " + str(
                        int.from_bytes(data[1:8], "little")))
                self.lastCounter = int.from_bytes(data[1:8], "little")
            except Exception as e:
                if "unpack requires a buffer of 2 bytes" in str(e):
                    print("Following exception can be ignored:")
                print(
                    "class exception: " + str(e) + " trackerid: " + str(self.trakID))


print("Restarting Bluetooth...")
os.system("bluetoothctl power off")
time.sleep(3)
os.system("bluetoothctl power on")
time.sleep(1)
os.system("clear")

print("Connecting will start in 10s. Turn on all your trackers, place them on a table and don't touch them until you see Safe to start tracking.")
print("If one or more trackers refuses to connect, you may need to re-pair it")
print()
time.sleep(10)
print("Connecting to " + str(len(TRACKER_ADDRESSES)) + " trackers.")

# Connect all trackers then send the start command to each one
for i in range(len(TRACKER_ADDRESSES)):
    connectTracker(TRACKER_ADDRESSES[i], i, False)

for i in range(len(TRACKER_ADDRESSES)):
    sendCommand(i, "start")

time.sleep(3)  # Give trackers a few seconds to stabilize

if AUTODISCOVER:
    SLIME_IP = "255.255.255.255"
    print('Autodiscovery enabled. If this gets stuck at "Searching...", try disabling it and manually set the SlimeVR IP.')
else:
    SLIME_IP = CONFIG['slime_ip']
    SLIME_PORT = CONFIG['slime_port']
    print('Using SlimeVR IP from config. If this gets stuck at "Searching...", make sure you have the right IP set in moslime.json')

found = False
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # allow broadcasting on this socket
handshake = build_handshake()
sock.bind(('0.0.0.0', 9696))  # listen on port 9696 to avoid conflicts with slime
sock.settimeout(1)
print("Searching for SlimeVR")

while not found:
    try:
        print("Searching...")
        sock.sendto(handshake, (SLIME_IP, SLIME_PORT))  # broadcast handshake on all interfaces
        data, src = sock.recvfrom(1024)

        if "Hey OVR =D" in str(data.decode('utf-8')):  # SlimeVR responds with a packet containing "Hey OVR =D"
            found = True
            SLIME_IP = src[0]
            SLIME_PORT = src[1]
    except:
        time.sleep(0)

print("Found SlimeVR at " + str(SLIME_IP) + ":" + str(SLIME_PORT))
PACKET_COUNTER += 1
time.sleep(.1)

# Add additional IMUs. SlimeVR only supports one "real" tracker per IP, so the workaround is to make all the
# trackers appear as extensions of the first tracker.
for i in range(len(TRACKER_ADDRESSES)):
    for z in range(3):  # slimevr has been missing "add IMU" packets so we just send them 3 times to make sure they get through
        add_imu(i)

for i in range(len(TRACKER_ADDRESSES)):  # Start notification threads
    globals()['s' + str(i) + 'thread'] = threading.Thread(target=waitForNotif, args=(i, TRACKER_ADDRESSES[i]))
    globals()['s' + str(i) + 'thread'].start()

time.sleep(.5)
ALL_CONNECTED = True

print("Safe to start tracking. To stop MoSlime, press Ctrl-C multiple times.")
print("If any of your trackers are still blinking blue, they need to be re-paired because otherwise they will turn off after a few minutes.")

while True:
    sendAllIMUs(TRACKER_ADDRESSES)
    continue

