import random
import math

EARTH_RADIUS = 6371000

# Sheet Percentage Constants
IRONS_ANGLE = 45.0
PLATEAU_ANGLE_1 = 120.0
PLATEAU_ANGLE_2 = 133.0
PLATEAU_ANGLE_3 = 165.0
FALL_ANGLE = 150.0
IRON_PERCENTAGE = 95.0
PLATEAU_PERCENTAGE = 35.0
GROWTH_FACTOR = 12 / 100.0
GROWTH_FACTOR_2 = 14 / 100.0

# Look-up Table for Boat Speed Polar Diagram to SOG Values
BSPD_LUT = {-180:0.81484,-179:0.81494,-178:0.81505,-177:0.81515,-176:0.81525,
            -175:0.81536,-174:0.81546,-173:0.81556,-172:0.81567,-171:0.81577,
            -170:0.81588,-169:0.81598,-168:0.81608,-167:0.81619,-166:0.81629,
            -165:0.81639,-164:0.818,-163:0.8196,-162:0.82121,-161:0.82282,
            -160:0.82442,-159:0.82603,-158:0.82763,-157:0.82924,-156:0.83085,
            -155:0.83245,-154:0.83406,-153:0.83566,-152:0.83727,-151:0.83887,
            -150:0.84048,-149:0.84336,-148:0.84623,-147:0.84911,-146:0.85199,
            -145:0.85486,-144:0.85774,-143:0.86062,-142:0.8635,-141:0.86637,
            -140:0.86925,-139:0.87213,-138:0.875,-137:0.87788,-136:0.88076,
            -135:0.88363,-134:0.88685,-133:0.89007,-132:0.89329,-131:0.89651,
            -130:0.89973,-129:0.90294,-128:0.90616,-127:0.90938,-126:0.9126,
            -125:0.91582,-124:0.91903,-123:0.92225,-122:0.92547,-121:0.92869,
            -120:0.93191,-119:0.93506,-118:0.93821,-117:0.94136,-116:0.94451,
            -115:0.94766,-114:0.95082,-113:0.95397,-112:0.95712,-111:0.96027,
            -110:0.96342,-109:0.96657,-108:0.96972,-107:0.97288,-106:0.97603,
            -105:0.97918,-104:0.98057,-103:0.98195,-102:0.98334,-101:0.98473,
            -100:0.98612,-99:0.98751,-98:0.9889,-97:0.99028,-96:0.99167,
            -95:0.99306,-94:0.99445,-93:0.99584,-92:0.99722,-91:0.99861,
            -90:1,-89:0.99929,-88:0.99858,-87:0.99787,-86:0.99716,
            -85:0.99645,-84:0.99574,-83:0.99503,-82:0.99432,-81:0.99361,
            -80:0.9929,-79:0.99219,-78:0.99148,-77:0.99077,-76:0.99006,
            -75:0.98935,-74:0.98599,-73:0.98264,-72:0.97928,-71:0.97593,
            -70:0.97257,-69:0.96921,-68:0.96586,-67:0.9625,-66:0.95915,
            -65:0.95579,-64:0.95243,-63:0.94908,-62:0.94572,-61:0.94236,
            -60:0.93901,-59:0.93199,-58:0.92497,-57:0.91795,-56:0.91093,
            -55:0.90391,-54:0.89689,-53:0.88987,-52:0.88285,-51:0.87583,
            -50:0.86881,-49:0.86179,-48:0.85477,-47:0.84775,-46:0.84073,
            -45:0.83371,-44:0.82042,-43:0.80714,-42:0.79386,-41:0.78057,
            -40:0.76729,-39:0.75401,-38:0.74072,-37:0.72744,-36:0.71415,
            -35:0.70087,-34:0.68759,-33:0.6743,-32:0.66102,-31:0.64774,
            -30:0.63445,-29:0.59216,-28:0.54986,-27:0.50756,-26:0.46526,
            -25:0.42297,-24:0.38067,-23:0.33837,-22:0.29608,-21:0.25378,
            -20:0.21148,-19:0.16919,-18:0.12689,-17:0.084594,-16:0.042297,
            -15:0,-14:0,-13:0,-12:0,-11:0,
            -10:0,-9:0,-8:0,-7:0,-6:0,
            -5:0,-4:0,-3:0,-2:0,-1:0,
            0:0,1:0,2:0,3:0,4:0,
            5:0,6:0,7:0,8:0,9:0,
            10:0,11:0,12:0,13:0,14:0,
            15:0,16:0.042297,17:0.084594,18:0.12689,19:0.16919,
            20:0.21148,21:0.25378,22:0.29608,23:0.33837,24:0.38067,
            25:0.42297,26:0.46526,27:0.50756,28:0.54986,29:0.59216,
            30:0.63445,31:0.64774,32:0.66102,33:0.6743,34:0.68759,
            35:0.70087,36:0.71415,37:0.72744,38:0.74072,39:0.75401,
            40:0.76729,41:0.78057,42:0.79386,43:0.80714,44:0.82042,
            45:0.83371,46:0.84073,47:0.84775,48:0.85477,49:0.86179,
            50:0.86881,51:0.87583,52:0.88285,53:0.88987,54:0.89689,
            55:0.90391,56:0.91093,57:0.91795,58:0.92497,59:0.93199,
            60:0.93901,61:0.94236,62:0.94572,63:0.94908,64:0.95243,
            65:0.95579,66:0.95915,67:0.9625,68:0.96586,69:0.96921,
            70:0.97257,71:0.97593,72:0.97928,73:0.98264,74:0.98599,
            75:0.98935,76:0.99006,77:0.99077,78:0.99148,79:0.99219,
            80:0.9929,81:0.99361,82:0.99432,83:0.99503,84:0.99574,
            85:0.99645,86:0.99716,87:0.99787,88:0.99858,89:0.99929,
            90:1,91:0.99861,92:0.99722,93:0.99584,94:0.99445,
            95:0.99306,96:0.99167,97:0.99028,98:0.9889,99:0.98751,
            100:0.98612,101:0.98473,102:0.98334,103:0.98195,104:0.98057,
            105:0.97918,106:0.97603,107:0.97288,108:0.96972,109:0.96657,
            110:0.96342,111:0.96027,112:0.95712,113:0.95397,114:0.95082,
            115:0.94766,116:0.94451,117:0.94136,118:0.93821,119:0.93506,
            120:0.93191,121:0.92869,122:0.92547,123:0.92225,124:0.91903,
            125:0.91582,126:0.9126,127:0.90938,128:0.90616,129:0.90294,
            130:0.89973,131:0.89651,132:0.89329,133:0.89007,134:0.88685,
            135:0.88363,136:0.88076,137:0.87788,138:0.875,139:0.87213,
            140:0.86925,141:0.86637,142:0.8635,143:0.86062,144:0.85774,
            145:0.85486,146:0.85199,147:0.84911,148:0.84623,149:0.84336,
            150:0.84048,151:0.83887,152:0.83727,153:0.83566,154:0.83406,
            155:0.83245,156:0.83085,157:0.82924,158:0.82763,159:0.82603,
            160:0.82442,161:0.82282,162:0.82121,163:0.8196,164:0.818,
            165:0.81639,166:0.81629,167:0.81619,168:0.81608,169:0.81598,
            170:0.81588,171:0.81577,172:0.81567,173:0.81556,174:0.81546,
            175:0.81536,176:0.81525,177:0.81515,178:0.81505,179:0.81494,
            180:0.81484}

