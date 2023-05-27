import os
import sys
import tkinter as tk
from tkinter import ttk
import subprocess
from threading import Thread
import time

import file_system.file_system_facade as fsf
import tex_file.tex_file_facade as tff

import _utils.logging as log
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan

import outside_calls.outside_calls_facade as ocf

import UI.widgets_wrappers as ww

import UI.widgets_collection.main.math.manager as mmm
import layouts.layouts_facade as lf

import data.constants as dc
import data.temp as dt

import settings.facade as sf

import scripts.osascripts as oscr


class ReAddAllNotesFromTheOMPage_BTN(ww.currUIImpl.Button,
                  dc.AppCurrDataAccessToken):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 5, "row" : 4},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_reAddNotes"
        text= "ReAdd notes"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        data, 
                        self.cmd)

    def cmd(self):
        omName = fsf.Data.Book.currOrigMatName
        fileName = fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsFilename(omName)
        cmd = oscr.get_PageOfSkimDoc_CMD(fileName)
        currPage, _ = _u.runCmdAndGetResult(cmd)

        if currPage != None:
            currPage = currPage.split("page ")[1]
            currPage = currPage.split(" ")[0]
        
        time.sleep(0.3)

        cmd = oscr.deleteAllNotesFromThePage(fileName, currPage)
        _u.runCmdAndWait(cmd)

        time.sleep(0.3)
        
        bookName = sf.Wr.Manager.Book.getCurrBookName()
        
        sections = fsf.Data.Book.sections
        noteIdx = 1

        for topSection in sections:
            subsections = fsf.Wr.BookInfoStructure.getSubsectionsList(topSection)
            for subSec in subsections:
                imPages:dict = fsf.Data.Sec.imLinkOMPageDict(subSec)
                imTexts:dict = fsf.Data.Sec.imLinkDict(subSec)
                for imIdx,imPage in imPages.items():
                    if imPage == currPage:
                        imText = imTexts[imIdx]
                        url = tff.Wr.TexFileUtils.getUrl(bookName, topSection, subSec, 
                                                        imIdx, "full", notLatex=True)
                        fsf.Wr.OriginalMaterialStructure.addNoteToOriginalMaterial(omName, currPage, 
                                                                                   url + " " + imText, noteIdx)
                        noteIdx += 1


class ExitApp_BTN(ww.currUIImpl.Button,
                  dc.AppCurrDataAccessToken):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 5, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_exitApp"
        text= "ExitApp"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        data, 
                        self.cmd)

    def cmd(self):
        import generalManger.generalManger as gm
        gm.GeneralManger.exitApp()
        

class LabelWithClick(ttk.Label):
    '''
    this is used to run different commands on whether the label was clicked even or odd times
    '''
    clicked = False


