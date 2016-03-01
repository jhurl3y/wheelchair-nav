import time
import RTIMU 
import sys, getopt 
sys.path.append('.') 
import os.path 
import time 
import math 
import navigation as nav
import gps_obj
from time import sleep
from dual_mc33926_rpi import motors, MAX_SPEED
import PID

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
motors.enable()
motors.setSpeeds(0, 0)

try:
    last_waypoint = gps_obj.GPS(53.272909, -9.059584)
    next_waypoint = gps_obj.GPS(53.273292, -9.060419)

    read = imu.IMURead() 

    while read is None:
        print 'No IMU reading'
        sleep(1)
        read = imu.IMURead() 

    print 'Have IMU reading'
        
    data = imu.getIMUData()
     
    fusionPose = data["fusionPose"]
    yaw = math.degrees(fusionPose[2])
    print 'Read yaw: %f' % math.degrees(fusionPose[2])

    heading = nav.yaw_to_heading(yaw, -90.0)
    print 'Heading: %f' % heading

    bearing = nav.get_bearing(last_waypoint, next_waypoint)
    print 'Bearing: ', bearing

    P = 1.2
    I = 1
    D = 0.0
    L = 200

    pid = PID.PID(P, I, D)

    pid.SetPoint=bearing
    pid.setSampleTime(0.01)

    END = L

    for i in range(1, END):
        pid.update(heading)
        output = pid.output

        if output > 0:
            motors.motor1.setSpeed(2)
            motors.motor2.setSpeed(-2)
        elif output < 0:
            motors.motor1.setSpeed(-2)
            motors.motor2.setSpeed(2)

        data = imu.getIMUData()
        fusionPose = data["fusionPose"]
        yaw = math.degrees(fusionPose[2])
        print 'Read yaw: %f' % math.degrees(fusionPose[2])
        heading = nav.yaw_to_heading(yaw, -90.0)
        print 'Heading: %f' % heading
        sleep(1)

    motors.setSpeeds(0, 0)
    
except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print "\nStop..."
    motors.setSpeeds(0, 0)
    motors.disable()






