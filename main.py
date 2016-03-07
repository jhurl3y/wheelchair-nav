import gps_poller 
import time
import RTIMU 
import sys, getopt 
sys.path.append('.') 
import os.path 
import time 
import math 
import navigation as nav
import gps_estimation as estimator
import gps_obj
from time import sleep

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
estimator = estimator.Estimator(0.5)
poll_interval = imu.IMUGetPollInterval()
print("Recommended Poll Interval: %dmS\n" % poll_interval)

try:

    last_waypoint = gps_obj.GPS(53.272909, -9.059584)
    next_waypoint = gps_obj.GPS(53.273292, -9.060419)

    while True:

	   location = gpsp.get_location()

        # Have to wait initially to get fix
        while location is None:
            print 'No fix'
            sleep(1)
            location = gpsp.get_location()

        print 'Have fix'

        read = imu.IMURead() 

        while read is None:
            print 'No IMU reading'
            sleep(1)
            read = imu.IMURead() 


        print 'Have IMU reading'

        current_timestamp = time.time() # gpsp.get_timestamp()
        last_waypoint.set_timestamp(current_timestamp)
        data = imu.getIMUData()

        while not location is None:
            print 'Next lat/lng: ', next_waypoint.latitude, ', ', next_waypoint.longitude
            print 'Read lat/lng (moving avg): ', location[0], ', ', location[1]
#	    print location[0], ',',  location[1]
            
            fusionPose = data["fusionPose"]
            yaw = math.degrees(fusionPose[2])
            print 'Read yaw: %f' % math.degrees(fusionPose[2])

            heading = nav.yaw_to_heading(yaw, -90.0)
            print 'Heading: %f' % heading

            current_timestamp = time.time() # gpsp.get_timestamp()
            estimator.set_state(last_waypoint.latitude, last_waypoint.longitude, 0, last_waypoint.timestamp) 
            estimator.k_filter(location[0], location[1], 2, current_timestamp)
            last_waypoint = gps_obj.GPS(estimator.lat, estimator.long)
            last_waypoint.set_timestamp(current_timestamp)
            print 'Filtered lat/lng: ', last_waypoint.latitude, ', ', last_waypoint.longitude
 #           print last_waypoint.latitude, ', ', last_waypoint.longitude

            bearing = nav.get_bearing(last_waypoint, next_waypoint)
            distance = nav.get_distance(last_waypoint, next_waypoint)

            print 'Bearing: ', bearing, ' Distance: ', distance
            print '------------------'
            sleep(1)
            location = gpsp.get_location()
            read = imu.IMURead() 	
            if read is None:
                break
            data = imu.getIMUData()
    
except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print "\nKilling Thread..."
    gpsp.stop()
    gpsp.join() # wait for the thread to finish what it's doing





# location = []
# while True:
# if gpsp.get_location() != location: 
#         location = gpsp.get_location()
#     if location:
#             print 'latitude: ' , location[0], ' longitude: ', location[1]
#         else:
#              print 'No fix'
# if imu.IMURead():
#         data = imu.getIMUData()
#         fusionPose = data["fusionPose"]
# #            print("yaw: %f" % math.degrees(fusionPose[2]))
#         print("yaw: %f" % nav.yaw_to_heading(math.degrees(fusionPose[2]), -90.0))
#         time.sleep(poll_interval*1.0/1000.0)
