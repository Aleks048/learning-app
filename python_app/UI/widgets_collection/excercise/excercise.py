import tkinter as tk
from tkinter import ttk
import Pmw
from PIL import Image, ImageTk
import time
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
import scripts.osascripts as osascr
import UI.widgets_data as wd
import data.temp as dt
import generalManger.generalManger as gm

exImages = []

class ImageText_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix, row, column, imLineIdx, text):
        name = "_textImage_ETR" + str(imLineIdx)
        self.defaultText = text
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row, "columnspan": 6},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }


        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wd.Data.ENT.defaultTextColor,
                                            "font": ('Georgia 14')},
            ww.TkWidgets.__name__ : {"width": 60, "fg": "white"}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraBuildOptions,
                        defaultText = self.defaultText)
        super().setData(self.defaultText)
        self.setTextColor("white")
    
    def receiveNotification(self, _):
        return self.getData()
    
    def defaultTextCMD(self):
        pass


class ExcerciseImageLabel(ttk.Label):
    lineImIdx = None

    def __init__(self, root, name, subsection, imIdx, lineIdx, text = _u.Token.NotDef.str_t):
        self.lineImIdx = str(lineIdx)

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
            img = ImageTk.PhotoImage(pilIm)
            exImages.append(img)
            return super().__init__(root, name = name, image = img, padding = [0, 0, 0, 0])
        else:
            return super().__init__(root, name = name, text = text, padding = [0, 0, 0, 0])


class ExcerciseImage(ww.currUIImpl.Frame):
    displayedImages = []
    subsection = None
    entryIdx = None

    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0, "columnspan": 6},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.NW}
        }
        name = "_excerciseImage_LBL"

        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data)
    
    def render(self, **kwargs):
                
        # get an image from the
        widget = self.widgetObj

        for child in widget.winfo_children():
            child.destroy()

        balloon = Pmw.Balloon(widget)
        self.imLabel = _ucomw.addMainEntryImageWidget(widget, 
                                                      self.subsection, self.entryIdx,
                                                      120, self.displayedImages, balloon)
        self.imLabel.render()
        self.imLabel.focus_force()

        def skipProofs(subsection, imIdx, i):
           return "proof" in fsf.Data.Sec.extraImagesDict(subsection)[imIdx][i].lower()

        exImLabels = _ucomw.addExtraEntryImagesWidgets(widget, 
                                                       self.subsection, self.entryIdx,
                                                       120, self.displayedImages, balloon,
                                                       skippConditionFn = skipProofs)
        for l in exImLabels:
            l.render()

        return super().render(**kwargs)


class AddExcerciseLine_BTN(ww.currUIImpl.Button):
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 1, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Add"
        name = "_AddExcerciseLine_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        text = self.notify(AddExcerciseLine_ETR)
        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        fsf.Wr.EntryInfoStructure.addLine(self.subsection, self.imIdx, text, bookPath)

        # update the box UI
        self.notify(Excercise_BOX)

    def receiveNotification(self, broadcasterType):
        if broadcasterType == AddExcerciseLine_ETR:
            self.cmd()

class ShowSolutions_BTN(ww.currUIImpl.Button):
    showSolutions = True
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 5, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Solutions"
        name = "_ShowSolutions_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        subsection = self.subsection
        imIdx = self.imIdx

        savePath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)

        filename = _upan.Names.Entry.Solution.name(imIdx, str(0))
        solutionPath = os.path.join(savePath, filename)

        for i in range(0, 5):
            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(solutionPath):
                if self.showSolutions:
                    ocf.Wr.FsAppCalls.openFile(solutionPath)
                else:
                    cmd = osascr.get_ClosePreviewByFilepath_CMD(solutionPath)
                    _u.runCmdAndWait(cmd)

                filename = _upan.Names.Entry.Solution.name(imIdx, str(i))
                solutionPath = os.path.join(savePath, filename)
        
        self.showSolutions = not self.showSolutions