class TOC_BOX(ww.currUIImpl.ScrollableBox):
    subsection = ""
    subsectionsClicked = {}
    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 3, "columnspan" : 5, "rowspan": 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_showCurrScreenshotLocation_text"

        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data,
                        height=420,
                        width=500)
    
    def receiveNotification(self, broadcasterName, data = None):
        self.render()
    
    def addTOCEntry(self, subsection, level, idx):
        def openPdfOnStartOfTheSection(widget):
            def __cmd(event = None, *args):
                # open orig material on page
                subsectionStartPage = fsf.Data.Sec.start(subsection)
                origMaterialBookFSPath_curr = _upan.Paths.OriginalMaterial.MainBook.getAbs()
                ocf.Wr.PdfApp.openPDF(origMaterialBookFSPath_curr, subsectionStartPage)

                event.widget.configure(foreground="white")
            
            widget.bind(ww.currUIImpl.Data.BindID.mouse1, __cmd)

        def bindChangeColorOnInAndOut(widget):
            def __changeTextColorBlue(event = None, *args):
                event.widget.configure(foreground="blue")
            
            def __changeTextColorBlack(event = None, *args):
                event.widget.configure(foreground="white")
            
            widget.bind(ww.currUIImpl.Data.BindID.enterWidget, __changeTextColorBlue)
            widget.bind(ww.currUIImpl.Data.BindID.leaveWidget, __changeTextColorBlack)
        
        def openOMOnThePageOfTheImage(widget, imIdx):
            def __cmd(event = None, *args):
                # open orig material on page
                imLinkOMPageDict = fsf.Data.Sec.imLinkOMPageDict(subsection)
                page = imLinkOMPageDict[imIdx]
                origMaterialBookFSPath_curr = _upan.Paths.OriginalMaterial.MainBook.getAbs()
                ocf.Wr.PdfApp.openPDF(origMaterialBookFSPath_curr, page)
            
            widget.bind( ww.currUIImpl.Data.BindID.mouse1, __cmd)
        
        def openSectionOnIdx(widget, imIdx):
            def __cmd(event = None, *args):
                # open orig material on page
                bookName = sf.Wr.Manager.Book.getCurrBookName()
                currTopSection = fsf.Data.Book.currTopSection

                url = tff.Wr.TexFileUtils.getUrl(bookName, currTopSection, subsection, imIdx, "full", notLatex=True)
                
                os.system("open {0}".format(url))
                event.widget.configure(foreground="white")
            
            widget.bind(ww.currUIImpl.Data.BindID.mouse1, __cmd)
       
        def openContentOfTheSection(frame, label):
            def __cmd(event = None, *args):
                # open orig material on page

                links:dict = fsf.Data.Sec.imLinkDict(subsection)

                # 4 : event of mouse click
                # 19 : event of being rendered
                if ((not label.clicked and int(event.type) == 4)) or\
                    ((self.subsectionsClicked[subsection] == True) and (int(event.type) == 19)):
                    i = 0

                    for k,v in links.items():
                        subSecID = subsection.replace(".", "")
                        tempFrame = ttk.Frame(frame, name = "contentFr_" + subSecID + str(i))
                        
                        testEntryPage = ttk.Label(tempFrame, text = k + ": " + v, name = "contentP_" + subSecID +str(i))
                        testEntryFull = ttk.Label(tempFrame, text = "[full]", name = "contentFull_" + subSecID + str(i))
                        
                        testEntryPage.grid(row=0, column=0, sticky=tk.NW)
                        testEntryFull.grid(row=0, column=1, sticky=tk.NW)
                        
                        openOMOnThePageOfTheImage(testEntryPage, k)
                        bindChangeColorOnInAndOut(testEntryPage)
                        openSectionOnIdx(testEntryFull, k)
                        bindChangeColorOnInAndOut(testEntryFull)

                        tempFrame.grid(row=i + 2, column=2, sticky=tk.NW)
                        i += 1

                    if int(event.type) == 4:
                        label.clicked = True
                        self.subsectionsClicked[subsection] = True
                else:
                    for child in frame.winfo_children():
                        if "content" in str(child):
                            child.destroy()
                    
                    if int(event.type) == 4:
                        label.clicked = False
                        self.subsectionsClicked[subsection] = False

                event.widget.configure(foreground="white")
            
            label.bind(ww.currUIImpl.Data.BindID.mouse1, __cmd)
            label.bind(ww.currUIImpl.Data.BindID.render, __cmd)
        
        prefix = ""
        if level != 0:
            prefix = "|" + int(level) * 4 * "-" + " "

        currBokkpath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        sectionFilepath = _upan.Paths.Section.JSON.getAbs(currBokkpath, subsection)
        
        subsectionText = ""

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(sectionFilepath):
            subsectionText = fsf.Data.Sec.text(subsection)

        if level == 0 and subsection != _u.Token.NotDef.str_t:
            subsectionText = fsf.Data.Book.sections[subsection]["name"]

        prettySubsections = prefix + subsection + ": " + subsectionText + "\n"
        
        locFrame = ttk.Frame(self.scrollable_frame)
        super().addTOCEntry(locFrame, idx, 0)

        subsectionLabel = ttk.Label(locFrame, text = prettySubsections)
        openPdfOnStartOfTheSection(subsectionLabel)
        bindChangeColorOnInAndOut(subsectionLabel)

        subsectionLabel.grid(row = 0, column= 0, sticky=tk.NW)

        if level != 0:
            openContentLabel = LabelWithClick(locFrame, text = "[content]")
            openContentOfTheSection(locFrame, openContentLabel)
            bindChangeColorOnInAndOut(openContentLabel)

            openContentLabel.grid(row = 0, column= 1, sticky=tk.NW)

    def populateTOC(self):
        text_curr = fsf.Wr.BookInfoStructure.getSubsectionsAsTOC()
        
        for i in range(len(text_curr)):
            self.addTOCEntry(text_curr[i][0], text_curr[i][1], i)

    def render(self, widjetObj=None, renderData=..., **kwargs):
        # update the subsections dict in the toc window.
        # the subsectionsClicked:dict is used to keep the open subsection content open
        subsectionsList = fsf.Wr.BookInfoStructure.getSubsectionsList()
        
        for subSec in subsectionsList:
            if subSec not in list(self.subsectionsClicked.keys()):
                self.subsectionsClicked[subSec] = False

        for child in self.scrollable_frame.winfo_children():
            child.destroy()
        
        self.populateTOC()

        return super().render(widjetObj, renderData, **kwargs)


