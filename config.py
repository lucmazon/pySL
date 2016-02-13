#!/usr/bin/python3
# -*- coding: utf-8 -*-

import liblo
from typing import List
from rawHID import RawHID

class OSCTarget:
    def __init__(self, osc_line):
        self.name = osc_line.get('name')
        self.host = osc_line.get('host')
        self.port = osc_line.get('port')
        self.target = liblo.Address(self.host, self.port)

    def __repr__(self):
        return "<'{0}' {1}:{2}>".format(self.name, self.host, self.port)

class OSCMessage:
    def __init__(self, osc_target, send_value):
        self.path = send_value[0]  # type: str
        self.args = send_value[1:]  # type: str
        self.osc_target = osc_target # type: OSCTarget

    def send(self, additional_args=None):
        if additional_args is None:
            additional_args = []
        args = self.args + additional_args
        liblo.send(self.osc_target.target, liblo.Message(self.path, *args))

    def __repr__(self):
        return "OSCMessage({0}, {1}, {2})".format(self.osc_target, self.path, self.args)


class Coordinates:
    def __init__(self, x, y):
        self.x = x  # type: int
        self.y = y  # type: int

    def __repr__(self):
        return "(x: {0},y: {1})".format(self.x, self.y)

class OSCEnabledSender:
    def __init__(self, osc_targets: List[OSCTarget], coordinates: Coordinates, config_line):
        self.coordinates = coordinates # type: Coordinates
        self.osc_messages = [] # type: List[OSCMessage]
        for osc_target in osc_targets:
            message = config_line.get(osc_target.name)
            if message:
                self.osc_messages.append(OSCMessage(osc_target, message))

class Pedal(OSCEnabledSender):
    def __init__(self, osc_targets: List[OSCTarget], coordinates: Coordinates, config_line):
        super().__init__(osc_targets, coordinates, config_line)

    def __repr__(self):
        return "<Pedal: {0}, osc_messages: {1}>".format(self.coordinates, self.osc_messages)

class Switch(OSCEnabledSender):
    def __init__(self, osc_targets: List[OSCTarget], coordinates: Coordinates, config_line):
        super().__init__(osc_targets, coordinates, config_line)
        self.label = config_line.get('label')  # type: str
        self.modal = config_line.get('modal')

    def __repr__(self):
        return "<coordinates: {0}, label: '{1}', modal: {2}, osc_messages: {3}>".format(self.coordinates, self.label, self.modal, self.osc_messages)

class GridItem:
    def __init__(self, grid_line):
        self.coordinates = Coordinates(*grid_line['coordinates'])
        self.type = grid_line['type']

    def __repr__(self):
        return "<type: {0}, {1}>".format(self.type, self.coordinates)

class Layer:
    def __init__(self, osc_targets, config, layer_line):
        switches_grid = [] # type: List[Coordinates]
        for grid_line in config.get('switches_grid'):
            switches_grid.append(Coordinates(*grid_line))

        pedals_grid = [] # type: List[Coordinates]
        for grid_line in config.get('pedals_grid'):
            pedals_grid.append(Coordinates(*grid_line))

        self.switches = []  # type: List[Switch]
        self.pedals = [] # type: List[Pedal]

        for index, switch_line in enumerate(layer_line.get('switches')):
            self.switches.append(Switch(osc_targets, switches_grid[index], switch_line))

        for index, pedal_line in enumerate(layer_line.get('pedals')):
            self.pedals.append(Pedal(osc_targets, pedals_grid[index], pedal_line))

    def __repr__(self):
        return repr(self.switches)

class Hardware:
    def __init__(self, hardware_config):
        self.id_vendor = hardware_config.get('id_vendor')
        self.id_product = hardware_config.get('id_product')
        self.max_potentiometer_value = hardware_config.get('max_potentiometer_value')
        self.switches = hardware_config.get('switches')
        self.pedals = hardware_config.get('pedals')

class Config:
    def __init__(self, data, args):
        self.current_layer = 0

        self.has_pedal = data.get('has_pedal')

        self.osc_targets = [] # type: List[OSCTarget]
        for osc_line in data.get('osc'):
            self.osc_targets.append(OSCTarget(osc_line))

        hardware = Hardware(data.get('hardware'))
        self.rawhid = RawHID(max_potentiometer_value=hardware.max_potentiometer_value, id_product=hardware.id_product, id_vendor=hardware.id_vendor)

        self.layers = []  # type: List[Layer]
        for layer in data.get('layers'):
            self.layers.append(Layer(self.osc_targets, data, layer))

    def get_current_switch(self, i):
        return self.layers[self.current_layer].switches[i]

    def get_current_pedal(self, i):
        return self.layers[self.current_layer].pedals[i]

    def switch_to_layer(self, layer_index):
        self.current_layer = layer_index

    def __repr__(self):
        return "osc targets: {0}, current layer: {1}, layers: {2}".format(repr(self.osc_targets), self.current_layer, repr(self.layers))