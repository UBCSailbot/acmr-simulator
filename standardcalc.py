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
        """
        if v1 == Vector2D.zero() or v2 == Vector2D.zero():
            return 0
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


