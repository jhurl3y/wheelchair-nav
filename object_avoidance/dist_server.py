import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)
try:
    while True:
        distance = GPIO.input(11)
        if distance != 0:
	    print distance

finally:
    GPIO.cleanup()
  
