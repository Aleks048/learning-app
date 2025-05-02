from PIL import Image
import time
import re
from threading import Thread
import os

import UI.widgets_wrappers as ww
import UI.widgets_data as wd
import UI.widgets_facade as wf

from UI.factories.entryImageWidgetsFactories import EntryImagesFactory
from UI.widgets_collection.common import TOCLabelWithClick, ImageSize_ETR, TOCLabelWithClickEntry, EntryShowPermamentlyCheckbox, TOCLabelWithClickGroup, TOCFrame, ImageGroupOM
from UI.widgets_collection.utils import bindWidgetTextUpdatable, bindOpenOMOnThePageOfTheImage, bindChangeColorOnInAndOut, addExtraIm, getEntryImg, getGroupImg

import file_system.file_system_facade as fsf
import data.temp as dt
import _utils.pathsAndNames as _upan
import settings.facade as sf
import _utils._utils_main as _u
import outside_calls.outside_calls_facade as ocf
import generalManger.generalManger as gm
import tex_file.tex_file_facade as tff



class EntryFrameManager:
    def __init__(self, entryFrame, subsection, imIdx, widgetFactory):
        self.factory = widgetFactory

        self.subsection = subsection
        self.imIdx = imIdx

        self.entryFrame = entryFrame
        self.groupFrame = None
        self.rowFrame1 = None

        self.fullMoveWidget = None
        self.uiResizeEtr = None
        self.latexEntryImage = None

        self.rowFrame2 = None
        self.linksFrameManager = None
        self.imagesFrame = None
        self.imagesFrameScroll = None

        self.imagesShown = False

        self.mainImLabel = None
        self.extraImLabels = None

    def changeFullMoveColor(self, default):
        if self.fullMoveWidget == None:
            return
        if default:
            self.fullMoveWidget.changeColor("white")
            bindChangeColorOnInAndOut(self.fullMoveWidget, False)
        else:
            self.fullMoveWidget.changeColor("brown")
            bindChangeColorOnInAndOut(self.fullMoveWidget, True)

    def alwaysShow(self):
        tocWImageDict = fsf.Data.Sec.tocWImageDict(self.subsection)
        if tocWImageDict == _u.Token.NotDef.dict_t:
            alwaysShow = False
        else:
            alwaysShow = True if tocWImageDict[self.imIdx] != "0" else False
        return alwaysShow

    def updateMainImage(self):
        if self.mainImLabel != None:
            self.mainImLabel.destroy()
            self.__setMainImage()
    
    def updateEntryImage(self):
        if self.latexEntryImage != None:
            self.latexEntryImage.updateLabel()

    def __getExtraImageFrame(self, eImIdx):
        entryImagesFactory = EntryImagesFactory(self.subsection, self.imIdx)
        extraImFrame = entryImagesFactory.produceEntryExtraImageFrame(rootLabel = self.imagesFrameScroll.scrollable_frame,
                                                                      eImIdx = int(eImIdx),
                                                                      imPadLeft = 0,
                                                                      leftMove = 0,
                                                                      createExtraWidgets = True,
                                                                      resizeFactor = 1.0,
                                                                      bindOpenWindow = True)
        return extraImFrame

    def updateExtraImage(self, eImIdx):
        eImFrameIdx = self.__findFrameIdxByEImIdx(eImIdx)
        self.replaceExtraImage(eImFrameIdx, eImFrameIdx)
    
    def replaceExtraImage(self, origEImFrameIdx, newEImFrameIdx):
        extraImFrame = self.__getExtraImageFrame(self.extraImLabels[int(newEImFrameIdx)].eImIdx)
        
        self.extraImLabels[int(origEImFrameIdx)].hide()
        self.extraImLabels[int(origEImFrameIdx)] = extraImFrame
        self.extraImLabels[int(origEImFrameIdx)].render()
    
    def __updateEImFrameEImIdx(self, frameIdx, newEImIdx):
        self.extraImLabels[frameIdx].eImIdx = newEImIdx
        for ch in self.extraImLabels[frameIdx].getChildren():
            ch.eImIdx = newEImIdx
            for gch in ch.getChildren():
                gch.eImIdx = newEImIdx

    def deleteExtraImage(self, eImIdx):
        for i in range(len(self.extraImLabels)):
            if self.extraImLabels[i].eImIdx == int(eImIdx):
                frameIdx = i
                self.extraImLabels[i].destroy()
            elif self.extraImLabels[i].eImIdx > int(eImIdx):
                newEImIdx = str(int(self.extraImLabels[i].eImIdx) - 1)
                self.__updateEImFrameEImIdx(i, newEImIdx)

        self.extraImLabels.pop(frameIdx)

    def addExtraImIdx(self, eImIdx):
        if self.extraImLabels != None:
            extraImFrame = self.__getExtraImageFrame(eImIdx)
            extraImFrame.render()
            self.extraImLabels.append(extraImFrame)
            return extraImFrame

    def __findFrameIdxByEImIdx(self, eImIdx):
        for i in range(len(self.extraImLabels)):
            if int(self.extraImLabels[i].eImIdx) == int(eImIdx):
                return i
        return _u.Token.NotDef.int_t

    def moveExtraIm(self, eImIdx, moveUp:bool):
        if moveUp:
            delta = -1
        else:
            delta = 1

        origFrameIdx = self.__findFrameIdxByEImIdx(eImIdx)

        newExtraImFrameIdx = origFrameIdx + delta

        if newExtraImFrameIdx < 0:
            return
        if newExtraImFrameIdx >= len(self.extraImLabels):
            return

        origEImIdx = int(self.extraImLabels[int(origFrameIdx)].eImIdx)
        newEImIdx = int(self.extraImLabels[int(newExtraImFrameIdx)].eImIdx)

        if origEImIdx == _u.Token.NotDef.int_t\
            or newEImIdx == _u.Token.NotDef.str_t:
            _u.log.autolog(f"Wrong extra image index from frame {origEImIdx} {newEImIdx}.")
            return

        fsf.Wr.SectionInfoStructure.moveExtraIm(self.subsection,
                                                self.imIdx,
                                                eImIdx = origEImIdx,
                                                destEimIdx = newEImIdx)

        self.updateExtraImage(origEImIdx)
        self.updateExtraImage(newEImIdx)

        return self.extraImLabels[int(newExtraImFrameIdx)]

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


    def __setMainImage(self, imPadLeft = 120):
        entryImagesFactory = EntryImagesFactory(self.subsection, self.imIdx)  
        imLabel = entryImagesFactory.produceEntryMainImageWidget(self.imagesFrameScroll.scrollable_frame,
                                                            imPadLeft = imPadLeft,
                                                            resizeFactor = 1.0)

        imLabel.render()
        self.mainImLabel = imLabel


    def __setExtraImages(self, createExtraWidgets, imPadLeft = 0):
        def skipProofAndExtra(subsection, imIdx, exImIdx):
            extraImages = fsf.Data.Sec.extraImagesDict(subsection)[imIdx]
            eImText = extraImages[exImIdx]
            return (("proof" in eImText.lower()) and (not dt.AppState.ShowProofs.getData("fakeToken")))\
                    or (("extra") in eImText.lower())

        entryImagesFactory = EntryImagesFactory(self.subsection, self.imIdx)   
        exImLabels = entryImagesFactory.produceEntryExtraImagesWidgets(rootLabel = self.imagesFrameScroll.scrollable_frame,
                                                        skippConditionFn = skipProofAndExtra,
                                                        createExtraWidgets = createExtraWidgets,
                                                        imPadLeft = imPadLeft)
        self.extraImLabels = exImLabels

        for l in exImLabels:
            l.render()

    def updateResizeEtrText(self, eImIdx = _u.Token.NotDef.str_t):
        if eImIdx == _u.Token.NotDef.str_t:
            newResizeFactor = fsf.Data.Sec.imageUIResize(self.subsection)[self.imIdx]
            self.uiResizeEtr.setData(newResizeFactor)
        else:
            newResizeFactor = fsf.Data.Sec.imageUIResize(self.subsection)[self.imIdx + "_" + str(eImIdx)]
            if self.extraImLabels[eImIdx].resizeEtr != None:
                self.extraImLabels[eImIdx].resizeEtr.setData(newResizeFactor)

    def showRow2(self):   
        self.rowFrame2.render()
        self.imagesShown = True   

    def hideRow2(self):
        self.rowFrame2.hide()
        self.imagesShown = False   

    def showImages(self, mainImPadLeft = 120, eImPadLeft = 0, createExtraImagesExtraWidgets = True):
        self.imagesShown = True   

        # if self.fullMoveWidget != None:
        #     self.fullMoveWidget.clicked = True 

        self.__setMainImage(imPadLeft = mainImPadLeft)
        self.__setExtraImages(createExtraWidgets = createExtraImagesExtraWidgets,
                              imPadLeft = eImPadLeft)

        scrollHeight = 0
        for ch in self.imagesFrameScroll.scrollable_frame.getChildren():
            scrollHeight += ch.getHeight()

        maxHeight = 300

        self.imagesFrameScroll.maxHeight = scrollHeight
        self.imagesFrameScroll.setCanvasHeight(min(scrollHeight, maxHeight))
        self.imagesFrameScroll.render()
        self.imagesFrame.render()

    def setFullImageLabelNotClicked(self):
        if self.fullMoveWidget != None:
            self.fullMoveWidget.clicked = False 

    def remove(self):
        self.entryFrame.destroy()

    def hideImages(self):
        self.imagesShown = False
        for ch in self.imagesFrame.getChildren().copy():
            ch.destroy()
        self.imagesFrame.hide()
        self.setFullImageLabelNotClicked()

