'''
    Simple udp socket server
    Silver Moon (m00n.silv3r@gmail.com)
'''
 
import socket
import time  
import sys, getopt 
sys.path.append('.') 
import os.path 
import math  
from time import sleep 
from dual_mc33926_rpi import motors, MAX_SPEED 
import PID
 
HOST = socket.gethostname()   # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port
 
# Datagram (udp) socket
try :
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print 'Socket created'
except socket.error, msg :
    print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
 
 
# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error , msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Socket bind complete'

motors.enable()
motors.setSpeeds(0, 0)

try:
    P = 1.2
    I = 1.3
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
     
    #now keep talking with the client
    while 1:
        # receive data from client (data, addr)
        d = s.recvfrom(1024)
        data = d[0]
        addr = d[1]
         
        if not data: 
            break
        
        data = data.strip().split()
        print data

        if int(data[1]) < 10:
            print 'Obstacle in way!'
            motors.setSpeeds(0, 0)
            break

        if len(data) > 2:
            left = int(data[3])
            right = int(data[5])

            if abs(left - right) < 5:
                motors.motor1.setSpeed(int(1.2*thresh_up))
                motors.motor2.setSpeed(int(thresh_up))
                break

            feedback =  left - right
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

            if output >= 0.0:
                motors.motor1.setSpeed(int(1.2*thresh_up))
                motors.motor2.setSpeed(drive)
                print 'Move Right'
            else:
                motors.motor1.setSpeed(int(drive))
                motors.motor2.setSpeed(int(thresh_up))
                print 'Move Left'

        else:
            motors.motor1.setSpeed(int(1.2*thresh_up))
            motors.motor2.setSpeed(int(thresh_up))

        sleep(0.1)
        motors.setSpeeds(0, 0)

     
except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print "\nStop..."
    motors.setSpeeds(0, 0)
    motors.disable()
    s.close()