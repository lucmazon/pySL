#!/usr/bin/python3
#-*- coding: utf-8 -*-
from typing import List

import usb.core
import usb.util
from enum import Enum

MAX_POTENTIOMETER_VALUE = 255

class ButtonStatus(Enum):
    PRESSED = 1
    RELEASED = 0

class Button:
    def __init__(self, id, status):
        self.id = id
        self.status = status

    def __eq__(self, other):
        return self.id == other.id and self.status == other.status

    def __str__(self):
        return "<Button {0},{1}>".format(self.id, self.status.name)

class Pedal:
    def __init__(self, id, value):
        self.id = id
        self.value = round(value / MAX_POTENTIOMETER_VALUE*100)

    def __eq__(self, other):
        return self.id == other.id and self.value == other.value

    def __str__(self):
        return "<Pedal {0}, {1}>".format(self.id, self.value)

class RawHID:
    def __init__(self):
        self.dev = usb.core.find(idVendor=0x16c0, idProduct=0x0480)
        if self.dev is None:
            raise ValueError('Our device is not connected')
        # first endpoint
        self.interface = 0
        self.endpoint = self.dev[0][(0,0)][0]
        # if the OS kernel already claimed the device, which is most likely true
        # thanks to http://stackoverflow.com/questions/8218683/pyusb-cannot-set-configuration
        if self.dev.is_kernel_driver_active(self.interface) is True:
          # tell the kernel to detach
          self.dev.detach_kernel_driver(self.interface)
          # claim the device
          usb.util.claim_interface(self.dev, self.interface)

        self.statuses = []
        for index in range(1,7):
            self.statuses.append(Button(index, ButtonStatus.RELEASED))
        self.statuses.append(Pedal(7, MAX_POTENTIOMETER_VALUE))

    def interpret_HID_packet(self, data):
        new_pedal = Pedal(7, data[25])
        changed_pedal = None
        if (self.statuses[6] != new_pedal):
            changed_pedal = new_pedal
        self.statuses[6] = new_pedal

        changed_buttons = [] # type: List[Button]
        for index, key in enumerate([2, 3, 4, 5, 6, 7]):
            new_status = Button(index, ButtonStatus.PRESSED if data[key] else ButtonStatus.RELEASED)
            if (self.statuses[index] != new_status):
                changed_buttons.append(new_status)
            self.statuses[index] = new_status

        return changed_pedal, changed_buttons

    def read_hid_status(self):
        return self.interpret_HID_packet(self.dev.read(self.endpoint.bEndpointAddress, self.endpoint.wMaxPacketSize))
