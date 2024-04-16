from tkinter import ttk
from PIL import Image, ImageTk
import Pmw
import os
import tkinter as tk
import re
import time

import UI.widgets_wrappers as ww
import UI.widgets_facade as wf
import UI.widgets_collection.main.math.UI_layouts.mainLayout as mui
import UI.widgets_collection.main.math.UI_layouts.common as mcomui
import UI.widgets_collection.toc.toc as tocw
import settings.facade as sf
import data.constants as dc
import data.temp as dt
import scripts.osascripts as oscr
import outside_calls.outside_calls_facade as ocf
import file_system.file_system_facade as fsm
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import tex_file.tex_file_facade as tff
import UI.widgets_collection.utils as _uuicom
import UI.widgets_data as wd
import generalManger.generalManger as gm

class ImageText_ETR(ww.currUIImpl.TextEntry):
    subsection = None
    imIdx = None
    textETR = None
    etrWidget = None # note this is set top the object so the <ENTER> bind workss

    def __init__(self, patentWidget, prefix, row, column, imIdx, text):
        name = "_textImageTOC_ETR" + str(imIdx)
        self.defaultText = text

        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }


        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wd.Data.ENT.defaultTextColor,
                                            "font": ('Georgia 14')},
            ww.TkWidgets.__name__ : {"width": 40}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraBuildOptions,
                        defaultText = self.defaultText)
        super().setData(self.defaultText)
    
    def receiveNotification(self, _):
        return self.getData()
    
    def defaultTextCMD(self):
        pass


class ImageGroupOM(ttk.OptionMenu):
    var = None
    subsection = None
    imIdx = None
    tocBox = None

    def __init__(self, tocBox, subsection, imIdx, master, variable, default: str, *values: str):
        self.var = variable
        self.imIdx = imIdx
        self.subsection = subsection
        self.tocBox = tocBox

        super().__init__(master, variable, default, *values, command=lambda *args: self.chooseGroupCmd())
                        
    def chooseGroupCmd(self):
        imagesGroupList:list = list(fsm.Data.Sec.imagesGroupsList(self.subsection).keys())
        imagesGroupDict = fsm.Data.Sec.imagesGroupDict(self.subsection)
        imagesGroupDict[self.imIdx] =  imagesGroupList.index(self.var.get())
        fsm.Data.Sec.imagesGroupDict(self.subsection, imagesGroupDict)

        self.tocBox.render()


class EntryShowPermamentlyCheckbox(ttk.Checkbutton):
    subsection = None
    imidx = None
    var = None
    tocBox = None
    
    def __init__(self, parent, subsection, imIdx, name, tocBox):
        self.subsection = subsection
        self.imidx = str(imIdx)
        self.tocBox = tocBox

        tocWImageDict = fsm.Data.Sec.tocWImageDict(self.subsection)
        if tocWImageDict == _u.Token.NotDef.dict_t:
            alwaysShow = "0"
        else:
            alwaysShow = tocWImageDict[self.imidx]

        self.var = tk.IntVar()
        self.var.set(int(alwaysShow))

        super().__init__(parent, 
                        text ='', 
                        takefocus = 0, 
                        variable= self.var,
                        name = name,
                        command = lambda *args: self.__cmd())

    def __cmd(self):
        if self.var == None:
            return

        if self.tocBox == None:
            return

        tocWImageDict = fsm.Data.Sec.tocWImageDict(self.subsection)
        tocWImageDict[self.imidx] = str(self.var.get())
        fsm.Data.Sec.tocWImageDict(self.subsection, tocWImageDict)

        self.tocBox.renderWithoutScroll()