class EntryWidgetFactory:
    class EntryUIs:
        class __EntryUIData:
            def __init__(self, name, column, cmd, row = 0) -> None:
                self.name = name
                self.column = column
                self.row = row
                self.cmd = cmd

        def __init__(self):
            raise NotImplementedError()

    def __init__(self, subsection, imIdx, topPad, leftPad):
        self.subsection = subsection
        self.imIdx = imIdx
        self.frame = None
        self.__nameIdPrefix = _upan.Names.Entry.getEntryNameID(self.subsection, self.imIdx)
        self.EntryUIs = self.EntryUIs()

        self.topPad = topPad
        self.leftPad = leftPad

        self.entryFrameManager = None

    def getPrefixID(self):
        return self.__nameIdPrefix

    def produceShiftLabelWidget(self, parentWidget):
        def shiftEntryCmd(event, *args):
            widget = event.widget
            fsf.Wr.SectionInfoStructure.shiftEntryUp(widget.subsection,
                                                        widget.imIdx)
            
            fsf.Data.Book.subsectionOpenInTOC_UI = self.subsection
            fsf.Data.Book.entryImOpenInTOC_UI = str(int(widget.imIdx) + 1)
            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onEntryShift" in dir(w):
                    w.onEntryShift(widget.subsection, widget.imIdx)

        shiftEntry = TOCLabelWithClick(parentWidget,
                                                text = self.EntryUIs.shift.name,
                                                prefix = "contentShiftEntry" + self.__nameIdPrefix,
                                                row = self.EntryUIs.shift.row, 
                                                column = self.EntryUIs.shift.column)
        shiftEntry.imIdx = self.imIdx
        shiftEntry.subsection = self.subsection
        shiftEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [shiftEntryCmd])
        bindChangeColorOnInAndOut(shiftEntry)
        return shiftEntry

    def produceLeadingEntryEtrWidget(self, parentWidget):
        def changeLeadingEntryCmd(event, subsection, imIdx,  *args):
            widget = event.widget

            leadingEntryIdx = widget.getData()

            leadingEntry = fsf.Data.Sec.leadingEntry(subsection)

            if str(leadingEntryIdx) == _u.Token.NotDef.str_t:
                if leadingEntry.get(imIdx) != None:
                    leadingEntry.pop(imIdx)
            else:
                leadingEntry[imIdx] = leadingEntryIdx

            fsf.Data.Sec.leadingEntry(subsection, leadingEntry)
            
            imagesGroupDict = fsf.Data.Sec.imagesGroupDict(subsection)

            if str(leadingEntryIdx) == _u.Token.NotDef.str_t:
                imagesGroupDict[imIdx] = 0
            else:
                imagesGroupDict[imIdx] = imagesGroupDict[leadingEntryIdx]

            fsf.Data.Sec.imagesGroupDict(subsection, imagesGroupDict)

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onSetLeadingEntry" in dir(w):
                    w.onSetLeadingEntry(widget.subsection, widget.imIdx)

        leadingEntryText = _u.Token.NotDef.str_t

        if fsf.Data.Sec.leadingEntry(self.subsection).get(self.imIdx) != None:
            leadingEntryIdx = fsf.Data.Sec.leadingEntry(self.subsection)[self.imIdx]

            leadingEntryText = leadingEntryIdx

        leadingEntry = ImageSize_ETR(parentWidget,
                                            prefix = "leadingEntry_" + self.__nameIdPrefix,
                                            row = 0, 
                                            column = self.EntryUIs.leadingEntry.column,
                                            imIdx = self.imIdx,
                                            text = leadingEntryText)
        
        leadingEntry.imIdx = self.imIdx
        leadingEntry.subsection = self.subsection
        leadingEntry.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                                [lambda e, *args: changeLeadingEntryCmd(e, self.subsection, self.imIdx)])
        return leadingEntry

    def produceChangeImSizeWidget(self, parentWidget):
        def resizeEntryImgCMD(event, *args):
            resizeFactor = event.widget.getData()

            # check if the format is right
            if not re.match("^[0-9]\.[0-9]$", resizeFactor):
                _u.log.autolog(\
                    f"The format of the resize factor '{resizeFactor}'is not correct")
                return
            
            subsection = event.widget.subsection
            imIdx = event.widget.imIdx
            
            uiResizeEntryIdx = fsf.Data.Sec.imageUIResize(subsection)

            if (uiResizeEntryIdx == None) \
                or (uiResizeEntryIdx == _u.Token.NotDef.dict_t):
                uiResizeEntryIdx = {}

            uiResizeEntryIdx[imIdx] = resizeFactor

            fsf.Data.Sec.imageUIResize(subsection, uiResizeEntryIdx)
            msg = f"After resize of {subsection} {imIdx}"
            ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onImageResize" in dir(w):
                    w.onImageResize(subsection, imIdx, None)

        uiResizeEntryIdx = fsf.Data.Sec.imageUIResize(self.subsection)

        if self.imIdx in list(uiResizeEntryIdx.keys()):
            resizeFactor = float(uiResizeEntryIdx[self.imIdx])
        else:
            resizeFactor = 1.0

        changeImSize = ImageSize_ETR(parentWidget,
                                        prefix = "contentUpdateEntryText" + self.__nameIdPrefix,
                                        row = 0, 
                                        column = self.EntryUIs.changeImSize.column,
                                        imIdx = self.imIdx,
                                        text = resizeFactor)
        changeImSize.imIdx = self.imIdx
        changeImSize.subsection = self.subsection
        changeImSize.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                [resizeEntryImgCMD])
        return changeImSize

    def produceRemoveEntryWidget(self, parentWidget):
        def removeEntryCmd(event, *args):
            widget = event.widget
            fsf.Wr.SectionInfoStructure.removeEntry(widget.subsection, widget.imIdx)

            def __afterDeletion(subsection, imIdx, *args):
                timer = 0
                while fsf.Data.Sec.figuresLabelsData(subsection).get(imIdx) != None:
                    time.sleep(0.3)
                    timer += 1
                    if timer > 50:
                        break

                for w in wd.Data.Reactors.entryChangeReactors.values():
                    if "onEntryDelete" in dir(w):
                        w.onEntryDelete(subsection, imIdx)

            t = Thread(target = __afterDeletion, args = [widget.subsection, widget.imIdx])
            t.start()

        removeEntry = TOCLabelWithClick(parentWidget,
                                        text = self.EntryUIs.delete.name,
                                        prefix = "contentRemoveEntry" + self.__nameIdPrefix,
                                        row = 0, 
                                        column = self.EntryUIs.delete.column)
        removeEntry.imIdx = self.imIdx
        removeEntry.subsection = self.subsection
        removeEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [removeEntryCmd])
        bindChangeColorOnInAndOut(removeEntry)
        return removeEntry

    def produceCopyEntryWidget(self, parentWidget):
        def copyEntryCmd(event, *args):
            widget = event.widget

            dt.UITemp.Copy.subsection = widget.subsection
            dt.UITemp.Copy.imIdx = widget.imIdx
            dt.UITemp.Copy.cut = False

        def cutEntryCmd(event, *args):
            widget = event.widget

            dt.UITemp.Copy.subsection = widget.subsection
            dt.UITemp.Copy.imIdx = widget.imIdx
            dt.UITemp.Copy.cut = True

        copyEntry = TOCLabelWithClick(parentWidget,
                                                text = self.EntryUIs.copy.name,
                                                prefix = "contentCopyEntry" + self.__nameIdPrefix,
                                                row = 0, 
                                                column = self.EntryUIs.copy.column)
        copyEntry.imIdx = self.imIdx
        copyEntry.subsection = self.subsection
        copyEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [copyEntryCmd])
        copyEntry.rebind([ww.currUIImpl.Data.BindID.shmouse1],
                            [cutEntryCmd])

        bindChangeColorOnInAndOut(copyEntry)
        return copyEntry

    def producePasteEntryWidget(self, parentWidget):
        def pasteEntryCmd(event, *args):
            widget = event.widget

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onPaste" in dir(w):
                    w.onPaste(widget.subsection, widget.imIdx)

        pasteAfterEntry = TOCLabelWithClick(parentWidget,
                                                text = self.EntryUIs.pasteAfter.name,
                                                prefix = "contentPasteAfterEntry" + self.__nameIdPrefix,
                                                row = 0, 
                                                column = self.EntryUIs.pasteAfter.column)
        pasteAfterEntry.imIdx = self.imIdx
        pasteAfterEntry.subsection = self.subsection

        pasteAfterEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [pasteEntryCmd])        
        bindChangeColorOnInAndOut(pasteAfterEntry) 

        return pasteAfterEntry

    def produceShowLinksForEntry(self, parentWidget):
        def showLinksForEntryCmd(e, manager):
            linksFrmaeManger = manager.linksFrameManager
            linksFrmaeManger.processChangeLinksViewStatusChange()        

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onLinksShow" in dir(w):
                    w.onLinksShow(e.widget.subsection, e.widget.imIdx, linksFrmaeManger.linksShown)

        showLinksForEntry = TOCLabelWithClick(parentWidget,
                                                text = self.EntryUIs.showLinks.name,
                                                prefix = "contentShowLinksForEntry" + self.__nameIdPrefix,
                                                row = 0, 
                                                column = self.EntryUIs.showLinks.column)
        showLinksForEntry.imIdx = self.imIdx
        showLinksForEntry.subsection = self.subsection

        showLinksForEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                    [lambda e, lf = self.entryFrameManager, *args: showLinksForEntryCmd(e, lf)])

        linkExist = self.imIdx in list(fsf.Data.Sec.imGlobalLinksDict(self.subsection).keys())

        if linkExist:
            showLinksForEntry.changeColor("brown")

        bindChangeColorOnInAndOut(showLinksForEntry, shouldBeBrown = linkExist)
        return showLinksForEntry

    def produceShowProof(self, parentWidget):
        def openProofsMenu(event, *args):
            prMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.ProofsManager)

            event.widget.shouldShowProofMenu = not event.widget.shouldShowProofMenu

            if (event.widget.shouldShowProofMenu):
                prMenuManger.show(subsection =  event.widget.subsection, imIdx = event.widget.imIdx)
            else:
                prMenuManger.hide(subsection =  event.widget.subsection, imIdx = event.widget.imIdx)

        tarOpenProofsUIEntry = TOCLabelWithClick(parentWidget, 
                                    text = self.EntryUIs.proof.name, 
                                    prefix = "contentGlLinksTSubsectionProof_" + self.__nameIdPrefix,
                                    row = 0, 
                                    column = 5)
        tarOpenProofsUIEntry.changeColor("brown")

        tarOpenProofsUIEntry.imIdx = self.imIdx
        tarOpenProofsUIEntry.subsection = self.subsection
        tarOpenProofsUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                    [openProofsMenu])
        bindChangeColorOnInAndOut(tarOpenProofsUIEntry)
        return tarOpenProofsUIEntry

    def produceCopyTextToMemWidget(self, parentWidget):
        def copyTextToMemCmd(event, *args):
            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onCopyTextToMem" in dir(w):
                    w.onCopyTextToMem(event.widget.subsection, event.widget.imIdx)

        copyTextToMem = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.copyText.name, 
                                        prefix = "contentCopyTextToMem" + self.__nameIdPrefix,
                                        row = self.EntryUIs.copyText.row, 
                                        column = self.EntryUIs.copyText.column,
                                        columnspan = 1)
        copyTextToMem.imIdx = self.imIdx
        copyTextToMem.subsection = self.subsection
        copyTextToMem.rebind([ww.currUIImpl.Data.BindID.mouse1],
                             [copyTextToMemCmd])
        bindChangeColorOnInAndOut(copyTextToMem)
        return copyTextToMem

    def produceRetakeImageWidget(self, parentWidget):
        def retakeImageCmd(event, *args):
            widget = event.widget
            subsection = widget.subsection
            imIdx = widget.imIdx

            currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            
            msg = "Do you want to retake entry image?"
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

            if not response:
                return

            imagePath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBookPath,
                                                                        subsection,
                                                                        str(imIdx))
            ocf.Wr.FsAppCalls.deleteFile(imagePath)
            figuresLabelsData = fsf.Data.Sec.figuresLabelsData(subsection)
            figuresData = fsf.Data.Sec.figuresData(subsection)

            if figuresLabelsData.get(str(imIdx)) != None:
                figuresLabelsData.pop(str(imIdx))
            
            if figuresData.get(str(imIdx)) != None:
                figuresData.pop(str(imIdx))
            

            fsf.Data.Sec.figuresLabelsData(subsection, figuresLabelsData)
            fsf.Data.Sec.figuresData(subsection, figuresData)

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onRetakeBefore" in dir(w):
                    w.onRetakeBefore(subsection, imIdx)

            def __cmdAfterImageCreated(subsection, imIdx):
                timer = 0

                while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                    time.sleep(0.3)
                    timer += 1

                    if timer > 50:
                        break
                
                
                for w in wd.Data.Reactors.entryChangeReactors.values():
                    if "onRetakeAfter" in dir(w):
                        w.onRetakeAfter(subsection, imIdx)

            t = Thread(target = __cmdAfterImageCreated, args = [subsection, imIdx])
            t.start()

        retakeImageForEntry = TOCLabelWithClick(parentWidget,
                                                text =  self.EntryUIs.retake.name,
                                                prefix = "contentRetakeImageForEntry" + self.__nameIdPrefix,
                                                row = 0, 
                                                column =  self.EntryUIs.retake.column)
        retakeImageForEntry.imIdx = self.imIdx
        retakeImageForEntry.subsection = self.subsection
        retakeImageForEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                    [retakeImageCmd])
        bindChangeColorOnInAndOut(retakeImageForEntry)
        return retakeImageForEntry

    def produceAddExtraImageWidget(self, parentWidget):
        def addExtraImCmd(event, *args):
            widget = event.widget
            addExtraIm(widget.subsection, widget.imIdx, False)

        addExtraImage = TOCLabelWithClick(parentWidget, 
                                            text = self.EntryUIs.addExtra.name,
                                            prefix = "contentAddExtraImageEntry" + self.__nameIdPrefix,
                                            row = 0, 
                                            column = self.EntryUIs.addExtra.column)
        addExtraImage.imIdx = self.imIdx
        addExtraImage.subsection = self.subsection
        addExtraImage.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [addExtraImCmd])
        bindChangeColorOnInAndOut(addExtraImage)
        return addExtraImage

    def produceAddProofImageWidget(self, parentWidget):
        def addExtraImProofCmd(event, *args):
            widget = event.widget
            addExtraIm(widget.subsection, widget.imIdx, True)

        addProofImage = TOCLabelWithClick(parentWidget, 
                                            text = self.EntryUIs.addProof.name,
                                            prefix = "contentAddExtraProofEntry" + self.__nameIdPrefix,
                                            row = 0, 
                                            column = self.EntryUIs.addProof.column)
        addProofImage.imIdx = self.imIdx
        addProofImage.subsection = self.subsection
        addProofImage.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [addExtraImProofCmd])
        bindChangeColorOnInAndOut(addProofImage)
        return addProofImage

    def produceCopyLinkWidget(self, parentWidget):
        def copyGlLinkCmd(event, *args):
            widget = event.widget
            dt.UITemp.Link.subsection = widget.subsection
            dt.UITemp.Link.imIdx = widget.imIdx
        
        copyLinkEntry = TOCLabelWithClick(parentWidget, 
                                            text = self.EntryUIs.copyLink.name,
                                            prefix = "contentCopyGlLinkEntry" + self.__nameIdPrefix,
                                            row = 0, 
                                            column = self.EntryUIs.copyLink.column)
        copyLinkEntry.imIdx = self.imIdx
        copyLinkEntry.subsection = self.subsection
        copyLinkEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [copyGlLinkCmd])
        bindChangeColorOnInAndOut(copyLinkEntry)
        return copyLinkEntry
    
    def producePasteLinkEntryWidget(self, parentWidget):
        def pasteGlLinkCmd(event, *args):
            widget = event.widget
            sourceSubsection = widget.subsection
            sourceTopSection = sourceSubsection.split(".")[0]
            sourceImIdx = widget.imIdx
            targetSubsection = dt.UITemp.Link.subsection
            targetImIdx = dt.UITemp.Link.imIdx

            excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.ExcerciseManager)
            excerciseWidgetShown = excerciseManager.shown

            if targetSubsection != _u.Token.NotDef.str_t\
                and targetImIdx != _u.Token.NotDef.str_t:
                gm.GeneralManger.AddLink(f"{targetSubsection}.{targetImIdx}",
                                        sourceSubsection,
                                        sourceImIdx,
                                        sourceTopSection)

            if excerciseWidgetShown:
                excerciseManager.show()
            
            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onPasteLink" in dir(w):
                    w.onPasteLink()


        pasteLinkEntry = TOCLabelWithClick(parentWidget,
                                            text = self.EntryUIs.pasteLink.name,
                                            prefix = "contentPasteGlLinkEntry" + self.__nameIdPrefix,
                                            row = 0, 
                                            column = self.EntryUIs.pasteLink.column)
        pasteLinkEntry.imIdx = self.imIdx
        pasteLinkEntry.subsection = self.subsection
        pasteLinkEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [pasteGlLinkCmd])
        bindChangeColorOnInAndOut(pasteLinkEntry)
        return pasteLinkEntry

    def produceOpenExcercisesWidget(self, parentWidget):
        def openExcerciseMenu(event, *args):
            exMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.ExcerciseManager)
            exMenuManger.subsection = event.widget.subsection
            exMenuManger.imIdx = event.widget.imIdx

            event.widget.shouldShowExMenu = not event.widget.shouldShowExMenu

            if (event.widget.shouldShowExMenu):
                exMenuManger.show()
            else:
                exMenuManger.hide()

        openExUIEntry = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.excercises.name, 
                                        prefix = "contentOpenExcerciseUIEntry" + self.__nameIdPrefix,
                                        row = 0, 
                                        column = self.EntryUIs.excercises.column,
                                        columnspan = 1)
        openExUIEntry.imIdx = self.imIdx
        openExUIEntry.subsection = self.subsection
        openExUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openExcerciseMenu])
        
        fullPathToEntryJSON = _upan.Paths.Entry.JSON.getAbs(sf.Wr.Manager.Book.getCurrBookFolderPath(),
                                                            self.subsection, self.imIdx)
        entryStructureExists = ocf.Wr.FsAppCalls.checkIfFileOrDirExists(fullPathToEntryJSON)

        #TODO: should probably change to something else since the structure might exist but no excercises present.
        excerciseExists = False
        if entryStructureExists:
            entryLinesList = fsf.Wr.EntryInfoStructure.readProperty(self.subsection, self.imIdx, 
                                                   fsf.Wr.EntryInfoStructure.PubProp.entryLinesList)
            if (entryLinesList != _u.Token.NotDef.list_t) and (entryLinesList != []):
                excerciseExists = True
        if excerciseExists:
            openExUIEntry.changeColor("brown")
        bindChangeColorOnInAndOut(openExUIEntry, shouldBeBrown = excerciseExists)
        return openExUIEntry

    def produceMainImageWidget(self, parentWidget, leftPad = 60, column = 0):
        def updateEntry(event, *args):
            def __getText(widget):
                imLinkDict = fsf.Data.Sec.imLinkDict(widget.subsection)
                text = imLinkDict[widget.imIdx]
                return text

            def __setText(newText, widget):
                imLinkDict = fsf.Data.Sec.imLinkDict(widget.subsection)
                imLinkDict[widget.imIdx] = newText
                fsf.Data.Sec.imLinkDict(widget.subsection, imLinkDict)
            
            def __updateImage(widget):
                textOnly = fsf.Data.Sec.textOnly(widget.subsection)[widget.imIdx]
                imLinkDict = fsf.Data.Sec.imLinkDict(widget.subsection)
                text = imLinkDict[widget.imIdx]
                fsf.Wr.SectionInfoStructure.rebuildEntryLatex(widget.subsection,
                                                            widget.imIdx,
                                                            text,
                                                            textOnly
                                                            )

                for w in wd.Data.Reactors.entryChangeReactors.values():
                    if "onMainLatexImageUpdate" in dir(w):
                        w.onMainLatexImageUpdate(widget.subsection, widget.imIdx)

            def __changeOnEtrFunc(widget):
                for w in wd.Data.Reactors.entryChangeReactors.values():
                    if "onEntryTextUpdate" in dir(w):
                        w.onEntryTextUpdate()
            
            def __changeOnLabelBackFunc(widget):
                for w in wd.Data.Reactors.entryChangeReactors.values():
                    if "onEntryTextUpdate" in dir(w):
                        w.onEntryTextUpdate()
            
            bindWidgetTextUpdatable(event, __getText, __setText, __updateImage, 
                                                      __changeOnEtrFunc, __changeOnLabelBackFunc)


        if fsf.Data.Sec.imLinkDict(self.subsection).get(self.imIdx) != None:
            v = fsf.Data.Sec.imLinkDict(self.subsection)[self.imIdx]

            latexTxt = tff.Wr.TexFileUtils.fromEntryToLatexTxt(self.imIdx, v)
            pilIm = getEntryImg(latexTxt, self.subsection, self.imIdx)

            shrink = 0.7
            pilIm.thumbnail([int(pilIm.size[0] * shrink),int(pilIm.size[1] * shrink)], Image.LANCZOS)
            img = ww.currUIImpl.UIImage(pilIm)

            textLabelPage = TOCLabelWithClickEntry(parentWidget,
                                            image = img, 
                                            prefix = "contentP_" + self.__nameIdPrefix, 
                                            padding= [leftPad, 0, 0, 0],
                                            row = 0, 
                                            column = column)
            textLabelPage.imIdx = self.imIdx
            textLabelPage.subsection = self.subsection
            textLabelPage.etrWidget = textLabelPage
            textLabelPage.imageLineIdx = int(self.imIdx)
            textLabelPage.entryText = v
            textLabelPage.imagePath = v

            textLabelPage.rebind([ww.currUIImpl.Data.BindID.mouse2],
                                    [updateEntry])
            
            bindOpenOMOnThePageOfTheImage(textLabelPage, textLabelPage.subsection, textLabelPage.imIdx)
            textLabelPage.image = img
        else:
            textLabelPage = TOCLabelWithClickEntry(parentWidget,
                                                text = _u.Token.NotDef.str_t, 
                                                prefix = "contentP_" + self.__nameIdPrefix, 
                                                padding= [leftPad, 0, 0, 0],
                                                row = 0, 
                                                column = column)

        self.entryFrameManager.latexEntryImage = textLabelPage
        return textLabelPage

    def produceOpenSecondaryImageWidget(self, parentWidget):
        def openSecondaryImage(widget):
            def __cmd(event = None, *args):
                widget = event.widget
                imIdx = widget.imIdx
                subsection = widget.subsection

                for w in wd.Data.Reactors.entryChangeReactors.copy().values():
                    if "onSecondaryImageOpen" in dir(w):
                        w.onSecondaryImageOpen(subsection, imIdx)
            
            widget.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])

        textLabelFull = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.im.name, 
                                        prefix = "contentFull_" + self.__nameIdPrefix,
                                        row = 0, 
                                        column = self.EntryUIs.im.column)
        textLabelFull.subsection = self.subsection
        textLabelFull.imIdx = self.imIdx
        openSecondaryImage(textLabelFull)
        bindChangeColorOnInAndOut(textLabelFull)
        return textLabelFull
        

    def produceFullMoveEntriesWidget(self, parentWidget):
        def fullMove(event, entryFrameManager:EntryFrameManager,
                                *args):
            if not event.widget.clicked:
                fsf.Data.Book.subsectionOpenInTOC_UI = self.subsection
                fsf.Data.Book.entryImOpenInTOC_UI = self.imIdx
            else:
                fsf.Data.Book.entryImOpenInTOC_UI = _u.Token.NotDef.str_t

            event.widget.clicked = not event.widget.clicked

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onFullEntryMove" in dir(w):
                    w.onFullEntryMove()
            

        showImages = TOCLabelWithClick(parentWidget, 
                                    text = self.EntryUIs.full.name,
                                    prefix = "contentOfImages_" + self.__nameIdPrefix,
                                    row = 0,
                                    column = self.EntryUIs.full.column)
        showImages.imIdx = self.imIdx
        showImages.subsection = self.subsection
        showImages.clicked = False
        showImages.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [lambda e, efm = self.entryFrameManager, *args: fullMove(e, efm, *args)])
        bindChangeColorOnInAndOut(showImages)
        return showImages

    def produceAlwaysShowChbxWidget(self, parentWidget):
        chkbtnShowPermamently = EntryShowPermamentlyCheckbox(parentWidget, 
                                                             self.subsection, self.imIdx, 
                                                             "contentShowAlways_" + self.__nameIdPrefix,
                                                             row = 0, 
                                                             column = self.EntryUIs.alwaysShow.column,)
        return chkbtnShowPermamently

    def produceDictWidget(self, parentWidget):
        def openNoteMenu(event, *args):
            notesMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.NotesManager)
            notesMenuManger.subsection = event.widget.subsection
            notesMenuManger.imIdx = event.widget.imIdx

            event.widget.shouldShowNotesMenu = not event.widget.shouldShowNotesMenu
            if (event.widget.shouldShowNotesMenu):
                notesMenuManger.show()
            else:
                notesMenuManger.hide()
        openNoteUIEntry = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.dict.name, 
                                        prefix = "contentOpenDictUIEntry" + self.__nameIdPrefix,
                                        row = self.EntryUIs.dict.row, 
                                        column = self.EntryUIs.dict.column,
                                        columnspan = 1)
        openNoteUIEntry.imIdx = self.imIdx
        openNoteUIEntry.subsection = self.subsection
        openNoteUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openNoteMenu])
        bindChangeColorOnInAndOut(openNoteUIEntry)
        return openNoteUIEntry 

    def produceOpenNotesWidget(self, parentWidget):
        def openNoteMenu(event, *args):
            notesMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.EntryNotesManager)
            notesMenuManger.subsection = event.widget.subsection
            notesMenuManger.imIdx = event.widget.imIdx

            event.widget.shouldShowNotesMenu = not event.widget.shouldShowNotesMenu
            if (event.widget.shouldShowNotesMenu):
                notesMenuManger.show()
            else:
                notesMenuManger.hide()
    
        openNoteUIEntry = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.entryNote.name, 
                                        prefix = "contentOpenNoteUIEntry" + self.__nameIdPrefix,
                                        row = self.EntryUIs.entryNote.row, 
                                        column = self.EntryUIs.entryNote.column,
                                        columnspan = 1)
        openNoteUIEntry.imIdx = self.imIdx
        openNoteUIEntry.subsection = self.subsection
        openNoteUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openNoteMenu])
        notesExist = False

        fullPathToEntryJSON = _upan.Paths.Entry.JSON.getAbs(sf.Wr.Manager.Book.getCurrBookFolderPath(),
                                                        self.subsection, self.imIdx)
        entryStructureExists = ocf.Wr.FsAppCalls.checkIfFileOrDirExists(fullPathToEntryJSON)
        if entryStructureExists:
            currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            entryWordDictArr = fsf.Wr.EntryInfoStructure.readProperty(self.subsection,
                                                    self.imIdx,
                                                    fsf.Wr.EntryInfoStructure.PubProp.entryWordDictDict,
                                                    currBookPath)

            if (entryWordDictArr != _u.Token.NotDef.dict_t)\
                and (entryWordDictArr != {}):
                notesExist = True
        if notesExist:
            openNoteUIEntry.changeColor("brown")
        bindChangeColorOnInAndOut(openNoteUIEntry, shouldBeBrown = notesExist)
        return openNoteUIEntry

    def showSubrentriesWidget(self, parentWidget):
        def showSubentriesCmd(event, *args):
            widget = event.widget
            
            if self.imIdx not in fsf.Data.Sec.leadingEntry(self.subsection).values():
                return

            showSubentries = fsf.Data.Sec.showSubentries(widget.subsection)
            if showSubentries.get(widget.imIdx) != None:
                showSubentries[widget.imIdx] = not showSubentries[widget.imIdx]
            else:
                showSubentries[widget.imIdx] = True
    
            fsf.Data.Sec.showSubentries(widget.subsection, showSubentries)

            for w in wd.Data.Reactors.entryChangeReactors.copy().values():
                if "onShowSubentries" in dir(w):
                    w.onShowSubentries(widget.subsection, widget.imIdx)

        showSubentries = TOCLabelWithClick(parentWidget,
                                        text = self.EntryUIs.showSubentries.name,
                                        prefix = "contentShowSubentriesEntry" + self.__nameIdPrefix,
                                        row = 0, 
                                        column = self.EntryUIs.showSubentries.column)
        showSubentries.imIdx = self.imIdx
        showSubentries.subsection = self.subsection
        showSubentries.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [showSubentriesCmd])
        
        if str(self.imIdx) in fsf.Data.Sec.leadingEntry(self.subsection).values():
            hasSubentries = True
        else:
            hasSubentries = False
        if hasSubentries:
            showSubentries.changeColor("brown")
        bindChangeColorOnInAndOut(showSubentries, shouldBeBrown = hasSubentries)
        return showSubentries

    def __produceGroupExtraWidgets(self, parentWidget, groupName):
        hideImageGroupLabel = TOCLabelWithClick(parentWidget, 
                                                text = "[show/hide]",
                                                prefix = "contentHideImageGroupLabel_" + self.__nameIdPrefix,
                                                row = 0, column = 1)

        hideImageGroupLabel.render()

        hideImageGroupLabel.subsection = self.subsection
        hideImageGroupLabel.imIdx = self.imIdx
        hideImageGroupLabel.group = groupName

        bindChangeColorOnInAndOut(hideImageGroupLabel)

        def __cmd(e):
            imagesGroupsList = fsf.Data.Sec.imagesGroupsList(e.widget.subsection)
            imagesGroupsList[e.widget.group] = not imagesGroupsList[e.widget.group]
            fsf.Data.Sec.imagesGroupsList(e.widget.subsection, imagesGroupsList)

        hideImageGroupLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])

        newGroup = ImageSize_ETR(parentWidget,
                prefix = "contentNewGroupImageGroupLabel_" + self.__nameIdPrefix,
                row = 0, 
                column = 3,
                imIdx = self.imIdx,
                text = groupName,
                width = 10)
        newGroup.subsection = self.subsection
        newGroup.render()
        newGroup.setData(groupName)

        moveGroup = ImageSize_ETR(parentWidget,
                prefix = "contentMoveImageGroupLabel_" + self.__nameIdPrefix,
                row = 0, 
                column = 2,
                imIdx = self.imIdx,
                text = self.subsection + ":" + self.imIdx,
                width = 10)
        moveGroup.subsection = self.subsection
        moveGroup.imIdx = self.imIdx

        def __moveGroup(e, *args): 
            subsection = e.widget.subsection
            imIdx = e.widget.imIdx
            # NOTE: this is a hack but I can't find a better way atm
            newGroupNameWName = "contentNewGroupImageGroupLabel_".lower()
            newGroupNameW = [i for i in e.widget.getParent().getChildren() \
                                if newGroupNameWName.lower() in i.name][0]

            targetWholePath:str = e.widget.getData()

            if ":" not in targetWholePath:
                _u.log.autolog("Incorrect destination path")

            targetSubsection = targetWholePath.split(":")[0]
            targetEntryIdx = targetWholePath.split(":")[1]
            targetGroupName = newGroupNameW.getData() if newGroupNameW.getData() != "" else "No group"
            sourceSubsection = subsection
            sourceEntryIdx = imIdx
            sourceGroupNameIdx = fsf.Data.Sec.imagesGroupDict(sourceSubsection)[sourceEntryIdx]
            sourceGroupName = list(fsf.Data.Sec.imagesGroupsList(sourceSubsection).keys())[sourceGroupNameIdx]

            # ask the user if we wnat to proceed.
            msg = "\
Do you want to move group \n\nto subsection\n'{0}' \n\nand entry: \n'{1}'\n\n with group name \n'{2}'?".format(targetSubsection, 
                                                                            targetEntryIdx, 
                                                                            targetGroupName)
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)


            if not response:
                return

            # UI
            pdfMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                            wf.Wr.MenuManagers.PdfReadersManager)
            pdfMenuManager.saveFigures()

            gm.GeneralManger.moveGroupToSubsection(sourceSubsection, sourceGroupName,
                                                    targetSubsection, targetGroupName, targetEntryIdx)

            self.widgetToScrollTo = None
            self.linkFrames = None
            self.currSecondRowLabels = None

            pdfMenuManager.forceUpdate()

        moveGroup.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                [__moveGroup])
        moveGroup.render()

    def produceGroupWidget(self, parentWidget):
        imagesGroupDict:dict = fsf.Data.Sec.imagesGroupDict(self.subsection)
        imagesGroupsWShouldShow:list = fsf.Data.Sec.imagesGroupsList(self.subsection)
        imagesGroups:list = list(imagesGroupsWShouldShow.keys())

        if imagesGroupDict.get(self.imIdx) != None:
            currImGroupidx = imagesGroupDict[self.imIdx]
        else:
            currImGroupidx = 0

        if int(self.imIdx) > 0 :
            entriesList = list(fsf.Data.Sec.imLinkDict(self.subsection).keys())
            entriesList.sort(key = int)

            print(entriesList)
            counter = 0

            while str(self.imIdx) not in entriesList:
                time.sleep(0.3)
                entriesList = list(fsf.Data.Sec.imLinkDict(self.subsection).keys())
                counter += 1
                if counter > 50:
                    _u.log.autolog("Something is wrong with the group list. Return")
                    return

            entriesList.index(str(self.imIdx))
            idx = entriesList[entriesList.index(self.imIdx) - 1] #previous entry

            if imagesGroupDict.get(str(idx)) != None:
                if idx == _u.Token.NotDef.str_t:
                    prevImGroupName = _u.Token.NotDef.str_t
                else:
                    prevImGroupName = imagesGroups[imagesGroupDict[idx]]
            else:
                prevImGroupName = _u.Token.NotDef.str_t
        elif self.imIdx == _u.Token.NotDef.str_t:
            prevImGroupName = imagesGroups[0]
        else:
            if imagesGroupDict.get(self.imIdx) != None:
                prevImGroupName = imagesGroups[imagesGroupDict[self.imIdx]]
            else:
                prevImGroupName = imagesGroups[0]

        if currImGroupidx == _u.Token.NotDef.str_t:
            currImGroupidx = 0

        currImGroupName = imagesGroups[currImGroupidx]

        topPad = 0

        if currImGroupName != prevImGroupName:
            if not imagesGroupsWShouldShow[currImGroupName]:
                topPad = 0
            elif (self.imIdx != "0"):
                topPad = 5

        imageGroupFrame = TOCFrame(parentWidget,
                                    prefix = "contentImageGroupFr_" + self.__nameIdPrefix,
                                    padding=[0, topPad, 0, 0], 
                                    row = 0, column = 0, columnspan = 100)

        if (currImGroupName != prevImGroupName) or (self.imIdx == "0"):
            def __updateGroup(event, *args):
                widget = event.widget

                if widget.group == "No group":
                    return

                def __getText(widget):
                    return widget.group
                                 
                def __setText(newText, widget):
                    oldGroupName = widget.group
    
                    imagesGroupsList = \
                        fsf.Data.Sec.imagesGroupsList(widget.subsection).copy()
                    imagesGroupsList = \
                        {k if k != oldGroupName else newText: v for k,v in imagesGroupsList.items()}
                    fsf.Data.Sec.imagesGroupsList(widget.subsection,
                                                    imagesGroupsList)
                    widget.group = newText
                
                def __updateImage(widget):
                    fsf.Wr.SectionInfoStructure.rebuildGroupOnlyImOnlyLatex(widget.subsection,
                                                                            widget.group)
                    #TODO: we need to update the other widgets as well

                bindWidgetTextUpdatable(event, __getText, __setText, __updateImage)

            img = getGroupImg(self.subsection, currImGroupName)
            imageGroupLabel = TOCLabelWithClickGroup(imageGroupFrame, 
                                        image = img, 
                                        prefix = "contentGroupP_" + self.__nameIdPrefix,
                                        padding = [30, 0, 0, 0], 
                                        row = 0, column = 0)
            imageGroupLabel.image = img
            imageGroupLabel.subsection = self.subsection
            imageGroupLabel.group = currImGroupName

            # NOTE: without rebind groups sometimes not shoing up #FIXME
            imageGroupLabel.rebind([ww.currUIImpl.Data.BindID.mouse2],
                                    [__updateGroup])

            imageGroupLabel.render()

            if currImGroupName != "No group":
                self.__produceGroupExtraWidgets(imageGroupFrame, currImGroupName)

        return imageGroupFrame 

    def produceGroupOM(self, parentWidget):
        imagesGroupDict:dict = fsf.Data.Sec.imagesGroupDict(self.subsection)
        imagesGroups = fsf.Data.Sec.imagesGroupsList(self.subsection)

        currImGroupidx = 0

        if imagesGroupDict.get(self.imIdx) != None:
            currImGroupidx = imagesGroupDict[self.imIdx]
        
        currImGroupidx = 0 if currImGroupidx == _u.Token.NotDef.str_t else currImGroupidx

        currImGroupName = list(imagesGroups.keys())[currImGroupidx]

        imageGroupOM = ImageGroupOM(imagesGroups,
                                   parentWidget, 
                                   self.subsection,
                                   self.imIdx,
                                   self,
                                   column = self.EntryUIs.group.column,
                                   currImGroupName = currImGroupName)
        return imageGroupOM

    def produceBookCodeProject(self, parentWidget):
        def openBookCodeProjectCmd(event, *args):
            subsection = event.widget.subsection
            imIdx = event.widget.imIdx
            dt.CodeTemp.currCodeFullLink = imIdx

            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            projectPath = _upan.Paths.Book.Code.getAbs(bookPath)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(projectPath):
                _u.log.autolog("Please add a book code project files.")
                return

            ocf.Wr.IdeCalls.openNewWindow(projectPath)

            bookCodeFiles:dict = fsf.Data.Sec.bookCodeFile(subsection)

            if bookCodeFiles.get(imIdx) != None:
                relFilepath = bookCodeFiles.get(imIdx)
                time.sleep(0.5)
                filepath = os.path.join(projectPath, relFilepath)

                if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(filepath):
                    return

                lines = []
                with open(filepath) as f:
                    lines = f.read().splitlines()
                
                marker = _upan.Names.codeLineMarkerBook(subsection, imIdx)

                for i in range(len(lines)):
                    if marker in lines[i]:
                        ocf.Wr.IdeCalls.openNewTab(filepath, i)
                        return

                ocf.Wr.IdeCalls.openNewTab(filepath)

        openBookCodeProject = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.openBookCodeProject.name, 
                                        prefix = "openBookCodeProject" + self.__nameIdPrefix,
                                        row = 1, 
                                        column = self.EntryUIs.openBookCodeProject.column,
                                        columnspan = 1)
        openBookCodeProject.imIdx = self.imIdx
        openBookCodeProject.subsection = self.subsection
        openBookCodeProject.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openBookCodeProjectCmd])
        bindChangeColorOnInAndOut(openBookCodeProject)
        return openBookCodeProject

    def produceSubsectionCodeProject(self, parentWidget):
        def openSubsectionCodeProjectCmd(event, *args):
            subsection = event.widget.subsection
            imIdx = event.widget.imIdx
            dt.CodeTemp.currCodeFullLink = imIdx

            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            codeTemplatePath =_upan.Paths.Book.Code.getSubsectionTemplatePathAbs(bookPath)
            codeSubsectionPath =_upan.Paths.Section.getCodeRootAbs(bookPath,
                                                                    subsection)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(codeSubsectionPath):
                ocf.Wr.FsAppCalls.copyFile(codeTemplatePath, codeSubsectionPath)

            ocf.Wr.IdeCalls.openNewWindow(codeSubsectionPath)

            subsectionCodeFiles:dict = fsf.Data.Sec.subsectionCodeFile(subsection)

            if subsectionCodeFiles.get(imIdx) != None:
                relFilepath = subsectionCodeFiles.get(imIdx)
                time.sleep(0.5)
                filepath = os.path.join(codeSubsectionPath, relFilepath)

                if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(filepath):
                    _u.log.autolog(f"Subsection '{filepath}' file not found.")
                    return

                lines = []
                with open(filepath) as f:
                    lines = f.read().splitlines()
                
                marker = _upan.Names.codeLineMarkerSubsection(subsection, imIdx)

                for i in range(len(lines)):
                    if marker in lines[i]:
                        ocf.Wr.IdeCalls.openNewTab(filepath, i)
                        return

                ocf.Wr.IdeCalls.openNewTab(filepath)

        openSubsectionCodeProject = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.openSubsectionCodeProject.name, 
                                        prefix = "openSubsectionCodeProject" + self.__nameIdPrefix,
                                        row = 1, 
                                        column = self.EntryUIs.openSubsectionCodeProject.column,
                                        columnspan = 1)
        openSubsectionCodeProject.imIdx = self.imIdx
        openSubsectionCodeProject.subsection = self.subsection
        openSubsectionCodeProject.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openSubsectionCodeProjectCmd])
        bindChangeColorOnInAndOut(openSubsectionCodeProject)
        return openSubsectionCodeProject

    def produceEntryCodeProject(self, parentWidget):
        def openEntryCodeProjectCmd(event, *args):
            subsection =  event.widget.subsection
            imIdx =  event.widget.imIdx
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

            entryPath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryPath):
                fsf.Wr.EntryInfoStructure.createStructure(bookPath, subsection, imIdx)

            entryCodeProjFilepath = _upan.Paths.Entry.getCodeProjAbs(bookPath, subsection, imIdx)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryCodeProjFilepath):
                codeProjTemplatePath = \
                    _upan.Paths.Book.Code.getEntryTemplatePathAbs(bookPath)
                ocf.Wr.FsAppCalls.copyFile(codeProjTemplatePath, entryCodeProjFilepath)

            ocf.Wr.IdeCalls.openNewWindow(_upan.Paths.Entry.getCodeProjAbs(bookPath, subsection, imIdx))

        openEntryCodeProject = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.openEntryCodeProject.name, 
                                        prefix = "openEntryCodeProject" + self.__nameIdPrefix,
                                        row = 1, 
                                        column = self.EntryUIs.openEntryCodeProject.column,
                                        columnspan = 1)
        openEntryCodeProject.imIdx = self.imIdx
        openEntryCodeProject.subsection = self.subsection
        openEntryCodeProject.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openEntryCodeProjectCmd])
        bindChangeColorOnInAndOut(openEntryCodeProject)
        return openEntryCodeProject


    def produceOpenProofMenu(self, parentWidget):
        def openProofsMenu(event, *args):
            prMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.ProofsManager)

            event.widget.shouldShowProofMenu = not event.widget.shouldShowProofMenu

            if (event.widget.shouldShowProofMenu):
                prMenuManger.show(subsection =  event.widget.subsection, imIdx = event.widget.imIdx)
            else:
                prMenuManger.hide(subsection =  event.widget.subsection, imIdx = event.widget.imIdx)

        openProofsUIEntry = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.proof.name, 
                                        prefix = "contentOpenProofsUIEntry" + self.__nameIdPrefix,
                                        row = self.EntryUIs.proof.row, 
                                        column = self.EntryUIs.proof.column)

        openProofsUIEntry.imIdx = self.imIdx
        openProofsUIEntry.subsection = self.subsection
        openProofsUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openProofsMenu])
        bindChangeColorOnInAndOut(openProofsUIEntry)
        return openProofsUIEntry

    def produceOpenWikiNotes(self, parentWidget):
        def openWiki(event, *args):
            os.system("\
    /Users/ashum048/books/utils/c++_modules/qt_KIK_Browser/build/Qt_6_8_0_macos-Debug/browser.app/Contents/MacOS/browser \
    http://localhost/wiki/A/User:The_other_Kiwix_guy/Landing")

        openEntryWikiUIEntry = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.wikiNote.name, 
                                        prefix = "contentOpenEntryWikiUIEntry" + self.__nameIdPrefix,
                                        row = 1, 
                                        column = self.EntryUIs.wikiNote.column,
                                        columnspan = 1)
        openEntryWikiUIEntry.imIdx = self.imIdx
        openEntryWikiUIEntry.subsection = self.subsection
        openEntryWikiUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                    [openWiki])
        bindChangeColorOnInAndOut(openEntryWikiUIEntry)
        return openEntryWikiUIEntry

    def produceEntryWidgetFrames(self, topPad, row, leftPad, rowsPad = 0):
        nameId = _upan.Names.Entry.getEntryNameID(self.subsection, self.imIdx)

        entryFrame = TOCFrame(self.frame,
                                prefix = "contentFr_" + nameId,
                                padding=[leftPad, topPad, 0, 0],
                                row = row, column = 0, columnspan = 100)
        entryFrame.render()

        entryFrameManager = EntryFrameManager(entryFrame = entryFrame, 
                                              subsection = self.subsection, 
                                              imIdx = self.imIdx,
                                              widgetFactory = self)

        entryFrameManager.groupFrame = self.produceGroupWidget(entryFrame)

        entryFrameManager.rowFrame1 = TOCFrame(entryFrame,
                            prefix = "contentRow1Fr_" + nameId,
                            padding=[rowsPad, 0, 0, 0],
                            row = 1, 
                            column = 0, columnspan = 100)
        entryFrameManager.rowFrame1.subsection = self.subsection
        entryFrameManager.rowFrame1.imIdx = self.imIdx
        entryFrameManager.rowFrame1.render()

        entryFrameManager.rowFrame2 = TOCFrame(entryFrame,
                            prefix = "contentRow2Fr_" + nameId,
                            padding=[60 + rowsPad, 0, 0, 0],
                            row = 2, 
                            column = 0, columnspan = 100)
        entryFrameManager.rowFrame2.subsection = self.subsection
        entryFrameManager.rowFrame2.imIdx = self.imIdx

        linksFrameFactory = LinksFrameFactory(self.subsection,
                                              self.imIdx)
        linksFrameFactory.produceLinksFrame(parentWidget = entryFrame,
                                            row = 3,
                                            leftPad = rowsPad)
        entryFrameManager.linksFrameManager = linksFrameFactory.manager
        
        entryFrameManager.imagesFrame = TOCFrame(entryFrame,
                            prefix = "ImagesFrame" + nameId,
                            padding=[0, 0, 0, 0],
                            row = 4, 
                            column = 0, columnspan = 100)
        entryFrameManager.imagesFrame.subsection = self.subsection
        entryFrameManager.imagesFrame.imIdx = self.imIdx
        entryFrameManager.imagesFrame.render()

        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : row, "columnspan" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }

        entryFrameManager.imagesFrameScroll = \
                                        ww.currUIImpl.ScrollableBox(prefix = "ImagesFrameScroll",
                                                                    name = nameId,
                                                                    rootWidget = entryFrameManager.imagesFrame,
                                                                    renderData = renderData,
                                                                    width = 660,
                                                                    height = 1,
                                                                    createTopScroll = False)

        return entryFrameManager

