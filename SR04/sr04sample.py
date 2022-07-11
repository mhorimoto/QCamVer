#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import RPi.GPIO as GPIO
 
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#TRIG = 17
#ECHO = 27

def sr04ope(t,e):
    # GPIO端子の初期設定
    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.3)
    # Trig端子を10us以上High
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)
    # EchoパルスがHighになる時間
    while GPIO.input(ECHO) == 0:
        echo_on = time.time()
    # EchoパルスがLowになる時間
    while GPIO.input(ECHO) == 1:
        echo_off = time.time()
        if (echo_off - echo_on > 0.026):
            echo_off = -1
            break
    if echo_off > 0:
       # Echoパルスのパルス幅(us)
       echo_pulse_width = (echo_off - echo_on) * 1000000
       # 距離を算出:Distance in cm = echo pulse width in uS/58
       distance = echo_pulse_width / 58
    else:
       distance = -1
    return int(distance)

for k in sys.argv[1:]:
    if k=="f" or k=="F":
        TRIG = 12
        ECHO = 16
        dist = sr04ope(TRIG,ECHO)
        print("FORWARD={0:d}cm".format(dist))
    if k=="h" or k=="H":
        TRIG = 17
        ECHO = 27
        dist = sr04ope(TRIG,ECHO)
        print("HIGH={0:d}cm".format(dist))
        
