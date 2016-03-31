from bluetooth import *
import drive_motors
import gps_navigator 
import gps_obj
from time import sleep
import sys, getopt 
sys.path.append('.') 
import os.path 
import autopilot as autonomous_nav

try: 
	while True:                 
		server_sock = BluetoothSocket( RFCOMM )
		server_sock.bind(("",PORT_ANY))
		server_sock.listen(1)

		port = server_sock.getsockname()[1]

		uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

		advertise_service( server_sock, "SampleServer",
					   service_id = uuid,
					   service_classes = [ uuid, SERIAL_PORT_CLASS ],
					   profiles = [ SERIAL_PORT_PROFILE ], 
						)

		print "Waiting for connection on RFCOMM channel %d" % port
		client_sock= None
		client_sock, client_info = server_sock.accept()
		print "Accepted connection from ", client_info
		nav = None
		autopilot = None
		start = 0.0
		end = 0.0
		state = 0
		STARTED_JOURNEY = 1
		NO_JOURNEY = 2
		JOURNEY_PAUSED = 3
		JOURNEY_FINISHED = 4
		PRE_JOURNEY = 5
		MANUAL_CONTROL = 6
		AUTONOMOUS_MODE = 7

		try:
			while True:
				data = client_sock.recv(1024) # waits

				if len(data) != 0: 
					data = data.split(';') 
					state = int(data[0])
					print state

				if state == STARTED_JOURNEY:
					if data is None:
						continue
					if len(data) < 2:
						continue
					data = data[1].split()
					print data

					nav = gps_navigator.NAVIGATOR()
					start = gps_obj.GPS(float(data[0]), float(data[1]))
					end = gps_obj.GPS(float(data[2]), float(data[3]))
					nav.start_sensors(start, end, client_sock)
					nav.start()
					
				elif state == NO_JOURNEY:
					continue

				elif state == JOURNEY_PAUSED:
					continue

				elif state == JOURNEY_FINISHED:
					if nav is not None:
						if not nav.stopped():
							print "\nKilling Thread..."
							nav.end_journey()
							nav.stop()
							nav.join()
							print "Finished Journey"
							break

				elif state == PRE_JOURNEY:
					continue

				elif state == MANUAL_CONTROL:
					if autopilot is not None:
						if not autopilot.stopped():
							print "\nKilling Thread..."
							autopilot.stop()
							autopilot.join()

					if nav is not None:
						if not nav.stopped():
							print "\nKilling Thread..."
							nav.end_journey()
							nav.stop()
							nav.join()

					if data is None:
						continue
					if len(data) < 2:
						continue

					motor_driver = drive_motors.DriveMotors()
					data = data[1]
					values = map(int, data.split())
					motor_driver.drive(values[0], values[1])
					print values

				elif state == AUTONOMOUS_MODE:
					autopilot = autonomous_nav.Autopilot()

					if (not autopilot.started) or autopilot.stopped() or autopilot.error:
						autopilot.wait_for_client('10.42.0.79', 8888) # PORT_ANY


		except (KeyboardInterrupt):#, SystemExit): #when you press ctrl+c
			print "\nStop..."
			motor_driver.finish()
			if nav is not None:
				if not nav.stopped():
					print "\nKilling Thread..."
					nav.end_journey()
					nav.stop()
					nav.join()

		finally:
			print "\nStop..."
			motor_driver.finish()
			if nav is not None:
				if not nav.stopped():
					print "\nKilling Thread..."
					nav.end_journey()
					nav.stop()
					nav.join()

		print "Disconnected"
		client_sock.close()
		server_sock.close()
		print "Finished"

except (KeyboardInterrupt):#, SystemExit): #when you press ctrl+c
	print "Exiting.."
	print "Disconnected"
	if client_sock is not None:
		client_sock.close() 
	server_sock.close() 
	print "Finished"