class PasteGlLink_BTN(ww.currUIImpl.Button):
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Paste Gl Link"
        name = "_PasteGlLink_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        sourceSubsection = self.subsection
        sourceTopSection = sourceSubsection.split(".")[0]
        sourceImIdx = self.imIdx
        targetSubsection = dt.UITemp.Link.subsection
        targetImIdx = dt.UITemp.Link.imIdx

        if targetSubsection != _u.Token.NotDef.str_t\
            and targetImIdx != _u.Token.NotDef.str_t:
            gm.GeneralManger.AddLink(f"{targetSubsection}.{targetImIdx}",
                                    sourceSubsection,
                                    sourceImIdx,
                                    sourceTopSection)

class HideAllETRsWindow_BTN(ww.currUIImpl.Button):
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 3, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Hide All ETRs"
        name = "_HideAllETRsWindow_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        self.notify(Excercise_BOX)

class MoveTOCtoExcerciseEntry_BTN(ww.currUIImpl.Button,
                                  dc.AppCurrDataAccessToken):
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 4, "row" : 2},
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
        excerciseManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.MathMenuManager)
        excerciseManager.moveTocToEntry(self.subsection, self.imIdx)

class HideExcerciseWindow_BTN(ww.currUIImpl.Button,
                              dc.AppCurrDataAccessToken):
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 2, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Hide"
        name = "_HideExcerciseWindow_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        excerciseManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.ExcerciseManager)
        excerciseManager.hide()

        msg = "\
After updating the excercises for \n\
'{0}':'{1}'.".format(self.subsection, self.imIdx)
        _u.log.autolog(msg)
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)


class AddExcerciseLine_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix):
        name = "_getExcerciseNewLineText_ETR"
        defaultText = "New excercise line text"  + " / \"solution:\" prefix to add solution"
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 3, "columnspan": 6},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        extraOptions = {
            ww.Data.GeneralProperties_ID : {"width" : 70},
            ww.TkWidgets.__name__ : {}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraOptions = extraOptions,
                        defaultText = defaultText,
                        bindCmd = self.bindCmd)
    
    def receiveNotification(self, broadcasterType):
        text = self.getData()

        if broadcasterType == AddExcerciseLine_BTN:
            self.setData(self.defaultText)

        if (text != self.defaultText) and (text != ""):
            return text
        else:
            return "-1"
      
    def getData(self, **kwargs):
        text = super().getData(**kwargs)
        return text
      
    def bindCmd(self):
        return [ww.currUIImpl.Data.BindID.Keys.shenter], \
                [lambda *args: self.notify(AddExcerciseLine_BTN)]


