#!/bin/bash
# Changelog (num = number at end of noautoupd):
# 1. raspi folder was moved, launcher.sh can't update itself

FILE=/home/moslime/noautoupd1
if test -f "$FILE"; then
    echo "$FILE exists. Don't run autoupdate.sh"
else
    cp /home/moslime/moslime/scripts/raspi/* /home/moslime
    touch /home/moslime/noautoupd1
fi
