#!/usr/bin/python3
import json
from collections import namedtuple

from bluepy import btle
from scipy.interpolate import interp1d
import socket
import time
import struct
import threading
import numpy as np

CONFIG = json.load(open('moslime.json'))
TRACKER_ADDRESSES = CONFIG['addresses']
SLIME_IP = CONFIG['slime_ip']  # SlimeVR Server
SLIME_PORT = CONFIG['slime_port']  # SlimeVR Server
TPS = CONFIG['tps']  # SlimeVR packet frequency. Keep below 300 (above 300 has weird behavior)


def build_handshake():
    buffer = b'\x00\x00\x00\x03'  # packet 3 header
    buffer += struct.pack('>Q', PACKET_COUNTER)
    buffer += struct.pack('>LLLLLLL', 0, 0, 0, 0, 0, 0, 0)
    buffer += struct.pack('B', len("MoSlime"))
    buffer += struct.pack(str(len("MoSlime")) + 's', "MoSlime".encode('UTF-8'))
    buffer += struct.pack('6s', '111111'.encode('UTF-8'))
    buffer += struct.pack('B', 255)
    return buffer


def add_imu(trackerID):
    global PACKET_COUNTER
    buffer = b'\x00\x00\x00\x0f'  # packet 15 header
    buffer += struct.pack('>Q', PACKET_COUNTER)
    buffer += struct.pack('B', trackerID)
    buffer += struct.pack('B', 3)
    buffer += struct.pack('B', 5)
    buffer += struct.pack('B', 255)
    sock.sendto(buffer, (SLIME_IP, SLIME_PORT))
    print("Add IMU: " + str(trackerID))
    PACKET_COUNTER += 1


def build_rotation_packet(qw: float, qx: float, qy: float, qz: float, tracker_id: int):
    # quant: Array containing the quanterion / trackerID: Tracker ID
    buffer = b'\x00\x00\x00\x11'  # packet 17 header
    buffer += struct.pack('>Q', PACKET_COUNTER)
    buffer += struct.pack('B', tracker_id)
    buffer += struct.pack('B', 1)
    buffer += struct.pack('>ffff', -qx, qz, qy, qw)  # expect x,z,y,w
    buffer += struct.pack('B', 0)
    return buffer


def build_accel_packet(ax, ay, az, trackerID):
    buffer = b'\x00\x00\x00\x04'  # packet 4 header
    buffer += struct.pack('>Q', PACKET_COUNTER)
    buffer += struct.pack('>fff', ax, ay, az)
    buffer += struct.pack('B', trackerID)
    return buffer


def sendCommand(tId, cmd):  # id: Tracker ID / cmd: Command to send
    if cmd == "start":  # Start tracker data stream
        globals()['cmd_ch_t' + str(tId)].write(bytearray(b'\x7e\x03\x18\xd6\x01\x00\x00'), True)
    else:
        print("Invalid command")


interp = interp1d([-8192, 8192], [-1, 1])


def hexToQuat(bytes):
    return interp(int.from_bytes(bytes, byteorder='little', signed=True))


def hexToFloat(bytes):
    return np.frombuffer(bytes, dtype=np.float16)


def waitForNotif(num):
    while True:
        globals()['t' + str(num)].waitForNotifications(0)


def multiply(w1, x1, y1, z1, w2, x2, y2, z2):
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return w, x, y, z


PACKET_COUNTER = 0
CMD_UUID = '0000ff00-0000-1000-8000-00805f9b34fb'
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ZERO_QUAT = [1, 0, 0, 0]
ALL_CONNECTED = False
MocopiPacket = namedtuple('MocopiPacket', 'sensor_id, qw, qx, qy, qz, ax, ay, az')
for i in range(len(TRACKER_ADDRESSES)):
    globals()['sensor' + str(i) + 'data'] = MocopiPacket(0, 0, 0, 0, 0, 0, 0, 0)  # Create tracker data containers


def sendAllIMUs(mac_addrs):  # mac_addrs: Table of mac addresses. Just used to get number of trackers
    global TPS, PACKET_COUNTER
    while True:
        for z in range(TPS):
            for i in range(len(mac_addrs)):
                sensor = globals()['sensor' + str(i) + 'data']
                rot = build_rotation_packet(sensor.qw, sensor.qx, sensor.qy, sensor.qz, i)
                sock.sendto(rot, (SLIME_IP, SLIME_PORT))
                PACKET_COUNTER += 1
                #Accel is not ready yet
                #accel = build_accel_packet(sensor.ax, sensor.ay, sensor.az, i)
                #sock.sendto(accel, (SLIME_IP, SLIME_PORT))
                #PACKET_COUNTER += 1
            time.sleep(1 / TPS)


