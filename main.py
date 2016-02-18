import gps_poller
import RTIMU
import sys, getopt
sys.path.append('.')
import os.path
import time
import math
# create the threads
gpsp = gps_poller.GpsPoller() 

gpsp.start()

SETTINGS_FILE = "RTIMULib"

print("Using settings file " + SETTINGS_FILE + ".ini")
if not os.path.exists(SETTINGS_FILE + ".ini"):
  print("Settings file does not exist, will be created")

s = RTIMU.Settings(SETTINGS_FILE)
imu = RTIMU.RTIMU(s)

print("IMU Name: " + imu.IMUName())

if (not imu.IMUInit()):
    print("IMU Init Failed")
    sys.exit(1)
else:
    print("IMU Init Succeeded")

# this is a good time to set any fusion parameters

imu.setSlerpPower(0.02)
imu.setGyroEnable(True)
imu.setAccelEnable(True)
imu.setCompassEnable(True)

poll_interval = imu.IMUGetPollInterval()
print("Recommended Poll Interval: %dmS\n" % poll_interval)

try:
    location = []
    while True:
 	if gpsp.get_location() != location: 
            location = gpsp.get_location()
	    if location:
                print 'latitude: ' , location[0], ' longitude: ', location[1]
    	    else:
                 print 'No fix'
	if imu.IMURead():
            data = imu.getIMUData()
            fusionPose = data["fusionPose"]
            print("yaw: %f" % (math.degrees(fusionPose[2]))) 
            time.sleep(poll_interval*1.0/1000.0)
except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print "\nKilling Thread..."
    gpsp.stop()
    gpsp.join() # wait for the thread to finish what it's doing
