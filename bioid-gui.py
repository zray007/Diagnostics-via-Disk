from guietta import _, Gui, Quit, ___, III, HS, VS, HSeparator, VSeparator, QFileDialog
from guietta import Empty, Exceptions

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
    title= title + " - " + pitch,
    exceptions = Exceptions.PRINT
)

pipeToRunningAnalysis = None

# TODO handle case when CD mounted...

# This syntax allows to decouple label text and name of method called, which is good practice.
def analysisStart(gui, *args):
    print("analysisStart")
    com=[ "readom", "-noerror", "-nocorr", "-c2scan", "dev=/dev/cdrom"]

    global pipeToRunningAnalysis
    pipeToRunningAnalysis = subprocess.Popen(com,
                               shell = False,
                               stdout = subprocess.PIPE,
                               stderr = subprocess.PIPE,
                               encoding = 'ascii',
                               universal_newlines=True)

def analysisStop(gui, *args):
    print("analysisStop")
    global pipeToRunningAnalysis
    pipeToRunningAnalysis.kill()

gui.events([ _ , _ , _ ],
           [ _ , _ , _ ],
           [ _ , _ , _ ],
           [ _ , _ , _ ],
           [ _ , _ , _ ],
           [ _ , _ , _ ],
           [ _ , _ , _ ],
           [ _ , analysisStart, analysisStop ],
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

def processRunningAnalysis():
    print("poll readom")
    global pipeToRunningAnalysis
    stdout_data = None
    stderr_data = None
    try:
        stdout_data, stderr_data = pipeToRunningAnalysis.communicate(timeout=0)
    except subprocess.TimeoutExpired:
        print("readom timeout: {!r}".format(stdout_data))
        return
        print("readom says: {!r}".format(stdout_data))


counter = 0
while True:
    try:
        name, event = gui.get(timeout=0.1)
    except Empty:
        print("poll")
        if pipeToRunningAnalysis is not None:
            processRunningAnalysis()
        continue

    if name is None:
        print("Exiting event loop")
        break
