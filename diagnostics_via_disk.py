from guietta import _, Gui, Quit, ___, III, HS, VS, HSeparator, VSeparator, QFileDialog
from guietta import Empty, Exceptions, P, PG

import os
import subprocess
import re
import cdio
import pycdio
import numpy as np
import math

from qtpy.QtGui import QFont
from qtpy.QtWidgets import QComboBox

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
    [ 'Available drives:'      , driveChooseComboBox    , [ 'refreshDrivesList' ], III         , III       ],
    [ 'CD/DVD drive'           , ['trayOpen']           , ['trayClose']          , III         , III       ],
    [ HSeparator               , ___                    , ___                    , III         , III       ],
    [ ["genIdFromTime"]        , ___                    , 'ortype'               , III         , III       ],
    [ 'Analysis run ID:'       , '__runID__'            , ___                    , III         , III       ],
    [ HSeparator               , ___                    , ___                    , III         , III       ],
    [ 'Analysis run control:'  , ['analysisStart']      , ['analysisStop']       , III         , III       ],
    [ HSeparator               , ___                    , ___                    , III         , III       ],
    [ 'Disk type:'             , 'diskType'             , ___                    , III         , III       ],
    [ 'Programmed speed:'      , 'programmedSpeed'      , ___                    , III         , III       ],
    [ 'Disk capacity:'         , 'diskCapacity'         , ___                    , III         , III       ],
    [ 'Sector size:'           , 'sectorSize'           , ___                    , III         , III       ],
    [ 'Analysis progress'      , P('analysisProgress')  , ___                    , III         , III       ],
    [ PG('plot') ],
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
    'diskType' : '',
    'diskCapacity' : '',
    'sectorSize' : '',
    'ortype': 'or type a valid file name below',
    'refreshDrivesList' : 'Update list',
    #'instantSpeed' : '',
}

for id, label in labels.items():
    gui.widgets[id].setText(label)

font = QFont( "Arial", 20, QFont.Bold)
titleWidget = gui.widgets['pitch']
titleWidget.setFont(font)

gui.widgets['diagnostics_via_disklogo'].setMargin(10)


drive = None
drive_name = None


runningAnalysisProcess = None
logfile_write_descriptor = None
logfile_read_descriptor = None



def enableOrDisableRelevantWidgets():
    running = ( runningAnalysisProcess is not None )
    gui.widgets['trayOpen'].setEnabled( drive is not None and not running )
    gui.widgets['trayClose'].setEnabled( drive is not None and not running )

    gui.widgets['analysisStart'].setEnabled( not running )
    gui.widgets['analysisStop'].setEnabled( running )
    gui.widgets['analysisProgress'].setEnabled( running )
    if not running:
        gui.analysisProgress = 0

enableOrDisableRelevantWidgets()



err_no_drive='NO DRIVE DETECTED'

def hands_off_the_drive(*args):
    global drive
    drive = None
    global drive_name
    drive_name = 'No drive selected'
    cb_refreshDrivesList()


def cb_refreshDrivesList(*args):
    drives = cdio.get_devices(pycdio.DRIVER_UNKNOWN)
    driveChooseComboBox.clear()
    if len(drives):
        driveChooseComboBox.addItems(drives)
    else:
        driveChooseComboBox.addItem(err_no_drive)

cb_refreshDrivesList()

def cb_QComboBox(*args):
    global drive
    global drive_name
    selectedName = driveChooseComboBox.currentText()
    print("Selected drive named {!r}", selectedName)
    if (selectedName == err_no_drive):
        drive = None
        drive_name = selectedName
    else:
        try:
            drive = cdio.Device(selectedName)
            drive_name = selectedName
        except OSError:
            drive = None
            drive_name = 'No drive selected'
            cb_refreshDrivesList()

    print("Selected drive named {!s} object {!r}".format(drive_name, drive))
    enableOrDisableRelevantWidgets()

cb_QComboBox()




# TODO handle case when CD mounted...

