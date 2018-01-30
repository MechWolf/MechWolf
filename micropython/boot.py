# This file is executed on every boot (including wake-boot from deepsleep)
from network import WLAN
import os
from machine import UART, RTC
import pycom
import time
import gc

def do_connect():

    sta_if = WLAN(mode=WLAN.STA)
    if not sta_if.isconnected():
        print('connecting to network...')
        
        #sta_if.connect('maple-ave-cast',auth = (WLAN.WPA2,'susannasung'))
        sta_if.connect('MIT')
        
        while not sta_if.isconnected():
            time.sleep(0.5)
    print('network config:', sta_if.ifconfig())

uart = UART(0, 115200)
os.dupterm(uart)
pycom.heartbeat(False)
gc.enable()
rtc = RTC()
do_connect()
rtc.ntp_sync('pool.ntp.org')
