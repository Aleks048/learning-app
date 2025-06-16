import UI.widgets_manager as wm
import UI.widgets_collection.mainTOC.mainTOC as ml
import UI.widgets_data as wd

import file_system.file_system_facade as fsf
import _utils._utils_main as _u


class LayoutManagers:
    class _MainTOC(wm.MenuLayout_Interface):
        prefix = "_MainTOC"
        tocBox = None

        addEntryETR = None

        def __init__(self, topFrame):
            self.topFrame = topFrame

            rootWidget = self.topFrame.contentFrame

            #
            # pre init
            #

            #
            # init
            #

            super().__init__(rootWidget, None)

            tocBox_BOX = ml.MainTOCBox(rootWidget, self.prefix, 
                                       windth =  self.topFrame.width - 20, #TODO: why we need this border
                                       height =  self.topFrame.height)
            self.addWidget(tocBox_BOX)
            self.tocBox = tocBox_BOX

        def changeEntryBoxMaxHeight(self, newHeight):
            if type(newHeight) == int:
                self.tocBox.maxHeight = self.tocBox.originalHeight - newHeight
                self.tocBox.setCanvasHeight(self.tocBox.maxHeight)
            else:
                # The case of no main entry
                self.tocBox.maxHeight = self.tocBox.originalHeight #??+ self.entryWindow_BOX.origHeight
                self.tocBox.setCanvasHeight(self.tocBox.maxHeight)


            self.topFrame.height = self.tocBox.maxHeight
            self.topFrame.setGeometry(self.topFrame.width, self.topFrame.height)
        
        def show(self):
            self.tocBox.widgetToScrollTo = None
            return super().show()

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class MainTOCManager(wm.MenuManager_Interface):
    def __init__(self, rootWidget):
        dimensions = _u.getMonitorsAreas()[0]
        width = dimensions[2] # 1500

        halfWidth = int(width / 2)

        width = halfWidth
        height = 780
        rootWidget.width = width
        rootWidget.height = height
        rootWidget.setGeometry(width, height)

        self.layouts = []
        self.isShown = False

        self.winRoot = rootWidget

        layouts = self.layouts

        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(rootWidget))
        
        currLayout = None
        for layout in layouts:
            if type(layout) == LayoutManagers._MainTOC:
                currLayout = layout
                break
        
        super().__init__(self.winRoot,
                        layouts,
                        currLayout)
    
    def scrollToCurrSubsecrtionWidget(self):
        for layout in self.layouts:
            if type(layout) == LayoutManagers._MainTOC:
                layout.tocBox.scrollToCurrSubsecrtionWidget()

    def changeLowerSubframeHeight(self, newHeight = None):
        for layout in self.layouts:
            if type(layout) == LayoutManagers._MainTOC:
                if newHeight == None:
                    layout.changeEntryBoxMaxHeight(wd.Data.MainEntryLayout.currSize)
                else:
                    layout.changeEntryBoxMaxHeight(newHeight)

    def addEntry(self, subsection, imIdx):
        fsf.Data.Book.subsectionOpenInTOC_UI = subsection
        fsf.Data.Book.currSection = subsection
        fsf.Data.Book.currTopSection = subsection.split(".")[0]
        fsf.Data.Book.entryImOpenInTOC_UI = imIdx

        for layout in self.layouts:
            if type(layout) == LayoutManagers._MainTOC:
                layout.tocBox.AddEntryWidget(imIdx, 
                                    subsection, 
                                    layout.tocBox.subsectionWidgetManagers[subsection].entriesFrame)

        for w in wd.Data.Reactors.entryChangeReactors.values():
            if "onFullEntryMove" in dir(w):
                w.onFullEntryMove()

    # def renderTocWidget(self):
    #     for layout in self.layouts:
    #         if type(layout) == LayoutManagers._Main:
    #             layout.tocBox.render()
    #             return


    def moveTocToEntry(self, subsection, imIdx, fromTOCWindow = False):
        for layout in self.layouts:
            if type(layout) == LayoutManagers._MainTOC:
                fsf.Data.Book.currTopSection = subsection.split(".")[0]
                fsf.Data.Book.subsectionOpenInTOC_UI = subsection

                layout.tocBox.renderFromTOCWindow = fromTOCWindow
                layout.tocBox.scrollToEntry(subsection, imIdx)
                layout.tocBox.renderFromTOCWindow = False
                return

    # def addTOCListener(self, widget):
    #     for layout in self.layouts:
    #         if type(layout) == LayoutManagers._MainTOC:
    #             widget.addListenerWidget(layout.tocBox)
    #             return

    def moveTocToCurrEntry(self):
        for layout in self.layouts:
            if type(layout) == LayoutManagers._MainTOC:
                layout.tocBox.render(shouldScroll = True)
                return

    # def scrollTocToEntry(self, subsection, imIdx):
    #     for layout in self.layouts:
    #         if type(layout) == LayoutManagers._MainTOC:
    #             layout.tocBox.scrollToEntry(subsection, imIdx)
    #             return

    def renderWithoutScroll(self):
        for layout in self.layouts:
            if type(layout) == LayoutManagers._MainTOC:
                layout.tocBox.render(shouldScroll = False)
                return

    def scrollToLatestClickedWidget(self, refreshImage = False, addBrownBorder = False):
        for layout in self.layouts:
            if type(layout) == LayoutManagers._MainTOC:
                if layout.tocBox.widgetToScrollTo != None:
                    layout.tocBox.scrollIntoView(None, layout.tocBox.widgetToScrollTo)
                    try:
                        layout.tocBox.widgetToScrollTo.readFigures()
                        if refreshImage or addBrownBorder:
                            layout.tocBox.widgetToScrollTo.refreshImage(addBrownBorder)
                    except:
                        pass
                return

    # def scrollToWidget(self, event, widget):
    #     for layout in self.layouts:
    #         if type(layout) == LayoutManagers._MainTOC:
    #             if layout.tocBox.widgetToScrollTo != None:
    #                 layout.tocBox.scrollIntoView(event, widget)

    # def showLinksForEntry(self, subsection, imIdx):
    #     for layout in self.layouts:
    #         if type(layout) == LayoutManagers._MainTOC:
    #             layout.tocBox.showLinksForSubsections = []
    #             layout.tocBox.showLinksForEntryCmd(None, subsection, imIdx)
    #             return