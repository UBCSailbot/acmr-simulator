import os
import sys
import simulator
from drivers import interface
import global_vars as gVars
from datatype import BoatData
import time
import sys
import threading
import atexit
from flask import Flask
import json
from datatype import GPSCoordinate
import standardcalc
import requests
from flask import jsonify
import csv

# Create boat data struct accessible to Flask and Simulator threads
boatDataStruct = BoatData.BoatData()
# Lock to control access to variable
dataLock = threading.Lock()

app = Flask(__name__, static_url_path='')

class simThread(threading.Thread):

    def __init__(self):
        super(simThread,self).__init__()
        self.exitFlag = 0

    def run(self):
        print "Starting the Simulator"
        global boatDataStruct
        global TWA, TWS
        global currentVector
        with dataLock:
            sim = simulator.Simulator(gVars.verbose, gVars.reset, gVars.gust, gVars.dataToUI)
            with open('simulation_data/test2.csv', 'wb') as file:
                w = csv.writer(file, lineterminator='\n')
                w.writerow(['Test','blah'])
                # for i in range(0, 10):
                #     w.writerow(['test','bla'])
                # for i in range(0, 10):
                while not self.exitFlag:
                    sim.dest_coords.lat = dest.lat
                    sim.dest_coords.long = dest.long
                    sim.update()
                    boatDataStruct = sim.boatData
                    TWA = sim.trueWindAngle
                    TWS = sim.trueWindSpeed
                    currentVector = sim.currentFlowVector
                    w.writerow(['Test','blab'])
                    time.sleep(0.25)

    def close(self):
        self.exitFlag = True
        self.join()

def run():
    print "Starting the Bus"
    gVars.simulated.add('TCU')
    gVars.simulated.add('SCU')
    gVars.simulated.add('MC')
    # Start the bus
    gVars.bus = interface.Interface(gVars.simulated)
    global dest
    dest = GPSCoordinate.GPSCoordinate(0,0).createCoordDistAway(50, 25)
    simulatorThread = simThread()
    simulatorThread.start()
    # Start the simulator thread
    # runSimThread()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    # atexit.register(interrupt)

    # Run the Flask application
    print "Starting the GUI (Flask application)"
    app.run(threaded=True,use_reloader=False)
    print "\n Exit - Keyboard Interrupt"
    gVars.bus.close()
    simulatorThread.close()
    # simulatorThread.exitFlag = True
    # simulatorThread.join()


@app.route('/')
def index():
    return app.send_static_file("index.html")

# This is where relevant data is sent from simulator to frontend.
@app.route('/data')
def data():
    lat = boatDataStruct.gps_coord.lat
    lng = boatDataStruct.gps_coord.long
    aws = boatDataStruct.windspeed
    awa = boatDataStruct.awa
    hog = boatDataStruct.hog
    sow = boatDataStruct.sow
    tws = TWS
    twa = TWA
    awa_abs = standardcalc.bound_to_180(boatDataStruct.hog + boatDataStruct.awa)
    # dest = GPSCoordinate.GPSCoordinate(0,0).createCoordDistAway(100,50)
    # Data to be sent in one array.
    coords = [lat, lng, awa_abs, sow, hog, dest.lat, dest.long, currentVector.length(), currentVector.angle(),
              awa, aws, twa, tws]
    # Converts data to JSON.
    return json.dumps(coords)


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
        pass