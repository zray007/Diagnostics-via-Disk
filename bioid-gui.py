from guietta import _, Gui, Quit, ___, III, HS, VS, HSeparator, VSeparator, QFileDialog

import os
import subprocess

from time import strftime

# Aim of the GUI.
# * Allow to start/monitor/stop a read process.
# * Show progress
# * Show graph

title="Bio-ID"
pitch="Scalable COVID testing on cheap commodity hardware"

gui = Gui(
    [ 'bioid-logo.png',                      "Scalable COVID testing on cheap commodity hardware", ___ ],
    [ HSeparator,                            ___,                                                  ___ ],
    [ 'CD/DVD drive',                        ['Open tray'],                                        ['Close tray']  ],
    [ HSeparator,                            ___,                                                  ___ ],
    [ ['Generate new ID from current time'], ___,                                                  'or type a valid file name below' ],
    [ 'Analysis run ID',                     '__runID__',                                          ___ ],
    [ HSeparator,                            ___,                                                  ___ ],
    [ 'Analysis run',                        ['Start'],                                            ['Abort']   ],
    title= title + " - " + pitch
)

# This syntax allows to decouple label text and name of method called, which is good practice.

def analysisStart(gui, *args):
    com=[ "readom", "-noerror", "-nocorr", "-c2scan", "dev=/dev/cdrom"]
    myPopen = subprocess.Popen(com,
                               shell = False,
                               stdout = subprocess.PIPE,
                               stderr = subprocess.PIPE,
                               encoding = 'ascii',
                               universal_newlines=True)
    while True:
        line = myPopen.stdout.readline()
        if line == '' and myPopen.poll() is not None:
            break
    returnStatus = myPopen.poll()
    if returnStatus != 0:
        raise RuntimeError('Problem')

gui.events([ _ , _ , _ ],
           [ _ , _ , _ ],
           [ _ , _ , _ ],
           [ _ , _ , _ ],
           [ _ , _ , _ ],
           [ _ , _ , _ ],
           [ _ , _ , _ ],
           [ _ , analysisStart, _ ],
)

#if "title" in dir(gui):
#    gui.title(title + " - " + pitch)

# This syntax allows event to run once at GUI start, which is what we want here
with gui.GeneratenewIDfromcurrenttime:
    gui.runID = strftime("%Y-%m-%d_%H-%M-%S.bioidrun")

# This syntax allows fire-and-forget behavior useful for calling eject.
with gui.Opentray:
   if gui.is_running:
        os.system("eject cdrom")

# This syntax allows fire-and-forget behavior useful for calling eject.
with gui.Closetray:
   if gui.is_running:
        os.system("eject -t cdrom")


#filename = QFileDialog.getOpenFileName(None, "Open File",
#                                             ".",
#                                             "Analysis run log *.bioidrun (*.bioidrun)")

gui.run()
