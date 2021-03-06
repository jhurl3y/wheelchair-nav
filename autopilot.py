#! /usr/bin/python

import os
from time import *
import time
import threading
import socket
import sys, getopt 
sys.path.append('.') 
import os.path 
import math  
from time import sleep 
from dual_mc33926_rpi import motors, MAX_SPEED 
import PID

class Autopilot(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.__stop = threading.Event()
        self.bound = False
        self.error = False
        self.started = False
        self.running = False

    def wait_for_client(self, host, port):
        try :
            self.started = True
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print 'Socket created'
        except socket.error, msg :
            print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            self.error = True
            return

        try:
            self.s.bind((host, port))
        except socket.error , msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            self.error = True
            return
        
        self.bound = True 
        print 'Socket bind complete'
        self.s.setblocking(0)
        self.start()
   
    def run(self):
        self.running = True
        motors.enable()
        motors.setSpeeds(0, 0)

        try:
            P = 1.2
            I = 1.3
            D = 0
            L = 200

            pid = PID.PID(P, I, D)

            pid.SetPoint=0
            pid.setSampleTime(0.01)
            motor_val = 0

            END = L
            max_out = 150.0
            thresh_up = 0.3*MAX_SPEED
            thresh_lo = 0.15*MAX_SPEED

            while not self.stopped():   
                try:
                    # receive data from client (data, addr)
                    d = self.s.recvfrom(1024)
                except socket.error , msg:
                    continue
                data = d[0]
                addr = d[1]
                 
                if not data: 
                    continue
                
                data = data.strip().split()
                print data

                if int(data[1]) < 25:
                    print 'Obstacle in way!'
                    #motors.setSpeeds(0, 0)
                    motors.motor1.setSpeed(-int(1.2*thresh_up))
                    motors.motor2.setSpeed(-int(thresh_up))
                    continue

                if len(data) > 2:
                    left = int(data[3])
                    right = int(data[5])

                    if abs(left - right) < 5:
                        motors.motor1.setSpeed(int(1.2*thresh_up))
                        motors.motor2.setSpeed(int(thresh_up))
                        print 'Move Straight'
                        continue

                    feedback =  left - right
                    pid.update(feedback)
                    output = pid.output
                    print 'output: ', output

                    if output >= 0.0:
                        speed = thresh_up - output/4.0 
                    else:
                        speed = thresh_up + output/4.0
                    
                    if speed < thresh_lo:
                        drive = int(thresh_lo)  
                    else: 
                        drive = int(speed)

                    if output <= 0.0:
                        motors.motor1.setSpeed(int(1.2*thresh_up))
                        motors.motor2.setSpeed(drive)
                        print 'Move Right'
                        print 'Left: ', int(1.2*thresh_up)
                        print 'Right: ', drive

                    else:
                        motors.motor1.setSpeed(int(drive))
                        motors.motor2.setSpeed(int(thresh_up))
                        print 'Move Left'
                        print 'Left: ', drive
                        print 'Right: ', int(thresh_up)
               
                else:
                    motors.motor1.setSpeed(int(1.2*thresh_up))
                    motors.motor2.setSpeed(int(thresh_up))
                    print 'Move Straight'
                    continue
      
        except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
            print "\nStop..."
            motors.setSpeeds(0, 0)
            motors.disable()
            self.s.close()

        finally:
            print "\nStopping..."
            motors.setSpeeds(0, 0)
            motors.disable()
            #self.s.close()
        
    def stop(self):
        self.s.close()
        self.running = False
        self.__stop.set()

    def stopped(self):
        return self.__stop.isSet()