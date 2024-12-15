#! /bin/bash

cd lib/openocd

# unzip the compiled OpenOCD
sudo unzip openocd_compiled.zip

# Put the configuration files into /usr/local/share
sudo cp -rn openocd_compiled/files/openocd /usr/local/share

# Put the openocd binary into /usr/bin
sudo cp -rn openocd_compiled/openocd /usr/bin

# Make the openocd binary executable
sudo chmod +x /usr/bin/openocd

# Remove the unzipped files
sudo rm -rf openocd_compiled

cd
