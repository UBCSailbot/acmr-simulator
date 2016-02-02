import math

EARTH_RADIUS = 6378140.0

class GPSCoordinate:
	"""
	This class will be a python representation of GPS coordinates
	i.e. with a latitude/longitude.
	"""
	def __init__(self, latitude=0, longitude=0):
		self.lat = latitude
		self.long = longitude

	def __repr__(self):
		return str("GPSCoordinate(latitude={lat}, longitude={long})".format(lat=self.lat, long=self.long))

	def __str__(self):
		return str("{lat}, {long}".format(lat=self.lat, long=self.long))

	def __eq__(self, other):
		return (self.lat == other.lat and self.long == other.long)

	def CartesianCoords(self):
		"""Returns the Cartesian Coordinate Equivalent of the GPS coord"""
		x = EARTH_RADIUS*math.cos(math.radians(self.lat))*self.long*math.pi/180.0
		y = EARTH_RADIUS*self.lat*math.pi/180.0
		return x, y

	def createCoordDistAway(self, xDist, yDist):
		result = GPSCoordinate()
		result.long = self.long + (180.0 / math.pi) * (float(xDist) / EARTH_RADIUS) / math.cos(math.radians(self.lat))
		result.lat = self.lat + (180.0 / math.pi) * (float(yDist) / EARTH_RADIUS)
		return result


if (__name__ == "__main__"):
	print "GPSCoordinate.py"