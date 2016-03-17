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
        'Rudder:{rudder}, WingAngle:{wingAngle}, TailAngle:{tailAngle}, SOW:{sow}'.format(awa=round(self.awa,1)
                                                , wspd=round(self.windspeed,1),
                                                  hog=round(self.hog,1), cog=round(self.cog,1), sog=round(self.sog,1),
                                                  lat=self.gps_coord.lat, long=self.gps_coord.long,
                                                  numsat=self.num_sat, auto=self.auto,
                                                  rudder=self.rudder, wingAngle=round(self.wingAngle,1),
                                                  tailAngle=self.tailAngle, sow=round(self.sow,3)))