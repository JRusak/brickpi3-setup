#!/bin/sh

PIHOME=/home/pi
BRICKPI3_DIR=$PIHOME/BrickPi3
UPDATE_BRICKPI_SCRIPT=$BRICKPI3_DIR/Install/update_brickpi3.sh
FLASH_FIRMWARE_SCRIPT=$BRICKPI3_DIR/Firmware/brickpi3samd_flash_firmware.sh

BRICKPI_REPO=git@github.com:JRusak/brickpi3-setup.git

FW_VERSION_SCRIPT=$BRICKPI3_DIR/Software/Python/Examples/Read_Info.py

install_git() {
    # Check if Git is already installed
    if command -v git &> /dev/null; then
        echo "Git is already installed."
        git --version
        return 0
    fi

    echo
    echo "Installing Git..."
    echo
    sudo apt install -y git

    # Confirm installation
    if command -v git &> /dev/null; then
        echo "Git installed successfully."
        git --version
    else
        echo "Git installation failed."
        return 1
    fi
}

get_brickpi_repo() {
    REPO_URL=$1
    TMP_DIR=$(mktemp -d)     # Temporary directory to clone the repository
    DEST_DIR="$PIHOME"

    # Clone the repository into the temporary directory
    echo
    echo "Cloning the repository..."
    echo
    git clone "$REPO_URL" "$TMP_DIR"

    # Check if the clone was successful
    if [ $? -ne 0 ]; then
        echo "Failed to clone repository."
        rm -rf "$TMP_DIR"
        exit 1
    fi

    # Move all files and folders from the cloned repository to the destination directory
    echo
    echo "Moving contents to $DEST_DIR..."
    echo
    for item in "$TMP_DIR"/*; do
        # Check if $item exists (in case TMP_DIR is empty or contains no files)
        if [ -e "$item" ]; then
            mv "$item" "$DEST_DIR"
        fi
    done

    # Clean up temporary directory
    rm -rf "$TMP_DIR"

    echo "Done! The contents have been moved to $DEST_DIR."
}

main() {
    install_git
    get_brickpi_repo $BRICKPI_REPO

    chmod +x $UPDATE_BRICKPI_SCRIPT

    bash $UPDATE_BRICKPI_SCRIPT --user-local --bypass-gui-installation
    
    chmod +x $FLASH_FIRMWARE_SCRIPT
    bash $FLASH_FIRMWARE_SCRIPT

    python3 $FW_VERSION_SCRIPT

    exit 0
}

main
