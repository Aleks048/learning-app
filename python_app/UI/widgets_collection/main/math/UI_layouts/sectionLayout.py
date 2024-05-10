import tkinter as tk
from threading import Thread
import subprocess

import UI.widgets_wrappers as ww
import file_system.file_system_facade as fsm
import _utils.logging as log
import tex_file.tex_file_facade as tff
import scripts.osascripts as oscr
import data.temp as dt
import data.constants as dc

import _utils._utils_main as _u
import _utils.pathsAndNames as _upan

import outside_calls.outside_calls_facade as ocf

import UI.widgets_collection.main.math.manager as mmm
import UI.widgets_collection.main.math.UI_layouts.common as comui
import UI.widgets_manager as wm
import layouts.layouts_facade as lf

import data.constants as dc
import data.temp as dt

import settings.facade as sf

class SwitchToCurrMainLayout_BTN(ww.currUIImpl.Button,
                                 dc.AppCurrDataAccessToken):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_swritchToCurrMainLayout_BTN"
        text= "To main"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        data, 
                        self.cmd)

    def cmd(self):
        # switch UI
        mathMenuManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken, mmm.MathMenuManager)
        mathMenuManager.switchUILayout(mmm.LayoutManagers._Main)



class RebuildCurrSection_BTN(ww.currUIImpl.Button):
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0,  "pady" : 0, "sticky" : tk.N,}
        }
        name = "_rebuildCurrSubsec_BTN"
        text = "rebuild"

        super().__init__(prefix, 
                        name,
                        text, 
                        patentWidget,
                        data, 
                        self.cmd)
    
    def cmd(self):
        ocf.Wr.LatexCalls.buildCurrentSubsectionPdf()

class ChangeSubsection_BTN(ww.currUIImpl.Button):
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_changeSubsection_BTN"
        text = "change subsecttion"

        super().__init__(prefix, 
                        name,
                        text, 
                        patentWidget,
                        data, 
                        self.cmd)
    
    def cmd(self):
        # get the name of the front skim document
        cmd = oscr.get_NameOfFrontSkimDoc_CMD()
        frontSkimDocumentName = str(subprocess.check_output(cmd, shell=True))
        
        # get subsection and top section from it
        frontSkimDocumentName = frontSkimDocumentName.replace("\\n", "")
        frontSkimDocumentName = frontSkimDocumentName.split("_")[1]
        topSection = frontSkimDocumentName.split(".")[0]
        subsection = frontSkimDocumentName
        
        imIDX_page = int(frontSkimDocumentName.split(" ")[1])

        # close current section vscode
        _, windowID, _ = _u.getOwnersName_windowID_ofApp(
                            "vscode",
                             fsm.Wr.SectionCurrent.readCurrSection())
        
        if (windowID != None):
            lf.Wr.LayoutsManager.closeIDEWindow(subsection, dt.OtherAppsInfo.VsCode.section_pid)

        #change the current subsection for the app
        fsm.Data.Book.currTopSection = topSection
        fsm.Data.Book.currSection = subsection


        self.notify(comui.SourceImageLinks_OM, subsection)