def cb_analysisStart(gui, *args):
    print("analysisStart")

    global drive
    try:
        mode = drive.get_disc_mode()
    except (cdio.DriverError, OSError):
        hands_off_the_drive()
        return

    gui.diskType = mode

    global maxSectorsOnThisDiscTechnology
    # There are many cases (80 minutes CD, and variations between
    # DVD+- and DVD-SL DVD-DL).  So far only covering main cases.
    if re.match(r"DVD", mode):
        # Source https://en.wikipedia.org/wiki/DVD#Capacity
        maxSectorsOnThisDiscTechnology = 4171712 # assuming DVD-DL!
    else:
        # Source https://en.wikipedia.org/wiki/CD-ROM#Capacity
        maxSectorsOnThisDiscTechnology = 333000

    com=[ "readom", "-noerror", "-nocorr", "-c2scan", "meshpoints=1000", "dev=" + drive_name ]

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
    global drive
    try:
        drive.eject_media()
    except cdio.DriverError:
        hands_off_the_drive()

def cb_trayClose(gui):
    global drive_name
    try:
        cdio.close_tray(drive_name)
    except cdio.DriverError:
        hands_off_the_drive()



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
sectorNumToMillimeter = None
c2data = None

def setCapacity(match_result, match_action_info):
    gui.diskCapacity = match_result.group(1)
    global diskSectorCount
    diskSectorCount = int ( match_result.group(2) )
    global c2data
    print("Initializing c2data with {} elements.".format(diskSectorCount))
    c2data = np.empty(diskSectorCount)
    global sectorNumToMillimeter
    sectorNumToMillimeter = np.empty(diskSectorCount)

    global maxSectorsOnThisDiscTechnology
    for sector in range(len(sectorNumToMillimeter)):
        sectorNumToMillimeter[sector] = \
            math.sqrt( sector / maxSectorsOnThisDiscTechnology \
                       * (58 * 58 - 25 * 25) + 25 * 25 ) # minor repetition, yet simple and fast

def updateProgress(match_result, match_action_info):
    global diskSectorCount
    currentSector = int ( match_result.group(1) )
    percentage = int ( 100 * currentSector / diskSectorCount )
    print("{!r} / {!r} = {!r}".format( currentSector, diskSectorCount , percentage ) )
    gui.analysisProgress = percentage

def updateGraphData(match_result, match_action_info):
    global c2data
    sectorInError = int ( match_result.group(1) )
    errorCount = int ( match_result.group(2) )
    global c2data
    print("Setting c2data{0} {1}.".format(sectorInError, errorCount))
    c2data[sectorInError] = errorCount

    gui.plot.setDownsampling(mode='peak')
    gui.plot.plot(sectorNumToMillimeter, c2data, title="C2 errors", clear=True)

labelParseRules = {
    "Read +speed: +(.+)$" : { 'func' : updateWidget, 'target' : 'programmedSpeed',  },
    "Write +speed: +(.+)$" : { 'func' : ignore },
    "Capacity: (([0-9]+) Blocks = [0-9]+ kBytes = [0-9]+ MBytes = [0-9]+ prMB)" : { 'func' : setCapacity },
    "addr: +([0-9]+)" : { 'func' : updateProgress },
    "Sectorsize: +(.+)$" : { 'func' : updateWidget, 'target' : 'sectorSize',  },
    "Copy from SCSI .+ disk to file '/dev/null'" : { 'func' : ignore },
    'C2 in sector: ([0-9]+) first at byte:  ([0-9]+) .+ total:   ([0-9]+) errors' : { 'func' : updateGraphData },
    "^$" : { 'func' : ignore },
    }

labelParseRulesCompiled = {
    re.compile(regexpstring) : match_action_info for regexpstring, match_action_info in labelParseRules.items()
}

regexp_to_split_lines = re.compile('\r\n|\r|\n')

def updateGuiFromProcessLog():
    #print("poll readom")
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
        #print("poll")
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
