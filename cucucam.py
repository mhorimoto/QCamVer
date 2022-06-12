#! /usr/bin/env python3
#coding: utf-8

import json
import requests
import time
import re
import picamera
import socket
import configparser
from time import sleep
import netifaces as ni

CONFIGFILE = "/usr/local/etc/CuCuCam.conf"

config = configparser.ConfigParser()
config.read(CONFIGFILE,encoding="utf-8")

post_url = config.get('SERVER','HOST')
key      = config.get('SERVER','KEY')
STRDIR   = config.get('MAIN','STDIR')

print("post_url=:{0}:\n".format(post_url))
print("key=:{0}:\n".format(key))
print("STRDIR=:{0}:\n".format(STRDIR))

if __name__ == "__main__":  
#時刻の取得とファイルヘッダーの作成
  now = time.strftime('%Y-%m-%d %H:%M:%S')
  time_header=re.sub("[-:\s]", "", now)
#  print (time_header)

#カメラ画像取得
#PiCamera
  camera = picamera.PiCamera()

  camera.resolution = (2592, 1944)
  camera.framerate = 15

  camera.start_preview()
  time.sleep(2)
  cam0=STRDIR+"/"+time_header+"_0.jpg"
  camera.capture(cam0)
  camera.close()

#データ転送
#  post_url = "https://agri-eye.net/rbtdata_uploader.php"
#  key=read_keys("/home/pi/pi_cam/system.ini")
#  key=read_keys("/home/pi/pi_cam/system_test.ini")

#  print (key)

#IPアドレス取得
  ni.ifaddresses('eth0')
  ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']

  #POSTするデータ設定
  data1 = {
    'key': key,
    'dt': now,
    'cam0': '0',
    'ip': ip
  }

#  print (data1)

  #POSTするファイルの読込
  files = { 'file0': open(cam0, 'rb') }

  #ヘッダー設定
  headers = {"Content-Type": "multipart/form-data"}

  #POST送信
  response = requests.post(
    post_url,
    data=data1,
    files=files)

  print (response.text)
