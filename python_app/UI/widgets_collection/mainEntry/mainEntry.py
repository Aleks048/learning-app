import file_system.file_system_facade as fsf

import _utils._utils_main as _u

import UI.widgets_data as wd
import UI.widgets_collection.common as comw


class MainEntryBox(comw.EntryWindow_BOX): 
    def __init__(self, parentWidget, prefix):
        super().__init__(parentWidget, prefix)
        self.origHeight = self.maxHeight

    def changeLinksSize(self):
        self.entryManager.linksFrameManager.makeLinksLarge()

    def setCanvasHeight(self, newHeight):
        if self.entryManager != None:
            self.entryManager.linksFrameManager.updateLinksHeight()

            if wd.Data.MainEntryLayout.currSize == wd.Data.MainEntryLayout.large:
                if self.linkFrameShown:
                    self.entryManager.imagesFrameScroll.setCanvasHeight(300)
                else:
                    self.entryManager.imagesFrameScroll.setCanvasHeight(600)
        else:
            newHeight = 300
    
        return super().setCanvasHeight(newHeight)

    def notificationRetakeImage(self, subsection, imIdx):
        super().setMain(subsection, imIdx)

    def notificationResizeImage(self, subsection, imIdx):
        super().setMain(subsection, imIdx)

    def notificationlinkFullMove(self, subsection, imIdx):
        super().setMain(subsection, imIdx)

    def notificationAfterImageWasCreated(self, subsection, imIdx):
        super().setMain(subsection, imIdx)

    def onLinksShow(self, subsection, imIdx, showLinks):
        self.linkFrameShown = showLinks

        linksHeight = self.entryManager.linksFrameManager.linksFrame.getHeight()
        self.entryManager.imagesFrameScroll.setCanvasHeight(350 - linksHeight)
        super().updateHeight()

    def onAddExtraImage(self, subsection, mainImIdx, extraImIdx):
        etm = self.entryManager
        if etm != None:
            eImFrame = etm.addExtraImIdx(extraImIdx)
            if eImFrame != None:
                self.scrollIntoView(None, eImFrame)
                self.updateHeight()

    def onTextOnlyTextUpdate(self):
        self.updateHeight()

    def onEntryTextUpdate(self):
        self.updateHeight()

    def onShowLinks(self):
        self.linkFrameShown = True
        self.updateHeight()

    def onRemoveLink(self):
        self.updateHeight()

    def onFullEntryMove(self):
        if fsf.Data.Book.entryImOpenInTOC_UI != _u.Token.NotDef.str_t:
            self.subsection = fsf.Data.Book.subsectionOpenInTOC_UI
            self.imIdx = fsf.Data.Book.entryImOpenInTOC_UI
            self.render()
        else:
            #TODO: should update the height()
            self.hideAllWithChildren()
            self.updateHeight()


    def onImageResize(self, subsection, imIdx, eImIdx):
        if (subsection == self.subsection) and (imIdx == self.imIdx):
            if self.entryManager != None:
                if eImIdx == None:
                    self.entryManager.updateMainImage()
                else:
                    self.entryManager.updateExtraImage(eImIdx)
                self.entryManager.updateResizeEtrText()

    def onRetakeAfter(self, subsection, imIdx, eImidx = _u.Token.NotDef.str_t):
        if self.entryManager != None:
            self.entryManager.updateMainImage()

    def onAlwaysShowChange(self, subsection, imIdx):
        if self.entryManager != None:
            for ch in self.entryManager.rowFrame2.getChildren():
                ch.render()

    def onPasteLink(self):
        if self.entryManager != None:
            self.linkFrameShown = True
            self.render()

    def onMainLatexImageUpdate(self, subsection, imIdx):
        if self.entryManager != None:
            etm = self.entryManager
            etm.updateEntryImage()

    def onEntryShift(self, subsection, imIdx):
        pass

    def onExtraImDelete(self, subsection, imIdx, eImIdx):
        if self.entryManager != None:
            etm = self.entryManager
            etm.deleteExtraImage(eImIdx)

    def onExtraImMove(self, subsection, imIdx, eImIdx, moveUp:bool):
        if self.entryManager != None:
            etm = self.entryManager
            eImFrame = etm.moveExtraIm(eImIdx, moveUp)

            if eImFrame != None:
                self.shouldScroll = True
                self.scrollIntoView(None, eImFrame)

    def render(self, scrollTOC=True):
        wd.Data.Reactors.entryChangeReactors[self.name] = self
        wd.Data.Reactors.subsectionChangeReactors[self.name] = self
        super().render(scrollTOC)

        if self.linkFrameShown:
            self.entryManager.linksFrameManager.showLinks()