class TOC_LBL(ww.currUIImpl.Label):
    subsection = ""
    def __init__(self, parentWidget, prefix, row = 5, subsection = "", level = ""):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : row, "columnspan": 5},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_TOCEntry_text" + subsection
        
        self.subsection = subsection

        prefix = ""
        if level != 0:
            prefix = "|" + int(level) * 4 * "-" + " "

        currBokkpath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        sectionFilepath = _upan.Paths.Section.JSON.getAbs(currBokkpath, subsection)
        
        subsectionText = ""
        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(sectionFilepath):
            subsectionText = fsf.Data.Sec.text(subsection)
       
        prettySubsections = prefix + subsection + ":" + subsectionText + "\n"
        
        text_curr = prettySubsections
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data, 
                        text = text_curr,
                        bindCmd= self.bindCmd)
    
    def receiveNotification(self, broadcasterName, data = None):
        pass
    
    def render(self, widjetObj=None, renderData=..., **kwargs):
        return super().render(widjetObj, renderData, **kwargs)

    def bindCmd(self):
        def __cmd(event = None, *args):
            # open orig material on page
            subsectionStartPage = fsf.Data.Sec.start(self.subsection)
            origMaterialBookFSPath_curr = _upan.Paths.OriginalMaterial.MainBook.getAbs()
            ocf.Wr.PdfApp.openPDF(origMaterialBookFSPath_curr, subsectionStartPage)

            self.changeColor("white")

        def __changeTextColorBlue(event = None, *args):
            self.changeColor("blue")
        
        def __changeTextColorBlack(event = None, *args):
            self.changeColor("white")
        
        cmds = [__cmd, __changeTextColorBlue, __changeTextColorBlack]

        events = [ww.currUIImpl.Data.BindID.mouse1,
                  ww.currUIImpl.Data.BindID.enterWidget,
                  ww.currUIImpl.Data.BindID.leaveWidget]
        
        return events, cmds


