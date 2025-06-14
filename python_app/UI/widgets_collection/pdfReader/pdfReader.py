from tkinter import ttk
import fitz
from PIL import Image
from threading import Thread
import time
import io
import re
import copy
import subprocess

import UI.widgets_wrappers as ww
import UI.widgets_manager as wm
import UI.widgets_collection.utils as uw
import UI.widgets_facade as wf
import UI.widgets_collection.utils as _ucomw
import UI.widgets_collection.common as comw
import UI.widgets_data as wd
import _utils._utils_main as _u
import data.temp as dt
import _utils.pathsAndNames as _upan
import data.constants as dc
import file_system.file_system_facade as fsf
import settings.facade as sf
import outside_calls.outside_calls_facade as ocf


class PdfReaderLebelWithClick(comw.TOCLabelWithClick):
    pass


class SecondaryImageFrameNameLabel(comw.TOCLabelWithClick):
    def __init__(self, root, prefix, row, column, 
                 columnspan=1, sticky=ww.currUIImpl.Orientation.NW, 
                 padding=[0, 0, 0, 0], image=None, text=None):
        self.subsection = None
        self.imIdx = None
        
        super().__init__(root, prefix, 
                         row, column, columnspan, 
                         sticky, padding, image, text)


class NotesImageLabel(ttk.Label):
    def __init__(self, root, name, subsection, imIdx, 
                 noteIdx, text = _u.Token.NotDef.str_t, padding = [0, 0, 0, 0]):
        self.image = None
        
        self.noteImIdx = str(noteIdx)

        bookName = sf.Wr.Manager.Book.getCurrBookName()

        imagePath = _upan.Paths.Entry.NoteImage.getAbs(bookName, subsection, imIdx, noteIdx)

        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
            imagePath = _upan.Paths.Entry.NoteImage.getAbs(bookName, subsection, imIdx, -1)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                fsf.Wr.EntryInfoStructure.rebuildNote(subsection, imIdx, -1, "-1", bookName)

        if text == _u.Token.NotDef.str_t:
            pilIm = Image.open(imagePath)
            pilIm.thumbnail([530, 1000], Image.LANCZOS)
            self.image = ww.currUIImpl.UIImage(pilIm)
            return super().__init__(root, name = name, image = self.image, padding = padding)
        else:
            return super().__init__(root, name = name, text = text, padding = padding)

