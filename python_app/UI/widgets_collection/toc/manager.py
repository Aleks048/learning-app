import UI.widgets_collection.toc.toc as tocw

import UI.widgets_manager as wm

class LayoutManagers:
    class TOCLayout(wm.MenuLayout_Interface):
        prefix = "_TOCLayout_"

        def __init__(self, winRoot):
            appDimensions = [850, 720, 300, 100]
            super().__init__(winRoot, appDimensions)

            tocBox = tocw.SearchTOC_BOX(winRoot, self.prefix, 
                                  windth = 800, height = 650, 
                                  showAll = True, makeScrollable = False, 
                                  shouldScroll = False)
            tocBox.populateTOC()
            self.addWidget(tocBox)

            searchInSubsectionsText_CHB = tocw.SearchInSubsectionsText_CHB(winRoot, self.prefix)
            self.addWidget(searchInSubsectionsText_CHB)

            filter_ETR = tocw.Filter_ETR(winRoot, self.prefix)
            self.addWidget(filter_ETR)

            filter_ETR.addListenerWidget(tocBox)
            filter_ETR.addListenerWidget(searchInSubsectionsText_CHB)

            winRoot.setGeometry(*self.appDimensions)

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class TOCManager(wm.MenuManager_Interface):
    def __init__(self):
        winRoot = tocw.TOCRoot(50, 50)
        layouts = []
        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))
            
        currLayout = layouts[0]
        
        super().__init__(winRoot,
                        layouts,
                        currLayout)
        winRoot.hide()
        