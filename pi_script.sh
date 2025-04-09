#!/bin/bash

PIHOME=/home/pi
BRICKPI3_DIR=$PIHOME/BrickPi3
UPDATE_BRICKPI_SCRIPT=$BRICKPI3_DIR/Install/update_brickpi3.sh
FLASH_FIRMWARE_SCRIPT=$PIHOME/flash_brickpi3_firmware.sh

BRICKPI_REPO="https://github.com/JRusak/"\
"brickpi3-setup.git"

install_git() {
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
    # Temporary directory to clone the repository
    TMP_DIR=$(mktemp -d)
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

    # Move all files and folders from the cloned
    # repository to the destination directory
    echo
    echo "Moving contents to $DEST_DIR..."
    echo
    for item in "$TMP_DIR"/*; do
        # Check if $item exists (in case TMP_DIR
        # is empty or contains no files)
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
    bash $UPDATE_BRICKPI_SCRIPT --user-local \
        --bypass-gui-installation

    chmod +x $FLASH_FIRMWARE_SCRIPT

    exit 0
}

main