class EntryWidgetFactoryTOC(EntryWidgetFactory):
    # row 1
    class EntryUIs(EntryWidgetFactory.EntryUIs):
        def __init__(self):
            self.full = self.__EntryUIData("[f]", 1, EntryWidgetFactory.produceFullMoveEntriesWidget)
            self.im = self.__EntryUIData("[i]", 2, EntryWidgetFactory.produceOpenSecondaryImageWidget)
            self.copyLink = self.__EntryUIData("[cl]", 3, EntryWidgetFactory.produceCopyLinkWidget)
            self.pasteLink = self.__EntryUIData("[pl]", 4, EntryWidgetFactory.producePasteLinkEntryWidget)
            self.copy = self.__EntryUIData("[c]", 5, EntryWidgetFactory.produceCopyEntryWidget)
            self.pasteAfter = self.__EntryUIData("[p]", 6, EntryWidgetFactory.producePasteEntryWidget)
            self.excercises = self.__EntryUIData("[e]", 7, EntryWidgetFactory.produceOpenExcercisesWidget)
            self.group = self.__EntryUIData("", 8, EntryWidgetFactory.produceGroupOM)

            # row 2
            self.showLinks = self.__EntryUIData("[Links]", 1, EntryWidgetFactory.produceShowLinksForEntry)
            self.alwaysShow = self.__EntryUIData("", 2, EntryWidgetFactory.produceAlwaysShowChbxWidget)
            self.changeImSize = self.__EntryUIData("", 3, EntryWidgetFactory.produceChangeImSizeWidget)
            self.delete = self.__EntryUIData("[Delete]", 4, EntryWidgetFactory.produceRemoveEntryWidget)
            self.retake = self.__EntryUIData("[Retake]", 5, EntryWidgetFactory.produceRetakeImageWidget)
            self.addExtra = self.__EntryUIData("[Add extra]", 6, EntryWidgetFactory.produceAddExtraImageWidget)
            self.addProof = self.__EntryUIData("[Add proof]", 7, EntryWidgetFactory.produceAddProofImageWidget)
            self.showSubentries = self.__EntryUIData("[Show sub]", 8, EntryWidgetFactory.showSubrentriesWidget)
            self.note = self.__EntryUIData("[Dictionary]", 8, EntryWidgetFactory.produceOpenNotesWidget)
            self.leadingEntry = self.__EntryUIData("", 9, EntryWidgetFactory.produceLeadingEntryEtrWidget)
            self.shift = self.__EntryUIData("[Shift Up]", 10, EntryWidgetFactory.produceShiftLabelWidget)
            self.copyText = self.__EntryUIData("[Copy text]", 11, EntryWidgetFactory.produceCopyTextToMemWidget)

    def produceEntryWidgetsForFrame(self, parentWidget, row):
        self.frame = parentWidget

        leadingEntry = fsf.Data.Sec.leadingEntry(self.subsection)

        rowsPad = 0

        if leadingEntry.get(self.imIdx) != None:
            if str(leadingEntry[self.imIdx]) != _u.Token.NotDef.str_t:
                rowsPad += 30

                showSubentries = fsf.Data.Sec.showSubentries(self.subsection)
                if showSubentries.get(self.imIdx) != None:
                    if not showSubentries[self.imIdx]:
                        self.entryFrameManager = None
                        return

        self.entryFrameManager = self.produceEntryWidgetFrames(topPad = self.topPad, 
                                                               leftPad = self.leftPad, 
                                                               row = row,
                                                               rowsPad = rowsPad)

        if self.entryFrameManager == None:
            return
        
        self.entryFrameManager.groupFrame.render()

        mainImageWidget = self.produceMainImageWidget(parentWidget = self.entryFrameManager.rowFrame1)
        mainImageWidget.render()

        if fsf.Data.Sec.tocWImageDict(self.subsection).get(self.imIdx) == None:
            return

        if fsf.Data.Sec.tocWImageDict(self.subsection)[self.imIdx] == "1":
            self.entryFrameManager.showImages()

        full = self.EntryUIs.full.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        self.entryFrameManager.fullMoveWidget = full
        full.render()
        im = self.EntryUIs.im.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        im.render()
        copy = self.EntryUIs.copy.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        copy.render()
        pasteAfter = self.EntryUIs.pasteAfter.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        pasteAfter.render()
        excercises = self.EntryUIs.excercises.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        excercises.render()
        copyLink = self.EntryUIs.copyLink.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        copyLink.render()
        pasteLink = self.EntryUIs.pasteLink.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        pasteLink.render()
        group = self.EntryUIs.group.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        group.render()

        leadingEntry = self.EntryUIs.leadingEntry.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        leadingEntry.render()
        showSubentries = self.EntryUIs.showSubentries.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        showSubentries.render()
        delete = self.EntryUIs.delete.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        delete.render()
        shift = self.EntryUIs.shift.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        shift.render()
        copyText = self.EntryUIs.copyText.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        copyText.render()
        retake = self.EntryUIs.retake.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        retake.render()
        addExtra = self.EntryUIs.addExtra.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        addExtra.render()
        addProof = self.EntryUIs.addProof.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        addProof.render()
        alwaysShow = self.EntryUIs.alwaysShow.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        alwaysShow.render()
        changeImSize = self.EntryUIs.changeImSize.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        changeImSize.render()
        self.entryFrameManager.uiResizeEtr = changeImSize

