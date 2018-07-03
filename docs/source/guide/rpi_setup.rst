Raspberry Pi Setup Guide
========================

On the Raspberry Pi
-------------------

MechWolf can be installed on the Raspberry Pi using a piece of software called
`PiBakery <http://www.pibakery.org>`_. Download PiBakery and install it using
the "Raspbian Lite" option.

- Insert the SD card (preferably class 10 or better) into your computer.

- Launch PiBakery and load the ``PiBakery.xml`` configuration file from the
  MechWolf repository. It is availible for download `here
  <https://raw.githubusercontent.com/Benjamin-Lee/MechWolf/master/pibaker_setup.xml>`_.

- Configure your Raspberry Pi's username, password and WiFi details where indicated.

  .. warning::

     Choose strong passwords. The username and password you choose can be used
     to remotely log in and control the Raspberry Pi.

- Click "Write" to put the customized copy of Raspbian Lite onto the SD card.

- Once the writing is complete, move the MechWolf folder onto the boot drive.

- Place your ``client_config.yml`` file onto the boot drive.

  When configuring a component that connects via usb, the serial port
  ``/dev/ttyUSB0/`` should work if there is only one USB device connected.

    .. note::

        If you are using a Raspberry Pi with multiple serial devices, we
        recommend using serial cables manufactured by FTDI. Because FTDI gives
        each device a unique serial number, mechwolf components can be
        referenced uniquely in the ``client_config.yml`` file. On the Raspberry
        Pi, this will be something like:
        ``/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AH06396Q-if00-port0``

- Start the Raspberry Pi. The MechWolf software suite should copy from the boot
  partition and launch automatically.

Serial Devices
--------------

Varian Pump RS422 Cables
~~~~~~~~~~~~~~~~~~~~~~~~

`FTDI RS422-USB Product Page <http://www.ftdichip.com/Products/Cables/USBRS422.htm>`_

`FTDI RS422-USB Datasheet
<http://www.ftdichip.com/Support/Documents/DataSheets/Cables/DS_USB_RS422_CABLES.pdf>`_

Part number: FTDI USB-RS422-WE-1800-BT CABLE, USB TO RS422 SERIAL, 1.8M, WIRE
END

Wiring guide
^^^^^^^^^^^^

This table describes how to connect the USB-RS422-WE to a DB9 connector. The
wires can be soldered or inserted into a DB9 breakout board with screw
terminals.

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

VICI Valve Cables
~~~~~~~~~~~~~~~~~

VICI valves configured with USB should work natively with the Raspberry Pi. VICI
valves configured with RS232 communication require a USB to RS232 conversion
cable: Part number: TERA grand USB2.0 to RS232 cable (USB2-RS232TS-03)

For MechWolf, use  a cable with an FTDI chipset (not PL2303). PL2303 chips do
not have unique identifiers, making it difficult to run multiple components on
one Raspberry Pi.
