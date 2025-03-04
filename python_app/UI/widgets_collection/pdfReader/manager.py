import UI.widgets_collection.pdfReader.pdfReader as imw

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

        def __init__(self, winRoot):
            self.winRoot = winRoot
            self.defaultAppDimensions = [720, 850]
            super().__init__(winRoot, self.defaultAppDimensions)
            self.pfdReader_BOX = imw.PfdReader_BOX(winRoot.topSubframe, self.prefix)
            self.addWidget(self.pfdReader_BOX)
            self.hidePdfReadersWindow_BTN = imw.HidePdfReaderWindow_BTN(winRoot.topSubframe, self.prefix)
            self.addWidget(self.hidePdfReadersWindow_BTN)
            self.resizePdfReaderWindow_BTN = imw.ResizePdfReaderWindow_BTN(winRoot.topSubframe, self.prefix)
            self.addWidget(self.resizePdfReaderWindow_BTN)
            self.changePagePdfReaderWindow_ETR = imw.ChangePagePdfReaderWindow_ETR(winRoot.topSubframe, self.prefix)
            self.addWidget(self.changePagePdfReaderWindow_ETR)

            self.secondaryEntry = imw.SecondaryImagesFrame(winRoot.bottomSubframe)
            self.addWidget(self.secondaryEntry)
            self.secondaryEntry.addListenerWidget(self.pfdReader_BOX)

            self.resizePdfReaderWindow_BTN.addListenerWidget(self.pfdReader_BOX)
            self.changePagePdfReaderWindow_ETR.addListenerWidget(self.pfdReader_BOX)

            winRoot.setGeometry(*self.appDimensions)

        def show(self, dimensions = None):
            self.pfdReader_BOX.subsection = self.subsection
            if dimensions == None:
                self.appDimensions = self.defaultAppDimensions
            else:
                self.appDimensions = dimensions

            if self.subsection != _u.Token.NotDef.str_t:
                if fsf.Data.Sec.isVideo(self.subsection):
                    self.appDimensions = [720, 517]

            self.pfdReader_BOX.imIdx = self.imIdx
            self.pfdReader_BOX.eImIdx = self.extraImIdx
            self.pfdReader_BOX.selectingZone = self.selector
            self.pfdReader_BOX.getTextOfSelector = self.getTextOfSelector

            if self.currPage != None:
                self.changePagePdfReaderWindow_ETR.changePage(None, self.currPage)
                self.pfdReader_BOX.changePage(self.currPage)

                self.currPage = None

            self.hidePdfReadersWindow_BTN.subsection = self.subsection
            self.hidePdfReadersWindow_BTN.imIdx = self.imIdx

            self.resizePdfReaderWindow_BTN.subsection = self.subsection
            self.resizePdfReaderWindow_BTN.imIdx = self.imIdx

            self.changePagePdfReaderWindow_ETR.subsection = self.subsection
            self.changePagePdfReaderWindow_ETR.imIdx = self.imIdx

            super().show()
        
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
                                     height = 0)
        layouts = []
        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))
            
        self.subsection = fsf.Data.Book.currSection
        currLayout = layouts[0]
        currLayout.subsection = self.subsection
        
        super().__init__(winRoot,
                        layouts,
                        currLayout)

    def forceUpdate(self):
        self.layouts[0].forceUpdate()
    
    def saveFigures(self):
        self.layouts[0].saveFigures()

    def unbind(self):
        self.winRoot.unbindAll()

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

    def moveToEntry(self, subsection, imIdx, eImIdx):
        currPage = int(fsf.Data.Sec.imLinkOMPageDict(subsection)[imIdx])
        self.layouts[0].show()
        self.layouts[0].changePagePdfReaderWindow_ETR.changePage(None, currPage)
        self.layouts[0].currPage = currPage
        self.layouts[0].selector = False
        # self.layouts[0].pfdReader_BOX.changePage(currPage)
        self.layouts[0].pfdReader_BOX.getIntoDrawingMode()
        self.layouts[0].pfdReader_BOX.moveToEntryWidget(subsection, imIdx, eImIdx)
