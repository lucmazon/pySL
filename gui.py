#!/usr/bin/env python

from Tkinter import *
import json
import liblo,sys


with open("mapping.json") as file:
    data = json.load(file)

print data

layout = data["layout"]
grid = layout["grid"]

root = Tk()

default_color = 'blue'
pressed_color = 'red'

current_bank = 0

def callback(path, args):
    value = args[0]
    print "message received '%s' with value '%s'" % (path, value)
    for i, message_mapping in enumerate(layout["osc"]):
        if message_mapping[1] == value:
            print "message matches item %d" % i
            draw_items(current_bank, i)

def draw_items(bank_id, item_id=-1):
    for i, item in enumerate(grid):
        current_color = default_color

        banks = data["banks"]
        bank_grid = banks[bank_id]["grid"][i]
        label = bank_grid["label"]
        row = grid[i][0]
        column = grid[i][1]

        bank = 0
        if i == item_id:
            try:
                bank = bank_grid["bank"]
            except KeyError, err:
                pass
            current_color = pressed_color
            
        Label(text=label, bg=current_color, fg='white', width=15).grid(row=row,column=column)

        global current_bank
        current_bank = current_bank + bank
        if current_bank >= len(data["banks"]):
            current_bank = 0

def loop():
    result = server.recv(0)
    if not result:
        draw_items(current_bank)
    root.after(50, loop)

try:
    server = liblo.Server(8888)
    target = liblo.Server(8000)
except liblo.ServerError, err:
    print err
    sys.exit()

# register osc messages
for message in layout["osc"]:
    server.add_method(message[0], None, callback)
    
draw_items(current_bank)
root.after(0, loop)
mainloop()
