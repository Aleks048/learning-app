from PIL import Image

import UI.widgets_wrappers as ww
import UI.widgets_data as wd
import UI.widgets_facade as wf

from UI.factories.entriesWidgetsFactories import EntryWidgetFactoryTOC, EntryWidgetFactorySearchTOC, EntryWidgetFactory
from UI.widgets_collection.common import TOCLabelWithClick, GeneralPurpose_ETR, TOCFrame
from UI.widgets_collection.utils import bindWidgetTextUpdatable, bindChangeColorOnInAndOut


import file_system.file_system_facade as fsf
import data.temp as dt
import _utils.pathsAndNames as _upan
import settings.facade as sf
import _utils._utils_main as _u
import outside_calls.outside_calls_facade as ocf
import generalManger.generalManger as gm


class SubsectionStartPage_ETR(GeneralPurpose_ETR):
    def __init__(self, patentWidget, prefix, row, column, imIdx, text, width=3):
        self.subsection = None
        super().__init__(patentWidget, prefix, row, column, imIdx, text, width)


class SubsectionPath_ETR(GeneralPurpose_ETR):
    def __init__(self, patentWidget, prefix, row, column, imIdx, text, width=3):
        self.subsection = None
        super().__init__(patentWidget, prefix, row, column, imIdx, text, width)


class SubsectionLabelWithClick(TOCLabelWithClick):
    def __init__(self, root, prefix, 
                 row, column, columnspan=1, sticky=ww.currUIImpl.Orientation.NW, 
                 padding=[0, 0, 0, 0], image=None, text=None):
        self.subsection = None
        super().__init__(root, prefix, row, column, columnspan, sticky, padding, image, text)

class TOCLabeWithClickSubsection(SubsectionLabelWithClick):   
    def updateLabel(self):
        if self.subsection in list(fsf.Data.Book.sections.keys()):
            topSectionImgPath = _upan.Paths.Screenshot.Images.getTopSectionEntryImageAbs(
                                                            sf.Wr.Manager.Book.getCurrBookName(),
                                                            self.subsection)

            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(topSectionImgPath):
                self.result = Image.open(topSectionImgPath)
            else:
                self.result = fsf.Wr.SectionInfoStructure.rebuildTopSectionLatex(self.subsection,
                                                                            _upan.Names.Subsection.getTopSectionPretty)
            result = self.result
            shrink = 0.8
            result.thumbnail([int(result.size[0] * shrink),int(result.size[1] * shrink)], Image.LANCZOS)
            self.image = ww.currUIImpl.UIImage(result)
            super().updateImage(self.image)
        else:
            subsectionImgPath = _upan.Paths.Screenshot.Images.getSubsectionEntryImageAbs(
                                                            sf.Wr.Manager.Book.getCurrBookName(), 
                                                            self.subsection)

            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(subsectionImgPath):
                self.result = Image.open(subsectionImgPath)
            else:
                self.result = \
                    fsf.Wr.SectionInfoStructure.rebuildSubsectionImOnlyLatex(self.subsection, 
                                                                            _upan.Names.Subsection.getSubsectionPretty)
            result = self.result
            shrink = 0.8
            result.thumbnail([int(result.size[0] * shrink),int(result.size[1] * shrink)], Image.LANCZOS)
            self.image = ww.currUIImpl.UIImage(result)
            super().updateImage(self.image)


