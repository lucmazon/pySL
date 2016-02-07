#!/usr/bin/python3
# -*- coding: utf-8 -*-

import liblo
from typing import List

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
        self.message = liblo.Message(self.path, *self.args)  # type: liblo.Message

    def send(self):
        liblo.send(self.osc_target.target, self.message)

    def __repr__(self):
        return "OSCMessage({0}, {1}, {2})".format(self.osc_target, self.path, self.args)


class Coordinates:
    def __init__(self, x, y):
        self.x = x  # type: int
        self.y = y  # type: int

    def __repr__(self):
        return "(x: {0},y: {1})".format(self.x, self.y)

class Switch:
    def __init__(self, osc_targets: List[OSCTarget], coordinates, config_line):
        self.coordinates = Coordinates(*coordinates)  # type: Coordinates
        self.label = config_line.get('label')  # type: str
        self.modal = config_line.get('modal')
        self.osc_messages = [] # type: List[OSCMessage]
        for osc_target in osc_targets:
            message = config_line.get(osc_target.name)
            if message:
                self.osc_messages.append(OSCMessage(osc_target, message))

    def __repr__(self):
        return "<coordinates: {0}, label: '{1}', modal: {2}, osc_messages: {3}>".format(self.coordinates, self.label, self.modal, self.osc_messages)

class Layer:
    def __init__(self, osc_targets, grid, switches):
        self.switches = []  # type: List[Switch]
        for index, switch_line in enumerate(switches):
            self.switches.append(Switch(osc_targets, grid[index], switch_line))

    def __repr__(self):
        return repr(self.switches)

class Config:
    def __init__(self, data, args):
        self.physical_layout = data.get('physical_layout')
        self.grid = self.physical_layout.get('grid')
        self.current_layer = 0

        self.osc_targets = [] # type: List[OSCTarget]
        for osc_line in data.get('osc'):
            self.osc_targets.append(OSCTarget(osc_line))

        self.layers = []  # type: List[Layer]
        for layer_line in data.get('layers'):
            self.layers.append(Layer(self.osc_targets, self.grid, layer_line))

    def get_current_switch(self, i):
        return self.layers[self.current_layer].switches[i]

    def switch_to_layer(self, layer_index):
        self.current_layer = layer_index

    def __repr__(self):
        return "osc targets: {0}, current layer: {1}, layers: {2}".format(repr(self.osc_targets), self.current_layer, repr(self.layers))