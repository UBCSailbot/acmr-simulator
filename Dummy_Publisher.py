import zmq
import sys
import time

context = zmq.Context()
pubSocket = context.socket(zmq.PUB)
pubSocket.connect("tcp://localhost:5551")

count = 0

while True:
    count += 1
    print "Sending " + str(count)

    pubSocket.send("RUD %s" %(str(count)))
    time.sleep(1)