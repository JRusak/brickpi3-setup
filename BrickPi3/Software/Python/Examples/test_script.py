from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division 

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

from typing import TypeAlias
from collections.abc import Callable


Option: TypeAlias = tuple[str, Callable]

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.


def print_options(options: list[Option]) -> None:
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


def finish_test() -> None:
    BP.reset_all()  # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
    print('\n')


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
        finish_test()


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
        finish_test()


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
            try:
                print(BP.get_sensor(BP.PORT_1))   # print the infrared value
            except brickpi3.SensorError as error:
                print(error)
            
            time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        finish_test()


def motors_test() -> None:
    intro = '''
# Hardware: Connect EV3 or NXT motor(s) to any of the BrickPi3 motor ports. Make sure that the BrickPi3 is running on a 9v power supply.
#           Connect an EV3 or NXT touch sensor to BrickPi3 Port 1.
#
# Results:  When you run this program, the motor(s) speed will ramp up and down while the touch sensor is pressed. The position for each motor will be printed.
'''
    init_test(intro)
    BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.TOUCH) # Configure for a touch sensor. If an EV3 touch sensor is connected, it will be configured for EV3 touch, otherwise it'll configured for NXT touch.

    try:
        print("Press touch sensor on port 1 to run motors")
        value = 0
        while not value:
            try:
                value = BP.get_sensor(BP.PORT_1)
            except brickpi3.SensorError:
                pass
        
        speed = 0
        adder = 1
        while True:
            # BP.get_sensor retrieves a sensor value.
            # BP.PORT_1 specifies that we are looking for the value of sensor port 1.
            # BP.get_sensor returns the sensor value.
            try:
                value = BP.get_sensor(BP.PORT_1)
            except brickpi3.SensorError as error:
                print(error)
                value = 0
            
            if value:                             # if the touch sensor is pressed
                if speed <= -100 or speed >= 100: # if speed reached 100, start ramping down. If speed reached -100, start ramping up.
                    adder = -adder
                speed += adder
            else:                                 # else the touch sensor is not pressed or not configured, so set the speed to 0
                speed = 0
                adder = 1
            
            # Set the motor speed for all four motors
            BP.set_motor_power(BP.PORT_A + BP.PORT_B + BP.PORT_C + BP.PORT_D, speed)
            
            try:
                # Each of the following BP.get_motor_encoder functions returns the encoder value (what we want to display).
                print("Encoder A: %6d  B: %6d  C: %6d  D: %6d" % (BP.get_motor_encoder(BP.PORT_A), BP.get_motor_encoder(BP.PORT_B), BP.get_motor_encoder(BP.PORT_C), BP.get_motor_encoder(BP.PORT_D)))
            except IOError as error:
                print(error)
            
            time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        finish_test()


def read_info() -> None:
    intro = '''
# Results: Print information about the attached BrickPi3.
'''
    print(intro)
    print()
    
    try:
        # Each of the following BP.get functions return a value that we want to display.
        print("Manufacturer    : ", BP.get_manufacturer()    ) # read and display the serial number
        print("Board           : ", BP.get_board()           ) # read and display the serial number
        print("Serial Number   : ", BP.get_id()              ) # read and display the serial number
        print("Hardware version: ", BP.get_version_hardware()) # read and display the hardware version
        print("Firmware version: ", BP.get_version_firmware()) # read and display the firmware version
        print("Battery voltage : ", BP.get_voltage_battery() ) # read and display the current battery voltage
        print("9v voltage      : ", BP.get_voltage_9v()      ) # read and display the current 9v regulator voltage
        print("5v voltage      : ", BP.get_voltage_5v()      ) # read and display the current 5v regulator voltage
        print("3.3v voltage    : ", BP.get_voltage_3v3()     ) # read and display the current 3.3v regulator voltage
        
    except IOError as error:
        print(error)

    except brickpi3.FirmwareVersionError as error:
        print(error)
    
    finish_test()


def voltages_test() -> None:
    intro = '''
# Results: Print the voltages of the BrickPi3.
'''
    init_test(intro)

    try:
        while True:
            print("Battery voltage: %6.3f  9v voltage: %6.3f  5v voltage: %6.3f  3.3v voltage: %6.3f" % (BP.get_voltage_battery(), BP.get_voltage_9v(), BP.get_voltage_5v(), BP.get_voltage_3v3())) # read and display the current voltages
            
            time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        finish_test()


def gyro_sensor_test() -> None:
    intro = '''
# Hardware: Connect an EV3 gyro sensor to BrickPi3 sensor port 1.
# 
# Results:  When you run this program, the gyro's absolute rotation and rate of rotation will be printed.
'''
    init_test(intro)

    BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_GYRO_ABS_DPS)

    try:
        while True:
            try:
                print(BP.get_sensor(BP.PORT_1))   # print the gyro sensor values
            except brickpi3.SensorError as error:
                print(error)
            
            time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        finish_test()


def infrared_remote_test() -> None:
    intro = '''
# Hardware: Connect an EV3 infrared sensor to BrickPi3 sensor port 1.
# 
# Results:  When you run this program, the infrared remote status will be printed.
'''
    init_test(intro)

    BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_INFRARED_REMOTE)

    try:
        while True:
            try:
                print(BP.get_sensor(BP.PORT_1))   # print the infrared values
            except brickpi3.SensorError as error:
                print(error)
            
            time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        finish_test()


def main() -> None:
    options = [
        ("Motors", motors_test),
        ("Touch sensor", touch_sensor_test),
        ("Color sensor", color_sensor_test),
        ("Infrared sensor", infrared_sensor_test),
        ("Infrared remote", infrared_remote_test),
        ("Gyro sensor", gyro_sensor_test),
        ("BrickPi3 info", read_info),
        ("Voltages", voltages_test)
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
