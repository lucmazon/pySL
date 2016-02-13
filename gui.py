#!/usr/bin/python3
# -*- coding: utf-8 -*-

from tkinter import *
import tkinter.ttk as ttk
import argparse
import threading
import logging
import yaml
from typing import List

from config import Config
from rawHID import ButtonStatus
import config

class Gui:
    def __init__(self, master, config, end_application):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", end_application)
        self.config = config # type: Config
        self.default_color = 'blue'
        self.pressed_color = 'red'
        self.labels = [] # type: List[Label]
        self.pedals_control = [] # type: List[IntVar]
        self.draw_items()

    def trigger_label_color(self, index, button_status):
        color = self.pressed_color if button_status == ButtonStatus.PRESSED else self.default_color
        relief = SUNKEN if button_status == ButtonStatus.PRESSED else RAISED
        self.labels[index].config(bg=color, relief=relief)

    def change_label_text(self, index, label):
        self.labels[index].config(text=label)

    def update_pedal(self, id, value):
        self.pedals_control[id].set(value)

    def update_labels(self):
        for index, switch in enumerate(self.config.layers[self.config.current_layer].switches):
            self.change_label_text(index, switch.label)

    def draw_items(self):
        current_layer = self.config.layers[self.config.current_layer]
        for index, switch in enumerate(current_layer.switches):
            self.labels.append(Label(text=switch.label, bg=self.default_color, fg='white', width=15, bd=4, relief=RAISED))
            self.labels[index].grid(row=switch.coordinates.y, column=switch.coordinates.x)

        if self.config.has_pedal:
            for index, pedal in enumerate(current_layer.pedals):
                self.pedals_control.append(IntVar())
                progress = ttk.Progressbar(self.master, orient='horizontal', mode='determinate', variable=self.pedals_control[index])
                progress.grid(row=pedal.coordinates.y, column=pedal.coordinates.x)


class ThreadedClient:
    def __init__(self, master, data, args):
        self.config = config.Config(data, args)
        self.first_run = True
        self.master = master
        self.gui = Gui(master, self.config, self.end_application)
        self.running = 1
        self.serverThread = threading.Thread(target=self.run_server)
        self.serverThread.start()

    def run_server(self):
        while self.running:
            if (self.first_run):
                self.first_run = False
                continue

            changed_pedals, changed_keys = self.config.rawhid.read_hid_status()

            if self.config.has_pedal:
                for changed_pedal in changed_pedals:
                    i = changed_pedal.id
                    self.gui.update_pedal(i, changed_pedal.value)

                    pedal = self.config.get_current_pedal(i)
                    for osc_message in pedal.osc_messages:
                        value = changed_pedal.value/100
                        logging.debug("sending pedal osc message '{0}, {1} {2}'".format(osc_message.path, osc_message.args, value))
                        osc_message.send([value])

            for changed_key in changed_keys:
                i = changed_key.id
                switch = self.config.get_current_switch(i)
                self.gui.trigger_label_color(i, changed_key.status)

                if switch.modal is not None:
                    if changed_key.status == ButtonStatus.PRESSED:
                        self.config.switch_to_layer(switch.modal)
                    else:
                        self.config.switch_to_layer(0)
                self.gui.update_labels()
                if changed_key.status == ButtonStatus.PRESSED and switch.osc_messages:
                    for osc_message in switch.osc_messages:
                        logging.debug("sending osc message '{0}, {1}'".format(osc_message.path, osc_message.args))
                        osc_message.send()

    def end_application(self):
        self.master.destroy()
        self.running = 0


parser = argparse.ArgumentParser(description='sends osc messages with a fancy gui')
parser.add_argument('-c', '--config', required=True, help='the configuration file')
parser.add_argument('-d', '--debug', action='store_true', help='display debug logs')
args = vars(parser.parse_args())

with open(args['config']) as file:
    data = yaml.load(file)

debug = args['debug']
logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
root = Tk()
root.wm_title("pySL")
client = ThreadedClient(root, data, args)
root.mainloop()
