#!/bin/bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-qtpy wodim eject git -y
pip3 install virtualenv
virtualenv env/diagvdisk
source env/diagvdisk/bin/activate
pip3 install qtpy guietta