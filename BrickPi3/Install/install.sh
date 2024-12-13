#! /bin/bash

PIHOME=/home/pi
SCRIPT=$PIHOME/lib/script_tools

source $SCRIPT/functions_library.sh

check_root_user() {
    if [[ $EUID -ne 0 ]]; then
        feedback "FAIL!  This script must be run as such: sudo ./install.sh"
        exit 1
    fi
}

install_wiringpi() {
    sudo bash $SCRIPT/update_wiringpi.sh
}

enable_spi() {
    feedback "Removing blacklist from /etc/modprobe.d/raspi-blacklist.conf"

    if grep -q "#blacklist spi-bcm2708" /etc/modprobe.d/raspi-blacklist.conf; then
        echo "SPI already removed from blacklist"
    else
        sudo sed -i -e 's/blacklist spi-bcm2708/#blacklist spi-bcm2708/g' /etc/modprobe.d/raspi-blacklist.conf
        echo "SPI removed from blacklist"
    fi

    #Adding in /etc/modules
    feedback "Adding SPI-dev in /etc/modules"

    if grep -q "spi-dev" /etc/modules; then
        echo "spi-dev already there"
    else
        echo spi-dev >> /etc/modules
        echo "spi-dev added"
    fi
    feedback "Making SPI changes in /boot/config.txt"

    if grep -q "#dtparam=spi=on" /boot/config.txt; then
        sudo sed -i 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt
        echo "SPI enabled"
    elif grep -q "dtparam=spi=on" /boot/config.txt; then
        echo "SPI already enabled"
    else
        sudo sh -c "echo 'dtparam=spi=on' >> /boot/config.txt"
        echo "SPI enabled"
    fi

}

check_root_user
install_wiringpi
enable_spi
