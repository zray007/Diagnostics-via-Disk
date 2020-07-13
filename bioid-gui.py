from guietta import _, Gui, Quit, ___, III, HS, VS, HSeparator, VSeparator, QFileDialog
from guietta import Empty, Exceptions, P

import os
import subprocess
import re

from time import strftime

# Aim of the GUI.
# * Allow to start/monitor/stop a read process.
# * Show progress
# * Show graph

product_name="Diagnostics via Disk"
product_name_tech="diagnostics_via_disk"

pitch="Ramp up COVID-19 testing using frugal devices: CD/DVD drives"

gui = Gui(
    [ 'bioid-logo.png',                 'pitch',           ___ ],
    [ HSeparator,                       ___,               ___ ],
    [ 'CD/DVD drive',                   ['trayOpen'],      ['trayClose']  ],
    [ HSeparator,                       ___,               ___ ],
    [ ["generateNewIdFromCurrentTime"], ___,               'or type a valid file name below' ],
    [ 'Analysis run ID',                '__runID__',       ___ ],
    [ HSeparator,                       ___,               ___ ],
    [ 'Analysis run control:',                   ['analysisStart'], ['analysisStop'] ],
    [ HSeparator,                       ___,               ___ ],
    [ 'Programmed speed:', 'programmedSpeed' , ___ ],
    [ 'Disk capacity:', 'diskCapacity' , ___ ],
    [ 'Sector size:', 'sectorSize' , ___ ],
    [ 'Analysis progress', P('analysisProgress'), ___ ],
    #  , 'instantSpeed
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
    'programmedSpeed' : '',
    'diskCapacity' : '',
    'sectorSize' : '',
    #'instantSpeed' : '',
}

for id, label in labels.items():
    gui.widgets[id].setText(label)

runningAnalysisProcess = None
logfile_write_descriptor = None
logfile_read_descriptor = None

# TODO handle case when CD mounted...

# This syntax allows to decouple label text and name of method called, which is good practice.
def analysisStart(gui, *args):
    print("analysisStart")
    com=[ "readom", "-noerror", "-nocorr", "-c2scan", "dev=/dev/cdrom"]

    logfilename = gui.runID + ".log"

    global logfile_write_descriptor
    logfile_write_descriptor = open(logfilename, "a")

    global runningAnalysisProcess
    runningAnalysisProcess = subprocess.Popen(com,
                                              shell = False,
                                              stdout = logfile_write_descriptor,
                                              stderr = subprocess.STDOUT)

    global logfile_read_descriptor
    logfile_read_descriptor = open(logfilename, "rb")

def analysisStop(gui, *args):
    print("analysisStop")
    global runningAnalysisProcess
    runningAnalysisProcess.kill()

# This syntax allows event to run once at GUI start, which is what we want here
def generateNewIdFromCurrentTime(gui):
    gui.runID = product_name_tech + "-run_" + strftime( "%Y-%m-%d_%H-%M-%S")

generateNewIdFromCurrentTime(gui);

# This syntax allows fire-and-forget behavior useful for calling eject.
def trayOpen(gui):
    os.system("eject cdrom")

# This syntax allows fire-and-forget behavior useful for calling eject.
def trayClose(gui):
    os.system("eject -t cdrom")


#filename = QFileDialog.getOpenFileName(None, "Open File",
#                                             ".",
#                                             "Analysis run log *.bioidrun (*.bioidrun)")

def updateWidget(match_result, match_action_info):
    target_widget = match_action_info['target']
    print("updateWidget " + target_widget)
    gui.widgets[target_widget].setText(match_result.group(1))

def ignore(match_result, match_action_info):
    print ("Ignoring line: {!r}".format(match_result.string))

diskSectorCount = None

def setCapacity(match_result, match_action_info):
    gui.diskCapacity = match_result.group(1)
    global diskSectorCount
    diskSectorCount = int ( match_result.group(2) )

def updateProgress(match_result, match_action_info):
    global diskSectorCount
    currentSector = int ( match_result.group(1) )
    percentage = int ( 100 * currentSector / diskSectorCount )
    print("{!r} / {!r} = {!r}".format( currentSector, diskSectorCount , percentage ) )
    gui.analysisProgress = percentage

labelParseRules = {
    "Read +speed: +(.+)$" : { 'func' : updateWidget, 'target' : 'programmedSpeed',  },
    "Write +speed: +(.+)$" : { 'func' : ignore },
    "Capacity: (([0-9]+) Blocks = 427008 kBytes = 417 MBytes = 437 prMB)" : { 'func' : setCapacity },
    "addr: +([0-9]+)" : { 'func' : updateProgress },
    "Sectorsize: +(.+)$" : { 'func' : updateWidget, 'target' : 'sectorSize',  },
    }

labelParseRulesCompiled = {
    re.compile(regexpstring) : match_action_info for regexpstring, match_action_info in labelParseRules.items()
}


def updateGuiFromProcessLog():
    print("poll readom")
    global runningAnalysisProcess
    global logfile_write_descriptor
    global logfile_read_descriptor

    write_position = logfile_write_descriptor.tell()
    read_position = logfile_read_descriptor.tell()

    bytes_available = write_position - read_position

    if bytes_available > 0 :
        bytes = logfile_read_descriptor.read(bytes_available)
        print("readom said: '{!r}'".format(bytes) )
        lineread = bytes.decode("ascii")
        match_result = None
        for regexp, match_action_info in labelParseRulesCompiled.items():
            match_result = regexp.match(lineread)
            if match_result is not None:
                break

        if match_result is not None:
            print ("matched {!r} with result {!r}".format(regexp.pattern, match_result))
            function_to_call = match_action_info['func']
            function_to_call(match_result, match_action_info)
        else:
            print ("Warning unmatched: {!r}".format(lineread))
            print ("Warning unmatched: {!r}".format(lineread))


    if runningAnalysisProcess.poll() is not None:
        print("process has exited")
        runningAnalysisProcess = None
        return


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
