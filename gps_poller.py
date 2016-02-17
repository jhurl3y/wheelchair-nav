#! /usr/bin/python
# Written by Dan Mandle http://dan.mandle.me September 2012
# License: GPL 2.0

import gps_obj
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
   
    def run(self):
        while not self.stopped():
            self.__gpsd.next() #grab EACH set of gpsd info to clear the buffer
            time.sleep(5) #set to whatever

    def stop(self):
        self.__stop.set()

    def stopped(self):
        return self.__stop.isSet()

    def get_location(self):
    	latitude = self.__gpsd.fix.latitude
    	longitude = self.__gpsd.fix.longitude        
    	return [latitude, longitude]
