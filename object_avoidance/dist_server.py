import time
import RPi.GPIO as GPIO

GPIO.setup(23, GPIO.IN)
try:
    while True:
        distance = GPIO.input(23)
        print distance

    finally:
        GPIO.cleanup()
  