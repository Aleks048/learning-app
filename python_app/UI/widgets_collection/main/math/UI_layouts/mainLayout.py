import os
import tkinter as tk
from tkinter import ttk
import time
import re
from PIL import ImageTk,Image
import Pmw

import file_system.file_system_facade as fsf
import tex_file.tex_file_facade as tff

import _utils.logging as log
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan

import outside_calls.outside_calls_facade as ocf

import UI.widgets_wrappers as ww

import UI.widgets_collection.main.math.manager as mmm
import UI.widgets_collection.main.math.UI_layouts.common as comui
import UI.widgets_manager as wm
import layouts.layouts_facade as lf

import data.constants as dc
import data.temp as dt

import settings.facade as sf

import scripts.osascripts as oscr
import outside_calls.outside_calls_facade as oscf

class LatestExtraImForEntry_LBL(ww.currUIImpl.Label):
    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 4, "row" : 14},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_latestExtraImForEntry_LBL_text"

        text_curr = self.getText(True)
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data, 
                        text = text_curr)
    
    def getText(self, init = False):
        currSection = fsf.Data.Book.currSection
        entriesDict = fsf.Data.Sec.imLinkDict(currSection)
        extraImagesDict = fsf.Data.Sec.extraImagesDict(currSection)
        
        if init:
            latestEntry = list(entriesDict.keys())[-1]
        else:
            latestEntry = self.notify(comui.SourceImageLinks_OM)

        latestExtraImName = "No"

        if latestEntry in list(extraImagesDict.keys()):
            latestExtraImName = extraImagesDict[latestEntry][-1]

        return "E IM: \"" + latestExtraImName + "\""

    def receiveNotification(self, broadcasterName, data = None):
        self.render()
    
    def render(self, widjetObj=None, renderData=..., **kwargs):
        text_curr = self.getText()
        self.changeText(text_curr)
        return super().render(widjetObj, renderData, **kwargs)


class ReAddAllNotesFromTheOMPage_BTN(ww.currUIImpl.Button,
                  dc.AppCurrDataAccessToken):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 5, "row" : 5},
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
        import generalManger.generalManger as gm

        omName = fsf.Data.Book.currOrigMatName
        fileName = fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsFilename(omName)
        cmd = oscr.get_PageOfSkimDoc_CMD(fileName)
        currPage, _ = _u.runCmdAndGetResult(cmd)

        if currPage != None:
            currPage = currPage.split("page ")[1]
            currPage = currPage.split(" ")[0]

        gm.GeneralManger.readdNotesToPage(currPage)


class ExitApp_BTN(ww.currUIImpl.Button,
                  dc.AppCurrDataAccessToken):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 5, "row" : 7},
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

        self.notify(TOC_BOX)

        gm.GeneralManger.exitApp()
        

class LabelWithClick(ttk.Label):
    '''
    this is used to run different commands on whether the label was clicked even or odd times
    '''
    clicked = False
    imIdx = ""
    subsection = ""
    imagePath = ""


