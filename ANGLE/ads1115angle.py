#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import busio
import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# These parameters must be calibrated for each individual.
A0CENTER = 11950.0  ### center value of azimuth angle
A0PFACTO = 8510.0   ### Positive limit (90 degrees) value of azimuth angle
A0NFACTO = 7220.0   ### Negative limit (-90 degrees) value of azimuth angle

A1CENTER = 13350.0  ### Center value of elevation angle
A1PFACTO = 8800.0   ### Positive limit (90 degrees) value of elevation angle
A1NFACTO = 9170.0   ### Negative limit (-90 degrees) value of elevation angle

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
    return(a0a,a1a)

if __name__ == "__main__":

    #  I2C busの準備
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)
    #  A0,A1の読み込み
    try:
        while True:
            (a0ans,a1ans) = getAngle(ads,ADS.P0,ADS.P1,A0CENTER,A0PFACTO,A0NFACTO,A1CENTER,A1PFACTO,A1NFACTO)
            print("A0={0}, A1={1}".format(int(a0ans),int(a1ans)))
            time.sleep(1)
    except KeyboardInterrupt:
        quit()

