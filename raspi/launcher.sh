#! /bin/bash

clear
trap main_dialog INT

function update {
	{
        clear
	sudo apt update
	sudo apt upgrade -y
	git -C /home/moslime/moslime/ pull
        cp /home/moslime/moslime/raspi/* /home/moslime/
	/home/moslime/autoupdate.sh
	whiptail --msgbox "When you press enter, the raspberry pi will reboot. If you're using the web client, wait until it's back on then just press connect on the screen that follows. Otherwise, just ssh back in however you did it in the first place." 20 78
	sudo shutdown -r now
	}
}

whiptail --msgbox "Welcome to MoSlime! If this is your first time using this, please reference https://github.com/lmore377/moslime/raspi.md for instructions.\n" 20 78

function main_dialog {
	{
	CHOICE=$(
	whiptail --title "MoSlime Launcher" --menu "Select an option" 16 100 9 \
		"1)" "Start MoSlime"   \
		"2)" "Run bluetoothctl (Manual bluetooth pairing)"  \
		"3)" "Edit Configuration" \
		"4)" "Remove all BT devices" \
		"5)" "Attempt auto-pair (Experimental)"\
		"6)" "Update" \
		"A)" "Exit to shell"\
		"B)" "Shutdown"\
		"C)" "Reboot"  3>&2 2>&1 1>&3
	)
	case $CHOICE in
		"1)")
			whiptail --msgbox "When you press enter, you'll have 10 seconds to turn on all your trackers.\nAfter turning them on, make sure you lay them on a flat surface and do not touch them until MoSlime say's it's safe." 20 78
			cp /home/moslime/moslime/moslime.json /home/moslime
			python3 /home/moslime/moslime/moslime.py
                        sleep 5
			clear
		;;
		"2)")
	        	whiptail --msgbox "Type 'exit' then press enter in the console when you're done" 20 78
                	bluetoothctl
			clear
		;;

		"3)")
			whiptail --msgbox "Use the arrow keys to move the cursor around. When you've made your edits, press Ctrl-X, Y, then enter." 20 78
			nano /home/moslime/moslime/moslime.json
			clear
		;;

		"4)")
			for device in $(bluetoothctl devices  | grep -o "[[:xdigit:]:]\{8,17\}"); do
				echo "removing bluetooth device: $device | $(bluetoothctl remove $device)"
			done
			clear
		;;

		"5)")
			whiptail --msgbox "Auto pairing is still experimental and somewhat likely to fail. If you want to try it anyways, follow these directions:\n1. Turn off all your trackers\n2. Turn on all your trackers then immediately press enter. The screen should switch to a console and show all the trackers being paired.\n\nIf you see any errors in the console, run 'Remove all BT devices' in the main menu then try pairing again.\nIf you see a 'Device Disconnected' error from bluepy, just quickly run autopair again." 20 78
			sudo python3 /home/moslime/pair-trackers.py
			clear
		;;

		"6)")
			update
			clear
		;;

		"A)")
                	result="Run /home/moslime/launcher.sh to open this menu again."
                	whiptail --msgbox "$result" 20 78
	                exit
		;;
		"B)")
			sudo shutdown -h now
		;;

		"C)")
			sudo shutdown -r now
		;;
	esac
	}
}

while [ 1 ]
do
main_dialog
done
exit
