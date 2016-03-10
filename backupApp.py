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
commonDataStruct = {}
# lock to control access to variable
dataLock = threading.Lock()
# thread handler
yourThread = threading.Thread()


app = Flask(__name__, static_url_path='')

def run():
    app.run(debug=True)
    # print "Starting the Bus"
    #
    # gVars.simulated.add('TCU')
    # gVars.simulated.add('SCU')
    # gVars.simulated.add('MC')
    #
    # gVars.bus = interface.Interface(gVars.simulated)


@app.route('/')
def index():
    return app.send_static_file("index.html")


# @app.route('/')
# def index():
#     return 'Hello World'


@app.route('/data')
def data():
    lat = random.uniform(35, 37)
    lng = random.uniform(139, 141)
    coords = [lat, lng]
    return json.dumps(coords)


if __name__ == '__main__':
    try:
        sys.exit(run())
    except KeyboardInterrupt:
        print "\n Exit - Keyboard Interrupt"

    # gVars.bus.close()