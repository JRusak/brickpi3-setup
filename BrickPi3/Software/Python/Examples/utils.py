from collections.abc import Callable
from brickpi3 import BrickPi3, SensorError
import time  # import the time library for the sleep function

from typing import TypeAlias

Option: TypeAlias = tuple[str, Callable]
Port: TypeAlias = tuple[int, str]


BP_SENSOR_PORTS = [
    (BrickPi3.PORT_1, "1"),
    (BrickPi3.PORT_2, "2"),
    (BrickPi3.PORT_3, "3"),
    (BrickPi3.PORT_4, "4"),
]

BP_MOTOR_PORTS = [
    (BrickPi3.PORT_A, "A"),
    (BrickPi3.PORT_B, "B"),
    (BrickPi3.PORT_C, "C"),
    (BrickPi3.PORT_D, "D"),
]


# brickpi3


def get_brickpi3_value(get_fun: Callable, port: int = None) -> any:
    try:
        return get_fun(port) if port else get_fun()
    except IOError as error:
        print(error)
        return 0


def print_available_ports(ports: list[Port]) -> None:
    print("Available ports:", *[p[1] for p in ports])


def get_ports(port_type: str) -> list[Port]:
    return {"sensor": BP_SENSOR_PORTS, "motor": BP_MOTOR_PORTS}.get(port_type, [])


def get_port_decision(ports: list[Port]) -> str:
    decision = ""

    while decision != "all" and decision not in [p[1] for p in ports]:
        decision = input(
            "Choose port or type 'all' if you want to run tests for all ports: "
        )

    return decision


# sensors


def get_multi_mode_values(
    bp: BrickPi3, port_number: int, sensor_type: list[int], parser: Callable
) -> None:
    values = []

    for s_t in sensor_type:
        bp.set_sensor_type(port_number, s_t)
        time.sleep(0.02)
        values.append(bp.get_sensor(port_number))

    return [parse_value(v, parser) for v in values]


def parse_value(value: any, parser: Callable) -> None:
    return parser(value) if parser else value


def configure_sensor(bp: BrickPi3, port_number: int) -> None:
    try:
        bp.get_sensor(port_number)
    except SensorError:
        print("Configuring...")
        error = True
        while error:
            time.sleep(0.1)
            try:
                bp.get_sensor(port_number)
                error = False
            except SensorError:
                error = True
    print("Configured.")


def get_color_from_color_sensor_value(value) -> str:
    return ["none", "Black", "Blue", "Green", "Yellow", "Red", "White", "Brown"][value]


def get_value_parser(parser: str) -> Callable:
    return {"COLOR": get_color_from_color_sensor_value}.get(parser)


# motors


def count_motor_power_based_on_encoder_value(
    bp: BrickPi3, port: int, divider: int, max_power: int
) -> int:
    power = get_brickpi3_value(bp.get_motor_encoder, port) / divider

    if power > max_power:
        power = max_power
    elif power < -max_power:
        power = -max_power

    return power


def get_ports_sum(ports: list[Port]) -> int:
    return sum(p[0] for p in ports)


def get_status_msg(msg_start: str, ports: list[Port], status_fun: Callable) -> str:
    status = [msg_start]
    for p, n in ports:
        status.append(f" {n}: {get_brickpi3_value(status_fun, p)}")
    return "".join(status)


def reset_motor_encoders(bp: BrickPi3) -> None:
    for port, _ in BP_MOTOR_PORTS:
        bp.offset_motor_encoder(port, get_brickpi3_value(bp.get_motor_encoder, port))


def get_other_ports(ports: list[Port], main_port: int) -> list[int]:
    return [p for p in ports if p[0] != main_port]


# tests


def print_options(options: list[Option]) -> None:
    print("Test options:")

    for i, op in enumerate(options):
        print(f"{i}. {op[0]}")

    print()
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
    input("Press enter to start the test")
    print()


def finish_test(bp: BrickPi3) -> None:
    bp.reset_all()  # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
    print("\n")
