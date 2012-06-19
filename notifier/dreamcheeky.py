
import time
import usb
 
from notifier import BaseNotifier

VENDOR_ID = 0x1d34
PRODUCT_ID = 0x0004

INIT_PACKET1 = (0x1F, 0x01, 0x29, 0x00, 0xB8, 0x54, 0x2C, 0x03)
INIT_PACKET2 = (0x00, 0x01, 0x29, 0x00, 0xB8, 0x54, 0x2C, 0x04)

class DreamcheekyNotifier(BaseNotifier):
    def __init__(self):
        """ Acquire a handle to an attached dreamcheeky device """
        self.device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)

        if self.device is None:
            pass

    def init_device(self):
        """ Initialize the device using the two init packets """

        if self.device.is_kernel_driver_active(0) is True:
            self.device.detach_kernel_driver(0)

        self.device.set_configuration()
        self.device.ctrl_transfer(0x21, 0x09, 0x81, 0, INIT_PACKET1, 100)
        self.device.ctrl_transfer(0x21, 0x09, 0x81, 0, INIT_PACKET2, 100) 


    def set_rgb(self, red, green, blue):
        """ Set the device to the give (red,green,blue) colour.
            Each component is an int 0x00 - 0x40 """

        color_packet = (red, green, blue, 0x00, 0x00, 0x54, 0x2C, 0x05)
        self.device.ctrl_transfer(0x21, 0x09, 0x81, 0, color_packet, 100)


    def welcome(self):
        """ Some visual feedback that the device is operational. """
        self.set_rgb(0x00, 0x40, 0x00)
        time.sleep(0.5)
        self.set_rgb(0x00, 0x00, 0x00)
        time.sleep(0.2)
        self.set_rgb(0x00, 0x40, 0x00)
        time.sleep(0.5)
        self.set_rgb(0x00, 0x00, 0x00)


    def error(self):
        """ Visual indication of an error condition. """
        self.set_rgb(0x40, 0x40, 0x40)
        time.sleep(0.4)
        self.set_rgb(0x00, 0x00, 0x00)
        time.sleep(0.2)
        self.set_rgb(0x40, 0x40, 0x40)
        time.sleep(0.4)
        self.set_rgb(0x00, 0x00, 0x00)
        time.sleep(0.2)


    def notify(self):
        """ Visual notification of new messages """
        self.set_rgb(0x00, 0x00, 0x40)
        time.sleep(0.4)
        self.set_rgb(0x00, 0x00, 0x00)
        time.sleep(0.2)
        self.set_rgb(0x00, 0x00, 0x40)
        time.sleep(0.4)
        self.set_rgb(0x00, 0x00, 0x00)
        time.sleep(0.2)
        self.set_rgb(0x00, 0x00, 0x40)


    def off(self):
        """ Turn off the dreamcheeky device. """
        self.set_rgb(0x00, 0x00, 0x00)