def connectTracker(mac_addr, tId):
    # mac_addr: Tracker MAC address / id: Tracker ID to send to slime (should be 0 for first tracker, anything for additional trackers)
    while True:
        try:
            print("Connecting to MAC: " + str(mac_addr) + " ID: " + str(tId))
            globals()['t' + str(tId)] = btle.Peripheral(mac_addr)
            globals()['t' + str(tId)].setDelegate(NotificationHandler(tId))
            globals()['t' + str(tId)].setMTU(40)
            globals()['cmd_t' + str(tId)] = globals()['t' + str(tId)].getServiceByUUID(CMD_UUID)
            globals()['cmd_ch_t' + str(tId)] = globals()['cmd_t' + str(tId)].getCharacteristics()[1]
            time.sleep(.5)
        except Exception as e:
            print("Tracker " + str(tId) + " EX: " + str(e))
            time.sleep(3)
            continue
        break


def correct(aX, aY, aZ):
    SEN4G = 8192.0
    ASC4G = ((32768.0 / SEN4G) / 32768.0) * 9.80665
    aX2 = aX * ASC4G
    aY2 = aY * ASC4G
    aZ2 = aZ * ASC4G
    return aX2, aY2, aZ2


class NotificationHandler(btle.DefaultDelegate):
    trakID = 0
    ignorePackets = -10
    # When Mocopi trackers start they sometimes send a few packets that aren't IMU data so we just discard the first
    # 10 to be safe
    offset = (0, 0, 0, 0)

    def __init__(self, tID):
        btle.DefaultDelegate.__init__(self)
        print("Connected to tracker ID " + str(tID))
        self.trakID = tID

    def handleNotification(self, _, data):
        global ZERO_QUAT, ALL_CONNECTED
        if ALL_CONNECTED:  # Don't collect data until all trackers successfully connect
            try:
                pw = hexToQuat(data[8:10])
                px = hexToQuat(data[10:12])
                py = hexToQuat(data[12:14])
                pz = hexToQuat(data[14:16])
                ax = hexToFloat(data[24:26])
                ay = hexToFloat(data[26:28])
                az = hexToFloat(data[28:30])
                if self.ignorePackets == 0:
                    # Once a number of packets have been discarded, we calculate the offset needed to make SlimeVR happy
                    self.offset = multiply(pw, -px, -py, -pz, 1, 0, 0, 0)
                    self.ignorePackets += 1
                    return
                elif self.ignorePackets < 0:
                    self.ignorePackets += 1
                qwc, qxc, qyc, qzc = multiply(pw, px, py, pz, *self.offset)
                az, ay, az = correct(ax, ay, az)
                globals()['sensor' + str(self.trakID) + 'data'] = MocopiPacket(self.trakID, qwc, qxc, qyc, qzc, ax, ay,
                                                                               az)
            except Exception as e:
                print("class exception: " + str(e) + " trackerid: " + str(self.trakID))


print("Connecting to " + str(len(TRACKER_ADDRESSES)) + " trackers.")
# Connect all trackers then send start command
for i in range(len(TRACKER_ADDRESSES)):
    connectTracker(TRACKER_ADDRESSES[i], i)
for i in range(len(TRACKER_ADDRESSES)):
    sendCommand(i, "start")
time.sleep(3)  # Give trackers a few seconds to stabilize
# Send the initial handshake to SlimeVR
handshake = build_handshake()
PACKET_COUNTER += 1
sock.sendto(handshake, (SLIME_IP, SLIME_PORT))
print("Handshake")
time.sleep(.1)

# Add additional IMUs. SlimeVR only supports one "real" tracker per IP so the workaround is to make all the
# trackers appear as extensions of the first tracker.
for i in range(len(TRACKER_ADDRESSES)):
    add_imu(i)
for i in range(len(TRACKER_ADDRESSES)):  # Start notification threads
    globals()['s' + str(i) + 'thread'] = threading.Thread(target=waitForNotif, args=(i,))
    globals()['s' + str(i) + 'thread'].start()
time.sleep(.5)
ALL_CONNECTED = True
print("Safe to start tracking")
while True:
    sendAllIMUs(TRACKER_ADDRESSES)
    continue

