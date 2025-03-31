from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division 

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

from typing import TypeAlias
from collections.abc import Callable


Option: TypeAlias = tuple[str, Callable]

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.


def print_options(options: list[Option]) -> None:
    print()
    print("Test options:")

    for i, op in enumerate(options):
        print(f'{i}. {op[0]}')

    print("Press Ctrl+C to exit the program.")


def get_option_number(options: list[Option]) -> int:
    option = ""

    while not option.isnumeric() or int(option) not in range(len(options)):
        option = input("Choose the number of option you want to test: ")

    return int(option)


def init_test(intro: str) -> None:
    print(intro)
    print("# To stop test press Ctrl+C.")
    print()
    input("Press any key to start the test")
    print()


def touch_sensor_test() -> None:
    intro = '''
# Hardware: Connect an EV3 or NXT touch sensor to BrickPi3 Port 1.
# 
# Results:  When you run this program, you should see a 0 when the touch sensor is not pressed, and a 1 when the touch sensor is pressed.
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


def color_sensor_test() -> None:
    intro = '''
# Hardware: Connect an EV3 color sensor to BrickPi3 sensor port 1.
# 
# Results:  When you run this program, the color will be printed.
'''
    init_test(intro)
    BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_COLOR_COLOR)

    color = ["none", "Black", "Blue", "Green", "Yellow", "Red", "White", "Brown"]

    try:
        while True:
            try:
                value = BP.get_sensor(BP.PORT_1)
                print(color[value])                # print the color
            except brickpi3.SensorError as error:
                print(error)
            
            time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.


def infrared_sensor_test() -> None:
    intro = '''
# Hardware: Connect an EV3 infrared sensor to BrickPi3 sensor port 1.
# 
# Results:  When you run this program, the infrared proximity will be printed.
'''
    init_test(intro)
    BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_INFRARED_PROXIMITY)

    try:
        while True:
            # BP.get_sensor retrieves a sensor value.
            # BP.PORT_1 specifies that we are looking for the value of sensor port 1.
            # BP.get_sensor returns the sensor value (what we want to display).
            try:
                print(BP.get_sensor(BP.PORT_1))   # print the infrared value
            except brickpi3.SensorError as error:
                print(error)
            
            time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.


def main() -> None:
    options = [
        # ("Motors", )
        ("Touch sensor", touch_sensor_test),
        ("Color sensor", color_sensor_test),
        ("Infrared sensor", infrared_sensor_test)
    ]

    try:
        while True:
            print_options(options)
            num = get_option_number(options)
            options[num][1]()
            
            BP.reset_all()

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.


if __name__ == "__main__":
    main()
