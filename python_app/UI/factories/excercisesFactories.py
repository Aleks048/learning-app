from threading import Thread
from PIL import Image
import time

import UI.widgets_facade as wf
import UI.widgets_collection.common as comw
import UI.widgets_collection.utils as _ucomw
import UI.widgets_wrappers as ww
import UI.widgets_data as wd
from UI.widgets_collection.utils import bindWidgetTextUpdatable
import file_system.file_system_facade as fsf
import settings.facade as sf
import _utils.pathsAndNames as _upan
import _utils._utils_main as _u

import outside_calls.outside_calls_facade as ocf


import data.temp as dt

class ExcerciseLineManager():
    def __init__(self, imIdx, subsection, excerciseWidgetFrame):
        self.copyInx = None

        self.latestLineIdxToscrollTo = None
        self.lineIdxShownInText = []

        self.frame = excerciseWidgetFrame
        self.lineEtr = None


def _rebuildExcerciseImage(*args, **kwargs):
    '''
        used for multithreaded line rebuild
    '''
    t = Thread(target= fsf.Wr.EntryInfoStructure.updateExerciseImage, 
            args = (args))
    t.start()
    return t


class ExcerciseImageLabel(ww.currUIImpl.Label):
    def __init__(self, root, prefix, subsection, imIdx, lineIdx, row, column, text = _u.Token.NotDef.str_t):
        self.lineImIdx = str(lineIdx)

        self.subsection = subsection
        self.bookName = sf.Wr.Manager.Book.getCurrBookName()
        self.imIdx = imIdx
        self.lineIdx = lineIdx

        data = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }

        name = "_ExcerciseImageLabel_"

        if text ==  _u.Token.NotDef.str_t:
            bookName = sf.Wr.Manager.Book.getCurrBookName()

            imagePath = _upan.Paths.Entry.LineImage.getAbs(bookName, subsection, imIdx, lineIdx)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                fsf.Wr.EntryInfoStructure.rebuildLine(subsection, 
                                                      imIdx, 
                                                      lineIdx, 
                                                      text,
                                                      currBookPath)

            pilIm = Image.open(imagePath)
            pilIm.thumbnail([530, 1000], Image.LANCZOS)
            self.image = ww.currUIImpl.UIImage(pilIm)
            return super().__init__(prefix, name, root, data, image = self.image, padding = [0, 0, 0, 0])
        else:
            return super().__init__(prefix, name, root, data, text = text, padding = [0, 0, 0, 0])

    def updateImage(self):
        imagePath = _upan.Paths.Entry.LineImage.getAbs(self.bookName, 
                                                       self.subsection, 
                                                       self.imIdx, 
                                                       self.lineIdx)
        counter = 0
        
        while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
            time.sleep(0.3)
            counter += 1

            if counter > 100:
                return

        pilIm = Image.open(imagePath)
        pilIm.thumbnail([530, 1000], Image.LANCZOS)
        self.image = ww.currUIImpl.UIImage(pilIm)
        return super().updateImage(self.image)


