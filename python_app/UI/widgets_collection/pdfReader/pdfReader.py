import tkinter as tk
from tkinter import ttk
import fitz
from PIL import Image, ImageTk
from threading import Thread
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
            img = ImageTk.PhotoImage(pilIm)
            self.image = img
            return super().__init__(root, name = name, image = img, padding = padding)
        else:
            return super().__init__(root, name = name, text = text, padding = padding)

class NotesLabel(ww.currUIImpl.Label,
                 dc.AppCurrDataAccessToken):
    def __init__(self, parentWidget, prefix):
        self.subsection = None
        self.imIdx = None
        self.noteShownIntext = False
        self.currEtr = None
        self.imLabel = None
        self.eImIdx = _u.Token.NotDef.int_t


        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 3, "columnspan": 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_NotesLabel_LBL"
        text = ""
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data, 
                        text = text)

    def __renderAfterRebuild(self, *args, **kwargs):
        def __internal(*args, **kwargs):
            noteIdx = kwargs["noteIdx"]
            t = _rebuildNote(*args, **kwargs)
            t.join()
            self.render()
            position = "0.0"#self.currEtr[1]
            self.currEtr.focus_force()

            try:
                self.currEtr.mark_set("insert", position)
            except:
                pass
        Thread(target = __internal,
               args = args, 
               kwargs = kwargs).start()

    def render(self, widjetObj=None, renderData=..., **kwargs):
        self.addNotesWidgets()

        return super().render(**kwargs)

    def addNotesWidgets(self):
        addLabel = _ucomw.TOCLabelWithClick(self.widgetObj, "_addNote_", 0, 0, text = "Add")
        
        noteImIdx = str(int(self.eImIdx) + 1) if self.eImIdx != _u.Token.NotDef.int_t else 0

        addLabel.noteImIdx = noteImIdx

        def addLabelNoteIdx(event, *args):
            text = _u.Token.NotDef.str_t
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            structureCreated = fsf.Wr.EntryInfoStructure.addNote(self.subsection, self.imIdx, 
                                                                    text, bookPath, 
                                                                    position = event.widget.noteImIdx)

            if structureCreated:
                mainMathManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                            wf.Wr.MenuManagers.MathMenuManager)
                mainMathManager.moveTocToEntry(self.subsection, self.imIdx)
            
            self.render()

        addLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [addLabelNoteIdx])
        _ucomw.bindChangeColorOnInAndOut(addLabel)
        addLabel.render()

        def __showTextOrImage(event, *args):
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            widgetnoteImIdx = str(event.widget.noteImIdx)

            if self.noteShownIntext:
                text = self.currEtr.getData()

                if text != self.currEtr.defaultText:
                    _rebuildNote(self.subsection,
                                        self.imIdx,
                                        event.widget.noteImIdx,
                                        text,
                                        bookPath)

                self.currEtr.pop(widgetnoteImIdx)
            else:
                self.noteShownIntext = True

            self.render()

        # image / text
        if not self.noteShownIntext:
            if self.currEtr != None:
                self.currEtr.grid_forget()
                self.currEtr = None
            label = NotesImageLabel(self.widgetObj, "notesImageIMG_", 
                                        self.subsection, self.imIdx, noteImIdx,
                                        padding = [0, 0, 0, 0])
            label.grid(row = 0, column = 2, sticky = tk.NW)
            label.bind(ww.currUIImpl.Data.BindID.mouse2, __showTextOrImage)
            self.imLabel = label
        else:
            if self.imLabel != None:
                self.imLabel.grid_forget()
                self.imLabel = None

            label = _ucomw.TOCFrame(self.widgetObj, 
                            "notesImageFRM_",
                            0, 2, 1
                            )
            notes = fsf.Wr.EntryInfoStructure.readProperty(self.subsection,
                                                       self.imIdx, 
                                                       fsf.Wr.EntryInfoStructure.PubProp.entryNotesList)
            text = notes[str(noteImIdx)]

            labETR = _ucomw.MultilineText_ETR(label, "notesImageETR_", 0, 0, 0, text)
            self.currEtr = labETR

            def rebuildETRImage(event, *args):
                widgetnoteImIdx = event.widget.noteImIdx
                text = self.currEtr.getData()

                bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                self.__renderAfterRebuild(self.subsection,
                            self.imIdx,
                            event.widget.noteImIdx,
                            text,
                            bookPath,
                            noteIdx = widgetnoteImIdx)

                self.noteShownIntext = False

                return "break"

            labETR.noteImIdx = noteImIdx
            labETR.rebind([ww.currUIImpl.Data.BindID.Keys.shenter], [rebuildETRImage])

            labETR.render()
            label.render()


        # '''
        # delete
        # '''
        deleteLabel = _ucomw.TOCLabelWithClick(self.widgetObj, "_deleteNote_", 
                                                0, 1, text = "Del")
        deleteLabel.noteImIdx = noteImIdx

        def deleteNoteIdx(event, *args):
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            fsf.Wr.EntryInfoStructure.deleteNote(bookPath,
                                                    self.subsection,
                                                    self.imIdx,
                                                    str(event.widget.noteImIdx))
            self.currEtr = None
            self.noteShownIntext = False

            self.render()

        deleteLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [deleteNoteIdx])
        _ucomw.bindChangeColorOnInAndOut(deleteLabel)
        deleteLabel.render()

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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        self.pageWidth = pageWidth

        self.pdfDoc = pdfDoc
        self.pageNum = pageNum

        name = "_PdfImage_LBL"

        super().__init__(prefix, 
                        name,
                        parentWidget,
                        renderData = data)
    
    def render(self, **kwargs):     
        # get an image from the
        widget = self.widgetObj

        for child in widget.winfo_children():
            child.destroy()

        page = self.pdfDoc.load_page(self.pageNum)
        pixmap = page.get_pixmap(dpi = 150)
        buf = io.BytesIO(pixmap.tobytes())
        pilIm = Image.open(buf)
        pilIm = pilIm.convert('RGB')
        width, height = pilIm.size
        pilIm = pilIm.resize([self.pageWidth, int((self.pageWidth / width) * height)],
                      Image.LANCZOS)
        img = ImageTk.PhotoImage(pilIm)
        self.imLabel = _ucomw.TOCCanvasWithclick(widget, imIdx =  None, subsection = None,
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
        self.imLabel.focus_force()

        return super().render(**kwargs)

class MoveTOCtoImageEntry_BTN(ww.currUIImpl.Button,
                                  dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        self.subsection = None
        self.imIdx = None

        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 1, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
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
            self.increaseLabel = _ucomw.TOCLabelWithClick(self.widgetObj, "_ResizePDF_BTNincreaseSize", 
                                    row = 0, column = 0, text = "+")
        if self.decreaseLabel == None:
            self.decreaseLabel = _ucomw.TOCLabelWithClick(self.widgetObj, "_ResizePDF_BTNDecreaseSize", 
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

        self.increaseLabel.bind(ww.currUIImpl.Data.BindID.mouse1,
                                lambda *args: __resizeCmd(True))        
        self.decreaseLabel.bind(ww.currUIImpl.Data.BindID.mouse1,
                                lambda *args: __resizeCmd(False))        

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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
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


    def changePage(self, increase, newPage = None):
        if newPage == None:
            if increase:
                newPage = int(self.getData()) + 1
            else:
                newPage = int(self.getData()) - 1

        self.setData(newPage)
        self.currPage = newPage

        _, cmd = self.__bindCMD()
        cmd[0](increase)

    def render(self, **kwargs):
        self.setData(self.currPage)

        if self.increasePage == None:
            self.increasePage = _ucomw.TOCLabelWithClick(self.rootWidget.widjetObj, "_ResizePDF_BTNNextIm", 
                                    row = self.row, column = self.column + 1, text = ">")
        if self.decreasePage == None:
            self.decreasePage = _ucomw.TOCLabelWithClick(self.rootWidget.widjetObj, "_ResizePDF_BTNPrevIm", 
                                    row = self.row, column = self.column - 1, text = "<")
        _ucomw.bindChangeColorOnInAndOut(self.increasePage)
        _ucomw.bindChangeColorOnInAndOut(self.decreasePage)


        self.increasePage.bind(ww.currUIImpl.Data.BindID.mouse1,
                                lambda *args: self.changePage(True))        
        self.decreasePage.bind(ww.currUIImpl.Data.BindID.mouse1,
                                lambda *args: self.changePage(False))        

        self.increasePage.render()
        self.decreasePage.render()
        return super().render(**kwargs)

    def __bindCMD(self):
        def __cmd(increase = None, *args):
            pageNumStr = self.getData()
            pageNum = int(pageNumStr)

            origMatName = fsf.Data.Book.currOrigMatName
            fsf.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(origMatName, pageNum)

            if increase != None:
                self.notify(PfdReader_BOX, [increase])
            else:
                self.notify(PfdReader_BOX)

        return [ww.currUIImpl.Data.BindID.Keys.shenter], [__cmd]

class PfdReader_BOX(ww.currUIImpl.ScrollableBox,
                    dc.AppCurrDataAccessToken):
    def __init__(self, parentWidget, prefix, windth = 700, height = 750):
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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_PdfReader_BOX"

        origMatName = fsf.Data.Book.currOrigMatName
        self.currPage = int(fsf.Wr.OriginalMaterialStructure.getMaterialCurrPage(origMatName))

        self.parent = parentWidget.widgetObj

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
            self.canvas.yview_scroll(-1 * event.delta, 'units')

        self.container.bind_all('<Mod1-MouseWheel>', on_vertical)

    def __renderAfterRebuild(self, *args, **kwargs):
        def __internal(*args, **kwargs):
            noteIdx = kwargs["noteIdx"]
            t = _rebuildNote(*args, **kwargs)
            t.join()
            self.render()
            position = self.etrTexts[noteIdx][1]
            self.currEtr[noteIdx].focus_force()

            try:
                self.currEtr[noteIdx].mark_set("insert", position)
            except:
                pass
        Thread(target = __internal,
               args = args, 
               kwargs = kwargs).start()

    def __scrollIntoView(self, event, widget = None):
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
            self.canvas.yview_moveto((pos / height) - 0.008)
        except:
            pass

    def removeMainLabel(self, subsection, imIdx):
        for p in self.displayedPdfPages:
            l = p.imLabel.getEntryWidget(subsection, imIdx)
            if l != None:
                l.deleteLabel()
                break

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

    def hide(self, **kwargs):
        for im in self.displayedPdfPages:
            im.imLabel.saveFigures()

        self.prevPage = self.currPage

        if self.changePrevPos:
            self.prevPosition, _ = self.canvas.yview()
            self.prevPos = self.prevPosition

        return super().hide(**kwargs)

    def render(self, widjetObj=None, renderData=..., shouldScroll = True, **kwargs):
        if self.currPage == self.prevPage:
            if (self.prevPos != 0.0) and (self.prevPos != None):
                self.prevPosition = self.prevPos

        for im in self.displayedPdfPages:
            im.widgetObj.grid_forget()

        self.displayedPdfPages = []

        for w in self.scrollable_frame.winfo_children():
            w.grid_forget()

        self.scrollable_frame.focus_force()

        self.addPdfPages()

        super().render(widjetObj, renderData, **kwargs)

        # if (self.latestWidgetToscrollTo != None) and (shouldScroll):
        #     self.__scrollIntoView(None, self.latestWidgetToscrollTo)
        self.canvas.yview_moveto(self.prevPosition)

    def changePage(self, currPage):
        self.currPage = currPage

        self.render()

        self.canvas.yview_moveto(0.4)

    def moveToCurrPage(self):
        origMatName = fsf.Data.Book.currOrigMatName
        self.currPage = fsf.Wr.OriginalMaterialStructure.getMaterialCurrPage(origMatName)

        self.render()

        self.canvas.yview_moveto(0.4)

    def receiveNotification(self, broadcasterType, data = None) -> None:
        if broadcasterType == ResizePdfReaderWindow_BTN:
            if data != None:
                for p in self.displayedPdfPages:
                    p.imLabel.saveFigures()
            else:
                origMatName = fsf.Data.Book.currOrigMatName
                zoomLevel = int(fsf.Wr.OriginalMaterialStructure.getMaterialZoomLevel(origMatName))
                self.pageWidth = zoomLevel

                self.canvas.update()
                self.render()

            # self.container.update()
            # self.canvas.update_idletasks()
            # self.scrollbar_top.update()
            # self.scrollbar_right.update()
            # self.canvas.xview(tk.SCROLL, 100, 'page') 
            self.canvas.xview_moveto(0.06) # not perfect but should work for now
        elif broadcasterType == ChangePagePdfReaderWindow_ETR:
            origMatName = fsf.Data.Book.currOrigMatName
            self.currPage = fsf.Wr.OriginalMaterialStructure.getMaterialCurrPage(origMatName)

            self.updateScrollerPosition()
            prevYview, _ = self.canvas.yview()

            if data != None:
                if len(data) != 0:
                    increase = data[0]
                    if increase:
                        prevYview -= 0.2
                    else:
                        prevYview += 0.2

            self.render()
            self.canvas.yview_moveto(prevYview)

    def updateScrollerPosition(self):
        prevYview, _ = self.canvas.yview()
        self.prevPos = prevYview
        self.prevPosition = prevYview

class PdfReadersRoot(ww.currUIImpl.RootWidget):
    pageLbl = None
    pdfBox = None

    def __init__(self, width, height):
        super().__init__(width, height)

        def __atsrAddingCmd():
            self.pdfBox.updateScrollerPosition()
            mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.startAddingTheEntry()

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

        def __bind(*args):
            self.widgetObj.bind_all(ww.currUIImpl.Data.BindID.Keys.left, 
                                    lambda *args: self.pageLbl.changePage(False))
            self.widgetObj.bind_all(ww.currUIImpl.Data.BindID.Keys.shleft, 
                                    lambda *args: __changePage(False))
            self.widgetObj.bind_all(ww.currUIImpl.Data.BindID.Keys.shright, 
                                    lambda *args: __changePage(True))
            self.widgetObj.bind_all(ww.currUIImpl.Data.BindID.Keys.right, 
                                    lambda *args: self.pageLbl.changePage(True))
            self.widgetObj.bind_all(ww.currUIImpl.Data.BindID.Keys.up,
                                    lambda *args: self.pdfBox.canvas.yview_scroll(-1, 'units'))
            self.widgetObj.bind_all(ww.currUIImpl.Data.BindID.Keys.down,
                                    lambda *args: self.pdfBox.canvas.yview_scroll(1, 'units'))
            self.widgetObj.bind_all(ww.currUIImpl.Data.BindID.Keys.shenter,
                                    lambda *args: __atsrAddingCmd())
        def __nunbind(*args):
            self.widgetObj.unbind_all(ww.currUIImpl.Data.BindID.Keys.left)
            self.widgetObj.unbind_all(ww.currUIImpl.Data.BindID.Keys.up)
            self.widgetObj.unbind_all(ww.currUIImpl.Data.BindID.Keys.down)
            self.widgetObj.unbind_all(ww.currUIImpl.Data.BindID.Keys.right)
            self.widgetObj.unbind_all(ww.currUIImpl.Data.BindID.Keys.shenter)

        self.widgetObj.bind("<Enter>", __bind, add = True)
        self.widgetObj.bind("<Leave>", __nunbind, add = True)