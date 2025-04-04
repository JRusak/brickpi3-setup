from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division 

from utils import *
from brickpi3 import FirmwareVersionError
from functools import wraps


BP = BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.


def run_for_specific_port(port_type: str):
    def decorator(fun: Callable):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            ports = get_ports(port_type)
            try:
                while True:
                    print()
                    print_available_ports(ports)
                    print("If you want to quit the test just press Ctrl+C.")
                    decision = get_port_decision(ports)
                    if (decision == "all"):
                        print("The test will be held for every {} port of the BrickPi3.".format(port_type))
                        for port_number, port_name in ports:
                            kwargs["port_number"] = port_number
                            kwargs["port_name"] = port_name
                            fun(*args, **kwargs)
                        return
                    else:
                        for p in ports:
                            if p[1] == decision:
                                kwargs["port_number"] = p[0]
                                kwargs["port_name"] = p[1]
                                fun(*args, **kwargs)
                                break
            except KeyboardInterrupt:
                finish_test(BP)
        return wrapper
    return decorator


@run_for_specific_port("sensor")
def test_sensor(
    intro: str,
    sensor_type: int | list[int],
    port_number: int = 1,
    port_name: str = "1",
    parser_type: str = None,
    ) -> None:
        init_test(intro.format(port_name))
        parser = get_value_parser(parser_type)
        
        if type(sensor_type) is int:
            BP.set_sensor_type(port_number, sensor_type)
        else:
            BP.set_sensor_type(port_number, sensor_type[0])
        
        configure_sensor(BP, port_number)
        try:
            while True:
                try:
                    if type(sensor_type) is int:
                        value = BP.get_sensor(port_number)
                        print(parse_value(value, parser))
                    else:
                        values = get_multi_mode_values(BP, port_number, sensor_type, parser)
                        print('   '.join(str(v) for v in values))
                except SensorError as error:
                    print(error)
                
                time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

        except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
            finish_test(BP)


def touch_sensor_test() -> None:
    intro = '''
# Hardware: Connect an EV3 or NXT touch sensor to BrickPi3 port {}.
# 
# Results:  When you run this program, you should see a 0 when the touch sensor is not pressed, and a 1 when the touch sensor is pressed.
'''
    test_sensor(intro, BP.SENSOR_TYPE.TOUCH)


def color_sensor_color_test() -> None:
    intro = '''
# Hardware: Connect an EV3 color sensor to BrickPi3 sensor port {}.
# 
# Results:  When you run this program, the color will be printed.
'''
    test_sensor(intro, BP.SENSOR_TYPE.EV3_COLOR_COLOR, parser_type="COLOR")


def color_sensor_raw_test() -> None:
    intro = '''
# Hardware: Connect an EV3 color sensor to BrickPi3 sensor port {}.
# 
# Results:  When you run this program, the raw color components will be printed.
'''
    test_sensor(intro, BP.SENSOR_TYPE.EV3_COLOR_COLOR_COMPONENTS)


def color_sensor_multi_mode_test() -> None:
    intro = '''
# Hardware: Connect an EV3 color sensor to BrickPi3 sensor port {}.
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
# Hardware: Connect an EV3 gyro sensor to BrickPi3 sensor port {}.
# 
# Results:  When you run this program, the gyro's absolute rotation and rate of rotation will be printed.
'''
    test_sensor(intro, BP.SENSOR_TYPE.EV3_GYRO_ABS_DPS)


def infrared_remote_test() -> None:
    intro = '''
# Hardware: Connect an EV3 infrared sensor to BrickPi3 sensor port {}.
# 
# Results:  When you run this program, the infrared remote status will be printed.
'''
    test_sensor(intro, BP.SENSOR_TYPE.EV3_INFRARED_REMOTE)


