#!/bin/bash
pkexec /bin/bash <<EOF
    echo "[Step 1 >] Disabling BTRFS protections."
    btrfs property set -ts / ro false
    echo "[Step 1 <] Disabled BTRFS protections."
    echo "[Step 2 >] Populating Pacman keyring."
    pacman-key --init
    pacman-key --populate archlinux
    echo "[Step 2 <] Populating Pacman keyring."
    echo "[Step 3 >] Updating Pacman packages."
    pacman --noconfirm -Syu
    echo "[Step 3 <] Pacman updated."
    echo "[Step 4 >] Disabling Pacman signature verification. (this is a temp fix)"
    sed -i "s/SigLevel    = Required DatabaseOptional/SigLevel = Never/g" /etc/pacman.conf
    echo "[Step 4 <] Pacman signature verification disabled."
    echo "[Step 5 >] Installing dependencies."
    pacman --noconfirm -S jdk17-openjdk python-bluepy
    echo "[Step 5 <] Dependencies installed."
    echo "[Step 6 >] Installing latest SlimeVR."
    mkdir /home/deck/slimevr
    wget https://github.com/SlimeVR/SlimeVR-Server/releases/latest/download/slimevr.jar -O /home/deck/slimevr/slimevr.jar
    chown -R deck:deck /home/deck/slimevr
    chmod +x /home/deck/slimevr/slimevr.jar
    echo "[Step 6 <] SlimeVR installed."
    echo "[Step 7 >] Cleaning up… Reinstating Pacman signature verification."
    sed -i "s/SigLevel    = Never/SigLevel = Required DatabaseOptional/g" /etc/pacman.conf
    echo "[Step 7 <] Reinstated Pacman signature verification."
    echo "[Step 8 >] Cleaning up… Reinstating BTRFS protections."
    btrfs property set -ts / ro true
    echo "[Step 7 <] Reinstated BTRFS protections."
    echo "<<<=== [DONE! EVERYTHING IS READY.] ===>>>"
EOF
zenity --info --text="Install complete. Please double click steamdeck_run_plus_slime in the scripts folder when you are ready to open MoSlime and Slime on Deck."
