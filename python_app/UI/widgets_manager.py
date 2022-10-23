import os
import tkinter as tk

import UI.widgets_collection as wc
import _utils._utils_main as _u


class StartupMenu:
    prefix = "_" + __name__

    monitorSize = _u.getMonitorSize()
    
    @classmethod
    def createMenu(cls):
        def _confirmationButtonCallback():
            # start the main layout for the chosen book

            cls.winRoot.destroy()

        cls.winRoot = tk.Tk()

        cls.winRoot.geometry("+" + str(int(cls.monitorSize[0] / 2)) \
                    + "+" \
                    + str(int(cls.monitorSize[1] / 2)))


        # get chooseBookOptionMenu
        books_OM = wc.getOptionsMenu_ChooseBook(cls.winRoot)
        books_OM.pack()

        # get confirmation button
        confirm_BTN = tk.Button(cls.winRoot,
                                name = "_startupConfirmBTN",
                                text= "start", 
                                command = _confirmationButtonCallback)
        
        confirm_BTN.pack()
        
        # run the tk
        cls.winRoot.mainloop()

    @classmethod
    def assignKeystrokes(cls):
        pass