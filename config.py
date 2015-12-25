#!/usr/bin/python3
# -*- coding: utf-8 -*-

import liblo
from typing import List

class OSCMessage:
    def __init__(self, send_value):
        self.path = send_value[0]  # type: str
        self.args = send_value[1:]  # type: str
        self.message = liblo.Message(self.path, *self.args)  # type: liblo.Message

    def __str__(self):
        return "OSCMessage({0}, {1})".format(self.path, self.args)


class Coordinates:
    def __init__(self, x, y):
        self.x = x  # type: int
        self.y = y  # type: int

    def __repr__(self):
        return "(x: {0},y: {1})".format(self.x, self.y)

class Switch:
    def __init__(self, coordinates, config_line):
        self.coordinates = Coordinates(*coordinates)  # type: Coordinates
        self.label = config_line.get('label')  # type: str
        self.modal = config_line.get('modal')
        self.osc_message = OSCMessage(config_line.get('send')) if config_line.get('send') else None  # type: OSCMessage

    def __repr__(self):
        return "<coordinates: {0}, label: '{1}', modal: {2}, osc_message: {3}>".format(self.coordinates, self.label, self.modal, self.osc_message)

class Layer:
    def __init__(self, grid, switches):
        self.switches = []  # type: List[Switch]
        for index, switch_line in enumerate(switches):
            self.switches.append(Switch(grid[index], switch_line))

    def __repr__(self):
        return repr(self.switches)

class Config:
    def __init__(self, data, args):
        self.target_port = args['target_port']
        self.target_host = args['target_host']
        self.physical_layout = data.get('physical_layout')
        self.grid = self.physical_layout.get('grid')
        self.current_layer = 0
        self.layers = []  # type: List[Layer]
        for layer_line in data.get('layers'):
            self.layers.append(Layer(self.grid, layer_line))

    def get_current_switch(self, i):
        return self.layers[self.current_layer].switches[i]

    def switch_to_layer(self, layer_index):
        self.current_layer = layer_index

    def __repr__(self):
        return "current layer: {0}, layers: {1}".format(self.current_layer, repr(self.layers))