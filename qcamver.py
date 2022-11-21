#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import os
import json
import requests
import time
import re
import picamera
import socket
import configparser
import netifaces as ni
import RPi.GPIO as GPIO
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

CONFIGFILE = "/usr/local/etc/QCamVer.conf"

config = configparser.ConfigParser()
config.read(CONFIGFILE,encoding="utf-8")

post_url = config.get('SERVER','HOST')
key      = config.get('SERVER','KEY')
STRDIR   = config.get('MAIN','STDIR')
a0center = float(config.get('CALIB','A0CENTER'))
a0pfacto = float(config.get('CALIB','A0PFACTO'))
a0nfacto = float(config.get('CALIB','A0NFACTO'))
a1center = float(config.get('CALIB','A1CENTER'))
a1pfacto = float(config.get('CALIB','A1PFACTO'))
a1nfacto = float(config.get('CALIB','A1NFACTO'))
dbgmsg   = config.get('MAIN','DEBUG')
if (dbgmsg=="0"):
    dbg = False
else:
    dbg = True

print(dbg)
if (dbg):
    print("post_url=:{0}:\n".format(post_url))
    print("key=:{0}:\n".format(key))
    print("STRDIR=:{0}:\n".format(STRDIR))

#
# GPIO端子の初期設定
#
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
D2 = 5
D3 = 6
GPIO.setup(D2,GPIO.OUT)
GPIO.setup(D3,GPIO.OUT)
GPIO.output(D2,GPIO.HIGH)
GPIO.output(D3,GPIO.HIGH)
#
def sr04ope(t,e):
    echo_on = 0
    echo_off = 0
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

########################################
# SR04による高さ計測
########################################
TRIG = 17
ECHO = 27
height = 0
loopmax = 4
for i in range(1,loopmax):
    height += sr04ope(TRIG,ECHO)
    time.sleep(0.1)
height_avg = int(height / (loopmax-1))
if dbg:
    print("height={0:d}".format(height_avg))
#
########################################
# 可変抵抗器による方位角、仰角測定
########################################
def getAngle(ads1x15,p0,p1,a0c,a0p,a0n,a1c,a1p,a1n):
    a0raw = AnalogIn(ads1x15,p0)
    a1raw = AnalogIn(ads1x15,p1)
    if a0raw.value > a0c:
        a0a = ((a0raw.value-a0c)/a0p) * 90
    else:
        a0a = ((a0c-a0raw.value)/a0n) * -90
    if a1raw.value < a1c:
        a1a = ((a1c-a1raw.value)/a1p) * 90
    else:
        a1a = ((a1raw.value-a1c)/a1n) * -90
    return(a0a,a1a,a0raw.value,a1raw.value)
#
#  I2C busの準備
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
(a0ang,a1ang,a0raw,a1raw) = getAngle(ads,ADS.P0,ADS.P1,a0center,a0pfacto,a0nfacto,a1center,a1pfacto,a1nfacto)
if dbg:
    print("A0={0}({2}), A1={1}({3})\n".format(a0raw,a1raw,a0ang,a1ang))

#
def main():
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    time_header=re.sub("[-:\s]", "", now)
    if (DEV_ID == -1):
        camera = picamera.PiCamera()
        camera.resolution = (2592, 1944)
        camera.framerate = 15
        camera.start_preview()
        time.sleep(2)
        path = STRDIR+"/"+time_header+"_M.jpg"
        camera.capture(path)
        camera.close()
        files = { 'file0': open(path, 'rb') }
#
    ni.ifaddresses('eth0')
    ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']

    #POSTするデータ設定
    data1 = {
        'key': key,
        'dt': now,
        'cam0': str(DEV_ID),
        'ip': ip,
        'p0': a0ang,
        'p1': a1ang,
        'p2': height_avg
    }
    files = { 'file0': open(path, 'rb') }
    headers = {"Content-Type": "multipart/form-data"}
        
    #POST送信
    response = requests.post(
        post_url,
        data=data1,
        files=files)
    print (response.text)
    os.remove(path)
    return

if __name__ == "__main__":
    GPIO.output(D2,GPIO.LOW)
    DEV_ID = -1
    WIDTH = 2592
    HEIGHT = 1944
    main()
    GPIO.output(D2,GPIO.HIGH)
