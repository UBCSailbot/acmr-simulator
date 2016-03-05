from datatype import GPSCoordinate


class BoatData:
    def __init__(self):
        self.awa = 0
        self.windspeed = 0
        self.hog = 0
        self.cog = 0
        self.gps_coord = GPSCoordinate.GPSCoordinate(0, 0)
        self.sog = 0
        # self.sheet_percent = 0
        self.num_sat = 0
        self.gps_accuracy = 0
        self.auto = 0
        self.rudder = 0
        self.sow = 0
        self.wingAngle = 0
        self.tailAngle = 0

    def __repr__(self):
        return (
        'AWA:{awa}, WSPD:{wspd}, HOG:{hog}, COG:{cog}, SOG:{sog}, LAT:{lat}, LONG:{long}, Sat#:{numsat}, Auto:{auto}, '
        'Rudder:{rudder}, WingAngle:{wingAngle}, TailAngle:{tailAngle}, SOW:{sow}'.format(awa=self.awa, wspd=self.windspeed,
                                                  hog=self.hog, cog=self.cog, sog=self.sog,
                                                  lat=self.gps_coord.lat, long=self.gps_coord.long,
                                                  numsat=self.num_sat, auto=self.auto,
                                                  rudder=self.rudder, wingAngle=self.wingAngle,
                                                  tailAngle=self.tailAngle, sow=self.sow))