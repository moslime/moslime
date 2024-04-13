import struct
from collections import namedtuple
import socket
import json
import time

MocopiPacket = namedtuple('MocopiPacket', 'qw, qx, qy, qz, ax, ay, az, counter')

ref_config = {  # Reference config, used when moslime.json is missing
    "addresses": ["3C:38:F4:XX:XX:XX"] * 6,
    "autodiscovery": True,
    "slime_ip": "127.0.0.1",
    "slime_port": 6969,
    "autostart" : False
}

def cfg_from_json(jsonfile):
    try:
        f = open(jsonfile)
    except:
        with open(jsonfile, "w") as f:
            json.dump(ref_config, f, indent=4)
        print(jsonfile + " not found. A new config file has been created, please edit it before attempting to run MoSlime again.")
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
        try:
            if CONFIG['tps'] != 0:
                print("The TPS option in " + jsonfile + " is no longer used and has been removed.")
                del CONFIG['tps']
            if 'autostart' not in CONFIG.keys():
                print("Autostart option not found in "+ jsonfile +". Setting to false.")
                CONFIG['autostart'] = False
            with open("moslime.json", "w") as f:
                    json.dump(CONFIG, f, indent=4)
        except:
            pass
        AUTOSTART = CONFIG['autostart']
        return (TRACKER_ADDRESSES, AUTODISCOVER, AUTOSTART, SLIME_IP, SLIME_PORT)
    except:
        ref_config['addresses'] = CONFIG['addresses']
        with open("moslime.json", "w") as f:
            json.dump(ref_config, f, indent=4)
        print("One or more options were missing from moslime.json. The file has been recreated and your MAC addresses have been copied over.")
        print("Please check the file then try running MoSlime again. If this issue persists, go to the support channel in the Discord.")
        quit()

def find_slime():
    SLIME_PORT = 6969
    found = False
    discover_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    discover_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    discover_sock.settimeout(5)
    try:
        discover_sock.bind(('0.0.0.0', SLIME_PORT))
        attempts = 1
        while not found and attempts <= 5:
            try:
                print("Searching for SlimeVR (" + str(attempts) +"/5)...")
                data, src = discover_sock.recvfrom(1024)
                found = True
                SLIME_IP = src[0]
                SLIME_PORT = src[1]
            except KeyboardInterrupt:
                quit()
            except:
                time.sleep(.25)
                attempts += 1
                if not found and attempts > 5:
                    print("Failed to find SlimeVR. Try restarting SlimeVR then MoSlime, specifically in that order. If issues still persist, disable autodiscovery and put your IP address in moslime.json")
                    quit()
    except SystemExit:
        quit()
    except:
        print("Couldn't bind to " + str(SLIME_PORT) + " for autodiscovery. Assuming SlimeVR is running locally.")
        SLIME_IP = "127.0.0.1"
        SLIME_PORT = SLIME_PORT
        found = True
    return (SLIME_IP, SLIME_PORT)

def create_sock():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Setup network socket
    sock.bind(("0.0.0.0", 0))
    sock.settimeout(3)
    return sock
    
def calc_batt(val_in):
    a = int.from_bytes(val_in[7:11], "big")
    percent = (a - 67410) / 6501390
    voltage = percent + 3.2
    return voltage, percent

def hexToQuat(bytes):
    return int.from_bytes(bytes, byteorder='little', signed=True) / 8192

def hexToFloat(bytes):
    return struct.unpack('<e', bytes)[0]

def multiply(w1, x1, y1, z1, w2, x2, y2, z2):  # multiply a quat by another
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return w, x, y, z