class PdfReaderImageCanvas(comw.TOCCanvasWithclick):
    class Label(comw.TOCCanvasWithclick.Label):
        def __init__(self, subsection, imIdx, canvas, 
                     startX, startY, endX, endY, 
                     extraDataToSave, labelStartX=None, labelStartY=None):
            self.subsection = subsection
            self.imIdx = imIdx
            self.eImIdx = None
            labelText = f"{subsection}:{self.imIdx}"
            super().__init__(labelText, canvas, 
                             startX, startY, endX, endY, 
                             extraDataToSave, labelStartX, labelStartY,
                             labelCmd = self.__labelCmd)

        def __labelCmd(self, *args):
            fsf.Data.Book.subsectionOpenInTOC_UI = self.subsection
            fsf.Data.Book.entryImOpenInTOC_UI = self.imIdx

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onFullEntryMove" in dir(w):
                    w.onFullEntryMove()

    def __init__(self, root, prefix, row, column, imIdx, subsection,
                  columnspan=1, sticky=ww.currUIImpl.Orientation.NW, 
                  image=None, extraImIdx = None, makeDrawable=True,
                  page=None, resizeFactor=1, imagePath="", *args, **kwargs):
        self.selectingSone = False
        self.omPage = page

        self.getTextOfSelector = False
        
        self.subsection = subsection
        self.imIdx = imIdx
        self.eImIdx = extraImIdx
        
        super().__init__(root = root, prefix = prefix, 
                         row = row, column = column,
                         columnspan = columnspan, sticky = sticky, 
                         image = image, 
                         makeDrawable = makeDrawable, resizeFactor = resizeFactor, 
                         imagePath = imagePath, *args, **kwargs)
    
        if makeDrawable:
            keys = ["<Enter>", "<Leave>"]

            def __b(*args):
                keys, cmds = self._bindCmd()
                self.rebind(keys, cmds)
            def __ub(*args):
                keys = self._unbindCmd()
                self.unbind(keys)

            cmds = [__b, __ub]
            self.rebind(keys, cmds)

    def getEntryWidget(self, subsection, imIdx , eImIdx = None):
        for l in self.labels:
            if (l.subsection == subsection) and (str(l.imIdx) == str(imIdx)):
                if eImIdx == None:
                    return l
                else:
                    if str(l.eImIdx) == str(eImIdx):
                        return l

        return None

    def release(self, event):
        super().release(event)

        if self.selectingZone \
            and self.lastRecrangle != None:
            x = self.lastRecrangle.startX
            y =  self.lastRecrangle.startY
            x1 = self.lastRecrangle.endX
            y1 = self.lastRecrangle.endY
            self.lastRecrangle.deleteRectangle()

            if "image" in dir(self.image):
                im = self.image.image
            else:
                im = self.image
            im = im.crop([x - 1, y - 1, x1 + 1, y1 + 1])

            if self.getTextOfSelector:
                text = _u.getTextFromImage(None, im)

                subprocess.run("pbcopy", text=True, input=text)
                self.selectingZone = False
                self.getTextOfSelector = False
                self.lastRecrangle = None
                self.startCoord = []
                return

            currBookpath = sf.Wr.Manager.Book.getCurrBookFolderPath()

            imPath = ""

            if (self.eImIdx == None) or (self.eImIdx == _u.Token.NotDef.int_t):
                imPath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBookpath, 
                                                                            self.subsection, 
                                                                            self.imIdx)
            else:
                imPath = _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(currBookpath, 
                                                                             self.subsection,
                                                                             self.imIdx,
                                                                             self.eImIdx)

            if (self.eImIdx == None) or (self.eImIdx == _u.Token.NotDef.int_t):
                OMName = fsf.Data.Book.currOrigMatName
                fsf.Wr.OriginalMaterialStructure.setMaterialCurrPage(OMName, self.omPage)
                imLinkOMPageDict = fsf.Data.Sec.imLinkOMPageDict(self.subsection)
                imLinkOMPageDict[self.imIdx] = str(self.omPage)
                fsf.Data.Sec.imLinkOMPageDict(self.subsection, imLinkOMPageDict)

                self.labels.append(PdfReaderImageCanvas.Label(self.subsection,
                                                              self.imIdx,
                                                            self,
                                                            x, y, x1, y1,
                                                            {"page": self.omPage},
                                                            x - 85, y))
            else:
                self.labels.append(PdfReaderImageCanvas.Label(self.subsection,
                                                            f"{self.imIdx}_{self.eImIdx}",
                                                            self,
                                                            x, y, x1, y1,
                                                            {"page": self.omPage},
                                                            x - 85, y))
            self.saveFigures()

            im.save(imPath)

            self.selectingZone = False
            self.getTextOfSelector = False
            self.lastRecrangle = None
            self.startCoord = []
            return
        else:
            if self.drawing:
                self.rectangles.append(self.lastRecrangle)
                self.drawing = False

            self.saveFigures()

            self.lastRecrangle = None
            self.startCoord = []

    def refreshImage(self, addBrownBorder = True):
        super().refreshImage(addBrownBorder = True)

        if self.makeDrawable:
            keys = ["<Enter>", "<Leave>"]

            def __b(*args):
                keys, cmds = self._bindCmd()
                self.rebind(keys, cmds)
            def __ub(*args):
                keys = self._unbindCmd()
                self.unbind(keys)

            cmds = [__b, __ub]
            self.rebind(keys, cmds)

    def readFigures(self, *args):
        omBookName = fsf.Data.Book.currOrigMatName
        zoomLevel = int(fsf.Wr.OriginalMaterialStructure.getMaterialZoomLevel(omBookName))
        pageSize = fsf.Wr.OriginalMaterialStructure.getMaterialPageSize(omBookName)
        pageSize = [int(i) for i in pageSize]
        pageSizeZoomAffected = [zoomLevel, int((zoomLevel / pageSize[0]) * pageSize[1])]
        widthScale = pageSizeZoomAffected[0] / pageSize[0]
        heightScale = pageSizeZoomAffected[1] / pageSize[1]

        figuresList = \
            fsf.Wr.OriginalMaterialStructure.getMaterialPageFigures(omBookName, self.omPage)

        if type(figuresList) != str:
            figuresList = copy.copy(figuresList)

        # NOTE: inafficient and need to be optimised
        subsections = [i for i in fsf.Wr.BookInfoStructure.getSubsectionsList() if "." in i]

        for i in range(len(subsections) - 1, -1, -1):
            subsection = subsections[i]
            subsectionStartPage = int(fsf.Data.Sec.start(subsection))

            if subsectionStartPage > int(self.omPage) + 10:
                continue

            figuresLabelsData = fsf.Data.Sec.figuresLabelsData(subsection).copy()
            
            for k, l in figuresLabelsData.items():
                if type(l) == dict:
                    if l["page"] == self.omPage:
                        labelToAdd = PdfReaderImageCanvas.Label(subsection, k,
                                                            self,
                                                            l["coords"][0] * widthScale,
                                                            l["coords"][1] * heightScale,
                                                            l["coords"][2] * widthScale,
                                                            l["coords"][3] * heightScale,
                                                            {"page": self.omPage},
                                                            l["labelCoords"][0] * widthScale,
                                                            l["labelCoords"][1] * heightScale)
                        self.labels.append(labelToAdd)

        self.rectangles = []

        for f in figuresList:
            if type(f) != str:
                if f.get("type") != None:
                    f.pop("type")

                f["endX"] = f["endX"] * widthScale
                f["endY"] = f["endY"] * heightScale
                f["startX"] = f["startX"] * widthScale
                f["startY"] = f["startY"] * heightScale

            rect = comw.TOCCanvasWithclick.Rectangle.rectangleFromDict(f, self)
            self.rectangles.append(rect)
    

    def saveFigures(self, stampChanges = False, *args):
        figuresList = []

        omBookName = fsf.Data.Book.currOrigMatName
        zoomLevel = int(fsf.Wr.OriginalMaterialStructure.getMaterialZoomLevel(omBookName))
        pageSize = fsf.Wr.OriginalMaterialStructure.getMaterialPageSize(omBookName)
        pageSize = [int(i) for i in pageSize]
        pageSizeZoomAffected = [zoomLevel, int((zoomLevel / pageSize[0]) * pageSize[1])]
        widthScale = pageSize[0] / pageSizeZoomAffected[0]
        heightScale = pageSize[1] / pageSizeZoomAffected[1]

        for i in range(len(self.rectangles)):
            if self.rectangles[i] != None:
                f= self.rectangles[i].toDict()

                f["endX"] = f["endX"] * widthScale
                f["endY"] = f["endY"] * heightScale
                f["startX"] = f["startX"] * widthScale
                f["startY"] = f["startY"] * heightScale

                figuresList.append(f)
            else:
                self.rectangles.pop(i)

        omBookName = fsf.Data.Book.currOrigMatName
        fsf.Wr.OriginalMaterialStructure.setMaterialPageFigures(omBookName, self.omPage, figuresList)

        for l in self.labels:
            f = l.toDict()

            coords = []
            coords.append(f["coords"][0] * widthScale)
            coords.append(f["coords"][1] * heightScale)
            coords.append(f["coords"][2] * widthScale)
            coords.append(f["coords"][3] * heightScale)
            f["coords"] = coords

            labelCoords = []
            labelCoords.append(f["labelCoords"][0] * widthScale)
            labelCoords.append(f["labelCoords"][1] * heightScale)
            f["labelCoords"] = labelCoords

            figuresLabelsData = fsf.Data.Sec.figuresLabelsData(l.subsection)

            if l.eImIdx == None:
                figuresLabelsData[l.imIdx] = f
            else:
                figuresLabelsData[f"{l.imIdx}_{l.eImIdx}"] = f

            fsf.Data.Sec.figuresLabelsData(l.subsection, figuresLabelsData)

        if stampChanges:
            msg = "\
        After saving the figures'."
            _u.log.autolog(msg)
            ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

            proofsManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.ProofsManager)
            proofsManager.refresh(self.subsection, self.imIdx)

