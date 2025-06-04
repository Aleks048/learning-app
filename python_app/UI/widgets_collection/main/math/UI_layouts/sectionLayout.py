import subprocess

import UI.widgets_wrappers as ww
import data.temp as dt
import data.constants as dc


import outside_calls.outside_calls_facade as ocf

import UI.widgets_collection.main.math.manager as mmm

import data.constants as dc
import data.temp as dt

import settings.facade as sf

class SwitchToCurrMainLayout_BTN(ww.currUIImpl.Button,
                                 dc.AppCurrDataAccessToken):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
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
            ww.TkWidgets.__name__ : {"padx" : 0,  "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N,}
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