def ultrasonic_sensor_test() -> None:
    intro = '''
# Hardware: Connect an EV3 ultrasonic sensor to BrickPi3 sensor port {}.
# 
# Results:  When you run this program, the ultrasonic sensor distance will be printed.
'''
    test_sensor(intro, BP.SENSOR_TYPE.EV3_ULTRASONIC_CM)


def infrared_sensor_test() -> None:
    intro = '''
# Hardware: Connect an EV3 infrared sensor to BrickPi3 sensor port {}.
# 
# Results:  When you run this program, the infrared proximity will be printed.
'''
    test_sensor(intro, BP.SENSOR_TYPE.EV3_INFRARED_PROXIMITY)


def motors_touch_sensor_test() -> None:
    intro = '''
# Hardware: Connect EV3 or NXT motor(s) to any of the BrickPi3 motor ports. Make sure that the BrickPi3 is running on a 9v power supply.
#           Connect an EV3 or NXT touch sensor to BrickPi3 Port 1.
#
# Results:  When you run this program, the motor(s) speed will ramp up and down while the touch sensor is pressed. The position for each motor will be printed.
'''
    init_test(intro)
    BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.TOUCH) # Configure for a touch sensor. If an EV3 touch sensor is connected, it will be configured for EV3 touch, otherwise it'll configured for NXT touch.
    configure_sensor(BP, BP.PORT_1)
    try:
        print("Press touch sensor on port 1 to run motors")
        value = 0
        while not value:
            try:
                value = BP.get_sensor(BP.PORT_1)
            except SensorError:
                pass
        
        speed = 0
        adder = 1
        while True:
            try:
                value = BP.get_sensor(BP.PORT_1)
            except SensorError as error:
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
            
            status = get_status_msg(
                "Encoder: ",
                BP_MOTOR_PORTS,
                BP.get_motor_encoder
            )
            print(status)
            
            time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        finish_test(BP)


def motors_readings(intro: str, msg_start: str, test_function: Callable) -> None:
    init_test(intro)
    reset_motor_encoders(BP)

    try:
        while True:
            status = get_status_msg(
                msg_start,
                BP_MOTOR_PORTS,
                test_function
            )
            print(status)
            
            time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        finish_test(BP)


def motor_encoder_test() -> None:
    intro = '''
# Hardware: Connect EV3 or NXT motor(s) to any of the BrickPi3 motor ports.
# 
# Results:  When you run this program, you should see the encoder value for each motor. By manually rotating a motor, the count should change by 1 for every degree of rotation.
'''
    motors_readings(intro, "Encoder: ", BP.get_motor_encoder)


def motor_status_test() -> None:
    intro = '''
# Hardware: Connect EV3 or NXT motor(s) to any of the BrickPi3 motor ports.
#
# Results:  When you run this program, the status of each motor will be printed.
'''
    motors_readings(intro, "Motor status: ", BP.get_motor_status)


@run_for_specific_port("motor")
def test_motors(
    intro: str,
    test_logic: Callable,
    port_number: int = 1,
    port_name: str = "A",
) -> None:
    init_test(intro.format(port_name, port_name))
    try:
        other_ports = get_other_ports(BP_MOTOR_PORTS, port_number)
        other_ports_sum = get_ports_sum(other_ports)
        reset_motor_encoders(BP)

        kwargs = {
            "port_number": port_number,
            "other_ports": other_ports,
            "other_ports_sum": other_ports_sum
        }
        test_logic(**kwargs)
        

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        finish_test(BP)


def motor_dps_test() -> None:
    intro = '''
# Hardware: Connect EV3 or NXT motors to the BrickPi3 motor ports. Make sure that the BrickPi3 is running on a 9v power supply.
#
# Results:  When you run this program, other motors' speed will be controlled by the position of motor {}. Manually rotate motor {}, and motors' speed will change.
'''
    
    def test_logic(
        port_number: int,
        other_ports: list[Port],
        other_ports_sum: int
    ) -> None:
        BP.set_motor_power(port_number, BP.MOTOR_FLOAT)

        while True:
            target = get_brickpi3_value(BP.get_motor_encoder, port_number)
            BP.set_motor_dps(other_ports_sum, target)
            BP.set_motor_limits(other_ports_sum, 50, 200)

            status = get_status_msg(
                f"Target Degrees Per Second: {target}   Motor status ",
                other_ports,
                BP.get_motor_status
            )
            print(status)

            time.sleep(0.02)

    test_motors(intro, test_logic)


