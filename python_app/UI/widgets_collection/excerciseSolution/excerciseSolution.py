import tkinter as tk
from tkinter import ttk
import time
from PIL import Image, ImageTk, ImageGrab
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

class ExcerciseSolutionImageLabel(ttk.Label):
    def __init__(self, root, name, subsection, imIdx, solutionIdx,
                 text = _u.Token.NotDef.str_t, padding = [0, 0, 0, 0]):
        self.image = None
        self.solImIdx = solutionIdx
        self.subsection = subsection
        self.imIdx = imIdx

        bookName = sf.Wr.Manager.Book.getCurrBookName()

        imagePath = _upan.Paths.Entry.SolutionImage.getAbs(bookName, 
                                                           subsection, 
                                                           imIdx,
                                                           solutionIdx)

        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
            text = "\"No solution yet\""

        if text == _u.Token.NotDef.str_t:
            pilIm = Image.open(imagePath)
            pilIm.thumbnail([530, 1000], Image.LANCZOS)
            img = ImageTk.PhotoImage(pilIm)
            self.image = img
            return super().__init__(root, name = name, image = img, padding = padding)
        else:
            return super().__init__(root, name = name, text = text, padding = padding)

class ExcerciseSolutionLabel(ww.currUIImpl.ScrollableBox,
                 dc.AppCurrDataAccessToken):
    def __init__(self, parentWidget, prefix):
        self.subsection = None
        self.imIdx = None
        self.imLabel = None
        self.lineIdx = None
        self.labels = []

        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 3, "columnspan": 3},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_ExcerciseSolutionLabel_LBL"
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data,
                        height = 720)

    def hide(self, **kwargs):
        for l in self.labels:
            l.grid_forget()

        return super().hide(**kwargs)

    def render(self, widjetObj=None, renderData=..., **kwargs):
        self.addSolutionWidgets()

        return super().render(**kwargs)

    def addSolutionWidgets(self):
        # image
        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        subsection = self.subsection
        imIdx = self.imIdx

        entryFSpath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryFSpath):
            solutionsNameToken = _upan.Names.Entry.Solution.solutionImgToken
            solutions = [i for i in os.listdir(entryFSpath) if solutionsNameToken in i]
            solutionsIndicies = [".".join(i.replace(solutionsNameToken, "").split(".")[:-1])\
                                  for i in solutions]

            for i in range(len(solutionsIndicies)):
                solIdx = solutionsIndicies[i]
                label = ExcerciseSolutionImageLabel(self.scrollable_frame, f"lineSolutionImageIMG_{solIdx}", 
                                            self.subsection, self.imIdx, solIdx,
                                            padding = [0, 0, 0, 0])
                label.grid(row = i + 2, column = 2, sticky = tk.NW)
                self.labels.append(label)
                self.imLabel = label
                def __openSolimage(event):
                    w = event.widget
                    bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                    ocf.Wr.FsAppCalls.openFile(_upan.Paths.Entry.SolutionImage.getAbs(bookPath,
                                                                                      w.subsection, 
                                                                                      w.imIdx,
                                                                                      w.solImIdx
                                                                                      ))
                label.bind(ww.currUIImpl.Data.BindID.mouse1, __openSolimage)

                # '''
                # delete
                # '''
                deleteLabel = _ucomw.TOCLabelWithClick(self.scrollable_frame, f"_deleteNote_{solIdx}", 
                                                        i + 2, 1, text = "Del")
                deleteLabel.subsection = self.subsection
                deleteLabel.imIdx = self.imIdx
                deleteLabel.solImIdx = solIdx

                def deleteNoteIdx(event, *args):
                    w = event.widget
                    bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                    
                    ocf.Wr.FsAppCalls.deleteFile(_upan.Paths.Entry.SolutionImage.getAbs(bookPath,
                                                                                        w.subsection,
                                                                                        w.imIdx,
                                                                                        w.solImIdx))
                    for l in self.labels:
                        l.grid_forget()

                    self.render()

                deleteLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [deleteNoteIdx])
                self.labels.append(deleteLabel)
                _ucomw.bindChangeColorOnInAndOut(deleteLabel)
                deleteLabel.render()

    def receiveNotification(self, broadcasterType) -> None:
        self.render()

class HideExcerciseSolutionWindow_BTN(ww.currUIImpl.Button,
                              dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Hide"
        name = "_HidehideExcerciseSolutionWindow_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        excerciseSolutionManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.ExcerciseSolutionManager)
        excerciseSolutionManager.hide()

class AddFromClipbordExcerciseSolutionWindow_BTN(ww.currUIImpl.Button,
                              dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 1, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Add from clipboard"
        name = "_addFromclipbordExcerciseSolutionWindow_BTN_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)
        self.subsection = None
        self.imIdx = None

    def cmd(self):
        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            
        entryFSpath = _upan.Paths.Entry.getAbs(bookPath, self.subsection, self.imIdx)

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryFSpath):
            solutionsNameToken = _upan.Names.Entry.Solution.solutionImgToken
            numSolutions = len([i for i in os.listdir(entryFSpath) if solutionsNameToken in i])

            solPath = _upan.Paths.Entry.SolutionImage.getAbs(bookPath, self.subsection, self.imIdx, numSolutions)
            im = ImageGrab.grabclipboard()
            im.save(solPath,'PNG')
        
            self.notify(ExcerciseSolutionLabel)

class AddScreenshotExcerciseSolutionWindow_BTN(ww.currUIImpl.Button,
                              dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 2, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Add from screenshot"
        name = "_addFromScreenshotExcerciseSolutionWindow_BTN_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)
        self.subsection = None
        self.imIdx = None

    def cmd(self):
        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            
        entryFSpath = _upan.Paths.Entry.getAbs(bookPath, self.subsection, self.imIdx)

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryFSpath):
            solutionsNameToken = _upan.Names.Entry.Solution.solutionImgToken
            numSolutions = len([i for i in os.listdir(entryFSpath) if solutionsNameToken in i])

            solPath = _upan.Paths.Entry.SolutionImage.getAbs(bookPath, self.subsection, self.imIdx, numSolutions)
            ocf.Wr.ScreenshotCalls.takeScreenshot(solPath)

            for _ in range(100):
                if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(solPath):
                    break
                time.sleep(0.3)
        
            self.notify(ExcerciseSolutionLabel)

class ExcerciseSolutionRoot(ww.currUIImpl.RootWidget):
    pass