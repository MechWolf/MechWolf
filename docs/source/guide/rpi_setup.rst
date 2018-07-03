    :Author: Alex Mijalis

.. contents::

Mechwolf Raspberry Pi Setup Guide

1 Raspberry Pi
--------------

MechWolf can be installed on the Raspberry Pi using a piece of
software called `PiBakery <http://www.pibakery.org>`_. Download PiBakery and install it using the
"Raspbian Lite" option.

- Insert the SD card (preferably class 10 or better) into your computer

- Launch PiBakery and load the PiBakery.xml configuration file from the MechWolf repository

- Configure your Raspberry Pi's username, password and WiFi details where indicated
  !!! Caution !!! Choose strong passwords. The username and password you
  choose can be used to remotely log in and control the Raspberry
  Pi.

- Click "Write" to put the customized copy of Raspbian Lite onto the SD card.

- Once the writing is complete, move the MechWolf folder onto the boot drive

- Place your client\ :sub:`config.yml`\ file onto the boot drive.
  *Note:* If you are using a Raspberry Pi, we recommend using serial
  cables manufactured by FTDI. Because FTDI gives each device a unique
  serial number, mechwolf components can be referenced uniquely in the
  client\ :sub:`config.yml`\ file. On the raspberry pi, this will be something like:
  /dev/serial/by-id/usb-FTDI\ :sub:`FT232R`\ \ :sub:`USB`\ \ :sub:`UART`\ \ :sub:`AH06396Q`\-if00-port0

- Start the raspberry pi. The MechWolf software suite should copy from the boot partition and launch automatically.

2 Varian Pump RS422 Cables
--------------------------

`FTDI RS422-USB Product Page <http://www.ftdichip.com/Products/Cables/USBRS422.htm>`_
`FTDI RS422-USB Datasheet <http://www.ftdichip.com/Support/Documents/DataSheets/Cables/DS_USB_RS422_CABLES.pdf>`_
Part number: FTDI USB-RS422-WE-1800-BT CABLE, USB TO RS422 SERIAL, 1.8M, WIRE END

2.1 Wiring guide
~~~~~~~~~~~~~~~~

This table describes how to connect the USB-RS422-WE to a DB9 connector. The wires can be soldered or inserted into a DB9 breakout board with screw terminals.

.. table::

    +-----------+-------------------+------------+-------------------+
    | RS422 Pin | RS422 Description | Wire Color | DB9 Connector Pin |
    +===========+===================+============+===================+
    |         3 | TXD-              | Red        |                 3 |
    +-----------+-------------------+------------+-------------------+
    |         1 | Ground            | Black      |                 5 |
    +-----------+-------------------+------------+-------------------+
    |         4 | TXD+              | Orange     |                 8 |
    +-----------+-------------------+------------+-------------------+
    |         5 | RXD+              | Yellow     |                 7 |
    +-----------+-------------------+------------+-------------------+
    |         8 | RXD-              | White      |                 2 |
    +-----------+-------------------+------------+-------------------+

3 VICI Valve Cables
-------------------

Part number: TERA grand USB2.0 to RS232 cable (USB2-RS232TS-03) For
MechWolf: Find a cable with an FTDI chipset (not PL2303). PL2303 chips
do not have unique identifiers, making it difficult to run multiple
components on one raspberry pi.
