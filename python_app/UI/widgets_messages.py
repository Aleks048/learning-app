from tkinter import messagebox
import tkinter as tk
from threading import Thread


class MessageMenu:
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

        l1=tk.Label(cls.winRoot, image="::tk::icons::question")
        l2=tk.Label(cls.winRoot,text= text)

        b1=tk.Button(cls.winRoot,text="Yes",command = lambda: onYesCallback(), width = 10)
        b2=tk.Button(cls.winRoot,text="No",command= lambda: cls.winRoot.destroy(),width = 10)


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

