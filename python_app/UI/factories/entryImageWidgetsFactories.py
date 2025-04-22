from PIL import Image, ImageOps
import time
import re
from threading import Thread
import os

import UI.widgets_wrappers as ww
import UI.widgets_data as wd
import UI.widgets_facade as wf
import UI.widgets_collection.common as comw

from UI.widgets_collection.common import TOCCanvasWithclick, TOCLabelWithClick, TOCTextWithClickTextOnlyEntry, ImageSize_ETR
from UI.widgets_collection.utils import bindWidgetTextUpdatable, bindOpenOMOnThePageOfTheImage, openVideoOnThePlaceOfTheImage, bindChangeColorOnInAndOut, addExtraIm

import file_system.file_system_facade as fsf
import data.constants as dc
import data.temp as dt
import _utils.pathsAndNames as _upan
import settings.facade as sf
import _utils._utils_main as _u
import outside_calls.outside_calls_facade as ocf

class EntryImagesFactory:
    class __ImageFrame(ww.currUIImpl.Frame):
        def __init__(self, imagePath, subsection, imIdx, 
                    row, column, columnspan,
                    prefix: str,
                    rootWidget,
                    extraOptions = {},
                    bindCmd = lambda *args: (None, None),
                    padding = [0, 0, 0, 0]): 
            renderData = {
                ww.Data.GeneralProperties_ID :{"column" : column, "row" : row, "columnspan" : columnspan},
                ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
            }
            self.subsection = subsection
            self.imIdx = imIdx
            self.imagePath = imagePath
            self.name = "_EntryImageFrame_"
            super().__init__(prefix, 
                            self.name,
                            rootWidget, 
                            renderData,
                            extraOptions,
                            bindCmd,
                            padding)


    class __MainImageFrame(__ImageFrame):
        def __init__(self, imagePath, subsection, imIdx, 
                    row, column, columnspan,
                    prefix: str,
                    rootWidget,
                    extraOptions = {},
                    bindCmd = lambda *args: (None, None),
                    padding = [0, 0, 0, 0]):
            self.subsection = subsection
            self.imIdx = imIdx
            self.imagePath = imagePath
            super().__init__(imagePath, subsection, imIdx, 
                            row, column, columnspan,
                            prefix,
                            rootWidget,
                            extraOptions,
                            bindCmd,
                            padding)

    class __ExtraImageFrame(__MainImageFrame):
        def __init__(self, imagePath, subsection, imIdx, eImIdx,
                    row, column, columnspan,
                    prefix: str,
                    rootWidget,
                    extraOptions = {},
                    bindCmd = lambda *args: (None, None),
                    padding = [0, 0, 0, 0]):
            self.eImIdx = eImIdx
            self.resizeEtr = None
            super().__init__(imagePath, subsection, imIdx, 
                            row, column, columnspan,
                            prefix,
                            rootWidget,
                            extraOptions,
                            bindCmd,
                            padding)

        # def changePosition(self, newImIdx):
        #     for ch in self.getChildren():
        #         print(ch.name)
        #         if "eImIdx" in dir(ch):
        #             ch.eImIdx = str(newImIdx)
        #     self.eImIdx = str(newImIdx)
        #     self.renderData["row"] = int(newImIdx) + 1


    def __getImageResizeFactor(self, eImIdx = None):
        uiResizeEntryIdx = fsf.Data.Sec.imageUIResize(self.subsection)

        uiResizeEntryIdx = fsf.Data.Sec.imageUIResize(self.subsection)

        if eImIdx == None:
            if uiResizeEntryIdx.get(self.imIdx) != None:
                resizeFactor = float(uiResizeEntryIdx[self.imIdx])
            else:
                resizeFactor = 1.0
        else:
            if uiResizeEntryIdx.get(self.imIdx + "_" + str(eImIdx)) != None:
                resizeFactor = float(uiResizeEntryIdx[self.imIdx + "_" + str(eImIdx)])
            else:
                resizeFactor = 1.0
        return resizeFactor

    def __init__(self, subsection, imIdx):
        self.imIdx = imIdx
        self.subsection = subsection

    def __getImageWidget(self, root, imagePath, widgetName, imIdx, subsection,
                    imPad = 0, imageSize = [450, 1000], 
                    row = 0, column = 0, columnspan = 1,
                    resizeFactor = 1.0,
                    bindOpenWindow = True,
                    extraImIdx = _u.Token.NotDef.int_t,
                    leftMove = 0):
        def openImageManager(event, tocBox = None, leftMove = 0, *args):
            imMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                            wf.Wr.MenuManagers.ImagesManager)
            imMenuManger.subsection = event.widget.subsection
            imMenuManger.imIdx = event.widget.imIdx

            width = int(event.widget.width * 1.5) if int(event.widget.width * 1.5) > 720 else 720
            currBookpath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            eImIdx = event.widget.eImIdx
            notePosidx = str(int(eImIdx) + 1) if eImIdx != _u.Token.NotDef.str_t else 0
            notesIm = _upan.Paths.Entry.NoteImage.getAbs(currBookpath,
                                                event.widget.subsection,
                                                event.widget.imIdx,
                                                notePosidx)
            
            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(notesIm):
                im = Image.open(notesIm)
                _, imHeight = im.size
            else:
                imHeight = 30

            height = int(event.widget.height * 1.5) + imHeight + 100

            imMenuManger.show([width, height, leftMove, 0], eImIdx, imHeight)

            if tocBox != None:
                tocBox.widgetToScrollTo = event.widget

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
            pilIm = Image.open(imagePath)
            
            # NOTE: this is how it was done originally. 
            #       No idea why. Whis way added figures are messed up at resize
            # if resizeFactor <= 1.0:
            #     pilIm.thumbnail([i * resizeFactor for i in imageSize], Image.LANCZOS)
            # else:
            origWidth, origHeight = pilIm.size
            newWidth = min(imageSize[0] * resizeFactor, origWidth * resizeFactor)
            changeFactor = (imageSize[0] / origWidth) * resizeFactor
            newHeight = min(changeFactor * origHeight, origHeight * resizeFactor)
            
            pilIm = pilIm.resize([int(newWidth), int(newHeight)], Image.LANCZOS)

            noteImIdx = str(int(extraImIdx) + 1) if extraImIdx != _u.Token.NotDef.int_t else 0
            notes:dict = fsf.Wr.EntryInfoStructure.readProperty(subsection,
                                                        imIdx, 
                                                        fsf.Wr.EntryInfoStructure.PubProp.entryNotesList)
            if notes.get(str(noteImIdx)) != None:
                pilIm = ImageOps.expand(pilIm, border = 2, fill="brown")

            img = ww.currUIImpl.UIImage(pilIm)

            if bindOpenWindow:
                imLabel = TOCCanvasWithclick(root, imIdx = imIdx, subsection = subsection,
                                            prefix = widgetName, image = img, padding = [imPad, 0, 0, 0],
                                            row = row, column = column, columnspan = columnspan,
                                            extraImIdx = extraImIdx, 
                                            resizeFactor = 1 / resizeFactor,
                                            imagePath = imagePath,
                                            makeDrawable = False)
            else:
                imLabel = TOCCanvasWithclick(root, imIdx = imIdx, subsection = subsection,
                                            prefix = widgetName, image = img, padding = [imPad, 0, 0, 0],
                                            row = row, column = column, columnspan = columnspan,
                                            extraImIdx = extraImIdx,
                                            resizeFactor = 1 / resizeFactor,
                                            imagePath = imagePath)
        else:
            img = None
            imLabel = TOCLabelWithClick(root, prefix = widgetName, text = "-1", padding = [imPad, 0, 0, 0],
                                        row = row, column = column, columnspan = columnspan)
            imLabel.eImIdx = extraImIdx

        imLabel.imagePath = imagePath
        imLabel.etrWidget = imLabel

        if bindOpenWindow:
            imLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [lambda e, *args: openImageManager(e, leftMove = leftMove)])

        return imLabel
    
    def produceEntryMainImageWidget(self,
                                rootLabel,
                                imPadLeft,
                                mainImgBindData = None,
                                resizeFactor = 1.0,
                                row = 0,
                                columnspan = 100,
                                column = 0,
                                bindOpenWindow = True,
                                leftMove = 0):
        # mainImage
        resizeFactor *= self.__getImageResizeFactor()

        currBookName = sf.Wr.Manager.Book.getCurrBookName()
        imagePath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBookName,
                                                                       self.subsection,
                                                                       self.imIdx)

        mainWidgetName = _upan.Names.UI.getMainEntryWidgetName(self.subsection, self.imIdx)

        tempLabel = EntryImagesFactory.__MainImageFrame(subsection = self.subsection,
                                                  imIdx = self.imIdx,
                                                  imagePath = imagePath,
                                                  row = row, column = column, columnspan = columnspan,
                                                  prefix = mainWidgetName,
                                                  rootWidget = rootLabel,
                                                  padding = [imPadLeft, 0, 0, 0])

        if mainImgBindData != None:
            tempLabel.rebind(*mainImgBindData)
        
        if fsf.Data.Sec.textOnly(self.subsection).get(self.imIdx) != None:
            textOnly = fsf.Data.Sec.textOnly(self.subsection)[self.imIdx]

            if not textOnly:
                imLabel = self.__getImageWidget(tempLabel, imagePath, mainWidgetName, 
                                            self.imIdx, self.subsection, imPad = 0,
                                            row = 0, column = 1, columnspan = 1,
                                            resizeFactor = resizeFactor, bindOpenWindow = bindOpenWindow,
                                            leftMove = leftMove)
                imLabel.render()
            else:
                text = fsf.Data.Sec.imageText(self.subsection)[self.imIdx]
                imLabel = TOCTextWithClickTextOnlyEntry(tempLabel, 
                                            mainWidgetName,
                                            row = 0, column = 1, columnspan = 1,
                                            text = text,
                                            )
                imLabel.subsection = self.subsection
                imLabel.imIdx = self.imIdx
                imLabel.render()

                def __getText(widget):
                    return fsf.Data.Sec.imageText(widget.subsection)[widget.imIdx]

                def __setText(newText, widget):
                    imageText = fsf.Data.Sec.imageText(widget.subsection)
                    imageText[widget.imIdx] = newText
                    fsf.Data.Sec.imageText(widget.subsection, imageText)
                
                def __changeOnEtrFunc(widget):
                    for w in wd.Data.Reactors.entryChangeReactors.values():
                        if "onTextOnlyTextUpdate" in dir(w):
                            w.onTextOnlyTextUpdate()
                
                def __changeOnLabelBackFunc(widget):
                    for w in wd.Data.Reactors.entryChangeReactors.values():
                        if "onTextOnlyTextUpdate" in dir(w):
                            w.onTextOnlyTextUpdate()

                imLabel.rebind([ww.currUIImpl.Data.BindID.mouse2],
                               [lambda e, g = __getText, 
                                          s = __setText, 
                                          c = __changeOnEtrFunc, 
                                          b = __changeOnLabelBackFunc, *args:
                                                            bindWidgetTextUpdatable(e, g, s, 
                                                                changeOnEtrFunc = c,
                                                                changeOnLabelBackFunc = b)])

            if not fsf.Data.Sec.isVideo(self.subsection):
                bindOpenOMOnThePageOfTheImage(imLabel, self.subsection, self.imIdx)
            else:
                openVideoOnThePlaceOfTheImage(imLabel, self.subsection, self.imIdx)
        return tempLabel

    def __produceEntryExtraImageExtraLabels(self, eImIdx, parentLabel, resizeFactor):
        eImWidgetName = _upan.Names.UI.getExtraEntryWidgetName(self.subsection,
                                                            self.imIdx,
                                                            eImIdx)

        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 0, "columnspan" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        tempEImLabel = ww.currUIImpl.Frame(prefix = eImWidgetName,
                                           name = "_eImFrame_" ,
                                           rootWidget = parentLabel,
                                           renderData = renderData)

        removeEntry = TOCLabelWithClick(tempEImLabel,
                                        text = "[d]",
                                        prefix = "delete_" + eImWidgetName,
                                        row =  eImIdx + 5, 
                                        column = 0,
                                        sticky = ww.currUIImpl.Orientation.NW)
        removeEntry.imIdx = self.imIdx
        removeEntry.subsection = self.subsection
        removeEntry.eImIdx = eImIdx

        def delEIm(event, *args):
            widget:TOCLabelWithClick = event.widget
            fsf.Wr.SectionInfoStructure.removeExtraIm(widget.subsection,
                                                    widget.imIdx,
                                                    eImIdx = widget.eImIdx)
            
            currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            entryFsPath = _upan.Paths.Entry.ExtraImage.getAbs(currBookPath, 
                                                              widget.subsection,
                                                              widget.imIdx,
                                                              widget.eImIdx)

            counter = 0
            while ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryFsPath):
                time.sleep(0.3)
                counter += 1
                if counter > 50:
                    return

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onExtraImDelete" in dir(w):
                    w.onExtraImDelete(widget.subsection, widget.imIdx, widget.eImIdx)
                  

            excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                            wf.Wr.MenuManagers.ExcerciseManager)
            if excerciseManager.shown:
                excerciseManager.show()

        removeEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],[delEIm])

        bindChangeColorOnInAndOut(removeEntry)
        removeEntry.render()

        moveEntryDown = TOCLabelWithClick(tempEImLabel,
                                        text = "[\u2193",
                                        prefix = "up_" + eImWidgetName,
                                        row =  eImIdx + 5, 
                                        column = 1,
                                        sticky = ww.currUIImpl.Orientation.NW)
        moveEntryDown.imIdx = self.imIdx
        moveEntryDown.subsection = self.subsection
        moveEntryDown.eImIdx = eImIdx

        def moveDown(event, *args):
            widget:TOCLabelWithClick = event.widget
            
            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onExtraImMove" in dir(w):
                    w.onExtraImMove(widget.subsection, widget.imIdx, widget.eImIdx, False)

            excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                            wf.Wr.MenuManagers.ExcerciseManager)
            if excerciseManager.shown:
                excerciseManager.show()

        moveEntryDown.rebind([ww.currUIImpl.Data.BindID.mouse1],[moveDown])
        bindChangeColorOnInAndOut(moveEntryDown)
        moveEntryDown.render()

        moveEntryUp = TOCLabelWithClick(tempEImLabel,
                                        text = "\u2191]",
                                        prefix = "down_" + eImWidgetName,
                                        row =  eImIdx + 5, 
                                        column = 2,
                                        sticky = ww.currUIImpl.Orientation.NW)
        moveEntryUp.imIdx = self.imIdx
        moveEntryUp.subsection = self.subsection
        moveEntryUp.eImIdx = eImIdx

        def moveUp(event, *args):
            widget:TOCLabelWithClick = event.widget
            
            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onExtraImMove" in dir(w):
                    w.onExtraImMove(widget.subsection, widget.imIdx, widget.eImIdx, True)

            excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                            wf.Wr.MenuManagers.ExcerciseManager)
            if excerciseManager.shown:
                excerciseManager.show()

        moveEntryUp.rebind([ww.currUIImpl.Data.BindID.mouse1],[moveUp])

        bindChangeColorOnInAndOut(moveEntryUp)
        moveEntryUp.render()

        retake = TOCLabelWithClick(tempEImLabel,
                                        text = "[r]",
                                        prefix = "retake_" + eImWidgetName,
                                        row =  eImIdx + 5, 
                                        column = 3,
                                        sticky = ww.currUIImpl.Orientation.NW)
        retake.imIdx = self.imIdx
        retake.subsection = self.subsection
        retake.eImIdx = eImIdx

        def retakeCmd(event, *args):
            widget = event.widget
            subsection = widget.subsection
            imIdx = widget.imIdx
            eImIdx = widget.eImIdx

            currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            imagePath = _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(currBookPath,
                                                                        subsection,
                                                                        str(imIdx),
                                                                        str(eImIdx))

            msg = "Do you want to retake extra image?"
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

            if not response:
                return

            ocf.Wr.FsAppCalls.deleteFile(imagePath)

            figuresLabelsData = fsf.Data.Sec.figuresLabelsData(subsection)
            figuresData = fsf.Data.Sec.figuresData(subsection)

            if figuresLabelsData.get(f"{imIdx}_{eImIdx}") != None:
                figuresLabelsData.pop(f"{imIdx}_{eImIdx}")
                fsf.Data.Sec.figuresLabelsData(subsection, figuresLabelsData)

            if figuresData.get(f"{imIdx}_{eImIdx}") != None:
                figuresData.pop(f"{imIdx}_{eImIdx}")
                fsf.Data.Sec.figuresData(subsection, figuresData)
            
            pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                wf.Wr.MenuManagers.PdfReadersManager)
            pdfReadersManager.show(subsection = subsection,
                                    imIdx = imIdx,
                                    selector = True,
                                    removePrevLabel = True,
                                    extraImIdx = eImIdx,
                                    withoutRender = True)
            def __cmdAfterImageCreated(imagePath, subsection, imIdx, eImIdx):
                timer = 0

                while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                    time.sleep(0.3)
                    timer += 1

                    if timer > 50:
                        break

                for w in wd.Data.Reactors.entryChangeReactors.values():
                    if "onRetakeAfter" in dir(w):
                        w.onRetakeAfter(subsection, imIdx, eImIdx)
                
            
            t = Thread(target = __cmdAfterImageCreated, args = [imagePath, subsection, imIdx, eImIdx])
            t.start()
            return

        retake.rebind([ww.currUIImpl.Data.BindID.mouse1],
                        [lambda e, *args: retakeCmd(e)])

        bindChangeColorOnInAndOut(retake)
        retake.render()

        def resizeEntryImgCMD(event, *args):
            resizeFactor = event.widget.getData()

            # check if the format is right
            if not re.match("^[0-9]\.[0-9]$", resizeFactor):
                _u.log.autolog(\
                    f"The format of the resize factor '{resizeFactor}'is not correct")
                return
            
            subsection = event.widget.subsection
            imIdx = event.widget.imIdx
            eImIdx = event.widget.eImIdx
            
            uiResizeEntryIdx = fsf.Data.Sec.imageUIResize(subsection)

            if (uiResizeEntryIdx == None) \
                or (uiResizeEntryIdx == _u.Token.NotDef.dict_t):
                uiResizeEntryIdx = {}

            uiResizeEntryIdx[str(imIdx) + "_" + str(eImIdx)] = resizeFactor

            fsf.Data.Sec.imageUIResize(subsection, uiResizeEntryIdx)

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onImageResize" in dir(w):
                    w.onImageResize(subsection, imIdx, event.widget.eImIdx)

            excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                            wf.Wr.MenuManagers.ExcerciseManager)
            if excerciseManager.shown:
                excerciseManager.show()

        changeImSize = ImageSize_ETR(tempEImLabel,
                                    prefix =  "imSize_" + eImWidgetName,
                                    row = eImIdx + 5, 
                                    column = 4,
                                    imIdx = self.imIdx,
                                    text = resizeFactor)
        changeImSize.imIdx = self.imIdx
        changeImSize.eImIdx = eImIdx
        changeImSize.subsection = self.subsection
        changeImSize.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                [lambda e, *args: resizeEntryImgCMD(e)])
        changeImSize.render()
        parentLabel.resizeEtr = changeImSize

        bookCodeProj = TOCLabelWithClick(tempEImLabel,
                                        text = "code: [b",
                                        prefix = "bookCodeProj_" + eImWidgetName,
                                        row =  eImIdx + 6, 
                                        column = 0,
                                        sticky = ww.currUIImpl.Orientation.NE,
                                        columnspan = 3)
        bookCodeProj.imIdx = self.imIdx
        bookCodeProj.subsection = self.subsection
        bookCodeProj.eImIdx = eImIdx

        def openBookCodeProjectCmd(event, *args):
            subsection = event.widget.subsection
            imIdx = event.widget.imIdx
            eImIdx = event.widget.eImIdx

            fullLink = imIdx + "_" + str(eImIdx)
            dt.CodeTemp.currCodeFullLink = fullLink

            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            projectPath = _upan.Paths.Book.Code.getAbs(bookPath)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(projectPath):
                _u.log.autolog("Please add a book code project files.")
                return

            ocf.Wr.IdeCalls.openNewWindow(projectPath)

            bookCodeFiles:dict = fsf.Data.Sec.bookCodeFile(subsection)

            if bookCodeFiles.get(fullLink) != None:
                relFilepath = bookCodeFiles.get(fullLink)
                time.sleep(0.5)
                filepath = os.path.join(projectPath, relFilepath)

                if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(filepath):
                    return

                lines = []
                with open(filepath) as f:
                    lines = f.read().splitlines()
                
                marker = _upan.Names.codeLineMarkerBook(subsection, fullLink)

                for i in range(len(lines)):
                    if marker in lines[i]:
                        ocf.Wr.IdeCalls.openNewTab(filepath, i)
                        return

                ocf.Wr.IdeCalls.openNewTab(filepath)

        bookCodeProj.rebind([ww.currUIImpl.Data.BindID.mouse1],[openBookCodeProjectCmd])
        bindChangeColorOnInAndOut(bookCodeProj)
        bookCodeProj.render()

        subsectionCodeProj = TOCLabelWithClick(tempEImLabel,
                                        text = ", s",
                                        prefix = "subCodeProj_" + eImWidgetName,
                                        row =  eImIdx + 6, 
                                        column = 3,
                                        sticky = ww.currUIImpl.Orientation.NW,
                                        columnspan = 1)
        subsectionCodeProj.imIdx = self.imIdx
        subsectionCodeProj.subsection = self.subsection
        subsectionCodeProj.eImIdx = eImIdx

        def openSubsectionCodeProjectCmd(event, *args):
            subsection = event.widget.subsection
            imIdx = event.widget.imIdx
            eImIdx = event.widget.eImIdx
            fullLink = imIdx + "_" + str(eImIdx)

            dt.CodeTemp.currCodeFullLink = fullLink

            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            codeTemplatePath =_upan.Paths.Book.Code.getSubsectionTemplatePathAbs(bookPath)
            codeSubsectionPath =_upan.Paths.Section.getCodeRootAbs(bookPath,
                                                                    subsection)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(codeSubsectionPath):
                ocf.Wr.FsAppCalls.copyFile(codeTemplatePath, codeSubsectionPath)

            ocf.Wr.IdeCalls.openNewWindow(codeSubsectionPath)

            subsectionCodeFiles:dict = fsf.Data.Sec.subsectionCodeFile(subsection)

            if subsectionCodeFiles.get(fullLink) != None:
                relFilepath = subsectionCodeFiles.get(fullLink)
                time.sleep(0.5)
                filepath = os.path.join(codeSubsectionPath, relFilepath)

                if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(filepath):
                    _u.log.autolog(f"Subsection '{filepath}' file not found.")
                    return

                lines = []
                with open(filepath) as f:
                    lines = f.read().splitlines()
                
                marker = _upan.Names.codeLineMarkerSubsection(subsection, fullLink)

                for i in range(len(lines)):
                    if marker in lines[i]:
                        ocf.Wr.IdeCalls.openNewTab(filepath, i)
                        return

                ocf.Wr.IdeCalls.openNewTab(filepath)

        subsectionCodeProj.rebind([ww.currUIImpl.Data.BindID.mouse1],[openSubsectionCodeProjectCmd])
        bindChangeColorOnInAndOut(subsectionCodeProj)
        subsectionCodeProj.render()

        entryCodeProj = TOCLabelWithClick(tempEImLabel,
                                        text = ", e]",
                                        prefix = "entryCodeProj_" + eImWidgetName,
                                        row =  eImIdx + 6, 
                                        column = 4,
                                        sticky = ww.currUIImpl.Orientation.NW,
                                        columnspan = 1)
        entryCodeProj.imIdx = self.imIdx
        entryCodeProj.subsection = self.subsection
        entryCodeProj.eImIdx = eImIdx

        def openEntryCodeProjectCmd(event, *args):
            subsection =  event.widget.subsection
            imIdx =  event.widget.imIdx
            eImIdx =  event.widget.eImIdx

            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

            entryPath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryPath):
                fsf.Wr.EntryInfoStructure.createStructure(bookPath, subsection, imIdx)

            entryCodeProjFilepath = _upan.Paths.Entry.getCodeProjAbs(bookPath, subsection, imIdx)
            codeFolderbaseName = _upan.Names.codeProjectBaseName()
            entryCodeProjFilepath = entryCodeProjFilepath.replace(codeFolderbaseName, 
                                                                    codeFolderbaseName + "_" + str(eImIdx))

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryCodeProjFilepath):
                codeProjTemplatePath = \
                    _upan.Paths.Book.Code.getEntryTemplatePathAbs(bookPath)
                ocf.Wr.FsAppCalls.copyFile(codeProjTemplatePath, entryCodeProjFilepath)

            ocf.Wr.IdeCalls.openNewWindow(entryCodeProjFilepath)

        entryCodeProj.rebind([ww.currUIImpl.Data.BindID.mouse1],[openEntryCodeProjectCmd])
        bindChangeColorOnInAndOut(entryCodeProj)
        entryCodeProj.render()

        addProof = TOCLabelWithClick(tempEImLabel,
                                        text = "[AddPr",
                                        prefix = "addProof_" + eImWidgetName,
                                        row =  eImIdx + 7, 
                                        column = 0,
                                        sticky = ww.currUIImpl.Orientation.NW,
                                        columnspan = 2)
        addProof.imIdx = self.imIdx
        addProof.subsection = self.subsection
        addProof.eImIdx = eImIdx

        def addExtraImProofCmd(event, *args):
            widget = event.widget
            addExtraIm(widget.subsection, widget.imIdx, 
                        True, event = event)

        addProof.rebind([ww.currUIImpl.Data.BindID.mouse1],
                        [lambda e, *args: addExtraImProofCmd(e)])
        bindChangeColorOnInAndOut(addProof)
        addProof.render()

        addEIm = TOCLabelWithClick(tempEImLabel,
                                        text = ", AddImage]",
                                        prefix = "addEIm_" + eImWidgetName,
                                        row =  eImIdx + 7, 
                                        column = 2,
                                        sticky = ww.currUIImpl.Orientation.NW,
                                        columnspan = 3)
        addEIm.imIdx = self.imIdx
        addEIm.subsection = self.subsection
        addEIm.eImIdx = eImIdx

        def addExtraImCmd(event, *args):
            widget = event.widget
            addExtraIm(widget.subsection, widget.imIdx, 
                        False, event = event)

        addEIm.rebind([ww.currUIImpl.Data.BindID.mouse1],
                        [lambda e, *args: addExtraImCmd(e)])
        bindChangeColorOnInAndOut(addEIm)
        addEIm.render()

        return tempEImLabel

    def produceEntryExtraImageFrame(self,
                                    rootLabel,
                                    eImIdx,
                                    createExtraWidgets,
                                    bindOpenWindow,
                                    resizeFactor,
                                    imPadLeft,
                                    leftMove):
        currBookName = sf.Wr.Manager.Book.getCurrBookName()

        uiResizeEntryIdx = fsf.Data.Sec.imageUIResize(self.subsection)
        shouldResetResizeFactor = False

        if (str(self.imIdx) + "_" + str(eImIdx)) in list(uiResizeEntryIdx.keys()):
            resizeFactor *= float(uiResizeEntryIdx[self.imIdx + "_" + str(eImIdx)])
        else:
            resizeFactor *= 1.0

        extraImFilepath = _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(currBookName,
                                                                            self.subsection,
                                                                            self.imIdx,
                                                                            eImIdx)

        eImWidgetName = _upan.Names.UI.getExtraEntryWidgetName(self.subsection,
                                                            self.imIdx,
                                                            eImIdx)

        def extraImtextUpdate(event, *args):
            eImTextDict = fsf.Data.Sec.extraImagesDict(event.widget.subsection)
            eImTextList = eImTextDict[event.widget.imIdx]
            text = eImTextList[event.widget.eImIdx]

            eimLabel = comw.MultilineText_ETR(event.widget.root, 
                                            eImWidgetName, 
                                            row = event.widget.row,
                                            column = event.widget.column,
                                            imLineIdx = None, 
                                            text = text)
            eimLabel.subsection = event.widget.subsection
            eimLabel.imIdx = event.widget.imIdx
            eimLabel.eImIdx = event.widget.eImIdx
            event.widget.hide()

            def __getBack(eimLabel, widget):
                newText = eimLabel.getData()
                eImTextDict = fsf.Data.Sec.extraImagesDict(eimLabel.subsection)
                eImTextList = eImTextDict[eimLabel.imIdx]
                eImTextList[eimLabel.eImIdx] = newText
                fsf.Data.Sec.extraImagesDict(eimLabel.subsection, eImTextDict)
                
                eimLabel.hide()
                widget.render()

            eimLabel.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                                                        [lambda *args: __getBack(eimLabel, event.widget)])
            eimLabel.render()

        #NOTE: we add one since we have main image already
        mainRow = int(eImIdx) + 1

        extraImFrame = EntryImagesFactory.__ExtraImageFrame(extraImFilepath,
                                                            self.subsection,
                                                            self.imIdx,
                                                            eImIdx,
                                                            row = mainRow, column = 0, columnspan = 1,
                                                            rootWidget = rootLabel, 
                                                            prefix = eImWidgetName,
                                                            padding = [imPadLeft, 0, 0, 0])

        eImLabel = self.__getImageWidget(extraImFrame, extraImFilepath, eImWidgetName, 
                                    self.imIdx, self.subsection, imPad = 0,
                                    row = 0, column = 1, columnspan = 1,
                                    resizeFactor = resizeFactor,
                                    extraImIdx = eImIdx,
                                    bindOpenWindow = bindOpenWindow,
                                    leftMove = leftMove)
        eImLabel.subsection = self.subsection
        eImLabel.imIdx = self.imIdx
        eImLabel.eImIdx = eImIdx

        bindOpenOMOnThePageOfTheImage(eImLabel, self.subsection, self.imIdx, str(eImIdx))
        eImLabel.rebind([ww.currUIImpl.Data.BindID.mouse2],
                        [extraImtextUpdate])
        eImLabel.render()
        

        if createExtraWidgets:
            extraImExtraWidgets = self.__produceEntryExtraImageExtraLabels(eImIdx = eImIdx, 
                                                                    parentLabel = extraImFrame,
                                                                    resizeFactor = resizeFactor)
            extraImExtraWidgets.render()

        if shouldResetResizeFactor:
            resizeFactor = None
            shouldResetResizeFactor = False

        return extraImFrame

    def produceEntryExtraImagesWidgets(self,
                                rootLabel,
                                skippConditionFn = lambda *args: False,
                                createExtraWidgets = True,
                                bindOpenWindow = True,
                                resizeFactor = 1.0,
                                imPadLeft = 0,
                                leftMove = 0):
        outLabels = []

        # extraImages
        if self.imIdx in list(fsf.Data.Sec.extraImagesDict(self.subsection).keys()):
            extraImages = fsf.Data.Sec.extraImagesDict(self.subsection)[self.imIdx]

            for eImIdx in range(0, len(extraImages)):
                if skippConditionFn(self.subsection, self.imIdx, eImIdx):
                    continue
                else:
                    #NOTE: this allows to have extra images to have separate roots
                    rl = rootLabel[eImIdx] if type(rootLabel) == list else rootLabel

                    extraImFrame = self.produceEntryExtraImageFrame(rl,
                                                                    eImIdx,
                                                                    createExtraWidgets,
                                                                    bindOpenWindow,
                                                                    resizeFactor,
                                                                    imPadLeft = imPadLeft,
                                                                    leftMove = leftMove)
                    extraImFrame.render()
                    outLabels.append(extraImFrame)

        return outLabels

