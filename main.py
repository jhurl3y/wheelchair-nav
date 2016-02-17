import imu_poller
import gps_poller
import gps_obj

# create the threads
gpsp = gps_poller.GpsPoller() 
imup = imu_poller.IMUPoller()

gpsp.start()
imup.start()

try:
    location = []
    while True:
	if gpsp.get_location() != location: 
            location = gpsp.get_location()
	    if location:
                print 'latitude: ' , location[0], ' longitude: ', location[1]
    	    else:
                 print 'No fix'

	if imup.get_data():
	    imu_data = imup.get_data()
            print 'pitch: ' , imu_data[0]
            print 'roll: ' , imu_data[1]
            print 'yaw: ' , imu_data[2]

except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print "\nKilling Thread..."
    gpsp.stop()
    gpsp.join() # wait for the thread to finish what it's doing
    imup.stop()
    imup.join()
