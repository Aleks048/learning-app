import time
from threading import Thread

import UI.widgets_collection.startup.startup as sw
import UI.widgets_wrappers as ww

import UI.widgets_manager as wm

import UI.widgets_collection.message.message as mw


import _utils.logging as log

import data.constants as dc
import data.temp as dt


class LayoutManagers:
    class PlainMessageLayout(wm.MenuLayout_Interface):
        prefix = "_PlainMessageLayout_"

        def __init__(self, winRoot):
            appDimensions = [800, 50, 500, 350]
            super().__init__(winRoot, appDimensions)

            message_LBL = mw.Message_LBL(winRoot, self.prefix)
            self.addWidget(message_LBL)

            winRoot.setGeometry(*self.appDimensions)
        
        def setProps(self,  msg = ""):
            for w in self.widgets:
                if w.__class__ ==  mw.Message_LBL:
                    w.changeText(msg)


    class ConfirmationMessageLayout(wm.MenuLayout_Interface):
        prefix = "_ConfirmationMessageLayout_"

        def __init__(self, winRoot):
            appDimensions = [800, 300, 400, 350]
            super().__init__(winRoot, appDimensions)

            message_LBL = mw.Message_LBL(winRoot, self.prefix)
            self.addWidget(message_LBL)

            confirm_BTN = mw.Confirm_BTN(winRoot, self.prefix)
            self.addWidget(confirm_BTN)

            decline_BTN = mw.Decline_BTN(winRoot, self.prefix)
            self.addWidget(decline_BTN)

            winRoot.setGeometry(*self.appDimensions)
        
        def setProps(self,  msg = ""):
            for w in self.widgets:
                if w.__class__ ==  mw.Message_LBL:
                    w.changeText(msg)
   

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
        winRoot = mw.MessageRoot(600, 600)
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

        def confirm(*args):
            self.stopWait(True)
            self.hide()
        def decline(*args):
            self.stopWait(False)
            self.hide()
        self.winRoot.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.enter,  confirm)
        self.winRoot.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.escape,  decline)
    
    def show(self, text, shouldWait = False):
        if shouldWait:
            self.switchUILayout(LayoutManagers.ConfirmationMessageLayout)
        else:
            self.switchUILayout(LayoutManagers.PlainMessageLayout)
         
        self.currLayout.setProps(text)
        super().show()

        if shouldWait:
            self.wait()

            return self.winRoot.getData()
    
    def wait(self):
        self.winRoot.wait()

    def stopWait(self, response):
        self.winRoot.stopWait(response)
    
    def showOnly(self, text, cmd = lambda *args: None):
        self.hideAllWidgets()

        return self.show(text, cmd)
    
    def hide(self):
        return super().hide()
        