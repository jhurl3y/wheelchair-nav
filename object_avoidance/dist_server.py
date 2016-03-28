import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(23, GPIO.IN)
try:
    while True:
        distance = GPIO.input(23)
        if distance != 0:
	    print distance

finally:
    GPIO.cleanup()
  
