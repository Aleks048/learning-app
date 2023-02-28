import data.constants as dc
import data.temp as dt
import _utils._utils_main as _u
import _utils.logging as log

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
        for layout in self.layouts:
            if type(layout) == toLayoutType:
                layout.show()
                return
        raise KeyError

    def startMainLoop(self):
        self.winRoot.startMainLoop()

    def stopMainLoop(self):
        self.winRoot.stopMainLoop()

    def show(self):
        self.hideAllWidgets()
        self.currLayout.show()
    
    def hide(self):
        pass
        # for l in self.layouts:
        #     l.hide()

    def hideAllWidgets(self):
        '''
        hide all widgets. clear all entries
        '''
        UIManagers = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken)
        for UIManager in UIManagers:
            UIManager.hide()

    def startManager(self):
        self.show()
        self.startMainLoop()



