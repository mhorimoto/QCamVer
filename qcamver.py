#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
from datetime import datetime
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
a0cala   = config.get('CALIB','A0CALA')
a0calb   = config.get('CALIB','A0CALB')
a0fact   = config.get('CALIB','A0FACT')
a1cala   = config.get('CALIB','A1CALA')
a1calb   = config.get('CALIB','A1CALB')
a1fact   = config.get('CALIB','A1FACT')
dbgmsg   = config.get('MAIN','DEBUG')
if (dbgmsg=="0"):
    dbg = False
else:
    dbg = True

def sr04ope():
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
    # Echoパルスのパルス幅(us)
    echo_pulse_width = (echo_off - echo_on) * 1000000
    # 距離を算出:Distance in cm = echo pulse width in uS/58
    dist = int(echo_pulse_width / 58)
    #print("distance={0:d}\n".format(distance))
    return dist

print(dbg)
if (dbg):
    print("post_url=:{0}:\n".format(post_url))
    print("key=:{0}:\n".format(key))
    print("STRDIR=:{0}:\n".format(STRDIR))

D2 = 5
D3 = 6
TRIG = 17
ECHO = 27
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
#
########################################
# SR04による高さ計測
########################################
#
# GPIO端子の初期設定
#
GPIO.setup(D2,GPIO.OUT)
GPIO.setup(D3,GPIO.OUT)
GPIO.output(D2,GPIO.HIGH)
GPIO.output(D3,GPIO.HIGH)
distance = 0
loopmax = 4
for i in range(1,loopmax):
    distance += sr04ope()
    time.sleep(0.5)
distance_avg = int(distance / (loopmax-1))

print("distance={0:d}\n".format(distance_avg))
#
########################################
# 可変抵抗器による方位角、仰角測定
########################################
#
#  I2C busの準備
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
#  A0,A1の読み込み
a0raw = AnalogIn(ads,ADS.P0)
a1raw = AnalogIn(ads,ADS.P1)
a0ang = int((a0raw.value-((a0raw.value*0.15)-2208))/88.37)
a1ang = int((a1raw.value-((a1raw.value*0.13)-2009))/88.37)
print("A0={0}({2}), A1={1}({3})\n".format(a0raw.value,a1raw.value,a0ang,a1ang))

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
    else:
        # /dev/video0を指定
        cap = cv2.VideoCapture(DEV_ID)
        # 解像度の指定
        print("WIDTH={0},HEIGHT={1}\n".format(WIDTH,HEIGHT))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        cap.set(cv2.CAP_PROP_BRIGHTNESS , -1)
        aw = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        ah = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        aa = cap.get(cv2.CAP_PROP_AUTO_EXPOSURE)
        ab = cap.get(cv2.CAP_PROP_BRIGHTNESS)
        print("SET_WIDTH={0},SET_HEIGHT={1}\n".format(aw,ah))
        print("SET_EXPOSURE={0},SET_BRIGHT={1}\n".format(aa,ab))
        # キャプチャの実施
        ret, frame = cap.read()
        if ret:
            # ファイル名に日付を指定
            path = STRDIR+"/" + time_header + "_"+str(DEV_ID)+".jpg"
            cv2.imwrite(path, frame)
        # 後片付け
        cap.release()
        #cv2.destroyAllWindows()
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
        'p2': distance_avg,
        'p3': 123
    }
    files = { 'file0': open(path, 'rb') }
    headers = {"Content-Type": "multipart/form-data"}
        
    #POST送信
    response = requests.post(
        post_url,
        data=data1,
        files=files)
    print (response.text)

    return


if __name__ == "__main__":
    GPIO.output(D2,GPIO.LOW)
    DEV_ID = -1
    WIDTH = 2592
    HEIGHT = 1944
    main()
    DEV_ID = 0
    WIDTH = 640
    HEIGHT = 480
    main()
#    DEV_ID = 2
#    WIDTH = 1280
#    HEIGHT = 720
#    main()
    GPIO.output(D2,GPIO.HIGH)
