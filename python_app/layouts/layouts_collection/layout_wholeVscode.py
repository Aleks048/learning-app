import os, subprocess
from time import sleep
from threading import Thread

import layouts.layouts_utils as lu

import _utils._utils_main as _u
import _utils.logging as log
import UI.widgets_facade as wm
import tex_file.tex_file_facade as tm
import file_system.file_system_manager as fsm
import data.temp as dt
import scripts.osascripts as oscr

import layouts.layouts_common as lc

class WholeVSCodeLayout(lc.Layout):
    layoutUInames = []
    pyAppDimensions = [None, None]
   
    @classmethod
    def set(cls, mainWinRoot):
        mainWinRoot.geometry(str(cls.pyAppDimensions[0]) + "x" + str(cls.pyAppDimensions[1]))

        mon_windth, mon_height = _u.getMonitorSize()
        # vscode open
        ownerName, windowID, ownerPID = _u.getOwnersName_windowID_ofApp("vscode")
        cmd = oscr.getMoveWindowCMD(ownerPID, 
                                [mon_windth, mon_height , 0 , 0])
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()