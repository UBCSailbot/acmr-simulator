# Main class for python simulator
import sys
import simulator
from drivers import interface
import global_vars as gVars
import run_threads
import static_vars as sVars
from datetime import datetime
from datatype import GPSCoordinate
from datatype import BoatData
import time

def run():


    # InterfaceThread = run_threads.ZMQ_Thread(2, "Interface Thread")
    # SimulatorThread = run_threads.MainSimulatorThread(1, "Simulator Thread")


    # SimulatorThread.start()
    # InterfaceThread.start()
    # Example calls:
    # hardware.getAWA()
    # hardware.getWindSpeed()

    print "Starting the Bus"

    gVars.simulated.add('TCU')
    gVars.simulated.add('SCU')
    gVars.simulated.add('MC')

    gVars.bus = interface.Interface(gVars.simulated)

    print "Starting the Simulator"

    # gVars.interfaceData = BoatData.BoatData()
    hardware = simulator.Simulator( gVars.verbose, gVars.reset, gVars.gust, gVars.dataToUI)
    while 1:
        hardware.update()
        # print "Received: Rudder Angle = " + str(gVars.bus.getData().rudder) + " ; Prop. Setting = " \
        #           + str(gVars.bus.getData().sheet_percent)
        time.sleep(0.25)


def getCurrentData():
    if gVars.currentProcess == None:
        pass
    gVars.interfaceData = gVars.bus.getData()


if __name__ == '__main__':
    try:
        gVars.verbose = gVars.reset = gVars.gust = gVars.dataToUI = False
        for arg in sys.argv:
            if arg == "--help":
                print "Sailing condition simulator for the UBC Sailbot Transat MCU"
                print "Usage instructions: 'python main.py <flags>'"
                print " Pass desired flags separated by spaces"
                print " -v : Verbose output"
                print " -r : Reset simulation"
                print " -g : Gust simulation enabled"
                print " -d : Send data to UI (do not use with Route Making)"
                sys.exit()
            if arg == "-v":
                gVars.verbose = True
            if arg == "-r":
                gVars.reset = True
            if arg == "-g":
                gVars.gust = True
            if arg == "-d":
                gVars.dataToUI = True
        sys.exit(run())

    except KeyboardInterrupt:
        print "\n Exit - Keyboard Interrupt"

    gVars.bus.close()




