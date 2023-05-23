import tkinter as tk

import _utils.logging as log
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan

import UI.widgets_wrappers as ww
import UI.widgets_manager as wm
import UI.widgets_collection.message.manager as mesm
import UI.widgets_collection.main.math.manager as mmm
import UI.widgets_data as wd
import UI.widgets_collection.main.math.UI_layouts.common as cl
import file_system.file_system_facade as fsf
import layouts.layouts_facade as lf

import data.constants as dc
import data.temp as dt


class ModifySubsection_BTN(ww.currUIImpl.Button,
                           dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 2, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Modify"
        name = "_modifySubsection_BTN"

        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        # get working subsection
        subsecPath = self.notify(ChooseSubsection_OM)
        topSection = self.notify(ChooseTopSection_OM)

        changeStr = "Do you want to change "
        notChangedStr = "for subsection: '{0}' ".format(subsecPath)
        
        # get start page
        startPage, endPage = self.notify(SetSectionStartPage_ETR)
        pageDataChanged = True

        if startPage == _u.Token.NotDef.str_t and endPage == _u.Token.NotDef.str_t:
            startPage = fsf.Data.Sec.start(subsecPath)
            endPage = fsf.Data.Sec.finish(subsecPath)
            pageDataChanged = False
        
        pageStr = "start page: '{0}', end page: '{1}', ".format(startPage, endPage)
        
        if pageDataChanged:
            changeStr += pageStr
        else:
            notChangedStr += "with " + pageStr
        
        # get name
        name = self.notify(SetSectionName_ETR)
        nameDataChanged = True

        if name == _u.Token.NotDef.str_t:
            name = fsf.Data.Sec.name(subsecPath)
            nameDataChanged = False

        nameStr = "name: '{0}', ".format(name)
        
        if nameDataChanged:
            changeStr += nameStr
        else:
            notChangedStr += "with " + nameStr

        # show notification with wait
        msg = changeStr + notChangedStr
        response = wm.UI_generalManager.showNotification(msg, True)
        
        mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                    mmm.MathMenuManager)
        mainManager.show()

        # update subsection on successful response
        if response == True:
            fsf.Data.Sec.text(subsecPath, name)
            fsf.Data.Sec.start(subsecPath, startPage)
            fsf.Data.Sec.finish(subsecPath, endPage)

        self.notify(CurrSectionPath_LBL, secPath = subsecPath)
        self.notify(SetSectionName_ETR, newName = name)
        self.notify(SetSectionStartPage_ETR, newStartPage = startPage)

        subsectionsList = fsf.Wr.BookInfoStructure.getSubsectionsList(topSection)
        subsectionsList.sort()
        self.notify(ChooseSubsection_OM, subsectionsList, subsecPath)
        self.notify(ChooseTopSection_OM, topSection)


class ChooseSubsection_OM(ww.currUIImpl.OptionMenu):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }
        name = "_chooseSubsecion_optionMenu"

        subsectionsList = fsf.Wr.SectionCurrent.getSubsectionsListForCurrTopSection()

        if subsectionsList == []:
            subsectionsList = ["No subsec yet."]

        super().__init__(prefix, 
                        name, 
                        subsectionsList,
                        patentWidget, 
                        renderData, 
                        self.cmd)
        
        currSubsection = _upan.Current.Names.Section.name()
        self.setData(currSubsection)
    
    def cmd(self):
        secPath = self.getData()

        name = fsf.Data.Sec.text(secPath)
        startPage = fsf.Data.Sec.start(secPath)
        endPage = fsf.Data.Sec.finish(secPath)
        pages = startPage

        if endPage != _u.Token.NotDef.str_t:
            pages += "-" + endPage

        noteAppLink = fsf.Data.Sec.notesAppLink(secPath)

        if noteAppLink == _u.Token.NotDef.str_t:
            noteAppLink = ""

        self.notify(CurrSectionPath_LBL, secPath = secPath)
        self.notify(SetSectionName_ETR, newName = name)
        self.notify(SetSectionStartPage_ETR, newStartPage = pages)
        self.notify(SetSectionNoteAppLink_ETR, newNoteAppLink = noteAppLink)
    
    def receiveNotification(self, broadcasterType, newOptionList = [], prevSubsectionPath = "", *args):
        if broadcasterType == ChooseTopSection_OM:
            self.updateOptions(newOptionList)
            self.setData(prevSubsectionPath)
        if broadcasterType == ModifySubsection_BTN or broadcasterType == ModifyNotesAppLink_BTN:
            if prevSubsectionPath == "":
                return self.getData()
            else:
                self.updateOptions(newOptionList)
                self.setData(prevSubsectionPath)

    def render(self, widjetObj=None, renderData=..., **kwargs):
        subsectionsList = fsf.Wr.SectionCurrent.getSubsectionsListForCurrTopSection()

        if subsectionsList == []:
            subsectionsList = ["No subsec yet."]

        self.updateOptions(subsectionsList)

        currSubsection = _upan.Current.Names.Section.name()
        self.setData(currSubsection)

        return super().render(widjetObj, renderData, **kwargs)


