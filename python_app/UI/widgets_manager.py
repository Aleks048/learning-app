import data.constants as dc
import data.temp as dt

import UI.widgets_facade as wf

menuManagers = []

class MenuLayout_Interface(dc.AppCurrDataAccessToken):
    name = None
    def __init__(self, winRoot, appDimensions):
        self.widgets = []
        self.appDimensions = []
        self.winRoot = winRoot
        self.appDimensions = appDimensions
        self.setAppDimensions()        

    def addWidget(self, widget):
        self.widgets.append(widget)
    
    def setAppDimensions(self):
        self.winRoot.setGeometry(*self.appDimensions)

    def show(self):
        self.setAppDimensions()
        for w in self.widgets:
            w.render()
    
    def hide(self):
        for w in self.widgets:
            w.hide()


class MenuManager_Interface(dc.AppCurrDataAccessToken):
    currLayout:MenuLayout_Interface
    
    def __init__(self, rootWidget, layouts, currLayout):
        super().__init__()

        self.winRoot = rootWidget
        self.layouts = layouts
        self.currLayout = currLayout

        #add manager to the list of all managers
        UIManagers = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken)
        UIManagers.append(self)
        dt.AppState.UIManagers.setData(self.appCurrDataAccessToken, UIManagers)

    def switchUILayout(self, toLayoutType):
        self.hideAllWidgets()
        self.winRoot.render()
        for layout in self.layouts:
            if type(layout) == toLayoutType:
                self.currLayout = layout
                layout.show()
                return
        raise KeyError

    def startMainLoop(self):
        self.winRoot.startMainLoop()

    def stopMainLoop(self):
        self.winRoot.stopMainLoop()

    def show(self):
        self.winRoot.render()
        self.winRoot.widgetObj.focus_force()
        self.currLayout.show()
    
    def showOnly(self):
        self.hideAllWidgets()
        self.show()
    
    def hide(self):
        self.winRoot.hide()
        for l in self.layouts:
            l.hide()

    def hideAllWidgets(self):
        '''
        hide all widgets. clear all entries
        '''
        UIManagers = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken)
        for UIManager in UIManagers:
            UIManager.hide()

    def startManager(self):
        self.show()


class UI_generalManager(dc.AppCurrDataAccessToken):
    @classmethod
    def showNotification(cls, msg, shouldWait):
        messsageMenuManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken, 
                                                    wf.Wr.MenuManagers.MessageMenuManager)
        
        if shouldWait:
            response = messsageMenuManager.show(msg, shouldWait)
            return response
        else:
            messsageMenuManager.show(msg, shouldWait)