class SubsectionFrameManager:
    def __init__(self, subsection, subsectionFrame, topFrame, entriesFrame, subsectionChildrenSectionsFrame, widgetFactory):
        self.opened = False
        
        self.factory = widgetFactory
        self.subsection = subsection

        self.subsectionFrame = subsectionFrame
        self.topFrame = topFrame
        self.entriesFrame = entriesFrame
        self.subsectionChildrenSectionsFrame = subsectionChildrenSectionsFrame

        self.openContentWidget = None
        self.entriesWidgetManagers = {}

    def removeAllSubsections(self):
        self.subsectionChildrenSectionsFrame.destroy()

        self.subsectionChildrenSectionsFrame = \
            self.factory.produceSectionChildrenSectionsFrame(self.subsectionFrame)


    def openSubsection(self):
        self.opened = True

        if self.openContentWidget != None:
            self.openContentWidget.clicked = True
            self.openContentWidget.changeColor("brown")
            bindChangeColorOnInAndOut(self.openContentWidget, True)

    def closeSubsection(self):
        self.opened = False

        for ch in self.entriesFrame.getChildren().copy():
            ch.destroy()
        
        if self.openContentWidget != None:
            self.openContentWidget.clicked = False
            self.openContentWidget.changeColor("white")
            bindChangeColorOnInAndOut(self.openContentWidget, False)

        self.entriesFrame.hide()

        self.entriesWidgetManagers = {}

class SubsectionFrameManagerMainTOC(SubsectionFrameManager):
    def addEntryWidget(self, imIdx):                
        entryWidgetFactory = EntryWidgetFactoryTOC(self.subsection, imIdx, 0, 0)
        row = len(list(self.entriesWidgetManagers.keys()))
        entryWidgetFactory.produceEntryWidgetsForFrame(self.entriesFrame, row)

        self.entriesWidgetManagers[imIdx] = entryWidgetFactory.entryFrameManager

    def addEntryWidgetsForSubsection(self, filter = ""):
        entries = fsf.Data.Sec.imLinkDict(self.subsection)

        row = 0

        for imIdx in entries.keys():
            if imIdx == _u.Token.NotDef.str_t:
                continue

            self.addEntryWidget(imIdx)

            row += 1

class SubsectionFrameManagerSearchTOC(SubsectionFrameManager):
    def addEntryWidget(self, imIdx):                
        entryWidgetFactory = EntryWidgetFactorySearchTOC(self.subsection, imIdx, 0, 0)
        row = len(list(self.entriesWidgetManagers.keys()))
        entryWidgetFactory.produceEntryWidgetsForFrame(self.entriesFrame, row)
        self.entriesWidgetManagers[imIdx] = entryWidgetFactory.entryFrameManager

    def addEntryWidgetsForSubsection(self, filter = ""):
        entries = fsf.Data.Sec.imLinkDict(self.subsection)
        extraImTexts = fsf.Data.Sec.extraImText(self.subsection)

        row = 0

        for imIdx, imText in entries.items():
            if imIdx == _u.Token.NotDef.str_t:
                continue

            filterInImageText = False

            entryImText = fsf.Wr.SectionInfoStructure.getEntryImText(self.subsection, imIdx)
            filterInImageText = filter.lower() in entryImText.lower()
            
            if not filterInImageText:
                if extraImTexts.get(imIdx) != None:
                    extraImText = extraImTexts[imIdx]
                    for t in extraImText:
                        if filter.lower() in t.lower():
                            filterInImageText = True
                            break
                

            if (filter.lower() in imText.lower()) \
                or filterInImageText:
                self.addEntryWidget(imIdx)

            row += 1

