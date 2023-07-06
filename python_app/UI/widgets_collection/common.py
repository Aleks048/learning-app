from tkinter import ttk
from PIL import ImageTk,Image
import Pmw
import os

import UI.widgets_wrappers as ww
import UI.widgets_collection.main.math.UI_layouts.mainLayout as mui
import _utils._utils_main as _u
import settings.facade as sf
import data.constants as dc
import data.temp as dt
import tkinter as tk
import scripts.osascripts as oscr
import outside_calls.outside_calls_facade as ocf
import file_system.file_system_facade as fsm
import _utils.logging as log
import _utils.pathsAndNames as _upan
import tex_file.tex_file_facade as tff


class LabelWithClick(ttk.Label):
    '''
    this is used to run different commands on whether the label was clicked even or odd times
    '''
    clicked = False
    imIdx = ""
    subsection = ""
    imagePath = ""


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
        imagesGroupDict = fsm.Data.Sec.imagesGroupDict(self.subsection)
        imagesGroupDict[self.imIdx] = self.var.get() if self.var.get() != "No group" else _u.Token.NotDef.str_t
        fsm.Data.Sec.imagesGroupDict(self.subsection, imagesGroupDict)

        self.tocBox.render()

class TOC_BOX(ww.currUIImpl.ScrollableBox,
              dc.AppCurrDataAccessToken):
    subsection = ""
    subsectionClicked = _u.Token.NotDef.str_t
    entryClicked = _u.Token.NotDef.str_t
    showSubsectionsForTopSection = {}
    displayedImages = []
    parent = None
    openedMainImg = None

    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 3, "columnspan" : 5, "rowspan": 10},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_showCurrScreenshotLocation_text"

        self.parent = parentWidget.widgetObj

        self.subsectionClicked = fsm.Data.Book.subsectionOpenInTOC_UI
        self.entryClicked = fsm.Data.Book.entryImOpenInTOC_UI

        tsList = fsm.Wr.BookInfoStructure.getTopSectionsList()

        if tsList != _u.Token.NotDef.list_t:
            for ts in tsList:
                self.showSubsectionsForTopSection[ts] = bool(int(fsm.Data.Book.sections[ts]["showSubsections"]))

        super().__init__(prefix,
                        name,
                        parentWidget,
                        renderData = data,
                        height=370,
                        width=570)
    
    def receiveNotification(self, broadcasterType, data = None, entryClicked = None):
        if broadcasterType == mui.ExitApp_BTN:
            tsList = fsm.Wr.BookInfoStructure.getTopSectionsList()

            sections = fsm.Data.Book.sections

            for ts in tsList:
                sections[ts]["showSubsections"] = str(int(self.showSubsectionsForTopSection[ts]))

            fsm.Data.Book.sections = sections

            fsm.Data.Book.subsectionOpenInTOC_UI = self.subsectionClicked
            fsm.Data.Book.entryImOpenInTOC_UI = self.entryClicked
        elif broadcasterType == mui.AddExtraImage_BTN:
            self.render(shouldScroll = False)
        elif broadcasterType == mui.ImageGeneration_BTN:
            self.entryClicked = entryClicked
            self.render()
        else:
            self.render()

    def addTOCEntry(self, subsection, level, row):
        def openPdfOnStartOfTheSection(widget):
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
                imOMName = fsm.Data.Sec.origMatNameDict(subsection)[imIdx]

                omFilepath = fsm.Wr.OriginalMaterialStructure.getMaterialPath(imOMName)                
                imLinkOMPageDict = fsm.Data.Sec.imLinkOMPageDict(subsection)
                page = imLinkOMPageDict[imIdx]

                ocf.Wr.PdfApp.openPDF(omFilepath, page)

                zoomLevel = fsm.Wr.OriginalMaterialStructure.getMaterialZoomLevel(imOMName)
                pdfToken:str = omFilepath.split("/")[-1].replace(".pdf", "")
                cmd = oscr.setDocumentScale(pdfToken, zoomLevel)
                _u.runCmdAndWait(cmd)
            
            widget.bind( ww.currUIImpl.Data.BindID.mouse1, __cmd)
        
        def openSectionOnIdx(widget, imIdx):
            def __cmd(event = None, *args):
                # open orig material on page
                bookName = sf.Wr.Manager.Book.getCurrBookName()
                currTopSection = fsm.Data.Book.currTopSection

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

                    imText = fsm.Data.Sec.imLinkDict(subsection)[str(imIdx)]
                    balloon.bind(imLabel, "{0}".format(imText))

                    self.openedMainImg = imLabel

                    # extraImages
                    if imIdx in list(fsm.Data.Sec.extraImagesDict(subsection).keys()):
                        extraImages = fsm.Data.Sec.extraImagesDict(subsection)[imIdx]

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

                links:dict = fsm.Data.Sec.imLinkDict(subsection)
                imagesGroupDict:dict = fsm.Data.Sec.imagesGroupDict(subsection)
                imagesGroups:list = list(set(imagesGroupDict.values()))
                imagesGroups = ["No group"] + [i for i in imagesGroups if i != _u.Token.NotDef.str_t]

                def closeAllSubsections():
                    for wTop1 in event.widget.master.master.winfo_children():
                        for wTop2 in wTop1.winfo_children():
                            if "labelwithclick" in str(wTop2):
                                wTop2.clicked = False
                            if "contentFr_"  in str(wTop2) or "contentDummyFr_" in str(wTop2):
                                wTop2.destroy()
                
                def removeEntryCmd(event, *args):
                    widget = event.widget
                    fsm.Wr.SectionInfoStructure.removeEntry(widget.subsection, widget.imIdx)
                    self.render()


                # 4 : event of mouse click
                # 19 : event of being rendered
                if ((not label.clicked and int(event.type) == 4)) or\
                    ((self.subsectionClicked == subsection) and (int(event.type) == 19)):
                    closeAllSubsections()

                    i = 0

                    subSecID = subsection.replace(".", "")
                    prevImGroupName = _u.Token.NotDef.str_t

                    for k,v in links.items():
                        currImGroupName = imagesGroupDict[k]
                        topPad = 0
                        gridRowStartIdx = 0

                        if currImGroupName != prevImGroupName:
                            topPad = 20

                        tempFrame = ttk.Frame(frame,
                                              name = "contentFr_" + subSecID + "_" + str(i),
                                              padding=[0, topPad, 0, 0])

                        if currImGroupName != prevImGroupName:
                            if currImGroupName != _u.Token.NotDef.str_t:
                                imageGroupLabel = ttk.Label(tempFrame, text = " "* 8 + currImGroupName, name = "contentGroupP_" + subSecID +str(i))
                                imageGroupLabel.grid(row = 0, column = 0, sticky=tk.NW)
                                gridRowStartIdx = 1

                        currGroup = imagesGroupDict[k] if imagesGroupDict[k] != _u.Token.NotDef.str_t else "No group"
                        imagesGroup = ImageGroupOM(self, subsection, k, tempFrame, tk.StringVar(), currGroup, *imagesGroups)
                        textLabelPage = ttk.Label(tempFrame, text = "\t" + k + ": " + v, name = "contentP_" + subSecID +str(i))
                        textLabelFull = ttk.Label(tempFrame, text = "[full]", name = "contentFull_" + subSecID + str(i))
                        showImages = LabelWithClick(tempFrame, text = "[images]", name = "contentOfImages_" + subSecID + str(i))
                        removeEntry = LabelWithClick(tempFrame, text = "[delete]", name = "contentRemoveEntry" + subSecID + str(i))

                        showImages.imIdx = k
                        showImages.clicked = False

                        imagesGroup.grid(row = gridRowStartIdx, column = 4, sticky=tk.NW)  
                        
                        removeEntry.grid(row = gridRowStartIdx, column = 3, sticky=tk.NW)  
                        removeEntry.imIdx = k
                        removeEntry.subsection = subsection
                        removeEntry.bind(ww.currUIImpl.Data.BindID.mouse1,
                                         removeEntryCmd)

                        showImages.grid(row = gridRowStartIdx, column = 2, sticky=tk.NW)
                        showImages.bind(ww.currUIImpl.Data.BindID.mouse1, 
                                        lambda e, *args: __showIMagesONClick(e, subSecID, True, *args))
                        showImages.bind(ww.currUIImpl.Data.BindID.customTOCMove, 
                                        lambda e, *args: __showIMagesONClick(e, subSecID, False, *args))

                        if subsection == self.subsectionClicked and k == self.entryClicked:
                            showImages.event_generate(ww.currUIImpl.Data.BindID.customTOCMove)

                        textLabelPage.grid(row = gridRowStartIdx, column = 0, sticky=tk.NW)
                        textLabelFull.grid(row = gridRowStartIdx, column = 1, sticky=tk.NW)

                        openOMOnThePageOfTheImage(textLabelPage, k)
                        bindChangeColorOnInAndOut(textLabelPage)
                        bindChangeColorOnInAndOut(showImages)
                        bindChangeColorOnInAndOut(removeEntry)
                        openSectionOnIdx(textLabelFull, k)
                        bindChangeColorOnInAndOut(textLabelFull)

                        tempFrame.grid(row=i + 2, column=0, columnspan = 100, sticky=tk.NW)
                        prevImGroupName = currImGroupName
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
                    log.autolog("hoy")
                    label.clicked = True
                    self.showSubsectionsForTopSection[subsection] = True
                    self.render()
                else:
                    if int(event.type) == 4:
                        log.autolog("Hoy")
                        self.subsectionClicked = _u.Token.NotDef.str_t
                        self.entryClicked = _u.Token.NotDef.str_t
                        self.showSubsectionsForTopSection[subsection] = False
                        self.displayedImages = []
                        self.openedMainImg = None

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
            subsectionText = fsm.Data.Sec.text(subsection)

        if level == 0 and subsection != _u.Token.NotDef.str_t:
            subsectionText = fsm.Data.Book.sections[subsection]["name"]

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
        text_curr = fsm.Wr.BookInfoStructure.getSubsectionsAsTOC()
        
        for i in range(len(text_curr)):
            self.addTOCEntry(text_curr[i][0], text_curr[i][1], i)

    def render(self, widjetObj=None, shouldScroll = True, renderData=..., **kwargs):

        for child in self.scrollable_frame.winfo_children():
            child.destroy()

        if self.showSubsectionsForTopSection == {}:
            tsList = fsm.Wr.BookInfoStructure.getTopSectionsList()

            if tsList != _u.Token.NotDef.list_t:
                for ts in tsList:
                    self.showSubsectionsForTopSection[ts] = bool(int(fsm.Data.Book.sections[ts]["showSubsections"]))

        self.populateTOC()

        super().render(widjetObj, renderData, **kwargs)

        if self.openedMainImg != None and shouldScroll:
            self.openedMainImg.event_generate(ww.currUIImpl.Data.BindID.customTOCMove)