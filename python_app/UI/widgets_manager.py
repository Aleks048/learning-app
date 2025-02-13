import data.constants as dc
import data.temp as dt

import UI.widgets_facade as wf

menuManagers = []

class MenuLayout_Interface(dc.AppCurrDataAccessToken):
    name = None
    def __init__(self, winRoot, appDimensions):
        self.widgets = set()
        self.appDimensions = []
        self.winRoot = winRoot
        self.appDimensions = appDimensions
        self.setAppDimensions()        

    def addWidget(self, widget):
        self.widgets.add(widget)
    
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
    __isShown = False

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
        self.hideAllWidgets(changePdfWidget = False)
        self.winRoot.render(changePdfReader = False)

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
        self.winRoot.forceFocus()
        self.currLayout.show()
        self.__isShown = True
    
    def showOnly(self):
        self.hideAllWidgets()
        self.show()
    
    def hide(self):
        self.winRoot.hide()

        for l in self.layouts:
            l.hide()

        self.__isShown = False

    def hideAllWidgets(self, changePdfWidget = True):
        '''
        hide all widgets. clear all entries
        '''
        
        UIManagers = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken)
        for UIManager in UIManagers:
            if not((not changePdfWidget) and ("pdfreadersmanage" in str(type(UIManager)).lower())):
                UIManager.hide()

    def startManager(self):
        self.show()

    def isShown(self):
        return self.__isShown


class UI_generalManager(dc.AppCurrDataAccessToken):
    @classmethod
    def showNotification(cls, msg, shouldWait):
        # allManagers = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken)
        # managersShown = [i for i in allManagers if i.isShown()]

        messsageMenuManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken, 
                                                    wf.Wr.MenuManagers.MessageMenuManager)
        
        response = None

        if shouldWait:
            response = messsageMenuManager.show(msg, shouldWait)
        else:
            messsageMenuManager.show(msg, shouldWait)

        # for m in managersShown:
        #     m.show()

        return response