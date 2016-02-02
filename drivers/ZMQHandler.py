"""
    Created by Lawrence Garcia on 31 Jan 2016

"""


import zmq
from datatype.BoatData import BoatData
import threading
import time

class ZMQHandler(threading.Thread):
    # in seconds
    ZMQ_DELAY = 0.1

    def __init__(self):
        super(ZMQHandler, self).__init__()
        self.context = zmq.Context()
        self.pubsocket = self.context.socket(zmq.PUB)
        self.pubsocket.connect("tcp://localhost:5551")

        self.subsocket = self.context.socket(zmq.SUB)
        self.subsocket.connect("tcp://localhost:5552")

        # Simulator subscribes to data for Rudder [Angle] (RUD) and Apparent Wind (AW) only.
        self.subsocket.setsockopt(zmq.SUBSCRIBE, "RUD")
        self.subsocket.setsockopt(zmq.SUBSCRIBE, "PROP")

        self.exitFlag = 0

        self.data = BoatData()

    def run(self):
        while not self.exitFlag:
            self.read()
            time.sleep(self.ZMQ_DELAY)

    def read(self):
        try:
            rec_str = self.subsocket.recv(flags=zmq.NOBLOCK)

            # print rec_str
            # Split the message by space
            received = rec_str.split()

            datatopic = received[0]

            if datatopic == 'RUD':
                if(len(received) != 2):
                    return
                self.data.rudder = int(received[1])
            elif datatopic == 'PROP':
                if(len(received) != 2):
                    return
                self.data.sheet_percent = int(received[1])
            elif datatopic == 'GPS':
                if(len(received) != 6):
                    return
                self.data.gps_coord.lat = float(received[1])
                self.data.gps_coord.long = float(received[2])
                self.data.hog = int(received[3])
                self.data.sog = int(received[4])
                self.data.cog = int(received[5])
            elif datatopic == 'AW':
                if(len(received) != 3):
                    return
                self.data.windspeed = int(received[1])
                self.data.awa = int(received[2])
            else:
                # print "Invalid Topic detected"
                print rec_str
                # ignore the unknown topic
                pass


        except zmq.error.ZMQError, e:
            # If there is no message, do nothing
            # print "..."
            # rec_str = ''
            pass
        pass

    def write(self, args):
        # args = tuple(args)
        args = map(str, args)
        send_str = " ".join(args)
        self.pubsocket.send(send_str)


#
# class ZMQController:
#     def __init__(self):
#         self.context = zmq.Context()
#         self.pubsocket = self.context.socket(zmq.PUB)
#         self.pubsocket.connect("tcp://localhost:5551")
#
#         self.subsocket = self.context.socket(zmq.SUB)
#         self.subsocket.connect("tcp://localhost:5552")
#
#         # Simulator subscribes to data for Rudder [Angle] (RUD) and Apparent Wind (AW) only.
#         self.subsocket.setsockopt(zmq.SUBSCRIBE, "RUD")
#         self.subsocket.setsockopt(zmq.SUBSCRIBE, "AW")
#
#         self.data = BoatData()
#
#     def read(self):
#
#
#         try:
#             rec_str = self.subsocket.recv(flags=zmq.NOBLOCK)
#
#             # Split the message by space
#             received = rec_str.split()
#
#             datatopic = received[0]
#
#             # print "Attempting to read..." + str(datatopic)
#
#             if datatopic == 'RUD':
#                 if(len(received) != 2):
#                     return
#                 self.data.rudder = int(received[1])
#             elif datatopic == 'PROP':
#                 if(len(received) != 2):
#                     return
#                 self.data.sheet_percent = int(received[1])
#             elif datatopic == 'GPS':
#                 if(len(received) != 6):
#                     return
#
#                 self.data.gps_coord.lat = float(received[1])
#                 self.data.gps_coord.long = float(received[2])
#                 self.data.hog = int(received[3])
#                 self.data.sog = int(received[4])
#                 self.data.cog = int(received[5])
#             elif datatopic == 'AW':
#                 if(len(received) != 3):
#                     return
#                 self.data.windspeed = int(received[1])
#                 self.data.awa = int(received[2])
#             else:
#                 # print "Invalid Topic detected"
#                 pass
#
#
#         except zmq.error.ZMQError, e:
#             # If there is no message, do nothing
#             # print "..."
#             # rec_str = ''
#             pass
#         pass
#
#     def write(self):
#         pass

