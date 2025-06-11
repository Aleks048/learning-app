import UI.widgets_collection.pdfReader.pdfReader as imw
import UI.widgets_collection.pdfReader.videoPlayer as viplmw

import UI.widgets_manager as wm
import file_system.file_system_facade as fsf
import _utils._utils_main as _u


class LayoutManagers:
    class PdfReadersLayout(wm.MenuLayout_Interface):
        prefix = "_PdfReadersLayout_"
        subsection = _u.Token.NotDef.str_t
        imIdx = _u.Token.NotDef.str_t
        extraImIdx = _u.Token.NotDef.int_t
        currPage = None
        selector = False
        changePrevPos = True
        getTextOfSelector = False

        pdfReaderSizeWhenVideo = 390
        pdfReaderSizeWhenVideoAndSummary = 50
        pdfReaderSizeWhenSummary = 500
        pdfRegularSize = 790

        def __init__(self, winRoot):
            super().__init__(winRoot)

            topFrame = wm.UI_generalManager.topLevelFrames["0000"]
            middleFrame = wm.UI_generalManager.topLevelFrames["0010"]
            bottomFrame = wm.UI_generalManager.topLevelFrames["0020"]

            self.pfdReader_BOX = imw.PfdReader_BOX(middleFrame, self.prefix)
            self.addWidget(self.pfdReader_BOX)
            self.resizePdfReaderWindow_BTN = imw.ResizePdfReaderWindow_BTN(middleFrame, self.prefix)
            self.addWidget(self.resizePdfReaderWindow_BTN)
            self.changePagePdfReaderWindow_ETR = imw.ChangePagePdfReaderWindow_ETR(middleFrame, self.prefix)
            self.addWidget(self.changePagePdfReaderWindow_ETR)

            self.secondaryEntry = imw.SecondaryImagesFrame(bottomFrame)
            self.addWidget(self.secondaryEntry)
            self.secondaryEntry.addListenerWidget(self.pfdReader_BOX)

            self.subsectionSummary = imw.SubsectionSummaryText(bottomFrame)
            self.videoPlayerFrame = viplmw.VideoPlayerRoot(topFrame)

            self.resizePdfReaderWindow_BTN.addListenerWidget(self.pfdReader_BOX)
            self.changePagePdfReaderWindow_ETR.addListenerWidget(self.pfdReader_BOX)

            # winRoot.setGeometry(*self.appDimensions)

        def show(self, dimensions = None):
            self.pfdReader_BOX.subsection = self.subsection

            if self.subsection != _u.Token.NotDef.str_t:
                if fsf.Data.Sec.isVideo(self.subsection):
                    self.appDimensions = [720, 117]

            self.pfdReader_BOX.imIdx = self.imIdx
            self.pfdReader_BOX.eImIdx = self.extraImIdx
            self.pfdReader_BOX.selectingZone = self.selector
            self.pfdReader_BOX.getTextOfSelector = self.getTextOfSelector

            if self.currPage != None:
                self.changePagePdfReaderWindow_ETR.changePage(None, self.currPage)
                self.pfdReader_BOX.changePage(self.currPage)

                self.currPage = None

            self.resizePdfReaderWindow_BTN.subsection = self.subsection
            self.resizePdfReaderWindow_BTN.imIdx = self.imIdx

            self.changePagePdfReaderWindow_ETR.subsection = self.subsection
            self.changePagePdfReaderWindow_ETR.imIdx = self.imIdx

            super().show()

        def showSummary(self, subsection):
            if not self.subsectionSummary.wasRendered:
                if self.videoPlayerFrame.wasRendered:
                    self.pfdReader_BOX.setCanvasHeight(self.pdfReaderSizeWhenVideoAndSummary)
                else:
                    self.pfdReader_BOX.setCanvasHeight(self.pdfReaderSizeWhenSummary)
                self.subsectionSummary.subsection = subsection
                self.subsectionSummary.render()
            else:
                if self.videoPlayerFrame.wasRendered:
                    self.pfdReader_BOX.setCanvasHeight(self.pdfReaderSizeWhenVideo)
                else:
                    self.pfdReader_BOX.setCanvasHeight(self.pdfRegularSize)
                
                self.subsectionSummary.subsection = subsection
                self.subsectionSummary.hide()

        def getVideoPosition(self):
            return self.videoPlayerFrame.getVideoPosition()

        def showVideo(self, subsection, imIdx):
            currSubsection  = self.videoPlayerFrame.videoLabel.subsection
            currImIdx = self.videoPlayerFrame.videoLabel.imIdx

            topFrame = wm.UI_generalManager.topLevelFrames["0000"]

            if (not self.videoPlayerFrame.wasRendered) \
                or (subsection != currSubsection) or (imIdx != currImIdx):
                self.pfdReader_BOX.setCanvasHeight(self.pdfReaderSizeWhenVideo)
                topFrame.render()
                self.videoPlayerFrame.render()
                self.videoPlayerFrame.showVideo(subsection, imIdx)
            else:
                self.pfdReader_BOX.setCanvasHeight(self.pdfRegularSize)
                self.videoPlayerFrame.hide()
                topFrame.hide()

        def hide(self):
            self.pfdReader_BOX.changePrevPos = self.changePrevPos
            return super().hide()
    
        def saveFigures(self):
             self.pfdReader_BOX.saveFigures()
            
        def forceUpdate(self):
            self.pfdReader_BOX.render(force = True)

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class PdfReadersManager(wm.MenuManager_Interface):
    imIdx = 0
    shown = False

    def __init__(self, rootWidget):
        winRoot = imw.PdfReadersRoot(rootWidget, 
                                     width = 0, 
                                     height = 0,
                                     topLevelFrameId = rootWidget.prefix)
        layouts = []
        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))
            
        self.subsection = fsf.Data.Book.currSection
        currLayout = layouts[0]
        currLayout.subsection = self.subsection
        
        super().__init__(winRoot,
                        layouts,
                        currLayout)

    def showSummary(self, subsection):
        self.layouts[0].showSummary(subsection)

    def showVideo(self, subsection, imIdx):
        return self.layouts[0].showVideo(subsection, imIdx)

    def getVideoPosition(self):
        return self.layouts[0].getVideoPosition()

    def forceUpdate(self):
        self.layouts[0].forceUpdate()
    
    def saveFigures(self):
        self.layouts[0].saveFigures()

    def unbind(self):
        self.winRoot.unbindAll()

    def removeLabel(self, subsection, imIdx, eImIdx):
        self.layouts[0].pfdReader_BOX.removeMainLabel(subsection, imIdx, eImIdx)

    def show(self, appDimensions = None, extraImIdx = None,
             subsection = None, imIdx = None, page = None, selector = False,
             changePrevPos = True, removePrevLabel = False, getTextOfSelector = False,
             withoutRender = False):
        self.winRoot.pageLbl = self.layouts[0].changePagePdfReaderWindow_ETR
        self.winRoot.pdfBox = self.layouts[0].pfdReader_BOX

        if removePrevLabel:
            self.layouts[0].pfdReader_BOX.removeMainLabel(subsection, imIdx, extraImIdx)

        if not withoutRender:
            self.hide(changePrevPos = changePrevPos)
        else:
            self.layouts[0].pfdReader_BOX.getIntoSelectingMode(subsection, imIdx, extraImIdx, 
                                                               getTextOfSelector)

        self.shown = True
        self.layouts[0].subsection = self.subsection if subsection == None else subsection
        self.layouts[0].imIdx = self.imIdx if imIdx == None else imIdx
        self.layouts[0].selector = selector
        self.layouts[0].extraImIdx = extraImIdx
        self.layouts[0].getTextOfSelector = getTextOfSelector

        if page != None:
            origMatName = fsf.Data.Book.currOrigMatName
            fsf.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(origMatName, int(page))
            self.layouts[0].currPage = page
        # self.layouts[0].appDimensions = appDimensions
        if not withoutRender:
            return super().show()

    def changeSize(self, dimensions = None):
        self.layouts[0].show(dimensions)

    def updateOMpage(self):
        self.layouts[0].pfdReader_BOX.updateOMpage()

    def hide(self, changePrevPos = False):
        self.layouts[0].changePrevPos = changePrevPos
        self.shown = False
        self.layouts[0].currPage = None
        return super().hide()

    def addSecondaryFrame(self, subsection, imIdx):
        self.layouts[0].secondaryEntry.addSecondaryFrame(subsection, imIdx)
        self.layouts[0].secondaryEntry.render()

    def moveToEntry(self, subsection, imIdx, eImIdx, forcePageChange = False):
        if eImIdx == None:
            currPage = int(fsf.Data.Sec.imLinkOMPageDict(subsection)[imIdx])
        else:
            currPage = int(fsf.Data.Sec.imLinkOMPageDict(subsection)[imIdx + "_" + str(eImIdx)])

        if forcePageChange:
            self.layouts[0].changePagePdfReaderWindow_ETR.changePage(None, currPage)

        self.layouts[0].currPage = currPage
        self.layouts[0].selector = False
        self.layouts[0].pfdReader_BOX.changePage(currPage)
        self.layouts[0].pfdReader_BOX.getIntoDrawingMode()

        if int(currPage) not in self.layouts[0].pfdReader_BOX.getShownPagesList():
            self.layouts[0].show()
        
        self.layouts[0].pfdReader_BOX.moveToEntryWidget(subsection, imIdx, eImIdx)
