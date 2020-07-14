#!/bin/bash

sudo apt-get update
sudo apt-get install -y \
     python3 python3-pip python3-virtualenv \
     python3-qtpy \
     wodim \
     libcdio-dev libiso9660-dev pkg-config python3-all-dev swig

python3 -m virtualenv --system-site-packages -p /usr/bin/python3 env/diagvdisk

source env/diagvdisk/bin/activate

pip3 install qtpy guietta pycdio
