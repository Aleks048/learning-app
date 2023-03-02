import tkinter as tk
import UI.widgets_wrappers as ww

import data.constants as dc
import data.temp as dt

import UI.widgets_collection.message.manager as mesm

import _utils.logging as log


class Decline_BTN(ww.currUIImpl.Button,
                         dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }
        text = "No"
        name = "_decline_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        messageManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                            mesm.MessageMenuManager)
        messageManager.stopWait(False)
        messageManager.hide()
    
    def bindCmd(self):
        keys = [ww.currUIImpl.Data.BindID.allKeys]
        def _bindCmd(event):
            if event.keysym == ww.currUIImpl.Data.BindID.Keys.escape:
                self.cmd()
        cmds = [_bindCmd]

        return keys, cmds
class Confirm_BTN(ww.currUIImpl.Button,
                         dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }
        text = "Yes"
        name = "_confirm_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        self.hideMessageWin()

    def hideMessageWin(self):
        messageManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                            mesm.MessageMenuManager)
        messageManager.stopWait(True)
        messageManager.hide()
    
    def bindCmd(self):
        keys = [ww.currUIImpl.Data.BindID.allKeys]
        def _bindCmd(event):
            if event.keysym == ww.currUIImpl.Data.BindID.Keys.enter:
                self.cmd()
        cmds = [_bindCmd]

        return keys, cmds

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
                
                messageManager.stopWait()
                messageManager.hide()
        cmds = [hideMessage]

        return keys, cmds

class MessageRoot(ww.currUIImpl.RootWidget):
    pass
