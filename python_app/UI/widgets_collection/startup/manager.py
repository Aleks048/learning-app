import os
import tkinter as tk
import threading

import UI.widgets_collection_old as wc
import UI.widgets_utils as wu
import UI.widgets_vars as wv
import UI.widgets_messages as wmes

import layouts.layouts_manager as lm

import file_system.file_system_manager as fsm

import _utils.logging as log
import _utils._utils_main as _u

import UI.widgets_collection.startup.startup as sw

import UI.widgets_manager as wm

class StartupLayout(wm.MenuLayout_Interface):
    prefix = "_StartupLayout_"

    def __init__(self, winRoot):
        winRoot.setGeometry(posx = int(self.monitorSize[0] / 2),
                            posy = int(self.monitorSize[1] / 2))
        
        books_OM = sw.ChooseStartupBook_OM(winRoot, self.prefix)
        self.addWidget(books_OM)

        confirm_BTN = sw.StartupConfirm_BTN(winRoot, self.prefix)
        self.addWidget(confirm_BTN)
        
        bookName_ETR = sw.StrtupBookName_ETR(winRoot, self.prefix)
        self.addWidget(bookName_ETR)
        bookLocation_ETR = sw.StrtupBookLocation_ETR(winRoot, self.prefix)
        self.addWidget(bookLocation_ETR)
        originalMaterialName_ETR = sw.StrtupOriginalMaterialName_ETR(winRoot, self.prefix)
        self.addWidget(originalMaterialName_ETR)
        originalMaterialLocation_ETR = sw.StrtupOriginalMaterialLocation_ETR(winRoot, self.prefix)
        self.addWidget(originalMaterialLocation_ETR)

        addbook_BTN = sw.AddBook_BTN(winRoot, self.prefix, None)
        addbook_BTN.addListenerWidget(books_OM)
        self.addWidget(addbook_BTN)

        # super().__init__(winRoot)

class StartupMenuManager(wm.MenuManager_Interface):
    prefix = "_StartupMenu_"
    monitorSize = _u.getMonitorSize()
    
    @classmethod
    def createMenu(cls):
        cls.winRoot = sw.StartupRoot(0, 0)
        startupLayout = StartupLayout(cls.winRoot)
        cls.layouts.append(startupLayout)
        cls.currLayout = startupLayout
        
        # run the tk
        # winRoot.mainloop()
        super().createMenu()

    @classmethod
    def _bindKeys(cls):
        cls.winRoot.bind("<Escape>", lambda e: cls.winRoot.destroy())
        cls.winRoot.bind("<Return>", lambda e: cls.winRoot.destroy())