class TOC_BOX(ww.currUIImpl.ScrollableBox,
              dc.AppCurrDataAccessToken):
    subsection = ""
    subsectionClicked = _u.Token.NotDef.str_t
    entryClicked = _u.Token.NotDef.str_t
    showSubsectionsForTopSection = {}
    displayedImages = []
    style = ttk.Style()
    parent = None
    openedMainImg = None

    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 3, "columnspan" : 5, "rowspan": 10},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_showCurrScreenshotLocation_text"

        self.parent = parentWidget.widgetObj

        self.subsectionClicked = fsf.Data.Book.subsectionOpenInTOC_UI
        self.entryClicked = fsf.Data.Book.entryImOpenInTOC_UI

        tsList = fsf.Wr.BookInfoStructure.getTopSectionsList()

        if tsList != _u.Token.NotDef.list_t:
            for ts in tsList:
                self.showSubsectionsForTopSection[ts] = bool(int(fsf.Data.Book.sections[ts]["showSubsections"]))

        self.style.configure('TFrame',  highlightbackground="blue", highlightthickness=1)

        super().__init__(prefix,
                        name,
                        parentWidget,
                        renderData = data,
                        height=370,
                        width=570)
    
    def receiveNotification(self, broadcasterType, data = None):
        if broadcasterType == ExitApp_BTN:
            tsList = fsf.Wr.BookInfoStructure.getTopSectionsList()

            sections = fsf.Data.Book.sections

            for ts in tsList:
                sections[ts]["showSubsections"] = str(int(self.showSubsectionsForTopSection[ts]))

            fsf.Data.Book.sections = sections

            fsf.Data.Book.subsectionOpenInTOC_UI = self.subsectionClicked
            fsf.Data.Book.entryImOpenInTOC_UI = self.entryClicked
        else:
            self.render()

    def addTOCEntry(self, subsection, level, row):
        def openPdfOnStartOfTheSection(widget):
            def __cmd(event = None, *args):
                # open orig material on page
                origMatNameDict = fsf.Data.Sec.origMatNameDict(subsection)
                omName = origMatNameDict[list(origMatNameDict.keys())[-1]]

                omFilepath = fsf.Wr.OriginalMaterialStructure.getMaterialPath(omName)
                subsectionStartPage = fsf.Data.Sec.start(subsection)

                ocf.Wr.PdfApp.openPDF(omFilepath, subsectionStartPage)

                zoomLevel = fsf.Wr.OriginalMaterialStructure.getMaterialZoomLevel(omName)
                pdfToken:str = omFilepath.split("/")[-1].replace(".pdf", "")
                cmd = oscr.setDocumentScale(pdfToken, zoomLevel)
                _u.runCmdAndWait(cmd)

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
                imOMName = fsf.Data.Sec.origMatNameDict(subsection)[imIdx]

                omFilepath = fsf.Wr.OriginalMaterialStructure.getMaterialPath(imOMName)                
                imLinkOMPageDict = fsf.Data.Sec.imLinkOMPageDict(subsection)
                page = imLinkOMPageDict[imIdx]

                ocf.Wr.PdfApp.openPDF(omFilepath, page)

                zoomLevel = fsf.Wr.OriginalMaterialStructure.getMaterialZoomLevel(imOMName)
                pdfToken:str = omFilepath.split("/")[-1].replace(".pdf", "")
                cmd = oscr.setDocumentScale(pdfToken, zoomLevel)
                _u.runCmdAndWait(cmd)
            
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
        
        def __showIMagesONClick(event, subSecID, shouklScroll = False, *args):
            label = event.widget
            imIdx = label.imIdx
            tframe = label.master
            gpframe = tframe.master
            balloon = Pmw.Balloon(tframe)

            imageWidgetID = "imageWidget"
            
            def closeAllImages():
                for parent in gpframe.winfo_children():
                    for child in parent.winfo_children():
                        if "contentOfImages_" in str(child):
                            child.clicked = False

                        if imageWidgetID in str(child):
                            child.destroy()

                self.displayedImages = []
                self.openedMainImg = None

            def __cmd(event, *args):
                if ((not label.clicked and int(event.type) == 4)) or\
                    ((not label.clicked and int(event.type) == 35)):
                    closeAllImages()
                    label.clicked = True
                    self.entryClicked = imIdx

                    # mainImage
                    currBookName = sf.Wr.Manager.Book.getCurrBookName()
                    screenshotFolder = _upan.Paths.Screenshot.getAbs(currBookName, subsection)
                    mainImageName = _upan.Names.getImageName(str(imIdx), subsection)
                    mainImagePath = os.path.join(screenshotFolder,  mainImageName + ".png")
                    pilIm = Image.open(mainImagePath)
                    pilIm.thumbnail([550,1000], Image.ANTIALIAS)
                    img = ImageTk.PhotoImage(pilIm)
                    self.displayedImages.append(img)
                    
                    imLabel = LabelWithClick(tframe, image=img, name = imageWidgetID + subSecID + imIdx)
                    imLabel.imagePath = mainImagePath
                    imLabel.bind(ww.currUIImpl.Data.BindID.mouse1, 
                                 lambda event, *args: os.system("open " + "\"" + event.widget.imagePath + "\""))

                    def scroll_into_view():
                        posy = 0
                        pwidget = imLabel

                        self.scrollBar.yview_scroll(-100, "units")
                        self.scrollBar.update()
                        imLabel.update()

                        while pwidget != self.parent:
                            posy += pwidget.winfo_y()
                            pwidget = pwidget.master

                        canvas_top = self.scrollBar.winfo_y()
                        
                        widget_top = posy

                        while widget_top not in range(int(canvas_top) + 150, int(canvas_top) + 200):
                            posy = 0
                            pwidget = imLabel
                            while pwidget != self.parent:
                                posy += pwidget.winfo_y()
                                pwidget = pwidget.master

                            imLabel.update()
                            widget_top = posy
                            self.scrollBar.yview_scroll(1, "units")
                            self.scrollBar.update()

                    imLabel.bind(ww.currUIImpl.Data.BindID.customTOCMove, lambda *args: scroll_into_view())

                    imLabel.grid(row = 1, column = 0, columnspan = 100)

                    imText = fsf.Data.Sec.imLinkDict(subsection)[str(imIdx)]
                    balloon.bind(imLabel, "{0}".format(imText))

                    self.openedMainImg = imLabel

                    # extraImages
                    if imIdx in list(fsf.Data.Sec.extraImagesDict(subsection).keys()):
                        extraImages = fsf.Data.Sec.extraImagesDict(subsection)[imIdx]

                        for i in range(0, len(extraImages)):
                            eImText = extraImages[i]

                            extraImName = _upan.Names.getExtraImageName(str(imIdx), subsection, i)

                            if "proof" in eImText.lower()\
                                and not dt.AppState.ShowProofs.getData(self.appCurrDataAccessToken):
                                continue

                            extraImFilepath = os.path.join(screenshotFolder, extraImName + ".png")

                            pilIm = Image.open(extraImFilepath)
                            pilIm.thumbnail([550,1000], Image.ANTIALIAS)
                            img = ImageTk.PhotoImage(pilIm)
                            self.displayedImages.append(img)

                            eimLabel = LabelWithClick(tframe, image=img, 
                                                    name=imageWidgetID + subSecID + imIdx + "e" + str(i))
                            eimLabel.imagePath = extraImFilepath
                            eimLabel.bind(ww.currUIImpl.Data.BindID.mouse1, 
                                        lambda event, *args: os.system("open " + "\"" + event.widget.imagePath + "\""))
                            eimLabel.grid(row = i + 2, column = 0, columnspan = 100)

                            balloon.bind(eimLabel, "{0}".format(eImText))
                    
                    if int(event.type) == 4 or \
                       int(event.type) == 35:
                        for child in tframe.winfo_children():
                            if "contentImages_" + subSecID in str(child):
                                child.clicked = True

                    if shouklScroll:
                        imLabel.event_generate(ww.currUIImpl.Data.BindID.customTOCMove)
                else:
                    closeAllImages()
                    self.entryClicked = _u.Token.NotDef.str_t
     
            __cmd(event, *args)

        def openContentOfTheSection(frame, label):
            def __cmd(event = None, *args):
                # open orig material on page

                links:dict = fsf.Data.Sec.imLinkDict(subsection)

                def closeAllSubsections():
                    for wTop1 in event.widget.master.master.winfo_children():
                        for wTop2 in wTop1.winfo_children():
                            if "labelwithclick" in str(wTop2):
                                wTop2.clicked = False
                            if "contentFr_"  in str(wTop2) or "contentDummyFr_" in str(wTop2):
                                wTop2.destroy()
                
                def removeEntryCmd(event, *args):
                    widget = event.widget
                    fsf.Wr.SectionInfoStructure.removeEntry(widget.subsection, widget.imIdx)
                    self.render()


                # 4 : event of mouse click
                # 19 : event of being rendered
                if ((not label.clicked and int(event.type) == 4)) or\
                    ((self.subsectionClicked == subsection) and (int(event.type) == 19)):
                    closeAllSubsections()

                    i = 0

                    subSecID = subsection.replace(".", "")
                    for k,v in links.items():
                        tempFrame = ttk.Frame(frame, name = "contentFr_" + subSecID + "_" + str(i), style= "TFrame")

                        textLabelPage = ttk.Label(tempFrame, text = "\t" + k + ": " + v, name = "contentP_" + subSecID +str(i))
                        textLabelFull = ttk.Label(tempFrame, text = "[full]", name = "contentFull_" + subSecID + str(i))
                        showImages = LabelWithClick(tempFrame, text = "[images]", name = "contentOfImages_" + subSecID + str(i))
                        removeEntry = LabelWithClick(tempFrame, text = "[delete]", name = "contentRemoveEntry" + subSecID + str(i))

                        showImages.imIdx = k
                        showImages.clicked = False

                        removeEntry.grid(row=0, column=3, sticky=tk.NW)  
                        removeEntry.imIdx = k
                        removeEntry.subsection = subsection
                        removeEntry.bind(ww.currUIImpl.Data.BindID.mouse1,
                                         removeEntryCmd)

                        showImages.grid(row=0, column=2, sticky=tk.NW)
                        showImages.bind(ww.currUIImpl.Data.BindID.mouse1, 
                                        lambda e, *args: __showIMagesONClick(e, subSecID, True, *args))
                        showImages.bind(ww.currUIImpl.Data.BindID.customTOCMove, 
                                        lambda e, *args: __showIMagesONClick(e, subSecID, False, *args))

                        if subsection == self.subsectionClicked and k == self.entryClicked:
                            showImages.event_generate(ww.currUIImpl.Data.BindID.customTOCMove)

                        textLabelPage.grid(row=0, column=0, sticky=tk.NW)
                        textLabelFull.grid(row=0, column=1, sticky=tk.NW)

                        openOMOnThePageOfTheImage(textLabelPage, k)
                        bindChangeColorOnInAndOut(textLabelPage)
                        bindChangeColorOnInAndOut(showImages)
                        bindChangeColorOnInAndOut(removeEntry)
                        openSectionOnIdx(textLabelFull, k)
                        bindChangeColorOnInAndOut(textLabelFull)

                        tempFrame.grid(row=i + 2, column=0, columnspan = 100, sticky=tk.NW)
                        i += 1
                    
                    dummyFrame = ttk.Frame(frame, name = "contentDummyFr_" + subSecID + str(i))
                    dummyEntryPage = ttk.Label(dummyFrame, text ="\n", name = "contentDummy_" + subSecID + str(i))
                    dummyEntryPage.grid(row=0, column=0, sticky=tk.NW)
                    dummyFrame.grid(row=i + 1, column=0, sticky=tk.NW)

                    if int(event.type) == 4:
                        label.clicked = True
                        self.subsectionClicked = subsection
                else:
                    for child in frame.winfo_children():
                        if "content" in str(child):
                            child.destroy()
                    
                    if int(event.type) == 4:
                        closeAllSubsections()
                            
                        label.clicked = False

                        self.subsectionClicked = _u.Token.NotDef.str_t

                event.widget.configure(foreground="white")
            
            label.bind(ww.currUIImpl.Data.BindID.mouse1, __cmd)

            if self.subsectionClicked == subsection and level != 0:
                label.event_generate(ww.currUIImpl.Data.BindID.mouse1, x=10, y=10)         
       
        def openContentOfTheTopSection(frame, label):
            def __cmd(event = None, *args):
                
                # 4 : event of mouse click
                # 19 : event of being rendered
                if ((not label.clicked and int(event.type) == 4)) or\
                    ((self.showSubsectionsForTopSection[subsection] == True) and (int(event.type) == 19)):
                    self.showSubsectionsForTopSection[subsection] = True
                    self.render()
                else:
                    if int(event.type) == 4:
                        self.showSubsectionsForTopSection[subsection] = False
                        self.render()

                event.widget.configure(foreground="white")
            
            label.bind(ww.currUIImpl.Data.BindID.mouse1, __cmd)
       
        if level != 0:
            topSection = subsection.split(".")[0]
            if not self.showSubsectionsForTopSection[topSection]:
                return

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
        
        labelName = subsection.replace(".", "")

        locFrame = ttk.Frame(self.scrollable_frame, name=labelName)
        super().addTOCEntry(locFrame, row, 0)

        if level == 0:
            subsectionLabel = ttk.Label(locFrame, text = prettySubsections, padding= [0, 20, 0, 0])
        else:
            subsectionLabel = ttk.Label(locFrame, text = prettySubsections)

        openPdfOnStartOfTheSection(subsectionLabel)
        bindChangeColorOnInAndOut(subsectionLabel)

        subsectionLabel.grid(row = 0, column= 0, sticky=tk.NW)

        if level != 0:
            openContentLabel = LabelWithClick(locFrame, text = "[content]")
            openContentOfTheSection(locFrame, openContentLabel)
            bindChangeColorOnInAndOut(openContentLabel)

            openContentLabel.grid(row = 0, column= 1, sticky=tk.NW)
        else:
            openContentLabel = LabelWithClick(locFrame, text = "[content]", padding= [0, 20, 0, 0])
            openContentLabel.clicked = self.showSubsectionsForTopSection[subsection]
            openContentOfTheTopSection(locFrame, openContentLabel)
            bindChangeColorOnInAndOut(openContentLabel)

            openContentLabel.grid(row = 0, column= 1, sticky=tk.NW)

    def populateTOC(self):
        text_curr = fsf.Wr.BookInfoStructure.getSubsectionsAsTOC()
        
        for i in range(len(text_curr)):
            self.addTOCEntry(text_curr[i][0], text_curr[i][1], i)

    def render(self, widjetObj=None, renderData=..., **kwargs):

        for child in self.scrollable_frame.winfo_children():
            child.destroy()

        if self.showSubsectionsForTopSection == {}:
            tsList = fsf.Wr.BookInfoStructure.getTopSectionsList()

            if tsList != _u.Token.NotDef.list_t:
                for ts in tsList:
                    self.showSubsectionsForTopSection[ts] = bool(int(fsf.Data.Book.sections[ts]["showSubsections"]))

        self.populateTOC()

        super().render(widjetObj, renderData, **kwargs)

        if self.openedMainImg != None:
            self.openedMainImg.event_generate(ww.currUIImpl.Data.BindID.customTOCMove)

