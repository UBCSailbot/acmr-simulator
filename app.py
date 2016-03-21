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

# Create boat data struct accessible to Flask and Simulator threads
boatDataStruct = BoatData.BoatData()
# Lock to control access to variable
dataLock = threading.Lock()
# Thread handler
simulatorThread = threading.Thread()

app = Flask(__name__, static_url_path='')

def interrupt():
    global simulatorThread
    simulatorThread.cancel()

def runSimulator():
    global boatDataStruct
    global TWA
    global currentVector
    global simulatorThread
    with dataLock:
        sim = simulator.Simulator(gVars.verbose, gVars.reset, gVars.gust, gVars.dataToUI)
        while 1:
            sim.dest_coords.lat = dest.lat
            sim.dest_coords.long = dest.long
            sim.update()
            boatDataStruct = sim.boatData
            TWA = sim.trueWindAngle
            currentVector = sim.currentFlowVector
            time.sleep(0.25)

def runSimThread():
    global simulatorThread
    global dest
    dest = GPSCoordinate.GPSCoordinate(0,0).createCoordDistAway(50, 25)
    # Create simulator thread
    simulatorThread = threading.Timer(1, runSimulator, ())
    simulatorThread.start()

def run():
    print "Starting the Bus"
    gVars.simulated.add('TCU')
    gVars.simulated.add('SCU')
    gVars.simulated.add('MC')
    # Start the bus
    gVars.bus = interface.Interface(gVars.simulated)
    # Start the simulator thread
    runSimThread()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    # atexit.register(interrupt)

    # Run the Flask application
    app.run(threaded=True)

@app.route('/')
def index():
    return app.send_static_file("index.html")

# This is where relevant data is sent from simulator to frontend.
@app.route('/data')
def data():
    lat = boatDataStruct.gps_coord.lat
    lng = boatDataStruct.gps_coord.long
    # aws = boatDataStruct.windspeed
    # awa = boatDataStruct.awa
    hog = boatDataStruct.hog
    sow = boatDataStruct.sow
    twa = TWA
    awa = standardcalc.bound_to_180(boatDataStruct.hog + boatDataStruct.awa)
    # dest = GPSCoordinate.GPSCoordinate(0,0).createCoordDistAway(100,50)
    # Data to be sent in one array.
    coords = [lat, lng, awa, sow, hog, dest.lat, dest.long, currentVector.length(), currentVector.angle()]
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
        print "\n Exit - Keyboard Interrupt"

    gVars.bus.close()