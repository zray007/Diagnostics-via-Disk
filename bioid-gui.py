from guietta import _, Gui, Quit, ___, III, HS, VS, HSeparator, VSeparator, QFileDialog

import os
from time import strftime

# Aim of the GUI.
# * Allow to start/monitor/stop a read process.
# * Show progress
# * Show graph

title="Bio-ID"
pitch="Scalable COVID testing on cheap commodity hardware"

gui = Gui(
    [ 'bioid-logo.png' , "Scalable COVID testing on cheap commodity hardware", ___ ],
    [ HSeparator , ___ , ___ ],
    [ 'CD/DVD drive' , ['Open tray'] , ['Close tray'] ],
    [ HSeparator , ___ , ___ ],
    [ ['Generate new ID from current time'], ___, 'or type a valid file name below' ],
    [ 'Analysis run ID' , '__runID__' , ___ ],
    [ HSeparator , ___ , ___ ],
    [ 'Analysis run' , ['Start'] , ['Abort'] ],
    title= title + " - " + pitch
)

#if "title" in dir(gui):
#    gui.title(title + " - " + pitch)

with gui.GeneratenewIDfromcurrenttime:
    gui.runID = strftime("%Y-%m-%d_%H-%M-%S.bioidrun")

with gui.Opentray:
   if gui.is_running:
        os.system("eject cdrom")

with gui.Closetray:
   if gui.is_running:
        os.system("eject -t cdrom")


#filename = QFileDialog.getOpenFileName(None, "Open File",
#                                             ".",
#                                             "Analysis run log *.bioidrun (*.bioidrun)")

gui.run()
