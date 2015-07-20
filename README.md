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

Basically, on an Ubuntu, you should do the following:

```
sudo apt-get install python3-tk
sudo pip3 install pyliblo pyyaml
```

Configuration
-------------

There's only one file you should edit or copy to configure how the application runs, and it's the `config.yaml` file.

There are comments all over the file so you can easily adapt it to your needs.

The configuration is composed of two parts, the `layout`, describing how your footswitches (or whatever you uses) are disposed and will be mapped by the application, and the `banks` saying what message to send when each button is pressed.

There can be multiple banks and you can use one of your switches to navigate between the different banks.

Usage
=====

Example
-------

```
$ gui.py -c config.yaml -t 192.168.1.10 -p 8000 -P 9951
```

Explanation
-----------

```
$ gui.py -h
usage: gui.py [-h] -c CONFIG [-t TARGET_HOST] [-p INPUT_PORT] [-P TARGET_PORT]

converts osc messages with a fancy gui

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        the configuration file
  -t TARGET_HOST, --target-host TARGET_HOST
                        the ip address or domain name of the machine where to
                        send converted OSC messages
  -p INPUT_PORT, --input-port INPUT_PORT
                        the port on the machine receiving the OSC messages to
                        convert
  -P TARGET_PORT, --target-port TARGET_PORT
                        the port on the machine where to send converted OSC
                        messages
```

To work correctly, **pySL** needs at least the config file you created above. The other parameters have the following default values:

- **TARGET_HOST**: localhost
- **INPUT_PORT**: 8888
- **TARGET_POST**: 9951 (SooperLooper's default OSC port)