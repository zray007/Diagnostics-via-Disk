#!/bin/bash

set -eu

#sudo apt-get update

function provide_python_module()
{
    PYMODNAME="$1"
    shift

    echo -n "Module $PYMODNAME..."
    dpkg -l python3-$PYMODNAME | grep ^ii && { echo "already installed" ; return 0  ; }

    echo

    sudo apt-get install -y "python3-$PYMODNAME" && { echo "Modyle $PYMODNAME installed via apt-get" ; return 0  ; }

    if [ -n "$*" ]
    then
        echo -n "Module ${PYMODNAME}: installing native dependencies..."
        sudo apt-get install -y "$@"
    fi

    echo -n "Module ${PYMODNAME}: installing via pip..."
    pip3 install $PYMODNAME
}

provide_python_module pip

provide_python_module qtpy

sudo apt-get install -y \
     wodim git

# Special case
function provide_python_cdio()
{
    sudo apt-get install -y python3-cdio && return 0

    echo "No python3-cdio, let's try to install it with correct libcdio"
    sudo apt-get install -y libcdio-dev

    LIBCDIO_VER="$(dpkg -s libcdio-dev | grep '^Version' | cut -d':' -f 2 | cut -d'.' -f 1)"
    echo $LIBCDIO_VER
    if [ $LIBCDIO_VER -lt 2 ]
    then
        sudo add-apt-repository ppa:spvkgn/whipper -y
    fi

    provide_python_module setuptools

    sudo apt-get install -y \
         libiso9660-dev \
         pkg-config python3-all-dev swig

    pip3 install pycdio
}

provide_python_cdio

provide_python_module scipy
provide_python_module numpy

ls -al /usr/lib/*/libf77blas.so.3 || sudo apt-get install libatlas3-base

provide_python_module pyqtgraph


if pip3 freeze | grep guietta.*git.*fidergo
then
    echo "Assuming guietta is okay."
else
    git clone https://github.com/fidergo-stephane-gourichon/guietta || echo "Assuming a correct clone is already there."
    cd guietta && pip3 install -e "$PWD"
fi
