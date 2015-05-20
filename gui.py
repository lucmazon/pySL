#!/usr/bin/env python

from Tkinter import *
import json, liblo, sys, argparse

parser = argparse.ArgumentParser(description='converts osc messages with a fancy gui')
parser.add_argument('-c', '--config', required=True, help='the configuration file')
parser.add_argument('-t', '--target-host', default='localhost', help='the ip address or domain name of the machine where to send converted OSC messages')
parser.add_argument('-p', '--input-port', type=int, default=8888, help='the port on the machine receiving the OSC messages to convert')
parser.add_argument('-P', '--target-port', type=int, default=9951, help='the port on the machine where to send converted OSC messages')
args = vars(parser.parse_args())

with open(args['config']) as file:
    data = json.load(file)

layout = data["layout"]
grid = layout["grid"]
banks = data["banks"]

root = Tk()

default_color = 'blue'
pressed_color = 'red'

current_bank = 0

def unpack(i):
    bank_grid = banks[current_bank]["grid"][i]
    label = bank_grid["label"]
    send = None
    bank = None
    try:
        send = bank_grid["send"]
    except KeyError, err:
        pass
    try:
        bank = bank_grid["bank"]
    except KeyError, err:
        pass
    row = grid[i][0]
    column = grid[i][1]
    return banks, bank_grid, label, send, bank, row, column
    
def callback(path, args):
    value = args[0]
    print "message received '%s' with value '%s'" % (path, value)
    for i, message_mapping in enumerate(layout["osc"]):
        if message_mapping[1] == value:
            print "message matches item %d" % i
            draw_items(i)
            banks, bank_grid, label, send, bank, row, column = unpack(i)
            update_bank(bank)
            if send:
                print "sending osc message '%s %s'" % (send[0], send[1])
                liblo.send(target, send[0], send[1])
                       
def draw_items(item_id=-1):
    for i, item in enumerate(grid):
        current_color = default_color

        banks, bank_grid, label, send, bank, row, column = unpack(i)

        if i == item_id:
            current_color = pressed_color
            
        Label(text=label, bg=current_color, fg='white', width=15).grid(row=row,column=column)

def update_bank(bank_value):
    global current_bank
    print bank_value
    if bank_value == "next":
        if current_bank == len(banks) - 1:
            current_bank = 0
        else:
            current_bank += 1
    elif bank_value == "previous":
        if current_bank == 0:
            current_bank = len(banks) - 1
        else:
            current_bank -= 1


def loop():
    result = server.recv(0)
    if not result:
        draw_items()
    root.after(50, loop)

try:
    server = liblo.Server(args['input_port'])
    target = liblo.Address(args['target_host'], args['target_port'])
except liblo.ServerError, err:
    print err
    sys.exit()

# register osc messages
for message in layout["osc"]:
    server.add_method(message[0], None, callback)
    
draw_items(current_bank)
root.after(0, loop)
mainloop()
