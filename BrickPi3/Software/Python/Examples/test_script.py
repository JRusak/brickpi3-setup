from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division 

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
                case _:
                    pass
            
            BP.reset_all()

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.


if __name__ == "__main__":
    main()
