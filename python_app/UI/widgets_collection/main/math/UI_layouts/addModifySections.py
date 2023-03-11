import tkinter as tk

import _utils.logging as log

import UI.widgets_wrappers as ww
import UI.widgets_data as wd
import file_system.file_system_facade as fsm
import UI.widgets_collection.main.math.UI_layouts.common as cl


class SwitchLayoutSectionVSMain_amsl_BTN(cl.SwitchLayoutSectionVSMain_BTN):
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }
        name = "_chooseSubsectionLayout_BTN"
        text = self.labelOptions[0]
        super().__init__(patentWidget, prefix, data, name, text)

class CurrSectionPath_LBL(ww.currUIImpl.Label):
    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 2, "columnspan": 3},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_showCurrSectionPath_LBL"
        text = self.__getCurrSectionPath_Formatted()
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data, 
                        text = text)
    
    def receiveNotification(self, broadcasterName, data = None):
        newText = self.__getCurrSectionPath_Formatted()
        self.changeText(newText)
        
    def __getCurrSectionPath_Formatted(self):
        currSecName = fsm.Wr.SectionCurrent.getSectionNameNoPrefix()
        name = fsm.Data.Sec.name(currSecName)
        startPage = fsm.Data.Sec.startPage(currSecName)
        currSecName = fsm.Wr.SectionCurrent.getSectionNameNoPrefix()

        return "current section path: {0}. Name: '{1}'. Start page: '{2}'".format(currSecName, name, startPage)

    def render(self, widjetObj=None, renderData=..., **kwargs):
        text = self.__getCurrSectionPath_Formatted()
        self.changeText(text)

        return super().render(widjetObj, renderData, **kwargs)

class SetSectionStartPage_BTN(ww.currUIImpl.Button):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 1, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.E}
        }
        text = "Start Page"
        name = "_setSectionStartPage_BTN"

        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        currTopSection = fsm.Data.Book.currTopSection
            
        startPage = self.notify(SetSectionStartPage_ETR)
        fsm.Data.Sec.startPage(currTopSection, startPage)

class SetSectionStartPage_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix):
        name = "_setSectionStartPage_ETR"
        defaultText = "Set Section Start Page"
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        defaultText = defaultText)
        super().setData(defaultText)
    
    def receiveNotification(self, broadcasterType):
        if broadcasterType == SetSectionStartPage_BTN:
            text = self.getData()
            return text if text != self.defaultText else ""
        if broadcasterType == CreateNewTopSection_BTN:
            text = self.getData()
            return text if text != self.defaultText else ""

class SetSectionName_BTN(ww.currUIImpl.Button):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 1, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.E}
        }
        text = "Name"
        name = "_setSectionName_BTN"

        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        currTopSection = fsm.Data.Book.currTopSection
            
        name = self.notify(SetSectionName_ETR)
        fsm.Data.Sec.name(currTopSection, name)

class SetSectionName_ETR(ww.currUIImpl.TextEntry):

    def __init__(self, patentWidget, prefix):
        name = "_setSectionName_ETR"
        defaultText = "Set Section Name"
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
    
    def receiveNotification(self, broadcasterType):
        if broadcasterType == SetSectionName_BTN:
            text = self.getData()
            return text if text != self.defaultText else ""
        if broadcasterType == CreateNewTopSection_BTN:
            text = self.getData()
            return text if text != self.defaultText else ""

class NewSectionPath_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix):
        name = "_getNewSectionPath_ETR"
        defaultText = "New section path"
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 2, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        defaultText = defaultText)
    
    def receiveNotification(self, broadcasterType):
        log.autolog(self.getData())

        return self.getData()

class RemoveTopSection_BTN(ww.currUIImpl.Button):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 2, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.E}
        }
        text = "New"
        name = "_removeTopSection_BTN"

        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        #TODO: implement removing top section
        pass

class CreateNewTopSection_BTN(ww.currUIImpl.Button):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 3, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }
        text = "New"
        name = "_createNewTopSection_BTN"

        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        newSecName = self.notify(SetSectionName_ETR)
        newSecStartPage = self.notify(SetSectionStartPage_ETR)
        secPath = self.notify(NewSectionPath_ETR)
        
        # TODO: check that the structure exists and ask user if we should proceed
        fsm.Wr.FileSystemManager.addSectionForCurrBook(secPath)

        separator = fsm.Data.Book.sections_path_separator

        topSectionName = secPath.split(separator)[0]
        fsm.Data.Book.currTopSection = topSectionName
        fsm.Data.Book.currSection = secPath
        sections = fsm.Data.Book.sections
        sections[topSectionName]["prevSubsectionPath"] = secPath
        fsm.Data.Book.sections = sections

        fsm.Data.Sec.name(secPath, newSecName)     
        fsm.Data.Sec.startPage(secPath, newSecStartPage)