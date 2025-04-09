#!/bin/bash

PIHOME=/home/pi
BRICKPI3_DIR=$PIHOME/BrickPi3
FLASH_FIRMWARE_SCRIPT="$BRICKPI3_DIR/Firmware/"\
"brickpi3samd_flash_firmware.sh"
FW_VERSION_SCRIPT="$BRICKPI3_DIR/Software/Python/Examples/"\
"Read_Info.py"

main() {
    chmod +x $FLASH_FIRMWARE_SCRIPT
    bash $FLASH_FIRMWARE_SCRIPT

    python3 $FW_VERSION_SCRIPT

    exit 0
}

main