class Excercise_BOX(ww.currUIImpl.ScrollableBox,
                    dc.AppCurrDataAccessToken):
    subsection = None
    imIdx = None

    currLineCopyIdx = _u.Token.NotDef.int_t

    lineIdxShownInText = []
    currEtr = _u.Token.NotDef.dict_t.copy()

    displayedImages = []

    latestWidgetToscrollTo = None
    latestLineIdxToscrollTo = None

    def __init__(self, parentWidget, prefix, windth = 700, height = 500):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 1, "columnspan" : 6, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_showExcerciseCurr_text"

        self.parent = parentWidget.widgetObj

        super().__init__(prefix,
                        name,
                        parentWidget,
                        renderData = data,
                        height = height,
                        width = windth,
                        makeScrollable = False)

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
            self.canvas.yview_moveto((pos / height))
        except:
            pass

    def addExcerciseLines(self):
        lines = fsf.Wr.EntryInfoStructure.readProperty(self.subsection,
                                                       self.imIdx, 
                                                       fsf.Wr.EntryInfoStructure.PubProp.entryLinesList)
        '''
        for each line add widgets:
        '''
        if self.currEtr == _u.Token.NotDef.dict_t:
            self.currEtr = {}           

        for i in range(len(lines)):
            def __showTextOrImage(event, *args):
                self.latestLineIdxToscrollTo = event.widget.lineImIdx
                bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                widgetlineImIdx = str(event.widget.lineImIdx)

                if widgetlineImIdx in self.lineIdxShownInText:
                    self.lineIdxShownInText.remove(widgetlineImIdx)
                    text = self.currEtr[widgetlineImIdx].getData()

                    if text != self.currEtr[widgetlineImIdx].defaultText:
                        fsf.Wr.EntryInfoStructure.rebuildLine(self.subsection,
                                                              self.imIdx,
                                                              event.widget.lineImIdx,
                                                              text,
                                                              bookPath)

                    self.currEtr.pop(widgetlineImIdx)
                else:
                    self.lineIdxShownInText.append(str(event.widget.lineImIdx))

                for lineImIdx in self.lineIdxShownInText:
                    if lineImIdx in list(self.currEtr.keys()):
                        text = self.currEtr[lineImIdx].getData()
                        fsf.Wr.EntryInfoStructure.rebuildLine(self.subsection,
                                                                self.imIdx,
                                                                lineImIdx,
                                                                text,
                                                                bookPath)

                self.render()

            # image / text
            if str(i) not in self.lineIdxShownInText:
                label = ExcerciseImageLabel(self.scrollable_frame, "linesImageIMG_" + str(i), 
                                            self.subsection, self.imIdx, i)
                label.grid(row = i + 1, column = 5)
                label.bind(ww.currUIImpl.Data.BindID.mouse2, __showTextOrImage)
            else:
                label = _ucomw.TOCFrame(self.scrollable_frame, 
                                "linesImageFRM_" + str(i),
                                i + 1, 5, 1
                                )
                labIm = ExcerciseImageLabel(label, "linesImageIMG_" + str(i), 
                                            self.subsection, self.imIdx, i)
                labIm.grid(row = 0, column = 0)

                labETR = _ucomw.MultilineText_ETR(label, "linesImageETR_", 1, 0, i, lines[i])
                self.currEtr[str(i)] = labETR

                labRebuild = _ucomw.TOCLabelWithClick(label, "linesImageRebuild_" + str(i), 
                                                2, 0, text = "Rebuild")
                labRebuild.lineImIdx = str(i)

                def rebuildETRImage(event, *args):
                    widgetlineImIdx = event.widget.lineImIdx
                    text = self.currEtr[widgetlineImIdx].getData()
                    position = self.currEtr[widgetlineImIdx].index(tk.INSERT)

                    if text != self.currEtr[widgetlineImIdx].defaultText:
                        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                        fsf.Wr.EntryInfoStructure.rebuildLine(self.subsection,
                                                            self.imIdx,
                                                            event.widget.lineImIdx,
                                                            text,
                                                            bookPath)
                    self.render()
                    self.currEtr[widgetlineImIdx].focus_force()
                    self.currEtr[widgetlineImIdx].mark_set("insert", position)
                    self.__scrollIntoView(event)

                    return "break"

                labETR.lineImIdx = str(i)
                labETR.rebind([ww.currUIImpl.Data.BindID.Keys.shenter], [rebuildETRImage])
                labRebuild.rebind([ww.currUIImpl.Data.BindID.mouse1], [rebuildETRImage])
                labIm.bind(ww.currUIImpl.Data.BindID.mouse2, __showTextOrImage)
                _ucomw.bindChangeColorOnInAndOut(labRebuild)

                labETR.render()
                labRebuild.render()
                label.render()


            if (str(i) == self.latestLineIdxToscrollTo) and label != None:
                self.latestWidgetToscrollTo = label

            '''
            copy
            '''
            copyLabel = _ucomw.TOCLabelWithClick(self.scrollable_frame, "_copyLine_" + str(i), 
                                                    i + 1, 1, text = "Copy")
            copyLabel.lineImIdx = i

            def setCopyLineIdx(event, *args):
                self.currLineCopyIdx = event.widget.lineImIdx

            copyLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [setCopyLineIdx])
            _ucomw.bindChangeColorOnInAndOut(copyLabel)
            copyLabel.render()

            '''
            paste
            '''
            pasteLabel = _ucomw.TOCLabelWithClick(self.scrollable_frame, "_pasteBLine_" + str(i), 
                                                    i + 1, 2, text = "PB")
            pasteLabel.lineImIdx = i

            def pasteLineIdx(event, *args):
                bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                linesList = fsf.Wr.EntryInfoStructure.readProperty(self.subsection, self.imIdx,
                                                        fsf.Wr.EntryInfoStructure.PubProp.entryLinesList,
                                                        bookPath)
                fsf.Wr.EntryInfoStructure.addLine(self.subsection, 
                                                  self.imIdx,
                                                  linesList[self.currLineCopyIdx],
                                                  bookPath, 
                                                  event.widget.lineImIdx)
                self.render()

            pasteLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [pasteLineIdx])
            _ucomw.bindChangeColorOnInAndOut(pasteLabel)
            pasteLabel.render()

            pasteLabel = _ucomw.TOCLabelWithClick(self.scrollable_frame, "_pasteALine_" + str(i), 
                                                    i + 1, 3, text = "PA")
            pasteLabel.lineImIdx = i

            def pasteLineIdx(event, *args):
                bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                linesList = fsf.Wr.EntryInfoStructure.readProperty(self.subsection, self.imIdx,
                                                        fsf.Wr.EntryInfoStructure.PubProp.entryLinesList,
                                                        bookPath)
                fsf.Wr.EntryInfoStructure.addLine(self.subsection, 
                                                  self.imIdx,
                                                  linesList[self.currLineCopyIdx],
                                                  bookPath, 
                                                  event.widget.lineImIdx + 1)
                self.render()

            pasteLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [pasteLineIdx])
            _ucomw.bindChangeColorOnInAndOut(pasteLabel)
            pasteLabel.render()

            '''
            delete
            '''
            deleteLabel = _ucomw.TOCLabelWithClick(self.scrollable_frame, "_deleteLine_" + str(i), 
                                                    i + 1, 4, text = "Del")
            deleteLabel.lineImIdx = i

            def deleteLineIdx(event, *args):
                bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                fsf.Wr.EntryInfoStructure.deleteLine(bookPath,
                                                     self.subsection,
                                                     self.imIdx,
                                                     event.widget.lineImIdx)
                self.currEtr.pop(str(event.widget.lineImIdx))
                self.render()

            deleteLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [deleteLineIdx])
            _ucomw.bindChangeColorOnInAndOut(deleteLabel)
            deleteLabel.render()

    def receiveNotification(self, broadcasterType) -> None:
        if broadcasterType == AddExcerciseLine_BTN:
            lines = fsf.Wr.EntryInfoStructure.readProperty(self.subsection,
                                                       self.imIdx, 
                                                       fsf.Wr.EntryInfoStructure.PubProp.entryLinesList)
            self.lineIdxShownInText.append(str(len(lines) - 1))
            self.render()
        if broadcasterType == HideAllETRsWindow_BTN:
            self.lineIdxShownInText = _u.Token.NotDef.list_t.copy()
            self.currEtr = _u.Token.NotDef.dict_t.copy()
            self.render()

    def render(self, widjetObj=None, renderData=..., **kwargs):
        global exImages
        exImages = []

        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        self.scrollable_frame.focus_force()

        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        entryLinesPath = _upan.Paths.Entry.getAbs(bookPath, self.subsection, self.imIdx)

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryLinesPath):
            self.addExcerciseLines()


        super().render(widjetObj, renderData, **kwargs)

        if self.latestWidgetToscrollTo != None:
            self.__scrollIntoView(None, self.latestWidgetToscrollTo)

class ExcerciseRoot(ww.currUIImpl.RootWidget):
    pass