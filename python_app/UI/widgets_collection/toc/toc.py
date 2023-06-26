
import UI.widgets_wrappers as ww

import data.constants as dc
import data.temp as dt
import UI.widgets_collection.toc.manager as tocm


class Hide_BTN(ww.currUIImpl.Button,
                         dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 5, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }
        text = "Hide"
        name = "_decline_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        tocManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                            tocm.TOCManager)
        tocManager.hide()


class TOCRoot(ww.currUIImpl.RootWidget):
    pass