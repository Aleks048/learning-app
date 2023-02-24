import tkinter as tk

import UI.widgets_wrappers as ww
import UI.widgets_data as wd
import file_system.file_system_manager as fsm



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
        currTopSection = \
                fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currTopSection_ID)
            
        startPage = self.notify(SetSectionStartPage_ETR)
        fsm.Wr.SectionInfoStructure.updateProperty(currTopSection, 
                                                fsm.PropIDs.Sec.startPage_ID, 
                                                startPage)

class SetSectionStartPage_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix):
        name = "_setSectionStartPage_ETR"
        defaultText = "Set Section Start Page"
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.widgetsWidth: "5"},
            ww.TkWidgets.__name__ : {}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraBuildOptions,
                        defaultText = defaultText)
        super().setData(defaultText)
    
    def receiveNotification(self, broadcasterType):
        if broadcasterType == SetSectionStartPage_BTN:
            return self.getData()

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
        currTopSection = \
                fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currTopSection_ID)
            
        name = self.notify(SetSectionName_ETR)
        fsm.Wr.SectionInfoStructure.updateProperty(currTopSection, 
                                                fsm.PropIDs.Sec.name_ID, 
                                                name)

class SetSectionName_ETR(ww.currUIImpl.TextEntry):

    def __init__(self, patentWidget, prefix):
        name = "_setSectionName_ETR"
        defaultText = "Set Section Name"
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.widgetsWidth: "5"},
            ww.TkWidgets.__name__ : {}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraBuildOptions,
                        defaultText = defaultText)
        super().setData(defaultText)
    
    def receiveNotification(self, broadcasterType):
        if broadcasterType == SetSectionName_BTN:
            return self.getData()

class getNewSectionPath_ETR(ww.currUIImpl.TextEntry):

    def __init__(self, patentWidget, prefix):
        name = "_getNewSectionPath_ETR"
        defaultText = ""
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.widgetsWidth: "5"},
            ww.TkWidgets.__name__ : {}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraBuildOptions,
                        self.bindCmd,
                        defaultText)
        super().setData(defaultText)

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
            ww.Data.GeneralProperties_ID :{"column" : 2, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
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
        secPath = None
        secName = None
        secStartPage = None
        
        #TODO: get names
        # for e in self.rootWidget.getChildren():
        #     if  cls.WidgetNames.Top.Section + wu.Data.ENT.entryWidget_ID in e._name:
        #         secPath = e.get()
        #     elif cls.WidgetNames.Top.Name + wu.Data.ENT.entryWidget_ID in e._name:
        #         secName = e.get()
        #     elif cls.WidgetNames.Top.StPage + wu.Data.ENT.entryWidget_ID in e._name:
        #         secStartPage = e.get()
        
        # TODO: check that the structure exists and ask user if we should proceed
        fsm.addSectionForCurrBook(secPath)
        separator = \
            fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_path_separator_ID)
        topSectionName = secPath.split(separator)[0]
        fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.currTopSection_ID, topSectionName)
        fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.currSection_ID, secPath)
        sections = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_ID)
        sections[topSectionName]["prevSubsectionPath"] = secPath
        fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.sections_ID, sections)

        fsm.Wr.SectionInfoStructure.updateProperty(secPath, 
                                                fsm.PropIDs.Sec.name_ID,
                                                secName)            
        fsm.Wr.SectionInfoStructure.updateProperty(secPath, 
                                                fsm.PropIDs.Sec.startPage_ID, 
                                                secStartPage)

        #
        # update ui
        #
        # topSections = \
        #     list(fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_ID).keys())
        # subsections = wu.getSubsectionsListForCurrTopSection()
        # wu.updateOptionMenuOptionsList(mainWinRoot, 
        #                             "_chooseSection_optionMenu",
        #                             topSections, 
        #                             wv.UItkVariables.topSection,
        #                             ChooseMaterial._topSectionChoosingCallback
        #                             ) 
        # wv.UItkVariables.topSection.set(topSectionName)
        
        # wu.updateOptionMenuOptionsList(mainWinRoot, 
        #                             "_chooseSubsecion_optionMenu",
        #                             subsections,
        #                             wv.UItkVariables.subsection,
        #                             ChooseMaterial._subsectionChoosingCallback
        #                             ) 
        # wv.UItkVariables.subsection.set(secPath)

        # wv.UItkVariables.imageGenerationEntryText.set("1")

        # # update screenshot widget
        # wu.Screenshot.setValueScreenshotLoaction()