class PdfReaderImage(ww.currUIImpl.Frame):
    def __init__(self, parentWidget, prefix, row, pdfDoc, pageNum, pageWidth):
        self.imLabel = None
        self.pdfDoc = None
        self.pageNum = None
        self.pageWidth = None
        self.selectingZone = False
        self.subsection = None
        self.imIdx = None
        self.extraImIdx = None
        self.row = 0
        self.getTextOfSelector = False

        self.row = row

        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : row, "columnspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        self.pageWidth = pageWidth

        self.pdfDoc = pdfDoc
        self.pageNum = pageNum

        name = "_PdfImage_LBL"

        super().__init__(prefix, 
                        name,
                        parentWidget,
                        renderData = data)
    
    def toSelectingZone(self, subsection, imIdx, eImIdx, getTextOfSelector):
        self.subsection = subsection
        self.imIdx = imIdx
        self.extraImIdx = eImIdx
        self.imLabel.subsection = subsection
        self.imLabel.imIdx = imIdx
        self.imLabel.eImIdx = eImIdx
        self.selectingZone = True
        self.getTextOfSelector = getTextOfSelector
        self.imLabel.selectingZone = True
        self.imLabel.getTextOfSelector = getTextOfSelector

    def render(self):
        for child in self.getChildren().copy():
            child.destroy()

        page = self.pdfDoc.load_page(self.pageNum)
        pixmap = page.get_pixmap(dpi = 150)
        buf = io.BytesIO(pixmap.tobytes())
        pilIm = Image.open(buf)
        pilIm = pilIm.convert('RGB')
        width, height = pilIm.size
        pilIm = pilIm.resize([self.pageWidth, int((self.pageWidth / width) * height)],
                      Image.LANCZOS)
        img = ww.currUIImpl.UIImage(pilIm)
        self.imLabel = PdfReaderImageCanvas(root = self, imIdx =  None, subsection = None,
                                        prefix = f"_PdfImage_LBLim_{self.row}", 
                                        image = img, padding = [0, 0, 0, 0],
                                        row = 1, column = 1, columnspan = 1,
                                        extraImIdx = _u.Token.NotDef.int_t,
                                        makeDrawable = True, page = self.pageNum, 
                                        pilIm = pilIm)
        self.imLabel.selectingZone = self.selectingZone
        self.imLabel.getTextOfSelector = self.getTextOfSelector

        if self.selectingZone:
            self.imLabel.subsection = self.subsection
            self.imLabel.imIdx = self.imIdx
            self.imLabel.eImIdx = self.extraImIdx

        self.imLabel.render()
        self.imLabel.forceFocus()

        return super().render()

class MoveTOCtoImageEntry_BTN(ww.currUIImpl.Button,
                                  dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        self.subsection = None
        self.imIdx = None

        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 1, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        text = "Move TOC"
        name = "_MoveTOCToEntry_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.MainTOCManager)
        mainManager.moveTocToEntry(self.subsection, self.imIdx)

class ResizePdfReaderWindow_BTN(ww.currUIImpl.Label,
                              dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        self.subsection = None
        self.imIdx = None
        self.increaseLabel = None
        self.decreaseLabel = None

        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 2, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        text = ""
        name = "_ResizePDF_BTN"
        super().__init__(prefix, 
                        name,  
                        patentWidget, 
                        renderData, 
                        text = text)

    def render(self, **kwargs):
        if self.increaseLabel == None:
            self.increaseLabel = PdfReaderLebelWithClick(self, "_ResizePDF_BTNincreaseSize", 
                                    row = 0, column = 0, text = "+")
        if self.decreaseLabel == None:
            self.decreaseLabel = PdfReaderLebelWithClick(self, "_ResizePDF_BTNDecreaseSize", 
                                    row = 0, column = 1, text = "-")
        _ucomw.bindChangeColorOnInAndOut(self.increaseLabel)
        _ucomw.bindChangeColorOnInAndOut(self.decreaseLabel)


        def __resizeCmd(increase:bool):
            origMatName = fsf.Data.Book.currOrigMatName
            zoomLevel = int(fsf.Wr.OriginalMaterialStructure.getMaterialZoomLevel(origMatName))

            self.notify(PfdReader_BOX, [True])

            if increase:
                zoomLevel += 50
            else:
                zoomLevel = max(zoomLevel - 50, 0)
            
            fsf.Wr.OriginalMaterialStructure.setZoomLevel(origMatName, zoomLevel)

            self.notify(PfdReader_BOX)

        self.increaseLabel.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                  [lambda *args: __resizeCmd(True)])        
        self.decreaseLabel.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                  [lambda *args: __resizeCmd(False)])        

        self.increaseLabel.render()
        self.decreaseLabel.render()
        return super().render(**kwargs)

class ChangePagePdfReaderWindow_ETR(ww.currUIImpl.TextEntry,
                              dc.AppCurrDataAccessToken):
    def __init__(self, parentWidget, prefix):
        self.subsection = None
        self.imIdx = None
        self.textETR = None
        self.etrWidget = None # note this is set top the object so the <ENTER> bind workss
        self.increasePage = None
        self.decreasePage = None
        self.parentWidget = None
        self.currPage = None
        self.row = 2
        self.column = 4

        self.parentWidget = parentWidget

        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : self.column, "row" : self.row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }

        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wd.Data.ENT.defaultTextColor,
                                            "font": ('Georgia 14')},
            ww.TkWidgets.__name__ : {"width": 7}
        }

        origMatName = fsf.Data.Book.currOrigMatName
        currPage = fsf.Wr.OriginalMaterialStructure.getMaterialCurrPage(origMatName)
        self.currPage = int(currPage)

        self.defaultText = currPage
        name = "_ChangePagePDF_BTN"

        super().__init__(prefix, 
                name, 
                parentWidget, 
                renderData,
                extraBuildOptions,
                defaultText = self.defaultText,
                bindCmd = self.__bindCMD)

        super().setData(self.defaultText)


    def changePage(self, increase, newPage = None, notify = False):
        if newPage == None:
            if increase:
                newPage = int(self.getData()) + 1
            else:
                newPage = int(self.getData()) - 1

        self.setData(newPage)
        self.currPage = newPage

        _, cmd = self.__bindCMD()
        cmd[0](increase, notify)

    def render(self, **kwargs):
        self.setData(self.currPage)

        if self.increasePage == None:
            self.increasePage = PdfReaderLebelWithClick(self.rootWidget, "_ResizePDF_BTNNextIm", 
                                    row = self.row, column = self.column + 1, text = ">")
        if self.decreasePage == None:
            self.decreasePage = PdfReaderLebelWithClick(self.rootWidget, "_ResizePDF_BTNPrevIm", 
                                    row = self.row, column = self.column - 1, text = "<")
        _ucomw.bindChangeColorOnInAndOut(self.increasePage)
        _ucomw.bindChangeColorOnInAndOut(self.decreasePage)


        self.increasePage.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                 [lambda *args: self.changePage(True)])
        self.decreasePage.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                 [lambda *args: self.changePage(False)])

        self.increasePage.render()
        self.decreasePage.render()
        return super().render(**kwargs)

    def __bindCMD(self):
        def __cmd(increase = None, notify = True, *args):
            pageNumStr = self.getData()
            pageNum = int(pageNumStr)

            origMatName = fsf.Data.Book.currOrigMatName
            fsf.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(origMatName, pageNum)

            if notify:
                if increase != None:
                    self.notify(PfdReader_BOX, [increase])
                else:
                    self.notify(PfdReader_BOX)

        return [ww.currUIImpl.Data.BindID.Keys.cmdenter], [__cmd]

class PfdReader_BOX(ww.currUIImpl.ScrollableBox,
                    dc.AppCurrDataAccessToken):
    def __init__(self, parentWidget, prefix, width, height):
        self.doc = None
        self.subsection = None
        self.imIdx = None
        self.eImIdx = None

        self.currNoteCopyIdx = _u.Token.NotDef.int_t
        self.displayedPdfPages = []
        self.currPage = None
        self.getTextOfSelector = False

        origMatName = fsf.Data.Book.currOrigMatName
        zoomLevel = int(fsf.Wr.OriginalMaterialStructure.getMaterialZoomLevel(origMatName))
        self.pageWidth = zoomLevel

        self.latestWidgetToscrollTo = None
        self.latestNoteIdxToscrollTo = None
        self.pdfImages = []
        self.selectingZone = False
        self.prevPosition = 0.4
        self.changePrevPos = True

        self.prevPage = None
        self.prevPos = None

        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 1, "columnspan" : 6, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.W}
        }
        name = "_PdfReader_BOX"

        origMatName = fsf.Data.Book.currOrigMatName
        self.currPage = int(fsf.Wr.OriginalMaterialStructure.getMaterialCurrPage(origMatName))

        self.parent = parentWidget

        super().__init__(prefix,
                         name,
                         parentWidget,
                         renderData = data,
                         height = height,
                         width = width,
                         makeScrollable = True)

        filePath =fsf.Wr.OriginalMaterialStructure.getMaterialPath(fsf.Data.Book.currOrigMatName)
        self.doc = fitz.open(filePath)

        def on_vertical(event):
            self.scrollY(-1 * event.delta)

        self.rebind([ww.currUIImpl.Data.BindID.cmdModwheel], [on_vertical])

    def __scrollIntoView(self, event, widget = None):
        posy = 0

        if widget == None:
            pwidget = event.widget
        else:
            pwidget = widget

        self.update()
        pwidget.update()

        while pwidget != self.rootWidget:
            posy += pwidget.getYCoord()
            pwidget = pwidget.getParent()

        posy = 0

        if widget == None:
            pwidget = event.widget
        else:
            pwidget = widget

        while pwidget != self.parent:
            posy += pwidget.getYCoord()
            pwidget = pwidget.getParent()

        pos = posy - self.yPosition()
        height = self.getFrameHeight()
        self.moveY((pos / height) - 0.008)

    def removeMainLabel(self, subsection, imIdx, eImIdx):
        for p in self.displayedPdfPages:
            l = p.imLabel.getEntryWidget(subsection, imIdx, eImIdx)

            if l != None:
                l.deleteLabel()
                break

    def getIntoDrawingMode(self):
        self.selectingZone = False
        self.getTextOfSelector = False

        for im in self.displayedPdfPages:
            im.selectingZone = self.selectingZone
            im.getTextOfSelector = self.getTextOfSelector
            im.imLabel.selectingZone = self.selectingZone
            im.imLabel.getTextOfSelector = self.getTextOfSelector

    def getIntoSelectingMode(self, subsection, imIdx, eImIdx, getTextOfSelector):
        self.selectingZone = True
        self.getTextOfSelector = getTextOfSelector

        self.subsection = subsection
        self.imIdx = imIdx

        if eImIdx != None:
            eImIdx = int(eImIdx)
        
        for im in self.displayedPdfPages:
            im.toSelectingZone(subsection, imIdx, eImIdx, getTextOfSelector)

    def saveFigures(self):
        for im in self.displayedPdfPages:
            im.imLabel.saveFigures()

    def moveToEntryWidget(self, subsection, imIdx, eImIdx = None):
        if eImIdx == None:
            self.currPage = int(fsf.Data.Sec.imLinkOMPageDict(subsection)[imIdx])
        else:
            figuresLabelsData = fsf.Data.Sec.figuresLabelsData(subsection)
            if figuresLabelsData.get(f"{imIdx}_{eImIdx}") != None:
                 self.currPage = figuresLabelsData[f"{imIdx}_{eImIdx}"]["page"]

        OMName = fsf.Data.Book.currOrigMatName
        fsf.Wr.OriginalMaterialStructure.setMaterialCurrPage(OMName, str(self.currPage))

        self.prevPosition = 0.4

        entryWidget = None

        for l in self.displayedPdfPages:
            if str(l.pageNum) == str(self.currPage):
                entryWidget = l.imLabel.getEntryWidget(subsection, imIdx, eImIdx)

        if entryWidget != None:
            self.__scrollIntoView(None, entryWidget.label)

    def addPdfPages(self):
        '''
        for page in the pdf:
        '''
        if self.currPage < 2:
            return

        for i in range(self.currPage - 2, self.currPage + 3):
            pageImage = PdfReaderImage(self.scrollable_frame, f"_pdfPageIm{i}", i, self.doc, i, self.pageWidth)    
            pageImage.selectingZone = self.selectingZone
            pageImage.getTextOfSelector = self.getTextOfSelector
            pageImage.pageNum = i

            if self.selectingZone:
                pageImage.subsection = self.subsection
                pageImage.imIdx = self.imIdx
                pageImage.extraImIdx = self.eImIdx

            pageImage.render()

            self.displayedPdfPages.append(pageImage)

    def updateOMpage(self, force = False):
        if not force:
            self.saveFigures()

        origMatName = fsf.Data.Book.currOrigMatName

        addPage = 0
        prevYview = self.getY()

        if (0.0 <= prevYview) and (prevYview < 0.2):
            addPage = -2
        elif (0.2 <= prevYview) and (prevYview < 0.4):
            addPage = -1
        elif (0.6 <= prevYview) and (prevYview < 0.8):
            addPage = +1
        elif (0.8 <= prevYview) and (prevYview <= 1.0):
            addPage = +2

        newPage = str(int(self.currPage) + addPage)

        if newPage !=  str(fsf.Wr.OriginalMaterialStructure.getMaterialCurrPage(origMatName)):
            fsf.Wr.OriginalMaterialStructure.setMaterialCurrPage(origMatName, newPage)

    def hide(self, **kwargs):
        self.updateOMpage()

        self.prevPage = self.currPage

        if self.changePrevPos:
            self.updateScrollerPosition()

        return super().hide(**kwargs)

    def render(self, force = False, forceRerender = False):
        wd.Data.Reactors.entryChangeReactors[self.name] = self

        self.updateOMpage(force = force)
        self.currPage = int(self.currPage)

        if not forceRerender:
            if int(self.currPage) in self.getShownPagesList():
                for p in self.displayedPdfPages:
                    if p.pageNum == int(int(self.currPage)):
                        self.__scrollIntoView(p)
                return

        if self.currPage == self.prevPage:
            if (self.prevPos != 0.0) and (self.prevPos != None):
                self.prevPosition = self.prevPos

        for im in self.displayedPdfPages:
            im.hide()

        self.displayedPdfPages = []

        for w in self.getChildren().copy():
            w.destroy()

        self.forceFocus()

        self.addPdfPages()

        super().render(self.renderData)

        # if (self.latestWidgetToscrollTo != None) and (shouldScroll):
        #     self.__scrollIntoView(None, self.latestWidgetToscrollTo)
        self.moveY(self.prevPosition)

    def changePage(self, currPage):
        self.saveFigures()

        self.currPage = currPage

        self.prevPos = 0.4
        self.prevPosition = 0.4

        self.render()

    def moveToCurrPage(self):
        self.saveFigures()

        origMatName = fsf.Data.Book.currOrigMatName
        self.currPage = fsf.Wr.OriginalMaterialStructure.getMaterialCurrPage(origMatName)

        self.render()

        self.moveY(0.4)

    def receiveNotification(self, broadcasterType, data = None) -> None:
        self.saveFigures()
        if broadcasterType == SecondaryImagesFrame:
            newHeight = 820 -  data[0] - 20
            # if self.getHeight() != newHeight:
            #     self.setCanvasHeight(newHeight = newHeight)
        elif broadcasterType == ResizePdfReaderWindow_BTN:
            if data != None:
                for p in self.displayedPdfPages:
                    p.imLabel.saveFigures()
            else:
                origMatName = fsf.Data.Book.currOrigMatName
                zoomLevel = int(fsf.Wr.OriginalMaterialStructure.getMaterialZoomLevel(origMatName))
                self.pageWidth = zoomLevel

                self.displayedPdfPages = []

                self.update()
                self.render()

            self.moveX(0.06) # not perfect but should work for now
        elif broadcasterType == ChangePagePdfReaderWindow_ETR:
            origMatName = fsf.Data.Book.currOrigMatName
            self.currPage = fsf.Wr.OriginalMaterialStructure.getMaterialCurrPage(origMatName)

            self.updateScrollerPosition()
            prevYview = self.getY()

            if data != None:
                if len(data) != 0:
                    increase = data[0]
                    if increase:
                        prevYview -= 0.2
                    else:
                        prevYview += 0.2

            self.render(forceRerender = True)
            self.moveY(prevYview)

    def updateScrollerPosition(self):
        self.saveFigures()

        prevYview = self.getY()
        self.prevPos = prevYview
        self.prevPosition = prevYview

    def onExtraImDelete(self, subsection, imIdx, eImIdx):
        pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                wf.Wr.MenuManagers.PdfReadersManager)
        pdfReadersManager.show(changePrevPos = False, removePrevLabel = True, 
                                subsection = subsection, imIdx = imIdx,
                                extraImIdx = str(eImIdx),
                                withoutRender = True)  

    def getShownPagesList(self):
        return [int(i.pageNum) for i in self.displayedPdfPages]

    def onFullEntryMove(self):
        pass
        #NOTE: we disable this for now since it creates two much movement on the pdf widget
        # if fsf.Data.Book.entryImOpenInTOC_UI != _u.Token.NotDef.str_t:
        #     pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
        #                                             wf.Wr.MenuManagers.PdfReadersManager)
        #     pdfReadersManager.moveToEntry(fsf.Data.Book.subsectionOpenInTOC_UI, 
        #                                 fsf.Data.Book.entryImOpenInTOC_UI,
        #                                 None)

    def onCopyTextToMem(self, subsection, imIdx):
         dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                        wf.Wr.MenuManagers.PdfReadersManager).show(subsection = subsection,
                                                                    imIdx = imIdx,
                                                                    selector = True,
                                                                    getTextOfSelector = True, 
                                                                    withoutRender = True)

    def onEntryDelete(self, subsection, imIdx):
        pdfReaderManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.PdfReadersManager)
        pdfReaderManager.removeLabel(subsection, imIdx, None)
    
    def onRetakeBefore(self, subsection, imIdx):
        dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                            wf.Wr.MenuManagers.PdfReadersManager).show(subsection = subsection,
                                                                        imIdx = imIdx,
                                                                        selector = True,
                                                                        removePrevLabel = True,
                                                                        withoutRender = True)

class SubsectionSummaryLink:
    def __init__(self, text, subsection, imIdx):
        self.text = text
        self.subsection = subsection
        self.imIdx = imIdx


class SubsectionSummaryText(ww.currUIImpl.MultilineText):
    def __init__(self, rootWidget):
        self.row = 1
        self.column = 0

        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : self.column, "row" : self.row, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NE}
        }

        extraOptions = {
            ww.Data.GeneralProperties_ID :{"width" : 300, "height" : 300},
            ww.TkWidgets.__name__ : {}
        }
        
        self.subsection = None
        self.name = "_subsectionSummary_"

        super().__init__(prefix = "", 
                         name = self.name, 
                         rootWidget = rootWidget, 
                         renderData = renderData,
                         extraOptions = extraOptions,
                         text = "",
                         width = 100,
                         height = 8)

        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdshv],
                    [self.__pasteLink])


    def __pasteLink(self, widget):
        link = f"[{dt.UITemp.Link.imIdx}|{dt.UITemp.Link.subsection}:{dt.UITemp.Link.imIdx}]"
        widget.addTextAtCurrent(link)

    def changeText(self, newText):
        self.updateText(newText)
        self.setData(newText)

    def updateLabel(self):
        newText = fsf.Data.Sec.subsectionSummaryText(self.subsection)

        newTextList = re.split(r"(\[[^\|]*\|[^\]]*\])", newText)

        links = []

        for i in range(len(newTextList)):
            if len (newTextList[i]) > 0:
                if newTextList[i][0] == "[":
                    links.append(newTextList[i])
                    newTextList[i] = "[" + newTextList[i].split("|")[1][:-1] + "]"

        newText = "".join(newTextList)

        self.changeText(newText)

        def moveToEntry(ppath):
            imIdx = ppath.split(":")[-1]
            subsection = ppath.split(":")[0]

            if subsection != fsf.Data.Book.subsectionOpenInTOC_UI:
                fsf.Data.Book.subsectionOpenInTOC_UI = subsection

                for w in wd.Data.Reactors.entryChangeReactors.values():
                    if "onSubsectionOpen" in dir(w):
                        w.onSubsectionOpen(subsection)

            fsf.Data.Book.entryImOpenInTOC_UI = imIdx

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onFullEntryMove" in dir(w):
                    w.onFullEntryMove()


        for l in links:
            text = "[" + l.split("|")[1][:-1] + "]"
            path = l.split("|")[1][:-1]
            self.makeLink(text, lambda p = path, *args: moveToEntry(p))

    def __makeLockable(self):
        def __getText(widget):
            return fsf.Data.Sec.subsectionSummaryText(self.subsection)

        def __setText(newText, widget):
            fsf.Data.Sec.subsectionSummaryText(self.subsection, newText)
        
        def __changeOnEtrFunc(widget):
            pass
        
        def __changeOnLabelBackFunc(widget):
            pass

        self.rebind([ww.currUIImpl.Data.BindID.mouse2],
                        [lambda e, g = __getText, 
                                    s = __setText, 
                                    c = __changeOnEtrFunc, 
                                    b = __changeOnLabelBackFunc, 
                                    pl = self.__pasteLink, *args:
                                                    uw.bindWidgetTextUpdatable(e, g, s, 
                                                        changeOnEtrFunc = c,
                                                        changeOnLabelBackFunc = b,
                                                        etrWidth = 100,
                                                        etrHeight = 8,
                                                        pasteLambda = self.__pasteLink)])

    def render(self):
        super().render(self.renderData)

        self.updateLabel()
        self.makeUneditable()
        self.__makeLockable()

class SecondaryImagesFrame(ww.currUIImpl.Frame):
    def __init__(self, rootWidget):
        name = "_SecondaryImagesFrame_"
        self.subsection = None
        self.imIdx = None
        self.secondWidgetFrameFrame = None
        self.mainTOCWidget = None

        self.secondImFrames = set()

        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 0, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NE}
        }
        super().__init__("", name, rootWidget, renderData = renderData)

    def addSecondaryFrame(self, subsection, imIdx):
        self.secondImFrames.add(subsection +  "_" + str(imIdx))
        self.subsection = subsection
        self.imIdx = str(imIdx)

    def receiveNotification(self, broadcasterType, data = None):
        if data != None:
            if data[0]:
                self.secondWidgetFrameFrame.destroy()
                self.secondWidgetFrameFrame = self.__addSecondaryFrameWidget(self.subsection, self.imIdx)
                self.secondWidgetFrameFrame.render()
        else:
            self.update()
            newHeight = self.getHeight()
            self.notify(PfdReader_BOX, data = [newHeight])

    def __addSecondaryFrameSelector(self):
        seclectorFrameRenderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 1, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NE}
        }

        seclectorFrame = ww.currUIImpl.Frame("_SelectorFrame_", self.name, self, seclectorFrameRenderData)

        column = 0
        for k in self.secondImFrames:
            label = SecondaryImageFrameNameLabel(seclectorFrame, 
                                     k.replace(".", "") + "selectorLabel",
                                     0,
                                     column,
                                     text = "   " + k + "   ")
            shouldBeBrown = k == (str(self.subsection) + "_" + str(self.imIdx))
            _ucomw.bindChangeColorOnInAndOut(label, shouldBeBrown = shouldBeBrown)
            if shouldBeBrown:
                label.changeColor("brown")
            column += 1
            label.render()
            label.subsection = k.split("_")[0]
            label.imIdx = k.split("_")[1]

            def __showLabel(label):
                if (str(label.subsection) == str(self.subsection))\
                    and (str(label.imIdx) == str(self.imIdx)):
                    self.subsection = None
                    self.imIdx = None
                else:
                    self.subsection = str(label.subsection)
                    self.imIdx = str(label.imIdx)
                self.render()

            label.rebind([ww.currUIImpl.Data.BindID.mouse1],
                         [lambda e, l = label, *args: __showLabel(l)])
            
            def __deleteLabel(label):
                self.secondImFrames.remove(label.subsection + "_" + label.imIdx)
                if (self.subsection == label.subsection)\
                    and (label.imIdx == self.imIdx):
                    self.subsection = None
                    self.imIdx = None
                self.render()

            label.rebind([ww.currUIImpl.Data.BindID.mouse2],
                         [lambda e, l = label, *args: __deleteLabel(l)])
        return seclectorFrame
    
    def __addSecondaryFrameWidget(self, subsection, imIdx):
        seconEntryWidgetFrameRenderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 0, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NE}
        }
        
        secondWidgetFrameFrame = ww.currUIImpl.Frame("_SecondWidgetFrame_", self.name, 
                                                     self, seconEntryWidgetFrameRenderData)

        prefix = "seconadaryFrameLabel_" + subsection.replace(".", "") +  "_" + str(imIdx)
        entryWidget = SecondaryEntryBox(secondWidgetFrameFrame, prefix)

        entryWidget.subsection = subsection
        entryWidget.imIdx = imIdx
        entryWidget.render()
        entryWidget.addListenerWidget(self)
        return secondWidgetFrameFrame
    
    def render(self):
        wd.Data.Reactors.entryChangeReactors[self.name] = self

        for ch in self.getChildren().copy():
            ch.destroy()

        frameSelector = self.__addSecondaryFrameSelector()
        frameSelector.render()

        if (self.subsection != None) and (self.imIdx != None):
            self.secondWidgetFrameFrame = self.__addSecondaryFrameWidget(self.subsection, self.imIdx)
            self.secondWidgetFrameFrame.render()
        
        super().render(self.renderData)

        newHeight = self.getHeight()
        self.notify(PfdReader_BOX, data = [newHeight])

    def onSecondaryImageOpen(self, subsection, imIdx):
        pdfMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                                wf.Wr.MenuManagers.PdfReadersManager)
        pdfMenuManager.addSecondaryFrame(subsection, imIdx)

class SecondaryEntryBox(comw.EntryWindow_BOX):
    def onExtraImDelete(self, subsection, imIdx, eImIdx):
        if (subsection == self.subsection) and (imIdx == self.imIdx):
            if self.entryManager != None:
                etm = self.entryManager
                etm.deleteExtraImage(eImIdx)

    def onMainLatexImageUpdate(self, subsection, imIdx):
        if (subsection == self.subsection) and (imIdx == self.imIdx):
            if self.entryManager != None:
                etm = self.entryManager
                etm.updateEntryImage()

    def onExtraImMove(self, subsection, imIdx, eImIdx, moveUp:bool):
        if (subsection == self.subsection) and (imIdx == self.imIdx):
            if self.entryManager != None:
                etm = self.entryManager
                eImFrame = etm.moveExtraIm(eImIdx, moveUp)

                if eImFrame != None:
                    self.shouldScroll = True
                    self.scrollIntoView(None, eImFrame)

    def onAlwaysShowChange(self, subsection, imIdx):
        if (subsection == self.subsection) and (imIdx == self.imIdx):
            if self.entryManager != None:
                for ch in self.entryManager.rowFrame2.getChildren():
                    ch.render()

    def onAlwaysShowChange(self, subsection, imIdx):
        if (subsection == self.subsection) and (imIdx == self.imIdx):
            if self.entryManager != None:
                self.entryManager.rowFrame1.hide()
                self.entryManager.rowFrame1.render()

    def onImageResize(self, subsection, imIdx, eImIdx):
        if (subsection == self.subsection) and (imIdx == self.imIdx):
            if self.entryManager != None:
                if eImIdx == None:
                    self.entryManager.updateMainImage()
                else:
                    self.entryManager.updateExtraImage(eImIdx)
                self.entryManager.updateResizeEtrText()

    def onRetakeAfter(self, subsection, imIdx, eImidx = _u.Token.NotDef.str_t):
        if (subsection == self.subsection) and (imIdx == self.imIdx):
            if self.entryManager != None:
                self.entryManager.updateMainImage()

    def render(self, scrollTOC=True):
        wd.Data.Reactors.entryChangeReactors[self.name] = self
        super().render(scrollTOC)

