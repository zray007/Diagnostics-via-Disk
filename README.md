# Bio-ID

## Scalable COVID testing on cheap commodity hardware: CD/DVD drives

Work in progress!

## How to use

* A graphical user interface.
* A command-line interface is also available.

All this is proof-of-concept level.  It works for us yet the performance might be bad with some specific hardware (CD readers) and there are conditions that we do not test (like no drive or several drives).

## Graphical user interface

### Requirements

* Linux machine with a CD/DVD/BluRay reader/player. For example, a Raspberry Pi and a USB-to-IDE or USB-to-SATA plus external drive is fine.
* CD/DVD/BluRay disk.
* Some packages installed.  Details are provided for a Debian-based OS (including Ubuntu and Raspberry OS).  Please adjust for other Linux-based distributions.

System-wide packages:

```bash
sudo apt-get update ; sudo apt-get install python3 python3-pip wodim python3-pyside2.qtcore python3-pyside2.qtgui python3-pyside2.qtwidgets
```

FIXME: assumes Intel architecture in practice.

The GUI is built upon Python and [guietta](https://guietta.readthedocs.io/en/latest/).

User-wide packages:

```bash
pip3 install guietta
```

### Launch software

```bash
python3 bioid-gui.py 
```

### Test access to CD-Rom drive

Click on "Open tray" and "Close tray".  The default CD/DVD drive on the system should do what you expect.


