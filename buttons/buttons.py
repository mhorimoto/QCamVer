#!/usr/bin/env python

import RPi.GPIO as GPIO
import os, time

GPIO.setmode(GPIO.BCM)

# GPIO23 : one shot take a picture
GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
# GPIO24 : shutdown button
GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def shutdown(channel):
    os.system("sudo shutdown -h now")

def reboot(channel):
    os.system("sudo reboot")

def take_pic(channel):
    os.system("sudo /usr/local/bin/cucucam.py")

GPIO.add_event_detect(24, GPIO.FALLING, callback = shutdown, bouncetime = 2000)
GPIO.add_event_detect(23, GPIO.FALLING, callback = take_pic, bouncetime = 2000)

while 1:
  time.sleep(100)
