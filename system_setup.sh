#!/bin/sh

pi_script=https://raw.githubusercontent.com/JRusak/brickpi3-setup/refs/heads/main/pi_script.sh
user=pi
password=pi

update_time() {
    echo "Updating date and time"
    sudo date -s "$(wget --method=HEAD -qSO- --max-redirect=0 google.com 2>&1 | sed -n 's/^ *Date: *//p')"
    echo
}

update_system() {
    echo "Updating system"
    sudo apt-get update
    echo

    echo "Upgrading system"
    sudo apt-get -y upgrade
    echo
}

create_user_with_sudo() {
    local username=$1
    local password=$2

    # Check if username is provided
    if [ -z "$username" ]; then
        echo "Please provide a username."
        return 1
    fi

    # Check if user already exists
    if id "$username" >/dev/null 2>&1; then
        echo "User '$username' already exists."
        return 1
    fi

    # Add new user
    sudo useradd -m -s /bin/bash "$username"

    # Set password for the user
    echo "$username:$password" | sudo chpasswd

    # Add user to groups
    sudo usermod -aG \
        sudo,adm,dialout,cdrom,audio,video,plugdev,games,users,input,render,netdev,spi,i2c,gpio,lpadmin \
        "$username"

    # Add the NOPASSWD line to the sudoers file
    sudo echo "$username ALL=(ALL) NOPASSWD: ALL" > "/etc/sudoers.d/$username"
    sudo chmod 440 "/etc/sudoers.d/$username"

    echo "User '$username' created with sudo privileges."
} 

run_script_as_user() {
    local username=$1
    local script_path=$2

    # Check if both username and script path are provided
    if [ -z "$username" ] || [ -z "$script_path" ]; then
        echo "Please provide both a username and the path to the script."
        return 1
    fi

    # Switch user and run the script with sudo privileges
    sudo -u "$username" sh -c "$(wget -qO- $script_path)"
}

login_as_user() {
    local username=$1

    su - $username
}

main() {
    update_time
    update_system

    create_user_with_sudo $user $password
    
    run_script_as_user $user $pi_script

    login_as_user $user
}

main