class TOC_BOX(ww.currUIImpl.ScrollableBox,
              dc.AppCurrDataAccessToken):
    subsectionClicked = _u.Token.NotDef.str_t
    entryClicked = _u.Token.NotDef.str_t
    secondEntryClicked = None

    renderFromTOCWindow = False

    secondEntryClickedImIdx = _u.Token.NotDef.str_t
    secondEntrySubsectionClicked = _u.Token.NotDef.str_t

    widgetToScrollTo = None

    currEntryWidget = None
    currSubsectionWidget = None

    showSubsectionsForTopSection = {}
    displayedImages = []
    parent = None
    openedMainImg = None

    showLinks = None
    showLinksForSubsections = []

    entryCopySubsection = None
    entryCopyImIdx = None

    cutEntry = False

    subsectionContentLabels = []

    currSecondRowLabels = []
    linkFrames = []

    showImagesLabels = {}

    updatedWidget = None

    class __EntryUIs:
        class __EntryUIData:
            def __init__(self, name, column) -> None:
                self.name = name
                self.column = column

        # row 1
        full = __EntryUIData("[f]", 1)
        im = __EntryUIData("[i]", 2)
        copyLink = __EntryUIData("[cl]", 3)
        pasteLink = __EntryUIData("[pl]", 4)
        copy = __EntryUIData("[c]", 5)
        pasteAfter = __EntryUIData("[p]", 6)
        excercises = __EntryUIData("[e]", 7)

        # row 2
        showLinks = __EntryUIData("[ShowLinks]", 1)
        alwaysShow = __EntryUIData("", 2)
        changeImSize = __EntryUIData("", 3)
        delete = __EntryUIData("[Delete]", 4)
        shift = __EntryUIData("[Shift]", 5)
        retake = __EntryUIData("[Retake]", 6)
        update = __EntryUIData("[Update]", 7)
        link = __EntryUIData("[Link]", 8)
        addExtra = __EntryUIData("[Add extra]", 9)
        proof = __EntryUIData("[p]", 10)
        group = __EntryUIData("", 11)

    # this data structure is used to store the
    # entry image widget that is turned into ETR for update
    class entryAsETR:
        subsection = _u.Token.NotDef.str_t
        imIdx = _u.Token.NotDef.str_t
        widget = None

        upddatedTextSubsection = _u.Token.NotDef.str_t
        upddatedTextImIdx = _u.Token.NotDef.str_t

        def reset(self):
            self.subsection = _u.Token.NotDef.str_t
            self.imIdx = _u.Token.NotDef.str_t
            self.widget = None

    class extraImAsETR:
        subsection = _u.Token.NotDef.str_t
        imIdx = _u.Token.NotDef.str_t
        eImIdx = _u.Token.NotDef.str_t
        widget = None

        upddatedText = _u.Token.NotDef.str_t
        upddatedTextExtraImIdx = _u.Token.NotDef.str_t

        def reset(self):
            self.subsection = _u.Token.NotDef.str_t
            self.imIdx = _u.Token.NotDef.str_t
            self.eImIdx = _u.Token.NotDef.str_t
            self.widget = None

    class entryTextOnlyAsETR:
        subsection = _u.Token.NotDef.str_t
        imIdx = _u.Token.NotDef.str_t
        widget = None

        def reset(self):
            self.subsection = _u.Token.NotDef.str_t
            self.imIdx = _u.Token.NotDef.str_t
            self.widget = None

    class subsectionAsETR:
        subsection = _u.Token.NotDef.str_t
        widget = None

        def reset(self):
            self.subsection = _u.Token.NotDef.str_t
            self.widget = None

    class groupAsETR:
        subsection = _u.Token.NotDef.str_t
        group = _u.Token.NotDef.str_t
        widget = None

        def reset(self):
            self.subsection = _u.Token.NotDef.str_t
            self.group = _u.Token.NotDef.str_t
            self.widget = None

    # used to filter toc data when the search is performed
    filterToken = ""
    searchSubsectionsText = False
    showAll = None
    shouldScroll = None

    def __init__(self, parentWidget, prefix, windth = 700, height = 570, 
                 showAll = False, makeScrollable = True, shouldScroll = True,
                 showLinks = False):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 3, "columnspan" : 6, "rowspan": 10},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_showCurrScreenshotLocation_text"

        self.parent = parentWidget.widgetObj
        self.showAll = showAll
        self.showLinks = showLinks

        self.entryAsETR = TOC_BOX.entryAsETR()
        self.extraImAsETR = TOC_BOX.extraImAsETR()
        self.entryTextOnlyAsETR = TOC_BOX.entryTextOnlyAsETR()
        self.subsectionAsETR = TOC_BOX.entryAsETR()
        self.groupAsETR = TOC_BOX.groupAsETR()

        self.subsectionClicked = fsm.Data.Book.subsectionOpenInTOC_UI
        self.entryClicked = fsm.Data.Book.entryImOpenInTOC_UI
        self.shouldScroll = shouldScroll

        tsList = fsm.Wr.BookInfoStructure.getTopSectionsList()

        if tsList != _u.Token.NotDef.list_t:
            for ts in tsList:
                if self.showAll:
                    self.showSubsectionsForTopSection[ts] = True
                else:
                    self.showSubsectionsForTopSection[ts] = bool(int(fsm.Data.Book.sections[ts]["showSubsections"]))

        super().__init__(prefix,
                        name,
                        parentWidget,
                        renderData = data,
                        height = height,
                        width = windth,
                        makeScrollable = makeScrollable)

    def scrollToEntry(self, subsection, imIdx):
        # move toc to
        self.subsectionClicked = subsection
        self.showSubsectionsForTopSection[subsection.split(".")[0]] = True
        self.entryClicked = imIdx

        # update to show the group when we show the entry
        groupsList = fsm.Data.Sec.imagesGroupsList(self.subsectionClicked)
        imGroupDict = fsm.Data.Sec.imagesGroupDict(self.subsectionClicked)
        groupsListKeys = groupsList.keys()

        if self.entryClicked in list(imGroupDict.keys()):
            idx = imGroupDict[self.entryClicked]
        else:
            return

        if idx != _u.Token.NotDef.str_t:
            groupName = list(groupsListKeys)[idx]
            groupsList[groupName] = True
            fsm.Data.Sec.imagesGroupsList(self.subsectionClicked, groupsList)

            self.__renderWithScrollAfter()

    def scrollIntoView(self, event, widget = None):
        if not self.shouldScroll:
            return

        try:
            posy = 0

            if widget == None:
                pwidget = event.widget
            else:
                pwidget = widget


            self.canvas.yview_scroll(-100, "units")
            self.canvas.update()
            pwidget.update()

            while pwidget != self.parent:
                posy += pwidget.winfo_y()
                pwidget = pwidget.master

            posy = 0

            if widget == None:
                pwidget = event.widget
            else:
                pwidget = widget

            while pwidget != self.parent:
                posy += pwidget.winfo_y()
                pwidget = pwidget.master

            pos = posy - self.scrollable_frame.winfo_rooty()
            height = self.scrollable_frame.winfo_height()
            self.canvas.yview_moveto((pos / height) - 0.04)
        except:
            pass
    
    def __renderWithScrollAfter(self):
        self.shouldScroll = False
        self.render()
        self.shouldScroll = True

        if self.currEntryWidget != None:
            self.currEntryWidget.clicked = False
            try:
                self.currEntryWidget.event_generate(ww.currUIImpl.Data.BindID.mouse1)
            except:
                pass

    def __renderWithoutScroll(self):
        self.shouldScroll = False
        self.render()
        self.shouldScroll = True

    def receiveNotification(self, broadcasterType, data = None, entryClicked = None):
        if broadcasterType == mui.ExitApp_BTN:
            tsList = fsm.Wr.BookInfoStructure.getTopSectionsList()

            sections = fsm.Data.Book.sections

            for ts in tsList:
                if ts == _u.Token.NotDef.str_t:
                    return

                sections[ts]["showSubsections"] = str(int(self.showSubsectionsForTopSection[ts]))

            fsm.Data.Book.sections = sections

            fsm.Data.Book.subsectionOpenInTOC_UI = self.subsectionClicked
            fsm.Data.Book.entryImOpenInTOC_UI = self.entryClicked
        elif broadcasterType == mui.AddExtraImage_BTN:
            self.entryClicked = entryClicked
            self.__renderWithScrollAfter()
        elif broadcasterType == mui.ImageGeneration_BTN:
            self.entryClicked = entryClicked
            self.__renderWithScrollAfter()
        elif broadcasterType == mui.ImageGroupAdd_BTN:
            self.__renderWithScrollAfter()
        elif broadcasterType == mui.RebuildCurrentSubsectionLatex_BTN:
            self.__renderWithScrollAfter()
        elif broadcasterType == mcomui.AddGlobalLink_BTN:
            self.__renderWithScrollAfter()
        elif broadcasterType == mui.ShowAllSubsections_BTN:
            self.__renderWithScrollAfter()
        elif broadcasterType == mui.ShowFirstEntryOfTheCurrPage:
            self.scrollToEntry(data[0], data[1])
            self.__renderWithScrollAfter()
        elif broadcasterType == mcomui.ImageSave_BTN:
            self.__renderWithScrollAfter()
        elif broadcasterType == mui.ShowHideLinks_BTN:
            self.showLinks = not self.showLinks
            self.showLinksForSubsections = []
            self.__renderWithScrollAfter()
        elif broadcasterType == mui.ScrollToCurrSubsectionAndBack_BTN:
            self.scrollToEntry(data[1], data[2])
        elif broadcasterType == tocw.Filter_ETR:
            self.filterToken = data[0]
            self.searchSubsectionsText = data[1]
            self.__renderWithoutScroll()
        else:
            self.__renderWithScrollAfter()

    def addTOCEntry(self, subsection, level, row):
        def openPdfOnStartOfTheSection(widget:_uuicom.TOCLabelWithClick):
            def __cmd(event = None, *args):
                # open orig material on page
                origMatNameDict = fsm.Data.Sec.origMatNameDict(subsection)
                omName = origMatNameDict[list(origMatNameDict.keys())[-1]]

                if str(omName) == _u.Token.NotDef.str_t:
                    # when there is no entries yet we use the current origMaterial name
                    omName = fsm.Data.Book.currOrigMatName

                omFilepath = fsm.Wr.OriginalMaterialStructure.getMaterialPath(omName)
                subsectionStartPage = fsm.Data.Sec.start(subsection)

                ocf.Wr.PdfApp.openPDF(omFilepath, subsectionStartPage)

                zoomLevel = fsm.Wr.OriginalMaterialStructure.getMaterialZoomLevel(omName)
                pdfToken:str = omFilepath.split("/")[-1].replace(".pdf", "")
                cmd = oscr.setDocumentScale(pdfToken, zoomLevel)
                _u.runCmdAndWait(cmd)

                event.widget.configure(foreground="white")
            
            widget.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])

        def openOMOnThePageOfTheImage(widget:_uuicom.TOCLabelWithClick, targetSubsection, targetImIdx):
            def __cmd(event = None, *args):
                # open orig material on page
                imOMName = fsm.Data.Sec.origMatNameDict(targetSubsection)[targetImIdx]

                omFilepath = fsm.Wr.OriginalMaterialStructure.getMaterialPath(imOMName)                
                imLinkOMPageDict = fsm.Data.Sec.imLinkOMPageDict(targetSubsection)
                page = imLinkOMPageDict[targetImIdx]

                ocf.Wr.PdfApp.openPDF(omFilepath, page)

                zoomLevel = fsm.Wr.OriginalMaterialStructure.getMaterialZoomLevel(imOMName)
                pdfToken:str = omFilepath.split("/")[-1].replace(".pdf", "")
                cmd = oscr.setDocumentScale(pdfToken, zoomLevel)
                _u.runCmdAndWait(cmd)
            
            widget.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])

        def openWebOfTheImage(widget:_uuicom.TOCLabelWithClick, webLink):
            def __cmd(event = None, *args):
                cmd = "open -na 'Google Chrome' --args --new-window \"" + webLink + "\""
                _u.runCmdAndWait(cmd)
            
            widget.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])

        # def openSectionOnIdx(widget:_uuicom.TOCLabelWithClick, imIdx):
        #     def __cmd(event = None, *args):
        #         # open orig material on page
        #         bookName = sf.Wr.Manager.Book.getCurrBookName()
        #         currTopSection = fsm.Data.Book.currTopSection

        #         url = tff.Wr.TexFileUtils.getUrl(bookName, currTopSection, subsection, imIdx, "full", notLatex=True)
                
        #         os.system("open {0}".format(url))
        #         event.widget.configure(foreground="white")
            
        #     widget.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])

        def openSecondaryImage(widget:_uuicom.TOCLabelWithClick):
            def __cmd(event = None, *args):
                widget = event.widget
                currImIdx = widget.imIdx
                secondSubsection = widget.subsection

                if (currImIdx == self.secondEntryClickedImIdx) and \
                    (secondSubsection == self.secondEntrySubsectionClicked):
                    self.secondEntryClickedImIdx = _u.Token.NotDef.str_t
                    self.secondEntrySubsectionClicked = _u.Token.NotDef.str_t
                    self.secondEntryClicked.clicked = False
                    self.secondEntryClicked = None
                else:
                    widget.clicked = True
                    self.secondEntrySubsectionClicked = secondSubsection
                    self.secondEntryClickedImIdx = currImIdx
                    self.secondEntryClicked = widget

                self.__renderWithoutScroll()
            
            widget.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])

        def __showIMagesONClick(event, label:_uuicom.TOCLabelWithClick, subSecID, 
                                shouldScroll = False, 
                                imPad = 120, link = False, textOnly = False,
                                *args):
            label:_uuicom.TOCLabelWithClick = event.widget
            imIdx = label.imIdx
            subsection = label.subsection
            '''
            TODO: need to change to the wrapper
            '''
            if link:
                tframe = label.master
            else:
                tframe = label.master.master

            gpframe = tframe.master
            balloon = Pmw.Balloon(tframe)

            isWdgetLink = "gllink" in str(label).lower().split(".")[-1]

            def __cmd(event, *args):
                if label.alwaysShow \
                    and (int(event.type) == 4) \
                    and (not self.showAll) \
                    and (not link):
                    currTopSection = subsection.split(".")[0]
                    fsm.Data.Book.currTopSection = currTopSection
                    fsm.Data.Book.currSection = subsection
                    fsm.Data.Book.subsectionOpenInTOC_UI = subsection
                    fsm.Data.Book.entryImOpenInTOC_UI = imIdx

                    self.notify(mui.ChooseTopSection_OM)
                    self.notify(mui.ChooseSubsection_OM)
                    self.notify(mcomui.SourceImageLinks_OM)
                    self.notify(mui.ScreenshotLocation_LBL)

                    self.subsectionClicked = subsection
                    self.entryClicked = imIdx

                shoulShowSecondRow = False

                if not link:
                    for w in self.linkFrames:
                        try:
                            if (w.subsection == subsection) and (w.imIdx == imIdx):
                                w.render()
                            else:
                                if not self.showLinks:
                                    w.grid_forget()
                        except:
                            pass

                    for w in  self.currSecondRowLabels:
                        try:
                            if (w.subsection == subsection) and (w.imIdx == imIdx):
                                w.render()
                                shoulShowSecondRow = True
                            else:
                                w.grid_forget()
                        except:
                            pass

                if ((not label.clicked) and ((int(event.type) == 4))) or\
                    ((not label.clicked) and ((int(event.type) == 35))) or\
                    ((label.clicked) and ((int(event.type) == 4)) and shoulShowSecondRow and (not link)):
                    if shoulShowSecondRow:
                        for k,w in self.showImagesLabels.items():
                            if k == subsection + imIdx:
                                try:
                                    showImages = self.showImagesLabels[subsection + imIdx]
                                    showImages.configure(foreground = "brown")  
                                    _uuicom.bindChangeColorOnInAndOut(showImages, shouldBeBrown = True)
                                except:
                                    pass
                            else:
                                try:
                                    showImages = self.showImagesLabels[k]
                                    showImages.configure(foreground = "white")  
                                    _uuicom.bindChangeColorOnInAndOut(showImages, shouldBeBrown = False)
                                except:
                                    pass

                    if self.showAll and shouldScroll and (not link):
                        mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                wf.Wr.MenuManagers.MathMenuManager)
                        mainManager.moveTocToEntry(subsection, imIdx, True)
                    # NOTE: not sure is we need to
                    #     return

                    if ((int(event.type) == 4) or (shouldScroll)) and (not link):
                        self.currEntryWidget = event.widget

                    if shouldScroll and (not link):
                        _uuicom.closeAllImages(gpframe, self.showAll, link,
                                               [subsection, self.secondEntryClickedImIdx])

                    if (not label.alwaysShow) \
                        and ((not isWdgetLink) or shoulShowSecondRow) \
                        and (not link):
                        self.entryClicked = imIdx

                    label.clicked = True

                    imageGroups = list(fsm.Data.Sec.imagesGroupsList(subsection).keys())
                    imageGroupidx = fsm.Data.Sec.imagesGroupDict(subsection)[imIdx]
                    imageGroup = imageGroups[int(imageGroupidx)]

                    shouldShowGroup = fsm.Data.Sec.imagesGroupsList(subsection)[imageGroup]

                    if (not shouldShowGroup) and (not isWdgetLink) and (not self.showAll):
                        return

                    if (not link) \
                        and shouldScroll \
                        and self.shouldScroll \
                        and (imIdx != self.secondEntryClickedImIdx)\
                        and (not self.showAll):
                        currTopSection = subsection.split(".")[0]
                        fsm.Data.Book.currTopSection = currTopSection
                        fsm.Data.Book.currSection = subsection
                        fsm.Data.Book.subsectionOpenInTOC_UI = subsection
                        fsm.Data.Book.entryImOpenInTOC_UI = imIdx

                        dt.UITemp.Link.subsection = subsection
                        dt.UITemp.Link.imIdx = imIdx

                        self.notify(mui.ChooseTopSection_OM)
                        self.notify(mui.ChooseSubsection_OM)
                        self.notify(mcomui.SourceImageLinks_OM)
                        self.notify(mui.ScreenshotLocation_LBL)

                        if not self.renderFromTOCWindow:
                            self.notify(mui.ScrollToCurrSubsectionAndBack_BTN)

                        self.subsectionClicked = subsection
                        self.entryClicked = imIdx

                    # mainImage
                    bindData  = [[ww.currUIImpl.Data.BindID.customTOCMove], 
                                 [lambda event: self.scrollIntoView(event)]]

                    uiResizeEntryIdx = fsm.Data.Sec.imageUIResize(subsection)

                    if imIdx in list(uiResizeEntryIdx.keys()):
                        resizeFactor = float(uiResizeEntryIdx[imIdx])
                    else:
                        resizeFactor = 1.0

                    if not textOnly:
                        imLabel = _uuicom.addMainEntryImageWidget(tframe, subsection, imIdx, 
                                                                imPad, self.displayedImages, 
                                                                balloon, bindData, resizeFactor = resizeFactor)

                        imLabel.render()
                    else:
                        def __updateEntryTextOnly(event, *args):
                            if (self.entryTextOnlyAsETR.subsection != _u.Token.NotDef.str_t) and \
                                (self.entryTextOnlyAsETR.imIdx != _u.Token.NotDef.str_t):
                                newText = self.entryTextOnlyAsETR.widget.getData()
                                imTextDict = fsm.Data.Sec.imageText(self.entryTextOnlyAsETR.subsection)
                                imTextDict[self.entryTextOnlyAsETR.imIdx] = newText
                                fsm.Data.Sec.imageText(self.entryTextOnlyAsETR.subsection, imTextDict)
                                self.entryTextOnlyAsETR.reset()
                                self.__renderWithScrollAfter()
                            else:
                                self.entryTextOnlyAsETR.subsection = event.widget.subsection
                                self.entryTextOnlyAsETR.imIdx = event.widget.imIdx
                                self.entryTextOnlyAsETR.widget = event.widget.etrWidget
                                self.__renderWithScrollAfter()

                        mainWidgetName = _upan.Names.UI.getMainEntryWidgetName(subsection, imIdx)
                        txt = fsm.Data.Sec.imageText(subsection)[imIdx]

                        if (subsection == self.entryTextOnlyAsETR.subsection)\
                            and (imIdx == self.entryTextOnlyAsETR.imIdx) :
                            imLabel = _uuicom.MultilineText_ETR(tframe, 
                                                                      mainWidgetName, 
                                                                      4,
                                                                      0, 
                                                                      0, 
                                                                      txt)
                            imLabel.config(width=90)
                            imLabel.config(padx=10)
                            imLabel.config(pady=10)
                            imLabel.imIdx = imIdx
                            imLabel.subsection = subsection
                            imLabel.etrWidget = imLabel
                            imLabel.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                                                 [__updateEntryTextOnly])
                            self.entryTextOnlyAsETR.widget = imLabel
                            imLabel.rebind(*bindData)
                            imLabel.render()
                            imLabel.focus_force()
                        else:
                            imLabel = _uuicom.TOCTextWithClick(tframe, 
                                                                mainWidgetName,
                                                                4,
                                                                0,
                                                                1000,
                                                                text=txt,
                                                                padx = 10,
                                                                pady = 10,
                                                                width = 95
                                                                )
                            imLabel.subsection = subsection
                            imLabel.imIdx = imIdx
                            imLabel.render()

                            if not link:
                                imLabel.rebind([ww.currUIImpl.Data.BindID.mouse2], [__updateEntryTextOnly])
                                imLabel.rebind(*bindData)

                    if not isWdgetLink:
                        self.openedMainImg = imLabel

                    if not textOnly:
                        # extraImages
                        def skippProof(subsection, imIdx, exImIdx):
                            extraImages = fsm.Data.Sec.extraImagesDict(subsection)[imIdx]
                            eImText = extraImages[exImIdx]
                            return "proof" in eImText.lower()\
                                    and not dt.AppState.ShowProofs.getData("appCurrDataAccessToken")

                        exImLabels = _uuicom.addExtraEntryImagesWidgets(tframe, subsection, imIdx,
                                                                        imPad, self.displayedImages, balloon,
                                                                        skippProof, resizeFactor, tocFrame = self)
                        for l in exImLabels:
                            l.render()

                    # NOTE: for links
                    if int(event.type) == 4 or \
                       int(event.type) == 35:
                        for child in tframe.winfo_children():
                            if "contentImages_" + subSecID in str(child):
                                child.clicked = True

                    if shouldScroll and (not self.showAll) and (not link):
                        imLabel.generateEvent(ww.currUIImpl.Data.BindID.customTOCMove)
                else:
                    if not isWdgetLink:
                        if int(event.type) == 4:
                            self.currEntryWidget = event.widget
                            self.currEntryWidget.clicked = False

                        # self.entryClicked = _u.Token.NotDef.str_t
                        self.scrollIntoView(event)

                        for w in  self.currSecondRowLabels:
                            if (w.subsection == subsection) and (w.imIdx == imIdx):
                                w.grid_forget()

                    _uuicom.closeAllImages(gpframe, self.showAll, link, linkIdx = imIdx)

            __cmd(event, *args)

        def openContentOfTheSection(frame:_uuicom.TOCFrame, label:_uuicom.TOCLabelWithClick):
            def __cmd(event = None, *args):
                # open orig material on page

                links:dict = fsm.Data.Sec.imLinkDict(subsection)
                imagesGroupDict:dict = fsm.Data.Sec.imagesGroupDict(subsection)
                imagesGroupsWShouldShow:list = fsm.Data.Sec.imagesGroupsList(subsection)
                imagesGroups:list = list(imagesGroupsWShouldShow.keys())

                def closeAllSubsections():
                    for wTop1 in event.widget.master.master.winfo_children():
                        for wTop2 in wTop1.winfo_children():
                            if "labelwithclick" in str(wTop2):
                                wTop2.clicked = False
                            if "contentFr_"  in str(wTop2) or "contentDummyFr_" in str(wTop2):
                                wTop2.destroy()

                def shiftEntryCmd(event, *args):
                    widget = event.widget
                    fsm.Wr.SectionInfoStructure.shiftEntryUp(widget.subsection,
                                                                widget.imIdx)
                    self.__renderWithScrollAfter()

                def showLinksForEntryCmd(event, *args):
                    widget = event.widget
                    subsection = widget.subsection
                    imIdx =  widget.imIdx
                    liskShpowId = subsection + "_" + imIdx

                    linkShouldBePresent = True

                    for l in self.showLinksForSubsections:
                        if liskShpowId in l:
                            self.showLinksForSubsections = []
                            linkShouldBePresent = False
                            break

                    if linkShouldBePresent:
                        if imIdx in list(fsm.Data.Sec.imGlobalLinksDict(subsection).keys()):
                            glLinks:dict = fsm.Data.Sec.imGlobalLinksDict(subsection)[imIdx]

                            for ln in glLinks:
                                if not self.showLinks:
                                    self.showLinksForSubsections.append(subsection + "_" + imIdx + "_" + ln)

                            self.showLinksForSubsections.append(liskShpowId)

                    self.__renderWithScrollAfter()

                def copyEntryCmd(event, *args):
                    widget = event.widget
                    self.entryCopySubsection = widget.subsection
                    self.entryCopyImIdx = widget.imIdx
                    self.cutEntry = False

                def cutEntryCmd(event, *args):
                    widget = event.widget
                    self.entryCopySubsection = widget.subsection
                    self.entryCopyImIdx = widget.imIdx
                    self.cutEntry = True

                def retakeImageCmd(event, *args):
                    widget = event.widget
                    subsection = widget.subsection
                    imIdx = widget.imIdx

                    currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                    imagePath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBookPath,
                                                                                subsection,
                                                                                str(imIdx))
                    ocf.Wr.FsAppCalls.deleteFile(imagePath)
                    ocf.Wr.ScreenshotCalls.takeScreenshot(imagePath)

                    timer = 0
                    while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                        time.sleep(0.3)
                        timer += 1

                        if timer > 50:
                            break

                    self.__renderWithScrollAfter()

                def pasteEntryCmd(event, *args):
                    widget = event.widget

                    if None in [self.entryCopySubsection, self.entryCopyImIdx] or\
                       _u.Token.NotDef.str_t in [self.entryCopySubsection, self.entryCopyImIdx]:
                        _u.log.autolog("Did not paste entry. The copy data is not correct.")
                        return

                    fsm.Wr.SectionInfoStructure.insertEntryAfterIdx(self.entryCopySubsection,
                                                                    self.entryCopyImIdx,
                                                                    widget.subsection,
                                                                    widget.imIdx,
                                                                    self.cutEntry)
                    self.__renderWithScrollAfter()

                def removeEntryCmd(event, *args):
                    widget = event.widget
                    fsm.Wr.SectionInfoStructure.removeEntry(widget.subsection, widget.imIdx)
                    self.__renderWithScrollAfter()

                def delGlLinkCmd(event, *args):
                    widget = event.widget
                    gm.GeneralManger.RemoveGlLink(widget.targetSubssection,
                                                  widget.sourceSubssection,
                                                  widget.sourceImIdx,
                                                  widget.targetImIdx)
                    self.__renderWithScrollAfter()

                def delWebLinkCmd(event, *args):
                    widget = event.widget
                    gm.GeneralManger.RemoveWebLink(widget.sourceSubssection,
                                                   widget.sourceImIdx,
                                                   widget.sourceWebLinkName)
                    self.__renderWithScrollAfter()

                def addGlLinkCmd(event, *args):
                    widget:_uuicom.TOCLabelWithClick = event.widget
                    self.notify(mcomui.AddGlobalLink_BTN,
                                [widget.subsection, widget.imIdx])
                    self.__renderWithScrollAfter()

                def addExtraImCmd(event, *args):
                    widget:_uuicom.TOCLabelWithClick = event.widget
                    self.notify(mui.AddExtraImage_BTN,
                                data = [widget.subsection, widget.imIdx])
                    self.__renderWithScrollAfter()

                def pasteGlLinkCmd(event, *args):
                    widget = event.widget
                    sourceSubsection = widget.subsection
                    sourceTopSection = sourceSubsection.split(".")[0]
                    sourceImIdx = widget.imIdx
                    targetSubsection = dt.UITemp.Link.subsection
                    targetImIdx = dt.UITemp.Link.imIdx

                    if targetSubsection != _u.Token.NotDef.str_t\
                        and targetImIdx != _u.Token.NotDef.str_t:
                        gm.GeneralManger.AddLink(f"{targetSubsection}.{targetImIdx}",
                                                sourceSubsection,
                                                sourceImIdx,
                                                sourceTopSection)
                        self.__renderWithScrollAfter()

                    if self.showAll:
                        mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                wf.Wr.MenuManagers.MathMenuManager)
                        mainManager.moveTocToCurrEntry()
                        tocManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                wf.Wr.MenuManagers.TOCManager)
                        tocManager.show()

                def copyGlLinkCmd(event, *args):
                    widget:_uuicom.TOCLabelWithClick = event.widget
                    dt.UITemp.Link.subsection = widget.subsection
                    dt.UITemp.Link.imIdx = widget.imIdx

                def resizeEntryImgCMD(event, *args):
                    resizeFactor = event.widget.get()

                    # check if the format is right
                    if not re.match("^[0-9]\.[0-9]$", resizeFactor):
                        _u.log.autolog(\
                            f"The format of the resize factor '{resizeFactor}'is not correct")
                        return
                    
                    subsection = event.widget.subsection
                    imIdx = event.widget.imIdx
                    
                    uiResizeEntryIdx = fsm.Data.Sec.imageUIResize(subsection)

                    if (uiResizeEntryIdx == None) \
                        or (uiResizeEntryIdx == _u.Token.NotDef.dict_t):
                        uiResizeEntryIdx = {}

                    uiResizeEntryIdx[imIdx] = resizeFactor

                    fsm.Data.Sec.imageUIResize(subsection, uiResizeEntryIdx)

                    self.__renderWithScrollAfter()

                def openExcerciseMenu(event, *args):
                    exMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                wf.Wr.MenuManagers.ExcerciseManager)
                    exMenuManger.subsection = event.widget.subsection
                    exMenuManger.imIdx = event.widget.imIdx

                    event.widget.shouldShowExMenu = not event.widget.shouldShowExMenu
                    if (event.widget.shouldShowExMenu):
                        exMenuManger.show()
                    else:
                        exMenuManger.hide()

                def openProofsMenu(event, *args):
                    prMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                wf.Wr.MenuManagers.ProofsManager)
                    prMenuManger.subsection = event.widget.subsection
                    prMenuManger.imIdx = event.widget.imIdx

                    event.widget.shouldShowExMenu = not event.widget.shouldShowExMenu
                    if (event.widget.shouldShowExMenu):
                        prMenuManger.show()
                    else:
                        prMenuManger.hide()

                def updateEntry(event, *args):
                    if (self.entryAsETR.subsection != _u.Token.NotDef.str_t) and \
                        (self.entryAsETR.imIdx != _u.Token.NotDef.str_t):
                        newText = self.entryAsETR.widget.getData()
                        imLinkDict = fsm.Data.Sec.imLinkDict(self.entryAsETR.subsection)
                        textOnly = fsm.Data.Sec.textOnly(self.entryAsETR.subsection)[self.entryAsETR.imIdx]
                        imLinkDict[self.entryAsETR.imIdx] = newText
                        fsm.Data.Sec.imLinkDict(self.entryAsETR.subsection, imLinkDict)
                        fsm.Wr.SectionInfoStructure.rebuildEntryLatex(self.entryAsETR.subsection,
                                                                      self.entryAsETR.imIdx,
                                                                      newText,
                                                                      textOnly
                                                                      )
                        self.entryAsETR.reset()
                        self.__renderWithoutScroll()
                        self.scrollIntoView(None, self.updatedWidget)
                    else:
                        self.entryAsETR.subsection = event.widget.subsection
                        self.entryAsETR.imIdx = event.widget.imIdx
                        self.entryAsETR.widget =event.widget.etrWidget
                        self.entryAsETR.upddatedTextSubsection = event.widget.subsection
                        self.entryAsETR.upddatedTextImIdx = event.widget.imIdx
                        self.__renderWithoutScroll()
                        self.scrollIntoView(None, self.entryAsETR.widget)

                # 4 : event of mouse click
                # 19 : event of being rendered
                if ((not label.clicked) and (int(event.type) == 4)) or\
                    ((self.subsectionClicked == subsection) and (int(event.type) == 19)):
                    if not self.showAll:
                        closeAllSubsections()

                    i = 0

                    for conWidget in self.subsectionContentLabels:
                        if conWidget.subsection != subsection:
                            conWidget.clicked = False

                    subSecID = _upan.Names.UI.getWidgetSubsecId(subsection)
                    prevImGroupName = _u.Token.NotDef.str_t

                    extraImagesDict = fsm.Data.Sec.extraImagesDict(subsection)

                    subsectionText:str = fsm.Data.Sec.text(subsection)

                    for k,v in links.items():
                        textOnly = fsm.Data.Sec.textOnly(subsection)[k]

                        entryImText = fsm.Wr.SectionInfoStructure.getEntryImText(subsection, k)
                        
                        if k in list(extraImagesDict.keys()):
                            for t in extraImagesDict[k]:
                                entryImText += t

                        if self.searchSubsectionsText:
                            tokenInSubsectionText = self.filterToken.lower() not in subsectionText.lower()
                        else:
                            tokenInSubsectionText = True                   

                        if (self.filterToken != ""):
                            if (self.filterToken.lower() not in v.lower())\
                                and (self.filterToken.lower() not in entryImText.lower())\
                                and tokenInSubsectionText:
                                continue

                        currImGroupidx = imagesGroupDict[k]

                        if currImGroupidx == _u.Token.NotDef.str_t:
                            currImGroupidx = 0

                        currImGroupName = imagesGroups[currImGroupidx]

                        topPad = 0
                        gridRowStartIdx = 1

                        if currImGroupName != prevImGroupName:
                            if not imagesGroupsWShouldShow[currImGroupName]:
                                topPad = 0
                            elif (k != "0"):
                                topPad = 5

                        if self.filterToken != "":
                            topPad = 0

                        nameId = _upan.Names.Entry.getEntryNameID(subsection, k)

                        tempFrame = _uuicom.TOCFrame(frame,
                                              prefix = "contentFr_" + nameId,
                                              padding=[0, topPad, 0, 0],
                                              row = i + 2, column = 0, columnspan = 100)

                        def getGroupImg(subsection, currImGroupName):
                            gi = str(list(fsm.Data.Sec.imagesGroupsList(subsection).keys()).index(currImGroupName))
                            groupImgPath = _upan.Paths.Screenshot.Images.getGroupImageAbs(sf.Wr.Manager.Book.getCurrBookName(), 
                                                                    subsection,
                                                                    gi)

                            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(groupImgPath):
                                result = Image.open(groupImgPath)
                            else:
                                result = \
                                    fsm.Wr.SectionInfoStructure.rebuildGroupOnlyImOnlyLatex(subsection,
                                                                                            currImGroupName)

                            shrink = 0.8
                            result.thumbnail([int(result.size[0] * shrink),int(result.size[1] * shrink)], Image.LANCZOS)
                            result = ImageTk.PhotoImage(result)
                            return result

                        if currImGroupName != prevImGroupName:
                            if currImGroupName != "No group":
                                imageGroupFrame = _uuicom.TOCFrame(tempFrame,
                                                            prefix = "contentImageGroupFr_" + nameId,
                                                            padding=[0, topPad, 0, 0], 
                                                            row = 0, column = 0, columnspan = 100)
                                imageGroupFrame.render()

                                def __updateGroup(event, *args):
                                    if (self.groupAsETR.subsection != _u.Token.NotDef.str_t) and\
                                        (self.groupAsETR.group != _u.Token.NotDef.str_t):
                                        newText = self.groupAsETR.widget.getData()
                                        oldGroupName = self.groupAsETR.group
                                        imagesGroupsList = \
                                            fsm.Data.Sec.imagesGroupsList(event.widget.subsection)
                                        imagesGroupsList = \
                                            {k if k != oldGroupName else newText: v for k,v in imagesGroupsList.items()}
                                        fsm.Data.Sec.imagesGroupsList(self.subsectionAsETR.subsection,
                                                                      imagesGroupsList)
                                        fsm.Wr.SectionInfoStructure.rebuildGroupOnlyImOnlyLatex(subsection,
                                                                                                newText)

                                        self.groupAsETR.reset()
                                    else:
                                        self.groupAsETR.subsection = event.widget.subsection
                                        self.groupAsETR.group = event.widget.group

                                    self.__renderWithScrollAfter()

                                if (subsection != self.groupAsETR.subsection) or\
                                    (currImGroupName != self.groupAsETR.group):
                                    img = getGroupImg(subsection, currImGroupName)
                                    imageGroupLabel = _uuicom.TOCLabelWithClick(imageGroupFrame, 
                                                                image = img, 
                                                                prefix = "contentGroupP_" + nameId,
                                                                padding = [30, 0, 0, 0], 
                                                                row = 0, column = 0)
                                    imageGroupLabel.image = img
                                    imageGroupLabel.subsection = subsection
                                    imageGroupLabel.group = currImGroupName
                                    imageGroupLabel.rebind([ww.currUIImpl.Data.BindID.mouse2],
                                                            [__updateGroup])
                                else:
                                    imageGroupLabel = _uuicom.MultilineText_ETR(imageGroupFrame, 
                                                            "contentGroupP_" + nameId, 
                                                            0, 0, 
                                                            "", # NOTE: not used anywhere  
                                                            currImGroupName)
                                    imageGroupLabel.subsection = subsection
                                    imageGroupLabel.etrWidget = imageGroupLabel
                                    self.groupAsETR.widget = imageGroupLabel
                                    imageGroupLabel.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                                                            [__updateGroup])
                                    imageGroupLabel.focus_force()

                                imageGroupLabel.render()
                                hideImageGroupLabel = _uuicom.TOCLabelWithClick(imageGroupFrame, 
                                                                        text = "[show/hide]",
                                                                        prefix = "contentHideImageGroupLabel_" + nameId,
                                                                        row = 0, column = 1)

                                if not self.showAll:
                                    hideImageGroupLabel.render()

                                hideImageGroupLabel.subsection = subsection
                                hideImageGroupLabel.imIdx = k
                                hideImageGroupLabel.group = currImGroupName

                                _uuicom.bindChangeColorOnInAndOut(hideImageGroupLabel)

                                def __cmd(e):
                                    imagesGroupsList = fsm.Data.Sec.imagesGroupsList(e.widget.subsection)
                                    imagesGroupsList[e.widget.group] = not imagesGroupsList[e.widget.group]
                                    fsm.Data.Sec.imagesGroupsList(e.widget.subsection, imagesGroupsList)
                                    self.__renderWithoutScroll()

                                hideImageGroupLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])
        
                                newGroup = _uuicom.ImageSize_ETR(imageGroupFrame,
                                        prefix = "contentNewGroupImageGroupLabel_" + nameId,
                                        row = 0, 
                                        column = 3,
                                        imIdx = k,
                                        text = currImGroupName,
                                        width = 10)
                                newGroup.subsection = subsection
                                newGroup.render()
                                newGroup.setData(currImGroupName)

                                moveGroup = _uuicom.ImageSize_ETR(imageGroupFrame,
                                        prefix = "contentMoveImageGroupLabel_" + nameId,
                                        row = 0, 
                                        column = 2,
                                        imIdx = k,
                                        text = subsection + ":" + str(k),
                                        width = 10)
                                moveGroup.subsection = subsection
                                moveGroup.imIdx = k

                                def __moveGroup(e, *args): 
                                    # NOTE: this is a hack but I can't find a better way atm   
                                    wName = str(e.widget)
                                    wName = wName.split("contentmoveimagegrouplabel_")[-1]
                                    wName = wName.split("_imageSizeTOC_ETR")[0]
                                    subsection = wName.split("_")[0].replace("$", ".")
                                    imIdx = wName.split("_")[1]
                                    newGroupNameWName ="contentNewGroupImageGroupLabel_".lower()
                                    newGroupNameW = [i for i in e.widget.master.winfo_children() \
                                                     if newGroupNameWName.lower() in str(i)][0]

                                    targetWholePath:str = e.widget.get()

                                    if ":" not in targetWholePath:
                                        _u.log.autolog("Incorrect destination path")

                                    targetSubsection = targetWholePath.split(":")[0]
                                    targetEntryIdx = targetWholePath.split(":")[1]
                                    targetGroupName = newGroupNameW.get() if newGroupNameW.get() != "" else "No Group"
                                    sourceSubsection = subsection
                                    sourceEntryIdx = imIdx
                                    sourceGroupNameIdx = fsm.Data.Sec.imagesGroupDict(sourceSubsection)[sourceEntryIdx]
                                    sourceGroupName = list(fsm.Data.Sec.imagesGroupsList(sourceSubsection).keys())[sourceGroupNameIdx]

                                    # ask the user if we wnat to proceed.
                                    msg = "\
Do you want to move group \n\nto subsection\n'{0}' \n\nand entry: \n'{1}'\n\n with group name \n'{2}'?".format(targetSubsection, 
                                                                                                 targetEntryIdx, 
                                                                                                 targetGroupName)
                                    response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

                                    mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                                wf.Wr.MenuManagers.MathMenuManager)
                                    mainManager.show()

                                    if not response:
                                        return

                                    gm.GeneralManger.moveGroupToSubsection(sourceSubsection, sourceGroupName,
                                                                           targetSubsection, targetGroupName, targetEntryIdx)
                                    self.__renderWithoutScroll()
                                moveGroup.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                                        [__moveGroup])
                                moveGroup.render()

                                gridRowStartIdx = 2
                            else:
                                img = getGroupImg(subsection, currImGroupName)
                                imageNoGroupLabel = _uuicom.TOCLabelWithClick(tempFrame, 
                                                            image = img,
                                                            prefix = "contentNoGroupP_" + nameId,
                                                            padding= [30, 0, 0, 0],
                                                            row = 0, column = 0)
                                imageNoGroupLabel.image = img
                                imageNoGroupLabel.render()
                                gridRowStartIdx = 2

                        tempFrameRow1 = _uuicom.TOCFrame(tempFrame,
                                            prefix = "contentRow1Fr_" + nameId,
                                            padding=[0, topPad, 0, 0],
                                            row = gridRowStartIdx - 1, 
                                            column = 0, columnspan = 100)

                        tempFrameRow2 = _uuicom.TOCFrame(tempFrame,
                                            prefix = "contentRow2Fr_" + nameId,
                                            padding=[60, topPad, 0, 0],
                                            row = gridRowStartIdx, 
                                            column = 0, columnspan = 100)
                        tempFrameRow2.subsection = subsection
                        tempFrameRow2.imIdx = k
                        self.currSecondRowLabels.append(tempFrameRow2)

                        if currImGroupName not in imagesGroups:
                            currImGroupName = imagesGroups[0]
                            imagesGroupDict[k] = 0
                            fsm.Data.Sec.imagesGroupDict(subsection, imagesGroupDict)

                        imagesGroup = ImageGroupOM(self, subsection, k, tempFrameRow2, 
                                                   tk.StringVar(), currImGroupName, *imagesGroups)

                        def getEntryImg(tex, subsection, imIdx):
                            textOnly = fsm.Data.Sec.textOnly(subsection)[imIdx]
                            currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                            entryImgPath = _upan.Paths.Screenshot.Images.getMainEntryTexImageAbs(currBookPath, 
                                                                                              subsection, 
                                                                                              imIdx)

                            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryImgPath):
                                result = Image.open(entryImgPath)
                            else:
                                result = tff.Wr.TexFileUtils.fromTexToImage(tex, 
                                                                            entryImgPath,
                                                                            fixedWidth = 700)

                            return result

                        latexTxt = tff.Wr.TexFileUtils.fromEntryToLatexTxt(k, v)
                        pilIm = getEntryImg(latexTxt, subsection, k)

                        shrink = 0.7
                        pilIm.thumbnail([int(pilIm.size[0] * shrink),int(pilIm.size[1] * shrink)], Image.LANCZOS)
                        img = ImageTk.PhotoImage(pilIm)

                        if (subsection == self.entryAsETR.subsection)\
                            and (k == self.entryAsETR.imIdx) :
                            textLabelPage = _uuicom.MultilineText_ETR(tempFrameRow1, 
                                                                      "contentP_" + nameId, 
                                                                      0,
                                                                      0, 
                                                                      i, 
                                                                      v)
                            textLabelPage.imIdx = k
                            textLabelPage.subsection = subsection
                            textLabelPage.etrWidget = textLabelPage
                            textLabelPage.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                                                 [updateEntry])
                            self.entryAsETR.widget = textLabelPage
                            textLabelPage.focus_force()
                        else:
                            textLabelPage = _uuicom.TOCLabelWithClick(tempFrameRow1,
                                                            image = img, 
                                                            prefix = "contentP_" + nameId, 
                                                            padding= [60, 0, 0, 0],
                                                            row = 0, 
                                                            column = 0)
                            textLabelPage.imIdx = k
                            textLabelPage.subsection = subsection
                            textLabelPage.etrWidget = textLabelPage
                            textLabelPage.rebind([ww.currUIImpl.Data.BindID.mouse2],
                                                 [updateEntry])
                            textLabelPage.image = img

                            if (self.entryAsETR.upddatedTextSubsection == subsection) and\
                               (self.entryAsETR.upddatedTextImIdx == k):
                                self.entryAsETR.upddatedTextSubsection = None
                                self.entryAsETR.upddatedTextImIdx = None
                                self.updatedWidget = textLabelPage

                        textLabelFull = _uuicom.TOCLabelWithClick(tempFrameRow1, 
                                                       text = self.__EntryUIs.im.name, 
                                                       prefix = "contentFull_" + nameId,
                                                       row = 0, 
                                                       column = self.__EntryUIs.im.column)
                        textLabelFull.subsection = subsection
                        textLabelFull.imIdx = k

                        chkbtnShowPermamently = EntryShowPermamentlyCheckbox(tempFrameRow2, 
                                                                             subsection, k, 
                                                                             "contentShowAlways_" + nameId,
                                                                             self)
                        showImages = _uuicom.TOCLabelWithClick(tempFrameRow1, 
                                                    text = self.__EntryUIs.full.name,
                                                    prefix = "contentOfImages_" + nameId,
                                                    row = 0,
                                                    column = self.__EntryUIs.full.column)
                        showImages.imIdx = k
                        showImages.subsection = subsection
                        showImages.clicked = False
                        self.showImagesLabels[subsection + k] = showImages

                        imShouldBeBrown = False

                        if (subsection == self.subsectionClicked) and (str(k) == self.entryClicked):
                            imShouldBeBrown = True 

                        if not textOnly:
                            showImages.rebind([ww.currUIImpl.Data.BindID.mouse1, ww.currUIImpl.Data.BindID.customTOCMove],
                                            [lambda e, *args: __showIMagesONClick(e, showImages, subSecID, True, *args),
                                            lambda e, *args: __showIMagesONClick(e, showImages, subSecID, False, *args)])
                        else:
                            showImages.rebind([ww.currUIImpl.Data.BindID.mouse1, ww.currUIImpl.Data.BindID.customTOCMove],
                                            [lambda e, *args: __showIMagesONClick(e, showImages, subSecID, 
                                                                                  True, textOnly = True, *args),
                                            lambda e, *args: __showIMagesONClick(e, showImages, subSecID, 
                                                                                 False, textOnly = True,*args)])

                        removeEntry = _uuicom.TOCLabelWithClick(tempFrameRow2,
                                                     text = self.__EntryUIs.delete.name,
                                                     prefix = "contentRemoveEntry" + nameId,
                                                     row = 0, 
                                                     column = self.__EntryUIs.delete.column)
                        removeEntry.imIdx = k
                        removeEntry.subsection = subsection
                        removeEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                           [removeEntryCmd])

                        shiftEntry = _uuicom.TOCLabelWithClick(tempFrameRow2,
                                                               text = self.__EntryUIs.shift.name,
                                                               prefix = "contentShiftEntry" + nameId,
                                                               row = 0, 
                                                               column = self.__EntryUIs.shift.column)
                        shiftEntry.imIdx = k
                        shiftEntry.subsection = subsection
                        shiftEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                          [shiftEntryCmd])

                        copyEntry = _uuicom.TOCLabelWithClick(tempFrameRow1,
                                                               text = self.__EntryUIs.copy.name,
                                                               prefix = "contentCopyEntry" + nameId,
                                                               row = 0, 
                                                               column = self.__EntryUIs.copy.column)
                        copyEntry.imIdx = k
                        copyEntry.subsection = subsection
                        copyEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                         [copyEntryCmd])
                        copyEntry.rebind([ww.currUIImpl.Data.BindID.shmouse1],
                                         [cutEntryCmd])

                        pasteAfterEntry = _uuicom.TOCLabelWithClick(tempFrameRow1,
                                                               text = self.__EntryUIs.pasteAfter.name,
                                                               prefix = "contentPasteAfterEntry" + nameId,
                                                               row = 0, 
                                                               column = self.__EntryUIs.pasteAfter.column)
                        pasteAfterEntry.imIdx = k
                        pasteAfterEntry.subsection = subsection
                        pasteAfterEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                               [pasteEntryCmd])

                        showLinksForEntry = _uuicom.TOCLabelWithClick(tempFrameRow2,
                                                               text = self.__EntryUIs.showLinks.name,
                                                               prefix = "contentShowLinksForEntry" + nameId,
                                                               row = 0, 
                                                               column = self.__EntryUIs.showLinks.column)
                        showLinksForEntry.imIdx = k
                        showLinksForEntry.subsection = subsection
                        showLinksForEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                                 [showLinksForEntryCmd])

                        linkExist = k in list(fsm.Data.Sec.imGlobalLinksDict(subsection).keys())

                        if linkExist:
                            showLinksForEntry.configure(foreground="brown")                 

                        retakeImageForEntry = _uuicom.TOCLabelWithClick(tempFrameRow2,
                                                               text =  self.__EntryUIs.retake.name,
                                                               prefix = "contentRetakeImageForEntry" + nameId,
                                                               row = 0, 
                                                               column =  self.__EntryUIs.retake.column)
                        retakeImageForEntry.imIdx = k
                        retakeImageForEntry.subsection = subsection
                        retakeImageForEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                                 [retakeImageCmd])

                        addLinkEntry = _uuicom.TOCLabelWithClick(tempFrameRow2, 
                                                         text = self.__EntryUIs.link.name,
                                                         prefix = "contentAddGlLinkEntry" + nameId,
                                                         row = 0, 
                                                         column = self.__EntryUIs.link.column)
                        addLinkEntry.imIdx = k
                        addLinkEntry.subsection = subsection
                        addLinkEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                            [addGlLinkCmd])

                        addExtraImage = _uuicom.TOCLabelWithClick(tempFrameRow2, 
                                                         text = self.__EntryUIs.addExtra.name,
                                                         prefix = "contentAddExtraImageEntry" + nameId,
                                                         row = 0, 
                                                         column = self.__EntryUIs.addExtra.column)
                        addExtraImage.imIdx = k
                        addExtraImage.subsection = subsection
                        addExtraImage.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                            [addExtraImCmd])

                        copyLinkEntry = _uuicom.TOCLabelWithClick(tempFrameRow1, 
                                                         text = self.__EntryUIs.copyLink.name,
                                                         prefix = "contentCopyGlLinkEntry" + nameId,
                                                         row = 0, 
                                                         column = self.__EntryUIs.copyLink.column)
                        copyLinkEntry.imIdx = k
                        copyLinkEntry.subsection = subsection
                        copyLinkEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                            [copyGlLinkCmd])

                        pasteLinkEntry = _uuicom.TOCLabelWithClick(tempFrameRow1,
                                                         text = self.__EntryUIs.pasteLink.name,
                                                         prefix = "contentPasteGlLinkEntry" + nameId,
                                                         row = 0, 
                                                         column = self.__EntryUIs.pasteLink.column)
                        pasteLinkEntry.imIdx = k
                        pasteLinkEntry.subsection = subsection
                        pasteLinkEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                            [pasteGlLinkCmd])

                        openExUIEntry = _uuicom.TOCLabelWithClick(tempFrameRow1, 
                                                      text = self.__EntryUIs.excercises.name, 
                                                      prefix = "contentOpenExcerciseUIEntry" + nameId,
                                                      row = 0, 
                                                      column = self.__EntryUIs.excercises.column,
                                                      columnspan = 1000)
                        openExUIEntry.imIdx = k
                        openExUIEntry.subsection = subsection
                        openExUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                             [openExcerciseMenu])

                        fullPathToEntryJSON = _upan.Paths.Entry.JSON.getAbs(sf.Wr.Manager.Book.getCurrBookFolderPath(),
                                                                            subsection,
                                                                            k)
                        excerciseExists = ocf.Wr.FsAppCalls.checkIfFileOrDirExists(fullPathToEntryJSON)

                        if excerciseExists:
                            openExUIEntry.configure(foreground="brown")

                        proofExists = False
                        exImDict = fsm.Data.Sec.extraImagesDict(subsection)

                        if k in list(exImDict.keys()):
                            exImNames = exImDict[k]
                            proofExists = len([i for i in exImNames if "proof" in i.lower()]) != 0

                        openProofsUIEntry = _uuicom.TOCLabelWithClick(tempFrameRow2, 
                                                      text = self.__EntryUIs.proof.name, 
                                                      prefix = "contentOpenExcerciseUIEntry" + nameId,
                                                      row = 0, 
                                                      column = self.__EntryUIs.proof.column)
                        if proofExists:
                            openProofsUIEntry.configure(foreground="brown")

                        openProofsUIEntry.imIdx = k
                        openProofsUIEntry.subsection = subsection
                        openProofsUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                             [openProofsMenu])

                        changeImText = _uuicom.TOCLabelWithClick(tempFrameRow2, 
                                                      text = self.__EntryUIs.update.name, 
                                                      prefix = "contentUpdateEntryText" + nameId,
                                                      row = 0, 
                                                      column = self.__EntryUIs.update.column)
                        changeImText.imIdx = k
                        changeImText.subsection = subsection
                        changeImText.etrWidget = textLabelPage
                        changeImText.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                             [updateEntry])

                        uiResizeEntryIdx = fsm.Data.Sec.imageUIResize(subsection)

                        if k in list(uiResizeEntryIdx.keys()):
                            resizeFactor = float(uiResizeEntryIdx[k])
                        else:
                            resizeFactor = 1.0

                        changeImSize = _uuicom.ImageSize_ETR(tempFrameRow2,
                                                      prefix = "contentUpdateEntryText" + nameId,
                                                      row = 0, 
                                                      column = self.__EntryUIs.changeImSize.column,
                                                      imIdx = k,
                                                      text = resizeFactor)
                        changeImSize.imIdx = k
                        changeImSize.widgetObj.imIdx = k
                        changeImSize.subsection = subsection
                        changeImSize.widgetObj.subsection = subsection
                        changeImSize.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                             [resizeEntryImgCMD])

                        showLinks = False

                        for l in self.showLinksForSubsections:
                            if subsection + "_" + k in l:
                                showLinks = True
                                break

                        if self.showLinks or showLinks:
                            # adding a frame to show global links
                            linksFrame = _uuicom.TOCFrame(tempFrame,
                                                prefix = "contentLinksFr_" + nameId,
                                                row = gridRowStartIdx + 1, column = 0, columnspan = 100)
                            linksFrame.subsection = subsection
                            linksFrame.imIdx = k

                            if showLinks:
                                self.linkFrames.append(linksFrame)

                            imGlobalLinksDict = fsm.Data.Sec.imGlobalLinksDict(subsection)

                            if k in imGlobalLinksDict.keys():
                                glLinks:dict = fsm.Data.Sec.imGlobalLinksDict(subsection)[k]

                                glLinkLablel = _uuicom.TOCLabelWithClick(linksFrame, 
                                                        text = "Links: ", 
                                                        prefix = "contentLinksIntroFr_" + nameId,
                                                        padding = [60, 0, 0, 0],
                                                        row = 0, column = 0)
                                glLinkLablel.render()
                                glLinkId = 0

                                # NOTE: should put all the links into 
                                # one frame. This way they will be aligned correctly
                                if type(glLinks) == dict:
                                    for ln, lk in glLinks.items():
                                        if "KIK" in lk:
                                            # NOTE: probably should be a frame here
                                            glLinkImLablel = _uuicom.TOCLabelWithClick(
                                                                    linksFrame, 
                                                                    prefix = "contentLinksImLabelIntroFr_" + nameId + "_" + str(glLinkId),
                                                                    padding = [60, 0, 0, 0],
                                                                    row = glLinkId + 1, column = 0)
                                            glLinkImLablel.render()
            
                                            targetSubsection = ln.split("_")[0]
                                            targetImIdx = ln.split("_")[1]
                                            textOnlyLink = fsm.Data.Sec.textOnly(targetSubsection)[targetImIdx]

                                            glLinkSubsectioLbl = _uuicom.TOCLabelWithClick(
                                                                    glLinkImLablel, 
                                                                    prefix = "contentGlLinksTSubsection_" + nameId + "_" + str(glLinkId),
                                                                    text = targetSubsection + ": ", 
                                                                    padding = [90, 0, 0, 0],
                                                                    row = 0, column = 0)
                                            glLinkSubsectioLbl.render()

                                            imLinkDict = fsm.Data.Sec.imLinkDict(targetSubsection)

                                            latexTxt = tff.Wr.TexFileUtils.fromEntryToLatexTxt(ln, imLinkDict[targetImIdx])
                                            pilIm = getEntryImg(latexTxt, targetSubsection, targetImIdx)

                                            shrink = 0.7
                                            pilIm.thumbnail([int(pilIm.size[0] * shrink),int(pilIm.size[1] * shrink)], Image.LANCZOS)
                                            img = ImageTk.PhotoImage(pilIm)

                                            glLinkLablel = _uuicom.TOCLabelWithClick(glLinkImLablel,
                                                                        image = img,
                                                                        text = ln + ": " + imLinkDict[targetImIdx], 
                                                                        prefix = "contentGlLinks_" + nameId + "_" + str(glLinkId),
                                                                        row = 0, column = 1
                                                                        )
                                            glLinkLablel.subsection = targetSubsection
                                            glLinkLablel.imIdx = targetImIdx
                                            glLinkLablel.image = img

                                            glLinkLablel.render()
                                            openOMOnThePageOfTheImage(glLinkLablel, targetSubsection, targetImIdx)

                                            linkLabelFull = _uuicom.TOCLabelWithClick(glLinkImLablel, 
                                                                        text = "[f]", 
                                                                        prefix = "contentGlLinksTSubsectionFull_" + nameId + "_" + str(glLinkId),
                                                                        row = 0, column= 2)
                                            linkLabelFull.render()

                                            linkLabelFull.subsection = ln.split("_")[0]
                                            linkLabelFull.imIdx = ln.split("_")[-1]

                                            _uuicom.bindChangeColorOnInAndOut(linkLabelFull)

                                            def __moveLinkFull(e, *args):
                                                widget = e.widget
                                                self.scrollToEntry(widget.subsection,
                                                                widget.imIdx)

                                            linkLabelFull.rebind([ww.currUIImpl.Data.BindID.mouse1], [__moveLinkFull])

                                            glLinksShowImages = _uuicom.TOCLabelWithClick(glLinkImLablel, 
                                                                            text = "[i]", 
                                                                            prefix = "contentGlLinksOfImages_" + nameId+ "_" + str(glLinkId),
                                                                            row = 0, column = 3)
                                            glLinksShowImages.imIdx = ln.split("_")[-1]
                                            glLinksShowImages.subsection = ln.split("_")[0]
                                            glLinksShowImages.clicked = False
                                            glLinksShowImages.render()
                                            glLinkSubSecID = _upan.Names.UI.getWidgetSubsecId(ln.split("_")[0])

                                            _uuicom.bindChangeColorOnInAndOut(glLinksShowImages)

                                            if not textOnlyLink:
                                                glLinksShowImages.rebind([ww.currUIImpl.Data.BindID.mouse1], 
                                                                        [lambda e, *args: __showIMagesONClick(e, 
                                                                                                            glLinksShowImages,
                                                                                                            glLinkSubSecID, 
                                                                                                            False, 
                                                                                                            150,
                                                                                                            True, 
                                                                                                            *args)])
                                            else:
                                                glLinksShowImages.rebind([ww.currUIImpl.Data.BindID.mouse1], 
                                                                        [lambda e, *args: __showIMagesONClick(e, 
                                                                                                            glLinksShowImages,
                                                                                                            glLinkSubSecID, 
                                                                                                            False, 
                                                                                                            150, 
                                                                                                            True, 
                                                                                                            textOnly = True,
                                                                                                            *args)])

                                            linkLabelDelete = _uuicom.TOCLabelWithClick(glLinkImLablel, 
                                                                        text = "[d]", 
                                                                        prefix = "contentGlLinksTSubsectionDel_" + nameId + "_" + str(glLinkId),
                                                                        row = 0, column = 4)
                                            linkLabelDelete.render()
                                            
                                            linkLabelDelete.targetSubssection = ln.split("_")[0]
                                            linkLabelDelete.sourceSubssection = subsection
                                            linkLabelDelete.targetImIdx = ln.split("_")[-1]
                                            linkLabelDelete.sourceImIdx = k

                                            linkLabelDelete.rebind([ww.currUIImpl.Data.BindID.mouse1], [delGlLinkCmd])

                                            _uuicom.bindChangeColorOnInAndOut(linkLabelDelete)

                                            tarProofExists = False
                                            tarExImDict = fsm.Data.Sec.extraImagesDict(ln.split("_")[0])

                                            if ln.split("_")[-1] in list(tarExImDict.keys()):
                                                tarExImNames = tarExImDict[ln.split("_")[-1]]
                                                tarProofExists = len([i for i in tarExImNames if "proof" in i.lower()]) != 0
                                            
                                            if tarProofExists:
                                                tarOpenProofsUIEntry = _uuicom.TOCLabelWithClick(glLinkImLablel, 
                                                        text = self.__EntryUIs.proof.name, 
                                                        prefix = "contentGlLinksTSubsectionProof_" + nameId + "_" + str(glLinkId),
                                                        row = 0, 
                                                        column = 5)
                                                tarOpenProofsUIEntry.configure(foreground="brown")

                                                tarOpenProofsUIEntry.imIdx = ln.split("_")[1]
                                                tarOpenProofsUIEntry.subsection = ln.split("_")[0]
                                                tarOpenProofsUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                                                    [openProofsMenu])
                                                _uuicom.bindChangeColorOnInAndOut(tarOpenProofsUIEntry, shouldBeBrown = True)

                                                tarOpenProofsUIEntry.render()

                                        elif "http" in lk:
                                            # NOTE: should be a frame here!
                                            glLinkImLablel = _uuicom.TOCLabelWithClick(
                                                                    linksFrame, 
                                                                    prefix = "contentWebLinksImLabelIntroFr_" + nameId + "_" + str(glLinkId),
                                                                    padding = [60, 0, 0, 0],
                                                                    row = glLinkId + 1, column = 0)
                                            glLinkImLablel.render()

                                            glLinkSubsectioLbl = _uuicom.TOCLabelWithClick(glLinkImLablel, 
                                                                    text = "web: ", 
                                                                    padding = [90, 0, 0, 0],
                                                                    prefix = "contentGlLinksTSubsection_" + nameId + "_" + str(glLinkId),
                                                                    row = glLinkId + 1, column = 0)
                                            glLinkSubsectioLbl.render()

                                            latexTxt = tff.Wr.TexFileUtils.formatEntrytext(ln)
                                            currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                                            linkFilepath = _upan.Paths.Screenshot.Images.getWebLinkImageAbs(currBookPath,
                                                                                            subsection,
                                                                                            k,
                                                                                            ln)

                                            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(linkFilepath):
                                                pilIm = Image.open(linkFilepath)
                                            else:
                                                pilIm = tff.Wr.TexFileUtils.fromTexToImage(latexTxt, linkFilepath) 

                                            shrink = 0.7
                                            pilIm.thumbnail([int(pilIm.size[0] * shrink),int(pilIm.size[1] * shrink)], Image.LANCZOS)
                                            img = ImageTk.PhotoImage(pilIm)

                                            glLinkLablel = _uuicom.TOCLabelWithClick(glLinkImLablel,
                                                                        image = img,
                                                                        text = ln, 
                                                                        prefix = "contentGlLinks_" + nameId + "_" + str(glLinkId),
                                                                        row = glLinkId + 1, column = 1)
                                            glLinkLablel.subsection = subsection
                                            glLinkLablel.imIdx = k
                                            glLinkLablel.image = img

                                            glLinkLablel.render()
                                            openWebOfTheImage(glLinkLablel, lk)

                                            linkLabelDelete = _uuicom.TOCLabelWithClick(glLinkImLablel, 
                                                                        text = "[d]", 
                                                                        prefix = "contentGlLinksTSubsectionDel_" + nameId + "_" + str(glLinkId),
                                                                        row = glLinkId + 1, column = 2)
                                            linkLabelDelete.render()

                                            linkLabelDelete.sourceSubssection = subsection
                                            linkLabelDelete.sourceImIdx = k
                                            linkLabelDelete.sourceWebLinkName = ln

                                            linkLabelDelete.rebind([ww.currUIImpl.Data.BindID.mouse1], [delWebLinkCmd])

                                            _uuicom.bindChangeColorOnInAndOut(linkLabelDelete)

                                        glLinkId += 1

                        tocWImageDict = fsm.Data.Sec.tocWImageDict(subsection)

                        if tocWImageDict == _u.Token.NotDef.dict_t:
                            alwaysShow = False
                        else:
                            alwaysShow = tocWImageDict[k] == "1"

                        showImages.alwaysShow = alwaysShow

                        if ((((subsection == self.subsectionClicked) and (str(k) == self.entryClicked)) or alwaysShow) or\
                            ((subsection == self.secondEntrySubsectionClicked) and (str(k) == self.secondEntryClickedImIdx))):
                            showImages.clicked = False

                            if (not (subsection == self.subsectionClicked and str(k) == self.entryClicked)):
                                showImages.generateEvent(ww.currUIImpl.Data.BindID.customTOCMove)
                            else:
                                self.widgetToScrollTo = showImages

                        if imagesGroupsWShouldShow[currImGroupName] or self.showAll:
                            tempFrameRow1.render()
                            textLabelPage.render()

                            if not showImages.alwaysShow:
                                textLabelFull.render()

                            showImages.render()

                            if not self.showAll:

                                if not textOnly:
                                    chkbtnShowPermamently.grid(row = 0, 
                                                            column = self.__EntryUIs.alwaysShow.column, sticky=tk.NW)

                                imagesGroup.grid(row = 0, column = self.__EntryUIs.group.column, 
                                                 sticky=tk.NW)
                                removeEntry.render()

                            addLinkEntry.render()
                            addExtraImage.render()
                            copyLinkEntry.render()
                            pasteLinkEntry.render()

                            if not textOnly:
                                retakeImageForEntry.render()

                            showLinks = False

                            for l in self.showLinksForSubsections:
                                if subsection + "_" + k in l:
                                    showLinks = True
                                    break

                            if self.showLinks or showLinks:
                                linksFrame.render()

                            openExUIEntry.render()
                            openProofsUIEntry.render()
                            showLinksForEntry.render()
                            shiftEntry.render()
                            copyEntry.render()
                            pasteAfterEntry.render()
                            changeImText.render()

                            if not textOnly:
                                changeImSize.render()

                        if self.entryAsETR.widget == None:
                            openOMOnThePageOfTheImage(textLabelPage, subsection, k)

                        if imShouldBeBrown:
                            showImages.configure(foreground="brown")  
                        _uuicom.bindChangeColorOnInAndOut(showImages, shouldBeBrown = imShouldBeBrown)
                        _uuicom.bindChangeColorOnInAndOut(removeEntry)
                        _uuicom.bindChangeColorOnInAndOut(shiftEntry)
                        _uuicom.bindChangeColorOnInAndOut(copyEntry)
                        _uuicom.bindChangeColorOnInAndOut(pasteAfterEntry)
                        _uuicom.bindChangeColorOnInAndOut(retakeImageForEntry)
                        _uuicom.bindChangeColorOnInAndOut(showLinksForEntry, shouldBeBrown = linkExist)
                        _uuicom.bindChangeColorOnInAndOut(addLinkEntry)
                        _uuicom.bindChangeColorOnInAndOut(addExtraImage)
                        _uuicom.bindChangeColorOnInAndOut(copyLinkEntry)
                        _uuicom.bindChangeColorOnInAndOut(pasteLinkEntry)
                        openSecondaryImage(textLabelFull)
                        _uuicom.bindChangeColorOnInAndOut(textLabelFull)
                        _uuicom.bindChangeColorOnInAndOut(openExUIEntry, shouldBeBrown = excerciseExists)
                        _uuicom.bindChangeColorOnInAndOut(openProofsUIEntry, shouldBeBrown = proofExists)
                        _uuicom.bindChangeColorOnInAndOut(changeImText)

                        tempFrame.render()
                        prevImGroupName = currImGroupName
                        i += 1

                    dummyFrame = _uuicom.TOCFrame(frame, prefix = "contentDummyFr_" + subSecID,
                                        row = i + 1, column = 0)
                    dummyEntryPage = _uuicom.TOCLabelWithClick(dummyFrame, 
                                                    text ="\n", 
                                                    prefix = "contentDummy_" + subSecID,
                                                    row=0, column=0)
                    dummyEntryPage.render()
                    dummyFrame.render()

                    if int(event.type) == 4:
                        label.clicked = True

                        if not label.alwaysShow:
                            self.subsectionClicked = subsection
                    
                    if not(self.showAll):
                        fsm.Data.Book.subsectionOpenInTOC_UI = subsection
                        fsm.Data.Book.currSection = subsection
                        fsm.Data.Book.currTopSection = subsection.split(".")[0]
                        fsm.Data.Book.entryImOpenInTOC_UI = "-1"
      
                        self.notify(mui.ChooseTopSection_OM)
                        self.notify(mui.ChooseSubsection_OM)
                        self.notify(mcomui.SourceImageLinks_OM)
                        self.notify(mui.ScreenshotLocation_LBL)

                    self.scrollIntoView(event)
                else:
                    for child in frame.getChildren():
                        if "content" in str(child):
                            child.destroy()
                    
                    if int(event.type) == 4:
                        if not self.showAll:
                            closeAllSubsections()

                        label.clicked = False

                        if not label.alwaysShow:
                            self.subsectionClicked = _u.Token.NotDef.str_t

                    self.scrollIntoView(event)

                event.widget.configure(foreground="white")
            
            label.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])

            if ((self.subsectionClicked == subsection) and (level != 0)) or self.showAll:
                label.generateEvent(ww.currUIImpl.Data.BindID.mouse1)

        def openContentOfTheTopSection(frame:_uuicom.TOCFrame, label:_uuicom.TOCLabelWithClick):
            def __cmd(event = None, *args):
                
                # 4 : event of mouse click
                # 19 : event of being rendered
                if ((not label.clicked) and (int(event.type) == 4)) or\
                    ((self.showSubsectionsForTopSection[subsection] == True) and (int(event.type) == 19)) or\
                    self.showAll:
                    fsm.Data.Book.currTopSection = subsection
                    label.clicked = True
                    self.showSubsectionsForTopSection[subsection] = True
                    self.__renderWithScrollAfter()
                else:
                    if int(event.type) == 4:
                        self.subsectionClicked = _u.Token.NotDef.str_t
                        self.entryClicked = _u.Token.NotDef.str_t
                        self.showSubsectionsForTopSection[subsection] = False
                        self.displayedImages = []
                        self.openedMainImg = None

                        self.showSubsectionsForTopSection[subsection] = False
                        self.__renderWithScrollAfter()

                event.widget.configure(foreground="white")
            
            label.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])

        if level != 0:
            topSection = subsection.split(".")[0]
            if not self.showSubsectionsForTopSection[topSection]:
                return

        topSection = subsection.split(".")[0]

        if level == 0:
            prettySubsections = _upan.Names.Subsection.getTopSectionPretty(topSection)
        else:
            prettySubsections = _upan.Names.Subsection.getSubsectionPretty(subsection)
        
        labelName = "label_" + subsection.replace(".", "")

        locFrame = _uuicom.TOCFrame(self.scrollable_frame, 
                            prefix = labelName,
                            row = row, column = 0)
        super().addTOCEntry(locFrame, row, 0)

        nameId = "subsecLabel_" + subsection 
        nameId = nameId.replace(".", "")


        def updateSubsection(event, *args):
            widget = event.widget
            subsection = widget.subsection

            if (self.subsectionAsETR.subsection != _u.Token.NotDef.str_t):
                newText = self.subsectionAsETR.widget.getData()

                if subsection in list(fsm.Data.Book.sections.keys()):
                    sections = fsm.Data.Book.sections
                    sections[subsection]["name"] = newText
                    fsm.Data.Book.sections = sections
                    fsm.Wr.SectionInfoStructure.rebuildTopSectionLatex(self.subsectionAsETR.subsection,
                                                                    _upan.Names.Subsection.getTopSectionPretty)
                else:
                    fsm.Data.Sec.text(self.subsectionAsETR.subsection, newText)
                    fsm.Wr.SectionInfoStructure.rebuildSubsectionImOnlyLatex(self.subsectionAsETR.subsection,
                                                                    _upan.Names.Subsection.getSubsectionPretty)
                self.subsectionAsETR.reset()
                self.__renderWithoutScroll()
            else:
                self.subsectionAsETR.subsection = event.widget.subsection
                self.subsectionAsETR.widget =event.widget.etrWidget
                self.__renderWithoutScroll()

        currSubsectionHidden = False
        hiddenSubsections = fsm.Data.Book.subsectionsHiddenInTOC_UI
        if not self.showAll:
            for hiddensSubsection in hiddenSubsections:
                if (hiddensSubsection in subsection) and (subsection != hiddensSubsection):
                    currSubsectionHidden = True

        if level == 0:
            if subsection != self.subsectionAsETR.subsection:
                topSectionImgPath = _upan.Paths.Screenshot.Images.getTopSectionEntryImageAbs(
                                                            sf.Wr.Manager.Book.getCurrBookName(),
                                                            subsection)

                if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(topSectionImgPath):
                    result = Image.open(topSectionImgPath)
                else:
                    result = fsm.Wr.SectionInfoStructure.rebuildTopSectionLatex(subsection,
                                                                                _upan.Names.Subsection.getTopSectionPretty)

                shrink = 0.8
                result.thumbnail([int(result.size[0] * shrink),int(result.size[1] * shrink)], Image.LANCZOS)
                result = ImageTk.PhotoImage(result)

                subsectionLabel = _uuicom.TOCLabelWithClick(locFrame, image = result, 
                                                prefix = nameId, padding = [0, 20, 0, 0],
                                                row = 0, column= 0)
                subsectionLabel.image = result
                subsectionLabel.subsection = subsection
                subsectionLabel.rebind([ww.currUIImpl.Data.BindID.mouse2],
                                        [updateSubsection])
                openPdfOnStartOfTheSection(subsectionLabel)
                subsectionLabel.render()
            else:
                topSectionName = fsm.Data.Book.sections[subsection]["name"]
                subsectionLabel = _uuicom.MultilineText_ETR(locFrame, 
                                                            nameId, 
                                                            0, 0, 
                                                            "", # NOTE: not used anywhere  
                                                            topSectionName)
                subsectionLabel.subsection = subsection
                subsectionLabel.etrWidget = subsectionLabel
                subsectionLabel.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                                        [updateSubsection])
                self.subsectionAsETR.widget = subsectionLabel
                subsectionLabel.focus_force()
                subsectionLabel.render()
        else:
            if not currSubsectionHidden:
                if subsection != self.subsectionAsETR.subsection:
                    subsectionImgPath = _upan.Paths.Screenshot.Images.getSubsectionEntryImageAbs(
                                                            sf.Wr.Manager.Book.getCurrBookName(), 
                                                            subsection)

                    if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(subsectionImgPath):
                        result = Image.open(subsectionImgPath)
                    else:
                        result = \
                            fsm.Wr.SectionInfoStructure.rebuildSubsectionImOnlyLatex(subsection, 
                                                                                 _upan.Names.Subsection.getSubsectionPretty)

                    shrink = 0.8
                    result.thumbnail([int(result.size[0] * shrink),int(result.size[1] * shrink)], Image.LANCZOS)
                    result = ImageTk.PhotoImage(result)

                    subsectionLabel = _uuicom.TOCLabelWithClick(locFrame, image = result, prefix = nameId,
                                                        row = 0, column= 0)
                    subsectionLabel.image = result
                    subsectionLabel.subsection = subsection
                    subsectionLabel.rebind([ww.currUIImpl.Data.BindID.mouse2],
                                            [updateSubsection])
                    openPdfOnStartOfTheSection(subsectionLabel)
                else:
                    subsectionLabel = _uuicom.MultilineText_ETR(locFrame, 
                                                                "contentP_" + nameId, 
                                                                0, 0, 
                                                                "", # NOTE: not used anywhere  
                                                                fsm.Data.Sec.text(subsection))
                    subsectionLabel.subsection = subsection
                    subsectionLabel.etrWidget = subsectionLabel
                    subsectionLabel.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                                            [updateSubsection])
                    self.subsectionAsETR.widget = subsectionLabel
                    subsectionLabel.focus_force()

                subsectionLabel.render()

        if level != 0:
            if (not currSubsectionHidden):
                openContentLabel = _uuicom.TOCLabelWithClick(locFrame, text = "[content]", 
                                                    prefix = "subsecContent" + subsection.replace(".", ""),
                                                    row = 0, column= 1)

                openContentLabel.subsection = subsection

                if subsection == fsm.Data.Book.currSection:
                    self.currSubsectionWidget = openContentLabel

                openContentOfTheSection(locFrame, openContentLabel)
                _uuicom.bindChangeColorOnInAndOut(openContentLabel)

                self.subsectionContentLabels.append(openContentLabel)

                if self.showAll or (subsection == fsm.Data.Book.currSection):
                    openContentLabel.clicked = False

                rebuildLatex = _uuicom.TOCLabelWithClick(locFrame, text = "[rebuild latex]",
                                                prefix = "subsecRebuild" + subsection.replace(".", ""),
                                                row = 0, column = 4)
                rebuildLatex.subsection = subsection

                _uuicom.bindChangeColorOnInAndOut(rebuildLatex)

                def rebuildSubsectionLatexWrapper(subsection):
                    fsm.Wr.SectionInfoStructure.rebuildSubsectionLatex(subsection,
                                                                    _upan.Names.Group.formatGroupText,
                                                                    _upan.Names.Subsection.getSubsectionPretty,
                                                                    _upan.Names.Subsection.getTopSectionPretty)
                    self.__renderWithScrollAfter()

                rebuildLatex.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                    [lambda e, *args: rebuildSubsectionLatexWrapper(e.widget.subsection)])

                def __updateStartPage(e, subsection, *args):
                    newStartPage = e.widget.get()
                    fsm.Data.Sec.start(subsection, newStartPage)
                    omName = fsm.Data.Book.currOrigMatName
                    omFilepath = fsm.Wr.OriginalMaterialStructure.getMaterialPath(omName)

                    ocf.Wr.PdfApp.openPDF(omFilepath, newStartPage)

                startPage = fsm.Data.Sec.start(subsection)
                changeStartPage = _uuicom.ImageSize_ETR(locFrame,
                                                        prefix = "updateStartPageEntryText" + subsection.replace(".", ""),
                                                        row = 0, 
                                                        column = 3,
                                                        imIdx = -1,
                                                        text = startPage)
                changeStartPage.subsection = subsection
                changeStartPage.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                        [lambda e, *args:__updateStartPage(e, changeStartPage.subsection, *args)])

                def __updateSubsectionPath(e, subsection, *args):
                    targetSubsection = e.widget.get()
                    sourceSubsection = subsection

                    # ask the user if we wnat to proceed.
                    msg = "Do you want to move \n\n subsection\n'{0}' \n\nto \n'{1}'?".format(sourceSubsection, targetSubsection)
                    response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

                    mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                wf.Wr.MenuManagers.MathMenuManager)
                    mainManager.show()

                    if not response:
                        return

                    gm.GeneralManger.moveSubsection(sourceSubsection,
                                                    targetSubsection)
                    self.__renderWithScrollAfter()

                updateSubsectionPath = _uuicom.ImageSize_ETR(locFrame,
                                                        prefix = "updateSubsectionPosEntryText" + subsection.replace(".", ""),
                                                        row = 0, 
                                                        column = 5,
                                                        imIdx = -1,
                                                        text = subsection,
                                                        width = 20)
                updateSubsectionPath.subsection = subsection
                updateSubsectionPath.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                        [lambda e, *args:__updateSubsectionPath(e, updateSubsectionPath.subsection, *args)])

                def __removeSubsection(e, subsection, *args):
                    sourceSubsection = subsection

                    # ask the user if we wnat to proceed.
                    msg = "Do you want to \n\nREMOVE \n\n subsection:\n'{0}'?".format(sourceSubsection)
                    response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

                    mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                wf.Wr.MenuManagers.MathMenuManager)
                    mainManager.show()

                    if not response:
                        return

                    gm.GeneralManger.deleteSubsection(sourceSubsection)
                    self.__renderWithScrollAfter()

                removeSubsection = _uuicom.TOCLabelWithClick(locFrame,
                                                        prefix = "removeSubsectionPosEntryText" + subsection.replace(".", ""),
                                                        row = 0, 
                                                        column = 6,
                                                        text = "[delete]",
                                                        width = 20)
                removeSubsection.subsection = subsection
                removeSubsection.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                        [lambda e, *args:__removeSubsection(e, removeSubsection.subsection, *args)])

                hideSubsections = _uuicom.TOCLabelWithClick(locFrame, text = "[show/hide]",
                                                prefix = "subsecShowHide" + subsection.replace(".", ""),
                                                row = 0, column = 2)
                subsectionsList = fsm.Wr.BookInfoStructure.getSubsectionsList(subsection)
                if subsectionsList != []:
                    hideSubsections.configure(foreground="brown")

                hideSubsections.subsection = subsection

                _uuicom.bindChangeColorOnInAndOut(removeSubsection)

                if subsectionsList != []:
                    _uuicom.bindChangeColorOnInAndOut(hideSubsections, shouldBeBrown = True)
                else:
                    _uuicom.bindChangeColorOnInAndOut(hideSubsections)

                def showHideSubsectionsWrapper(subsection):
                    subsectionsHidden:list = fsm.Data.Book.subsectionsHiddenInTOC_UI

                    if subsection in subsectionsHidden:
                        subsectionsHidden.remove(subsection)
                    else:
                        subsectionsHidden.append(subsection)
                    
                    fsm.Data.Book.subsectionsHiddenInTOC_UI =  subsectionsHidden
                    self.__renderWithScrollAfter()

                hideSubsections.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                       [lambda e, *args: showHideSubsectionsWrapper(e.widget.subsection)])

                openContentLabel.render()
                rebuildLatex.render()
                changeStartPage.render()

                if not self.showAll:
                    hideSubsections.render()
                    updateSubsectionPath.render()
                    removeSubsection.render()
        else:
            openContentLabel = _uuicom.TOCLabelWithClick(locFrame, 
                                                 prefix = "openContentLabel" + subsection.replace(".", ""),
                                                 text = "[content]", padding = [0, 20, 0, 0],
                                                 row = 0, column= 1)

            if subsection in list(self.showSubsectionsForTopSection.keys()):
                openContentLabel.clicked = self.showSubsectionsForTopSection[subsection]
            else:
                self.showSubsectionsForTopSection[subsection] = True
                openContentLabel.clicked = True

            openContentOfTheTopSection(locFrame, openContentLabel)
            _uuicom.bindChangeColorOnInAndOut(openContentLabel)

            openContentLabel.render()

    def populateTOC(self):
        text_curr = fsm.Wr.BookInfoStructure.getSubsectionsAsTOC()

        text_curr_filtered = []

        if self.filterToken != "":
            for i in range(len(text_curr)):
                subsection = text_curr[i][0]

                if "." not in subsection:
                    continue

                imLinkDict = fsm.Data.Sec.imLinkDict(subsection)
                extraImagesDict = fsm.Data.Sec.extraImagesDict(subsection)

                for k,v in imLinkDict.items():
                    entryImText = fsm.Wr.SectionInfoStructure.getEntryImText(subsection, k)

                    if k in list(extraImagesDict.keys()):
                        for t in extraImagesDict[k]:
                            entryImText += t

                    if (self.filterToken.lower() in v.lower()) \
                        or (self.filterToken.lower() in entryImText.lower()):
                        text_curr_filtered.append(text_curr[i])
                        break
        else:
            text_curr_filtered = text_curr

        for i in range(len(text_curr_filtered)):
            subsection = text_curr_filtered[i][0]
            topSection = subsection.split(".")[0]
            level = text_curr_filtered[i][1]

            if (topSection == fsm.Data.Book.currTopSection) \
                or self.showAll:
                self.showSubsectionsForTopSection[subsection] = True
            else:
                self.showSubsectionsForTopSection[subsection] = False

            self.addTOCEntry(subsection, level, i)

    def render(self, widjetObj=None, shouldScroll = False, renderData=..., **kwargs):
        self.shouldScroll = shouldScroll
        self.displayedImages = []
        self.subsectionContentLabels = []
        self.currSecondRowLabels = []
        self.linkFrames = []
        self.showImagesLabels = {}

        for child in self.scrollable_frame.winfo_children():
            child.destroy()

        if self.showSubsectionsForTopSection == {}:
            tsList = fsm.Wr.BookInfoStructure.getTopSectionsList()

            if tsList != _u.Token.NotDef.list_t:
                for ts in tsList:
                    self.showSubsectionsForTopSection[ts] = bool(int(fsm.Data.Book.sections[ts]["showSubsections"]))

        self.populateTOC()

        super().render(widjetObj, renderData, **kwargs)

        if self.widgetToScrollTo != None:
            try:
                self.widgetToScrollTo.event_generate(ww.currUIImpl.Data.BindID.mouse1)
            except:
                pass

        if self.openedMainImg != None and shouldScroll:
            try:
                self.openedMainImg.event_generate(ww.currUIImpl.Data.BindID.customTOCMove)
            except:
                pass
        
        if self.entryAsETR.widget != None:
            self.entryAsETR.widget.focus_force()