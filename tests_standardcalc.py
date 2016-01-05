"""Tests to cover the sensors.py file"""

import unittest
import standardcalc
import math

class TestVector2D(unittest.TestCase):
	def setUp(self):
		# Vectors in each quadrant
		# Q1 is top right: x>0, y>0, and goes counter clockwise
		self.vectorQ1 = standardcalc.Vector2D(3, 4)
		self.vectorQ2 = standardcalc.Vector2D(-3, 4)
		self.vectorQ3 = standardcalc.Vector2D(-1, -1)
		self.vectorQ4 = standardcalc.Vector2D(6, -8)
		self.vectors = [self.vectorQ1, self.vectorQ2, self.vectorQ3, self.vectorQ4]

	def testAdditionToZero(self):
		for vector in self.vectors:
			actual = vector + standardcalc.Vector2D.zero()
			expected = vector
			self.assertEqual(actual, expected)

	def testAddition(self):
		actual = self.vectorQ1 + self.vectorQ2
		expected = standardcalc.Vector2D(0, 8)
		self.assertEqual(actual, expected)

	def testAdditionToSelf(self):
		actual = standardcalc.Vector2D.zero()
		actual += self.vectorQ1
		expected = standardcalc.Vector2D(3, 4)
		self.assertEqual(actual, expected)

	def testSubtraction(self):
		actual = self.vectorQ1 - self.vectorQ2
		expected = standardcalc.Vector2D(6, 0)
		self.assertEqual(actual, expected)

	def testSubtractionToSelf(self):
		actual = standardcalc.Vector2D.zero()
		actual -= self.vectorQ1
		expected = standardcalc.Vector2D(-3, -4)
		self.assertEqual(actual, expected)

	def testScalarMultiplication(self):
		actual = self.vectorQ1 * 2
		expected = standardcalc.Vector2D(6, 8)
		self.assertEqual(actual, expected)

		actual = 2 * self.vectorQ1
		self.assertEqual(actual, expected)

	def testScalarDivision(self):
		actual = self.vectorQ1 / 2
		expected = standardcalc.Vector2D(1.5, 2)
		self.assertEqual(actual, expected)

	def testAngles(self):
		north = standardcalc.Vector2D(0, 1)
		south = standardcalc.Vector2D(0, -1)
		west = standardcalc.Vector2D(-1, 0)
		east = standardcalc.Vector2D(1, 0)
		northeast = standardcalc.Vector2D(1, 1)
		northwest = standardcalc.Vector2D(-1, 1)
		southeast = standardcalc.Vector2D(1, -1)
		southwest = standardcalc.Vector2D(-1, -1)

		specialTriangle = standardcalc.Vector2D.create_from_angle(30, 2)

		self.assertEqual(north.angle(), 0)
		self.assertEqual(south.angle(), 180)
		self.assertEqual(west.angle(), -90)
		self.assertEqual(east.angle(), 90)

		self.assertEqual(northeast.angle(), 45)
		self.assertEqual(northwest.angle(), -45)
		self.assertEqual(southeast.angle(), 135)
		self.assertEqual(southwest.angle(), -135)

		self.assertAlmostEqual(specialTriangle.angle(), 30, delta=0.1)


	def testAngleBetween(self):
		north = standardcalc.Vector2D(0, 1)
		south = standardcalc.Vector2D(0, -1)
		west = standardcalc.Vector2D(-1, 0)
		east = standardcalc.Vector2D(1, 0)
		northeast = standardcalc.Vector2D(1, 1)
		northwest = standardcalc.Vector2D(-1, 1)
		southeast = standardcalc.Vector2D(1, -1)
		southwest = standardcalc.Vector2D(-1, -1)

		self.assertAlmostEqual(standardcalc.Vector2D.angle_between(north, south), 180)
		self.assertAlmostEqual(standardcalc.Vector2D.angle_between(east, west), 180)
		self.assertAlmostEqual(standardcalc.Vector2D.angle_between(north, east), 90)
		self.assertAlmostEqual(standardcalc.Vector2D.angle_between(north, west), -90)
		self.assertAlmostEqual(standardcalc.Vector2D.angle_between(southeast, south), 45)
		self.assertAlmostEqual(standardcalc.Vector2D.angle_between(southeast, northeast), -90)
		self.assertAlmostEqual(standardcalc.Vector2D.angle_between(southeast, northwest), 180, places=5)
		self.assertAlmostEqual(standardcalc.Vector2D.angle_between(southeast, west), 135)
		self.assertAlmostEqual(standardcalc.Vector2D.angle_between(southwest, north), 135)
		self.assertAlmostEqual(standardcalc.Vector2D.angle_between(southwest, southeast), -90)
		self.assertAlmostEqual(standardcalc.Vector2D.angle_between(southwest, west), 45)
		self.assertAlmostEqual(standardcalc.Vector2D.angle_between(southwest, southwest), 0, 5)


	def testCreateFromAngle(self):
		specialTriangle30 = standardcalc.Vector2D.create_from_angle(30, 2)
		specialTriangle60 = standardcalc.Vector2D.create_from_angle(60, 2)
		specialTriangle45 = standardcalc.Vector2D.create_from_angle(45, math.sqrt(2))

		self.assertAlmostEqual(specialTriangle30.x, 1)
		self.assertAlmostEqual(specialTriangle30.y, math.sqrt(3))

		self.assertAlmostEqual(specialTriangle60.x, math.sqrt(3))
		self.assertAlmostEqual(specialTriangle60.y, 1)

		self.assertAlmostEqual(specialTriangle45.x, 1)
		self.assertAlmostEqual(specialTriangle45.y, 1)


	# Also checks for immutability
	def tearDown(self):
		self.assertTrue(self.vectorQ1 == standardcalc.Vector2D(3, 4))
		self.assertTrue(self.vectorQ2 == standardcalc.Vector2D(-3, 4))
		self.assertTrue(self.vectorQ3 == standardcalc.Vector2D(-1, -1))
		self.assertTrue(self.vectorQ4 == standardcalc.Vector2D(6, -8))
		self.assertTrue(self.vectorQ1 == [3, 4])
		self.assertTrue(self.vectorQ2 == [-3, 4])
		self.assertTrue(self.vectorQ3 == [-1, -1])
		self.assertTrue(self.vectorQ4 == [6, -8])

