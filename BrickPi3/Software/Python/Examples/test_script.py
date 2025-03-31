from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division 

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers


BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.


def print_options() -> None:
    print("1. Motors")
    print("2. Touch sensor")
    print("3. Color sensor")
    print("To exit type 0")


def get_option() -> int:
    option = ""

    while not option.isnumeric():
        option = input("Choose the number of what you want to test out: ")

    return int(option)


def init_test(intro: str) -> None:
    print(intro)
    input("Press any key to start the test")


def touch_sensor_test():
    intro = '''# This code is an example for reading a touch sensor connected to PORT_1 of the BrickPi3
# 
# Hardware: Connect an EV3 or NXT touch sensor to BrickPi3 Port 1.
# 
# Results:  When you run this program, you should see a 0 when the touch sensor is not pressed, and a 1 when the touch sensor is pressed.
#
# To stop press Ctrl+C.
'''
    init_test(intro)
    BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.TOUCH)
    try:
        while True:
            try:
                value = BP.get_sensor(BP.PORT_1)
                print(value)
            except brickpi3.SensorError as error:
                print(error)
            
            time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.


def main() -> None:
    try:
        print_options()
        while True:
            match get_option():
                case 0:
                    BP.reset_all()
                    exit(0)
                case 1:
                    pass
                case 2:
                    touch_sensor_test()
                case _:
                    pass
            
            BP.reset_all()

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.


if __name__ == "__main__":
    main()