class EntryWidgetFactoryEntryWindow(EntryWidgetFactory):
    class EntryUIs(EntryWidgetFactory.EntryUIs):
        def __init__(self):
            self.full = self.__EntryUIData("[f]", 1, EntryWidgetFactory.produceFullMoveEntriesWidget)
            self.copyLink = self.__EntryUIData("[cl]", 3, EntryWidgetFactory.produceCopyLinkWidget)
            self.pasteLink = self.__EntryUIData("[pl]", 4, EntryWidgetFactory.producePasteLinkEntryWidget)
            self.copy = self.__EntryUIData("[c]", 5, EntryWidgetFactory.produceCopyEntryWidget)
            self.pasteAfter = self.__EntryUIData("[p]", 6, EntryWidgetFactory.producePasteEntryWidget)
            self.excercises = self.__EntryUIData("[e]", 7, EntryWidgetFactory.produceOpenExcercisesWidget)

            self.showLinks = self.__EntryUIData("[Links]", 1, EntryWidgetFactory.produceShowLinksForEntry)
            self.alwaysShow = self.__EntryUIData("", 2, EntryWidgetFactory.produceAlwaysShowChbxWidget)
            self.changeImSize = self.__EntryUIData("", 3, EntryWidgetFactory.produceChangeImSizeWidget)
            self.retake = self.__EntryUIData("[Retake]", 4, EntryWidgetFactory.produceRetakeImageWidget)
            self.addExtra = self.__EntryUIData("[Add exta]", 5, EntryWidgetFactory.produceAddExtraImageWidget)
            self.addProof = self.__EntryUIData("[Add proof]", 6, EntryWidgetFactory.produceAddProofImageWidget)
            self.dict = self.__EntryUIData("[Dictionary]", 7, EntryWidgetFactory.produceDictWidget)
            self.group = self.__EntryUIData("", 8, EntryWidgetFactory.produceGroupOM)
            
            self.openBookCodeProject = self.__EntryUIData("[code:b", 1, EntryWidgetFactory.produceBookCodeProject)
            self.openSubsectionCodeProject = self.__EntryUIData(",s", 2, EntryWidgetFactory.produceSubsectionCodeProject)
            self.openEntryCodeProject = self.__EntryUIData(",e]", 3, EntryWidgetFactory.produceEntryCodeProject)
            self.entryNote = self.__EntryUIData("[Note]", 4, EntryWidgetFactory.produceOpenNotesWidget, row = 1)
            self.wikiNote = self.__EntryUIData("[Wiki]", 5, EntryWidgetFactory.produceOpenWikiNotes)
            self.copyText = self.__EntryUIData("[Copy text]", 6, EntryWidgetFactory.produceCopyTextToMemWidget, row = 1)
            self.proof = self.__EntryUIData("[Show proof]", 7, EntryWidgetFactory.produceOpenProofMenu, row = 1)

    def produceEntryWidgetsForFrame(self, parentWidget, row):
        self.frame = parentWidget

        self.entryFrameManager = self.produceEntryWidgetFrames(topPad = self.topPad, 
                                                               leftPad = self.leftPad,
                                                               row = row)

        mainImageWidget = self.produceMainImageWidget(parentWidget = self.entryFrameManager.rowFrame1)
        mainImageWidget.render()

        self.entryFrameManager.rowFrame2.render()
        self.entryFrameManager.showImages()

        full = self.EntryUIs.full.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        self.entryFrameManager.fullMoveWidget = full
        full.render()
        copy = self.EntryUIs.copy.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        copy.render()
        pasteAfter = self.EntryUIs.pasteAfter.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        pasteAfter.render()
        excercises = self.EntryUIs.excercises.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        excercises.render()
        copyLink = self.EntryUIs.copyLink.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        copyLink.render()
        pasteLink = self.EntryUIs.pasteLink.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        pasteLink.render()


        showLinks = self.EntryUIs.showLinks.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        showLinks.render()
        alwaysShow = self.EntryUIs.alwaysShow.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        alwaysShow.render()
        changeImSize = self.EntryUIs.changeImSize.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        changeImSize.render()
        self.entryFrameManager.uiResizeEtr = changeImSize
        retake = self.EntryUIs.retake.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        retake.render()
        addExtra = self.EntryUIs.addExtra.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        addExtra.render()
        addProof = self.EntryUIs.addProof.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        addProof.render() 
        dictionary = self.EntryUIs.dict.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        dictionary.render()
        group = self.EntryUIs.group.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        group.render()

        openBookCodeProject = self.EntryUIs.openBookCodeProject.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        openBookCodeProject.render()
        openSubsectionCodeProject = self.EntryUIs.openSubsectionCodeProject.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        openSubsectionCodeProject.render()
        openEntryCodeProject = self.EntryUIs.openEntryCodeProject.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        openEntryCodeProject.render()
        entryNote = self.EntryUIs.entryNote.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        entryNote.render()
        wikiNote = self.EntryUIs.wikiNote.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        wikiNote.render()
        copyText = self.EntryUIs.copyText.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        copyText.render()
        proof = self.EntryUIs.proof.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        proof.render()

