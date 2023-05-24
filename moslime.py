#!/usr/bin/python3
from bluepy import btle
from scipy.interpolate import interp1d
import socket
import time
import struct
import threading

# This is all you need to set. You can put as few or as many trackers as you want (performance might suffer a bit with more than 6 trackers)
tracker_addrs = ['3C:38:F4:xx:xx:xx', '3C:38:F4:xx:xx:xx', '3C:38:F4:xx:xx:xx', '3C:38:F4:xx:xx:xx', '3C:38:F4:xx:xx:xx', '3C:38:F4:xx:xx:xx']
UDP_IP = "192.168.1.191" # SlimeVR Server
UDP_PORT = 6969 # SlimeVR Server

#no touch
cmd_uuid = '0000ff00-0000-1000-8000-00805f9b34fb'
m = interp1d([-8192,8192],[-1,1])
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
quat_zero = [1,0,0,0]
packet_counter = 0
allConnected = False
sensorrcvd = []
for i in range(len(tracker_addrs)):
  globals()['sensor'+ str(i) + 'data'] = {'sensor_id': 0,'quat': {'x': 0,'y': 0,'z': 0,'w': 0}} # Create tracker data containers
  globals()['sensorrcvd'].append(False) # Create "tracker received" flags

def multiply(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return w, x, y, z

def hexToQuat(bytes):
    return m(int.from_bytes(bytes, byteorder='little', signed=True))

def connectTracker(mac_addr, tId): # mac_addr: Tracker MAC address / id: Tracker ID to send to slime (should be 0 for first tracker, anything for additional trackers)
  while True:
   try:
    print("Connecting to MAC: " + str(mac_addr) + " ID: " + str(tId))
    globals()['t'+ str(tId)] = btle.Peripheral(mac_addr)
    globals()['t'+ str(tId)].setDelegate(NotificationHandler(tId))
    globals()['cmd_t'+ str(tId)] =  globals()['t'+ str(tId)].getServiceByUUID(cmd_uuid)
    globals()['cmd_ch_t'+ str(tId)] =  globals()['cmd_t'+ str(tId)].getCharacteristics()[1]
    time.sleep(.5)
   except Exception as e:
    print("Tracker " + str(tId) + " EX: " + str(e))
    time.sleep(3)
    continue
   break

def sendCommand(tId, cmd): # id: Tracker ID / cmd: Command to send
  if cmd == "start": # Start tracker data stream
    globals()['cmd_ch_t'+ str(tId)].write(bytearray([0x7e, 0x03, 0x18, 0xd6, 0x01, 0x00, 0x00]), True)
  else:
    print("Invalid command")

def build_handshake(pcounter): # pcounter: Packet number (should be fed by global counter)
    mapping = {'packet_type': 3,'packet_id': 0,'board': 2,'imu': 3,'mcu' : 4,'imu_info' : [5,6,7],'build' : 8,'firm': "test",'mac' : "111111"}
    mapping['packet_id'] = pcounter
    buffer = b''
    buffer += struct.pack('>L', mapping['packet_type'])
    buffer += struct.pack('>Q', mapping['packet_id'])
    buffer += struct.pack('>L', mapping['board'])
    buffer += struct.pack('>L', mapping['imu'])
    buffer += struct.pack('>L', mapping['mcu'])
    buffer += struct.pack('>L', mapping['imu_info'][0])
    buffer += struct.pack('>L', mapping['imu_info'][1])
    buffer += struct.pack('>L', mapping['imu_info'][2])
    buffer += struct.pack('>L', mapping['build'])
    buffer += struct.pack('B', len(mapping['firm']))
    buffer += struct.pack(str(len(mapping['firm'])) + 's', mapping['firm'].encode('UTF-8'))
    buffer += struct.pack('6s', mapping['mac'].encode('UTF-8'))
    buffer += struct.pack('B', 255)
    return buffer

def add_imu(trackerID):
    global packet_counter
    mapping = {'packet_type': 15,'packet_id': 1, 'sensor_id': 64, 'sensor_status': 3, 'sensor_type' : 5}
    mapping['sensor_id'] = trackerID
    mapping['packet_id'] = packet_counter
    buffer = b''
    buffer += struct.pack('>L', mapping['packet_type'])
    buffer += struct.pack('>Q', mapping['packet_id'])
    buffer += struct.pack('B', mapping['sensor_id'])
    buffer += struct.pack('B', mapping['sensor_status'])
    buffer += struct.pack('B', mapping['sensor_type'])
    buffer += struct.pack('B', 255)
    sock.sendto(buffer, (UDP_IP, UDP_PORT))
    print("Add IMU: " + str(trackerID))
    packet_counter += 1

def build_imu_packet(quant, pcounter, trackerID): # quant: Array containing the quanterion / pcounter: Packet number (should be fed by global counter) / trackerID: Tracker ID
    mapping = {'packet_type': 17,'packet_id': 1,'sensor_id': 0,'data_type': 1,'quat': {'x': 0,'y': 0,'z': 0,'w': 0},'calibration_info': 0}    
    mapping['quat']['x'] = -quant[0]
    mapping['quat']['y'] = -quant[1]
    mapping['quat']['z'] = quant[2]
    mapping['quat']['w'] = quant[3]
    mapping['packet_id'] = pcounter
    mapping['sensor_id'] = trackerID
    buffer = b''
    buffer += struct.pack('>L', mapping['packet_type'])
    buffer += struct.pack('>Q', mapping['packet_id'])
    buffer += struct.pack('B', mapping['sensor_id'])
    buffer += struct.pack('B', mapping['data_type'])
    buffer += struct.pack('>ffff', *mapping['quat'].values())
    buffer += struct.pack('B', mapping['calibration_info'])
    return buffer

def waitForNotif(num): # num: Tracker ID
  while True:
   globals()['t'+ str(num)].waitForNotifications(0)

def sendAllIMUs(mac_addrs): # mac_addrs: Table of mac addresses. Just used to get number of trackers
  global sensorrcvd
  for i in range(len(mac_addrs)):
    while True:
     for i in range(50): # This and the time.sleep are needed to limit the packet rate to 50 per second. Without it, the PPS goes up to 20k and it starts resending IMU data that has already been sent.
      if all([True for x in sensorrcvd]):
        for i in range(len(mac_addrs)):
          global packet_counter
          sensor = globals()['sensor'+ str(i) + 'data']  
          imu = build_imu_packet([sensor['quat']['x'], sensor['quat']['y'], sensor['quat']['z'], sensor['quat']['w']], packet_counter, i)
          sock.sendto(imu, (UDP_IP, UDP_PORT))
          packet_counter += 1
          tr1 = tr2 = tr3 = tr4 = tr5 = tr6 = 0
      time.sleep(0.02)

def waitForNotif(num):
  while True:
   globals()['t'+ str(num)].waitForNotifications(0)

class NotificationHandler(btle.DefaultDelegate):
   trakID = 0
   ignorePackets = -10 # When Mocopi trackers start they sometimes send a few packets that aren't IMU data so we just discard the first 10 to be safe
   offset = [0,0,0,0]
   def __init__(self, tID):
        btle.DefaultDelegate.__init__(self)
        print("Connected to tracker ID " + str(tID))
        self.trakID = tID
   def handleNotification(self, cHandle, data):
    global quat_zero, allConnected
    if allConnected: # Don't collect data until all trackers successfully connect 
     try:
       if self.ignorePackets == 0: # Once a number of packets have been discarded, we calculate the offset needed to make SlimeVR happy
         tmp_quant = [hexToQuat(data[8:10]), -hexToQuat(data[10:12]), -hexToQuat(data[12:14]), -hexToQuat(data[14:16])]
         self.offset = multiply(tmp_quant, quat_zero)
         self.ignorePackets += 1
       elif self.ignorePackets < 0:
         self.ignorePackets += 1

       quant_corrected = multiply([hexToQuat(data[8:10]), hexToQuat(data[10:12]), hexToQuat(data[12:14]), hexToQuat(data[14:16])], self.offset)
       quant_W = quant_corrected[0]
       quant_X = quant_corrected[1]
       quant_Y = -quant_corrected[3]
       quant_Z = quant_corrected[2]
         
       globals()['sensor'+ str(self.trakID) + 'data'] = {'sensor_id': self.trakID,'quat': {'x': quant_X, 'y': quant_Y, 'z': quant_Z, 'w': quant_W}}
       globals()['sensorrcvd'][self.trakID] = True
     except Exception as e:
        print("class exception: " + str(e) + " trackerid: " + str(self.trakID))

print("Connecting to " + str(len(tracker_addrs)) + " trackers.")

# Connect all trackers then send start command
for i in range(len(tracker_addrs)):
  connectTracker(tracker_addrs[i], i)
for i in range(len(tracker_addrs)):
  sendCommand(i, "start")

time.sleep(3) # Give trackers a few seconds to stabilize

#Send the initial handshake to SlimeVR
handshake = build_handshake(packet_counter)
packet_counter += 1
sock.sendto(handshake, (UDP_IP, UDP_PORT))
print("Handshake")
time.sleep(.1)

# Add additional IMUs. SlimeVR only supports one "real" tracker per IP so the workaround is to make all the 
# trackers appear as extensions of the first tracker.
for i in range(len(tracker_addrs)):
  add_imu(i)

for i in range(len(tracker_addrs)): # Start notification threads 
  globals()['s'+ str(i) + 'thread'] = threading.Thread(target=waitForNotif, args=(i,))
  globals()['s'+ str(i) + 'thread'].start()

time.sleep(.5)
allConnected = True

print("Safe to start tracking")

while True:
  sendAllIMUs(tracker_addrs)
  continue
