import math
import navigation as nav

class GPS:

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def get_latitude_radians(self):
        return math.radians(self.latitude)

    def get_longitude_radians(self):
        return math.radians(self.longitude)

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp
