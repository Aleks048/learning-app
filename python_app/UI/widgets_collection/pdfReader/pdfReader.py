from tkinter import ttk
import fitz
from PIL import Image
from threading import Thread
import time
import io

import UI.widgets_wrappers as ww
import UI.widgets_facade as wf
import UI.widgets_collection.utils as _ucomw
import UI.widgets_data as wd
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import data.constants as dc
import file_system.file_system_facade as fsf
import settings.facade as sf
import outside_calls.outside_calls_facade as ocf
import data.temp as dt

def _rebuildNote(*args, **kwargs):
    '''
        used for multithreaded note rebuild
    '''
    t = Thread(target= fsf.Wr.EntryInfoStructure.rebuildNote, 
            args = (args))
    t.start()
    return t


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
        self.imLabel = _ucomw.TOCCanvasWithclick(root = self, imIdx =  None, subsection = None,
                                        prefix = f"_PdfImage_LBLim_{self.row}", 
                                        image = img, padding = [0, 0, 0, 0],
                                        row = 1, column = 1, columnspan = 1,
                                        extraImIdx = _u.Token.NotDef.int_t,
                                        makeDrawable = True, isPdfPage = True, page = self.pageNum, 
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
                                                          wf.Wr.MenuManagers.MathMenuManager)
        mainManager.moveTocToEntry(self.subsection, self.imIdx)

class HidePdfReaderWindow_BTN(ww.currUIImpl.Button,
                              dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        self.subsection = None
        self.imIdx = None

        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        text = "Hide"
        name = "_HidePdfReaderWindow_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        pdfReaderManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.PdfReadersManager)
        pdfReaderManager.hide()

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
            self.increaseLabel = _ucomw.TOCLabelWithClick(self, "_ResizePDF_BTNincreaseSize", 
                                    row = 0, column = 0, text = "+")
        if self.decreaseLabel == None:
            self.decreaseLabel = _ucomw.TOCLabelWithClick(self, "_ResizePDF_BTNDecreaseSize", 
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
            self.increasePage = _ucomw.TOCLabelWithClick(self.rootWidget, "_ResizePDF_BTNNextIm", 
                                    row = self.row, column = self.column + 1, text = ">")
        if self.decreasePage == None:
            self.decreasePage = _ucomw.TOCLabelWithClick(self.rootWidget, "_ResizePDF_BTNPrevIm", 
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
    def __init__(self, parentWidget, prefix, windth = 700, height = 800):
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
                         width = windth,
                         makeScrollable = True)

        filePath =fsf.Wr.OriginalMaterialStructure.getMaterialPath(fsf.Data.Book.currOrigMatName)
        self.doc = fitz.open(filePath)

        def on_vertical(event):
            self.scrollY(-1 * event.delta)

        self.rebind(['<Mod1-MouseWheel>'], [on_vertical])

    def __scrollIntoView(self, event, widget = None):
        posy = 0

        if widget == None:
            pwidget = event.widget
        else:
            pwidget = widget

        self.scrollY(-100)
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
        self.render()

        entryWidget = self.displayedPdfPages[2].imLabel.getEntryWidget(subsection, 
                                                                       imIdx,
                                                                       eImIdx)
        if entryWidget != None:
            self.__scrollIntoView(None, entryWidget.label)

    def addPdfPages(self):
        '''
        for page in the pdf:
        '''
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

    def render(self, force = False):
        self.updateOMpage(force = force)
        self.currPage = int(self.currPage)

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
        if broadcasterType == ResizePdfReaderWindow_BTN:
            if data != None:
                for p in self.displayedPdfPages:
                    p.imLabel.saveFigures()
            else:
                origMatName = fsf.Data.Book.currOrigMatName
                zoomLevel = int(fsf.Wr.OriginalMaterialStructure.getMaterialZoomLevel(origMatName))
                self.pageWidth = zoomLevel

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

            self.render()
            self.moveY(prevYview)

    def updateScrollerPosition(self):
        self.saveFigures()

        prevYview = self.getY()
        self.prevPos = prevYview
        self.prevPosition = prevYview

class PdfReadersRoot(ww.currUIImpl.Frame):

    def __init__(self, rootWidget, width, height):
        self.pageLbl = None
        self.pdfBox = None

        name = "_PdfReadersRoot_"
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 0, "rowspan": 20},
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


                self.forceFocus()
            
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

        def __bind(*args):
            self.rebind([ww.currUIImpl.Data.BindID.Keys.left], 
                        [lambda e, *args: __changePositionUp()])
            self.rebind([ww.currUIImpl.Data.BindID.Keys.right], 
                        [lambda e, *args: __changePositionDown()])
            self.rebind([ww.currUIImpl.Data.BindID.Keys.shleft], 
                        [lambda *args: __changePage(False)])
            self.rebind([ww.currUIImpl.Data.BindID.Keys.shright], 
                        [lambda *args: __changePage(True)])
            self.rebind([ww.currUIImpl.Data.BindID.Keys.up],
                        [lambda *args: self.pdfBox.scrollY(-1)])
            self.rebind([ww.currUIImpl.Data.BindID.Keys.down],
                        [lambda *args: self.pdfBox.scrollY(1)])
            self.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                        [lambda *args: __atsrAddingCmd()])

        def __nunbind(*args):
            self.unbind([ww.currUIImpl.Data.BindID.Keys.left,
                            ww.currUIImpl.Data.BindID.Keys.shleft,
                            ww.currUIImpl.Data.BindID.Keys.up,
                            ww.currUIImpl.Data.BindID.Keys.down,
                            ww.currUIImpl.Data.BindID.Keys.right,
                            ww.currUIImpl.Data.BindID.Keys.shright,
                            ww.currUIImpl.Data.BindID.Keys.shenter,
                        ])

        self.rebind([ww.currUIImpl.Data.BindID.focusIn,
                     ww.currUIImpl.Data.BindID.focusOut],
                    [__bind,
                     __nunbind])
        self.rebind([ww.currUIImpl.Data.BindID.enterWidget],
                    [lambda *args: self.forceFocus()])

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