class ChooseOriginalMaterial_OM(ww.currUIImpl.OptionMenu):
    prevChoice = ""

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 5, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }
        name = "_chooseOriginalMaterial_OM"

        origMatNames = fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsNames()

        super().__init__(prefix, 
                        name, 
                        origMatNames,
                        patentWidget, 
                        renderData, 
                        self.cmd)
        
        #TODO: set the data to currOrigMaterialName
        currOrigMatName = fsf.Data.Book.currOrigMatName
        self.setData(currOrigMatName)
        self.prevChoice = currOrigMatName
    
    def cmd(self):
        # close original material document
        fsf.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(self.prevChoice)
        prevChoiceID = fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsFilename(self.prevChoice)
        _, _, oldPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, 
                                                    prevChoiceID)     
        
        if oldPID != None:
            lf.Wr.LayoutsManager.closePDFwindow(prevChoiceID, oldPID)
        
        time.sleep(0.3)

        # open another original material
        origMatName = self.getData()
        self.prevChoice = origMatName
        origMatPath = fsf.Wr.OriginalMaterialStructure.getMaterialPath(origMatName)
        origMatCurrPage = fsf.Wr.OriginalMaterialStructure.getMaterialCurrPage(origMatName)
        ocf.Wr.PdfApp.openPDF(origMatPath, origMatCurrPage)

        width, height = _u.getMonitorSize()
        halfWidth = int(width / 2)

        newChoiceID = fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsFilename(origMatName)
        _, _, newPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, 
                                                    newChoiceID)
        while newPID == None:
            time.sleep(0.1)
            _, _, newPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, 
                                                    newChoiceID)
        cmd = oscr.getMoveWindowCMD(newPID, [halfWidth, height, 0, 0], newChoiceID)
        _u.runCmdAndWait(cmd)

        # update book settings
        fsf.Data.Book.currOrigMatName = origMatName
    
    def render(self, widjetObj=None, renderData=..., **kwargs):
        names = fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsNames()
        self.updateOptions(names)

        currOrigMatName = fsf.Data.Book.currOrigMatName
        self.setData(currOrigMatName)
        return super().render(widjetObj, renderData, **kwargs)


class SwitchToCurrSectionLayout_BTN(ww.currUIImpl.Button,
                                    dc.AppCurrDataAccessToken):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 4, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_swritchToCurrSectionLayout_BTN"
        text= "To section"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        data, 
                        self.cmd)

    def cmd(self):
        # switch UI
        mathMenuManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken, mmm.MathMenuManager)
        mathMenuManager.switchUILayout(mmm.LayoutManagers._Section)
        
        # switch other apps
        lf.Wr.SectionLayout.set()


class ChooseSubsection_OM(ww.currUIImpl.OptionMenu):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 2},
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
        newSubsection = self.getData()

        # close current subsection FS window
        currSection = fsf.Data.Book.currSection
        if newSubsection != currSection:
            lf.Wr.LayoutsManager.closeFSWindow(currSection)

        # open new subsection
        sections = fsf.Data.Book.sections
        topSection = fsf.Data.Book.currTopSection
        sections[topSection]["prevSubsectionPath"] = newSubsection
        fsf.Data.Book.sections = sections
        fsf.Data.Book.currSection = newSubsection

        self.notify(ImageGeneration_ETR, fsf.Wr.Links.ImIDX.get(newSubsection))

        self.notify(ScreenshotLocation_LBL)

        lf.Wr.MainLayout.set()
    
    def receiveNotification(self, broadcasterType, newOptionList = [], prevSubsectionPath = "", *args) -> None:
        if broadcasterType == ChooseTopSection_OM:
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
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 1},
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

        # update top section
        fsf.Data.Book.currTopSection = topSection
        
        # update subsection
        sections = fsf.Data.Book.sections
        prevSubsectionPath = sections[topSection]["prevSubsectionPath"]
        
        # close current subsection FS window
        currSection = fsf.Data.Book.currSection
        
        if currSection != prevSubsectionPath:
            lf.Wr.LayoutsManager.closeFSWindow(currSection)
            fsf.Data.Book.currSection = prevSubsectionPath

        # update image index
        secionImIndex = fsf.Wr.Links.ImIDX.get(prevSubsectionPath)        
        

        subsectionsList = fsf.Wr.SectionCurrent.getSubsectionsListForCurrTopSection()
        subsectionsList.sort()
        
        #
        # Update other widgets
        #

        # subsection option menu widget
        # notify choose subsection OM
        self.notify(ChooseSubsection_OM, subsectionsList, prevSubsectionPath)

        # update screenshot widget
        self.notify(ScreenshotLocation_LBL)

        # update image index widget
        self.notify(ImageGeneration_ETR, 
                    fsf.Wr.Links.ImIDX.get(prevSubsectionPath))
        
        lf.Wr.MainLayout.set()
    
    def receiveNotification(self, broadcasterType):
        if broadcasterType == ChooseSubsection_OM:
            return self.getData()
    
    def render(self, widjetObj=None, renderData=..., **kwargs):
        topSectionsList = fsf.Wr.BookInfoStructure.getTopSectionsList()
        if topSectionsList != _u.Token.NotDef.list_t:
            topSectionsList.sort(key = int)
        
        if topSectionsList == []:
            topSectionsList = ["No top sec yet."]
        
        self.setData(topSectionsList)

        currTopSection = fsf.Data.Book.currTopSection
        self.setData(currTopSection)

        return super().render(widjetObj, renderData, **kwargs)


