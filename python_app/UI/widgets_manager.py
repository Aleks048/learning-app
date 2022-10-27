import os
import tkinter as tk
from tkinter import messagebox
from threading import Thread

import UI.widgets_collection as wc
import _utils._utils_main as _u
import UI.widgets_vars as wv

class StartupMenu:
    prefix = "_" + __name__

    monitorSize = _u.getMonitorSize()
    
    @classmethod
    def createMenu(cls):
        def _confirmationButtonCallback():
            # TODO:start the main layout for the chosen book

            cls.winRoot.destroy()

        cls.winRoot = tk.Tk()

        cls.winRoot.geometry("+" + str(int(cls.monitorSize[0] / 2)) \
                    + "+" \
                    + str(int(cls.monitorSize[1] / 2)))


        # get chooseBookOptionMenu
        books_OM = wc.ChooseBookSection.getOptionsMenu_ChooseBook(cls.winRoot)
        books_OM.pack()

        # get confirmation button
        confirm_BTN = tk.Button(cls.winRoot,
                                name = "_startupConfirmBTN",
                                text= "start", 
                                command = _confirmationButtonCallback)
        
        confirm_BTN.pack()
        
        # assign the keys
        cls._bindKeys()
        
        # run the tk
        cls.winRoot.mainloop()

    @classmethod
    def _bindKeys(cls):
        cls.winRoot.bind("<Escape>", lambda e: cls.winRoot.destroy())
        # cls.winRoot.bind("<Return>", lambda e: cls.winRoot.destroy())


class LayoutsMenus:
    def ChaptersLayoutUI(winMainRoot):
        wv.UItkVariables.needRebuild = tk.BooleanVar()

        layoutOM = wc.Layout.getOptionsMenu_Layouts(winMainRoot, cls.__name__)
        layoutOM.grid(column=0, row=0, padx=0, pady=0)
        layoutOM.update()
        
        showProofsBTN = wc.getShowProofs_BTN(winMainRoot, cls.__name__)
        showProofsBTN.grid(column=1, row=0, padx=0, pady=0)

        dummyEntry = tk.Entry(winMainRoot, text = "Dummy", name = cls.__name__.lower() + "_dummyFocusEntry")
        dummyEntry.grid(column=2, row=0, padx=0, pady=0)
        dummyEntry.focus_set()

        saveImageBTN = wc.getSaveImage_BTN(winMainRoot, cls.__name__)
        saveImageBTN.grid(column=3, row=0, padx=0, pady=0)

        createGlLinkBTN, createGlLinkETR = wc.getGlobalLinksAdd_Widgets(winMainRoot, cls.__name__)
        createGlLinkETR.grid(column=4, row=0, padx=0, pady=0)
        createGlLinkBTN.grid(column=5, row=0, padx=0, pady=0)


        mon_width, _ = _u.getMonitorSize()
        cls.pyAppDimensions[0] = int(mon_width / 2)
        cls.pyAppDimensions[1] = layoutOM.winfo_height() + 5
    
    def mainLayoutUI(winMainRoot):
        mon_width, _ = _u.getMonitorSize()
        cls.pyAppDimensions = [int(mon_width / 2), 90]

        chooseBookOM = wc.ChooseBookSection.getOptionsMenu_ChooseBook(winMainRoot, cls.__name__)
        chooseBookOM.grid(column = 0, row = 0, padx = 0, pady = 0)

        layoutOM = wc.Layout.getOptionsMenu_Layouts(winMainRoot, cls.__name__)
        layoutOM.grid(column = 0, row = 1, padx = 0, pady = 0)

        imageGenerationUI = wc.getTextEntryButton_imageGeneration(winMainRoot, cls.__name__)
        imageGenerationUI[0].grid(column = 1, row = 0, padx = 0, pady = 0, sticky = tk.N)
        imageGenerationUI[1].grid(column = 1, row = 1, padx = 0, pady = 0, sticky = tk.N)

        addExtraImage = ui.UIWidgets.getAddImage_BTN(winMainRoot, cls.__name__)
        addExtraImage.grid(column = 1, row = 0, padx = 0, pady = 0, sticky = tk.E)

        imageGenerationRestartBTN = ui.UIWidgets.getImageGenerationRestart_BTN(winMainRoot, cls.__name__)
        imageGenerationRestartBTN.grid(column = 1, row = 0, padx = 0, pady = 0, sticky = tk.W)

        TOCcreate_CB, TOCWithImage_CB = ui.UIWidgets.getCheckboxes_TOC(winMainRoot, cls.__name__)
        TOCcreate_CB.grid(column = 1, row = 1, padx = 0, pady = 0, sticky = tk.W)
        TOCWithImage_CB.grid(column = 1, row = 1, padx = 0, pady = 0, sticky = tk.E)
        
        currScrShotDirText = ui.UIWidgets.Screenshot.getText_CurrentScreenshotDir(winMainRoot, cls.__name__)
        currScrShotDirText.grid(columnspan = 2,row = 2)

        chooseChapterOptionMenu = ui.UIWidgets.ChooseBookChapter.getOptionMenu_ChooseChapter(winMainRoot, cls.__name__)
        chooseChapterOptionMenu.grid(column = 2, row = 0, padx = 0, pady = 0)

        chooseChapterMenusAndbackBtn = ui.ChaptersUI.getButton_chooseChaptersMenusAndBack(winMainRoot, cls.__name__)
        chooseChapterMenusAndbackBtn.grid(column = 3, row = 0, padx = 0, pady = 0)

        chooseSubChapterMenu = ui.UIWidgets.ChooseBookChapter.getOptionMenu_ChooseSubchapter(winMainRoot, cls.__name__)
        chooseSubChapterMenu.grid(column = 3, row = 2, padx = 0, pady = 0)