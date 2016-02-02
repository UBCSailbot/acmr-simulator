# Main class for python simulator
import sys
import simulator
import thread
from drivers import interface
import global_vars as gVars
import static_vars as sVars
from datetime import datetime
from datatype import GPSCoordinate

def run():
    hardware = simulator.Simulator(verbose, reset, gust, dataToUI)

    gVars.simulated.add('WS')
    gVars.simulated.add('GPS')
    gVars.simulated.add('TCU')
    gVars.simulated.add('SCU')

    gVars.bus = interface.Interface(gVars.simulated)
    gVars.currentData = gVars.bus.getData()

    while 1:
        hardware.update()

    # Example calls:
    # hardware.getAWA()
    # hardware.getWindSpeed()

def getCurrentData():
    if gVars.currentProcess == None:
        pass
    gVars.currentData = gVars.bus.getData()


if __name__ == '__main__':
    try:
        verbose = reset = gust = dataToUI = False
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
                verbose = True
            if arg == "-r":
                reset = True
            if arg == "-g":
                gust = True
            if arg == "-d":
                dataToUI = True
        sys.exit(run())
    except KeyboardInterrupt:
        print "\n Exit - Keyboard Interrupt"
