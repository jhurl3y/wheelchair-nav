import sys, getopt

sys.path.append('.')
import RTIMU
import os.path
import time
import math

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
        self.__data = 0

        def run(self):
            while True:
                if self.__imu.IMURead():
                    self.__data = imu.getIMUData()["fusionPose"]
                    time.sleep(poll_interval*10.0/1000.0)

        def get_data(self):
            return [math.degrees(data[0]), math.degrees(data[1]), math.degrees(data[2])]


                    