class SubsectionWidgetFactory:
    class EntryUIs:
        class __EntryUIData:
            def __init__(self, name, column, cmd, row = 0) -> None:
                self.name = name
                self.column = column
                self.row = row
                self.cmd = cmd

        def __init__(self):
            self.content = self.__EntryUIData("[content]", 1, SubsectionWidgetFactory.produceOpenContentWidget)
            self.hideSubsections = self.__EntryUIData("[show/hide]", 2, SubsectionWidgetFactory.produceShowHideSubsectionLabel)
            self.startPage = self.__EntryUIData("", 3, SubsectionWidgetFactory.produceChangeStartPageETR)
            self.summary = self.__EntryUIData("[summary]", 4, SubsectionWidgetFactory.produceSubsectionSummary)
            self.path = self.__EntryUIData("", 5, SubsectionWidgetFactory.produceUpdateSubsectionPathETR)
            self.showVideo = self.__EntryUIData("[show video]", 6, SubsectionWidgetFactory.produceShowVideoLabel)
            self.remove = self.__EntryUIData("[delete]", 7, SubsectionWidgetFactory.produceRemoveSubsectionLabel)
            self.rebuild = self.__EntryUIData("[rebuild latex]", 8, SubsectionWidgetFactory.produceSubsectionRebuildLatex)

    def __init__(self, subsection):
        self.subsection = subsection
        self.widgetManager = None
        self.frame = None

        self.EntryUIs = self.EntryUIs()

    def __getPrefix(self):
        nameId = "subsecLabel_" + self.subsection 
        return nameId.replace(".", "")

    def __bindOpenPdfOnStartOfTheSection(self, widget):
        def __cmd(event = None, *args):
            # open orig material on page
            origMatNameDict = fsf.Data.Sec.origMatNameDict(self.subsection)
            omName = origMatNameDict[list(origMatNameDict.keys())[-1]]

            if str(omName) == _u.Token.NotDef.str_t:
                # when there is no entries yet we use the current origMaterial name
                omName = fsf.Data.Book.currOrigMatName

            subsectionStartPage = fsf.Data.Sec.start(self.subsection)
            fsf.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(omName, subsectionStartPage)

            pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.PdfReadersManager)
            pdfReadersManager.show(page = int(subsectionStartPage))

            event.widget.changeColor("white")
        
        widget.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])

    def __bindUpdateSubsection(self, event, *args):
        def __setTextFunc(newText, widget):
            subsection = widget.subsection
            if subsection in list(fsf.Data.Book.sections.keys()):
                sections = fsf.Data.Book.sections
                sections[subsection]["name"] = newText
                fsf.Data.Book.sections = sections
            else:
                fsf.Data.Sec.text(event.widget.subsection, newText)

        def __getTextFunc(widget):
            subsection = widget.subsection
            sectionName = ""
            if subsection in list(fsf.Data.Book.sections.keys()):
                # Top section
                sectionName = fsf.Data.Book.sections[subsection]["name"]
            else:
                sectionName = fsf.Data.Sec.text(subsection)

            return sectionName
        
        def __updateImageFunc(widget):
            subsection = widget.subsection
            if subsection in list(fsf.Data.Book.sections.keys()):
                fsf.Wr.SectionInfoStructure.rebuildTopSectionLatex(widget.subsection,
                                                                _upan.Names.Subsection.getTopSectionPretty)
            else:
                fsf.Wr.SectionInfoStructure.rebuildSubsectionImOnlyLatex(widget.subsection,
                                                                _upan.Names.Subsection.getSubsectionPretty)

        bindWidgetTextUpdatable(event, __getTextFunc, __setTextFunc, __updateImageFunc)

    def produceTopSectionLatexImage(self):
        topSectionImgPath = _upan.Paths.Screenshot.Images.getTopSectionEntryImageAbs(
                                                            sf.Wr.Manager.Book.getCurrBookName(),
                                                            self.subsection)

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(topSectionImgPath):
            result = Image.open(topSectionImgPath)
        else:
            result = fsf.Wr.SectionInfoStructure.rebuildTopSectionLatex(self.subsection,
                                                                        _upan.Names.Subsection.getTopSectionPretty)

        shrink = 0.8
        result.thumbnail([int(result.size[0] * shrink),int(result.size[1] * shrink)], Image.LANCZOS)
        result = ww.currUIImpl.UIImage(result)

        subsectionLabel = TOCLabeWithClickSubsection(root = self.widgetManager.topFrame,
                                                    image = result,
                                                    prefix = "_topSection" + self.__getPrefix(), 
                                                    padding = [0, 0, 0, 0],
                                                    row = 0, column= 0)
        subsectionLabel.image = result
        subsectionLabel.subsection = self.subsection
        subsectionLabel.rebind([ww.currUIImpl.Data.BindID.mouse2],
                                [self.__bindUpdateSubsection])
        self.__bindOpenPdfOnStartOfTheSection(subsectionLabel)
        return subsectionLabel

    def produceTopSectionExtraWidgets(self):
        openContentLabel = self.produceOpenContentWidget()
        openContentLabel.render()

    def produceOpenContentWidget(self):
        def openContentOfSubsection(e):
            widget = e.widget
            isTopSection = len(widget.subsection.split(".")) == 1

            if not widget.clicked:
                if isTopSection:
                    fsf.Data.Book.currTopSection = widget.subsection
                else:
                    fsf.Data.Book.subsectionOpenInTOC_UI = widget.subsection
                    fsf.Data.Book.currSection = widget.subsection

                for w in wd.Data.Reactors.subsectionChangeReactors.values():
                    if isTopSection:
                        if "onTopSectionOpen" in dir(w):
                            w.onTopSectionOpen(widget.subsection)
                    else:
                        if "onSubsectionOpen" in dir(w):
                            w.onSubsectionOpen(widget.subsection)
                
                widget.changeColor("brown")
                bindChangeColorOnInAndOut(widget, shouldBeBrown = True)
                widget.clicked = True
            else:
                if isTopSection:
                    fsf.Data.Book.currTopSection = _u.Token.NotDef.str_t
                else:
                    fsf.Data.Book.subsectionOpenInTOC_UI = _u.Token.NotDef.str_t
                    fsf.Data.Book.currSection = _u.Token.NotDef.str_t

                for w in wd.Data.Reactors.subsectionChangeReactors.values():
                    if isTopSection:
                        if "onTopSectionClose" in dir(w):
                            w.onTopSectionClose(widget.subsection)
                    else:
                        if "onSubsectionClose" in dir(w):
                            w.onSubsectionClose(widget.subsection)

                widget.changeColor("white")
                bindChangeColorOnInAndOut(widget, shouldBeBrown = False)
                widget.clicked = False

        openContentLabel = SubsectionLabelWithClick(self.widgetManager.topFrame, text = self.EntryUIs.content.name, 
                                            prefix = "subsecContent" + self.__getPrefix(),
                                            row = 0, column= self.EntryUIs.content.column)
        openContentLabel.subsection = self.subsection

        self.widgetManager.openContentWidget = openContentLabel

        openContentLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], 
                    [lambda e, *args: openContentOfSubsection(e)])
        bindChangeColorOnInAndOut(openContentLabel)
        return openContentLabel

    def produceSubsectionRebuildLatex(self):
        def rebuildSubsectionLatexWrapper(subsection):
            fsf.Wr.SectionInfoStructure.rebuildSubsectionLatex(subsection,
                                                            _upan.Names.Group.formatGroupText,
                                                            _upan.Names.Subsection.getSubsectionPretty,
                                                            _upan.Names.Subsection.getTopSectionPretty)

            for w in wd.Data.Reactors.subsectionChangeReactors.values():
                if "onRebuildSubsectionLatex" in dir(w):
                    w.onRebuildSubsectionLatex(subsection)

        rebuildLatex = SubsectionLabelWithClick(self.widgetManager.topFrame, text = self.EntryUIs.rebuild.name,
                                        prefix = "subsecRebuild" + self.__getPrefix(),
                                        row = 0, column = self.EntryUIs.rebuild.column)
        rebuildLatex.subsection = self.subsection

        bindChangeColorOnInAndOut(rebuildLatex)
        rebuildLatex.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [lambda e, *args: rebuildSubsectionLatexWrapper(e.widget.subsection)])
        return rebuildLatex

    def produceSubsectionSummary(self):
        def cmd(subsection):
            summaryManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.SummaryManager)
            summaryManager.showSummary(subsection)
            if not summaryManager.shown:
                summaryManager.show()

        
        showSummary = SubsectionLabelWithClick(self.widgetManager.topFrame, text = self.EntryUIs.summary.name,
                                            prefix = "summary" + self.subsection.replace(".", ""),
                                            row = 0, column = self.EntryUIs.summary.column)
        showSummary.subsection = self.subsection

        bindChangeColorOnInAndOut(showSummary)
        showSummary.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [lambda e, *args: cmd(e.widget.subsection)])

        return showSummary

    def produceShowVideoLabel(self):
        def showSubsectiionVideoWrapper(subsection):  
            pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.PdfReadersManager)
            pdfReadersManager.showVideo(subsection, "0")

            for w in wd.Data.Reactors.subsectionChangeReactors.values():
                if "onShowVideo" in dir(w):
                    w.onShowVideo(subsection)

        showVideo = SubsectionLabelWithClick(self.widgetManager.topFrame, text = self.EntryUIs.showVideo.name,
                                            prefix = "showVideo" + self.subsection.replace(".", ""),
                                            row = 0, column = self.EntryUIs.showVideo.column)
        showVideo.subsection = self.subsection

        bindChangeColorOnInAndOut(showVideo)
        showVideo.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [lambda e, *args: showSubsectiionVideoWrapper(e.widget.subsection)])

        return showVideo

    def produceChangeStartPageETR(self):
        def __updateStartPage(e, *args):
            newStartPage = e.widget.getData()
            subsection = e.widget.subsection
            fsf.Data.Sec.start(subsection, newStartPage)
            omName = fsf.Data.Book.currOrigMatName
            
            fsf.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(omName, newStartPage)

            pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.PdfReadersManager)
            pdfReadersManager.show(page = int(newStartPage))

            for w in wd.Data.Reactors.subsectionChangeReactors.values():
                if "onUpdateSubsectionStartPage" in dir(w):
                    w.onUpdateSubsectionStartPage(subsection)

        startPage = fsf.Data.Sec.start(self.subsection)
        changeStartPage = SubsectionStartPage_ETR(self.widgetManager.topFrame,
                                        prefix = "updateStartPageEntryText" + self.subsection.replace(".", ""),
                                        row = 0, 
                                        column = self.EntryUIs.startPage.column,
                                        imIdx = -1,
                                        text = startPage)
        changeStartPage.subsection = self.subsection
        changeStartPage.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                [lambda e, *args:__updateStartPage(e, changeStartPage.subsection, *args)])
        
        return changeStartPage

    def produceUpdateSubsectionPathETR(self):
        def __updateSubsectionPath(e, *args):
            targetSubsection = e.widget.getData()
            subsection = e.widget.subsection
            sourceSubsection = subsection

            # ask the user if we wnat to proceed.
            msg = "Do you want to move \n\n subsection\n'{0}' \n\nto \n'{1}'?".format(sourceSubsection, targetSubsection)
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

            mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.show()

            if not response:
                return

            gm.GeneralManger.MoveSubsection(sourceSubsection,
                                            targetSubsection)
            
            for w in wd.Data.Reactors.subsectionChangeReactors.values():
                if "onUpdateSubsectionPath" in dir(w):
                    w.onUpdateSubsectionPath(subsection)

        updateSubsectionPath = SubsectionPath_ETR(self.widgetManager.topFrame,
                                                prefix = "updateSubsectionPosEntryText" + self.subsection.replace(".", ""),
                                                row = 0, 
                                                column = self.EntryUIs.path.column,
                                                imIdx = -1,
                                                text = self.subsection,
                                                width = 20)
        updateSubsectionPath.subsection = self.subsection
        updateSubsectionPath.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                [lambda e, *args:__updateSubsectionPath(e, updateSubsectionPath.subsection, *args)])

        return updateSubsectionPath

    def produceRemoveSubsectionLabel(self):
        def __removeSubsection(e, subsection, *args):
            sourceSubsection = subsection

            # ask the user if we wnat to proceed.
            msg = "Do you want to \n\nREMOVE \n\n subsection:\n'{0}'?".format(sourceSubsection)
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

            mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.show()

            if not response:
                return

            gm.GeneralManger.DeleteSubsection(sourceSubsection)

            for w in wd.Data.Reactors.subsectionChangeReactors:
                if "onSubsectionRemove" in dir(w):
                    w.onSubsectionRemove(subsection)

        removeSubsection = SubsectionLabelWithClick(self.widgetManager.topFrame,
                                                prefix = "removeSubsectionPosEntryText" + self.subsection.replace(".", ""),
                                                row = 0, 
                                                column = self.EntryUIs.remove.column,
                                                text = self.EntryUIs.remove.name)
        removeSubsection.subsection = self.subsection

        bindChangeColorOnInAndOut(removeSubsection)
        removeSubsection.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [lambda e, *args:__removeSubsection(e, removeSubsection.subsection, *args)])

        return removeSubsection

    def produceShowHideSubsectionLabel(self):
        def showHideSubsectionsWrapper(subsection):
            subsectionsHidden:list = fsf.Data.Book.subsectionsHiddenInTOC_UI

            if subsection in subsectionsHidden:
                subsectionsHidden.remove(subsection)
            else:
                subsectionsHidden.append(subsection)
            
            fsf.Data.Book.subsectionsHiddenInTOC_UI =  subsectionsHidden

            for w in wd.Data.Reactors.subsectionChangeReactors.values():
                if "onSubsectionShowHide" in dir(w):
                    w.onSubsectionShowHide(subsection)

        hideSubsections = SubsectionLabelWithClick(self.widgetManager.topFrame, 
                                            text = self.EntryUIs.hideSubsections.name,
                                            prefix = "subsecShowHide" + self.subsection.replace(".", ""),
                                            row = 0, 
                                            column = self.EntryUIs.hideSubsections.column)
        subsectionsList = fsf.Wr.BookInfoStructure.getSubsectionsList(self.subsection)

        if subsectionsList != []:
            hideSubsections.changeColor("brown")

        hideSubsections.subsection = self.subsection

        if subsectionsList != []:
            bindChangeColorOnInAndOut(hideSubsections, shouldBeBrown = True)
        else:
            bindChangeColorOnInAndOut(hideSubsections)

        hideSubsections.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [lambda e, *args: showHideSubsectionsWrapper(e.widget.subsection)])
        
        return hideSubsections

    def produceSubsectionExtraWidgets(self):
        openContentLabel = self.EntryUIs.content.cmd(self)
        openContentLabel.render()

        rebuildLatexLabel = self.EntryUIs.rebuild.cmd(self)
        rebuildLatexLabel.render()

        if fsf.Data.Sec.isVideo(self.subsection):
            showVideoLabel =  self.EntryUIs.showVideo.cmd(self)
            showVideoLabel.render()
        
        changeStartPageEtr =  self.EntryUIs.startPage.cmd(self)
        changeStartPageEtr.render()

        updateSubsectionPathETR = self.EntryUIs.path.cmd(self)
        updateSubsectionPathETR.render()

        removeSubsectionLabel = self.EntryUIs.remove.cmd(self)
        removeSubsectionLabel.render()

        showHideSubsectionLabel = self.EntryUIs.hideSubsections.cmd(self)
        showHideSubsectionLabel.render()

        showSummaryLabel = self.EntryUIs.summary.cmd(self)
        showSummaryLabel.render()

    def produceSubsectionLatexImage(self):
        subsectionImgPath = _upan.Paths.Screenshot.Images.getSubsectionEntryImageAbs(
                                                            sf.Wr.Manager.Book.getCurrBookName(), 
                                                            self.subsection)

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(subsectionImgPath):
            result = Image.open(subsectionImgPath)
        else:
            result = \
                fsf.Wr.SectionInfoStructure.rebuildSubsectionImOnlyLatex(self.subsection, 
                                                                        _upan.Names.Subsection.getSubsectionPretty)

        shrink = 0.8
        result.thumbnail([int(result.size[0] * shrink),int(result.size[1] * shrink)], Image.LANCZOS)
        result = ww.currUIImpl.UIImage(result)

        subsectionLabel = TOCLabeWithClickSubsection(self.widgetManager.topFrame, 
                                            image = result, 
                                            prefix = "_subsecion" + self.__getPrefix(),
                                            row = 0, column= 0)
        subsectionLabel.image = result
        subsectionLabel.subsection = self.subsection
        subsectionLabel.rebind([ww.currUIImpl.Data.BindID.mouse2],
                                [self.__bindUpdateSubsection])
        self.__bindOpenPdfOnStartOfTheSection(subsectionLabel)
        return subsectionLabel

    def produceSectionChildrenSectionsFrame(self, parentWidget):
        subsectionChildrenSectionsFrame = TOCFrame(parentWidget, 
                                                   "subsectionChildrenSectionsFrame" + self.__getPrefix(), 
                                                   row = 2, 
                                                   column = 0, 
                                                   columnspan = 1, 
                                                   padding = [0, 0, 0, 0])
        subsectionChildrenSectionsFrame.render()

        return subsectionChildrenSectionsFrame

    def produceSubsectionFrame(self, row):
        topPad = 0 if (len(self.subsection.split(".")) != 1) or (row == 0) else 20

        subsectionFrame = TOCFrame(self.frame, "subsectionFrame" + self.__getPrefix(), row, 
                         column = 0, columnspan = 1, padding = [0, topPad, 0, 0])
        subsectionFrame.render()

        topFrame = TOCFrame(subsectionFrame, "subsectionTopFrame" + self.__getPrefix(), row = 0, 
                         column = 0, columnspan = 1, padding = [0, 0, 0, 0])
        topFrame.render()

        entriesFrame = TOCFrame(subsectionFrame, "subsectionEntriesFrame" + self.__getPrefix(), row = 1, 
                         column = 0, columnspan = 1, padding = [0, 0, 0, 0])
        entriesFrame.render()
        
        subsectionChildrenSectionsFrame = self.produceSectionChildrenSectionsFrame(subsectionFrame)

        return subsectionFrame, \
               topFrame, \
               entriesFrame, \
               subsectionChildrenSectionsFrame

