"""Tests to cover the simulator.py file"""

import unittest
import standardcalc
import simulator


class TestAdjustSOG(unittest.TestCase):
    def setUp(self):
        self.hardware = simulator.Simulator(False, False, False, False)
        self.set_current_data_to_zero()
        self.hardware.currentData['awa'] = 30
        self.hardware.currentData['sheetPercentage'] = 20
        self.hardware.currentData['windSpeed'] = 15

    def test_wind_speed_zero(self):
        self.hardware.currentData['windSpeed'] = 0
        self.hardware.adjust_sog()
        self.assertEqual(self.hardware.currentData['sog'], 0)

    def test_wind_speed_high(self):
        # Test matters more for high sheet percentages. As this is the condition that will make the new sailing speed
        # model max out quickly
        self.hardware.currentData['sheetPercentage'] = 100

        self.hardware.currentData['sog'] = 0
        self.hardware.currentData['windSpeed'] = 5
        self.hardware.adjust_sog()
        sog5 = self.hardware.currentData['sog']

        self.hardware.currentData['sog'] = 0
        self.hardware.currentData['windSpeed'] = 20
        self.hardware.adjust_sog()
        sog20 = self.hardware.currentData['sog']

        self.hardware.currentData['sog'] = 0
        self.hardware.currentData['windSpeed'] = 50
        self.hardware.adjust_sog()
        sog50 = self.hardware.currentData['sog']

        self.hardware.currentData['sog'] = 0
        self.hardware.currentData['windSpeed'] = 100
        self.hardware.adjust_sog()
        sog100 = self.hardware.currentData['sog']

        self.assertNotEqual(sog5, sog20)
        self.assertAlmostEqual(sog20, sog50, delta=0.1)
        self.assertAlmostEqual(sog50, sog100, delta=0.01)

    def test_awa_is_in_irons(self):
        self.hardware.currentData['awa'] = 0
        self.hardware.adjust_sog()
        self.assertAlmostEqual(self.hardware.currentData['sog'], 0, delta=0.05)

        # self.hardware.currentData['awa'] = 40
        # self.hardware.adjust_sog()
        # self.assertAlmostEqual(self.hardware.currentData['sog'], 0, delta=0.5)
        #
        # self.hardware.currentData['awa'] = -40
        # self.hardware.adjust_sog()
        # self.assertAlmostEqual(self.hardware.currentData['sog'], 0, delta=0.5)

    def test_awa_point_of_sails(self):
        # Close reach
        self.hardware.currentData['sog'] = 0
        self.set_ideal_settings_for(60)
        self.hardware.adjust_sog()
        close_reach_speed = self.hardware.currentData['sog']

        # Beam reach
        self.hardware.currentData['sog'] = 0
        self.set_ideal_settings_for(90)
        self.hardware.adjust_sog()
        beam_reach_speed = self.hardware.currentData['sog']

        # Broad reach
        self.hardware.currentData['sog'] = 0
        self.set_ideal_settings_for(120)
        self.hardware.adjust_sog()
        broad_reach_speed = self.hardware.currentData['sog']

        # Running
        self.hardware.currentData['sog'] = 0
        self.set_ideal_settings_for(180)
        self.hardware.adjust_sog()
        running_speed = self.hardware.currentData['sog']

        # If boat is sailing ideally, then beam reach should be fastest
        self.assertLess(close_reach_speed, beam_reach_speed)
        self.assertLess(broad_reach_speed, beam_reach_speed)

    def test_sheet_settings_effects(self):
        # Close Reach
        self.verify_sheet_settings_effects_for(60)

        # Beam Reach
        self.verify_sheet_settings_effects_for(90)

        # Broad Reach
        self.verify_sheet_settings_effects_for(120)

        # Running
        self.verify_sheet_settings_effects_for(180)

    def verify_sheet_settings_effects_for(self, awa):
        # Basically tests that the calculated Ideal Sheet Percentage produces the maximum speed

        self.hardware.currentData['awa'] = awa
        ideal_sheet_settings = standardcalc.calculate_ideal_sheet_percentage(awa)
        # max_sog = standardcalc.calculateMaxSOG(awa, self.hardware.currentData['windSpeed'])

        # Ideal Settings
        self.hardware.currentData['sog'] = 5
        self.hardware.currentData['sheetPercentage'] = ideal_sheet_settings
        self.hardware.adjust_sog()
        ideal_sog = self.hardware.currentData['sog']

        # Too low sheet %
        self.hardware.currentData['sog'] = 5
        self.hardware.currentData['sheetPercentage'] = ideal_sheet_settings - 10
        self.hardware.adjust_sog()
        less_than_ideal_sog = self.hardware.currentData['sog']

        # Too high sheet %
        self.hardware.currentData['sog'] = 5
        self.hardware.currentData['sheetPercentage'] = ideal_sheet_settings + 10
        self.hardware.adjust_sog()
        over_ideal_sog = self.hardware.currentData['sog']

        self.assertLessEqual(less_than_ideal_sog, ideal_sog)
        self.assertLessEqual(ideal_sog, over_ideal_sog)

    def set_ideal_settings_for(self, awa):
        self.hardware.currentData['awa'] = awa
        self.hardware.currentData['sheetPercentage'] = 50

    def set_current_data_to_zero(self):
        for key in self.hardware.currentData.keys():
            self.hardware.currentData[key] = 0