class ChooseTopSection_OM(ww.currUIImpl.OptionMenu):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 2, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }
        name = "_chooseSection_optionMenu"

        topSectionsList = fsf.Wr.BookInfoStructure.getTopSectionsList()
        if topSectionsList != _u.Token.NotDef.list_t:
            topSectionsList.sort(key = int)

        if topSectionsList == []:
            topSectionsList = ["No top sec yet."]

        super().__init__(prefix, 
                        name, 
                        topSectionsList,
                        patentWidget, 
                        renderData, 
                        self.cmd)
        
        currTopSection = fsf.Data.Book.currTopSection
        self.setData(currTopSection)
    
    def cmd(self):
        topSection = self.getData()

        sections = fsf.Data.Book.sections
        prevSubsectionPath = sections[topSection]["prevSubsectionPath"]

        subsectionsList = fsf.Wr.BookInfoStructure.getSubsectionsList(topSection)
        subsectionsList.sort()
        name = fsf.Data.Sec.text(prevSubsectionPath)
        startPage = fsf.Data.Sec.start(prevSubsectionPath)
        endPage = fsf.Data.Sec.finish(prevSubsectionPath)
        pages = startPage

        if endPage != _u.Token.NotDef.str_t:
            pages += "-" + endPage

        noteAppLink = fsf.Data.Sec.notesAppLink(prevSubsectionPath)
        
        if noteAppLink == _u.Token.NotDef.str_t:
            noteAppLink = ""
        
        #
        # Update other widgets
        #

        # subsection option menu widget
        # notify choose subsection OM
        self.notify(ChooseSubsection_OM, subsectionsList, prevSubsectionPath)
        self.notify(CurrSectionPath_LBL, secPath = prevSubsectionPath)
        self.notify(SetSectionName_ETR, newName = name)
        self.notify(SetSectionStartPage_ETR, newStartPage = pages)
        self.notify(SetSectionNoteAppLink_ETR, newNoteAppLink = noteAppLink)
    
    def receiveNotification(self, broadcasterType, topSec = ""):
        if topSec == "":
            return self.getData()
        else:
            self.setData(topSec)
    
    def render(self, widjetObj=None, renderData=..., **kwargs):
        topSectionsList = fsf.Wr.BookInfoStructure.getTopSectionsList()
        topSectionsList.sort(key = int)
        if topSectionsList == []:
            topSectionsList = ["No top sec yet."]
        
        self.setData(topSectionsList)

        currTopSection = fsf.Data.Book.currTopSection
        self.setData(currTopSection)

        return super().render(widjetObj, renderData, **kwargs)


class SwitchLayoutSectionVSMain_amsl_BTN(cl.SwitchLayoutSectionVSMain_BTN):
    labelOptions = ["Swith layout", "Swith layout"]

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
    
    def receiveNotification(self, broadcasterType, data = None, secPath = None):
        if broadcasterType == ChooseTopSection_OM:
            newText = self.__getSectionPath_Formatted(secPath)
            self.changeText(newText)
        
        if broadcasterType == ChooseSubsection_OM:
            newText = self.__getSectionPath_Formatted(secPath)
            self.changeText(newText)
        
        if broadcasterType == ModifySubsection_BTN:
            newText = self.__getSectionPath_Formatted(secPath)
            self.changeText(newText)
        
    def __getCurrSectionPath_Formatted(self):
        currSecName = fsf.Wr.SectionCurrent.getSectionNameNoPrefix()

        return self.__getSectionPath_Formatted(currSecName)
        
    def __getSectionPath_Formatted(self, secName):
        name = fsf.Data.Sec.text(secName)
        startPage = fsf.Data.Sec.start(secName)

        return "working section path: {0}. Name: '{1}'. Start page: '{2}'".format(secName, name, startPage)

    def render(self, widjetObj=None, renderData=..., **kwargs):
        text = self.__getCurrSectionPath_Formatted()
        self.changeText(text)

        return super().render(widjetObj, renderData, **kwargs)



class ModifyNotesAppLink_BTN(ww.currUIImpl.Button,
                           dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 1, "row" : 3},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Modify Link"
        name = "_modifyNotesAppLink_BTN"

        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        # info from other widgets
        subsecPath = self.notify(ChooseSubsection_OM)
        topSection = self.notify(ChooseTopSection_OM)
        link = self.notify(SetSectionNoteAppLink_ETR)

        # show notification with wait
        msg = "Do you want to change notes app link: '{0}' for subsection: '{1}'".format(link, subsecPath)
        response = wm.UI_generalManager.showNotification(msg, True)
        mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                    mmm.MathMenuManager)
        mainManager.show()

        # update subsections link on successful response
        if response == True:
            fsf.Data.Sec.notesAppLink(subsecPath, link)
        
        self.notify(CurrSectionPath_LBL, secPath = subsecPath)

        subsectionsList = fsf.Wr.BookInfoStructure.getSubsectionsList(topSection)
        subsectionsList.sort()
        self.notify(ChooseSubsection_OM, subsectionsList, subsecPath)
        self.notify(ChooseTopSection_OM, topSection)


