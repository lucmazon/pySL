![Alt](https://raw.github.com/lucmazon/pySL/master/gui.png)

About
=====

**pySL** is a simple OSC messages converter, with a pretty basic GUI. I use it to convert messages from my foot controller
to [SooperLooper](http://essej.net/sooperlooper/) compatible messages, but you can use it for whatever you can imagine!

Setup
=====

Requirements
------------

To make **pySL** work, there are a few things you need:

- [python 3](https://www.python.org/downloads/)
- tkinter: for the GUI
- [pyliblo](http://das.nasophon.de/pyliblo/): OSC library
- [pyYAML](http://pyyaml.org/): to read the configuration file

Basically, on an archlinux, you should do the following:

```
sudo pacman -S liblo tk python-yaml
sudo pip install pyliblo pyyaml
```

Configuration
-------------

This application only requires a single configuration file, customizable to your needs. The file format is `yaml`.
A working example is present as `sooperlooper.yaml`. There are comments all over the file so you can easily adapt it as you wish.

The configuration is composed of several parts:

- the flag `has_pedal` tells if you have a pedal or not
- the `osc` section, describing the programs to which send osc messages
- the `switches_grid` and `pedals_grid`, where you describe how your switches and pedals are disposed in a grid
- the `hardware` section, where stuff about your raw hid device are configured (current version for a teensy 2, using [pedaliero](https://github.com/lucmazon/pedaliero))
- the `layers`, where you describe the switches/pedals actions:
  - a `label` in case of switches
  - `modal` for switching between layers
  - the name of an osc receiver to send osc messages to
  (you can combine `modal` and an osc receiver if you wish)

Usage
=====

Example
-------

`sooperlooper.yaml` is a perfectly functional configuration file. Use it or interpret it!

```
$ gui.py -c sooperlooper.yaml
```

Explanation
-----------

```
usage: gui.py [-h] -c CONFIG [-d]

sends osc messages with a fancy gui

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        the configuration file
  -d, --debug           display debug logs
```
