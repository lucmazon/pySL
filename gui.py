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

try:
    server = liblo.Server(8888)
except liblo.ServerError, err:
    print err
    sys.exit()

def button(path, args):
    pressed = args[0]
    print "message received '%s' with index '%d'" % (path, pressed)
    draw_items(0, pressed-1)

server.add_method('/pedalBoard/button' , 'i', button)

def draw_items(bank_id, item_id=-1):
    for i, item in enumerate(grid):
        current_color = default_color
        label = data["banks"][bank_id]["grid"][i]["label"]
        row = grid[i][0]
        column = grid[i][1]
        
        if i == item_id:
            current_color = pressed_color
            
        Label(text=label, bg=current_color, fg='white', width=15).grid(row=row,column=column)

def loop():
    result = server.recv(0)
    if not result:
        draw_items(0)
    root.after(50, loop)
        
def task(index):
    color = ['blue', 'red']
    if index > 1:
        index = 0
    for i, item in enumerate(grid):
        Label(text=data["banks"][0]["grid"][i]["label"], bg=color[index], fg='white', relief=RIDGE,width=15).grid(row=grid[i][0],column=grid[i][1])
    root.after(500, task, index + 1)
    

draw_items(0)
root.after(0, loop)
mainloop()