class TestBoundto180(unittest.TestCase):
	def setUp(self):
		self.num1 = 5
		self.num1bounded = 5
		self.num2 = 200
		self.num2bounded = -160
		self.num3 = -200
		self.num3bounded = 160
		self.num4 = 890
		self.num4bounded = 170
		self.num5 = 920
		self.num5bounded = -160
		self.num6 = -890
		self.num6bounded = -170
		self.num7 = -920
		self.num7bounded = 160

	def testNoChange(self):
		self.assertEqual(standardcalc.bound_to_180(self.num1), self.num1bounded)

	def testGreaterThan180(self):
		self.assertEqual(standardcalc.bound_to_180(self.num2), self.num2bounded)

	def testLessThan180(self):
		self.assertEqual(standardcalc.bound_to_180(self.num3), self.num3bounded)

	def testGreaterThan360ToPositive(self):
		self.assertEqual(standardcalc.bound_to_180(self.num4), self.num4bounded)

	def testGreaterThan360ToNegative(self):
		self.assertEqual(standardcalc.bound_to_180(self.num5), self.num5bounded)

	def testLessThan360ToNegative(self):
		self.assertEqual(standardcalc.bound_to_180(self.num6), self.num6bounded)

	def testLessThan360ToPositive(self):
		self.assertEqual(standardcalc.bound_to_180(self.num7), self.num7bounded)


class TestCalculations(unittest.TestCase):
	def testShiftCoordinates(self):
		displacement = standardcalc.Vector2D.create_from_angle(30, 1000000)
		latitude, longitude = standardcalc.shift_coordinates(53.0, 40.0, displacement)
		self.assertAlmostEqual(latitude, 60.5, delta=0.2)
		self.assertAlmostEqual(longitude, 49.1, delta=0.2)

# class TestCalculateIdealSheetPercentage(unittest.TestCase):
#     def testSeries(self):
#         self.assertAlmostEqual(standardcalc.calculateIdealSheetPercentage(0), 95, delta=3)
#         self.assertAlmostEqual(standardcalc.calculateIdealSheetPercentage(16), 95, delta=3)
#         self.assertAlmostEqual(standardcalc.calculateIdealSheetPercentage(52), 92, delta=3)
#         self.assertAlmostEqual(standardcalc.calculateIdealSheetPercentage(79), 69, delta=3)
#         self.assertAlmostEqual(standardcalc.calculateIdealSheetPercentage(102), 48, delta=3)
#         self.assertAlmostEqual(standardcalc.calculateIdealSheetPercentage(134), 30, delta=3)
#         self.assertAlmostEqual(standardcalc.calculateIdealSheetPercentage(151), 27, delta=3)
#         self.assertAlmostEqual(standardcalc.calculateIdealSheetPercentage(161), 18, delta=3)
#         self.assertAlmostEqual(standardcalc.calculateIdealSheetPercentage(180), 13, delta=3)
#
#
