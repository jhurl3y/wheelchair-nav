import sys, getopt

sys.path.append('.')
import RTIMU
import os.path
import time
import math
import threading

SETTINGS_FILE = "RTIMULib"

class IMUPoller(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        s = RTIMU.Settings(SETTINGS_FILE)
        self.__imu = RTIMU.RTIMU(s)
        self.__imu.setSlerpPower(0.02)
        self.__imu.setGyroEnable(True)
        self.__imu.setAccelEnable(True)
        self.__imu.setCompassEnable(True)
        self.__poll_interval = self.__imu.IMUGetPollInterval()
	self.__data = []
        self.__stop = threading.Event()        

    def run(self):
        while not self.stopped():
            if self.__imu.IMURead():
                self.__data = imu.getIMUData()["fusionPose"]
                time.sleep(poll_interval*10.0/1000.0)

    def stop(self):
        self.__stop.set()

    def stopped(self):
        return self.__stop.isSet()

    def get_data(self):
	if self.__data:
            pitch = math.degrees(self.__data[0])
            roll = math.degrees(self.__data[1])
            yaw = math.degrees(self.__data[2])
            return [pitch, roll, yaw]              
