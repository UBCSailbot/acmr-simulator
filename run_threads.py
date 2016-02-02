import sys
import simulator
import time
import threading
import global_vars as gVars
from datatype import BoatData
from drivers import interface
from drivers import ZMQHandler


class MainSimulatorThread ():
    def __init__(self):
        # threading.Thread.__init__(self)
        # self.threadID = threadID
        # self.name = name
        pass

    def run(self):
        print "Starting " + self.name

        gVars.interfaceData = BoatData.BoatData()
        hardware = simulator.Simulator( gVars.verbose, gVars.reset, gVars.gust, gVars.dataToUI)
        while 1:
            hardware.update()



class ZMQ_Thread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print "Starting " + self.name

        gVars.simulated.add('WS')
        gVars.simulated.add('SCU')

        gVars.bus = interface.Interface(gVars.simulated)

        # ZMQ = ZMQHandler.ZMQController()

        while 1:
            ZMQ.read()
            print "Received: Rudder Angle = " + str(ZMQ.data.rudder) + " ; Prop. Setting = " \
                  + str(ZMQ.data.sheet_percent)
            gVars.interfaceData = ZMQ.data

            time.sleep(1)