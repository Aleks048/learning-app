import UI.widgets_manager as wm
import UI.widgets_collection.mainEntry.mainEntry as me
import UI.widgets_data as wd

import _utils._utils_main as _u
import file_system.file_system_facade as fsf

class LayoutManagers:
    class _Main(wm.MenuLayout_Interface):
        prefix = "_mainLayout"
        tocBox = None

        addEntryETR = None

        def __init__(self, topFrame):
            #
            # pre init
            #

            self.topFrame = topFrame
            self.rootWidget = topFrame.contentFrame

            #
            # init
            #

            super().__init__(self.rootWidget, None)
    
            self.entryWindow_BOX = me.MainEntryBox(self.rootWidget, self.prefix)
            self.entryWindow_BOX.setCanvasHeight(300)
            self.addWidget(self.entryWindow_BOX)

            #
            # post init
            #
        
        def changeEntryBoxMaxHeight(self, newHeight):
            if type(newHeight) == int:
                self.entryWindow_BOX.maxHeight = self.entryWindow_BOX.origHeight + newHeight
                self.entryWindow_BOX.setCanvasHeight(self.entryWindow_BOX.maxHeight)
            else:
                # The case of no main entry
                self.entryWindow_BOX.maxHeight = 0
                self.entryWindow_BOX.setCanvasHeight(self.entryWindow_BOX.maxHeight)
            
            self.topFrame.height = self.entryWindow_BOX.maxHeight
            self.topFrame.setGeometry(self.topFrame.width, self.topFrame.height)
        
        def changeLinksSize(self):
            self.entryWindow_BOX.changeLinksSize()
        
        def show(self):
            self.entryWindow_BOX.subsection = fsf.Data.Book.subsectionOpenInTOC_UI
            self.entryWindow_BOX.imIdx = fsf.Data.Book.entryImOpenInTOC_UI
            return super().show()

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class MainEntryMenuManager(wm.MenuManager_Interface):
    def __init__(self, topFrame):
        dimensions = _u.getMonitorsAreas()[0]
        width = dimensions[2] # 1500

        halfWidth = int(width / 2)

        width = halfWidth
        height = 300
        topFrame.width = width
        topFrame.height = height
        topFrame.setGeometry(width, height)

        self.layouts = []
        self.isShown = False
    
        self.winRoot = topFrame
        layouts = self.layouts

        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(self.winRoot))
        
        currLayout = None
        for layout in layouts:
            if type(layout) == LayoutManagers._Main:
                currLayout = layout
                break
        
        super().__init__(self.winRoot,
                        layouts,
                        currLayout)
    
    def changeLowerSubframeHeight(self):
        for layout in self.layouts:
            if type(layout) == LayoutManagers._Main:
                layout.changeEntryBoxMaxHeight(wd.Data.MainEntryLayout.currSize)
    

    def changeLinksSize(self):
        for layout in self.layouts:
            if type(layout) == LayoutManagers._Main:
                layout.changeLinksSize()