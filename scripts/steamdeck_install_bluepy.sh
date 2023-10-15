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
    pacman --noconfirm -S python-bluepy
    echo "[Step 5 <] Dependencies installed."
    echo "[Step 6 >] Cleaning up… Reinstating Pacman signature verification."
    sed -i "s/SigLevel    = Never/SigLevel = Required DatabaseOptional/g" /etc/pacman.conf
    echo "[Step 6 <] Reinstated Pacman signature verification."
    echo "[Step 7 >] Cleaning up… Reinstating BTRFS protections."
    btrfs property set -ts / ro true
    echo "[Step 7 <] Reinstated BTRFS protections."
    echo "<<<=== [DONE! EVERYTHING IS READY.] ===>>>"
EOF
zenity --info --text="Install complete."
