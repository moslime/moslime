#!/bin/bash
xterm -e "java -jar /home/deck/slimevr/slimevr.jar run" &
sleep 1
xdg-open https://slimevr-gui.bscotch.ca/ &
sleep 5
xterm -e "python ../moslime.py" &
