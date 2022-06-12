#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
import os,time
import RPi.GPIO as GPIO

TRIG = 17
ECHO = 27
#TRIG = 12
#ECHO = 16

starttime = 0
finishtime = 0
during = 0
flag = 0

def countstart(channel):
    global starttime
    starttime = time.perf_counter_ns()
#    GPIO.remove_event_detect(ECHO)
    GPIO.add_event_detect(ECHO, GPIO.FALLING, callback = countstop)


def countstop(channel):
    global flag,starttime,finishtime,during
    finishtime = time.perf_counter_ns()
    during = finishtime - starttime
    flag = 1

def countope(channel):
    global flag,starttime,finishtime,during
    if GPIO.input(ECHO)==1:
        starttime = time.perf_counter_ns()
    else:
        finishtime = time.perf_counter_ns()
        during = finishtime - starttime
        flag = 1

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
 
# GPIO端子の初期設定
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.output(TRIG, GPIO.LOW)
time.sleep(0.3)
#GPIO.add_event_detect(ECHO, GPIO.FALLING, callback = countstop, bouncetime = 2000)

GPIO.add_event_detect(ECHO, GPIO.BOTH, callback = countope)

# Trig端子を10us以上High
GPIO.output(TRIG, GPIO.HIGH)
time.sleep(0.00001)
#starttime = time.perf_counter_ns()
GPIO.output(TRIG, GPIO.LOW)

time.sleep(0.5)

if (flag==1):
    print("START={0}\nEND={1}\nDURING={2}\n".format(starttime,finishtime,during))
else:
    print("TIMEOUT\n")

GPIO.remove_event_detect(ECHO)
GPIO.cleanup()

ss = 331.5 + (0.61*25)
distance = ((during/10000000) * ss) / 2
# Echoパルスのパルス幅(us)
#echo_pulse_width = (echo_off - echo_on) * 1000000
 
# 距離を算出:Distance in cm = echo pulse width in uS/58
#distance = echo_pulse_width / 58
 
print(distance)
