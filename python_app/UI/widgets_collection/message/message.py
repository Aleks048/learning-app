import tkinter as tk
import UI.widgets_wrappers as ww

import data.constants as dc
import data.temp as dt

import UI.widgets_collection.message.manager as mesm

class Message_LBL(ww.currUIImpl.Label,
                  dc.AppCurrDataAccessToken):
    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }
        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {"width" : 150, "anchor" : tk.N},
            ww.TkWidgets.__name__ : {}
        }

        name = "_ShowMessage_text"
        text = ""
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data, 
                        bindCmd = self.bindCmd,
                        extraOptions = extraBuildOptions,
                        text = text)

    def bindCmd(self):
        return None, None
        # keys = [ww.currUIImpl.Data.BindID.enter, ww.currUIImpl.Data.BindID.escape]
        # messageManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
        #                                                 mesm.MessageMenuManager)
        # cmds = [messageManager.stopMainLoop, messageManager.stopMainLoop]

        return keys, cmds

class MessageRoot(ww.currUIImpl.RootWidget):
    pass
