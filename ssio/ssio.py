#! /usr/bin/env python3
#coding: utf-8

Version = "1.10"

import os
import sys
import time
import netifaces
import urllib.parse
import urllib.request

args = sys.argv
if len(args) == 2:
    OPE  = args[1]
else:
    OPE  = "NOT_ASSIGN"

NAME = os.uname().nodename
HOST = "https://api.smart-agri.jp/ssio/ssio.php"
ecnt = 0

while True:
    try:
        IPA  = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
        MACA = netifaces.ifaddresses('eth0')[netifaces.AF_LINK][0]['addr']
        break
    except KeyError:
        if ecnt > 10 :
            quit(0)
        ecnt = ecnt + 1
        time.sleep(2)
        continue


sval = {'N':NAME,'H':MACA,'A':IPA,'O':OPE}
params = urllib.parse.urlencode(sval)
params = params.encode('ascii')
#print(params)
urlreq = urllib.request.Request(HOST,params)
with urllib.request.urlopen(urlreq) as urlresponse:
    the_page = urlresponse.read()

quit(0)



