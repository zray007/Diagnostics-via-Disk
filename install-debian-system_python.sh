#!/bin/bash

sudo apt-get update

sudo apt-get install -y \
     python3 python3-pip python3-qtpy \
     python3-cdio
     wodim git \

pip3 install qtpy

git clone https://github.com/fidergo-stephane-gourichon/guietta
cd guietta
pip3 install -e "$PWD"
