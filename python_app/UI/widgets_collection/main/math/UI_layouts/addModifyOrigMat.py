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


# class SetSectionName_ETR(ww.currUIImpl.TextEntry):

#     def __init__(self, patentWidget, prefix):
#         name = "_setSectionName_ETR"
#         defaultText = fsf.Data.Sec.name(fsf.Data.Book.currSection)
#         renderData = {
#             ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 1},
#             ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
#         }

#         super().__init__(prefix, 
#                         name, 
#                         patentWidget, 
#                         renderData,
#                         defaultText = defaultText)
#         super().setData(defaultText)
    
#     def receiveNotification(self, broadcasterType, newName = ""):
#         if broadcasterType == CreateNewTopSection_BTN:
#             text = self.getData()
#             return text if text != self.defaultText else ""
#         if broadcasterType == ChooseTopSection_OM:
#             self.setData(newName)
#             self.updateDafaultText(newName)
#         if broadcasterType == ChooseSubsection_OM:
#             self.setData(newName)
#             self.updateDafaultText(newName)
#         if broadcasterType == ModifySubsection_BTN:
#             if newName not in (None, ""):
#                 self.setData(newName)
#                 self.updateDafaultText(newName)
#             else:
#                 return self.getData()


# class NewSectionPath_ETR(ww.currUIImpl.TextEntry):
#     def __init__(self, patentWidget, prefix):
#         name = "_getNewSectionPath_ETR"
#         defaultText = "New section path"
#         renderData = {
#             ww.Data.GeneralProperties_ID : {"column" : 2, "row" : 1},
#             ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
#         }

#         super().__init__(prefix, 
#                         name, 
#                         patentWidget, 
#                         renderData,
#                         defaultText = defaultText)
    
#     def receiveNotification(self, broadcasterType):
#         log.autolog(self.getData())

#         return self.getData()


# class RemoveTopSection_BTN(ww.currUIImpl.Button):
#     def __init__(self, patentWidget, prefix):
#         renderData = {
#             ww.Data.GeneralProperties_ID :{"column" : 2, "row" : 0},
#             ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.E}
#         }
#         text = "New"
#         name = "_removeTopSection_BTN"

#         super().__init__(prefix, 
#                         name, 
#                         text, 
#                         patentWidget, 
#                         renderData, 
#                         self.cmd)

#     def cmd(self):
#         #TODO: implement removing top section
#         pass


# class CreateNewTopSection_BTN(ww.currUIImpl.Button):
#     def __init__(self, patentWidget, prefix):
#         renderData = {
#             ww.Data.GeneralProperties_ID :{"column" : 3, "row" : 1},
#             ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
#         }
#         text = "New"
#         name = "_createNewTopSection_BTN"

#         super().__init__(prefix, 
#                         name, 
#                         text, 
#                         patentWidget, 
#                         renderData, 
#                         self.cmd)

#     def cmd(self):
#         newSecName = self.notify(SetSectionName_ETR)
#         newSecStartPage = self.notify(SetSectionStartPage_ETR)
#         secPath = self.notify(NewSectionPath_ETR)
        
#         # TODO: check that the structure exists and ask user if we should proceed
#         fsf.Wr.FileSystemManager.addSectionForCurrBook(secPath)

#         separator = fsf.Data.Book.sections_path_separator

#         topSectionName = secPath.split(separator)[0]
#         fsf.Data.Book.currTopSection = topSectionName
#         fsf.Data.Book.currSection = secPath
#         sections = fsf.Data.Book.sections
#         sections[topSectionName]["prevSubsectionPath"] = secPath
#         fsf.Data.Book.sections = sections

#         fsf.Data.Sec.name(secPath, newSecName)     
#         fsf.Data.Sec.startPage(secPath, newSecStartPage)