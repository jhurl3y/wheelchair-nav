#! /usr/bin/python

import os
from time import *
import time
import RPi.GPIO as GPIO
import threading

class UltrasonicPoller(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.__stop = threading.Event()
        GPIO.setmode(GPIO.BOARD)
        self.distance = 0
   
    def run(self):
        try:
            GPIO.setup(13, GPIO.OUT)
            while not self.stopped():
                GPIO.setup(21, GPIO.OUT)
                GPIO.output(21, False)
                time.sleep(0.000002)
                GPIO.output(21, True)
                time.sleep(0.000005)
                GPIO.output(21, False)
                GPIO.setup(21, GPIO.IN)

                # Count microseconds that SIG was high
                while GPIO.input(21) == 0:
                  starttime = time.time()

                while GPIO.input(21) == 1:
                  endtime = time.time()

                duration = endtime - starttime
                # The speed of sound is 340 m/s or 29 microseconds per centimeter.
                # The ping travels out and back, so to find the distance of the
                # object we take half of the distance travelled.
                # distance = duration / 29 / 2
                self.distance = duration * 34000 / 2
                GPIO.output(13, int(self.distance))
                time.sleep(1)

        finally:
            GPIO.cleanup()
            
    def stop(self):
        self.__stop.set()

    def stopped(self):
        return self.__stop.isSet()
