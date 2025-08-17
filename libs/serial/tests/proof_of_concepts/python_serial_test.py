#!/usr/bin/env python3

import sys


def main() -> None:
    """Minimal serial test, updated for Python 3."""
    if len(sys.argv) != 2:
        print("python: Usage_serial_test <port name like: /dev/ttyUSB0>")
        sys.exit(1)

    import serial  # Imported lazily to avoid dependency at import time

    sio = serial.Serial(sys.argv[1], 115200)
    sio.timeout = 0.25

    while True:
        sio.write(b"Testing.")
        print(sio.read(8))


if __name__ == "__main__":
    main()