class EntryWidgetFactorySearchTOC(EntryWidgetFactory):
    # row 1
    class EntryUIs(EntryWidgetFactory.EntryUIs):
        def __init__(self):
            self.full = self.__EntryUIData("[f]", 1, EntryWidgetFactory.produceFullMoveEntriesWidget)
            self.im = self.__EntryUIData("[i]", 2, EntryWidgetFactorySearchTOC.produceOpenImageInTocWidget)
            self.copyLink = self.__EntryUIData("[cl]", 3, EntryWidgetFactory.produceCopyLinkWidget)
            self.pasteLink = self.__EntryUIData("[pl]", 4, EntryWidgetFactory.producePasteLinkEntryWidget)
            self.copy = self.__EntryUIData("[c]", 5, EntryWidgetFactory.produceCopyEntryWidget)
            self.pasteAfter = self.__EntryUIData("[p]", 6, EntryWidgetFactory.producePasteEntryWidget)

    def produceOpenImageInTocWidget(self, parentWidget):
        def openImageInPlace(widget):
            def __cmd(event = None, *args):
                widget = event.widget
                imIdx = widget.imIdx
                subsection = widget.subsection

                widget.clicked = not widget.clicked

                if widget.clicked:
                    widget.changeColor("brown")
                else:
                    widget.changeColor("white")

                bindChangeColorOnInAndOut(textLabelFull, shouldBeBrown = widget.clicked)

                for w in wd.Data.Reactors.entryChangeReactors.copy().values():
                    if "onOpenImageInTocWidget" in dir(w):
                        w.onOpenImageInTocWidget(subsection, imIdx)
            
            widget.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])

        textLabelFull = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.im.name, 
                                        prefix = "contentFull_" + super().getPrefixID(),
                                        row = 0, 
                                        column = self.EntryUIs.im.column)
        textLabelFull.subsection = self.subsection
        textLabelFull.imIdx = self.imIdx

        openImageInPlace(textLabelFull)
        bindChangeColorOnInAndOut(textLabelFull)
        return textLabelFull

    def produceEntryWidgetsForFrame(self, parentWidget, row):
        self.frame = parentWidget

        leadingEntry = fsf.Data.Sec.leadingEntry(self.subsection)

        rowsPad = 0

        if leadingEntry.get(self.imIdx) != None:
            if str(leadingEntry[self.imIdx]) != _u.Token.NotDef.str_t:
                rowsPad += 30

                showSubentries = fsf.Data.Sec.showSubentries(self.subsection)
                if showSubentries.get(self.imIdx) != None:
                    if not showSubentries[self.imIdx]:
                        self.entryFrameManager = None
                        return

        self.entryFrameManager = self.produceEntryWidgetFrames(topPad = self.topPad, 
                                                               leftPad = self.leftPad, 
                                                               row = row,
                                                               rowsPad = rowsPad)

        if self.entryFrameManager == None:
            return
        
        self.entryFrameManager.groupFrame.render()

        mainImageWidget = self.produceMainImageWidget(parentWidget = self.entryFrameManager.rowFrame1)
        mainImageWidget.render()

        if fsf.Data.Sec.tocWImageDict(self.subsection)[self.imIdx] == "1":
            self.entryFrameManager.showImages()

        full = self.EntryUIs.full.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        self.entryFrameManager.fullMoveWidget = full
        full.render()
        im = self.EntryUIs.im.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        im.render()
        copy = self.EntryUIs.copy.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        copy.render()
        pasteAfter = self.EntryUIs.pasteAfter.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        pasteAfter.render()
        copyLink = self.EntryUIs.copyLink.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        copyLink.render()
        pasteLink = self.EntryUIs.pasteLink.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        pasteLink.render()