class SubsectionWidgetFactoryMainTOC(SubsectionWidgetFactory):
    def produceSubsectionWidgets(self, parentFrame, row):
        self.frame = parentFrame

        subsectionFrame, topFrame, entriesFrame, subsectionChildrenSectionsFrame = \
                                                         self.produceSubsectionFrame(row)

        self.widgetManager = SubsectionFrameManagerMainTOC(self.subsection, 
                                                    subsectionFrame, 
                                                    topFrame, 
                                                    entriesFrame, 
                                                    subsectionChildrenSectionsFrame,
                                                    self)
        
        if len(self.subsection.split(".")) == 1:
            subsectionImageLabel = self.produceTopSectionLatexImage()
        else:
            subsectionImageLabel = self.produceSubsectionLatexImage()
        
        subsectionImageLabel.render()

        if len(self.subsection.split(".")) == 1:
            self.produceTopSectionExtraWidgets()
        else:
            self.produceSubsectionExtraWidgets()

class SubsectionWidgetFactorySearchTOC(SubsectionWidgetFactory):
    def produceSubsectionWidgets(self, parentFrame, row):
        self.frame = parentFrame

        subsectionFrame, topFrame, entriesFrame, subsectionChildrenSectionsFrame = \
                                                         self.produceSubsectionFrame(row)

        self.widgetManager = SubsectionFrameManagerSearchTOC(self.subsection, 
                                                    subsectionFrame, 
                                                    topFrame, 
                                                    entriesFrame, 
                                                    subsectionChildrenSectionsFrame,
                                                    self)
        
        if len(self.subsection.split(".")) == 1:
            subsectionImageLabel = self.produceTopSectionLatexImage()
        else:
            subsectionImageLabel = self.produceSubsectionLatexImage()
        
        subsectionImageLabel.render()

        if len(self.subsection.split(".")) == 1:
            self.produceTopSectionExtraWidgets()
        else:
            self.produceSubsectionExtraWidgets()

    def produceSubsectionExtraWidgets(self):
        if fsf.Data.Sec.isVideo(self.subsection):
            showVideoLabel =  self.EntryUIs.showVideo.cmd(self)
            showVideoLabel.render()

        updateSubsectionPathETR = self.EntryUIs.path.cmd(self)
        updateSubsectionPathETR.render()

        removeSubsectionLabel = self.EntryUIs.remove.cmd(self)
        removeSubsectionLabel.render()

        showSummaryLabel = self.EntryUIs.summary.cmd(self)
        showSummaryLabel.render()
