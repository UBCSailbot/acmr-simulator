from datatype import GPSCoordinate

import standardcalc
import random

class SimulatorData:
    def __init__(self, verbose, gust, data_to_ui):
        random.seed()

        self.awa = 0
        self.aws = 0
        self.awVector = standardcalc.Vector2D.zero()

        self.twa = random.randint(-180, 180)
        self.tws = float(random.randint(10, 15))
        self.twVector = standardcalc.Vector2D.zero()

        self.currentFlowAngle = random.randint(-180, 180)
        self.currentFlowSpeed = float(random.randint(1, 5))
        self.currentVector = standardcalc.Vector2D.zero()

        self.hog = 0
        self.cog = 0
        self.gps_coord = GPSCoordinate.GPSCoordinate(0, 0)
        self.sog = 0
        self.sheet_percent = 0
        self.num_sat = 0
        self.gps_accuracy = 0
        self.auto = 0
        self.rudder = 0

        self.verbose = verbose
        self.gust = gust
        self.dataToUI = data_to_ui

        self.gustTimer = 0
        self.dataTimer = 0
        self.preGustTrueWindSpeed = 0
        self.preGustTrueWindAngle = 0

        #adding other BoatData variables 4 Feb 2016 by Lawrence Garcia
        random.seed()
        self.currentData = {'latitude': 0, 'longitude': 0, 'hog': 0, 'cog': 0, 'awa': 0, 'sog': 0, 'windSpeed': 0,
                            'rudderAngle': 0, 'sheetPercentage': 0}
        self.oldData = self.currentData.copy()
        # Choose Random Wind Angle between -180 and 180
        self.trueWindAngle =
        self.trueWindSpeed =
        self.currentFlowAngle =
        self.currentFlowSpeed =



        self.boatData = BoatData.BoatData()
