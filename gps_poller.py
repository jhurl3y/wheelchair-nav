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
   
    def run(self):
        try:
            while True:
                self.__gpsd.next() #grab EACH set of gpsd info to clear the buffer
                time.sleep(5) #set to whatever
        except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
            gpsp.join() # wait for the thread to finish what it's doing

    def get_location(self):
	lat = self.__gpsd.fix.latitude
	long = self.__gpsd.fix.longitude        
	return [lat, long]
