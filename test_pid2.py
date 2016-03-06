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
    print 'Read yaw: %f' % yaw

    heading = nav.yaw_to_heading(yaw, -90.0)
    print 'Heading: %f' % heading

#    bearing = nav.get_bearing(last_waypoint, next_waypoint) 
    bearing = 108.0
    print 'Bearing: ', bearing

    P = 1.2
    I = 1
    D = 0
    L = 200

    pid = PID.PID(P, I, D)

    pid.SetPoint=bearing
    pid.setSampleTime(0.01)
    motor_val = 0

    END = L
    max_out = 150.0

    thresh_up = 0.35*MAX_SPEED
    thresh_lo = 0.2*MAX_SPEED
    i = 0
    while True:
        i += 1
        
       # if abs(360.0 + heading - bearing) < abs(heading - bearing):
        #    feedback = heading + 360.0
	if abs(360.0 - heading + bearing) < abs(heading - bearing):
	    feedback = heading - 360.0
        else:
            feedback = heading
    
        pid.update(feedback)
        output = pid.output

#        motor_val += (output - (1/i))
#        print 'Output: %f' % output 
	
        if output >= 0.0:
            speed = thresh_up - output/4.0
        else:
            speed = thresh_up + output/4.0

#        print 'Speed: %f' % speed 

        if speed < thresh_lo:
            drive = int(thresh_lo)
        else:
            drive = int(speed)

	if abs(heading - bearing) < 2.0:
            motors.motor1.setSpeed(int(1.2*thresh_up))
            motors.motor2.setSpeed(int(thresh_up))
    	    print 'Both'
	elif output > 0.0:
            motors.motor1.setSpeed(int(1.2*thresh_up))
            motors.motor2.setSpeed(drive)
	   # print 'motor 1: %f' % int(1.2*thresh_up)
	   # print 'motor 2: %f' % drive
	    print 'Left'
        elif output < 0.0:
            motors.motor1.setSpeed(int(drive))
            motors.motor2.setSpeed(int(thresh_up))
	   # print 'motor 1: %f' % drive
	   # print 'motor 2: %f' % int(thresh_up)
	    print 'Right'

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



    # if output < -30.0:
    #     motors.motor1.setSpeed(int(-0.2*MAX_SPEED))
    #     motors.motor2.setSpeed(int(0.2*MAX_SPEED))
    # elif output > 30.0:
    #     motors.motor1.setSpeed(int(0.2*MAX_SPEED))
    #     motors.motor2.setSpeed(int(-0.2*MAX_SPEED))
    # elif output < -15.0:
    #     motors.motor1.setSpeed(int(-0.15*MAX_SPEED))
    #     motors.motor2.setSpeed(int(0.15*MAX_SPEED))
    # elif output > 15.0:
    #     motors.motor1.setSpeed(int(0.15*MAX_SPEED))
    #     motors.motor2.setSpeed(int(-0.15*MAX_SPEED))
    # elif output < -5.0:
    #     motors.motor1.setSpeed(int(-0.12*MAX_SPEED))
    #     motors.motor2.setSpeed(int(0.12*MAX_SPEED))
    # elif output > 5.0:
    #     motors.motor1.setSpeed(int(0.12*MAX_SPEED))
    #     motors.motor2.setSpeed(int(-0.12*MAX_SPEED))
    # else:
    #     if -0.001 < output < 0.001:
    #         break
    #     if output > 0.0:
    #         motors.motor1.setSpeed(int(0.1*MAX_SPEED))
    #         motors.motor2.setSpeed(int(-0.1*MAX_SPEED))
    #     elif output < 0.0:
    #         motors.motor1.setSpeed(int(-0.1*MAX_SPEED))
    #         motors.motor2.setSpeed(int(0.1*MAX_SPEED))