class LinksFrameManager:
    def __init__(self, subsection, imIdx, linksFrame, linksFactory):
        self.imIdx = imIdx
        self.subsection = subsection
        self.linksFrame = linksFrame
        self.factory = linksFactory

        self.linksShown = False

        self.entriesFrame = None

    def makeLinksLarge(self):
        if wd.Data.MainEntryLayout.largeLinks:
            size = wd.Data.MainEntryLayout.largeLinksSize
            self.factory.scrollableBox.setCanvasHeight(size)
        else:
            self.updateLinksHeight()

    def updateLinksHeight(self):
        delta = 0

        if wd.Data.MainEntryLayout.currSize == wd.Data.MainEntryLayout.large:
            delta = 50

        self.factory.scrollableBox.setCanvasHeight(self.factory.scrollableBox.originalHeight + delta)

    def processChangeLinksViewStatusChange(self):
        if not self.linksShown:
            self.factory.produceLinksEntryFrames()
            self.linksFrame.render()
        else:
            self.linksFrame.hide()
        
        self.linksShown = not self.linksShown

    def showLinks(self):
        self.factory.produceLinksEntryFrames()
        self.linksFrame.render()
        self.linksShown = True
        for w in wd.Data.Reactors.entryChangeReactors.values():
            if "onShowLinks" in dir(w):
                w.onShowLinks()