def motor_position_test() -> None:
    intro = '''
# Hardware: Connect EV3 or NXT motors to the BrickPi3 motor ports. Make sure that the BrickPi3 is running on a 9v power supply.
#
# Results:  When you run this program, other motors will run to match the position of motor {}. Manually rotate motor {}, and motors will follow.
'''
    def test_logic(
        port_number: int,
        other_ports: list[Port],
        other_ports_sum: int
    ) -> None:
        BP.set_motor_power(port_number, BP.MOTOR_FLOAT)
        BP.set_motor_limits(other_ports_sum, 50, 200)

        while True:
            target = get_brickpi3_value(BP.get_motor_encoder, port_number)
            BP.set_motor_position(other_ports_sum, target)
            
            status = get_status_msg(
                f"Target: {target}   Motor position ",
                other_ports,
                BP.get_motor_encoder
            )
            print(status)

            time.sleep(0.02)
    
    test_motors(intro, test_logic)


def motor_power_test() -> None:
    intro = '''
# Hardware: Connect EV3 or NXT motors to the BrickPi3 motor ports. Make sure that the BrickPi3 is running on a 9v power supply.
#
# Results:  When you run this program, motors' power will be controlled by the position of motor {}. Manually rotate motor {}, and motors' power will change.
'''
    def test_logic(
        port_number: int,
        other_ports: list[Port],
        other_ports_sum: int
    ) -> None:
        while True:
            power = count_motor_power_based_on_encoder_value(
                BP,
                port_number,
                10,
                100
            )
            BP.set_motor_power(other_ports_sum, power)

            

            time.sleep(0.02)

    test_motors(intro, test_logic)


def read_info() -> None:
    intro = '''
# Results: Print information about the attached BrickPi3.
'''
    print(intro)
    print()
    
    try:
        # Each of the following BP.get functions return a value that we want to display.
        print("Manufacturer    : ", get_brickpi3_value(BP.get_manufacturer)    ) # read and display the serial number
        print("Board           : ", get_brickpi3_value(BP.get_board)           ) # read and display the serial number
        print("Serial Number   : ", get_brickpi3_value(BP.get_id)              ) # read and display the serial number
        print("Hardware version: ", get_brickpi3_value(BP.get_version_hardware)) # read and display the hardware version
        print("Firmware version: ", get_brickpi3_value(BP.get_version_firmware)) # read and display the firmware version
        print("Battery voltage : ", get_brickpi3_value(BP.get_voltage_battery) ) # read and display the current battery voltage
        print("9v voltage      : ", get_brickpi3_value(BP.get_voltage_9v)      ) # read and display the current 9v regulator voltage
        print("5v voltage      : ", get_brickpi3_value(BP.get_voltage_5v)      ) # read and display the current 5v regulator voltage
        print("3.3v voltage    : ", get_brickpi3_value(BP.get_voltage_3v3)     ) # read and display the current 3.3v regulator voltage
        input("\nPress any key to continue ...")
    except FirmwareVersionError as error:
        print(error)
    finally:
        finish_test(BP)


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
        finish_test(BP)


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
        finish_test(BP)


def main() -> None:
    options = [
        ("Motor encoder", motor_encoder_test),
        ("Motor status", motor_status_test),
        ("Motor power", motor_power_test),
        ("Motor position", motor_position_test),
        ("Motor DPS", motor_dps_test),
        ("Motors with touch sensor", motors_touch_sensor_test),
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
        finish_test(BP)

if __name__ == "__main__":
    main()
