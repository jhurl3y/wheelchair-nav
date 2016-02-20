import math
import gps

def get_bearing(gps_start, gps_end):
    startLat = gps_start.get_latitude_radians()
    startLong = gps_start.get_longitude_radians()
    endLat = gps_end.get_latitude_radians()
    endLong = gps_end.get_longitude_radians()

    dLong = endLong - startLong

    dPhi = math.log(math.tan(endLat/2.0+math.pi/4.0)/math.tan(startLat/2.0+math.pi/4.0))

    if abs(dLong) > math.pi:
        if dLong > 0.0:
            dLong = -(2.0 * math.pi - dLong)
        else:
            dLong = (2.0 * math.pi + dLong)

    return (math.degrees(math.atan2(dLong, dPhi)) + 360.0) % 360.0;

def get_distance(gps_start, gps_end):
    R = 6371000; # m

    startLat = gps_start.get_latitude_radians()
    startLong = gps_start.get_longitude_radians()
    endLat = gps_end.get_latitude_radians()
    endLong = gps_end.get_longitude_radians()

    dLat = endLat - startLat
    dLon = endLong - startLong

    a = math.sin(dLat/2) * math.sin(dLat/2) + math.sin(dLon/2) * math.sin(dLon/2) * math.cos(startLat) * math.cos(endLat); 
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)); 

    return R * c

def yaw_to_heading(yaw, offset):
    if -180.0 < yaw < 0.0:
        yaw = yaw + 360.0
    yaw = yaw + offset

    if yaw > 360.0:
	yaw = yaw -360.0
    elif yaw < 0.0:
	yaw = 360.0 + yaw
    
    return yaw

# degrees, mins, seconds => degrees
# int, int, float
def convert_to_degrees(degrees, minutes, seconds):
    return degrees + (minutes / 60.0) + (seconds / 3600.0) 

# degrees => degrees, mins, seconds
# degrees has to be postive
def convert_from_degrees(degrees):
    d = math.floor(degrees)
    minutes = (degrees - d) * 60.0
    m = math.floor(minutes)
    s = (minutes - m) * 60.0
    return [int(d), int(m), round(s, 5)]

