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
import requests
from flask import jsonify

# variables that are accessible from anywhere
boatDataStruct = BoatData.BoatData()
# lock to control access to variable
dataLock = threading.Lock()
# thread handler
simulatorThread = threading.Thread()

app = Flask(__name__, static_url_path='')

def run():
    print "Starting the Bus"

    gVars.simulated.add('TCU')
    gVars.simulated.add('SCU')
    gVars.simulated.add('MC')
    gVars.bus = interface.Interface(gVars.simulated)

    def interrupt():
        global simulatorThread
        simulatorThread.cancel()

    def runSimulator():
        global boatDataStruct
        global simulatorThread
        with dataLock:
            sim = simulator.Simulator( gVars.verbose, gVars.reset, gVars.gust, gVars.dataToUI)
            while 1:
                sim.update()
                boatDataStruct = sim.boatData
                time.sleep(0.25)


    def runSimThread():
        # Do initialisation stuff here

        global simulatorThread
        # Create your thread
        simulatorThread = threading.Timer(2, runSimulator, ())
        simulatorThread.start()

    # Initiate
    runSimThread()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)
    app.run(debug=True)

@app.route('/')
def index():
    return app.send_static_file("index.html")

@app.route('/data')
def data():
    lat = 35 + boatDataStruct.gps_coord.lat
    lng = 130 + boatDataStruct.gps_coord.long
    # lat = random.uniform(35, 37)
    # lng = random.uniform(139, 141)
    aws = boatDataStruct.windspeed
    awa = boatDataStruct.awa
    coords = [lat, lng, aws, awa]
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