import UI.widgets_collection.startup.startup as sw

import UI.widgets_manager as wm

import UI.widgets_collection.message.message as mw


import _utils.logging as log


# class ConfirmationMenu:

#     @classmethod
#     def createMenu(cls, text, onYesFunc, *args):
#         cls.winRoot = tk.Tk()
        
#         def onYesCallback():
#             cls.winRoot.destroy()
#             Thread(target=lambda: onYesFunc(*args)).start()

#         cls.onYesCallBack = onYesCallback

#         cls.winRoot.title("Confirmation")

#         l1=tk.Label(cls.winRoot, image="::tk::icons::question")
#         l2=tk.Label(cls.winRoot,text= text)

#         b1=tk.Button(cls.winRoot,text="Yes",command = lambda: onYesCallback(), width = 10)
#         b2=tk.Button(cls.winRoot,text="No",command= lambda: cls.winRoot.destroy(),width = 10)


#         # layout
#         l1.grid(row=0, column=0, pady=(7, 0), padx=(10, 30), sticky="e")
#         l2.grid(row=0, column=1, columnspan=3, pady=(7, 10), sticky="w")

#         b1.grid(row=1, column=1, padx=(2, 35), sticky="e")
#         b2.grid(row=1, column=2, padx=(2, 35), sticky="e")

#         cls._bindKeys()

#         cls.winRoot.mainloop()

    
#     @classmethod
#     def _bindKeys(cls):
#         def onYesCallbackWrapper(e):
#             cls.onYesCallBack()
#         cls.winRoot.bind("<Return>", onYesCallbackWrapper)
#         cls.winRoot.bind("<Escape>", lambda e: cls.winRoot.destroy())

class LayoutManagers:
    class PlainMessageLayout(wm.MenuLayout_Interface):
        prefix = "_MessageLayout_"

        def __init__(self, winRoot):
            appDimensions = [200, 50, 700, 350]
            super().__init__(winRoot, appDimensions)

            message_LBL = mw.Message_LBL(winRoot, self.prefix)
            self.addWidget(message_LBL)

            winRoot.setGeometry(*self.appDimensions)
        
        def setProps(self,  msg = "", cmd = lambda _: None):
            for w in self.widgets:
                if w.__class__ ==  mw.Message_LBL:
                    w.changeText(msg)


    class ConfirmationMessageLayout(wm.MenuLayout_Interface):
        prefix = "_ConfirmationMessageLayout_"

        def __init__(self, winRoot):
            appDimensions = [50, 20, 700, 700]
            super().__init__(winRoot, appDimensions)

            message_LBL = mw.Message_LBL(winRoot, self.prefix)

            winRoot.setGeometry(*self.appDimensions)  
   

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class MessageMenuManager(wm.MenuManager_Interface):
    def __init__(self):
        winRoot = sw.StartupRoot(100, 100)
        layouts = []
        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))
            
        currLayout = None
        for layout in layouts:
            if type(layout) == LayoutManagers.PlainMessageLayout:
                currLayout = layout
                break
        
        super().__init__(winRoot,
                        layouts,
                        currLayout)
    
    def show(self, text):
        self.currLayout.setProps(text)
        return super().show()
    
    def showOnly(self, text):
        self.hideAllWidgets()
        return self.show(text)
    
    def hide(self):
        return super().hide()
        