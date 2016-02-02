# Python simulator class for MCU
import random
import standardcalc
import os
import math
import threading
import sys
import time
from drivers import interface
import global_vars as gVars
import static_vars as sVars
from datetime import datetime
from datatype import GPSCoordinate

# This will be the format of the file output
# The file will be a space delimited file.
# The first line will be a header, depicting which variable is where
# hog awa sog windSpeed latitude longitude rudderAngle sheetPercentage
# |--------------------------------------------------------------|
# | hog | awa | sog | wSpd | lat | long | rud | sheet|
# |--------------------------------------------------------------|
# | oldHog| oldAwa| oldSog|oldWSpd| oldLat|oldLong| oldRud| oldSh|
# |--------------------------------------------------------------|

# Assumes the mcu repository is in the parent directory of simulator.
MCU_DIRECTORY = os.path.join(os.path.pardir, "mcu", "build")
# for self closed loop, change to read from "simulatorOutput"
# otherwise, use "mcuOutput"
LINK_FILE = os.path.join(MCU_DIRECTORY, "simuLink")
ROUTE_FILE = os.path.join(MCU_DIRECTORY, "routeLink")
DUMMY_BOAT_INPUTS_FILE = os.path.join(MCU_DIRECTORY,"dummy_boat_inputs.txt")