def generate_bell_curve(max):
    """Creates a Bell Curve from -max to max, centre at 0"""

    output = 0

    # adds six dice up generate bell curve from 0 to max*2
    for i in range(0, 6):
        output += random.uniform(0, max / 3.0)

    # centers distribution around 0
    output -= max

    return output


# Bounds angle to -180 to 180
def bound_to_180(angle):
    if angle < 0:
        angle %= -360
    else:
        angle %= 360

    if angle <= -180:
        return angle + 360
    elif angle > 180:
        return angle - 360
    else:
        return angle


def shift_coordinates(old_latitude, old_longitude, displacement):
    """displacement is a Vector2D"""
    latitude = math.degrees(
        math.asin(math.sin(math.radians(old_latitude)) * math.cos(displacement.length() / EARTH_RADIUS) +
                  math.cos(math.radians(old_latitude)) * math.sin(displacement.length() / EARTH_RADIUS) * math.cos(
                      math.radians(displacement.angle()))))
    longitude = math.degrees(math.radians(old_longitude) + \
                             math.atan2(math.sin(math.radians(displacement.angle())) * math.sin(
                                 displacement.length() / EARTH_RADIUS) * math.cos(math.radians(old_latitude)),
                                        math.cos(displacement.length() / EARTH_RADIUS) - math.sin(
                                            math.radians(old_latitude)) * math.sin(math.radians(latitude))))
    return latitude, longitude


# This is the python equivalent of the getSheetSettings function in the MCU
# for wolfram: plot Piecewise[{{45x^(1/100),0<x<=45},{x*(12/100)^(x/75)/(12/100), 45<x<=120},{x*(14/100)^(x/75)/(14/100)
# , 120<x<=133},{30-(x/10-13.3),133<x<=150},{13, 150<x<=180}}], 0<=x<=180
def calculate_ideal_sheet_percentage(awa):
    ideal_sheet_percent = 0
    awa = abs(awa)

    if awa == 0:
        ideal_sheet_percent = IRON_PERCENTAGE
    elif awa <= IRONS_ANGLE:
        ideal_sheet_percent = IRON_PERCENTAGE * math.pow(awa, 1 / 100.0)
    elif awa <= PLATEAU_ANGLE_1:
        ideal_sheet_percent = awa * math.pow(GROWTH_FACTOR, awa / 75.0) / GROWTH_FACTOR
    elif awa <= PLATEAU_ANGLE_2:
        ideal_sheet_percent = awa * math.pow(GROWTH_FACTOR_2, awa / 75.0) / GROWTH_FACTOR_2
    elif awa <= FALL_ANGLE:
        ideal_sheet_percent = 30.0 - (awa / 10.0 - 133 / 10.0)
    elif awa <= PLATEAU_ANGLE_3:
        ideal_sheet_percent = 28.0
        for i in range(0, int(PLATEAU_ANGLE_3 - FALL_ANGLE)):
            ideal_sheet_percent -= 1.0
    elif awa < 180:
        ideal_sheet_percent = 13.0

    return float(ideal_sheet_percent)


