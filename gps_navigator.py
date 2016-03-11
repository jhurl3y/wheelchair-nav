import gps_poller 
import time
import RTIMU 
import sys, getopt 
sys.path.append('.') 
import os.path 
import math 
import navigation as nav
import gps_estimation as estimator
import gps_obj
from time import sleep
from dual_mc33926_rpi import motors, MAX_SPEED 
import PID
from bluetooth import *
import threading

SETTINGS_FILE = "RTIMULib"
s = RTIMU.Settings(SETTINGS_FILE)
imu = RTIMU.RTIMU(s)

class NAVIGATOR(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.stop = threading.Event()
        self.start_sensors()

    def start_sensors(self):
        global SETTINGS_FILE
        global imu
        # create the threads
        self.gpsp = gps_poller.GpsPoller() 
        self.gpsp.start()

        print("Using settings file " + SETTINGS_FILE + ".ini")
        if not os.path.exists(SETTINGS_FILE + ".ini"):
          print("Settings file does not exist, will be created")

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
        self.estimator = estimator.Estimator(0.5)
        self.poll_interval = imu.IMUGetPollInterval()
        print("Recommended Poll Interval: %dmS\n" % self.poll_interval)
        #self.check_gps()
        motors.enable()
        motors.setSpeeds(0, 0)

    def stop(self):
        self.stop.set()

    def stopped(self):
        return self.stop.isSet()

    def go(self, start, end, socket):
        try:
            print 'Turning to bearing angle'
            self.turn(start, end)
            motors.setSpeeds(0, 0)
            sleep(1)
            # print 'Driving to destination'
            # self.estimator = estimator.Estimator(0.5)
            # self.drive(start, end)
            # motors.setSpeeds(0, 0)
            # sleep(1)
            print 'Reached destination'
            socket.send("Finished")
        except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
            print "\nStop..."
            motors.setSpeeds(0, 0)
            motors.disable()
            print "\nKilling Thread..."
    	    self.gpsp.stop()
    	    self.gpsp.join()

    def end_journey(self):
    	print "\nStop..."
        motors.setSpeeds(0, 0)
        motors.disable()
        print "\nKilling Thread..."
    	self.gpsp.stop()
    	self.gpsp.join()

    def check_imu(self):
        global imu
        read = imu.IMURead() 

        while read is None:
            print 'No IMU reading'
            sleep(1)
            read = imu.IMURead() 

        print 'Have IMU reading'

    def check_gps(self):
        self.location = self.gpsp.get_location()

        # Have to wait initially to get fix
        while self.location is None:
            print 'No fix'
            sleep(1)
            self.location = self.gpsp.get_location()

        print 'Have fix'


    def estimate_position(self):
        print 'Read lat/lng (moving avg): ', self.location[0], ', ', self.location[1]
        current_timestamp = time.time() # gpsp.get_timestamp()
        self.estimator.set_state(self.last_waypoint.latitude, self.last_waypoint.longitude, 0, self.last_waypoint.timestamp) 
        self.estimator.k_filter(self.location[0], self.location[1], 2, current_timestamp)
        self.last_waypoint = gps_obj.GPS(self.estimator.lat, self.estimator.long)
        self.last_waypoint.set_timestamp(current_timestamp)
        print 'Filtered lat/lng: ', last_waypoint.latitude, ', ', last_waypoint.longitude


    def turn(self, start, end):
        global imu
        self.check_imu()
            
        data = imu.getIMUData()
        fusionPose = data["fusionPose"]
        yaw = math.degrees(fusionPose[2])

        heading = nav.yaw_to_heading(yaw, -90.0)
        print 'Heading: %f' % heading

        bearing = nav.get_bearing(start, end)
        print 'Bearing: ', bearing

        P = 1.2
        I = 1.3
        D = 0
        L = 200

        pid = PID.PID(P, I, D)

        pid.SetPoint = bearing
        pid.setSampleTime(0.01)
        motor_val = 0

        thresh_up = 0.7*MAX_SPEED
        thresh_lo = 0.12*MAX_SPEED
        i = 0
        while True:
            i += 1
            
            if abs(360.0 - heading + bearing) < abs(heading - bearing):
                feedback = heading - 360.0
            else:
                feedback = heading
        
            pid.update(feedback)
            output = pid.output

            motor_val += (output - (1/i))
            print 'Output: %f' % output 

            if output >= 0.0:
                if output > thresh_up:
                    drive = int(thresh_up)
                elif output < thresh_lo:
                    drive = int(thresh_lo)
                else:
                    drive = int(output)
            else:
                if output < -thresh_up:
                    drive = int(thresh_up)
                elif output > -thresh_lo:
                    drive = int(thresh_lo)
                else:
                    drive = int(-output)
        
            if output > 0.0:
                motors.motor1.setSpeed(drive)
                motors.motor2.setSpeed(-drive)
            elif output < 0.0:
                motors.motor1.setSpeed(-drive)
                motors.motor2.setSpeed(drive)

            self.check_imu()

            data = imu.getIMUData()
            fusionPose = data["fusionPose"]
            yaw = math.degrees(fusionPose[2])
            heading = nav.yaw_to_heading(yaw, -90.0)
            print 'Heading: %f' % heading
            print 'Bearing: ', bearing

            if abs(heading - bearing) < 1.0:
                break

            sleep(0.1)
            motors.setSpeeds(0, 0)      

    def drive(self, start, end):
        global imu
        self.check_gps()
        self.check_imu()

        self.last_waypoint = start
        current_timestamp = time.time() # gpsp.get_timestamp()
        self.last_waypoint.set_timestamp(current_timestamp)
            
        data = imu.getIMUData()
        fusionPose = data["fusionPose"]
        yaw = math.degrees(fusionPose[2])
 
        heading = nav.yaw_to_heading(yaw, -90.0)
        print 'Heading: %f' % heading

        bearing = nav.get_bearing(start, end) 
        print 'Bearing: ', bearing

        P = 1.2
        I = 1
        D = 0
        L = 200

        pid = PID.PID(P, I, D)

        pid.SetPoint=bearing
        pid.setSampleTime(0.01)
        motor_val = 0

        thresh_up = 0.35*MAX_SPEED
        thresh_lo = 0.2*MAX_SPEED

        while True:
            print nav.get_distance(self.last_waypoint, end)
            if nav.get_distance(self.last_waypoint, end) < 5.0:
                break
            
            if abs(360.0 - heading + bearing) < abs(heading - bearing):
                feedback = heading - 360.0
            else:
                feedback = heading
        
            pid.update(feedback)
            output = pid.output

            if output >= 0.0:
                speed = thresh_up - output/4.0
            else:
                speed = thresh_up + output/4.0

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
  
                print 'Left'
            elif output < 0.0:
                motors.motor1.setSpeed(int(drive))
                motors.motor2.setSpeed(int(thresh_up))
                print 'Right'

            self.check_gps()
            self.check_imu()
            self.estimate_position()

            data = imu.getIMUData()
            fusionPose = data["fusionPose"]
            yaw = math.degrees(fusionPose[2])
            heading = nav.yaw_to_heading(yaw, -90.0)
            print 'Heading: %f' % heading
            bearing = nav.get_bearing(self.last_waypoint, end) 
            print 'Bearing: ', bearing

            sleep(0.1)
            motors.setSpeeds(0, 0)

