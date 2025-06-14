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
            super().__init__(winRoot)

            self.pfdReader_BOX = imw.PfdReader_BOX(winRoot, 
                                                   self.prefix,
                                                   width = winRoot.width,
                                                   height = winRoot.height - 45)
            self.addWidget(self.pfdReader_BOX)
            self.resizePdfReaderWindow_BTN = imw.ResizePdfReaderWindow_BTN(winRoot, self.prefix)
            self.addWidget(self.resizePdfReaderWindow_BTN)
            self.changePagePdfReaderWindow_ETR = imw.ChangePagePdfReaderWindow_ETR(winRoot, self.prefix)
            self.addWidget(self.changePagePdfReaderWindow_ETR)

            self.resizePdfReaderWindow_BTN.addListenerWidget(self.pfdReader_BOX)
            self.changePagePdfReaderWindow_ETR.addListenerWidget(self.pfdReader_BOX)

        def show(self, dimensions = None):
            self.pfdReader_BOX.subsection = self.subsection

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
    topFrame = None

    def __init__(self, rootWidget):
        self.topFrame = rootWidget

        dimensions = _u.getMonitorsAreas()[0]
        width = dimensions[2] # 1500
        height = dimensions[3] - 50 # 850

        halfWidth = int(width / 2)

        width = halfWidth, 
        height = height - 105
        rootWidget.width = width
        rootWidget.height = height
        rootWidget.setGeometry(width, height)

        winRoot = imw.PdfReadersRoot(rootWidget, 
                                     width = rootWidget.width, 
                                     height = rootWidget.height,
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

    def updateOMpage(self):
        self.layouts[0].pfdReader_BOX.updateOMpage()

    def hide(self, changePrevPos = False):
        self.layouts[0].changePrevPos = changePrevPos
        self.shown = False
        self.layouts[0].currPage = None
        return super().hide()

    def reduceHeight(self, delta):
        pdfBox = self.layouts[0].pfdReader_BOX
        pdfBox.setCanvasHeight(pdfBox.height - delta)    
        self.topFrame.setGeometry(self.topFrame.width, self.topFrame.height - delta)    

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
