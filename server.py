from bluetooth import *
import drive_motors
import gps_navigator 
import gps_obj as gps

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
#                   protocols = [ OBEX_UUID ] 
                    )

    print "Waiting for connection on RFCOMM channel %d" % port

    client_sock, client_info = server_sock.accept()
    print "Accepted connection from ", client_info
    nav = gps_navigator.NAVIGATOR()
    start = 0.0
    end = 0.0
    state = 0
    STARTED_JOURNEY = 1
    NO_JOURNEY = 2
    JOURNEY_PAUSED = 3
    JOURNEY_FINISHED = 4
    PRE_JOURNEY = 5
    MANUAL_CONTROL = 6

    try:
    	motor_driver = drive_motors.DriveMotors()
    	while True:
            data = client_sock.recv(1024)

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
                start = gps.GPS(float(data[0]), float(data[1]))
                end = gps.GPS(float(data[2]), float(data[3]))
                nav = gps_navigator.NAVIGATOR()
		nav.start_sensors()
                nav.go(start, end, client_sock)
        		
    	    elif state == NO_JOURNEY:
                continue
    	    elif state == JOURNEY_PAUSED:
                if nav.started == True:
                    if not nav.stopped():
                        print "\nKilling Thread..."
                        nav.end_journey()
	     	        nav.join()
		continue
    	    elif state == JOURNEY_FINISHED:
                break
    	    elif state == PRE_JOURNEY:
                continue
    	    elif state == MANUAL_CONTROL:
                if data is None:
                    continue
                if len(data) < 2:
                    continue
                data = data[1]
            	values = map(int, data.split())
            	motor_driver.drive(values[0], values[1])
                print values

    except IOError:
        pass
    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
        print "\nStop..."
    	motor_driver.finish()
        if nav.started == True:
            if not nav.stopped():
                print "\nKilling Thread..."
                nav.end_journey()
	     	nav.join()
    finally:
        print "\nStop..."
    	motor_driver.finish()
        if nav.started == True:
            if not nav.stopped():
                print "\nKilling Thread..."
                nav.end_journey()
	     	nav.join()


    print "Disconnected"
    client_sock.close()
    server_sock.close()
    print "Finished"
