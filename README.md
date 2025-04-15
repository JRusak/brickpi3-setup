# BrickPi3 software installation guide

Raspberry Pi OS (64-bit) (tested and recommended)

```sh
sudo raspi-config
```

Interface Options → SPI → Enable

 ```sh
sudo reboot
```

 ```sh
curl -kL https://raw.githubusercontent.com/JRusak/brickpi3-setup/refs/heads/main/system_setup.sh | sudo bash
```

```sh
su - pi
```

password for the "pi" user is also just "pi"

If you are using new BrickPi3 you also need to flash firmware onto the board.  
After switching to user "pi" run below command:

```sh
./flash_brickpi3_firmware.sh
```
