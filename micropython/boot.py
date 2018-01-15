# This file is executed on every boot (including wake-boot from deepsleep)

import network
import ntptime

def do_connect():

    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('maple-ave-cast','susannasung')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

do_connect()
ntptime.settime()