class ExcerciseLineFactory:
    def __init__(self, subsection, imIdx, lineIdx, row):
        self.subsection = subsection
        self.imIdx = imIdx
        self.lineIdx = lineIdx
        self.row = row

        self.manager = None

    def getPrefix(self):
        subsctionTransformed = self.subsection.replace(".", "")
        return f"{subsctionTransformed}_{self.imIdx}_{self.lineIdx}"

    def produceLineFrame(self, parentWidget):
        frame = comw.TOCFrame(parentWidget, 
                              self.getPrefix() + "linesFRM_",
                              row = self.row, column = 0, columnspan = 1)
        return frame

    def produceMainImageFrame(self, parentWidget):
        def __rebuildETRImage(event, labIm, *args):
            # labIm = event.widget.getPosition()
            newText = event.widget.getData()

            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            fsf.Wr.EntryInfoStructure.updateExerciseLine(event.widget.subsection,
                                                         event.widget.imIdx,
                                                         event.widget.lineImIdx,
                                                         newText,
                                                         bookPath)

            _rebuildExcerciseImage(event.widget.subsection,
                                   event.widget.imIdx,
                                   event.widget.lineImIdx,
                                   bookPath)
            

            def __updateImage(widget, bookPath, subsection, imIdx, lineIdx):
                imagePath = _upan.Paths.Entry.LineImage.getAbs(bookPath, 
                                                               subsection, 
                                                               imIdx, 
                                                               lineIdx)
                counter = 0
                
                while ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                    counter += 1

                    if counter > 100:
                        return

                widget.updateImage()

            t = Thread(target= __updateImage, 
                    args = [labIm, bookPath, self.subsection, self.imIdx, self.lineIdx])
            t.start()


            
            return "break"

        def __showTextOrImage(event, widget, *args):
            if widget.wasRendered:
                widget.hide()

                for w in wd.Data.Reactors.excerciseLineChangeReactors.values():
                    if "onTextUpdateEtrHide" in dir(w):
                        w.onTextUpdateEtrHide(self.lineIdx)
            else:
                widget.render()

                for w in wd.Data.Reactors.excerciseLineChangeReactors.values():
                    if "onTextUpdateEtrShow" in dir(w):
                        w.onTextUpdateEtrShow(self.lineIdx)

        frame = comw.TOCFrame(parentWidget, 
                              self.getPrefix() + "linesImageFRM_",
                              row = 0, column = 6, columnspan = 1)

        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        entryLinesList = fsf.Wr.EntryInfoStructure.readProperty(self.subsection, 
                                                                self.imIdx, 
                                                                fsf.Wr.EntryInfoStructure.PubProp.entryLinesList, 
                                                                        bookPath)
        text  = entryLinesList[int(self.lineIdx)]
        labETR = comw.MultilineText_ETR(frame, "linesImageETR_", row = 1, column = 0,
                                         imLineIdx=self.lineIdx, text = text)
        labETR.subsection = self.subsection
        labETR.imIdx = self.imIdx
        labETR.lineImIdx = self.lineIdx

        label = ExcerciseImageLabel(frame, self.getPrefix() + "linesImageIMG_", 
                                    self.subsection, self.imIdx, lineIdx = self.lineIdx, 
                                    row = 0, column = 0)
        label.render()
        label.rebind([ww.currUIImpl.Data.BindID.mouse2],
                        [lambda e, etr = labETR, *args: __showTextOrImage(e, etr)])
        labETR.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                        [lambda e, l = label, *args: __rebuildETRImage(e, l)])

        return frame, labETR

    def producePasteBeforeLineWidget(self, parentWidget):
        '''
        produce paste before excercise line widget
        '''
        pasteLabel = comw.TOCLabelWithClick(parentWidget, self.getPrefix() + "_pasteBLine_", 
                                            0, 2, text = "PB")
        pasteLabel.lineImIdx = self.lineIdx

        def pasteLineIdx(event, manager, *args):
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            linesList = fsf.Wr.EntryInfoStructure.readProperty(self.subsection, self.imIdx,
                                                    fsf.Wr.EntryInfoStructure.PubProp.entryLinesList,
                                                    bookPath)
            fsf.Wr.EntryInfoStructure.addLine(self.subsection, 
                                                self.imIdx,
                                                linesList[manager.copyInx],
                                                bookPath, 
                                                event.widget.lineImIdx)
            entryLinesNotesList = fsf.Wr.EntryInfoStructure.readProperty(self.subsection, self.imIdx,
                                fsf.Wr.EntryInfoStructure.PubProp.entryLinesNotesList,
                                bookPath)

            if int(manager.copyInx) <= int(event.widget.lineImIdx):
                manager.copyInx = str(int(manager.copyInx) + 1)

            if entryLinesNotesList.get(str(manager.copyInx)) != None:
                    fsf.Wr.EntryInfoStructure.addLineNote(self.subsection, 
                                                self.imIdx,
                                                entryLinesNotesList[str(manager.copyInx)],
                                                bookPath, 
                                                str(int(event.widget.lineImIdx) - 1))
            
            excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.ExcerciseManager)
            excerciseManager.updateExcerciseBox()

        pasteLabel.rebind([ww.currUIImpl.Data.BindID.mouse1],
                          [lambda e, m = self.manager, *args: pasteLineIdx(e, m)])
        _ucomw.bindChangeColorOnInAndOut(pasteLabel)
        return pasteLabel

    def producePasteAfterLineWidget(self, parentWidget):
        '''
        produce paste after excercise line widget
        '''
        pasteLabel = comw.TOCLabelWithClick(parentWidget, self.getPrefix() + "_pasteALine_", 
                                                0, 3, text = "PA")
        pasteLabel.lineImIdx = self.lineIdx

        def pasteLineIdx(event, manager, *args):
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            linesList = fsf.Wr.EntryInfoStructure.readProperty(self.subsection, self.imIdx,
                                                    fsf.Wr.EntryInfoStructure.PubProp.entryLinesList,
                                                    bookPath)
            fsf.Wr.EntryInfoStructure.addLine(self.subsection, 
                                                self.imIdx,
                                                linesList[manager.copyInx],
                                                bookPath, 
                                                event.widget.lineImIdx + 1)
            entryLinesNotesList = fsf.Wr.EntryInfoStructure.readProperty(self.subsection, self.imIdx,
                                                fsf.Wr.EntryInfoStructure.PubProp.entryLinesNotesList,
                                                bookPath)

            if int(manager.copyInx) <= int(event.widget.lineImIdx):
                manager.copyInx = str(int(manager.copyInx) + 1)

            if entryLinesNotesList.get(str(manager.copyInx)) != None:
                    fsf.Wr.EntryInfoStructure.addLineNote(self.subsection, 
                                                self.imIdx,
                                                entryLinesNotesList[str(manager.copyInx)],
                                                bookPath, 
                                                str(event.widget.lineImIdx + 1))
    
            excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.ExcerciseManager)
            excerciseManager.updateExcerciseBox()

        pasteLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], 
                          [lambda e, m = self.manager, *args: pasteLineIdx(e, m)])
        _ucomw.bindChangeColorOnInAndOut(pasteLabel)
        return pasteLabel

    def produceDeleteLineWidget(self, parentWidget):
        '''
        delete
        '''
        deleteLabel = comw.TOCLabelWithClick(parentWidget, self.getPrefix() + "_deleteLine_", 
                                             0, 4, text = "Del")
        deleteLabel.lineImIdx = self.lineIdx

        def deleteLineIdx(event, *args):
            lineIdx = event.widget.lineImIdx
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            deletedStructure = fsf.Wr.EntryInfoStructure.deleteLine(bookPath,
                                                                    self.subsection,
                                                                    self.imIdx,
                                                                    event.widget.lineImIdx)
            
            excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.ExcerciseManager)
            excerciseManager.deleteLine(lineIdx)

            if deletedStructure:
                mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.MathMenuManager)
                mainManager.renderWithoutScroll()
                mainManager.moveTocToEntry(self.subsection, self.imIdx)

        deleteLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [deleteLineIdx])
        _ucomw.bindChangeColorOnInAndOut(deleteLabel)

        return deleteLabel

    def produceOpenNoteWidget(self, parentWidget):
        '''
        note
        '''
        noteLabel = comw.TOCLabelWithClick(parentWidget, self.getPrefix() + "_notesForLine_", 
                                            0, 5, text = "N")
        noteLabel.lineImIdx = self.lineIdx
        noteLabel.subsection = self.subsection
        noteLabel.imIdx = self.imIdx

        def noteForLineIdx(event, *args):
            widget = event.widget
            excerciseLineNoteManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.ExcerciseLineNoteManager)
            excerciseLineNoteManager.show(widget.subsection, widget.imIdx, widget.lineImIdx)

        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        entryLinesNotesList = fsf.Wr.EntryInfoStructure.readProperty(self.subsection, self.imIdx,
                                fsf.Wr.EntryInfoStructure.PubProp.entryLinesNotesList,
                                bookPath)
        shouldBeBrown = False

        if entryLinesNotesList.get(self.lineIdx) != None:
            noteLabel.changeColor("brown")
            shouldBeBrown = True

        noteLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [noteForLineIdx])
        _ucomw.bindChangeColorOnInAndOut(noteLabel, shouldBeBrown)

        return noteLabel

    def produceCopyLineWidget(self, parentWidget):
        '''
        produce copy excercise line widget
        '''

        copyLabel = comw.TOCLabelWithClick(parentWidget, 
                                           self.getPrefix() + "copyLine_", 
                                           row = 0, column = 0, text = "Copy")
        copyLabel.lineImIdx = self.lineIdx

        def setCopyLineIdx(event, *args):
            self.manager.copyInx = event.widget.lineImIdx

        copyLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [setCopyLineIdx])
        _ucomw.bindChangeColorOnInAndOut(copyLabel)

        return copyLabel

    def produce(self, parentWidget):
        lineFrame = self.produceLineFrame(parentWidget)
        lineFrame.render()

        self.manager = ExcerciseLineManager(self.imIdx, self.subsection, lineFrame)

        lineImageFrame, lineEtr = self.produceMainImageFrame(lineFrame)
        self.manager.lineEtr = lineEtr
        lineImageFrame.render()
        copyWidget = self.produceCopyLineWidget(lineFrame)
        copyWidget.render()
        openNoneWidget = self.produceOpenNoteWidget(lineFrame)
        openNoneWidget.render()
        deleteLineWidget = self.produceDeleteLineWidget(lineFrame)
        deleteLineWidget.render()
        pasteBeforeWidget = self.producePasteBeforeLineWidget(lineFrame)
        pasteBeforeWidget.render()
        pasteAfterWidget = self.producePasteAfterLineWidget(lineFrame)
        pasteAfterWidget.render()
        return self.manager