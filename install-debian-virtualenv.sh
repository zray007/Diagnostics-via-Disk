#!/bin/bash

set -eu

sudo apt-get update
sudo apt-get install -y \
     python3 python3-pip python3-virtualenv \
     python3-qtpy \
     wodim

LIBCDIO_VER="$(dpkg -s libcdio-dev | grep '^Version' | cut -d':' -f 2 | cut -d'.' -f 1)"
echo $LIBCDIO_VER
if [ $LIBCDIO_VER -lt 2 ]
then
sudo add-apt-repository ppa:spvkgn/whipper -y
fi

sudo apt-get install -y \
     libcdio-dev libiso9660-dev \
     pkg-config python3-all-dev swig

python3 -m virtualenv --system-site-packages -p /usr/bin/python3 env/diagvdisk

source env/diagvdisk/bin/activate

pip3 install qtpy pycdio pyqtgraph

git clone https://github.com/fidergo-stephane-gourichon/guietta
cd guietta
pip3 install -e "$PWD"