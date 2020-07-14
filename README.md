# Diagnostics Via Disk

## Ramp up COVID-19 testing using frugal devices: CD/DVD drives

This is a proof-of-concept for hackster project at https://www.hackster.io/laserx/diagnostics-via-disc-5793c0 for [The COVID-19 Detect &amp; Protect Challenge](https://www.hackster.io/contests/UNDPCOVID19)

![GUI screenshot](doc/gui-screenshot-00.png)

## How to use

* A graphical user interface.
* A command-line interface is also available.

All this is proof-of-concept level.  It works for us yet the performance might be bad with some specific hardware (CD readers) and there are conditions that we do not test (like no drive or several drives).

## Requirements

### Hardware

* Linux machine with a CD/DVD/BluRay reader/player. For example, a Raspberry Pi and a USB-to-IDE or USB-to-SATA plus external drive is fine.
* CD/DVD/BluRay disk.

### Software

The code is built upon:

* Python
* Qt (via [qtpy](https://pypi.org/project/QtPy/)) 
* [pycdio](https://pypi.org/project/pycdio/)
* [guietta](https://guietta.readthedocs.io/en/latest/).
* `readom` (from package `wodim`)

#### Quick install, on Debian and derivatives, using a ad-hoc python virtualenv

The script installs the base requirements and uses a python virtual environment for python requirements

```bash
bash install-debian-virtualenv.sh
```

#### Quick install, on Debian and derivatives, using system Python

Details are provided for a Debian-based OS (including Ubuntu and Raspberry Pi OS).  Please adjust for other Linux-based distributions.

```bash
install-debian-system_python.sh
```

### Launch software

#### Run using bash script
Opens the GUI from the bioid created by install script virtual environment
```bash
bash run.sh
```
#### Run Manually
```bash
python3 bioid-gui.py 
```

### Test access to CD-Rom drive

Click on "Open tray" and "Close tray".  The default CD/DVD drive on the system should do what you expect.

