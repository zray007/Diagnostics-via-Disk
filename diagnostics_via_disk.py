from guietta import _, Gui, Quit, ___, III, HS, VS, HSeparator, VSeparator, QFileDialog
from guietta import Empty, Exceptions, P

import os
import subprocess
import re

from qtpy.QtGui import QFont

from time import strftime

# Aim of the GUI.
# * Allow to start/monitor/stop a read process.
# * Show progress
# * Show graph

product_name="Diagnostics via Disk"
product_name_tech="diagnostics_via_disk"
logo_path='diagnostics_via_disk-logo.png'

pitch="Ramp up COVID-19 testing\nusing frugal devices: CD/DVD drives"

driveChooseComboBox = QComboBox()

# To realign in emacs:
# C-u align-regexp
# as a regexp set this without the quotes:  '\(\),'
# let default answer '1' for the two question
# repeat? yes

gui = Gui(
    [ 'pitch'                  , ___                    , ___                    , VSeparator  , logo_path ],
    [ HSeparator               , ___                    , ___                    , III         , III       ],
    [ 'CD/DVD drive'           , ['trayOpen']           , ['trayClose']          , III         , III       ],
    [ HSeparator               , ___                    , ___                    , III         , III       ],
    [ ["genIdFromTime"]        , ___                    , 'ortype'               , III         , III       ],
    [ 'Analysis run ID'        , '__runID__'            , ___                    , III         , III       ],
    [ HSeparator               , ___                    , ___                    , III         , III       ],
    [ 'Analysis run control:'  , ['analysisStart']      , ['analysisStop']       , III         , III       ],
    [ HSeparator               , ___                    , ___                    , III         , III       ],
    [ 'Programmed speed:'      , 'programmedSpeed'      , ___                    , III         , III       ],
    [ 'Disk capacity:'         , 'diskCapacity'         , ___                    , III         , III       ],
    [ 'Sector size:'           , 'sectorSize'           , ___                    , III         , III       ],
    [ 'Analysis progress'      , P('analysisProgress')  , ___                    , III         , III       ],
    title= product_name + " - " + pitch.replace('\n'," "),
    exceptions = Exceptions.PRINT
)

labels = {
    'pitch' : pitch,
    'trayOpen' : 'Open tray',
    'trayClose' : 'Close tray',
    'genIdFromTime' : 'Generate new ID from current time',
    'analysisStart' : 'Start',
    'analysisStop' : 'Stop',
    'programmedSpeed' : '',
    'diskCapacity' : '',
    'sectorSize' : '',
    'ortype': 'or type a valid file name below',
    #'instantSpeed' : '',
}

for id, label in labels.items():
    gui.widgets[id].setText(label)


font = QFont( "Arial", 20, QFont.Bold)
titleWidget = gui.widgets['pitch']
titleWidget.setFont(font)

gui.widgets['diagnostics_via_disklogo'].setMargin(10)

runningAnalysisProcess = None
logfile_write_descriptor = None
logfile_read_descriptor = None

# TODO handle case when CD mounted...

def cb_analysisStart(gui, *args):
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
    enableOrDisableRelevantWidgets()
    global logfile_read_descriptor
    logfile_read_descriptor = open(logfilename, "rb")

def cb_analysisStop(gui, *args):
    print("analysisStop")
    global runningAnalysisProcess
    runningAnalysisProcess.kill()

def cb_genIdFromTime(gui):
    gui.runID = product_name_tech + "-run_" + strftime( "%Y-%m-%d_%H-%M-%S")

cb_genIdFromTime(gui);

def cb_trayOpen(gui):
    os.system("eject cdrom")

def cb_trayClose(gui):
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
    "Capacity: (([0-9]+) Blocks = [0-9]+ kBytes = [0-9]+ MBytes = [0-9]+ prMB)" : { 'func' : setCapacity },
    "addr: +([0-9]+)" : { 'func' : updateProgress },
    "Sectorsize: +(.+)$" : { 'func' : updateWidget, 'target' : 'sectorSize',  },
    }

labelParseRulesCompiled = {
    re.compile(regexpstring) : match_action_info for regexpstring, match_action_info in labelParseRules.items()
}

def enableOrDisableRelevantWidgets():
    running = ( runningAnalysisProcess is not None )
    gui.widgets['analysisStart'].setEnabled( not running )
    gui.widgets['analysisStop'].setEnabled( running )
    gui.widgets['trayOpen'].setEnabled( not running )
    gui.widgets['trayClose'].setEnabled( not running )
    gui.widgets['analysisProgress'].setEnabled( running )
    if not running:
        gui.analysisProgress = 0

enableOrDisableRelevantWidgets()

regexp_to_split_lines = re.compile('\r\n|\r|\n')

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
        partread = bytes.decode("ascii")
        linesread = regexp_to_split_lines.split(partread)
        for lineread in linesread:
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
        enableOrDisableRelevantWidgets()
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
    functionName = "cb_" + name
    function = globals().get(functionName, None)
    if function is None:
        print("Unknown " + functionName)
    else:
        print("Calling " + functionName + " function {!r}".format(function) )
        function(gui)
        print("Returned from " + functionName)