class PdfReadersRoot(ww.currUIImpl.Frame):
    def __init__(self, rootWidget, topLevelFrameId, width, height):
        self.pageLbl = None
        self.pdfBox = None

        self.topLevelFrameId = topLevelFrameId

        name = "_PdfReadersRoot_"
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 0, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NE}
        }
        extraOptions = {
            ww.Data.GeneralProperties_ID :{"width" : width, "height" : height},
            ww.TkWidgets.__name__ : {}
        }
        super().__init__("", name, rootWidget, renderData = renderData, extraOptions = extraOptions)


        def __atsrAddingCmd():
            self.pdfBox.updateScrollerPosition()
            mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.startAddingTheEntry()
            self.pdfBox.getIntoDrawingMode()

            def __cmdAfterImageCreated(self):
                subsection = fsf.Data.Book.subsectionOpenInTOC_UI
                numImages = len(list(fsf.Data.Sec.imLinkDict(subsection).keys()))
                timer = 0
                keys = list(fsf.Data.Sec.imLinkDict(subsection).copy().keys())
                defValPresent = _u.Token.NotDef.str_t in keys

                while numImages >= len(keys):
                    time.sleep(0.3)
                    timer += 1


                    if timer > 500:
                        break
                    if (_u.Token.NotDef.str_t in keys) != defValPresent:
                        break

                    keys = list(fsf.Data.Sec.imLinkDict(subsection).copy().keys())

                topFrame = wm.UI_generalManager.topLevelFrames[self.topLevelFrameId]
                topFrame.forceFocus()
            
            t = Thread(target = __cmdAfterImageCreated, args = [self])
            t.start()

        def __changePage(increase):
            if increase:
                newPage = int(self.pdfBox.currPage) + 1
            else:
                newPage = int(self.pdfBox.currPage) - 1
            self.pageLbl.changePage(increase)
            
            origMatName = fsf.Data.Book.currOrigMatName
            fsf.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(origMatName, newPage)
            self.pdfBox.moveToCurrPage()
            self.pdfBox.updateScrollerPosition()
            self.forceFocus()

        def __changePositionUp(*args):
            self.pageLbl.changePage(False, None, True)
            self.forceFocus()

        def __changePositionDown(*args):
            self.pageLbl.changePage(True, None, True)
            self.forceFocus()

        def runCmdAndForce(cmd, *args):
            cmd(*args)

            topFrame = wm.UI_generalManager.topLevelFrames[self.topLevelFrameId]
            topFrame.forceFocus()

        def __bind(*args):
            topFrame = wm.UI_generalManager.topLevelFrames[self.topLevelFrameId]
            
            topFrame.rebind([ww.currUIImpl.Data.BindID.Keys.left], 
                        [lambda e, *args:runCmdAndForce(__changePositionUp)])
            topFrame.rebind([ww.currUIImpl.Data.BindID.Keys.right], 
                        [lambda e, *args: runCmdAndForce(__changePositionDown)])
            topFrame.rebind([ww.currUIImpl.Data.BindID.Keys.shleft], 
                        [lambda *args: runCmdAndForce(__changePage, False)])
            topFrame.rebind([ww.currUIImpl.Data.BindID.Keys.shright], 
                        [lambda *args: runCmdAndForce(__changePage, True)])
            topFrame.rebind([ww.currUIImpl.Data.BindID.Keys.up],
                        [lambda *args: runCmdAndForce(self.pdfBox.scrollY, -1)])
            topFrame.rebind([ww.currUIImpl.Data.BindID.Keys.down],
                        [lambda *args: runCmdAndForce(self.pdfBox.scrollY, 1)])
            topFrame.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                        [lambda *args: __atsrAddingCmd()])

        def __nunbind(*args):
            topFrame = wm.UI_generalManager.topLevelFrames[self.topLevelFrameId]
            
            topFrame.unbind([ww.currUIImpl.Data.BindID.Keys.left,
                            ww.currUIImpl.Data.BindID.Keys.shleft,
                            ww.currUIImpl.Data.BindID.Keys.up,
                            ww.currUIImpl.Data.BindID.Keys.down,
                            ww.currUIImpl.Data.BindID.Keys.right,
                            ww.currUIImpl.Data.BindID.Keys.shright,
                            ww.currUIImpl.Data.BindID.Keys.shenter,
                        ])

        topFrame = wm.UI_generalManager.topLevelFrames[self.topLevelFrameId]
        
        topFrame.rebind([ww.currUIImpl.Data.BindID.focusIn,
                     ww.currUIImpl.Data.BindID.focusOut],
                    [__bind,
                     __nunbind])

        topFrame.rebind([ww.currUIImpl.Data.BindID.enterWidget],
                    [lambda *args: topFrame.forceFocus()])

        self.render()

    def __nunbind(self, *args):
        self.unbind([ww.currUIImpl.Data.BindID.Keys.left,
                        ww.currUIImpl.Data.BindID.Keys.shleft,
                        ww.currUIImpl.Data.BindID.Keys.up,
                        ww.currUIImpl.Data.BindID.Keys.down,
                        ww.currUIImpl.Data.BindID.Keys.right,
                        ww.currUIImpl.Data.BindID.Keys.shright,
                        ww.currUIImpl.Data.BindID.Keys.shenter,
                    ])

    def unbindAll(self):
        self.__nunbind()