class TestAdjustHOG(unittest.TestCase):
    def setUp(self):
        self.hardware = simulator.Simulator(False, False, False, False)
        self.set_current_data_to_zero()
        self.hardware.currentData['sog'] = 10
        self.hardware.currentData['hog'] = 0

    def test_sog_zero(self):
        self.hardware.currentData['sog'] = 0
        self.hardware.currentData['rudderAngle'] = 0
        self.hardware.adjust_hog()
        self.assertEqual(self.hardware.currentData['hog'], 0)

        self.hardware.currentData['rudderAngle'] = 10
        self.hardware.adjust_hog()
        self.assertEqual(self.hardware.currentData['hog'], 0)

        self.hardware.currentData['rudderAngle'] = 40
        self.hardware.adjust_hog()
        self.assertEqual(self.hardware.currentData['hog'], 0)

    def test_series(self):
        self.hardware.currentData['hog'] = 0
        self.hardware.currentData['sog'] = 2.5
        self.hardware.currentData['rudderAngle'] = 10
        self.hardware.adjust_hog()
        self.assertAlmostEqual(self.hardware.currentData['hog'], 0.4341 / self.hardware.L_CENTERBOARD_TO_RUDDER
                               * self.hardware.TIME_SCALE , delta=0.05)

        self.hardware.currentData['hog'] = 0
        self.hardware.currentData['sog'] = 2.5
        self.hardware.currentData['rudderAngle'] = 40
        self.hardware.adjust_hog()
        self.assertAlmostEqual(self.hardware.currentData['hog'], 1.607 / self.hardware.L_CENTERBOARD_TO_RUDDER
                               * self.hardware.TIME_SCALE , delta=0.05)

        self.hardware.currentData['hog'] = 150
        self.hardware.currentData['sog'] = 8
        self.hardware.currentData['rudderAngle'] = 20
        self.hardware.adjust_hog()
        self.assertAlmostEqual(self.hardware.currentData['hog'], 150 + 2.736 / self.hardware.L_CENTERBOARD_TO_RUDDER
                               * self.hardware.TIME_SCALE , delta=0.05)

        self.hardware.currentData['hog'] = 150
        self.hardware.currentData['sog'] = 8
        self.hardware.currentData['rudderAngle'] = -30
        self.hardware.adjust_hog()
        self.assertAlmostEqual(self.hardware.currentData['hog'], 150 + 4 / self.hardware.L_CENTERBOARD_TO_RUDDER
                               * self.hardware.TIME_SCALE , delta=0.05)

        self.hardware.currentData['hog'] = -100
        self.hardware.currentData['sog'] = 8
        self.hardware.currentData['rudderAngle'] = 40
        self.hardware.adjust_hog()
        self.assertAlmostEqual(self.hardware.currentData['hog'], -100 + 5.142 / self.hardware.L_CENTERBOARD_TO_RUDDER
                               * self.hardware.TIME_SCALE , delta=0.05)
        self.hardware.currentData['hog'] = -100
        self.hardware.currentData['sog'] = 6
        self.hardware.currentData['rudderAngle'] = -20
        self.hardware.adjust_hog()
        self.assertAlmostEqual(self.hardware.currentData['hog'], -100 + 2.052 / self.hardware.L_CENTERBOARD_TO_RUDDER
                               * self.hardware.TIME_SCALE , delta=0.05)

    def set_current_data_to_zero(self):
        for key in self.hardware.currentData.keys():
            self.hardware.currentData[key] = 0


