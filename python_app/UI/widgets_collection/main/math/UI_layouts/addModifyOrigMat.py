import tkinter as tk

import _utils.logging as log
import _utils.pathsAndNames as _upan

import UI.widgets_wrappers as ww
import UI.widgets_collection.message.manager as mesm
import UI.widgets_collection.main.math.manager as mmm
import UI.widgets_data as wd
import file_system.file_system_facade as fsf
import UI.widgets_collection.main.math.UI_layouts.common as cl

import data.constants as dc
import data.temp as dt

class LayoutsSwitchOrigMatVSMain_BTN(cl.LayoutsSwitchOrigMatVSMain_BTN):
    labelOptions = ["Orig Mat", "Main"]

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 2, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }
        name = "_layoutsSwitchOrigMatVSMain_BTN"
        
        text = self.labelOptions[0]

        super().__init__(patentWidget,
                        prefix, 
                        data,
                        name,
                        text)

class AddOrigMaterial_BTN(ww.currUIImpl.Button):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Add"
        name = "_addOrigMaterial_BTN"

        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        origMatFilepath = self.notify(GetOrigMatPath_ETR)
        origMatDestRelPath = self.notify(GetOrigMatDestRelPath_ETR)
        origMatName = self.notify(GetOrigMatName_ETR)

        fsf.Wr.OriginalMaterialStructure.addOriginalMaterial(origMatFilepath,
                                                            origMatDestRelPath,
                                                            origMatName)


class GetOrigMatPath_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix):
        name = "_getOrigMatPath_ETR"
        defaultText = "get original material filepath"
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 1, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        defaultText = defaultText)
        super().setData(defaultText)
    

    def receiveNotification(self, broadcasterType, *args):
        text = self.getData()

        if text == self.defaultText:
            return ""
        else:
            return text

class GetOrigMatDestRelPath_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix):
        name = "_getOrigMatDestRelPath_ETR"
        defaultText = "get original material dest rel path"
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        defaultText = defaultText)
        super().setData(defaultText)
    

    def receiveNotification(self, broadcasterType, *args):
        text = self.getData()
        
        if text == self.defaultText:
            return ""
        else:
            return text

class GetOrigMatName_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix):
        name = "_getOrigMatName_ETR"
        defaultText = "get original material name"
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 1, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        defaultText = defaultText)
        super().setData(defaultText)
    

    def receiveNotification(self, broadcasterType, *args):
        text = self.getData()
        
        if text == self.defaultText:
            return ""
        else:
            return text