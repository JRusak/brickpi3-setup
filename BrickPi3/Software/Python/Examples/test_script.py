from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division 

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

from typing import TypeAlias
from collections.abc import Callable
from itertools import permutations

Option: TypeAlias = tuple[str, Callable]

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

BP_SENSOR_PORTS = [
    (BP.PORT_1, "1"),
    (BP.PORT_2, "2"),
    (BP.PORT_3, "3"),
    (BP.PORT_4, "4")
]

BP_MOTOR_PORTS = [
    (BP.PORT_A, "A"),
    (BP.PORT_B, "B"),
    (BP.PORT_C, "C"),
    (BP.PORT_D, "D")
]


def get_color_from_color_sensor_value(value) -> str:
    return ["none", "Black", "Blue", "Green", "Yellow", "Red", "White", "Brown"][value]


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


def configure_sensor(port) -> None:
    try:
        BP.get_sensor(port)
    except brickpi3.SensorError:
        print("Configuring...")
        error = True
        while error:
            time.sleep(0.1)
            try:
                BP.get_sensor(port)
                error = False
            except brickpi3.SensorError:
                error = True
    print("Configured.")


def get_value_parser(parser: str) -> Callable:
    return {
        "COLOR": get_color_from_color_sensor_value
    }.get(parser)


def parse_value(value, parser: Callable) -> None:
    return parser(value) if parser else value


def get_multi_mode_values(port, sensor_type: list[str] ,parser: Callable) -> None:
    values = []

    for s_t in sensor_type:
        BP.set_sensor_type(port, s_t)
        time.sleep(0.02)
        values.append(BP.get_sensor(port))

    return [parse_value(v, parser) for v in values]


def test_sensor(intro: str, sensor_type: str | list[str], parser_type: str = None) -> None:
    try:
        print("The test will be held for every sensor port of the BrickPi3.")
        for port, number in enumerate(BP_SENSOR_PORTS):
            print("If you want to quit the test just press Ctrl+C.")
            init_test(intro.format(str(number)))
            parser = get_value_parser(parser_type)
            
            if type(sensor_type) is str:
                BP.set_sensor_type(port, sensor_type)
            else:
                BP.set_sensor_type(port, sensor_type[0])
            
            configure_sensor(port)
            try:
                while True:
                    try:
                        if type(sensor_type) is str:
                            value = BP.get_sensor(port)
                            print(parse_value(value, parser))
                        else:
                            values = get_multi_mode_values(port, sensor_type, parser)
                            print('   '.join(values))
                    except brickpi3.SensorError as error:
                        print(error)
                    
                    time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

            except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
                finish_test()
    except KeyboardInterrupt:
        finish_test()


def touch_sensor_test() -> None:
    intro = '''
# Hardware: Connect an EV3 or NXT touch sensor to BrickPi3 {}.
# 
# Results:  When you run this program, you should see a 0 when the touch sensor is not pressed, and a 1 when the touch sensor is pressed.
'''
    test_sensor(intro, BP.SENSOR_TYPE.TOUCH)


def color_sensor_color_test() -> None:
    intro = '''
# Hardware: Connect an EV3 color sensor to BrickPi3 sensor {}.
# 
# Results:  When you run this program, the color will be printed.
'''
    test_sensor(intro, BP.SENSOR_TYPE.EV3_COLOR_COLOR, parser_type="COLOR")


def color_sensor_raw_test() -> None:
    intro = '''
# Hardware: Connect an EV3 color sensor to BrickPi3 sensor {}.
# 
# Results:  When you run this program, the raw color components will be printed.
'''
    test_sensor(intro, BP.SENSOR_TYPE.EV3_COLOR_COLOR_COMPONENTS)


