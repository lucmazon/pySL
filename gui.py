#!/usr/bin/env python

from Tkinter import *
import sys
import argparse
import threading
import liblo
# pip install pyliblo
import commentjson
# pip install commentjson

class Item:
    def __init__(self, id, label, send, bank, row, column):
        self.id = id
        self.label = label
        self.send = send
        self.bank = bank
        self.row = row
        self.column = column

class Config:
    def __init__(self, data, args):
        self.layout = data['layout']
        self.grid = self.layout['grid']
        self.banks = data['banks']
        self.current_bank = 0
        self.input_port = args['input_port']
        self.target_port = args['target_port']
        self.target_host = args['target_host']

    def update_bank(self, item):
        if item.bank == "next":
            if self.current_bank == len(self.banks) - 1:
                self.current_bank = 0
            else:
                self.current_bank += 1
            return True
        elif item.bank == "previous":
            if self.current_bank == 0:
                self.current_bank = len(self.banks) - 1
            else:
                self.current_bank -= 1
            return True

    def get_items(self):
        items = []
        for i in range(0, len(self.grid)):
            items.append(self.get_item(i))
        return items

    def get_item(self, i):
        bank_grid = self.banks[self.current_bank]['grid'][i]
        label = bank_grid['label']
        send = None
        bank = None
        try:
            send = bank_grid['send']
        except KeyError, err:
            pass
        try:
            bank = bank_grid['bank']
        except KeyError, err:
            pass
        row = self.grid[i][1]
        column = self.grid[i][0]
        return Item(i, label, send, bank, row, column)

class Gui:
    def __init__(self, master, config, endApplication):
        master.protocol("WM_DELETE_WINDOW", endApplication)
        self.config = config
        self.default_color = 'blue'
        self.pressed_color = 'red'
        self.config = config
        self.labels = []
        self.draw_items()

    def press_label(self, item_id):
        self.change_label_color(item_id, self.pressed_color)

    def release_label(self, item_id):
        self.change_label_color(item_id, self.default_color)

    def change_label_color(self, item_id, color):
        self.labels[item_id].config(bg=color)

    def change_label_text(self, item):
        self.labels[item.id].config(text=item.label)

    def update_labels(self):
        for item in self.config.get_items():
            self.change_label_text(item)

    def draw_items(self):
        for i, item in enumerate(self.config.grid):
            item = self.config.get_item(i)

            self.labels.append(Label(text=item.label, bg=self.default_color, fg='white', width=15))
            self.labels[i].grid(row=item.row,column=item.column)


class ThreadedClient:
    def __init__(self, master, data, args):
        self.config = Config(data, args)
        try:
            self.server = liblo.Server(self.config.input_port)
            self.target = liblo.Address(self.config.target_host, self.config.target_port)
        except liblo.ServerError, err:
            print err
            sys.exit()
        self.master = master
        self.gui = Gui(master, self.config, self.end_application)
        self.gui.draw_items()
        self.running = 1
        self.serverThread = threading.Thread(target=self.run_server)
        self.serverThread.start()

    def run_server(self):
        # register osc messages
        for message in self.config.layout["osc"]:
            self.server.add_method(message[0], None, self.server_callback)
        while self.running:
            self.server.recv(50)

    def server_callback(self, path, args):
        value = args[0]
        print "message received '%s' with value '%s'" % (path, value)
        for i, message_mapping in enumerate(self.config.layout["osc"]):
            if message_mapping[1] == value:
                print "message matches item %d" % i
                item = self.config.get_item(i)
                self.gui.press_label(i)
                if self.config.update_bank(item):
                    self.gui.update_labels()
                self.master.after(200, self.gui.release_label, i)
                if item.send:
                    print "sending osc message '%s %s'" % (item.send[0], item.send[1])
                    liblo.send(self.target, item.send[0], item.send[1])

    def end_application(self):
        self.master.destroy()
        self.running = 0

parser = argparse.ArgumentParser(description='converts osc messages with a fancy gui')
parser.add_argument('-c', '--config', required=True, help='the configuration file')
parser.add_argument('-t', '--target-host', default='localhost', help='the ip address or domain name of the machine where to send converted OSC messages')
parser.add_argument('-p', '--input-port', type=int, default=8888, help='the port on the machine receiving the OSC messages to convert')
parser.add_argument('-P', '--target-port', type=int, default=9951, help='the port on the machine where to send converted OSC messages')
args = vars(parser.parse_args())

with open(args['config']) as file:
    data = commentjson.load(file)

root = Tk()
client = ThreadedClient(root, data, args)
root.mainloop()