def build_handshake(mac, fw, pcounter):
    fw = fw.decode("utf-8")
    fw_string = "MoSlime/bluepy - Puck Version:" + fw
    buffer = b'\x00\x00\x00\x03'  # packet 3 header
    buffer += struct.pack('>Q', pcounter)  # packet counter
    buffer += struct.pack('>I', 15)  # board type
    buffer += struct.pack('>I', 8)  # IMU type 
    buffer += struct.pack('>I', 7)  # MCU type
    buffer += struct.pack('>III', 0, 0, 0)  # IMU info
    buffer += struct.pack('>I', int(fw.replace('.', '')))  # Build
    buffer += struct.pack('B', len(fw_string))  # length of fw string
    buffer += struct.pack(str(len(fw_string)) + 's', fw_string.encode('UTF-8'))  # fw string
    buffer += struct.pack('6s', bytes.fromhex(mac.replace(':', '')))  # MAC address
    buffer += struct.pack('B', 255)
    return buffer

def build_sensor_info(pcounter):
    buffer = b'\x00\x00\x00\x0f'  # packet 15 header
    buffer += struct.pack('>Q', pcounter)  # packet counter
    buffer += struct.pack('B', 0)  # tracker id (shown as IMU Tracker #x in SlimeVR)
    buffer += struct.pack('B', 0)  # sensor status
    buffer += struct.pack('B', 8)  # sensor type - Reports BMI160 but mocopi uses BMI270. SlimeVR doesn't have 270 support
    return buffer

def build_rotation_packet(
    qw: float, qx: float, qy: float, qz: float, pcounter):
    # qw,qx,qy,qz: parts of a quaternion / trackerID: Tracker ID
    buffer = b'\x00\x00\x00\x11'  # packet 17 header
    buffer += struct.pack('>Q', pcounter)  # packet counter
    buffer += struct.pack('B', 0)  # Sensor ID
    buffer += struct.pack('B', 1)  # data type (use is unknown)
    buffer += struct.pack('>ffff', -qx, qz, qy, qw)  # quaternion as x,z,y,w
    buffer += struct.pack('B', 0)  # calibration info (seems to not be used by SlimeVR currently)
    return buffer

def build_accel_packet(ax, ay, az, pcounter):
    buffer = b'\x00\x00\x00\x04'  # packet 4 header
    buffer += struct.pack('>Q', pcounter)  # packet counter
    buffer += struct.pack('>fff', ax, ay, az)  # acceleration as x y z
    buffer += struct.pack('B', 0)  # Sensor ID
    return buffer

# Voltage is 1:1 with what's shown in SlimeVR
# Percentage: 0.0 = 0% / 0.50 = 50% / 1.0 = 100%
def build_battery_packet(voltage, percentage, pcounter):
    buffer = b'\x00\x00\x00\x0C'
    buffer += struct.pack('>Q', pcounter)
    buffer += struct.pack('>ff', voltage, percentage)
    return buffer

def build_error_packet(pcounter):
    buffer = b'\x00\x00\x00\x0E'
    buffer += struct.pack('>Q', pcounter)
    buffer += struct.pack('B', 0)  # Sensor ID
    buffer += struct.pack('B', 1)  # Error code
    return buffer

def correctAccel(aX, aY, aZ):  # Used to correct accel data from the tracker (multiplying the tracker data by 0.12 makes it match the standard m/s^2)
    aX2 = aX * 0.12
    aY2 = aY * 0.12
    aZ2 = aZ * 0.12
    return aX2, aY2, aZ2

def process_packet(data, offset = (0,0,0,0), calibrate = False):
    pw = hexToQuat(data[8:10])
    px = hexToQuat(data[10:12])
    py = hexToQuat(data[12:14])
    pz = hexToQuat(data[14:16])
    ax = hexToFloat(data[24:26])
    az = hexToFloat(data[26:28])
    ay = hexToFloat(data[28:30])
    if calibrate:
        ret_offset = (pw, -px, -py, -pz)
        return ret_offset
    qwc, qxc, qyc, qzc = multiply(pw, px, py, pz, *offset)  # apply quat offset/correction
    axc, ayc, azc = correctAccel(ax, ay, az)  # apply accel offset
    return MocopiPacket(qwc, qxc, qyc, qzc, axc, ayc, azc, int.from_bytes(data[1:8], "little"))
