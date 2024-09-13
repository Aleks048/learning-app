import tkinter as tk
from tkinter import ttk
import Pmw
from PIL import Image, ImageTk
from threading import Thread
import os
import time

import UI.widgets_wrappers as ww
import UI.widgets_facade as wf
import UI.widgets_collection.utils as _ucomw
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import data.constants as dc
import file_system.file_system_facade as fsf
import settings.facade as sf
import outside_calls.outside_calls_facade as ocf
import data.temp as dt

images = []


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
        self.noteImIdx = None
        self.image = None

        self.noteImIdx = str(noteIdx)

        bookName = sf.Wr.Manager.Book.getCurrBookName()

        imagePath = _upan.Paths.Entry.NoteImage.getAbs(bookName, subsection, imIdx, noteIdx)

        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
            imagePath = _upan.Paths.Entry.NoteImage.getAbs(bookName, subsection, imIdx, -1)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                notesPath = _upan.Paths.Entry.getAbs(bookName, subsection, imIdx)
                filename = _upan.Names.Entry.Note.name(imIdx, noteIdx)
                notesPath = os.path.join(notesPath, filename)
                if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(notesPath):
                    fsf.Wr.EntryInfoStructure.rebuildNote(subsection, imIdx, -1, "-1", bookName)
                else:
                    text = "\"No notes yet\""

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

            try:
                self.currEtr.focus_force()
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
            text = ""

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
            
            imagesManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.ImagesManager)
            appDimensions = imagesManager.appDimensions
            appDimensions[1] -= imagesManager.notesImDimensions

            if self.noteShownIntext:
                text = self.currEtr.getData()
                nLines = len(text.split("\n"))

                appDimensions[1] += nLines * 35
                imagesManager.notesImDimensions = nLines * 35
            
            imagesManager.show(appDimensions, self.eImIdx, imagesManager.notesImDimensions)

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

                notesIm = _upan.Paths.Entry.NoteImage.getAbs(bookPath,
                                                event.widget.subsection,
                                                event.widget.imIdx,
                                                event.widget.noteImIdx)

                ocf.Wr.FsAppCalls.deleteFile(notesIm)

                self.__renderAfterRebuild(self.subsection,
                            self.imIdx,
                            event.widget.noteImIdx,
                            text,
                            bookPath,
                            noteIdx = widgetnoteImIdx)

                self.noteShownIntext = False

                imagesManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                            wf.Wr.MenuManagers.ImagesManager)
                appDimensions = imagesManager.appDimensions
                appDimensions[1] -= imagesManager.notesImDimensions
   
                while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(notesIm):
                    time.sleep(0.1)

                im = Image.open(notesIm)
                _, imHeight = im.size
                imagesManager.notesImDimensions = imHeight
                appDimensions[1] += imagesManager.notesImDimensions
                
                imagesManager.show(appDimensions, self.eImIdx, imagesManager.notesImDimensions)

                return "break"

            labETR.noteImIdx = noteImIdx
            labETR.subsection = self.subsection
            labETR.imIdx = self.imIdx
            labETR.eImIdx = self.eImIdx
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

class ImageMainImage(ww.currUIImpl.Frame):
    def __init__(self, parentWidget, prefix):
        self.displayedImages = []
        self.subsection = None
        self.entryIdx = None
        self.extraWidgetIdx = _u.Token.NotDef.int_t
        self.imLabel = None

        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0, "columnspan": 6},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_imageMainImage_LBL"

        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data)

    def hide(self, **kwargs):
        if self.imLabel != None:
            for l in self.imLabel.winfo_children():
                if type(l) == _ucomw.TOCCanvasWithclick:
                    l.saveFigures()
        return super().hide(**kwargs)    

    def render(self, **kwargs):     
        # get an image from the
        widget = self.widgetObj

        for child in widget.winfo_children():
            child.destroy()

        balloon = Pmw.Balloon(widget)

        if self.extraWidgetIdx == _u.Token.NotDef.int_t:
            self.imLabel = _ucomw.addMainEntryImageWidget(widget, 
                                                        self.subsection, self.entryIdx,
                                                        0, self.displayedImages, balloon,
                                                        bindOpenWindow = False,
                                                        resizeFactor = 1.5)
        else:
            self.imLabel = _ucomw.addExtraEntryImagesWidgets(widget, 
                                                        self.subsection, self.entryIdx,
                                                        0, self.displayedImages, balloon,
                                                        createExtraWidgets = False,
                                                        bindOpenWindow = False,
                                                        resizeFactor = 1.5)[self.extraWidgetIdx]
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

class HideImagesWindow_BTN(ww.currUIImpl.Button,
                              dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        self.subsection = None
        self.imIdx = None

        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Hide"
        name = "_HideImagesWindow_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        imagesManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.ImagesManager)
        imagesManager.hide()

        excerciseManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.ExcerciseManager)
        if excerciseManager.shown:
            excerciseManager.show()

class ImagesRoot(ww.currUIImpl.RootWidget):
    hideWidget = None
    
    def __init__(self, width, height):

        super().__init__(width, height)
    
        def __bind(*args):
            self.widgetObj.bind_all(ww.currUIImpl.Data.BindID.Keys.escape, 
                                    lambda *args: self.hideWidget.cmd())
        def __nunbind(*args):
            self.widgetObj.unbind_all(ww.currUIImpl.Data.BindID.Keys.escape)

        self.widgetObj.bind("<Enter>", __bind, add = True)
        self.widgetObj.bind("<Leave>", __nunbind, add = True)