![moslime](resources/moslime_logo.png)
Bring your Mocopi trackers into SteamVR!

Built on the battle-tested algorithms and runtime of SlimeVR, this project aims to improve and extend the Mocopi on PC experience. No first-party app required.

Official Support Discord - https://discord.gg/vCQ2xP8KZb

## Disclaimers
This third-party software is deemed alpha quality, provided as is, and without warranty.
Mocopi is a trademark owned by the Sony Corporation. MoSlime is not endorsed by the Sony Corporation nor SlimeVR, nor are they affiliated with the MoSlime developers.
This software does not modify the firmware of your Mocopi trackers and should not break them. However, only use this software if you agree to assume the risks therein.

## Note about Windows support
**We have found a workaround and Windows support will be coming soon.**\
It involves bypassing the Windows bluetooth stack entirely and switching from bluepy to [Bumble](https://github.com/google/bumble/)

Windows is currently not supported because of an issue with how it handles pairing and how the trackers present themselves.
<details>
  <summary>TL;DR: Bluetooth devices are supposed to have a unique key that identifies a device in the event that it's MAC address changes. All Mocopi trackers have the same key and Windows does not like that.</summary>
 
  - As part of the pairing process, Bluetooth LE devices exchange a few keys that help them identify each other and secure their connection. One of these keys is the Identity Resolving Key, which is a 128 bit key that helps devices identify each other in the event that one or the other changes their MAC address (MAC Randomization is a privacy feature of BLE). This key is supposed to be unique per device but with Mocopi, it's hardcoded to be all zeros on all trackers. Platforms such as Linux, Android, iOS, etc. don't really care about the key being the same but Windows enforces use of that key and complains when multiple devices have the same key. Here's the error that Windows gives:

   `The device (3c:38:f4:xx:xx:xx) is trying to distribute an Identity Resolving Key that is already used by a paired device. The pairing was rejected, if the intent was to pair with this device, you may need to first delete the existing pairing information.`
</details>

## Current and Planned Features
- [x] Auto-connect to trackers (manual pairing still needed) 
- [x] Send IMU rotation data to SlimeVR
- [x] Auto discovery and paring of trackers (Partially complete)
- [x] Auto reconnect when trackers disconnect
- [x] SlimeVR Server auto discovery
- [x] Send IMU acceleration data to SlimeVR (Doesn't help with drift currently, only allows for gesture controls)
- [x] Battery and Firmware verion reporting
- [ ] UI to allow easy configuration

## Requirements and Setup
Setup and usage instructions can be found in the [Wiki](https://github.com/moslime/moslime/wiki)

## Tracker Mounting
With MoSlime, the trackers can be placed and assigned to any body part you want. Assuming you're using MoSlime alongside a VR headset, here are the recommended tracker positions:
 - Head   - Place on your chest. For some people, the head strap should be big enough to strech over your chest.
 - Hip    - Should still be used for hip
 - Wrists - Use these for your upper legs/knees. You may need to make some custom straps for these (you can use the original mount, just take the 2 screws off the back)
 - Ankles - Should still be used for ankles

   - If you're lucky, you might be able to strech the wrist straps around your ankles and your ankle straps around your knees

## Tested Bluetooth adapters
 - [Intel 8265NGW - Combo WiFi/BT card](https://www.intel.com/content/www/us/en/products/sku/94150/intel-dual-band-wirelessac-8265/specifications.html)
 - [tp-link UB500](https://www.tp-link.com/us/home-networking/usb-adapter/ub500/)
 - Raspberry Pi 3B/3B+/4B (3B and 3B+ struggle a bit, it may be a good idea to lower the TPS in moslime.json)

## Known Problematic Adapters
- Intel 18260NGW - unusable when more than one tracker is connected
- SENA UD100 - has issues connecting to more than 4 trackers

## Contributors
 - [@lmore377](https://github.com/lmore377) - Original Bluetooth reverse-engineering work, Python code, quaternion correction math
 - [@PlatinumVsReality](https://github.com/PlatinumVsReality) - Slime packet generation code, Rust code, wip web interface, graphics, moral support
 - [@itstait](https://github.com/itstait) - Helped optimize multithreading (trust me it used to be much worse)

Special thanks to the SlimeVR team for making their amazing software in the first place and for answering our endless questions!

## Resources
 - https://github.com/lmore377/mocopi-reverse-engineering - Initial reverse engineering work
 - https://github.com/SlimeVR/SlimeVR-Tracker-ESP - Used to figure out networking / packet structure
 - https://github.com/carl-anders/slimevr-wrangler - Used to figure out networking / packet structure
 - https://www.creativefabrica.com/product/coffeecake/ - Font used for the logo. Special thanks to Khurasan!
 - https://www.dafont.com/dripping.font - Additional font used, Dripping by Woodcutter