def color_sensor_multi_mode_test() -> None:
    intro = '''
# Hardware: Connect an EV3 color sensor to BrickPi3 sensor {}.
# 
# Results:  When you run this program it will rapidly switch between modes, taking readings, and then it will print the values.
'''
    sensor_type = [
        BP.SENSOR_TYPE.EV3_COLOR_REFLECTED,
        BP.SENSOR_TYPE.EV3_COLOR_AMBIENT,
        BP.SENSOR_TYPE.EV3_COLOR_COLOR,
        BP.SENSOR_TYPE.EV3_COLOR_COLOR_COMPONENTS,
    ]
    test_sensor(intro, sensor_type)


def gyro_sensor_test() -> None:
    intro = '''
# Hardware: Connect an EV3 gyro sensor to BrickPi3 sensor {}.
# 
# Results:  When you run this program, the gyro's absolute rotation and rate of rotation will be printed.
'''
    test_sensor(intro, BP.SENSOR_TYPE.EV3_GYRO_ABS_DPS)


def infrared_remote_test() -> None:
    intro = '''
# Hardware: Connect an EV3 infrared sensor to BrickPi3 sensor {}.
# 
# Results:  When you run this program, the infrared remote status will be printed.
'''
    test_sensor(intro, BP.SENSOR_TYPE.EV3_INFRARED_REMOTE)


def ultrasonic_sensor_test() -> None:
    intro = '''
# Hardware: Connect an EV3 ultrasonic sensor to BrickPi3 sensor {}.
# 
# Results:  When you run this program, the ultrasonic sensor distance will be printed.
'''
    test_sensor(intro, BP.SENSOR_TYPE.EV3_ULTRASONIC_CM)


def infrared_sensor_test() -> None:
    intro = '''
# Hardware: Connect an EV3 infrared sensor to BrickPi3 sensor {}.
# 
# Results:  When you run this program, the infrared proximity will be printed.
'''
    test_sensor(intro, BP.SENSOR_TYPE.EV3_INFRARED_PROXIMITY)


def motors_test() -> None:
    intro = '''
# Hardware: Connect EV3 or NXT motor(s) to any of the BrickPi3 motor ports. Make sure that the BrickPi3 is running on a 9v power supply.
#           Connect an EV3 or NXT touch sensor to BrickPi3 Port 1.
#
# Results:  When you run this program, the motor(s) speed will ramp up and down while the touch sensor is pressed. The position for each motor will be printed.
'''
    init_test(intro)
    BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.TOUCH) # Configure for a touch sensor. If an EV3 touch sensor is connected, it will be configured for EV3 touch, otherwise it'll configured for NXT touch.
    configure_sensor(BP.PORT_1)
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


def motor_encoder_test() -> None:
    intro = '''
# Hardware: Connect EV3 or NXT motor(s) to any of the BrickPi3 motor ports.
# 
# Results:  When you run this program, you should see the encoder value for each motor. By manually rotating a motor, the count should change by 1 for every degree of rotation.
'''
    init_test(intro)

    try:
        while True:
            try:
                print("Encoder A: %6d  B: %6d  C: %6d  D: %6d" % (BP.get_motor_encoder(BP.PORT_A), BP.get_motor_encoder(BP.PORT_B), BP.get_motor_encoder(BP.PORT_C), BP.get_motor_encoder(BP.PORT_D)))
            except IOError as error:
                print(error)
            
            time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        finish_test()


