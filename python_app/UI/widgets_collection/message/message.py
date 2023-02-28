import tkinter as tk
import UI.widgets_wrappers as ww

class Message_LBL(ww.currUIImpl.Label):
    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }
        name = "_ShowMessage_text"
        text = ""
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data, 
                        bindCmd = self.bindCmd,
                        text = text)
    
    def render(self, widjetObj = None, text = "test", renderData=..., **kwargs):
        self.changeText(text)
        return super().render(widjetObj, renderData, **kwargs)

    def bindCmd(self):
        keys = [ww.currUIImpl.Data.BindID.enter, ww.currUIImpl.Data.BindID.escape]
        cmds = [self.hide(), self.hide()]

        return keys, cmds

class MessageRoot(ww.currUIImpl.RootWidget):
    pass
