#! /bin/bash

OPENOCD_SCRIPTS=/usr/local/share/openocd/scripts

# check the RPi version
RPI_VERSION=$(python3 -c "import auto_detect_rpi; print (auto_detect_rpi.getRPIGenerationCode())")

echo "Found "$RPI_VERSION

INTERFACE_FILE="none"
if [ "$RPI_VERSION" == "RPI1" ] || [ "$RPI_VERSION" == "RPI0" ]; then
    # use rpi1 interface config file
    INTERFACE_FILE="rpi1.cfg"
elif [ "$RPI_VERSION" == "RPI2" ] || [ "$RPI_VERSION" == "RPI3" ] || [ "$RPI_VERSION" == "RPI3B+" ] || [ "$RPI_VERSION" == "RPI3A+" ] ; then
    # use rpi2 interface config file
    INTERFACE_FILE="rpi2.cfg"
elif [ "$RPI_VERSION" == "RPI4" ]; then
    INTERFACE_FILE="rpi4.cfg"
elif [ "$RPI_VERSION" == "RPI5" ]; then
    INTERFACE_FILE="rpi5.cfg"
fi

if [ "$INTERFACE_FILE" == "none" ]; then
    # unsupported RPI
    echo "Unsupported RPi version '$RPI_VERSION'"
else
    echo "Using interface file '$INTERFACE_FILE' for RPi version '$RPI_VERSION'."

    # Read the path of the BrickPi3 repository
    REPO_PATH=$(readlink -f $(dirname $0) | grep -E -o "^(.*?\\BrickPi3)")

    # Get the absolute path of the latest Firmware update
    FIRMWARE_FILE=$(sudo find "$REPO_PATH"/Firmware/ -maxdepth 1 -name *.bin)

    if [ "$FIRMWARE_FILE" == "" ]; then
        echo "Failed to find firmware file."
    else
        echo "** Updating the BrickPi3 Firmware with '$FIRMWARE_FILE'"

        # flash the firmware
        sudo openocd -f $OPENOCD_SCRIPTS/interface/$INTERFACE_FILE -c "transport select swd; set CHIPNAME at91samd21j18; source [find target/at91samdXX.cfg]; adapter speed 50; adapter srst delay 100; adapter srst pulse_width 100" -c "init; targets; reset halt; program $FIRMWARE_FILE verify; reset" -c "shutdown"
        echo
        echo
        echo 'if you see ** Verified OK ** then all is good. If not, please try again. Sometimes it can take a few tries before it works.'
    fi
fi
