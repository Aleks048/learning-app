from tkinter import ttk
from PIL import Image, ImageTk
import Pmw
import os

import UI.widgets_wrappers as ww
import UI.widgets_collection.main.math.UI_layouts.mainLayout as mui
import UI.widgets_collection.toc.toc as tocw
import settings.facade as sf
import data.constants as dc
import data.temp as dt
import tkinter as tk
import scripts.osascripts as oscr
import outside_calls.outside_calls_facade as ocf
import file_system.file_system_facade as fsm
import _utils._utils_main as _u
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
    group = ""
    image = None


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

        self.tocBox.render()

def getWidgetSubsecId(subsection):
    return subsection.replace(".", "$")

def getWidgetNameID(subsection, idx):
    subSecID = getWidgetSubsecId(subsection)
    nameId:str = subSecID + "_" + str(idx)
    return nameId.replace(".", "")

class TOC_BOX(ww.currUIImpl.ScrollableBox,
              dc.AppCurrDataAccessToken):
    subsection = ""
    subsectionClicked = _u.Token.NotDef.str_t
    entryClicked = _u.Token.NotDef.str_t
    showSubsectionsForTopSection = {}
    displayedImages = []
    parent = None
    openedMainImg = None

    # used to filter toc data when the search is performed
    filterToken = ""
    showAll = None

    def __init__(self, parentWidget, prefix, windth = 700, height = 570, showAll = False):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 3, "columnspan" : 6, "rowspan": 10},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_showCurrScreenshotLocation_text"

        self.parent = parentWidget.widgetObj
        self.showAll = showAll

        self.subsectionClicked = fsm.Data.Book.subsectionOpenInTOC_UI
        self.entryClicked = fsm.Data.Book.entryImOpenInTOC_UI

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
                        width = windth)
    

    def scroll_into_view(self, event):
        try:
            posy = 0
            pwidget = event.widget

            self.scrollBar.yview_scroll(-100, "units")
            self.scrollBar.update()
            event.widget.update()

            while pwidget != self.parent:
                posy += pwidget.winfo_y()
                pwidget = pwidget.master

            canvas_top = self.scrollBar.winfo_y()

            widget_top = posy

            count = 1
            while widget_top not in range(int(canvas_top) + 200, int(canvas_top) + 250):
                if count > 200:
                    break

                count +=1
                posy = 0
                pwidget = event.widget

                while pwidget != self.parent:
                    posy += pwidget.winfo_y()
                    pwidget = pwidget.master

                event.widget.update()
                widget_top = posy
                
                if self.scrollBar != None:
                    self.scrollBar.yview_scroll(1, "units")
                    self.scrollBar.update()
        except:
            pass

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
            self.render(shouldScroll = False)
        elif broadcasterType == mui.ImageGeneration_BTN:
            self.entryClicked = entryClicked
            self.render()
        elif broadcasterType == mui.ImageGroupAdd_BTN:
            self.render()
        elif broadcasterType == tocw.Filter_ETR:
            self.filterToken = data
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

        def bindChangeColorOnInAndOut(widget, shouldBeRed = False):
            def __changeTextColorBlue(event = None, *args):
                event.widget.configure(foreground="blue")

            def __changeTextColorRed(event = None, *args):
                event.widget.configure(foreground="red")

            def __changeTextColorWhite(event = None, *args):
                event.widget.configure(foreground="white")
            
            widget.bind(ww.currUIImpl.Data.BindID.enterWidget, __changeTextColorBlue)
            if not shouldBeRed:
                widget.bind(ww.currUIImpl.Data.BindID.leaveWidget, __changeTextColorWhite)
            else:
                widget.bind(ww.currUIImpl.Data.BindID.leaveWidget, __changeTextColorRed)
        
        def openOMOnThePageOfTheImage(widget:LabelWithClick, targetSubsection, targetImIdx):
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

            imageWidgetID = "imageWidget_"
            
            def closeAllImages():
                for parent in gpframe.winfo_children():
                    for child in parent.winfo_children():
                        if "contentOfImages_" in str(child):
                            subsection = str(child).split("_")[-2].replace("$", ".")
                            idx = str(child).split("_")[-1]
                            alwaysShow = fsm.Data.Sec.tocWImageDict(subsection)[idx] == "1"

                            if not alwaysShow: 
                                child.clicked = False
                            else: 
                                child.clicked = True

                        if imageWidgetID in str(child):
                            subsection = str(child).split("_")[-2].replace("$", ".")
                            idx = str(child).split("_")[-1]
                            alwaysShow = fsm.Data.Sec.tocWImageDict(subsection)[idx] == "1"

                            if not alwaysShow: 
                                try:
                                    child.destroy()
                                except:
                                    pass

            def __cmd(event, *args):
                if ((not label.clicked and int(event.type) == 4)) or\
                    ((not label.clicked and int(event.type) == 35)):
                    closeAllImages()
                    label.clicked = True
                    self.entryClicked = imIdx

                    imageGroups = list(fsm.Data.Sec.imagesGroupsList(subsection).keys())
                    imageGroupidx = fsm.Data.Sec.imagesGroupDict(subsection)[imIdx]
                    imageGroup = imageGroups[imageGroupidx]

                    shouldShowGroup = fsm.Data.Sec.imagesGroupsList(subsection)[imageGroup]

                    if not shouldShowGroup:
                        return

                    # mainImage
                    currBookName = sf.Wr.Manager.Book.getCurrBookName()
                    screenshotFolder = _upan.Paths.Screenshot.getAbs(currBookName, subsection)
                    mainImageName = _upan.Names.getImageName(str(imIdx), subsection)
                    mainImagePath = os.path.join(screenshotFolder,  mainImageName + ".png")
                    pilIm = Image.open(mainImagePath)
                    pilIm.thumbnail([550,1000], Image.ANTIALIAS)
                    img = ImageTk.PhotoImage(pilIm)
                    self.displayedImages.append(img)
                    
                    name:str = imageWidgetID + "_" + subSecID + "_" + imIdx
                    name = name.replace(".", "$")
                    imLabel = LabelWithClick(tframe, image=img, name = name, padding= [90, 0, 0, 0])
                    imLabel.imagePath = mainImagePath
                    imLabel.bind(ww.currUIImpl.Data.BindID.mouse1, 
                                 lambda event, *args: os.system("open " + "\"" + event.widget.imagePath + "\""))

                    imLabel.bind(ww.currUIImpl.Data.BindID.customTOCMove, lambda event: self.scroll_into_view(event))

                    imLabel.grid(row = 3, column = 0, columnspan = 1000, sticky=tk.NW)

                    imLinkDict = fsm.Data.Sec.imLinkDict(subsection)

                    if type(imLinkDict) == dict:
                        if str(imIdx) in list(imLinkDict.keys()):
                            imText = imLinkDict[str(imIdx)]
                        else:
                            imText = _u.Token.NotDef.str_t
                    else:
                        imText = _u.Token.NotDef.str_t

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

                            ename = imageWidgetID + "_e_" + str(i) + "_" + subSecID + "_" + imIdx
                            ename = ename.replace(".", "$")
                            eimLabel = LabelWithClick(tframe, image=img, name = ename, padding= [90, 0, 0, 0])
                            eimLabel.imagePath = extraImFilepath
                            eimLabel.bind(ww.currUIImpl.Data.BindID.mouse1, 
                                        lambda event, *args: os.system("open " + "\"" + event.widget.imagePath + "\""))
                            eimLabel.grid(row = i + 4, column = 0, columnspan = 1000, sticky=tk.NW)

                            balloon.bind(eimLabel, "{0}".format(eImText))
                    
                    if int(event.type) == 4 or \
                       int(event.type) == 35:
                        for child in tframe.winfo_children():
                            if "contentImages_" + subSecID in str(child):
                                child.clicked = True

                    if shouklScroll:
                        imLabel.event_generate(ww.currUIImpl.Data.BindID.customTOCMove)
                else:
                    self.entryClicked = _u.Token.NotDef.str_t
                    self.scroll_into_view(event)
                    closeAllImages()
     
            __cmd(event, *args)

        def openContentOfTheSection(frame, label):
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
                
                def removeEntryCmd(event, *args):
                    widget = event.widget
                    fsm.Wr.SectionInfoStructure.removeEntry(widget.subsection, widget.imIdx)
                    self.render()


                # 4 : event of mouse click
                # 19 : event of being rendered
                if ((not label.clicked) and (int(event.type) == 4)) or\
                    ((self.subsectionClicked == subsection) and (int(event.type) == 19)) or\
                    self.showAll:

                    if not self.showAll:
                        closeAllSubsections()

                    i = 0

                    subSecID = getWidgetSubsecId(subsection)
                    prevImGroupName = _u.Token.NotDef.str_t

                    for k,v in links.items():
                        if (self.filterToken != "") and \
                           (self.filterToken.lower() not in v.lower()):
                            continue

                        currImGroupidx = imagesGroupDict[k]

                        if currImGroupidx == _u.Token.NotDef.str_t:
                            currImGroupidx = 0

                        currImGroupName = imagesGroups[currImGroupidx]

                        topPad = 0
                        gridRowStartIdx = 0

                        if currImGroupName != prevImGroupName:
                            if not imagesGroupsWShouldShow[currImGroupName]:
                                topPad = 10
                            elif (k != "0"):
                                topPad = 20

                        if self.filterToken != "":
                            topPad = 0

                        nameId = getWidgetNameID(subsection, k)

                        tempFrame = ttk.Frame(frame,
                                              name = "contentFr_" + nameId,
                                              padding=[0, topPad, 0, 0])

                        if currImGroupName != prevImGroupName:
                            if currImGroupName != "No group":
                                imageGroupFrame = ttk.Frame(tempFrame,
                                                            name = "contentImageGroupFr_" + nameId,
                                                            padding=[0, topPad, 0, 0])
                                imageGroupFrame.grid(row = 0, column = 0, sticky=tk.NW)

                                imageGroupLabel = ttk.Label(imageGroupFrame, 
                                                            text = currImGroupName, 
                                                            name = "contentGroupP_" + nameId,
                                                            padding= [30, 0, 0, 0])
                                imageGroupLabel.grid(row = 0, column = 0, sticky=tk.NW)
                                hideImageGroupLabel = LabelWithClick(imageGroupFrame, 
                                                                     text = "[show/hide]", 
                                                                     name = "contentHideImageGroupLabel_" + nameId)
                                hideImageGroupLabel.grid(row = 0, column = 1, sticky=tk.NW)
                                hideImageGroupLabel.subsection = subsection
                                hideImageGroupLabel.imIdx = str(i)
                                hideImageGroupLabel.group = currImGroupName

                                bindChangeColorOnInAndOut(hideImageGroupLabel)

                                def __cmd(e):
                                    imagesGroupsList = fsm.Data.Sec.imagesGroupsList(e.widget.subsection)
                                    imagesGroupsList[e.widget.group] = not imagesGroupsList[e.widget.group]
                                    fsm.Data.Sec.imagesGroupsList(e.widget.subsection, imagesGroupsList)
                                    self.render()

                                hideImageGroupLabel.bind(ww.currUIImpl.Data.BindID.mouse1, __cmd)
                                gridRowStartIdx = 1
                            else:
                                imageNoGroupLabel = ttk.Label(tempFrame, 
                                                            text = "No group",
                                                            name = "contentNoGroupP_" + nameId,
                                                            padding= [30, 0, 0, 0])
                                imageNoGroupLabel.grid(row = 0, column = 0, sticky=tk.NW)
                                gridRowStartIdx = 1

                        if currImGroupName not in imagesGroups:
                            currImGroupName = imagesGroups[0]
                            imagesGroupDict[k] = 0
                            fsm.Data.Sec.imagesGroupDict(subsection, imagesGroupDict)

                        imagesGroup = ImageGroupOM(self, subsection, k, tempFrame, 
                                                   tk.StringVar(), currImGroupName, *imagesGroups)

                        # textLabelPage = ttk.Label(tempFrame, 
                        #                           text = k + ": " + v, 
                        #                           name = "contentP_" + nameId, 
                        #                           wraplength=450,
                        #                           padding=[60, 0, 0, 0])
                        
                        def getEntryImg(tex):
                            secreenshotPath = _upan.Paths.Screenshot.getAbs(sf.Wr.Manager.Book.getCurrBookName(), subsection)
                            entryImgPath = os.path.join(secreenshotPath, f"_{nameId}.png")

                            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryImgPath):
                                result = Image.open(entryImgPath)
                            else:
                                result = tff.Wr.TexFileUtils.fromTexToImage(tex, entryImgPath) 

                            return result

                        latexTxt = tff.Wr.TexFileUtils.fromEntryToLatexTxt(k, v)
                        pilIm = getEntryImg(latexTxt)

                        shrink = 0.7
                        pilIm.thumbnail([int(pilIm.size[0] * shrink),int(pilIm.size[1] * shrink)], Image.ANTIALIAS)
                        img = ImageTk.PhotoImage(pilIm)
                        
                        textLabelPage = LabelWithClick(tempFrame,
                                                 image=img, 
                                                 name = "contentP_" + nameId, 
                                                 padding= [60, 0, 0, 0])
                        textLabelPage.image = img

                        # if "excercise" in v.lower():
                        #     textLabelPage.configure(foreground="red")

                        textLabelFull = ttk.Label(tempFrame, text = "[full]", name = "contentFull_" + nameId)
                        chkbtnShowPermamently = EntryShowPermamentlyCheckbox(tempFrame, 
                                                                             subsection, str(i), 
                                                                             "contentShowAlways_" + nameId,
                                                                             self)
                        showImages = LabelWithClick(tempFrame, text = "[im]", name = "contentOfImages_" + nameId)
                        removeEntry = LabelWithClick(tempFrame, text = "[delete]", name = "contentRemoveEntry" + nameId)

                        # adding a frame to show global links
                        linksFrame = ttk.Frame(tempFrame,
                                              name = "contentLinksFr_" + nameId,
                                              padding=[0, 0, 0, 0])
                        
                        imGlobalLinksDict = fsm.Data.Sec.imGlobalLinksDict(subsection)

                        if str(i) in imGlobalLinksDict.keys():
                            glLinks:dict = fsm.Data.Sec.imGlobalLinksDict(subsection)[str(i)]

                            glLinkLablel = ttk.Label(linksFrame, 
                                                    text = "Links: ", 
                                                    name = "contentLinksIntroFr_" + nameId,
                                                    padding=[60, 0, 0, 0])
                            glLinkId = 0

                            for lk, _ in glLinks.items():
                                targetSubsection = lk.split("_")[0]
                                glLinkLablel.subsection = targetSubsection
                                targetImIdx = lk.split("_")[1]
                                glLinkLablel.imIdx = targetImIdx

                                imLinkDict = fsm.Data.Sec.imLinkDict(targetSubsection)

                                glLinkLablel = LabelWithClick(linksFrame, text = lk + ": " + imLinkDict[targetImIdx], name = "contentGlLinks_" + nameId + "_" + str(glLinkId))
                                glLinkLablel.grid(row = 0, column = glLinkId + 1, sticky=tk.NW)
                                bindChangeColorOnInAndOut(glLinkLablel)

                                openOMOnThePageOfTheImage(glLinkLablel, targetSubsection, targetImIdx)
                                glLinkId += 1

                        showImages.imIdx = k
                        showImages.clicked = False

                        
                        removeEntry.imIdx = k
                        removeEntry.subsection = subsection
                        removeEntry.bind(ww.currUIImpl.Data.BindID.mouse1,
                                         removeEntryCmd)

                        showImages.bind(ww.currUIImpl.Data.BindID.mouse1, 
                                        lambda e, *args: __showIMagesONClick(e, subSecID, True, *args))
                        showImages.bind(ww.currUIImpl.Data.BindID.customTOCMove, 
                                        lambda e, *args: __showIMagesONClick(e, subSecID, False, *args))

                        tocWImageDict = fsm.Data.Sec.tocWImageDict(subsection)

                        if tocWImageDict == _u.Token.NotDef.dict_t:
                            alwaysShow = False
                        else:
                            alwaysShow = tocWImageDict[str(i)] == "1"

                        if (subsection == self.subsectionClicked and k == self.entryClicked) or alwaysShow:
                            showImages.event_generate(ww.currUIImpl.Data.BindID.customTOCMove)

                        if imagesGroupsWShouldShow[currImGroupName]:
                            textLabelPage.grid(row = gridRowStartIdx, column = 0, sticky=tk.NW)
                            showImages.grid(row = gridRowStartIdx, column = 1, sticky=tk.NW)
                            textLabelFull.grid(row = gridRowStartIdx, column = 2, sticky=tk.NW)
                            chkbtnShowPermamently.grid(row = gridRowStartIdx, column = 3, sticky=tk.NW)
                            imagesGroup.grid(row = gridRowStartIdx, column = 4, sticky=tk.NW)  
                            removeEntry.grid(row = gridRowStartIdx, column = 5, sticky=tk.NW)
                            linksFrame.grid(row = gridRowStartIdx + 1, column = 0, columnspan = 6, sticky=tk.NW)

                        openOMOnThePageOfTheImage(textLabelPage, subsection, k)

                        if "excercise" in v.lower():
                            bindChangeColorOnInAndOut(textLabelPage, True)
                        else:
                            bindChangeColorOnInAndOut(textLabelPage, False)

                        bindChangeColorOnInAndOut(showImages)
                        bindChangeColorOnInAndOut(removeEntry)
                        openSectionOnIdx(textLabelFull, k)
                        bindChangeColorOnInAndOut(textLabelFull)

                        tempFrame.grid(row=i + 2, column=0, columnspan = 100, sticky=tk.NW)
                        prevImGroupName = currImGroupName
                        i += 1
                    
                    dummyFrame = ttk.Frame(frame, name = "contentDummyFr_" + nameId)
                    dummyEntryPage = ttk.Label(dummyFrame, text ="\n", name = "contentDummy_" + nameId)
                    dummyEntryPage.grid(row=0, column=0, sticky=tk.NW)
                    dummyFrame.grid(row=i + 1, column=0, sticky=tk.NW)

                    if int(event.type) == 4:
                        label.clicked = True
                        self.subsectionClicked = subsection

                    self.scroll_into_view(event)
                else:
                    for child in frame.winfo_children():
                        if "content" in str(child):
                            child.destroy()
                    
                    if int(event.type) == 4:
                        closeAllSubsections()
                            
                        label.clicked = False

                        self.subsectionClicked = _u.Token.NotDef.str_t

                    self.scroll_into_view(event)

                event.widget.configure(foreground="white")
            
            label.bind(ww.currUIImpl.Data.BindID.mouse1, __cmd)

            if (self.subsectionClicked == subsection and level != 0) or self.showAll:
                label.event_generate(ww.currUIImpl.Data.BindID.mouse1, x=10, y=10)         
       
        def openContentOfTheTopSection(frame, label):
            def __cmd(event = None, *args):
                
                # 4 : event of mouse click
                # 19 : event of being rendered
                if ((not label.clicked) and (int(event.type) == 4)) or\
                    ((self.showSubsectionsForTopSection[subsection] == True) and (int(event.type) == 19)) or\
                    self.showAll:
                    label.clicked = True
                    self.showSubsectionsForTopSection[subsection] = True
                    self.render()
                else:
                    if int(event.type) == 4:
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
        
        labelName = "label_" + subsection.replace(".", "")

        locFrame = ttk.Frame(self.scrollable_frame, name=labelName)
        super().addTOCEntry(locFrame, row, 0)

        nameId = "subsecLabel_" + subsection 
        nameId = nameId.replace(".", "")

        if level == 0:
            subsectionLabel = ttk.Label(locFrame, text = prettySubsections, padding= [0, 20, 0, 0], name = nameId)
        else:
            subsectionLabel = ttk.Label(locFrame, text = prettySubsections, name = nameId)

        openPdfOnStartOfTheSection(subsectionLabel)
        bindChangeColorOnInAndOut(subsectionLabel)

        subsectionLabel.grid(row = 0, column= 0, sticky=tk.NW)

        if level != 0:
            openContentLabel = LabelWithClick(locFrame, text = "[content]")
            rebuildLatex = LabelWithClick(locFrame, text = "[rebuild latex]")
            rebuildLatex.subsection = subsection

            if self.showAll:
                openContentLabel.clicked = True

            openContentOfTheSection(locFrame, openContentLabel)
            bindChangeColorOnInAndOut(openContentLabel)
            bindChangeColorOnInAndOut(rebuildLatex)

            def rebuildSubsectionLatexWrapper(subsection):
                fsm.Wr.SectionInfoStructure.rebuildSubsectionLatex(subsection, getWidgetNameID)
                self.render()

            rebuildLatex.bind(ww.currUIImpl.Data.BindID.mouse1,
                              lambda e, *args: rebuildSubsectionLatexWrapper(e.widget.subsection))

            openContentLabel.grid(row = 0, column= 1, sticky=tk.NW)
            rebuildLatex.grid(row = 0, column= 2, sticky=tk.NW)
        else:
            openContentLabel = LabelWithClick(locFrame, text = "[content]", padding= [0, 20, 0, 0])
            openContentLabel.clicked = self.showSubsectionsForTopSection[subsection]
            openContentOfTheTopSection(locFrame, openContentLabel)
            bindChangeColorOnInAndOut(openContentLabel)

            openContentLabel.grid(row = 0, column= 1, sticky=tk.NW)

    def populateTOC(self):
        text_curr = fsm.Wr.BookInfoStructure.getSubsectionsAsTOC()

        text_curr_filtered = []

        if self.filterToken != "":
            for i in range(len(text_curr)):
                subsection = text_curr[i][0]
                if "." not in subsection:
                    continue

                imLinkDict = fsm.Data.Sec.imLinkDict(subsection)
                
                for k,v in imLinkDict.items():
                    if self.filterToken.lower() in v.lower():
                        text_curr_filtered.append(text_curr[i])
                        break
        else:
            text_curr_filtered = text_curr

        for i in range(len(text_curr_filtered)):
            subsection = text_curr_filtered[i][0]
            level = text_curr_filtered[i][1]

            self.addTOCEntry(subsection, level, i)

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
            try:
                self.openedMainImg.event_generate(ww.currUIImpl.Data.BindID.customTOCMove)
            except:
                pass