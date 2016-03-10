import os
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
import sys
import threading
import atexit
from flask import Flask
import random
import json
import requests
from flask import jsonify

POLL_TIME = 5


# variables that are accessible from anywhere
commonDataStruct = BoatData.BoatData()
# lock to control access to variable
dataLock = threading.Lock()
# thread handler
yourThread = threading.Thread()


app = Flask(__name__, static_url_path='')




def run():
    def interrupt():
        global yourThread
        yourThread.cancel()

    def doStuff():
        global commonDataStruct
        global yourThread
        with dataLock:
            commonDataStruct.gps_coord.lat = random.uniform(0,5)
            commonDataStruct.gps_coord.long = random.uniform(0,5)


        # Set the next thread to happen
        yourThread = threading.Timer(POLL_TIME, doStuff, ())
        yourThread.start()

    def doStuffStart():
        # Do initialisation stuff here
        global yourThread
        # Create your thread
        yourThread = threading.Timer(POLL_TIME, doStuff, ())
        yourThread.start()

    # Initiate
    doStuffStart()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)

    app.run(debug=True)

@app.route('/')
def index():
    return app.send_static_file("index.html")

@app.route('/data')
def data():
    lat = commonDataStruct.gps_coord.lat
    lng = commonDataStruct.gps_coord.long
    # lat = random.uniform(35, 37)
    # lng = random.uniform(139, 141)
    coords = [lat, lng]
    return json.dumps(coords)


if __name__ == '__main__':
    try:
        sys.exit(run())
    except KeyboardInterrupt:
        print "\n Exit - Keyboard Interrupt"

    # gVars.bus.close()