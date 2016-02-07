#!/usr/bin/python3
# -*- coding: utf-8 -*-

from tkinter import *
import argparse
import threading
import yaml

from rawHID import RawHID, ButtonStatus
import config

class Gui:
    def __init__(self, master, config, end_application):
        master.protocol("WM_DELETE_WINDOW", end_application)
        self.config = config
        self.default_color = 'blue'
        self.pressed_color = 'red'
        self.config = config
        self.labels = []
        self.draw_items()

    def trigger_label_color(self, index, button_status):
        color = self.pressed_color if button_status == ButtonStatus.PRESSED else self.default_color
        relief = SUNKEN if button_status == ButtonStatus.PRESSED else RAISED
        self.labels[index].config(bg=color, relief=relief)

    def change_label_text(self, index, label):
        self.labels[index].config(text=label)

    def update_labels(self):
        for index, switch in enumerate(self.config.layers[self.config.current_layer].switches):
            self.change_label_text(index, switch.label)

    def draw_items(self):
        for index, switch in enumerate(self.config.layers[self.config.current_layer].switches):
            self.labels.append(
                Label(text=switch.label, bg=self.default_color, fg='white', width=15, bd=4, relief=RAISED))
            self.labels[index].grid(row=switch.coordinates.y, column=switch.coordinates.x)


class ThreadedClient:
    def __init__(self, master, data, args):
        self.config = config.Config(data, args)
        self.first_run = True
        self.master = master
        self.gui = Gui(master, self.config, self.end_application)
        self.gui.draw_items()
        self.rawhid = RawHID()
        self.running = 1
        self.serverThread = threading.Thread(target=self.run_server)
        self.serverThread.start()

    def run_server(self):
        while self.running:
            changed_keys = self.rawhid.read_hid_status()
            if (self.first_run):
                self.first_run = False
                continue

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
                        print("sending osc message '{0}, {1}'".format(osc_message.path, osc_message.args))
                        osc_message.send()

    def end_application(self):
        self.master.destroy()
        self.running = 0


parser = argparse.ArgumentParser(description='converts osc messages with a fancy gui')
parser.add_argument('-c', '--config', required=True, help='the configuration file')
args = vars(parser.parse_args())

with open(args['config']) as file:
    data = yaml.load(file)

root = Tk()
root.wm_title("pySL")
client = ThreadedClient(root, data, args)
root.mainloop()
