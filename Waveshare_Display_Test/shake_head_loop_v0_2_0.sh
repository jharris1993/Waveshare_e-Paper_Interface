#!/usr/bin/python3.7

# shake_head_loop v0.2.0 - shake_head_loop_v0_2_0.sh
# Smooth servo movement, local PID file, and graceful signal handling.

import os
import signal
import sys
import time

import easygopigo3 as easy

# User settings
sleep_time = 0.50       # Pause at each destination (seconds)
loop = 1                # 1 = repeat; anything else = run once
offset = 45             # Degrees either side of center
step_degrees = 4       # Maximum movement per command (degrees)
step_delay = 0.01       # Pause between movement commands (seconds)

PID_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        "shake_head_loop.PID")
stop_requested = False


def request_stop(signum, frame):
    global stop_requested
    stop_requested = True
    print("\nSignal {} received; stopping.".format(signum))


def pause(seconds):
    """Wait in short intervals so termination is responsive."""
    deadline = time.monotonic() + seconds
    while not stop_requested:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(remaining, 0.05))


def move_smoothly(servo, current, destination, allow_stop=True):
    """Step to the exact destination; return the last commanded angle."""
    if step_degrees <= 0:
        raise ValueError("step_degrees must be positive")
    while current != destination:
        if allow_stop and stop_requested:
            break
        delta = destination - current
        current += max(-step_degrees, min(step_degrees, delta))
        servo.rotate_servo(current)
        time.sleep(step_delay)
    return current


def acquire_pid_file():
    """Create a PID file without overwriting an existing instance's file."""
    try:
        fd = os.open(PID_FILE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        raise RuntimeError("PID file already exists: {} (check for a running instance)".format(PID_FILE))
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write("{}\n".format(os.getpid()))
    except BaseException:
        os.unlink(PID_FILE)
        raise


def main():
    global stop_requested
    acquire_pid_file()
    servo_1 = None
    servo_2 = None
    position_1 = None
    position_2 = None
    center_1 = None
    center_2 = None
    try:
        signal.signal(signal.SIGINT, request_stop)
        signal.signal(signal.SIGTERM, request_stop)
        signal.signal(signal.SIGHUP, request_stop)

        easy_gpg = easy.EasyGoPiGo3()
        servo_1 = easy_gpg.init_servo('SERVO1')
        servo_2 = easy_gpg.init_servo('SERVO2')

        print("Running: Test Servos. PID: {}".format(os.getpid()))
        serial_number = easy_gpg.get_id()
        print("This robot's serial number is\n{}\n".format(serial_number))

        if serial_number == "A0F6E45F4E514B4B41202020FF152B11":
            print('Robot is "Charlene"')
            center_1, center_2 = 86, 76
        elif serial_number == "64B61037514E343732202020FF111A05":
            print('Robot is "Charlie"')
            center_1, center_2 = 86, 94
        else:
            print('Robot is "Unknown"; using default centering constants of 90/90.')
            center_1, center_2 = 90, 90

        right, left = center_1 - offset, center_1 + offset
        up, down = center_2 - offset, center_2 + offset

        # The starting physical positions are unknown; initial centering
        # must therefore use direct commands. Subsequent moves are stepped.
        servo_1.rotate_servo(center_1)
        servo_2.rotate_servo(center_2)
        position_1, position_2 = center_1, center_2

        while not stop_requested:
            print("\nStarting test:")
            pause(2 * sleep_time)
            if stop_requested:
                break
            print("Using centering constants {}/{}".format(center_1, center_2))

            print("Test Servo 1 (horizontal motion)")
            for destination in (right, left, center_1):
                position_1 = move_smoothly(servo_1, position_1, destination)
                pause(sleep_time)
                if stop_requested:
                    break
            if stop_requested:
                break

            print("Test Servo 2 (vertical motion)")
            for destination in (up, down):
                position_2 = move_smoothly(servo_2, position_2, destination)
                pause(sleep_time)
                if stop_requested:
                    break
            if stop_requested:
                break

            print("Re-Center Both Servos")
            position_1 = move_smoothly(servo_1, position_1, center_1)
            position_2 = move_smoothly(servo_2, position_2, center_2)
            pause(sleep_time)
            if loop != 1:
                break
    finally:
        # Best-effort gradual recentering, then release servo PWM.
        try:
            if servo_1 is not None and position_1 is not None and center_1 is not None:
                move_smoothly(servo_1, position_1, center_1, allow_stop=False)
            if servo_2 is not None and position_2 is not None and center_2 is not None:
                move_smoothly(servo_2, position_2, center_2, allow_stop=False)
        finally:
            try:
                if servo_1 is not None:
                    servo_1.disable_servo()
                if servo_2 is not None:
                    servo_2.disable_servo()
            finally:
                try:
                    os.unlink(PID_FILE)
                except FileNotFoundError:
                    pass
                print("Complete: Test Servos - Exiting.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError) as exc:
        print("Error: {}".format(exc), file=sys.stderr)
        sys.exit(1)
