import UI.widgets_collection.startup.startup as sw

import UI.widgets_manager as wm

import data.constants as dc

class StartupLayout(wm.MenuLayout_Interface):
    prefix = "_StartupLayout_"

    def __init__(self, winRoot):
        monitorSize = dc.MonitorSize.getData()
        appDimensions = [-1, -1, int(monitorSize[0] / 2), int(monitorSize[1] / 2)]
        super().__init__(winRoot, appDimensions)

        winRoot.setGeometry(*self.appDimensions)
        
        books_OM = sw.ChooseStartupBook_OM(winRoot, self.prefix)
        self.addWidget(books_OM)

        confirm_BTN = sw.StartupConfirm_BTN(winRoot, self.prefix)
        self.addWidget(confirm_BTN)
        
        bookName_ETR = sw.StrtupBookName_ETR(winRoot, self.prefix)
        self.addWidget(bookName_ETR)
        bookLocation_ETR = sw.StrtupBookLocation_ETR(winRoot, self.prefix)
        self.addWidget(bookLocation_ETR)
        originalMaterialRelPath_ETR = sw.StrtupOriginalMaterialRelPath_ETR(winRoot, self.prefix)
        self.addWidget(originalMaterialRelPath_ETR)
        originalMaterialName_ETR = sw.StrtupOriginalMaterialName_ETR(winRoot, self.prefix)
        self.addWidget(originalMaterialName_ETR)
        originalMaterialLocation_ETR = sw.StrtupOriginalMaterialLocation_ETR(winRoot, self.prefix)
        self.addWidget(originalMaterialLocation_ETR)

        addbook_BTN = sw.AddBook_BTN(winRoot, self.prefix)
        addbook_BTN.addListenerWidget(books_OM)
        addbook_BTN.addListenerWidget(bookName_ETR)
        addbook_BTN.addListenerWidget(bookLocation_ETR)
        addbook_BTN.addListenerWidget(originalMaterialRelPath_ETR)
        addbook_BTN.addListenerWidget(originalMaterialName_ETR)
        addbook_BTN.addListenerWidget(originalMaterialLocation_ETR)
        self.addWidget(addbook_BTN)


class StartupMenuManager(wm.MenuManager_Interface):
    def __init__(self):
        winRoot = sw.StartupRoot(0, 0)
        startupLayout = StartupLayout(winRoot)
        super().__init__(winRoot,
                        [startupLayout],
                        startupLayout)
