import data.constants as dc
import data.temp as dt
import _utils._utils_main as _u
import _utils.logging as log

menuManagers = []

class MenuLayout_Interface(dc.AppCurrDataAccessToken):
    name = None
    widgets = []
    appDimensions = []

    name = None
    def __init__(self, winRoot, appDimensions):
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
    layouts = []
    currLayout = None
    name = None
    winRoot = None

    @classmethod
    def createMenu(cls):
        #add manager to the list of all managers
        UIManagers = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken)
        UIManagers.append(cls)

        dt.AppState.UIManagers.setData(cls.appCurrDataAccessToken, UIManagers)
    
    @classmethod
    def switchUILayout(cls, toLayout_name):
        for layout in cls.layouts:
            if layout.name == toLayout_name:
                layout.show()
                return
        raise KeyError

    @classmethod
    def startMainLoop(cls):
        cls.winRoot.startMainLoop()
   
    @classmethod
    def stopMainLoop(cls):
        cls.winRoot.startMainLoop()

    @classmethod
    def show(cls):
        cls.hideAllWidgets()
        cls.currLayout.show()
    
    @classmethod
    def hide(cls):
        for l in cls.layouts:
            l.hide()

    @classmethod
    def _bindKeys(cls):
        raise NotImplementedError()

    @classmethod
    def hideAllWidgets(cls):
        '''
        hide all widgets. clear all entries
        '''
        UIManagers = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken)
        for UIManager in UIManagers:
            UIManager.hide()
    
    @classmethod
    def startManager(cls):
        cls.createMenu()
        cls.show()
        cls.startMainLoop()