def calculate_error_coefficient(awa, sheet_percentage):
    # when error is 0, coefficient is 1, but drops off as error gets larger than 10
    error = abs(sheet_percentage - calculate_ideal_sheet_percentage(awa))
    error_coefficient = -1.4 / math.pi * math.atan(math.pi * error / 50 - math.pi / 2) + math.pi / 8 + 0.1
    return error_coefficient

#Returns the normalized boat speed for a given apparent wind_speed and awa from the BSPD
def calculate_sog_BSPD(awa, wind_speed):
    sog = wind_speed * BSPD_LUT[round(awa)]
    return sog

# Returns maximum velocity at current apparent wind_speed and awa
def calculate_max_sog(awa, wind_speed):
    awa = abs(awa)
    v1 = 12 / (1 + math.pow(math.e, -(wind_speed * 0.6 - 5.5)))

    if awa < 45:
        v2 = 0.00015 * math.pow(awa, 2) + 0.5
    elif awa < 115:
        v2 = -0.000163265306122 * math.pow(awa, 2) + 0.0261224489796 * awa - 0.0448979591837
    elif awa <= 180:
        v2 = 0.000025641025641 * math.pow(awa, 2) - 0.0137179487179 * awa + 2.03846153846
    else:
        raise Exception

    return v1 * v2


class Vector2D():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Vector2D(x, y)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Vector2D(x, y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __eq__(self, other):
        if isinstance(other, Vector2D):
            return (self.x == other.x) and (self.y == other.y)
        elif isinstance(other, list):
            return (self.x == other[0]) and (self.y == other[1])
        else:
            return False

    def __neg__(self):
        return Vector2D(-self.x, -self.y)

    # Scalar operations, other must be a scalar
    def __mul__(self, other):
        return Vector2D(other * self.x, other * self.y)

    def __div__(self, other):
        return Vector2D(self.x.__truediv__(other), self.y.__truediv__(other))

    def __rmul__(self, other):
        return Vector2D(other * self.x, other * self.y)

    def __str__(self):
        return str([self.x, self.y])

    def __repr__(self):
        return str([self.x, self.y])

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def angle(self):
        """
        Returns the angle, measured as 0 degrees from North,
        up to -180 (on the left) to +180 (on the right).
        """

        if self.x == 0:
            return 0 if self.y > 0 else 180

        if self.y == 0:
            return 90 if self.x > 0 else -90

        angle = 180.0 * (math.atan(self.x.__truediv__(self.y))) / math.pi

        if self.y > 0:
            return angle
        elif self.x > 0:
            return 180 + angle
        elif self.x < 0:
            return -180 + angle
        else:
            raise Exception


    @staticmethod
    def create_from_angle(angle, length):
        """
        Creates a vector according to the angle and length of the vector.
        Angle: an angle in degrees, where the angle is measured from 0 at North,
        and angle goes from -180 (on the left) to +180 (on the right).
        Length: must be a scalar number
        """
        # convert to radians
        angle = (angle * math.pi) / 180.0
        x = length * math.sin(angle)
        y = length * math.cos(angle)
        return Vector2D(x, y)

    @staticmethod
    def zero():
        return Vector2D(0, 0)

    @staticmethod
    def dot(v1, v2):
        """
        Calculates the vector scalar product (dot product) of v1 and v2.
        :param v1: Vector V1
        :param v2: Vector V2
        :return: Dot Product of the Vectors
        """
        return v1.x * v2.x + v1.y * v2.y

    @staticmethod
    def angle_between(v1, v2):
        """
        Finds the angle of v2 w.r.t to v1.
        :param v1: Reference vector to measure angle to
        :param v2: Vector to measure angle of w.r.t v1
        :return: Angle between the two vectors, where 0 means they point in the same direction
        -90 means v2 points to the west of v1, etc. 0 is returned if either is a zero vector.
        Modified by L.Garcia 15 March 2016: If either is a zero vector, the angle of the other is returned.
        If both are zero vectors, 0 is returned.
        """
        if v1 == Vector2D.zero() and v2 == Vector2D.zero():
            return 0
        elif v1 == Vector2D.zero():
            return -v2.angle()
        elif v2 == Vector2D.zero():
            return v1.angle()

        # Use dot product to find angle
        angle = math.degrees(math.acos(Vector2D.dot(v1, v2) / (v1.length() * v2.length())))

        v1_angle = v1.angle()
        v2_angle = v2.angle()

        if v1_angle >= 0:
            if v2_angle < v1_angle:
                return -angle if v2_angle > v1_angle - 180 else angle
            else:
                return angle
        else:
            if v2_angle > v1_angle:
                return angle if v2_angle < v1_angle + 180 else -angle
            else:
                return -angle


