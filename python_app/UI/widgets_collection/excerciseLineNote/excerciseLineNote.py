import tkinter as tk
from tkinter import ttk
import Pmw
from PIL import Image, ImageTk
from threading import Thread
import os

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

class ExcerciseLineNoteImageLabel(ttk.Label):
    def __init__(self, root, name, subsection, imIdx, 
                 lineIdx, text = _u.Token.NotDef.str_t, padding = [0, 0, 0, 0]):
        self.noteImIdx = None
        self.image = None

        self.lineIdx = str(lineIdx)

        bookName = sf.Wr.Manager.Book.getCurrBookName()

        imagePath = _upan.Paths.Entry.LineNoteImage.getAbs(bookName, subsection, 
                                                           imIdx, self.lineIdx)

        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
            text = "\"No notes yet\""

        if text == _u.Token.NotDef.str_t:
            pilIm = Image.open(imagePath)
            pilIm.thumbnail([530, 1000], Image.LANCZOS)
            img = ImageTk.PhotoImage(pilIm)
            self.image = img
            return super().__init__(root, name = name, image = img, padding = padding)
        else:
            return super().__init__(root, name = name, text = text, padding = padding)


def _rebuildLineNote(*args, **kwargs):
    '''
        used for multithreaded note rebuild
    '''
    t = Thread(target= fsf.Wr.EntryInfoStructure.rebuildLineNote, 
            args = (args))
    t.start()
    return t

class ExcerciseLineNoteLabel(ww.currUIImpl.Label,
                 dc.AppCurrDataAccessToken):
    def __init__(self, parentWidget, prefix):
        self.subsection = None
        self.imIdx = None
        self.noteShownIntext = False
        self.currEtr = None
        self.imLabel = None
        self.lineIdx = None


        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 3, "columnspan": 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_ExcerciseLineNoteLabel_LBL"
        text = ""
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data, 
                        text = text)

    def __renderAfterRebuild(self, *args, **kwargs):
        def __internal(*args, **kwargs):
            t = _rebuildLineNote(*args, **kwargs)
            t.join()
            self.render()
            position = "0.0"#self.currEtr[1]
            # self.currEtr.focus_force()

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
        # '''
        # add
        # '''
        addLabel = _ucomw.TOCLabelWithClick(self.widgetObj, "_addExcerciseLineNote_", 0, 0, text = "Add")

        def addLabelNoteIdx(event, *args):
            text = _u.Token.NotDef.str_t
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            
            fsf.Wr.EntryInfoStructure.addLineNote(self.subsection, self.imIdx, text, bookPath, self.lineIdx)
            fsf.Wr.EntryInfoStructure.rebuildLineNote(self.subsection, self.imIdx, self.lineIdx, text,bookPath)
            
            self.render()

        addLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [addLabelNoteIdx])
        _ucomw.bindChangeColorOnInAndOut(addLabel)
        addLabel.render()

        def __showTextOrImage(event, *args):
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

            if self.noteShownIntext:
                text = self.currEtr.getData()

                if text != self.currEtr.defaultText:
                    fsf.Wr.EntryInfoStructure.rebuildLineNote(self.subsection, 
                                                              self.imIdx,
                                                              self.lineIdx,
                                                              text, 
                                                              bookPath)

                self.currEtr = None
            else:
                self.noteShownIntext = True

            self.render()

        # image / text
        if not self.noteShownIntext:
            if self.currEtr != None:
                self.currEtr.grid_forget()
                self.currEtr = None
            label = ExcerciseLineNoteImageLabel(self.widgetObj, "lineNotesImageIMG_", 
                                        self.subsection, self.imIdx, self.lineIdx,
                                        padding = [0, 0, 0, 0])
            label.grid(row = 0, column = 2, sticky = tk.NW)
            label.bind(ww.currUIImpl.Data.BindID.mouse2, __showTextOrImage)
            self.imLabel = label
        else:
            if self.imLabel != None:
                self.imLabel.grid_forget()
                self.imLabel = None

            label = _ucomw.TOCFrame(self.widgetObj, 
                            "lineNotesImageFRM_",
                            0, 2, 1
                            )

            notes = fsf.Wr.EntryInfoStructure.readProperty(self.subsection,
                                                       str(self.imIdx), 
                                                       fsf.Wr.EntryInfoStructure.PubProp.entryLinesNotesList)
            text = notes[str(self.lineIdx)]

            labETR = _ucomw.MultilineText_ETR(label, "lineNotesImageETR_", 0, 0, 0, text)
            self.currEtr = labETR

            def rebuildETRImage(event, *args):
                text = self.currEtr.getData()

                bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                self.__renderAfterRebuild(self.subsection, 
                                          self.imIdx,
                                          self.lineIdx,
                                          text, 
                                          bookPath)

                self.noteShownIntext = False

                return "break"

            labETR.lineImIdx = self.lineIdx
            labETR.rebind([ww.currUIImpl.Data.BindID.Keys.shenter], [rebuildETRImage])

            labETR.render()
            label.render()


        # '''
        # delete
        # '''
        deleteLabel = _ucomw.TOCLabelWithClick(self.widgetObj, "_deleteNote_", 
                                                0, 1, text = "Del")

        def deleteNoteIdx(event, *args):
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            
            fsf.Wr.EntryInfoStructure.deleteLineNote(bookPath, self.subsection, self.imIdx, self.lineIdx)
            self.currEtr = None
            self.noteShownIntext = False

            self.render()

        deleteLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [deleteNoteIdx])
        _ucomw.bindChangeColorOnInAndOut(deleteLabel)
        deleteLabel.render()

class ExcerciseLineNoteLineImage(ww.currUIImpl.Frame):
    def __init__(self, parentWidget, prefix):
        self.displayedImages = []
        self.subsection = None
        self.imIdx = None
        self.lineIdx = None
        self.imLabel = None
        self.pilIm = None

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
        return super().hide(**kwargs)    

    def render(self, **kwargs):
        bookName = sf.Wr.Manager.Book.getCurrBookName()
        imagePath = _upan.Paths.Entry.LineImage.getAbs(bookName, 
                                                       self.subsection, 
                                                       self.imIdx, 
                                                       self.lineIdx)

        pilIm = Image.open(imagePath)
        pilIm.thumbnail([530, 1000], Image.LANCZOS)
        img = ImageTk.PhotoImage(pilIm) 
        self.pilIm = img
        self.imLabel = _ucomw.TOCLabelWithClick(self.widgetObj,
                                                "_lineMainImage_",
                                                0, 0, 1,
                                                image = img)

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

class HideExcerciseLineNoteWindow_BTN(ww.currUIImpl.Button,
                              dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Hide"
        name = "_HidehideExcerciseLineNoteWindow_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        excerciseLineNoteManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.ExcerciseLineNoteManager)
        excerciseLineNoteManager.hide()

class ExcerciseLineNoteRoot(ww.currUIImpl.RootWidget):
    pass