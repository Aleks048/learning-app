import data.constants as dc
import data.temp as dt

import _utils.logging as log
import outside_calls.outside_calls_facade as ocf
import settings.facade as sf

import UI.widgets_collection.common as comw
import UI.widgets_wrappers as ww

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

    def switchUILayout(self, toLayoutType, hideWidgets = True):
        if hideWidgets:
            self.hideAllWidgets(changePdfWidget = False)

        for layout in self.layouts:
            if type(layout) == toLayoutType:
                self.currLayout = layout
                layout.show()
                self.winRoot.render()
                return
            else:
                layout.hide()
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
            if not((not changePdfWidget) and ("pdfreadersmanage" in str(type(UIManager)).lower()))\
                and ("proof" not in str(type(UIManager)).lower()):
                UIManager.hide()

    def startManager(self):
        self.show()

    def isShown(self):
        return self.__isShown


class UI_generalManager(dc.AppCurrDataAccessToken):
    @classmethod
    def showNotification(cls, msg, shouldWait):
        import UI.widgets_facade as wf
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

    @classmethod
    def __createMainRoot(cls, width, height, x, y):
        winRoot = comw.MainRoot(width, height)
        winRoot.setGeometry(width, height, x, y)
        winRoot.configureColumn(0, weight=1)
        winRoot.configureColumn(1, weight=1)

        return winRoot

    @classmethod
    def startup(cls):
        import UI.widgets_collection.startup.manager as sm
        log.autolog("-- Srartup startup menu started: ")
        startupMenuManager = sm.StartupMenuManager()
        log.autolog("Started '{0}' UI manager".format("startup menu"))

        startupMenuManager.show()
        log.autolog("-- Srartup of startup menu ended.")

        ww.currUIImpl.startLoop()

    @classmethod
    def startNonStartMenus(cls):
        import UI.widgets_collection.main.math.manager as mm
        import UI.widgets_collection.message.manager as mesm
        import UI.widgets_collection.toc.manager as tocm
        import UI.widgets_collection.excercise.manager as exm
        import UI.widgets_collection.notes.manager as nom
        import UI.widgets_collection.entryNotes.manager as enom
        import UI.widgets_collection.proofs.manager as prm
        import UI.widgets_collection.image.manager as imm
        import UI.widgets_collection.pdfReader.manager as pdfrm
        import UI.widgets_collection.excerciseLineNote.manager as enm
        import UI.widgets_collection.excerciseSolution.manager as eslnm
        import UI.widgets_collection.excerciseExtra.manager as eextm

        cls.winRoot = cls.__createMainRoot(1500, 850, 0, 0)

        # create startup menu
        log.autolog("-- Srartup of other menus started: ")
        messageMenuManager = mesm.MessageMenuManager()
        log.autolog("Started '{0}' UI manager".format("message menu"))
        mainMenuManager = mm.MathMenuManager(cls.winRoot)
        log.autolog("Started '{0}' UI manager".format("main menu"))
        tocMenuManager = tocm.TOCManager()
        log.autolog("Started '{0}' UI manager".format("toc menu"))
        exMenuManager = exm.ExcerciseManager()
        log.autolog("Started '{0}' UI manager".format("excercise menu"))
        notesMenuManager = nom.NotesManager()
        log.autolog("Started '{0}' UI manager".format("dictionary menu"))
        entryNotesMenuManager = enom.EntryNotesManager()
        log.autolog("Started '{0}' UI manager".format("entry notes menu"))
        proofsMenuManager = prm.ProofsManager()
        log.autolog("Started '{0}' UI manager".format("proofs menu"))
        imagagesMenuManager = imm.ImagesManager()
        log.autolog("Started '{0}' UI manager".format("image menu"))
        pdfReadersMenuManager = pdfrm.PdfReadersManager(cls.winRoot)
        log.autolog("Started '{0}' UI manager".format("pdfReader menu"))
        excerciseLineNoteManager = enm.ExcerciseLineNoteManager()
        log.autolog("Started '{0}' UI manager".format("excercise note menu"))
        excerciseSolutionManager = eslnm.ExcerciseSolutionManager()
        log.autolog("Started '{0}' UI manager".format("excercise solution menu"))
        excerciseExtraManager = eextm.ExcerciseExtraManager()
        log.autolog("Started '{0}' UI manager".format("excercise extra menu"))

        log.autolog("-- Srartup  of other menus ended.")

        pdfReadersMenuManager.show()
        mainMenuManager.show()

    @classmethod
    def exit(cls):
        import UI.widgets_collection.startup.manager as sm
        import UI.widgets_collection.message.manager as mesm
        import UI.widgets_collection.toc.manager as tocm
        import UI.widgets_collection.excercise.manager as exm
        import UI.widgets_collection.notes.manager as nom
        import UI.widgets_collection.entryNotes.manager as enom
        import UI.widgets_collection.proofs.manager as prm
        import UI.widgets_collection.image.manager as imm
        import UI.widgets_collection.pdfReader.manager as pdfrm
        import UI.widgets_collection.excerciseLineNote.manager as enm
        import UI.widgets_collection.excerciseSolution.manager as eslnm
        import UI.widgets_collection.excerciseExtra.manager as eextm

        log.autolog("- Starting exiting the app")

        # Updating the remote
        msg = "Closing the book."
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

        # main
        # mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
        #                                         wf.Wr.MenuManagers.MathMenuManager)
        # mainManager.winRoot.ExitApp()

        # message
        mesManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    mesm.MessageMenuManager)
        mesManager.winRoot.ExitApp()
        
        
        # toc
        tocManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                tocm.TOCManager)
        tocManager.winRoot.ExitApp()
        
        # ex
        exManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                exm.ExcerciseManager)
        exManager.winRoot.ExitApp()

        # proof
        proofsManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                               prm.ProofsManager)
        proofsManager.hideAll()

        # images
        imagesManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                imm.ImagesManager)
        imagesManager.winRoot.ExitApp()

        # pdfReader
        pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                pdfrm.PdfReadersManager)
        pdfReadersManager.updateOMpage()
        # pdfReadersManager.winRoot.ExitApp()

        # excerciseLineNoteManager
        excerciseLineNoteManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                               enm.ExcerciseLineNoteManager)
        excerciseLineNoteManager.winRoot.ExitApp()

        # excerciseSolutionManager
        excerciseSolutionManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                               eslnm.ExcerciseSolutionManager)
        excerciseSolutionManager.winRoot.ExitApp()

        # excerciseExtraManager
        excerciseExtraManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                eextm.ExcerciseExtraManager)
        excerciseExtraManager.winRoot.ExitApp()

        # notes
        notesManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                nom.NotesManager)
        notesManager.winRoot.ExitApp()

        # entry notes
        entryNotesManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                enom.EntryNotesManager)
        entryNotesManager.winRoot.ExitApp()

        cls.winRoot.ExitApp()

        # startup
        stManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                sm.StartupMenuManager)
        stManager.winRoot.ExitApp()