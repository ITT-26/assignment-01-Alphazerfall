import math
import socket
import time
import json

IP = "127.0.0.1"
PORT = 5700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

TICK_LENGTH = 0.05
t = 0.0
button_1_state = False

while True:
    accel = {
        "x": math.sin(t),
        "y": math.cos(t),
        "z": math.sin(t - 1)
    }


    message_dict = {"acceleration": accel, "button_1": "true"}
    message = json.dumps(message_dict)

    #print(message)

    sock.sendto(message.encode(), (IP, PORT))

    t += TICK_LENGTH
    time.sleep(TICK_LENGTH)
