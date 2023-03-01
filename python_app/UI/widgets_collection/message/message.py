import tkinter as tk
import UI.widgets_wrappers as ww

import data.constants as dc
import data.temp as dt

import UI.widgets_collection.message.manager as mesm

import _utils.logging as log

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
        keys = [ww.currUIImpl.Data.BindID.allKeys]
        def hideMessage(event):
            if event.keysym == ww.currUIImpl.Data.BindID.Keys.enter or \
                event.keysym == ww.currUIImpl.Data.BindID.Keys.escape:

                dt.AppState.Wait.setData(self.appCurrDataAccessToken, False)

                messageManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                            mesm.MessageMenuManager)
                messageManager.hide()
        cmds = [hideMessage]

        return keys, cmds

class MessageRoot(ww.currUIImpl.RootWidget):
    pass
