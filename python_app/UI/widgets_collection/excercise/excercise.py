import tkinter as tk
from tkinter import ttk
import Pmw
from PIL import Image, ImageTk
import time
import os
from threading import Thread

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
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row, "columnspan": 7},
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
    
    def hide(self, **kwargs):
        # get an image from the
        widget = self.widgetObj

        for child in widget.winfo_children():
            child.destroy()
        return super().hide(**kwargs)

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


class AddExcerciseLine_BTN(ww.currUIImpl.Button,
                           dc.AppCurrDataAccessToken):
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
        structureCreated = fsf.Wr.EntryInfoStructure.addLine(self.subsection, self.imIdx, text, bookPath)

        # update the box UI
        self.notify(Excercise_BOX)

        if structureCreated:
            excerciseManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.MathMenuManager)
            excerciseManager.moveTocToEntry(self.subsection, self.imIdx)


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
        excerciseSolutionManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.ExcerciseSolutionManager)
        if self.showSolutions:
            excerciseSolutionManager.show(self.subsection, self.imIdx)
            self.showSolutions = False
        else:
            excerciseSolutionManager.hide()
            self.showSolutions = True

class ShowExtra_BTN(ww.currUIImpl.Button):
    showSolutions = True
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 6, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Extra"
        name = "_ShowExtra_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        excerciseExtraManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.ExcerciseExtraManager)
        if self.showSolutions:
            excerciseExtraManager.show(self.subsection, self.imIdx)
            self.showSolutions = False
        else:
            excerciseExtraManager.hide()
            self.showSolutions = True


class HideExcerciseImage(ww.currUIImpl.Button):
    subsection = None
    imIdx = None

    show = False

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Hide Main Image"
        name = "_HideExcerciseImage_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                          wf.Wr.MenuManagers.ExcerciseManager)
        excerciseManager.show(self.show)
        self.show = not self.show

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
        defaultText = "New excercise line text"
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 3, "columnspan": 7},
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

def _rebuildLine(*args, **kwargs):
    '''
        used for multithreaded line rebuild
    '''
    t = Thread(target= fsf.Wr.EntryInfoStructure.rebuildLine, 
            args = (args))
    t.start()
    return t

