import UI.widgets_collection.pdfReader.pdfReader as imw

import UI.widgets_manager as wm
import file_system.file_system_facade as fsf
import _utils._utils_main as _u


class LayoutManagers:
    class PdfReadersLayout(wm.MenuLayout_Interface):
        prefix = "_PdfReadersLayout_"

        def __init__(self, winRoot:imw.PdfReadersRoot):
            winRoot.pfdReader_BOX = imw.PfdReader_BOX(winRoot, 
                                                   self.prefix,
                                                   width = winRoot.width,
                                                   height = winRoot.height - 45)
            winRoot.widgets.append(winRoot.pfdReader_BOX)
            winRoot.resizePdfReaderWindow_BTN = imw.ResizePdfReaderWindow_BTN(winRoot, self.prefix)
            winRoot.widgets.append(winRoot.resizePdfReaderWindow_BTN)
            winRoot.changePagePdfReaderWindow_ETR = imw.ChangePagePdfReaderWindow_ETR(winRoot, self.prefix)
            winRoot.widgets.append(winRoot.changePagePdfReaderWindow_ETR)

            winRoot.resizePdfReaderWindow_BTN.addListenerWidget(winRoot.pfdReader_BOX)
            winRoot.changePagePdfReaderWindow_ETR.addListenerWidget(winRoot.pfdReader_BOX)

        def show(self, winRoot:imw.PdfReadersRoot):
            winRoot.pfdReader_BOX.subsection = winRoot.subsection
            winRoot.pfdReader_BOX.imIdx = winRoot.imIdx
            winRoot.pfdReader_BOX.eImIdx = winRoot.extraImIdx
            winRoot.pfdReader_BOX.selectingZone = winRoot.selector
            winRoot.pfdReader_BOX.getTextOfSelector = winRoot.getTextOfSelector

            if winRoot.currPage != None:
                winRoot.changePagePdfReaderWindow_ETR.changePage(None, winRoot.currPage)
                winRoot.pfdReader_BOX.changePage(winRoot.currPage)

                winRoot.currPage = None

            winRoot.resizePdfReaderWindow_BTN.subsection = winRoot.subsection
            winRoot.resizePdfReaderWindow_BTN.imIdx = winRoot.imIdx
            winRoot.changePagePdfReaderWindow_ETR.subsection = winRoot.subsection
            winRoot.changePagePdfReaderWindow_ETR.imIdx = winRoot.imIdx

            for w in winRoot.widgets:
                w.render()

        def hide(self, winRoot:imw.PdfReadersRoot):
            winRoot.pfdReader_BOX.changePrevPos = winRoot.changePrevPos
            for w in winRoot.widgets:
                w.hide()
    
        def saveFigures(self, winRoot:imw.PdfReadersRoot):
            winRoot.pfdReader_BOX.saveFigures()
            
        def forceUpdate(self, winRoot:imw.PdfReadersRoot):
            winRoot.pfdReader_BOX.render(force = True)

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class PdfReadersManager(wm.MenuManager_Interface):
    shown = False

    def __init__(self, topFrame):
        self.topFrame = topFrame
        rootWidget = topFrame.contentFrame

        dimensions = _u.getMonitorsAreas()[0]
        width = dimensions[2] # 1500
        height = dimensions[3] - 50 # 850

        halfWidth = int(width / 2)

        width = halfWidth
        height = height - 105

        topFrame.width = width
        topFrame.height = height

        topFrame.setGeometry(width, height)

        winRoot = imw.PdfReadersRoot(rootWidget, 
                                     width = topFrame.width, 
                                     height = topFrame.height,
                                     topLevelFrameId = topFrame.prefix)
        layouts = []
        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))

        winRoot.subsection = fsf.Data.Book.currSection
        
        currLayout = None
        super().__init__(winRoot,
                        layouts,
                        currLayout)

    def forceUpdate(self):
        self.layouts[0].forceUpdate(self.winRoot)
    
    def saveFigures(self):
        self.layouts[0].saveFigures(self.winRoot)

    def unbind(self):
        self.winRoot.unbindAll()

    def removeLabel(self, subsection, imIdx, eImIdx):
        self.winRoot.pfdReader_BOX.removeMainLabel(subsection, imIdx, eImIdx)

    def show(self, appDimensions = None, extraImIdx = None,
             subsection = None, imIdx = None, page = None, selector = False,
             changePrevPos = True, removePrevLabel = False, getTextOfSelector = False,
             withoutRender = False):
        self.winRoot.pageLbl = self.winRoot.changePagePdfReaderWindow_ETR
        self.winRoot.pdfBox = self.winRoot.pfdReader_BOX

        if removePrevLabel:
            self.winRoot.pfdReader_BOX.removeMainLabel(subsection, imIdx, extraImIdx)

        if not withoutRender:
            self.hide(changePrevPos = changePrevPos)
        else:
            self.winRoot.pfdReader_BOX.getIntoSelectingMode(subsection, imIdx, extraImIdx, 
                                                               getTextOfSelector)

        self.shown = True
        self.winRoot.subsection = self.winRoot.subsection if subsection == None else subsection
        self.winRoot.imIdx = self.winRoot.imIdx if imIdx == None else imIdx
        self.winRoot.selector = selector
        self.winRoot.extraImIdx = extraImIdx
        self.winRoot.getTextOfSelector = getTextOfSelector

        if page != None:
            origMatName = fsf.Data.Book.currOrigMatName
            fsf.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(origMatName, int(page))
            self.winRoot.currPage = page
        # self.layouts[0].appDimensions = appDimensions
        if not withoutRender:
            self.layouts[0].show(self.winRoot)
            return super().show()

    def updateOMpage(self):
        self.winRoot.pfdReader_BOX.updateOMpage()

    def hide(self, changePrevPos = False):
        self.winRoot.changePrevPos = changePrevPos
        self.shown = False
        self.winRoot.currPage = None
        super().hide()
        self.layouts[0].hide(self.winRoot)

    def reduceHeight(self, delta):
        pdfBox = self.winRoot.pfdReader_BOX
        pdfBox.setCanvasHeight(pdfBox.height - delta)    
        self.topFrame.setGeometry(self.topFrame.width, self.topFrame.height - delta)    

    def moveToEntry(self, subsection, imIdx, eImIdx, forcePageChange = False):
        if eImIdx == None:
            currPage = int(fsf.Data.Sec.imLinkOMPageDict(subsection)[imIdx])
        else:
            currPage = int(fsf.Data.Sec.imLinkOMPageDict(subsection)[imIdx + "_" + str(eImIdx)])

        if forcePageChange:
            self.winRoot.changePagePdfReaderWindow_ETR.changePage(None, currPage)

        self.winRoot.currPage = currPage
        self.winRoot.selector = False
        self.winRoot.pfdReader_BOX.changePage(currPage)
        self.winRoot.pfdReader_BOX.getIntoDrawingMode()

        if int(currPage) not in self.winRoot.pfdReader_BOX.getShownPagesList():
            self.layouts[0].show(self.winRoot)
        
        self.winRoot.pfdReader_BOX.moveToEntryWidget(subsection, imIdx, eImIdx)
