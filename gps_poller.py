#! /usr/bin/python

import os
from gps import *
from time import *
import time
import threading

class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.__gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
        self.__stop = threading.Event()
        locations = list()
   
    def run(self):
        while not self.stopped():
            self.__gpsd.next() #grab EACH set of gpsd info to clear the buffer
            if self.__gpsd.satellites:
                if len(locations) >= 30:
                    locations.pop(0)
                locations.append[self.__gpsd.fix.latitude, self.__gpsd.fix.longitude]
            time.sleep(0.1) #set to whatever, 10 Hz

    def stop(self):
        self.__stop.set()

    def stopped(self):
        return self.__stop.isSet()

    def get_location(self):
        if self.__gpsd.satellites:
            sum_lat = 0
            sum_long = 0
            for location in locations:
                sum_lat = sum_lat + location[0]
                sum_long = sum_long + location[1]

            return [sum_lat/len(locations), sum_long/len(locations)]
            
    def get_timestamp(self):
        return self.__gpsd.fix.time