class TestUpdateVectors(unittest.TestCase):
    def setUp(self):
        self.hardware = simulator.Simulator(False, False, False, False)
        self.set_current_data_to_zero()

    def test_zero_vectors(self):
        self.hardware.update_vectors()
        self.assertEqual(self.hardware.boatVector, standardcalc.Vector2D.zero() + self.hardware.currentFlowVector)

        self.assertAlmostEqual(self.hardware.apparentWindVector + self.hardware.currentFlowVector, self.hardware.windVector)

    def test_displacement_vectors(self):
        # Wind from the North, 0 current from north
        self.hardware.trueWindAngle = 0
        self.hardware.trueWindSpeed = 10
        self.hardware.currentFlowAngle = 0
        self.hardware.currentFlowSpeed = 0

        # Boat Heading East
        self.hardware.currentData['hog'] = 90
        self.hardware.currentData['sog'] = 10

        self.hardware.update_vectors()

        # Apparent Wind is NorthEast
        self.assertAlmostEqual(self.hardware.currentData['awa'], -45)

        # Boat Heading West
        self.hardware.currentData['hog'] = -90
        self.hardware.currentData['sog'] = 10

        self.hardware.update_vectors()

        # Apparent Wind is NorthWest
        self.assertAlmostEqual(self.hardware.currentData['awa'], 45)

        # Boat Heading Southeast
        self.hardware.currentData['hog'] = 120
        self.hardware.currentData['sog'] = 5

        self.hardware.update_vectors()

        # Apparent Wind is West
        self.assertAlmostEqual(self.hardware.currentData['awa'], -90)

        # Boat Heading South
        self.hardware.currentData['hog'] = 180
        self.hardware.currentData['sog'] = 5

        self.hardware.update_vectors()

        # Apparent Wind is South
        self.assertAlmostEqual(self.hardware.currentData['awa'], 180)

        #Current South as well
        self.hardware.currentFlowSpeed = 1 #test will fail if current speed makes boat faster than wind
        self.hardware.currentFlowAngle = 0

        self.hardware.update_vectors()

        #Apparent Wind is still South
        self.assertAlmostEqual(self.hardware.currentData['awa'], 180)

        #Current heading East, Boat Stationary
        self.hardware.currentData['sog'] = 0
        self.hardware.currentFlowSpeed = 10
        self.hardware.currentFlowAngle = 90

        self.hardware.update_vectors()

        # Apparent Wind is NorthEast
        self.assertAlmostEqual(self.hardware.currentData['awa'], -45)

        #Current heading East, Boat heading East
        self.hardware.currentData['hog'] = 90
        self.hardware.currentData['sog'] = 5
        self.hardware.currentFlowSpeed = 5

        self.hardware.update_vectors()

        # Apparent Wind is NorthEast
        self.assertAlmostEqual(self.hardware.currentData['awa'], -45)

    def set_current_data_to_zero(self):
        for key in self.hardware.currentData.keys():
            self.hardware.currentData[key] = 0


class TestAdjustPosition(unittest.TestCase):
    def setUp(self):
        self.hardware = simulator.Simulator(False, False, False, False)
        self.set_current_data_to_zero()

    def test_zero_displacement(self):
        self.hardware.currentData['sog'] = 0
        self.assertEqual(self.hardware.currentData['latitude'], 0)
        self.assertEqual(self.hardware.currentData['longitude'], 0)

        self.hardware.update_vectors()
        self.hardware.adjust_position()

        self.assertEqual(self.hardware.currentData['latitude'], 0)
        self.assertEqual(self.hardware.currentData['longitude'], 0)

    def set_current_data_to_zero(self):
        for key in self.hardware.currentData.keys():
            self.hardware.currentData[key] = 0
        self.hardware.currentFlowSpeed = 0

        # class TestAdjustPosition(unittest.TestCase):
        # def testSeries(self):
        #         cls = sensors.Hardware(0)
        #         self.currentData = dict (latitude = 0, longitude = 0)
        #         for cls.trueWindAngle in range (-180, 180, 5):
        #             for cls.trueWindSpeed in range (0, 25):
        #                 for cls.currentData['hog'] in range (-180, 180, 5):
        #                     for cls.currentData['sog'] in range (0, 12):
        #                         cls.currentData['longitude'] = 0
        #                         cls.currentData['latitude'] = 0
        #                         cls.displacement = 0
        #                         cls.updateVectors()
        #                         self.disp = cls.TIME_INTERVAL*cls.boatVelocity
        #                         cls.adjustSOG()
        #                         standardcalc.shiftCoordinates(cls.currentData['latitude'],
        #                                                       cls.currentData['longitude'],
        #                                                       self.disp)
        #                         self.assertGreaterEqual(cls.displacement, 0.0)
        #                         self.assertEqual(cls.currentData['latitude'], self.currentData['latitude'])
        #                         self.assertEqual(cls.currentData['longitude'], self.currentData['longitude'])
        #
        #
        # #this test might sometimes fail (statistically unlikely), just try running it again. If it fails twice, check the code
        # class TestGust(unittest.TestCase):
        #     def testNumber(self):
        #         count = 0
        #         cls = sensors.Hardware(0)
        #         for x in range (0,100):
        #             cls.gustTimer = 0
        #             cls.gustManager()
        #             if cls.gustTimer != 0:
        #                 count += 1
        #             self.assertLess(count, 3)