class Excercise_BOX(ww.currUIImpl.ScrollableBox,
                    dc.AppCurrDataAccessToken):
    subsection = None
    imIdx = None

    currLineCopyIdx = _u.Token.NotDef.int_t

    lineIdxShownInText = []
    currEtr = _u.Token.NotDef.dict_t.copy()
    etrTexts = _u.Token.NotDef.dict_t.copy()

    displayedImages = []

    latestWidgetToscrollTo = None
    latestLineIdxToscrollTo = None

    def __init__(self, parentWidget, prefix, windth = 700, height = 500):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 1, "columnspan" : 7, "rowspan": 1},
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

        def on_vertical(event):
            self.canvas.yview_scroll(-1 * event.delta, 'units')

        self.container.bind_all('<Mod1-MouseWheel>', on_vertical)

    def __renderAfterRebuild(self, *args, **kwargs):
        def __internal(*args, **kwargs):
            lineIdx = kwargs["lineIdx"]
            t = _rebuildLine(*args, **kwargs)
            t.join()
            self.render()
            position = self.etrTexts[lineIdx][1]
            self.currEtr[lineIdx].focus_force()

            try:
                self.currEtr[lineIdx].mark_set("insert", position)
            except:
                pass
        Thread(target = __internal,
               args = args, 
               kwargs = kwargs).start()

    def __scrollIntoView(self, event, widget = None):
        # NOTE: this is a hack to make opening different excercise windows
        # without it we get a crash
        try:
            self.scrollable_frame.update()
            self.scrollable_frame.update_idletasks()

            posy = 0

            if widget == None:
                pwidget = event.widget
            else:
                pwidget = widget

            shouldScrollToRebuild = False

            if "linesImageFRM_" in str(pwidget):
                for ch in pwidget.winfo_children():
                    if "linesImageRebuild_" in str(ch):
                        pwidget = ch
                        shouldScrollToRebuild = True
                        break

            while pwidget != self.parent:
                posy += pwidget.winfo_y()
                pwidget = pwidget.master

            pos = posy - self.scrollable_frame.winfo_rooty()
            height = self.scrollable_frame.winfo_height()

            preScaceRegular = float(self.canvas.winfo_height() - 100) / height
            preScaceEntry =int( self.canvas.winfo_height() - 130) / height

            if not shouldScrollToRebuild:
                self.canvas.yview_moveto((pos / height) - preScaceRegular)
            else:
                self.canvas.yview_moveto((pos / height) - preScaceEntry)
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

        numRowsPre = 1

        for i in range(len(lines)):
            def __showTextOrImage(event, *args):
                self.latestLineIdxToscrollTo = event.widget.lineImIdx
                bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                widgetlineImIdx = str(event.widget.lineImIdx)

                # for lineImIdx in self.lineIdxShownInText:
                #     if lineImIdx in list(self.currEtr.keys()):
                #         text = self.currEtr[lineImIdx].getData()
                #         fsf.Wr.EntryInfoStructure.rebuildLine(self.subsection,
                #                                                 self.imIdx,
                #                                                 lineImIdx,
                #                                                 text,
                #                                                 bookPath)

                if widgetlineImIdx in self.lineIdxShownInText:
                    self.lineIdxShownInText.remove(widgetlineImIdx)
                    text = self.currEtr[widgetlineImIdx].getData()

                    if text != self.currEtr[widgetlineImIdx].defaultText:
                        _rebuildLine(self.subsection,
                                            self.imIdx,
                                            event.widget.lineImIdx,
                                            text,
                                            bookPath)

                    self.currEtr.pop(widgetlineImIdx)
                else:
                    self.lineIdxShownInText.append(str(event.widget.lineImIdx))

                self.render()

            # image / text
            if str(i) not in self.lineIdxShownInText:
                label = ExcerciseImageLabel(self.scrollable_frame, "linesImageIMG_" + str(i), 
                                            self.subsection, self.imIdx, i)
                label.grid(row = i + numRowsPre + 1, column = 6)
                label.bind(ww.currUIImpl.Data.BindID.mouse2, __showTextOrImage)
                label.bind(ww.currUIImpl.Data.BindID.mouse1, self.__scrollIntoView)
                labelToScrollTo = label
            else:
                label = _ucomw.TOCFrame(self.scrollable_frame, 
                                "linesImageFRM_" + str(i),
                                i + numRowsPre + 1, 6, 1
                                )
                labIm = ExcerciseImageLabel(label, "linesImageIMG_" + str(i), 
                                            self.subsection, self.imIdx, i)
                labIm.grid(row = 0, column = 0)

                text = ""
                if str(i) in list(self.etrTexts.keys()):
                    text = self.etrTexts[str(i)][0]
                else:
                    text = lines[i]

                labETR = _ucomw.MultilineText_ETR(label, "linesImageETR_", 1, 0, i, text)
                self.currEtr[str(i)] = labETR

                labRebuild = _ucomw.TOCLabelWithClick(label, "linesImageRebuild_" + str(i), 
                                                2, 0, text = "Rebuild")
                labRebuild.lineImIdx = str(i)

                def rebuildETRImage(event, *args):
                    widgetlineImIdx = event.widget.lineImIdx
                    text = self.currEtr[widgetlineImIdx].getData()
                    position = self.currEtr[widgetlineImIdx].index(tk.INSERT)

                    bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                    self.__renderAfterRebuild(self.subsection,
                                self.imIdx,
                                event.widget.lineImIdx,
                                text,
                                bookPath,
                                lineIdx = widgetlineImIdx)
                    # self.render(shouldScroll = False)
                    # self.currEtr[widgetlineImIdx].focus_force()
                    # self.currEtr[widgetlineImIdx].mark_set("insert", position)
                    # self.__scrollIntoView(event)

                    return "break"

                labETR.lineImIdx = str(i)
                labETR.rebind([ww.currUIImpl.Data.BindID.Keys.shenter], [rebuildETRImage])
                labRebuild.rebind([ww.currUIImpl.Data.BindID.mouse1], [rebuildETRImage])
                labIm.bind(ww.currUIImpl.Data.BindID.mouse2, __showTextOrImage)
                labIm.bind(ww.currUIImpl.Data.BindID.mouse1, self.__scrollIntoView)
                _ucomw.bindChangeColorOnInAndOut(labRebuild)

                labETR.render()
                labRebuild.render()
                label.render()
                labelToScrollTo = label


            if (str(i) == self.latestLineIdxToscrollTo) and label != None:
                self.latestWidgetToscrollTo = labelToScrollTo

            '''
            copy
            '''
            copyLabel = _ucomw.TOCLabelWithClick(self.scrollable_frame, "_copyLine_" + str(i), 
                                                    i + numRowsPre + 1, 1, text = "Copy")
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
                                                    i + numRowsPre + 1, 2, text = "PB")
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
                entryLinesNotesList = fsf.Wr.EntryInfoStructure.readProperty(self.subsection, self.imIdx,
                                    fsf.Wr.EntryInfoStructure.PubProp.entryLinesNotesList,
                                    bookPath)

                if int(self.currLineCopyIdx) <= int(event.widget.lineImIdx):
                    self.currLineCopyIdx = str(int(self.currLineCopyIdx) + 1)

                if entryLinesNotesList.get(str(self.currLineCopyIdx)) != None:
                     fsf.Wr.EntryInfoStructure.addLineNote(self.subsection, 
                                                  self.imIdx,
                                                  entryLinesNotesList[str(self.currLineCopyIdx)],
                                                  bookPath, 
                                                  str(int(event.widget.lineImIdx) - 1))
                self.render()

            pasteLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [pasteLineIdx])
            _ucomw.bindChangeColorOnInAndOut(pasteLabel)
            pasteLabel.render()

            pasteLabel = _ucomw.TOCLabelWithClick(self.scrollable_frame, "_pasteALine_" + str(i), 
                                                    i + numRowsPre + 1, 3, text = "PA")
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
                entryLinesNotesList = fsf.Wr.EntryInfoStructure.readProperty(self.subsection, self.imIdx,
                                                    fsf.Wr.EntryInfoStructure.PubProp.entryLinesNotesList,
                                                    bookPath)

                if int(self.currLineCopyIdx) <= int(event.widget.lineImIdx):
                    self.currLineCopyIdx = str(int(self.currLineCopyIdx) + 1)

                if entryLinesNotesList.get(str(self.currLineCopyIdx)) != None:
                     fsf.Wr.EntryInfoStructure.addLineNote(self.subsection, 
                                                  self.imIdx,
                                                  entryLinesNotesList[str(self.currLineCopyIdx)],
                                                  bookPath, 
                                                  str(event.widget.lineImIdx + 1))
                self.render()

            pasteLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [pasteLineIdx])
            _ucomw.bindChangeColorOnInAndOut(pasteLabel)
            pasteLabel.render()

            '''
            delete
            '''
            deleteLabel = _ucomw.TOCLabelWithClick(self.scrollable_frame, "_deleteLine_" + str(i), 
                                                    i + numRowsPre + 1, 4, text = "Del")
            deleteLabel.lineImIdx = i

            def deleteLineIdx(event, *args):
                bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                deletedStructure = fsf.Wr.EntryInfoStructure.deleteLine(bookPath,
                                                                        self.subsection,
                                                                        self.imIdx,
                                                                        event.widget.lineImIdx)
                if deletedStructure:
                    mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.MathMenuManager)
                    mainManager.renderWithoutScroll()
                    mainManager.moveTocToEntry(self.subsection, self.imIdx)

                try:
                    self.currEtr.pop(str(event.widget.lineImIdx))
                except:
                    pass
                self.render()

            deleteLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [deleteLineIdx])
            _ucomw.bindChangeColorOnInAndOut(deleteLabel)
            deleteLabel.render()

            '''
            note
            '''
            noteLabel = _ucomw.TOCLabelWithClick(self.scrollable_frame, "_notesForLine_" + str(i), 
                                                    i + numRowsPre + 1, 5, text = "N")
            noteLabel.lineImIdx = i
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

            if entryLinesNotesList.get(str(i)) != None:
                noteLabel.configure(foreground="brown")
                shouldBeBrown = True

            noteLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [noteForLineIdx])
            _ucomw.bindChangeColorOnInAndOut(noteLabel, shouldBeBrown)
            noteLabel.render()

    def receiveNotification(self, broadcasterType) -> None:
        if broadcasterType == AddExcerciseLine_BTN:
            lines = fsf.Wr.EntryInfoStructure.readProperty(self.subsection,
                                                       self.imIdx, 
                                                       fsf.Wr.EntryInfoStructure.PubProp.entryLinesList)
            self.lineIdxShownInText = [(str(len(lines) - 1))]
            self.currEtr = _u.Token.NotDef.dict_t.copy()
            self.render()
        if broadcasterType == HideAllETRsWindow_BTN:
            self.lineIdxShownInText = _u.Token.NotDef.list_t.copy()
            self.currEtr = _u.Token.NotDef.dict_t.copy()
            self.render()

    def render(self, widjetObj=None, renderData=..., shouldScroll = True, **kwargs):
        global exImages
        exImages = []
        self.etrTexts =  _u.Token.NotDef.dict_t.copy()

        dummyPreLabel = tk.Label(self.scrollable_frame, height = 1000)
        dummyPreLabel.grid(row = 1, column=0)

        self.etrTexts = _u.Token.NotDef.dict_t.copy()

        if self.currEtr != _u.Token.NotDef.dict_t.copy():
            for k,v in self.currEtr.items():
                self.etrTexts[k] = [self.currEtr[k].getData(),
                                    self.currEtr[k].index(tk.INSERT)]

        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        self.scrollable_frame.focus_force()

        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        entryLinesPath = _upan.Paths.Entry.getAbs(bookPath, self.subsection, self.imIdx)

        fullPathToEntryJSON = _upan.Paths.Entry.JSON.getAbs(bookPath, self.subsection, self.imIdx)

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(fullPathToEntryJSON):
            numLines = len(fsf.Wr.EntryInfoStructure.readProperty(self.subsection,
                                                        self.imIdx, 
                                                        fsf.Wr.EntryInfoStructure.PubProp.entryLinesList))
        else:
            numLines = 0

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryLinesPath):
            self.addExcerciseLines()


        dummyPostLabel = tk.Label(self.scrollable_frame, height = 1000)
        dummyPostLabel.grid(row = 1 + numLines + 1, column=0)


        super().render(widjetObj, renderData, **kwargs)

        if (self.latestWidgetToscrollTo != None) and (shouldScroll):
            self.__scrollIntoView(None, self.latestWidgetToscrollTo)

class ExcerciseRoot(ww.currUIImpl.RootWidget):
    ExcerciseBox = None
    AddExcerciseBTN = None

    def __init__(self, width, height, bindCmd=...):
        super().__init__(width, height, self.bindCmd)    

    def bindCmd(self):
        def __scrollUp(*args):
            if self.ExcerciseBox != None:
                self.ExcerciseBox.canvas.yview_scroll(1, "units")
        def __scrollDown(*args):
            if self.ExcerciseBox != None:
                self.ExcerciseBox.canvas.yview_scroll(-1, "units")
        def __addLine(*args):
            if self.ExcerciseBox != None:
                self.AddExcerciseBTN.cmd()
        return [ww.currUIImpl.Data.BindID.Keys.shdown, 
                ww.currUIImpl.Data.BindID.Keys.shup,
                ww.currUIImpl.Data.BindID.Keys.cmdshs], \
               [__scrollUp, __scrollDown, __addLine]
    pass