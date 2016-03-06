from __future__ import division

class Motor:
  def __init__(self, max_speed):
    self.max_speed = max_speed

  # returns speeds calculated for left right motors
  # from angle -> (left_speed, right_speed)
  def get_speeds(self, angle, speed):
    speed = self.max_speed * (speed/10)

    # straight ahead
    if angle == 0:
      return (speed, speed)
    # direct right
    elif angle == 90:
      return (speed, -1 * speed)
    # direct left
    elif angle == -90:
      return (-1 * speed, speed)
    # straight reverse
    elif angle == 180:
      return (-1 * speed, - 1 * speed)
    
    # forward right
    elif 0 < angle <= 45:
      return (speed, (1 - angle/45) * speed)
    # forward sharp right
    elif 45 < angle < 90:
      return (speed, -1 * ((angle - 45)/45) * speed)
    # forward left
    elif 0 > angle >= -45:
      return ((1 + angle/45) * speed, speed)
    # forward sharp left
    elif -45 > angle > -90:
      return (((angle + 45)/45) * speed, speed)
    
    # reverse right 
    elif 180 > angle > 135: 
      return (-1 * speed, ((angle - 135)/45) * -1 * speed)
    # reverse sharp right
    elif 135 >= angle > 90:
      return (-1 * speed, (1 - (angle - 90)/45) * speed)
    # reverse left
    elif -180 < angle < -135:
      return (((angle + 135)/45) * speed, -1 * speed)
    # reverse sharp left
    elif -135 <= angle < -90:
      return ((1 + (angle + 90)/45) * speed, -1 * speed)
    else:
      return (0, 0)

