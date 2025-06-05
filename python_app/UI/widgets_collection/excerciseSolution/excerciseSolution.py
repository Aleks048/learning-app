import time
from PIL import Image, ImageGrab
import os

import UI.widgets_wrappers as ww
import UI.widgets_facade as wf
import UI.widgets_collection.utils as _ucomw
import UI.widgets_collection.common as comw

import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import data.constants as dc
import file_system.file_system_facade as fsf
import settings.facade as sf
import outside_calls.outside_calls_facade as ocf
import data.temp as dt


class SolutionsLabel(comw.TOCLabelWithClick):
    def __init__(self, root, prefix, row, column, 
                 columnspan=1, sticky=ww.currUIImpl.Orientation.NW, 
                 padding=[0, 0, 0, 0], image=None, text=None):
        self.subsection = None
        self.imIdx = None
        self.solImIdx = None

        super().__init__(root, prefix, 
                         row, column, columnspan, 
                         sticky, padding, image, text)

class ExcerciseSolutionImageLabel(ww.currUIImpl.Label):
    def __init__(self, root, prefix, subsection, imIdx, solutionIdx,
                 text = _u.Token.NotDef.str_t, padding = [0, 0, 0, 0], row = 0, column = 0):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }

        name = "_ExcerciseSolutionImageLabel_"

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
            self.image = ww.currUIImpl.UIImage(pilIm)
            return super().__init__(prefix, name, root, renderData, image = self.image, padding = padding)
        else:
            return super().__init__(prefix, name, root, renderData, padding = padding)

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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.W}
        }
        name = "_ExcerciseSolutionLabel_LBL"
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data,
                        height = 720)

    def hide(self, **kwargs):
        for l in self.labels:
            l.hide()

        return super().hide(**kwargs)

    def render(self):
        self.addSolutionWidgets()

        return super().render(self.renderData)

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
                                            padding = [0, 0, 0, 0],
                                            row = i + 2, column = 2)
                label.render()
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
                label.rebind([ww.currUIImpl.Data.BindID.mouse1], [__openSolimage])

                # '''
                # delete
                # '''
                deleteLabel = SolutionsLabel(self.scrollable_frame, f"_deleteNote_{solIdx}", 
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
                        l.hide()

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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
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