class ChooseOriginalMaterial_OM(ww.currUIImpl.OptionMenu):
    prevChoice = ""

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 5, "row" : 13},
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

        zoomLevel = fsf.Wr.OriginalMaterialStructure.getMaterialZoomLevel(origMatName)
        pdfToken:str = origMatPath.split("/")[-1].replace(".pdf", "")
        cmd = oscr.setDocumentScale(pdfToken, zoomLevel)
        _u.runCmdAndWait(cmd)

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
            ww.Data.GeneralProperties_ID : {"column" : 5, "row" : 3},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_swritchToCurrSectionLayout_BTN"
        text= "To Section L"
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
            ww.Data.GeneralProperties_ID : {"column" : 5, "row" : 10},
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
            ww.Data.GeneralProperties_ID : {"column" : 5, "row" : 9},
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
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 2, "columnspan": 5},
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
            ww.Data.GeneralProperties_ID : {"column" : 5, "row" : 1},
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
            ww.Data.GeneralProperties_ID : {"column" : 4, "row" : 1},
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
        prevChoice = self.getData()
        self.setData(False)

        return prevChoice


class ImageGeneration_BTN(ww.currUIImpl.Button,
                          dc.AppCurrDataAccessToken):
    labelOptions = ["imIdx", "imName"]
    dataFromUser = [-1, -1]

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 1},
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

            if not re.match("^[0-9]+$", self.dataFromUser[0]):
                msg = "Incorrect image index \nId: '{0}'.".format(self.dataFromUser[0])
                wm.UI_generalManager.showNotification(msg, True)

                mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                            mmm.MathMenuManager)
                mainManager.show()

                return

            addToTOC = self.notify(addToTOC_CHB)
            addToTOCwIm = self.notify(addToTOCwImage_CHB)

            msg = "\
Do you want to create entry with \nId: '{0}', Name: '{1}'".format(self.dataFromUser[0], self.dataFromUser[1])
            response = wm.UI_generalManager.showNotification(msg, True)

            mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                        mmm.MathMenuManager)
            mainManager.show()
            
            if not response:
                return

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
            self.notify(comui.SourceImageLinks_OM)
            self.notify(LatestExtraImForEntry_LBL)
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
            self.updateLabel(self.labelOptions[0])
            return self.dataFromUser[0]