class ScreenshotLocation_LBL(ww.currUIImpl.Label):
    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 1, "row" : 2, "columnspan": 4},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_showCurrScreenshotLocation_text"
        text_curr = _upan.Paths.Screenshot.getRel_formatted()
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data, 
                        text = text_curr)
    
    def receiveNotification(self, broadcasterName, data = None):
        if broadcasterName == ChooseTopSection_OM:
            text = _upan.Paths.Screenshot.getRel_formatted()
            self.changeText(text)
        if broadcasterName == ChooseSubsection_OM:
            text = _upan.Paths.Screenshot.getRel_formatted()
            self.changeText(text)
    
    def render(self, widjetObj=None, renderData=..., **kwargs):
        text_curr = _upan.Paths.Screenshot.getRel_formatted()
        self.changeText(text_curr)
        return super().render(widjetObj, renderData, **kwargs)


class addToTOC_CHB(ww.currUIImpl.Checkbox):
    def __init__(self, parentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_create_toc"
        text = "add TOC entry"
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = renderData, 
                        text = text)
        self.setData(True)
        
    def receiveNotification(self, broadcasterName):
        return self.getData()


class addToTOCwImage_CHB(ww.currUIImpl.Checkbox):   
    def __init__(self, parentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 1, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_toc_w_image"
        text = "TOC entry with image"
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData, 
                        text = text)
        self.setData(False)
    
    def receiveNotification(self, broadcasterName):
        return self.getData()


class ImageGeneration_BTN(ww.currUIImpl.Button,
                          dc.AppCurrDataAccessToken):
    labelOptions = ["imIdx", "imName"]
    dataFromUser = [-1, -1]

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 2, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_imageGeneration_process_BTN"
        text = self.labelOptions[0]

        super().__init__(prefix, 
                        name,
                        text, 
                        patentWidget,
                        data, 
                        self.cmd)
    
    def cmd(self):
        def _createTexForTheProcessedImage():
            import generalManger.generalManger as gm
            addToTOC = self.notify(addToTOC_CHB)
            addToTOCwIm = self.notify(addToTOCwImage_CHB)

            currSubsection = fsf.Data.Book.currSection
            entryAdded:bool = gm.GeneralManger.AddEntry(currSubsection, 
                                                        self.dataFromUser[0], 
                                                        self.dataFromUser[1], 
                                                        addToTOC, 
                                                        addToTOCwIm)

            if not entryAdded:
                return
            
            currImNum = self.dataFromUser[0]
            nextImNum = str(int(currImNum) + 1)
            self.notify(ImageGeneration_ETR, nextImNum)
            self.notify(TOC_BOX)
            self.updateLabel(self.labelOptions[0])
        
        buttonNamesToFunc = {self.labelOptions[0]: lambda *args: self.notify(ImageGeneration_ETR, ""),
                            self.labelOptions[1]: _createTexForTheProcessedImage}

        sectionImIndex = fsf.Wr.Links.ImIDX.get_curr()
        for i in range(len(self.labelOptions)):
            if self.labelOptions[i] == self.text:
                nextButtonName = self.labelOptions[(i+1)%len(self.labelOptions)]
                self.dataFromUser[i] = self.notify(ImageGeneration_ETR, sectionImIndex) 
                buttonNamesToFunc[self.labelOptions[i]]()
                self.updateLabel(nextButtonName)
                break


    def receiveNotification(self, broadcasterType):
        if broadcasterType == ImageGenerationRestart_BTN:
            self.updateLabel(self.labelOptions[0])
        if broadcasterType == AddExtraImage_BTN:
            return self.dataFromUser[0]

