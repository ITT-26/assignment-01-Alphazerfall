import sys
import socket

IP = "127.0.0.1"
PORT = 5700
BUFFER_SIZE  = 1024

server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
server.settimeout(0.1)  # to avoid ctrl+c not working because socket is running in a blocking fashion
server.bind((IP, PORT))

try:
    # listen to client
    while(True):
        try:
            data, addr = server.recvfrom(BUFFER_SIZE)
            data_decoded = data.decode()
            print(f'message from client ({addr}): {data_decoded}')

        # if timed out, just ignore this and wait for the next message
        except TimeoutError:
            continue

# close socket and quit program on ctrl+c
except KeyboardInterrupt:
    server.close()
    sys.exit(0)



    