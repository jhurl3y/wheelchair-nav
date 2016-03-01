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
j = 0
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
    print 'Read yaw: %f' % yaw

    heading = nav.yaw_to_heading(yaw, -90.0)
    print 'Heading: %f' % heading

    bearing = nav.get_bearing(last_waypoint, next_waypoint)
    print 'Bearing: ', bearing

    P = 1.2
    I = 1
    D = 0
    L = 500

    pid = PID.PID(P, I, D)

    pid.SetPoint=bearing
    pid.setSampleTime(0.01)

    END = L

    for i in range(1, END):
        pid.update(heading)
	output = pid.output
	print output 

        if output < -30.0:
            motors.motor1.setSpeed(int(-0.2*MAX_SPEED))
            motors.motor2.setSpeed(int(0.2*MAX_SPEED))
        elif output > 30.0:
            motors.motor1.setSpeed(int(0.2*MAX_SPEED))
            motors.motor2.setSpeed(int(-0.2*MAX_SPEED))
        elif output < -15.0:
            motors.motor1.setSpeed(int(-0.15*MAX_SPEED))
            motors.motor2.setSpeed(int(0.15*MAX_SPEED))
        elif output > 15.0:
            motors.motor1.setSpeed(int(0.15*MAX_SPEED))
            motors.motor2.setSpeed(int(-0.15*MAX_SPEED))
        elif output < -5.0:
            motors.motor1.setSpeed(int(-0.12*MAX_SPEED))
            motors.motor2.setSpeed(int(0.12*MAX_SPEED))
        elif output > 5.0:
            motors.motor1.setSpeed(int(0.12*MAX_SPEED))
            motors.motor2.setSpeed(int(-0.12*MAX_SPEED))
        else:
	    
            if -0.3 < output < 0.3:
		if i > 3:
		    j = j + 1
		    if j == 2:
			print j
                        break 
            if output > 0.0:
                motors.motor1.setSpeed(int(0.1*MAX_SPEED))
                motors.motor2.setSpeed(int(-0.1*MAX_SPEED))
            elif output < 0.0:
                motors.motor1.setSpeed(int(-0.1*MAX_SPEED))
                motors.motor2.setSpeed(int(0.1*MAX_SPEED))

        read = imu.IMURead() 

        while read is None:
            print 'No IMU reading'
            read = imu.IMURead() 

        data = imu.getIMUData()
        fusionPose = data["fusionPose"]
        yaw = math.degrees(fusionPose[2])
        heading = nav.yaw_to_heading(yaw, -90.0)
        print 'Heading: %f' % heading
        print 'Bearing: ', bearing
        sleep(0.1)
        motors.setSpeeds(0, 0)

    
except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print "\nStop..."
    motors.setSpeeds(0, 0)
    motors.disable()






