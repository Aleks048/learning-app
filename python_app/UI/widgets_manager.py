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


class ShowMessageMenu:
    @classmethod
    def createMenu(cls, text):
         # Create an instance of tkinter frame or window
        cls.winRoot = tk.Tk()

        messagebox.showinfo('Processing knoledge', text)

        cls._bindKeys()
        cls.winRoot.mainloop()

    @classmethod
    def _bindKeys(cls):
        cls.winRoot.bind("<Enter>", lambda e: cls.winRoot.destroy())
        cls.winRoot.bind("<Escape>", lambda e: cls.winRoot.destroy())


class ConfirmationMenu:

    @classmethod
    def createMenu(cls, text, onYesFunc, *args):
        cls.winRoot = tk.Tk()
        
        def onYesCallback():
            cls.winRoot.destroy()
            Thread(target=lambda: onYesFunc(*args)).start()

        cls.onYesCallBack = onYesCallback

        cls.winRoot.title("Confirmation")

        l1, l2, b1, b2 = wc.addConfirmationWidgets(cls.winRoot, text, onYesCallback)

        # layout
        l1.grid(row=0, column=0, pady=(7, 0), padx=(10, 30), sticky="e")
        l2.grid(row=0, column=1, columnspan=3, pady=(7, 10), sticky="w")

        b1.grid(row=1, column=1, padx=(2, 35), sticky="e")
        b2.grid(row=1, column=2, padx=(2, 35), sticky="e")

        cls._bindKeys()

        cls.winRoot.mainloop()
    
    @classmethod
    def _bindKeys(cls):
        def onYesCallbackWrapper(e):
            cls.onYesCallBack()
        cls.winRoot.bind("<Return>", onYesCallbackWrapper)
        cls.winRoot.bind("<Escape>", lambda e: cls.winRoot.destroy())



class MainMenu:
    pass