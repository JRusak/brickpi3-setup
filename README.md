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
curl -kL https://raw.githubusercontent.com/JRusak/brickpi-setup/refs/heads/main/system_setup.sh | sudo bash
```