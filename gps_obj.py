import math

class GPS:

    def __init__(self, latitude, longitude):
        self.__latitude = latitude
        self.__longitude = longitude

    def get_latitude_radians(self):
        return math.radians(self.__latitude)

    def get_longitude_radians(self):
        return math.radians(self.__longitude)
