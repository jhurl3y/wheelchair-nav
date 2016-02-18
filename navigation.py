import math
import gps

@staticmethod
def get_bearing(gps_start, gps_end):
    startLat = gps_start.get_latitude_radians
    startLong = gps_start.get_longitude_radians
    endLat = gps_end.get_latitude_radians
    endLong = gps_end.get_longitude_radians

    dLong = endLong - startLong

    dPhi = math.log(math.tan(endLat/2.0+math.pi/4.0)/math.tan(startLat/2.0+math.pi/4.0))

    if abs(dLong) > math.pi:
        if dLong > 0.0:
            dLong = -(2.0 * math.pi - dLong)
        else:
            dLong = (2.0 * math.pi + dLong)

    return (math.degrees(math.atan2(dLong, dPhi)) + 360.0) % 360.0;

@staticmethod
def get_distance(gps_start, gps_end):
    R = 6371; # km

    startLat = gps_start.get_latitude_radians
    startLong = gps_start.get_longitude_radians
    endLat = gps_end.get_latitude_radians
    endLong = gps_end.get_longitude_radians

    dLat = endLat - startLat
    dLon = endLong - startLong

    a = math.sin(dLat/2) * math.sin(dLat/2) +
            math.sin(dLon/2) * math.sin(dLon/2) * math.cos(startLat) * Math.cos(endLat); 
    c = 2 * Math.atan2(math.sqrt(a), math.sqrt(1-a)); 

    return R * c

@staticmethod
def yaw_to_heading(yaw, offset):
    if -180.0 < yaw < 0.0:
        yaw = yaw + 360.0
    yaw = yaw + offset
    return yaw