class ImageGeneration_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 2, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_imageGeneration_ETR"
        defaultText = "0"

        super().__init__(prefix, 
                        name,
                        patentWidget, 
                        data,
                        defaultText = defaultText)

        secImIndex = fsf.Wr.Links.ImIDX.get_curr()

        if secImIndex == _u.Token.NotDef.str_t:
            self.updateDafaultText(defaultText)
        else:
            self.updateDafaultText(str(int(secImIndex) + 1))

    def receiveNotification(self, broadcasterType, dataToSet = None):
        if broadcasterType == ImageGenerationRestart_BTN:
            currImIdx = str(int(fsf.Wr.SectionCurrent.getImIDX()) + 1)
            self.setData(currImIdx)
        elif broadcasterType == ImageGeneration_BTN:
            prevData = self.getData()
            self.setData(dataToSet)
            return prevData
        elif broadcasterType == ChooseSubsection_OM or broadcasterType == ChooseTopSection_OM:
            # TODO: find a nicer wahy without checking the dict
            imDict = fsf.Wr.SectionCurrent.getCurrLinkIdxDict()
            currIdx = fsf.Wr.SectionCurrent.getImIDX()
            currIdx = int(currIdx)
            nextIdx = str(currIdx + 1)

            if imDict == _u.Token.NotDef.dict_t:
                self.setData(currIdx)
            else:
                self.setData(nextIdx)
        elif broadcasterType == AddExtraImage_BTN:
            return self.getData()
    
    def render(self, **kwargs):
        secImIndex = fsf.Wr.Links.ImIDX.get_curr()

        if secImIndex == _u.Token.NotDef.str_t:
            newIDX = "0"
        else:
            if secImIndex != 0:
                newIDX = str(int(secImIndex) + 1)
            else:
                newIDX = "0"
        
        self.updateDafaultText(newIDX)
        self.setData(newIDX)

        return super().render(**kwargs)

    def defaultTextCMD(self):
        pass

class AddExtraImage_BTN(ww.currUIImpl.Button):  
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 1, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text= "addExtraIm"
        name = "_imageGenerationAddIm"

        super().__init__(prefix, 
                        name,
                        text, 
                        patentWidget,
                        data, 
                        self.cmd)

    def cmd(self):
        mainImIdx = self.notify(ImageGeneration_BTN)
        if mainImIdx == "-1":
            mainImIdx = fsf.Wr.Links.ImIDX.get_curr()
       
        extraImName = self.notify(ImageGeneration_ETR)
        
        currentSubsection = _upan.Current.Names.Section.name()
        currentSubsectionNum = currentSubsection.split("_")[0]
        
        
        extraImagePath_curr = _upan.Paths.Screenshot.getAbs()
        extraImageName = _upan.Names.getExtraImageName(mainImIdx, currentSubsectionNum, extraImName)
        
        ocf.Wr.ScreenshotCalls.takeScreenshot(os.path.join(extraImagePath_curr, extraImageName))

        # update the content file
        tff.Wr.TexFileModify.addExtraImage(mainImIdx, extraImageName)

class ImageGenerationRestart_BTN(ww.currUIImpl.Button):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_imageGenerationRestart"
        text= "restart"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        data, 
                        self.cmd)

    def cmd(self):
        self.notifyAllListeners()

class ImageCreation:
    pass
