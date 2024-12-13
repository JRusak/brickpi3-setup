#!/bin/bash

PIHOME=/home/pi
LIB_PATH=$PIHOME/lib
SCRIPT=$LIB_PATH/script_tools

source $SCRIPT/functions_library.sh


# Check if WiringPi Installed and has the latest version.  If it does, skip the step.
# Gets the version of wiringPi installed
version=`gpio -v`    

# Parses the version to get the number
set -- $version         

# Gets the third word parsed out of the first line of gpio -v returned.
# Should be 3.10
WIRINGVERSIONDEC=$3     

# Store to temp file
echo $WIRINGVERSIONDEC >> tmpversion    

# Remove decimals
VERSION=$(sed 's/\.//g' tmpversion)     

# Remove the temp file
delete_file tmpversion                           

feedback "wiringPi VERSION is $VERSION"
if [ -n "$VERSION" ] && [ $VERSION -eq '310' ]; then

    feedback "FOUND WiringPi Version 3.10 No installation needed."
else
    feedback "Did NOT find WiringPi Version 3.10"
    # Check if the directory exists.
    create_folder "$LIB_PATH"

    # Change directories
    cd $LIB_PATH
 
    # Install wiringPi
    cd wiringPi
    sudo chmod +x ./build
    sudo ./build
    feedback "wiringPi Installed"
fi
# End check if WiringPi installed
