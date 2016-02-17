import imu_poller
import gps_poller
import gps_obj

# create the threads
gpsp = gps_poller.GpsPoller() 
#imup = imu_poller.IMUPoller()

gpsp.start()
#imup.start()

try:
    while True:
        location = gpsp.get_location()
	if location:
        #imu_data = imup.get_data()
            print 'latitude: ' , location[0]
            print 'longitude: ' , location[1]
       # print 'pitch: ' , imu_data[0]
       #print 'roll: ' , imu_data[1]
       # print 'yaw: ' , imu_data[2]
except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print "\nKilling Thread..."
    gpsp.join() # wait for the thread to finish what it's doing
