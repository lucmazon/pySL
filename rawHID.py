#!/usr/bin/python3
#-*- coding: utf-8 -*-
from typing import List

import usb.core
import usb.util
from enum import Enum

MAX_POTENTIOMETER_VALUE = 255
# ID for a teensy 2
ID_VENDOR = 0x16c0
ID_PRODUCT = 0x0480

class ButtonStatus(Enum):
    PRESSED = 1
    RELEASED = 0

class Switch:
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
    def __init__(self, max_potentiometer_value=MAX_POTENTIOMETER_VALUE, id_vendor=ID_VENDOR, id_product=ID_PRODUCT, switches_range=range(2, 8), pedals_range=range(25,26)):
        self.dev = usb.core.find(idVendor=id_vendor, idProduct=id_product)
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

        self.switches_range = switches_range
        self.pedals_range = pedals_range

        self.switches_statuses = []
        for index in switches_range:
            self.switches_statuses.append(Switch(index, ButtonStatus.RELEASED))

        self.pedals_statuses = []
        for index in pedals_range:
            self.pedals_statuses.append(Pedal(index, max_potentiometer_value))

    def read_hid_status(self):
        data = self.dev.read(self.endpoint.bEndpointAddress, self.endpoint.wMaxPacketSize)

        changed_pedals = [] # type: List[Pedal]
        for index, key in enumerate(self.pedals_range):
            new_pedal = Pedal(index, data[key])
            if (self.pedals_statuses[index] != new_pedal):
                changed_pedals.append(new_pedal)
            self.pedals_statuses[index] = new_pedal

        changed_buttons = [] # type: List[Switch]
        for index, key in enumerate(self.switches_range):
            new_switch = Switch(index, ButtonStatus.PRESSED if data[key] else ButtonStatus.RELEASED)
            if (self.switches_statuses[index] != new_switch):
                changed_buttons.append(new_switch)
            self.switches_statuses[index] = new_switch

        return changed_pedals, changed_buttons
