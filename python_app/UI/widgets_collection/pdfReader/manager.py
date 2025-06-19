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
        topFrame = topFrame
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

        self.winRoots = [None]

        super().__init__(rootWidget = None,
                        layouts = [],
                        currLayout = None)

        self.__addTopFrame(topFrame, rootWidget, 0)

        extraHatWidget = self.produceTopFrameHatExtraWidgets(topFrame.hatFrame.viewHatFrames[-1])
        extraHatWidget.render()

    def onTopSizeChange(self, width, height):
        self.winRoot.pdfBox.setCanvasHeight(height - 50)

    def onAddViewer(self, topFrame, rootWidget, row):
        self.winRoot.hide()
        self.winRoots.append(None)

        self.__addTopFrame(topFrame, rootWidget, row)
        self.show()
    
    def onViewerChange(self, idx, bookName = None):
        origMatName = fsf.Data.Book.currOrigMatName

        origMatCurrPage = fsf.Wr.OriginalMaterialStructure.getMaterialCurrPage(origMatName)      
        fsf.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(origMatName, origMatCurrPage)

        self.winRoot.hide()        
        self.winRoot = self.winRoots[idx]
        if bookName != None:
            self.winRoot.book = bookName

        fsf.Data.Book.currOrigMatName = self.winRoot.book

        if bookName != None:
            self.winRoot.destroy()

        self.rerender()

        self.winRoot.topFrame.changeHatViewerSelectorColor(idx)

        if bookName != None:
            self.winRoot.topFrame.contentFrame.setGeometry(self.winRoot.topFrame.width, 
                                                           self.winRoot.topFrame.height - 20)

    def produceTopFrameHatExtraWidgets(self, rootWidget):
        return imw.ChooseOriginalMaterial_OM(rootWidget, rootWidget.prefix)

    def rerender(self):
        row = self.winRoot.row
        topFrame = self.winRoot.topFrame
        rootWidget = self.winRoot.rootWidget

        self.__addTopFrame(topFrame, rootWidget, row)

        self.show()
        self.onTopSizeChange(None, topFrame.height - 30)

    def __addTopFrame(self, topFrame, rootWidget, row, bookName = None):
        if self not in topFrame.contentFrame.sizeChangeReactors:
            topFrame.contentFrame.sizeChangeReactors.append(self)

        winRoot = imw.PdfReadersRoot(rootWidget, 
                                     width = topFrame.width, 
                                     height = topFrame.height,
                                     topFrame = topFrame,
                                     row = row)
        
        if bookName != None:
            winRoot.book = bookName

        layouts = []
        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))

        self.winRoots[row] = winRoot

        winRoot.subsection = fsf.Data.Book.currSection

        self.winRoot = winRoot
        self.layouts.extend(layouts)

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
        self.winRoot.topFrame.setGeometry(self.winRoot.topFrame.width, self.winRoot.topFrame.height - delta)    

    def moveToEntry(self, subsection, imIdx, eImIdx, forcePageChange = False):
        bookName = fsf.Data.Sec.origMatNameDict(subsection)[imIdx]

        foundBook = False

        if bookName != self.winRoot.book:
            for i in range(len(self.winRoots)):
                if self.winRoot.book == bookName:
                    self.onViewerChange(i)
                    foundBook = True
                    break
        else:
            foundBook = True
        
        if not foundBook:
            self.onViewerChange(len(self.winRoots) - 1, bookName)

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
