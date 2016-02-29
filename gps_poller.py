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
        self.locations = list()
   
    def run(self):
        while not self.stopped():
            self.__gpsd.next() #grab EACH set of gpsd info to clear the buffer
            if self.__gpsd.satellites:

		curr_loc = [self.__gpsd.fix.latitude, self.__gpsd.fix.longitude]
		
		if len(self.locations) == 0:
                    self.locations.append(curr_loc)
		    

		if curr_loc != self.locations[-1]:
                    if len(self.locations) >= 20:
                        self.locations.pop(0)
	            self.locations.append(curr_loc)
            time.sleep(0.01) #set to whatever, 10 Hz

    def stop(self):
        self.__stop.set()

    def stopped(self):
        return self.__stop.isSet()

    def get_location(self):
        if self.__gpsd.satellites:
            sum_lat = 0
            sum_long = 0
            for location in self.locations:
                sum_lat = sum_lat + location[0]
                sum_long = sum_long + location[1]
#	    print len(self.locations)
            return [sum_lat/len(self.locations), sum_long/len(self.locations)]
            
    def get_timestamp(self):
        return self.__gpsd.fix.time