class LinksFrameFactory:
    def __init__(self, subsection, imIdx):
        self.imIdx = imIdx
        self.subsection = subsection
        self.manager = None

        self.scrollableBox = None
    
    def produceMainFrame(self, parentWidget, row, leftPad):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : row, "columnspan" : 100},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        name = "_LinksFrame_"
        self.prefix =  _upan.Names.Entry.getEntryNameID(self.subsection, self.imIdx)

        frame = ww.currUIImpl.Frame(prefix = self.prefix,
                                   name = name, 
                                   rootWidget = parentWidget,
                                   renderData = renderData,
                                   padding = [leftPad, 0, 0, 10])

        delta = 0

        if wd.Data.MainEntryLayout.currSize == wd.Data.MainEntryLayout.large:
            delta = 50

        renderDataScroll = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 1, "columnspan" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }

        scrollableBox = ww.currUIImpl.ScrollableBox(prefix = self.prefix,
                                                    name = name, 
                                                    rootWidget = frame,
                                                    renderData = renderDataScroll,
                                                    width = 680,
                                                    height = 150 + delta,
                                                    createTopScroll = False)
        self.scrollableBox = scrollableBox
        scrollableBox.render()
        
        return frame

    def produceLinksMainWidgets(self, haveLinks):
        linksPrefixLabel = TOCLabelWithClick(root = self.manager.linksFrame, 
                                text =  "Links: " if haveLinks else "No links", 
                                prefix = "contentLinksIntroFr_" + self.prefix,
                                padding = [60, 0, 0, 0],
                                row = 0, column = 0)
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 1, "columnspan" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        linksEntriesFrame = ww.currUIImpl.Frame(prefix = self.prefix,
                                               name = "contentLinksEntriesFr_",
                                               rootWidget = self.scrollableBox.scrollable_frame,
                                               renderData = renderData,
                                               padding = [60, 0, 0, 0])
        return linksPrefixLabel, linksEntriesFrame

    def __produceLinksEntryFrame(self, parentWidget, linkSubsection, linksImIdx, row):
        entryFrameFactory = EntryWidgetFactoryLink(linkSubsection, linksImIdx, 0, 0, 
                                                   sourceSubsection = self.subsection, 
                                                   sourceImIdx = self.imIdx)
        entryFrameFactory.produceEntryWidgetsForFrame(parentWidget, row)
        entryWidgetManager = entryFrameFactory.entryFrameManager
        return entryWidgetManager
    
    def __produceLinksWebLinkFrame(self, parentWidget, subsection, imIdx, webLinkName, row):
        entryFrameFactory = EntryWidgetFactoryWebLink(subsection = subsection, 
                                                      imIdx = imIdx,
                                                      topPad = 0,
                                                      leftPad = 0,
                                                      webLinkName = webLinkName)
        entryFrameFactory.produceEntryWidgetsForFrame(parentWidget, row)
        entryWidgetManager = entryFrameFactory.entryFrameManager
        return entryWidgetManager
       

    def produceLinksEntryFrames(self):
        if fsf.Data.Sec.imGlobalLinksDict(self.subsection).get(self.imIdx) == None:
            return

        glLinks:dict = fsf.Data.Sec.imGlobalLinksDict(self.subsection)[self.imIdx].copy()

        # NOTE: should put all the links into 
        # one frame. This way they will be aligned correctly
        if type(glLinks) == dict:
            row = 0
            for ln, lk in glLinks.items():
                if "KIK" in lk:
                    targetSubsection = ln.split("_")[0]
                    targetImIdx = ln.split("_")[1]
                    self.__produceLinksEntryFrame(self.manager.entriesFrame, 
                                                  targetSubsection, 
                                                  targetImIdx,
                                                  row)
                elif "http" in lk:
                    self.__produceLinksWebLinkFrame(self.manager.entriesFrame, 
                                                  self.subsection, 
                                                  self.imIdx, 
                                                  ln,
                                                  row)
                    
                row += 1

    def produceLinksFrame(self, parentWidget, row, leftPad):
        linksFrame = self.produceMainFrame(parentWidget = parentWidget,
                                           row = row, 
                                           leftPad = leftPad)
        self.manager = LinksFrameManager(self.subsection, self.imIdx, linksFrame, self)

        imGlobalLinksDict = fsf.Data.Sec.imGlobalLinksDict(self.subsection)
        haveLinks = self.imIdx in imGlobalLinksDict.keys()

        linksPrefixLabel, linksEntriesFrame = self.produceLinksMainWidgets(haveLinks)
        linksPrefixLabel.render()
        linksEntriesFrame.render()
        self.manager.entriesFrame = linksEntriesFrame

