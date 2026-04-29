import math
from random import random
import socket
import time
import json

IP = "127.0.0.1"
PORT = 5700
TICK_LENGTH = 0.05  # 20 Hz update rate
BUTTON_TOGGLE_CHANCE = 0.02  # Chance to toggle button state each tick


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    t = 0.0
    button_1_state = False

    print(f"Sending DIPPID data to {IP}:{PORT}")

    try:
        while True:
            # Simulate button toggle
            if random() < BUTTON_TOGGLE_CHANCE:
                button_1_state = not button_1_state
            
            message_dict = {
                "accelerometer": {
                    "x": math.sin(t * 0.5),
                    "y": math.cos(t * 0.7),
                    "z": math.sin(t * 0.9 + 1.0)
                },
                "button_1": int(button_1_state)

            }

            message = json.dumps(message_dict)

            sock.sendto(message.encode(), (IP, PORT))

            t += TICK_LENGTH
            time.sleep(TICK_LENGTH)
    except KeyboardInterrupt:
        print("Exiting")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