def motor_dps_test() -> None:
    intro = '''
# Hardware: Connect EV3 or NXT motors to the BrickPi3 motor ports. Make sure that the BrickPi3 is running on a 9v power supply.
#
# Results:  When you run this program, other motors' speed will be controlled by the position of motor {}. Manually rotate motor {}, and motors' speed will change.
'''
    try:
        print("The test will be held for every motor port of the BrickPi3.")
        for main_port, number in enumerate(BP_MOTOR_PORTS):
            print("If you want to quit the test just press Ctrl+C.")
            init_test(intro.format(number))
            try:
                other_ports = [p for p in BP_MOTOR_PORTS if p[0] != main_port]
                try:
                    for port, _ in BP_MOTOR_PORTS:
                        BP.offset_motor_encoder(port, BP.get_motor_encoder(port))
                except IOError as error:
                    print(error)
                
                BP.set_motor_power(main_port, BP.MOTOR_FLOAT)

                while True:
                    # The following BP.get_motor_encoder function returns the encoder value
                    try:
                        target = BP.get_motor_encoder(main_port)
                    except IOError as error:
                        print(error)
                    
                    BP.set_motor_dps(sum(p[0] for p in other_ports), target)
                    
                    status = [f"Target Degrees Per Second: {target}"]
                    status.append("  Motor status ")
                    for p, n in other_ports:
                        status.append(f" {n}: ", BP.get_motor_status(p))
                    print(''.join(status))

                    time.sleep(0.02)

            except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
                finish_test()
    except KeyboardInterrupt:
        finish_test()


def motor_position_test() -> None:
    intro = '''
# Hardware: Connect EV3 or NXT motors to the BrickPi3 motor ports. Make sure that the BrickPi3 is running on a 9v power supply.
#
# Results:  When you run this program, other motors will run to match the position of motor {}. Manually rotate motor {}, and motors will follow.
'''
    try:
        print("The test will be held for every motor port of the BrickPi3.")
        for main_port, number in enumerate(BP_MOTOR_PORTS):
            print("If you want to quit the test just press Ctrl+C.")
            init_test(intro.format(number))
            try:
                other_ports = [p for p in BP_MOTOR_PORTS if p[0] != main_port]
                other_ports_sum = sum(p[0] for p in other_ports)
                try:
                    for port, _ in BP_MOTOR_PORTS:
                        BP.offset_motor_encoder(port, BP.get_motor_encoder(port))
                except IOError as error:
                    print(error)
                
                BP.set_motor_power(main_port, BP.MOTOR_FLOAT)
                BP.set_motor_limits(other_ports_sum, 50, 200)

                while True:
                    try:
                        target = BP.get_motor_encoder(main_port)
                    except IOError as error:
                        print(error)
                    
                    BP.set_motor_position(other_ports_sum, target)
                    
                    try:
                        status = [f"Target: {target}"]
                        status.append("  Motor position ")
                        for p, n in other_ports:
                            status.append(f" {n}: ", BP.get_motor_encoder(p))
                        print(''.join(status))
                    except IOError as error:
                        print(error)

                    time.sleep(0.02)

            except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
                finish_test()
    except KeyboardInterrupt:
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
    finally:
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


def led_test() -> None:
    intro = '''
# Results:  When you run this program, the BrickPi3 LED will fade up and down.
'''
    init_test(intro)

    try:
        while True:
            for i in range(101):    # count from 0-100
                BP.set_led(i)       # set the LED brightness (0 to 100)
                time.sleep(0.01)    # delay for 0.1 seconds (100ms) to reduce the Raspberry Pi CPU load and give time to see the LED pulsing.
            
            for i in range(101):    # count from 0-100
                BP.set_led(100 - i) # set the LED brightness (100 to 0)
                time.sleep(0.01)     # delay for 0.1 seconds (100ms) to reduce the Raspberry Pi CPU load and give time to see the LED pulsing.

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        finish_test()


def main() -> None:
    options = [
        ("Motors", motors_test),
        ("Motor encoder", motor_encoder_test),
        ("Motor DPS", motor_dps_test),
        ("Motor position", motor_position_test),
        ("Touch sensor", touch_sensor_test),
        ("Color sensor", color_sensor_color_test),
        ("Color sensor (raw)", color_sensor_raw_test),
        ("Color sensor (multi mode)", color_sensor_multi_mode_test),
        ("Gyro sensor", gyro_sensor_test),
        ("Infrared sensor", infrared_sensor_test),
        ("Infrared remote", infrared_remote_test),
        ("Ultrasonic sensor", ultrasonic_sensor_test),
        ("LED", led_test),
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