class Simulator():
    # degrees of wind change
    WIND_ANGLE_FLUCTUATIONS = .2
    # amount of wind speed change
    WIND_SPEED_FLUCTUATIONS = .4
    # degrees of wind change
    CURRENT_ANGLE_FLUCTUATIONS = .05
    # amount of wind speed change
    CURRENT_SPEED_FLUCTUATIONS = .03
    # runtime for the mcu
    CLOCK_INTERVAL = 1 #was 0.01
    # Time scale for calculations, if equal to clock interval the simulation will run in real time.
    TIME_SCALE = CLOCK_INTERVAL
    # Change in HOG for max rudder setting in 1 meter
    MAX_RUDDER_HOG_CHANGE = 10.0
    # Max rudder angle possible (angle between -45 to 45)
    MAX_RUDDER_ANGLE = 45.0
    # This affects how fast the boat reaches the ideal SOG
    SOG_DECAY_FACTOR = (3 / CLOCK_INTERVAL)
    # How likely a gust is to occur every virtual second (Higher => Less probable)
    GUST_PROBABILITY = 100
    # Actual seconds between every time data is sent to the server
    DATA_DELAY = 1
    #NEW CONSTANTS
    # This is the centerboard to rudder distance L
    L_CENTERBOARD_TO_RUDDER = 1.0

    def __init__(self, verbose, reset, gust, data_to_ui):
        random.seed()
        self.currentData = {'latitude': 0, 'longitude': 0, 'hog': 0, 'cog': 0, 'awa': 0, 'sog': 0, 'windSpeed': 0,
                            'rudderAngle': 0, 'sheetPercentage': 0}
        self.oldData = self.currentData.copy()
        # Choose Random Wind Angle between -180 and 180
        self.trueWindAngle = random.randint(-180, 180)
        self.trueWindSpeed = float(random.randint(10, 15))
        self.currentFlowAngle = random.randint(-180, 180)
        self.currentFlowSpeed = float(random.randint(1, 5))
        self.currentFlowVector = standardcalc.Vector2D.zero()
        self.displacement = standardcalc.Vector2D.zero()

        self.windVector = standardcalc.Vector2D.zero()
        self.boatVector = standardcalc.Vector2D.zero()
        self.apparentWindVector = standardcalc.Vector2D.zero()
        self.verbose = verbose
        self.gust = gust
        self.dataToUI = data_to_ui
        self.gustTimer = 0
        self.dataTimer = 0
        self.preGustTrueWindSpeed = 0
        self.preGustTrueWindAngle = 0

        # These are initializations that make it simple to debug
        # self.trueWindAngle = 0
        # self.trueWindSpeed = 0

        # reset data stored in files
        if reset:
            self.reset_data()

        if data_to_ui:
            self.start_test()

    def update(self):
        self.read_data()
        self.update_old_data()
        if self.gust:
            self.gust_manager()
        self.adjust_sog()
        self.adjust_hog()
        self.adjust_true_wind()
        self.adjust_current()
        self.update_vectors()
        self.adjust_cog_and_sog_for_current()
        self.adjust_position()

        if self.verbose:
            pass
            # print "FINAL SOG:  " + str(self.currentData['sog'])

        self.write_data()
        if self.dataToUI:
            self.send_data_to_ui()

    def read_data(self):
        # keys = ["hog", "cog", "awa", "sog", "windSpeed", "latitude", "longitude", "rudderAngle", "sheetPercentage"]
        #
        # for index, key in enumerate(keys):
        #      self.currentData[key] = float(current_data[index])

        #To enter rudder angle and sheet percentage manually
        # rudderAngle = input("Enter rudder angle: ")
        # self.currentData['rudderAngle'] = rudderAngle
        # sheetPercentage = input("Enter sheet percentage: ")
        # self.currentData['sheetPercentage'] = sheetPercentage

        # To read rudder angle and sheet percentage from file
        # input_file = open('dummy_boat_inputs.txt','r')

        data = gVars.bus.getData()
        self.currentData['rudderAngle'] = data.rudder
        self.currentData['sheetPercentage'] = data.sheet_percent

        # self.currentData['rudderAngle'] = float(input_file.readline())
        # self.currentData['sheetPercentage'] = float(input_file.readline())

    def update_old_data(self):
        self.oldData = self.currentData.copy()

    def gust_manager(self):
        if self.gustTimer <= 0:
            if random.randint(1, self.GUST_PROBABILITY / self.TIME_SCALE) == 2:
                self.preGustTrueWindAngle = self.trueWindAngle
                self.preGustTrueWindSpeed = self.trueWindSpeed
                self.trueWindSpeed = random.randint(20, 30)
                self.trueWindAngle += random.randint(-5, 5)
                self.gustTimer = random.randint(5, 80) / self.TIME_SCALE
        else:
            self.gustTimer -= 1
            if self.verbose:
                print "Gust is active. Timer: " + str(self.gustTimer)
            if self.gustTimer <= 0:
                self.trueWindSpeed = abs(self.preGustTrueWindSpeed + random.randint(-2, 2))
                self.trueWindAngle = standardcalc.bound_to_180(self.preGustTrueWindAngle + random.randint(-1, 1))

    def adjust_hog(self):
        # Make functional, i.e. go to desired rudder angle immediately
        hogChange = self.currentData['sog'] * math.sin(abs(self.currentData['rudderAngle'])* math.pi / 180.0) \
                    / self.L_CENTERBOARD_TO_RUDDER * self.TIME_SCALE
        self.currentData['hog'] += hogChange
        self.currentData['hog'] = standardcalc.bound_to_180(self.currentData['hog'])

        # normalized_rudder_ratio = self.currentData['rudderAngle'] / self.MAX_RUDDER_ANGLE
        # self.currentData['hog'] += normalized_rudder_ratio * self.MAX_RUDDER_HOG_CHANGE * \
        #                            self.currentData['sog'] * self.TIME_SCALE
        # self.currentData['hog'] = standardcalc.bound_to_180(self.currentData['hog'])

    def adjust_cog_and_sog_for_current(self):
        self.currentData['cog'] = self.boatVector.angle()
        self.currentData['sog'] = self.boatVector.length()

    def adjust_sog(self):
        # v_b = w_a*f(phi_aw)*beta where w_a is the apparent wind speed, f(phi_aw) is the norm. BSPD and beta is
        # the control parameter setting (e.g. sheet setting)

        self.currentData['sog'] = standardcalc.calculate_sog_BSPD( self.currentData['awa'],
                                   self.currentData['windSpeed']) * self.currentData['sheetPercentage'] / 100.0

        # multiplier = standardcalc.calculateErrorCoefficient(self.currentData['awa'],
        # self.currentData['sheetPercentage'])
        max_sog = standardcalc.calculate_max_sog(self.currentData['awa'], self.currentData['windSpeed'])

        if self.currentData['sog'] > max_sog:
            self.currentData['sog'] = max_sog
        #
        # tempVector = standardcalc.Vector2D.create_from_angle(self.currentData['cog'], self.currentData['sog']) \
        #                   - self.currentFlowVector
        # self.currentData['sog'] = tempVector.length()
        #
        # # idealSOG = multiplier * max_sog
        # self.currentData['sog'] = self.currentData['sog'] + ((max_sog - self.currentData['sog']) / self.SOG_DECAY_FACTOR)
        #
        # # Rectify if negative
        # self.currentData['sog'] = abs(self.currentData['sog'])
        #

        if self.verbose:
            print "IDEAL SHEET SETTINGS: " + str(standardcalc.calculate_ideal_sheet_percentage(self.currentData['awa']))
            print "MAX SOG: " + str(max_sog)
            print "NEW SOG:  " + str(self.currentData['sog'])

    def adjust_true_wind(self):
        # True wind angle is allowed to fluctuate
        # self.trueWindAngle += standardcalc.generate_bell_curve(self.WIND_ANGLE_FLUCTUATIONS * self.CLOCK_INTERVAL)
        # self.trueWindSpeed += standardcalc.generate_bell_curve(self.WIND_SPEED_FLUCTUATIONS * self.CLOCK_INTERVAL)

        self.trueWindAngle += random.gauss(0,1) * self.CLOCK_INTERVAL
        self.trueWindSpeed += random.gauss(0,1) * self.CLOCK_INTERVAL
        self.trueWindAngle = standardcalc.bound_to_180(self.trueWindAngle)
        self.trueWindSpeed = abs(self.trueWindSpeed)

    def adjust_current(self):
        # self.currentFlowAngle += standardcalc.generate_bell_curve(self.CURRENT_ANGLE_FLUCTUATIONS * self.CLOCK_INTERVAL)
        # self.currentFlowSpeed += standardcalc.generate_bell_curve(self.CURRENT_SPEED_FLUCTUATIONS * self.CLOCK_INTERVAL)
        self.currentFlowAngle += random.gauss(0,1) * self.CLOCK_INTERVAL
        self.currentFlowSpeed += random.gauss(0,1) * self.CLOCK_INTERVAL
        self.currentFlowAngle = standardcalc.bound_to_180(self.currentFlowAngle)
        self.currentFlowSpeed = abs(self.currentFlowSpeed)

    def update_vectors(self):
        self.windVector = -standardcalc.Vector2D.create_from_angle(self.trueWindAngle, self.trueWindSpeed)
        self.currentFlowVector = standardcalc.Vector2D.create_from_angle(self.currentFlowAngle, self.currentFlowSpeed)
        self.boatVector = standardcalc.Vector2D.create_from_angle(self.currentData['hog'], self.currentData['sog']) \
                          + self.currentFlowVector
        self.apparentWindVector = self.windVector - self.boatVector

        self.currentData['awa'] = standardcalc.bound_to_180(
            standardcalc.Vector2D.angle_between(self.boatVector, -self.apparentWindVector))
        self.currentData['windSpeed'] = self.apparentWindVector.length()

    def adjust_position(self):
        # Vector addition
        self.displacement = self.CLOCK_INTERVAL * self.boatVector
        self.currentData['latitude'], self.currentData['longitude'] = standardcalc.shift_coordinates(
            self.currentData['latitude'],
            self.currentData['longitude'],
            self.displacement)

    def write_data(self):
        time.sleep(1)
        keys = ["hog", "cog", "awa", "sog", "windSpeed", "latitude", "longitude", "rudderAngle", "sheetPercentage"]

        # Create the space delimited lines
        header_line = ""
        old_data = ""
        current_data = ""

        for key in keys:
            header_line += key + " "
            old_data += '%.8f' % self.oldData[key] + " "
            current_data += '%.8f' % self.currentData[key] + " "

        header_line = header_line.rstrip()
        old_data = old_data.rstrip()
        current_data = current_data.rstrip()

        if self.verbose:
            # Debug printer
            print "===================="
            print header_line
            print old_data
            print current_data

            print "\n"
            print "TRUE WIND SPEED: " + '%.8f' % self.trueWindSpeed
            print "TRUE WIND ANGLE: " + '%.8f' % self.trueWindAngle
            print "CURRENT SPEED: " + '%.8f' % self.currentFlowSpeed
            print "CURRENT ANGLE: " + '%.8f' % self.currentFlowAngle
        else:
            print current_data

    def reset_data(self):
        # # Create the space delimited lines
        # data_line = "0.00000000 0.00000000 -90.0000000 10.00000000 20.00000000 49.676614 -123.178798 0.00000000 " \
        #             "70.00000000"  # Start Point: Jericho 49.276001 -123.200235, ^Squamish^, NL 53.57479000 -52.27294900
        #
        # output_file = open(LINK_FILE, "w+")
        # output_file.write(data_line)
        # output_file.close()
        #
        # route_file = open(ROUTE_FILE, "w+")
        # route_file.write("")
        # route_file.close()
        #
        # # RESET ROUTE
        # # dataLine2 = "1 24 49.277415 -123.199393 49.301 -123.224 49.324253 -123.280875 49.343717 -123.291175 49.356465 -123.303191 49.368092 -123.310057 49.383740 -123.300101 49.414349 -123.288771 49.430205 -123.300101 49.440029 -123.277442 49.432885 -123.254439 49.416136 -123.255469 49.413233 -123.284652 49.426856 -123.303878 49.420826 -123.357779 49.415690 -123.406188 49.389103 -123.423354 49.375022 -123.436744 49.355347 -123.441550 49.333203 -123.444640 49.304109 -123.352286 49.300975 -123.238990 49.277415 -123.199393 49.276001 -123.200235"
        # # dataLine2 = "1 8 49.277415 -123.199393 49.283540 -123.199793 49.281948 -123.204426 49.277415 -123.199393 49.283540 -123.199793 49.280778 -123.181104 49.277415 -123.199393 49.276001 -123.200235"
        # # dataLine2 = "1 40 49.277415 -123.199393 49.302873 -123.237853 49.313058 -123.369603 49.273201 -123.726659 49.218515 -123.856435 49.177572 -123.896604 49.167696 -123.907762 49.154450 -123.915486 49.145018 -123.917203 49.143222 -123.902783 49.148611 -123.897805 49.166125 -123.917031 49.170614 -123.927846 49.175328 -123.932137 49.178133 -123.928533 49.181948 -123.924756 49.185539 -123.919263 49.182173 -123.896775 49.169828 -123.883214 49.154562 -123.873258 49.147938 -123.858838 49.145355 -123.848538 49.142323 -123.833604 49.139516 -123.807168 49.137831 -123.795323 49.136904 -123.789401 49.133338 -123.779616 49.130362 -123.770862 49.120757 -123.736100 49.125082 -123.722711 49.128115 -123.715930 49.128958 -123.703485 49.128452 -123.689151 49.121656 -123.681684 49.126824 -123.507104 49.268609 -123.431573 49.306231 -123.248925 49.288319 -123.207726 49.277415 -123.199393 49.276001 -123.200235"
        # dataLine2 = "1 11 49.676614 -123.178798 49.666394 -123.202488 49.662616 -123.228237 49.648169 -123.243343 49.632383 -123.235447 49.610142 -123.236133 49.591228 -123.242656 49.573198 -123.258793 49.567186 -123.321621 49.560506 -123.261196 49.586554 -123.247463"
        # outputFile2 = open(ROUTE_FILE, "w+")
        # outputFile2.write(dataLine2)
        # outputFile2.close()

        if self.verbose:
            # Debug printer
            print "===================="
            print "   Resetting Data   "
            print "===================="

    def send_data_to_ui(self):
        if self.dataTimer <= 0:
            # payload = {'b_i': 'test', 's': 'testing', 'lat': self.currentData['latitude'], 'lon': self.currentData['longitude'], 'w_a': self.currentData['awa'], 'w_s': self.currentData['windSpeed'], 'cond': 'unknown', 'hog': self.currentData['hog'], 'sog': self.currentData['sog'], 'p_p': '49.277415 -123.199393,49.301 -123.224,49.324253 -123.280875,49.343717 -123.291175,49.356465 -123.303191,49.368092 -123.310057,49.383740 -123.300101,49.414349 -123.288771,49.430205 -123.300101,49.440029 -123.277442,49.432885 -123.254439,49.416136 -123.255469,49.413233 -123.284652,49.426856 -123.303878,49.420826 -123.357779,49.415690 -123.406188,49.389103 -123.423354,49.375022 -123.436744,49.355347 -123.441550,49.333203 -123.444640,49.304109 -123.352286,49.300975 -123.238990,49.277415 -123.199393,49.276001 -123.200235'}
            # payload = {'b_i': 'test', 's': 'testing', 'lat': self.currentData['latitude'], 'lon': self.currentData['longitude'], 'w_a': self.currentData['awa'], 'w_s': self.currentData['windSpeed'], 'cond': 'unknown', 'hog': self.currentData['hog'], 'sog': self.currentData['sog'], 'p_p': '49.277415 -123.199393,49.302873 -123.237853,49.313058 -123.369603,49.273201 -123.726659,49.218515 -123.856435,49.177572 -123.896604,49.167696 -123.907762,49.154450 -123.915486,49.145018 -123.917203,49.143222 -123.902783,49.148611 -123.897805,49.166125 -123.917031,49.170614 -123.927846,49.175328 -123.932137,49.178133 -123.928533,49.181948 -123.924756,49.185539 -123.919263,49.182173 -123.896775,49.169828 -123.883214,49.154562 -123.873258,49.147938 -123.858838,49.145355 -123.848538,49.142323 -123.833604,49.139516 -123.807168,49.137831 -123.795323,49.136904 -123.789401,49.133338 -123.779616,49.130362 -123.770862,49.120757 -123.736100,49.125082 -123.722711,49.128115 -123.715930,49.128958 -123.703485,49.128452 -123.689151,49.121656 -123.681684,49.126824 -123.507104,49.268609 -123.431573,49.306231 -123.248925,49.288319 -123.207726,49.277415 -123.199393,49.276001 -123.200235'}
            payload = dict(b_i='test', s='testing', lat=self.currentData['latitude'],
                           lon=self.currentData['longitude'], w_a=self.currentData['awa'],
                           w_s=self.currentData['windSpeed'], cond='unknown', hog=self.currentData['hog'],
                           sog=self.currentData['sog'],
                           p_p='49.676614 -123.178798,49.666394 -123.202488,49.662616 -123.228237,49.648169 -123.243343,49.632383 -123.235447,49.610142 -123.236133,49.591228 -123.242656,49.573198 -123.258793,49.567186 -123.321621,49.560506 -123.261196,49.586554 -123.247463')
            r = requests.get("http://ubctransat.com:6543/api/add", params=payload)
            if self.verbose:
                # Debug printer
                print "========================"
                print "   Sending Data To UI   "
                # print r.url
                # print r.text
                print "========================"

            self.dataTimer = self.DATA_DELAY / self.CLOCK_INTERVAL
        else:
            self.dataTimer -= 1

    '''tell the ui that we are starting a new test'''
    @staticmethod
    def start_test():

        payload = {'s': 'el2d0s9k3'}

        r = requests.get("http://track.ubctransat.com/api/test/new", params=payload)

        print "========================"
        print "   Starting New Test    "
        print "========================"

