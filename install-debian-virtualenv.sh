#!/bin/bash

sudo apt-get update
sudo apt-get install -y \
     python3 python3-pip python3-virtualenv \
     python3-qtpy \
     wodim \
     libcdio-dev libiso9660-dev python3-all-dev

virtualenv env/diagvdisk
source env/diagvdisk/bin/activate

pip3 install qtpy guietta pycdio
