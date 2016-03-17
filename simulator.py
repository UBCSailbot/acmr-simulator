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
from datatype import BoatData
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
    # maximum wind speed (20 knots; typical is 6 - 12 knots)
    MAX_WIND_SPEED = 10.0
    # maximum current speed (~1 knot; max current speed in English Bay: 0.75 knots)
    MAX_CURRENT_SPEED = 0.5
    # degrees of wind change
    WIND_ANGLE_FLUCTUATIONS = .2
    # amount of wind speed change
    WIND_SPEED_FLUCTUATIONS = .4
    # degrees of wind change
    CURRENT_ANGLE_FLUCTUATIONS = .05
    # amount of wind speed change
    CURRENT_SPEED_FLUCTUATIONS = .03
    # runtime for the mcu
    CLOCK_INTERVAL = 0.25  # was 0.01
    # Time scale for calculations, if equal to clock interval the simulation will run in real time.
    TIME_SCALE = CLOCK_INTERVAL
    # Change in HOG for max rudder setting in 1 meter
    MAX_RUDDER_HOG_CHANGE = 10.0
    # Max rudder angle possible (angle between -45 to 45)
    MAX_RUDDER_ANGLE = 45.0
    # This affects how fast the boat reaches the ideal SOG
    SOW_DECAY_FACTOR = (3 / CLOCK_INTERVAL)
    # How likely a gust is to occur every virtual second (Higher => Less probable)
    GUST_PROBABILITY = 100
    # Actual seconds between every time data is sent to the server
    DATA_DELAY = 0.01
    #NEW CONSTANTS
    # This is the centerboard to rudder distance L
    L_CENTERBOARD_TO_RUDDER = 0.2
    # Maximum tail angle
    MAX_TAIL_ANGLE = 15.0
    # Time constant for exponential decay of SOW
    SOW_TIME_CONSTANT = 2.0

    def __init__(self, verbose, reset, gust, data_to_ui):
        random.seed()

        # Choose Random Wind Angle between -180 and 180
        # self.trueWindAngle = random.randint(-180, 180)
        self.trueWindAngle = 30.0
        # Choose random wind speed (between typical values of 6 - 12 knots)
        self.trueWindSpeed = float(random.uniform(5, 6))

        self.windVector = standardcalc.Vector2D.zero()
        self.windVector = standardcalc.Vector2D.create_from_angle(self.trueWindAngle, self.trueWindSpeed)
        self.apparentWindVector = standardcalc.Vector2D.zero()

        self.currentFlowAngle = random.randint(-180, 180)
        self.currentFlowSpeed = 0.0
        # self.currentFlowSpeed = float(random.uniform(0.2, 0.4))
        self.currentFlowVector = standardcalc.Vector2D.zero()

        self.boatVector = standardcalc.Vector2D.zero()
        self.verbose = verbose
        self.gust = gust
        self.dataToUI = data_to_ui

        self.displacementVector = standardcalc.Vector2D.zero()
        self.gustTimer = 0
        self.dataTimer = 0
        self.preGustTrueWindSpeed = 0
        self.preGustTrueWindAngle = 0

        self.boatData = BoatData.BoatData()
        self.oldBoatData = BoatData.BoatData()
        self.oldBoatDataString = ""

    def update(self):
        self.read_data()
        self.update_old_data()
        self.adjust_true_wind()
        # self.adjust_current()
        if self.gust:
            self.gust_manager()
        self.adjust_aw()
        self.adjust_sow()
        self.adjust_hog()
        self.update_vectors()
        self.update_sailAngles()
        self.adjust_position()

        self.write_data()
        gVars.boatVars = self.boatData

    def read_data(self):

        data = gVars.bus.getData()

        self.boatData.rudder = data.rudder
        # self.boatData.rudder = 20
        # TODO: Revert once TCU implemented
        tailAngle = data.tailAngle
        tailAngle = 50
        if tailAngle > self.MAX_TAIL_ANGLE:
            self.boatData.tailAngle = self.MAX_TAIL_ANGLE
        elif tailAngle < -self.MAX_TAIL_ANGLE:
            self.boatData.tailAngle = -self.MAX_TAIL_ANGLE
        else:
            self.boatData.tailAngle = tailAngle

    def update_old_data(self):
        self.oldBoatDataString = self.boatData.__repr__()

    def adjust_true_wind(self):
        # True wind angle is allowed to fluctuate
        self.trueWindAngle += random.gauss(0, 5) * self.CLOCK_INTERVAL
        self.trueWindSpeed += random.gauss(0, 0.5) * self.CLOCK_INTERVAL
        if self.trueWindSpeed > self.MAX_WIND_SPEED:
            self.trueWindSpeed = self.MAX_WIND_SPEED
        self.trueWindAngle = standardcalc.bound_to_180(self.trueWindAngle)
        self.trueWindSpeed = abs(self.trueWindSpeed)
        self.windVector = standardcalc.Vector2D.create_from_angle(self.trueWindAngle, self.trueWindSpeed)

    def adjust_current(self):
        self.currentFlowAngle += random.gauss(0, 0.1) * self.CLOCK_INTERVAL
        self.currentFlowSpeed += random.gauss(0, 1) * 0.5 * self.CLOCK_INTERVAL
        self.currentFlowAngle = standardcalc.bound_to_180(self.currentFlowAngle)
        if self.currentFlowSpeed > self.MAX_CURRENT_SPEED:
            self.currentFlowSpeed = self.MAX_CURRENT_SPEED

        self.currentFlowSpeed = abs(self.currentFlowSpeed)
        self.currentFlowVector = standardcalc.Vector2D.create_from_angle(self.currentFlowAngle, self.currentFlowSpeed)

    def gust_manager(self):
        if self.gustTimer <= 0:
            if random.randint(1, self.GUST_PROBABILITY / self.CLOCK_INTERVAL) == 2:
                self.preGustTrueWindAngle = self.trueWindAngle
                self.preGustTrueWindSpeed = self.trueWindSpeed
                self.trueWindSpeed = random.randint(20, 30)
                self.trueWindAngle += random.randint(-5, 5)
                self.gustTimer = random.randint(5, 80) / self.CLOCK_INTERVAL
        else:
            self.gustTimer -= 1
            if self.verbose:
                print "Gust is active. Timer: " + str(self.gustTimer)
            if self.gustTimer <= 0:
                self.trueWindSpeed = abs(self.preGustTrueWindSpeed + random.randint(-2, 2))
                self.trueWindAngle = standardcalc.bound_to_180(self.preGustTrueWindAngle + random.randint(-1, 1))

    def adjust_aw(self):
        self.boatVector = standardcalc.Vector2D.create_from_angle(self.boatData.hog, self.boatData.sow) \
                          - self.currentFlowVector
        # Update COG and SOG
        self.boatData.cog = self.boatVector.angle()
        self.boatData.sog = self.boatVector.length()

        self.apparentWindVector = self.windVector - self.boatVector

        # print str(self.apparentWindVector.angle()) + " " + str(self.apparentWindVector.length())
        self.boatData.awa = standardcalc.bound_to_180(
            standardcalc.Vector2D.angle_between(self.boatVector, -self.apparentWindVector))
        self.boatData.windspeed = self.apparentWindVector.length()

    def adjust_sow(self):
        # v_b = w_a*f(phi_aw)*beta where w_a is the apparent wind speed, f(phi_aw) is the norm. BSPD and beta is
        # the control parameter setting (e.g. sheet setting)
        # sowChange = ( standardcalc.calculate_sog_BSPD( self.boatData.awa,
        #             self.boatData.windspeed) * self.boatData.sheet_percent / 100.0 ) - self.boatData.sow

        # Use tailAngle to adjust sowChange.
        # sowChange = (standardcalc.calculate_sog_BSPD(self.boatData.awa,
        #             self.boatData.windspeed) * abs(self.boatData.tailAngle / self.MAX_TAIL_ANGLE)*0.6) - self.boatData.sow


        # self.boatData.sow += ( sowChange / self.SOW_DECAY_FACTOR )*self.CLOCK_INTERVAL

        # next_sow = standardcalc.calculate_sog_BSPD(self.boatData.awa,
        #                     self.boatData.windspeed) * self.boatData.tailAngle / 100.0
        next_sow = standardcalc.calculate_sog_BSPD(self.boatData.awa,
                    self.boatData.windspeed)*0.8
        # self.boatData.sow = standardcalc.calculate_sog_BSPD(self.boatData.awa,
        #                     self.boatData.windspeed) * 50.0 / 100.0
        max_sow = standardcalc.calculate_max_sog(self.boatData.awa, self.boatData.windspeed)

        sow_change = (next_sow - self.boatData.sow)*math.exp(-self.SOW_TIME_CONSTANT*self.CLOCK_INTERVAL)

        self.boatData.sow += sow_change

        if self.boatData.sow > max_sow:
            self.boatData.sow = max_sow


    def adjust_hog(self):
        # Update HOG from rudder change
        hogChange = (self.boatData.sow * math.sin(self.boatData.rudder * math.pi / 180.0)
                     / self.L_CENTERBOARD_TO_RUDDER * self.CLOCK_INTERVAL)

        self.boatData.hog += hogChange
        self.boatData.hog = standardcalc.bound_to_180(self.boatData.hog)

    def update_vectors(self):
        pass
        # self.boatVector = standardcalc.Vector2D.create_from_angle(self.boatData.hog, self.boatData.sow)
        #                   # + self.currentFlowVector
        # # Update COG and SOG
        # self.boatData.cog = self.boatVector.angle()
        # self.boatData.sog = self.boatVector.length()
        #
        # self.apparentWindVector = self.windVector - self.boatVector
        #
        # self.boatData.awa = standardcalc.bound_to_180(
        #     standardcalc.Vector2D.angle_between(self.boatVector, -self.apparentWindVector))
        # self.boatData.windspeed = self.apparentWindVector.length()

    def update_sailAngles(self):
        # Using 2 right now, but this should be the factor relating tail Angle and angle of attack
        # wingAngle is defined in the same way as AWA, relative to the boat
        self.boatData.wingAngle = self.boatData.awa - self.boatData.tailAngle * 2

    def adjust_position(self):
        # Vector addition
        self.displacementVector = self.CLOCK_INTERVAL * standardcalc.Vector2D.create_from_angle(self.boatData.cog,
                                                                                                self.boatData.sog)

        self.boatData.gps_coord.lat, self.boatData.gps_coord.long = standardcalc.shift_coordinates(
            self.boatData.gps_coord.lat,
            self.boatData.gps_coord.long,
            self.displacementVector
        )

    def write_data(self):

        # Publish GPS and AW data to the bus.
        gVars.bus.publish("GPS", self.boatData.gps_coord.lat, self.boatData.gps_coord.long,
                          self.boatData.hog, self.boatData.sog, self.boatData.cog)
        gVars.bus.publish("AW", self.boatData.windspeed, self.boatData.awa)

        if self.verbose:
            # Debug printer
            print "===================="
            # print header_line
            # print old_data
            print self.oldBoatDataString
            print self.boatData.__repr__()


            print "\n"
            print "TRUE WIND SPEED: " + '%.8f' % self.trueWindSpeed
            print "TRUE WIND ANGLE: " + '%.8f' % self.trueWindAngle
            print "CURRENT SPEED: " + '%.8f' % self.currentFlowSpeed
            print "CURRENT ANGLE: " + '%.8f' % self.currentFlowAngle

        else:
            print self.boatData.__repr__() + ", CFS:" + str(round(self.currentFlowSpeed,2)) + \
                  ", CFA:" + str(round(self.currentFlowAngle,2))

    '''tell the ui that we are starting a new test'''
    @staticmethod
    def start_test():

        payload = {'s': 'el2d0s9k3'}

        r = requests.get("http://track.ubctransat.com/api/test/new", params=payload)

        print "========================"
        print "   Starting New Test    "
        print "========================"

