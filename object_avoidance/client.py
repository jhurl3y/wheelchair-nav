import socket
import sys

HOST, PORT = "10.42.0.1", 9999
data = "Hey".join(sys.argv[1:])

# SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    # As you can see, there is no connect() call; UDP has no connections.
    # Instead, data is directly sent to the recipient via sendto().
    sock.sendto(data + "\n", (HOST, PORT))
    received = sock.recv(1024)

    print "Sent:     {}".format(data)
    print "Received: {}".format(received)
