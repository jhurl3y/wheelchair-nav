from dual_mc33926_rpi import motors, MAX_SPEED
import calc_motor_values

class DriveMotors:
  
  def __init__(self):
    motors.enable()
    motors.setSpeeds(0, 0)
    self.angle = 0
    self.speed = 0
    self.calc_motor_values = calc_motor_values.Motor(MAX_SPEED)

  def drive(self, angle, speed):
    if angle != self.angle or speed != self.speed:
      self.angle = angle
      self.speed = speed
      left, right = self.calc_motor_values.get_speeds(self.angle, self.speed)
      motors.motor1.setSpeed(int(left))
      motors.motor2.setSpeed(int(right))

  def finish(self):
    motors.setSpeeds(0, 0)
    motors.disable()
