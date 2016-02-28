#  Rough method to get most accurate gps estimation
import math

class Estimator():

    def __init__(self, Q_metres_per_sec):
        self.Q_metres_per_sec = Q_metres_per_sec
        self.min_accuracy = -1
        self.variance = -1

    def set_state(self, lat, lon, accuracy, timestamp):
        self.lat = lat
        self.long = lon
        self.variance = accuracy * accuracy
        self.timestamp = timestamp

    def get_accuracy(self):
        return math.sqrt(self.variance)  

    def k_filter(self, lat_measurement, lng_measurement, accuracy, timestamp):  
        if accuracy < self.min_accuracy:
            accuracy = self.min_accuracy

        if self.variance < 0:
            self.timestamp = timestamp
            self.lat = lat_measurement
            self.long = lng_measurement
            self.variance = accuracy * accuracy
        else:
            time_inc = self.timestamp - timestamp

            if time_inc > 0:
                self.variance += time_inc * self.Q_metres_per_second * self.Q_metres_per_second / 1000;
                self.timestamp = timestamp

            K = self.variance / (self.variance + accuracy * accuracy);
            self.lat += K * (lat_measurement - self.lat);
            self.long += K * (lng_measurement - self.long);
       
            self.variance = (1 - K) * self.variance; 
              
        