class SetSectionNoteAppLink_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix):
        name = "_setSectionNoteAppLink_ETR"
        defaultText = fsf.Data.Sec.notesAppLink(fsf.Data.Book.currSection)
        
        if defaultText == _u.Token.NotDef.str_t or defaultText == "":
            defaultText = "Section notes app link"
        
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 3},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        defaultText = defaultText)
        super().setData(defaultText)
    
    def receiveNotification(self, broadcasterType, data = None, newNoteAppLink = _u.Token.NotDef.str_t):
        if newNoteAppLink != _u.Token.NotDef.str_t:
            self.setData(newNoteAppLink)
            self.defaultText = newNoteAppLink
        else:
            return self.getData()



class SetSectionStartPage_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix):
        name = "_setSectionStartPage_ETR"
        startPage = fsf.Data.Sec.start(fsf.Data.Book.currSection)
        endPage = fsf.Data.Sec.finish(fsf.Data.Book.currSection)
        page = startPage
        
        if endPage != _u.Token.NotDef.str_t:
            page += "-" + endPage

        defaultText = page

        if defaultText == _u.Token.NotDef.str_t or defaultText == "":
            defaultText = "Section start page"
        
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
    
    def receiveNotification(self, broadcasterType, data = None, newStartPage = ""):
        if broadcasterType == CreateNewTopSection_BTN:
            text = self.getData()
            return self.__getStartAndFinishPages(text)
           

        if broadcasterType == ChooseTopSection_OM:
            self.setData(newStartPage)
            self.updateDafaultText(newStartPage)
        
        if broadcasterType == ChooseSubsection_OM:
            self.setData(newStartPage)
            self.updateDafaultText(newStartPage)
        
        if broadcasterType == ModifySubsection_BTN:
            if newStartPage not in (None, ""):
                self.setData(newStartPage)
                self.updateDafaultText(newStartPage)
            else:            
                text = self.getData()
                startPage, endPage = self.__getStartAndFinishPages(text)
                
                if text == self.defaultText:
                    return _u.Token.NotDef.str_t, _u.Token.NotDef.str_t
                else:
                    return startPage, endPage
    
    def __getStartAndFinishPages(self, text):
        if "-" in text:
            text = text.split("-")
        
            if len(text) > 1:
                # we have the first and last page
                return text[0], text[1]
            else:
                # we only have the last page
                return _u.Token.NotDef.str_t, text[0][1]

        # we have only the start page
        return text if text != self.defaultText else "" , _u.Token.NotDef.str_t


class SetSectionName_ETR(ww.currUIImpl.TextEntry):

    def __init__(self, patentWidget, prefix):
        name = "_setSectionName_ETR"
        defaultText = fsf.Data.Sec.text(fsf.Data.Book.currSection)
        
        if defaultText == _u.Token.NotDef.str_t or defaultText == "":
            defaultText = "Section Name"
        
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
    
    def receiveNotification(self, broadcasterType, newName = ""):
        if broadcasterType == CreateNewTopSection_BTN:
            text = self.getData()
            return text if text != self.defaultText else ""
        if broadcasterType == ChooseTopSection_OM:
            self.setData(newName)
            self.updateDafaultText(newName)
        if broadcasterType == ChooseSubsection_OM:
            self.setData(newName)
            self.updateDafaultText(newName)
        if broadcasterType == ModifySubsection_BTN:
            if newName not in (None, ""):
                self.setData(newName)
                self.updateDafaultText(newName)
            else:
                d = self.getData()

                if d == self.defaultText:
                    return _u.Token.NotDef.str_t
                else:
                    return self.getData()


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
        return self.getData()
      
    def getData(self, **kwargs):
        text = super().getData(**kwargs)
        text = text.replace(" ", "_")
        return text


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
        # close current subsection FS window
        currSection = fsf.Data.Book.currSection
        lf.Wr.LayoutsManager.closeFSWindow(currSection)

        newSecName = self.notify(SetSectionName_ETR)
        newSecStartPage, newSecEndPage = self.notify(SetSectionStartPage_ETR)
        secPath = self.notify(NewSectionPath_ETR)
        
        # TODO: check that the structure exists and ask user if we should proceed
        fsf.Wr.FileSystemManager.addSectionForCurrBook(secPath)

        separator = fsf.Data.Book.sections_path_separator

        topSectionName = secPath.split(separator)[0]
        fsf.Data.Book.currTopSection = topSectionName
        fsf.Data.Book.currSection = secPath
        sections = fsf.Data.Book.sections
        sections[topSectionName]["prevSubsectionPath"] = secPath
        fsf.Data.Book.sections = sections

        fsf.Data.Sec.text(secPath, newSecName)
        fsf.Data.Sec.start(secPath, newSecStartPage)
        fsf.Data.Sec.finish(secPath, newSecEndPage)