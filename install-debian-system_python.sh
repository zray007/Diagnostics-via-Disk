#!/bin/bash

sudo apt-get update

sudo apt-get install -y \
     python3 python3-pip python3-qtpy \
     python3-cdio
     wodim git \

pip3 install --no-dependencies guietta

# The `--no-deps` option is because Ubuntu provides `PyQt5` which
# guietta can use, although dependencies tell `PySide2` is mandatory,
# so we have to instruct pip .