class EntryWidgetFactoryWebLink(EntryWidgetFactory):
    class EntryUIs(EntryWidgetFactory.EntryUIs):
        def __init__(self):
            self.delete = self.__EntryUIData("[del]", 1, EntryWidgetFactoryLink.produceDeleteLinkLabel)
    
    def __init__(self, subsection, imIdx, topPad, leftPad, webLinkName):
        self.webLinkName = webLinkName

        super().__init__(subsection, imIdx, topPad, leftPad)
    
    def produceDeleteWebLink(self, parentWidget):
        def __delWebLinkCmd(event, efm):
            widget = event.widget
            gm.GeneralManger.RemoveWebLink(widget.subsection,
                                            widget.imIdx,
                                            widget.sourceWebLinkName)

            efm.remove()

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onRemoveLink" in dir(w):
                    w.onRemoveLink()
            
        linkLabelDelete = TOCLabelWithClick(parentWidget, 
                                            text = self.EntryUIs.delete.name, 
                                            prefix = "contentGlLinksTSubsectionDel_" + self.getPrefixID(),
                                            row = self.EntryUIs.delete.row, 
                                            column = 2)

        linkLabelDelete.subsection = self.subsection
        linkLabelDelete.imIdx = self.imIdx
        linkLabelDelete.sourceWebLinkName = self.webLinkName

        linkLabelDelete.rebind([ww.currUIImpl.Data.BindID.mouse1], 
                               [lambda e, m = self.entryFrameManager, *args: __delWebLinkCmd(e, m)])

        bindChangeColorOnInAndOut(linkLabelDelete)
        return linkLabelDelete

    def __produceEntryPrefixLabel(self, parentWidget):
        glLinkPrefixLbl = TOCLabelWithClick(parentWidget, 
                                                text = "web: ", 
                                                padding = [0, 0, 0, 0],
                                                prefix = "contentGlLinksTSubsection_" + self.getPrefixID(),
                                                row = 0, column = 0)
        return glLinkPrefixLbl

    def __produceMainImageLabel(self, parentWidget):
        def __openWebOfTheImageCmd(webLink):
            cmd = "open -na 'Google Chrome' --args --new-window \"" + webLink + "\""
            _u.runCmdAndWait(cmd)

        latexTxt = tff.Wr.TexFileUtils.formatEntrytext(self.webLinkName)
        currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        linkFilepath = _upan.Paths.Screenshot.Images.getWebLinkImageAbs(currBookPath,
                                                        self.subsection,
                                                        self.imIdx,
                                                        self.webLinkName)

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(linkFilepath):
            pilIm = Image.open(linkFilepath)
        else:
            pilIm = tff.Wr.TexFileUtils.fromTexToImage(latexTxt, linkFilepath) 

        shrink = 0.7
        pilIm.thumbnail([int(pilIm.size[0] * shrink),int(pilIm.size[1] * shrink)], Image.LANCZOS)
        img = ww.currUIImpl.UIImage(pilIm)

        glLinkLablel = TOCLabelWithClick(parentWidget,
                                    image = img,
                                    text = self.webLinkName, 
                                    prefix = "contentGlLinks_" + self.getPrefixID(),
                                    row = 0, column = 1)
        glLinkLablel.subsection = self.subsection
        glLinkLablel.imIdx = self.imIdx
        glLinkLablel.image = img

        glLinks:dict = fsf.Data.Sec.imGlobalLinksDict(self.subsection)[self.imIdx]

        glLinkLablel.rebind([ww.currUIImpl.Data.BindID.mouse1], \
                            [lambda e, wl = glLinks[self.webLinkName], *args: __openWebOfTheImageCmd(wl)])
        return glLinkLablel

    def produceEntryMainFrame(self, parentWidget):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 0, "columnspan" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        name = "_LinksMainImageFrame_"

        mainImageFrame = ww.currUIImpl.Frame(prefix = self.getPrefixID(),
                                             name = name, 
                                             rootWidget = parentWidget,
                                             renderData = renderData,
                                             padding = [0, 0, 0, 0])

        glLinkPrefixLbl = self.__produceEntryPrefixLabel(mainImageFrame)
        glLinkPrefixLbl.render()

        glLinkMainImLbl = self.__produceMainImageLabel(mainImageFrame)
        glLinkMainImLbl.render()

        return mainImageFrame

    def produceEntryWidgetsForFrame(self, parentWidget, row):
        self.frame = parentWidget
        self.entryFrameManager = self.produceEntryWidgetFrames(topPad = self.topPad, 
                                                               leftPad = self.leftPad,
                                                               row = row)

        mainImageWidget = self.produceEntryMainFrame(parentWidget = self.entryFrameManager.rowFrame1)
        mainImageWidget.render()

        deleteLabelWidget = self.produceDeleteWebLink(parentWidget = self.entryFrameManager.rowFrame1)
        deleteLabelWidget.render()

class EntryWidgetFactoryLink(EntryWidgetFactory):
    class EntryUIs(EntryWidgetFactory.EntryUIs):
        def __init__(self):
            self.full = self.__EntryUIData("[f]", 1, EntryWidgetFactory.produceFullMoveEntriesWidget)
            self.im = self.__EntryUIData("[i]", 2, EntryWidgetFactoryLink.produceOpenLinkImages)
            self.delete = self.__EntryUIData("[del]", 3, EntryWidgetFactoryLink.produceDeleteLinkLabel)
            self.excercises = self.__EntryUIData("[e]", 4, EntryWidgetFactory.produceOpenExcercisesWidget)
            self.proof = self.__EntryUIData("[pr]", 5, EntryWidgetFactory.produceOpenProofMenu, row = 0)

    def __init__(self, subsection, imIdx, topPad, leftPad, sourceSubsection, sourceImIdx):
        self.sourceSubsection = sourceSubsection
        self.sourceImIdx = sourceImIdx

        super().__init__(subsection, imIdx, topPad, leftPad)

    def produceOpenLinkImages(self, parentWidget):
        def showImagesCmd(e, efm):
            if not e.widget.clicked:
                efm.showImages(mainImPadLeft = 60, eImPadLeft = 60, createExtraImagesExtraWidgets = False)
            else:
                efm.hideImages()
            
            e.widget.clicked = not e.widget.clicked

        showImages = TOCLabelWithClick(parentWidget, 
                                    text = self.EntryUIs.im.name,
                                    prefix = "showImages_" + self.getPrefixID(),
                                    row = 0,
                                    column = self.EntryUIs.im.column)
        showImages.imIdx = self.imIdx
        showImages.subsection = self.subsection
        showImages.clicked = False
        showImages.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [lambda e, efm = self.entryFrameManager, *args: showImagesCmd(e, efm, *args)])
        bindChangeColorOnInAndOut(showImages)
        return showImages

    def produceDeleteLinkLabel(self, parentWidget):
        def __delGlLinkCmd(event, efm):
            widget = event.widget

            gm.GeneralManger.RemoveGlLink(widget.targetSubssection,
                                            widget.sourceSubssection,
                                            widget.sourceImIdx,
                                            widget.targetImIdx)
            efm.remove()

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onRemoveLink" in dir(w):
                    w.onRemoveLink()

        linkLabelDelete = TOCLabelWithClick(parentWidget, 
                                                    text = self.EntryUIs.delete.name, 
                                                    prefix = "contentGlLinksTSubsectionDel_" + self.getPrefixID(),
                                                    row = 0,
                                                    column = self.EntryUIs.delete.column)
        
        linkLabelDelete.targetSubssection = self.subsection
        linkLabelDelete.sourceSubssection = self.sourceSubsection
        linkLabelDelete.targetImIdx = self.imIdx
        linkLabelDelete.sourceImIdx = self.sourceImIdx

        linkLabelDelete.rebind([ww.currUIImpl.Data.BindID.mouse1], 
                               [lambda e, efm = self.entryFrameManager, *args: __delGlLinkCmd(e, efm)])
        bindChangeColorOnInAndOut(linkLabelDelete)
        return linkLabelDelete

    def __produceLinkPathLabel(self, parentWidget):
        glLinkSubsectioLbl = TOCLabelWithClick(parentWidget, 
                                               prefix = "contentGlLinksTSubsection_" + self.getPrefixID(),
                                               text = self.subsection + ": ", 
                                               padding = [0, 0, 0, 0],
                                               row = 0, column = 0)
        return glLinkSubsectioLbl

    def produceMainImageWidget(self, parentWidget):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 0, "columnspan" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        name = "_LinksMainImageFrame_"

        mainImageFrame = ww.currUIImpl.Frame(prefix = self.getPrefixID(),
                                             name = name, 
                                             rootWidget = parentWidget,
                                             renderData = renderData,
                                             padding = [0, 0, 0, 0])

        linkPathLabel = self.__produceLinkPathLabel(mainImageFrame)
        linkPathLabel.render()
        mainImageWidget = super().produceMainImageWidget(parentWidget = mainImageFrame,
                                                      leftPad = 0, column = 1)
        mainImageWidget.render()
        return mainImageFrame

    def produceEntryWidgetsForFrame(self, parentWidget, row):
        self.frame = parentWidget

        self.entryFrameManager = self.produceEntryWidgetFrames(topPad = self.topPad, 
                                                               leftPad = self.leftPad,
                                                               row = row)

        mainImageWidget = self.produceMainImageWidget(parentWidget = self.entryFrameManager.rowFrame1)
        mainImageWidget.render()

        # self.entryFrameManager.showImages(mainImPadLeft = 0, createExtraImagesExtraWidgets = False)

        full = self.EntryUIs.full.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        self.entryFrameManager.fullMoveWidget = full
        full.render()
        im = self.EntryUIs.im.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        im.render()
        delete = self.EntryUIs.delete.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        delete.render()
        excercises = self.EntryUIs.excercises.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        excercises.render()

        proof = self.EntryUIs.proof.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        proof.render()
