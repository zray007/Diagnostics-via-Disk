from guietta import _, Gui, Quit, ___, III, HS, VS, HSeparator, VSeparator, QFileDialog
from guietta import Empty, Exceptions

import os
import subprocess

from time import strftime

# Aim of the GUI.
# * Allow to start/monitor/stop a read process.
# * Show progress
# * Show graph

product_name="Bio-ID"
pitch="Scalable COVID testing on cheap commodity hardware"

gui = Gui(
    [ 'bioid-logo.png',                 'pitch',           ___ ],
    [ HSeparator,                       ___,               ___ ],
    [ 'CD/DVD drive',                   ['trayOpen'],      ['trayClose']  ],
    [ HSeparator,                       ___,               ___ ],
    [ ["generateNewIdFromCurrentTime"], ___,               'or type a valid file name below' ],
    [ 'Analysis run ID',                '__runID__',       ___ ],
    [ HSeparator,                       ___,               ___ ],
    [ 'Analysis run',                   ['analysisStart'], ['analysisStop'] ],
    title= product_name + " - " + pitch,
    exceptions = Exceptions.PRINT
)

labels = {
    'pitch' : pitch,
    'trayOpen' : 'Open tray',
    'trayClose' : 'Close tray',
    'generateNewIdFromCurrentTime' : 'Generate new ID from current time',
    'analysisStart' : 'Start',
    'analysisStop' : 'Stop',
}

for id, label in labels.items():
    gui.widgets[id].setText(label)

runningAnalysisProcess = None

# TODO handle case when CD mounted...

# This syntax allows to decouple label text and name of method called, which is good practice.
def analysisStart(gui, *args):
    print("analysisStart")
    com=[ "readom", "-noerror", "-nocorr", "-c2scan", "dev=/dev/cdrom"]

    global runningAnalysisProcess
    runningAnalysisProcess = subprocess.Popen(com,
                               shell = False,
                               stdout = subprocess.PIPE,
                               stderr = subprocess.PIPE,
                               encoding = 'ascii',
                               universal_newlines=True)

def analysisStop(gui, *args):
    print("analysisStop")
    global runningAnalysisProcess
    runningAnalysisProcess.kill()

# This syntax allows event to run once at GUI start, which is what we want here
def generateNewIdFromCurrentTime(gui):
    gui.runID = strftime("%Y-%m-%d_%H-%M-%S.bioidrun")

# This syntax allows fire-and-forget behavior useful for calling eject.
def trayOpen(gui):
    os.system("eject cdrom")

# This syntax allows fire-and-forget behavior useful for calling eject.
def trayClose(gui):
    os.system("eject -t cdrom")


#filename = QFileDialog.getOpenFileName(None, "Open File",
#                                             ".",
#                                             "Analysis run log *.bioidrun (*.bioidrun)")

def updateGuiFromProcessLog():
    print("poll readom")
    global runningAnalysisProcess
    stdout_data = None
    stderr_data = None
    try:
        stdout_data, stderr_data = runningAnalysisProcess.communicate(timeout=0)
    except subprocess.TimeoutExpired:
        print("readom timeout: {!r}".format(stdout_data))
        return
        print("readom says: {!r}".format(stdout_data))


while True:
    try:
        name, event = gui.get(timeout=0.1)
    except Empty:
        print("poll")
        if runningAnalysisProcess is not None:
            updateGuiFromProcessLog()
        continue

    if name is None:
        print("Exiting event loop")
        break

    print("Event {!r}".format(name))
    function = globals().get(name, None)
    if function is None:
        print("Unknown " + name)
    else:
        print("Calling " + name)
        function(gui)
        print("Returned from " + name)
