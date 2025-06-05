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


class ExcerciseExtraLabelWithClick(comw.ExcerciseLabel):
    pass

class ExcerciseExtraImageLabel(ww.currUIImpl.Label):
    def __init__(self, root, prefix, subsection, imIdx, extraIdx,
                 text = _u.Token.NotDef.str_t, padding = [0, 0, 0, 0],
                 row = 0, column = 0):
        
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }

        name = "_ExcerciseExtraImageLabel_"

        self.image = None
        self.solImIdx = extraIdx
        self.subsection = subsection
        self.imIdx = imIdx

        bookName = sf.Wr.Manager.Book.getCurrBookName()

        imagePath = _upan.Paths.Entry.ExtraImage.getAbs(bookName, 
                                                           subsection, 
                                                           imIdx,
                                                           extraIdx)

        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
            text = "\"No extra yet\""

        if text == _u.Token.NotDef.str_t:
            pilIm = Image.open(imagePath)
            w, h = pilIm.size

            if h > 400:
                pilIm.thumbnail([530, 300], Image.LANCZOS)
            else:
                pilIm.thumbnail([530, 1000], Image.LANCZOS)

            self.image = ww.currUIImpl.UIImage(pilIm)
            return super().__init__(prefix, name, root, renderData, image = self.image, padding = padding)
        else:
            return super().__init__(prefix, name, root, renderData, text = text, padding = padding)

class ExcerciseExtraLabel(ww.currUIImpl.ScrollableBox,
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
        name = "_ExcerciseExtraLabel_LBL"
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
        self.addExtraWidgets()

        return super().render(self.renderData)

    def addExtraWidgets(self):
        # image
        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        subsection = self.subsection
        imIdx = self.imIdx

        entryFSpath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryFSpath):
            extrasNameToken = _upan.Names.Entry.Extra.extraImgToken
            extras = [i for i in os.listdir(entryFSpath) if extrasNameToken in i]
            extrasIndicies = [".".join(i.replace(extrasNameToken, "").split(".")[:-1])\
                                  for i in extras]

            for i in range(len(extrasIndicies)):
                solIdx = extrasIndicies[i]
                label = ExcerciseExtraImageLabel(self.scrollable_frame, f"lineExtraImageIMG_{solIdx}", 
                                            self.subsection, self.imIdx, solIdx,
                                            padding = [0, 0, 0, 0],
                                            row = i + 2, column = 2)
                label.render()
                self.labels.append(label)
                self.imLabel = label

                def __openSolimage(event):
                    w = event.widget
                    bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                    ocf.Wr.FsAppCalls.openFile(_upan.Paths.Entry.ExtraImage.getAbs(bookPath,
                                                                                      w.subsection, 
                                                                                      w.imIdx,
                                                                                      w.solImIdx
                                                                                      ))
                label.rebind([ww.currUIImpl.Data.BindID.mouse1], [__openSolimage])

                # '''
                # delete
                # '''
                deleteLabel = ExcerciseExtraLabelWithClick(self.scrollable_frame, f"_deleteNote_{solIdx}", 
                                                        i + 2, 1, text = "Del")
                deleteLabel.subsection = self.subsection
                deleteLabel.imIdx = self.imIdx
                deleteLabel.solImIdx = solIdx

                def deleteNoteIdx(event, *args):
                    w = event.widget
                    bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                    
                    ocf.Wr.FsAppCalls.deleteFile(_upan.Paths.Entry.ExtraImage.getAbs(bookPath,
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

class HideExcerciseExtraWindow_BTN(ww.currUIImpl.Button,
                              dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        text = "Hide"
        name = "_HidehideExcerciseExtraWindow_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        excerciseExtraManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.ExcerciseExtraManager)
        excerciseExtraManager.hide()

class AddFromClipbordExcerciseExtraWindow_BTN(ww.currUIImpl.Button,
                              dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 1, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        text = "Add from clipboard"
        name = "_addFromclipbordExcerciseExtraWindow_BTN_BTN"
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
            extrasNameToken = _upan.Names.Entry.Extra.extraImgToken
            numExtras = len([i for i in os.listdir(entryFSpath) if extrasNameToken in i])

            solPath = _upan.Paths.Entry.ExtraImage.getAbs(bookPath, self.subsection, self.imIdx, numExtras)
            im = ImageGrab.grabclipboard()
            im.save(solPath,'PNG')
        
            self.notify(ExcerciseExtraLabel)

class AddScreenshotExcerciseExtraWindow_BTN(ww.currUIImpl.Button,
                              dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 2, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        text = "Add from screenshot"
        name = "_addFromScreenshotExcerciseExtraWindow_BTN_BTN"
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
            extrasNameToken = _upan.Names.Entry.Extra.extraImgToken
            numExtras = len([i for i in os.listdir(entryFSpath) if extrasNameToken in i])

            solPath = _upan.Paths.Entry.ExtraImage.getAbs(bookPath, self.subsection, self.imIdx, numExtras)
            ocf.Wr.ScreenshotCalls.takeScreenshot(solPath)

            for _ in range(100):
                if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(solPath):
                    break
                time.sleep(0.3)
        
            self.notify(ExcerciseExtraLabel)

class ExcerciseExtraRoot(ww.currUIImpl.RootWidget):
    pass