class ImageGeneration_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "columnspan": 6}
        }
        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {},
            ww.TkWidgets.__name__ : {"width": 240}
        }
        name = "_imageGeneration_ETR"
        defaultText = "0"

        super().__init__(prefix, 
                        name,
                        patentWidget, 
                        data,
                        extraBuildOptions,
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

class AddExtraImage_BTN(ww.currUIImpl.Button,
                        dc.AppCurrDataAccessToken):  
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 1, "row" : 1},
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
        extraImageIdx = _u.Token.NotDef.str_t

        if "_" in mainImIdx:
            mainAndExtraIndex = mainImIdx.split("_")

            for idx in mainAndExtraIndex:
                if not re.match("^[0-9]+$", idx):
                    msg = "Incorrect image index \nId: '{0}'.".format(idx)
                    wm.UI_generalManager.showNotification(msg, True)

                    mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                                mmm.MathMenuManager)
                    mainManager.show()

                    return

            mainImIdx = mainAndExtraIndex[0]
            extraImageIdx = mainAndExtraIndex[1]
        else:
            if not re.match("^[0-9]+$", mainImIdx):
                msg = "Incorrect main image index \nId: '{0}'.".format(mainImIdx)
                wm.UI_generalManager.showNotification(msg, True)

                mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                            mmm.MathMenuManager)
                mainManager.show()

                return

        
        if mainImIdx == _u.Token.NotDef.str_t:
            mainImIdx = fsf.Wr.Links.ImIDX.get_curr()
       
        extraImText = self.notify(ImageGeneration_ETR)
        
        currentSubsection = _upan.Current.Names.Section.name()
        
        extraImagePath_curr = _upan.Paths.Screenshot.getAbs()

        msg = "\
Do you want to add extra image to: '{0}' with name: '{1}'?".format(mainImIdx, extraImText)
        response = wm.UI_generalManager.showNotification(msg, True)

        mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                    mmm.MathMenuManager)
        mainManager.show()
        
        if not response:
            return

        # update the content file
        extraImagesDict = fsf.Data.Sec.extraImagesDict(currentSubsection)

        extraImagesList = []

        if extraImagesDict == _u.Token.NotDef.dict_t:
            extraImagesDict = {}

        if mainImIdx in list(extraImagesDict.keys()):
            extraImagesList = extraImagesDict[mainImIdx]
        
        if extraImageIdx != _u.Token.NotDef.str_t:
            extraImageIdx = int(extraImageIdx)

            if extraImageIdx < len(extraImagesList):
                extraImagesList[extraImageIdx] = extraImText
            else:
                msg = "\
Incorrect extra image index \nId: '{0}'.\n Outside the range of the indicies.".format(extraImageIdx)
                wm.UI_generalManager.showNotification(msg, True)

                mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                            mmm.MathMenuManager)
                mainManager.show()

                return
        else:
            extraImagesList.append(extraImText)

        if extraImText in extraImagesList:
            msg = "Extra image with text \n: '{0}' already exists. Proceed?".format(extraImText)
            response = wm.UI_generalManager.showNotification(msg, True)

            mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                        mmm.MathMenuManager)
            mainManager.show()

            if not response:
                return

        extraImagesDict[mainImIdx] = extraImagesList
        fsf.Data.Sec.extraImagesDict(currentSubsection, extraImagesDict)
        
        if extraImageIdx == _u.Token.NotDef.str_t:
            extraImageIdx = len(extraImagesList) - 1
        
        extraImageName = _upan.Names.getExtraImageName(mainImIdx, currentSubsection, extraImageIdx)
        extraImagePathFull = os.path.join(extraImagePath_curr, extraImageName)
        ocf.Wr.ScreenshotCalls.takeScreenshot(extraImagePathFull)

        tff.Wr.TexFileModify.addExtraImage(mainImIdx, str(extraImageIdx))

        self.notify(LatestExtraImForEntry_LBL)

        while not oscf.Wr.FsAppCalls.checkIfFileOrDirExists(extraImagePathFull + ".png"):
            time.sleep(0.3)

        self.notify(TOC_BOX)

class ImageGenerationRestart_BTN(ww.currUIImpl.Button):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 2, "row" : 1},
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
