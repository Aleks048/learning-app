import os
import tkinter as tk
from tkinter import messagebox
from threading import Thread

import UI.widgets_collection as wc
import UI.widgets_utils as wu
import UI.widgets_vars as wv
import UI.widgets_messages as wmes
import _utils._utils_main as _u

class Data:
    UItkVariables = wv.UItkVariables

class Wrappers:
    class ConfirmationMenu(wmes.ConfirmationMenu):
        pass
    
    class MessageMenu(wmes.MessageMenu):
        pass

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
        books_OM = wc.ChooseMaterial.getOptionsMenu_ChooseBook(cls.winRoot)
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
        cls.winRoot.bind("<Return>", lambda e: cls.winRoot.destroy())


class MainMenu:

    @classmethod
    def createMenu(cls):
        winRoot = tk.Tk()

        wc.LayoutsMenus.SectionLayoutUI.addWidgets(winRoot)
        wu.hideAllWidgets(winRoot)
        wc.LayoutsMenus.MainLayoutUI.addWidgets(winRoot)

        winRoot.mainloop()