import data.constants as dc
import data.temp as dt

import _utils.logging as log
import _utils._utils_main as _u
import outside_calls.outside_calls_facade as ocf
import settings.facade as sf

import UI.widgets_collection.common as comw
import UI.widgets_wrappers as ww

menuManagers = []

class MenuLayout_Interface(dc.AppCurrDataAccessToken):
    name = None
    def __init__(self, winRoot, appDimensions = None):
        self.widgets = set()
        self.winRoot = winRoot
        self.appDimensions = appDimensions

        if self.appDimensions != None:
            self.setAppDimensions()        

    def addWidget(self, widget):
        self.widgets.add(widget)
    
    def setAppDimensions(self):
        if self.appDimensions != None:
            self.winRoot.setGeometry(*self.appDimensions)

    def show(self):
        if self.appDimensions != None:
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

        for layout in self.layouts:
            if type(layout) == toLayoutType:
                self.currLayout = layout
                layout.show()
                self.winRoot.render()
            else:
                layout.hide()

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
    topLevelFrames = {}

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

    def addImage(subsection, imIdx, extraImIdx,
                selector = True,
                changePrevPos = True,
                withoutRender = True):
        import UI.widgets_collection.pdfReader.manager as pdfm
        pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                           pdfm.PdfReadersManager)
        pdfReadersManager.show(subsection = subsection,
                               imIdx = imIdx,
                               selector = selector,
                               extraImIdx = extraImIdx,
                               changePrevPos = changePrevPos,
                               withoutRender = withoutRender)

    @classmethod
    def addTopLevelFrame(cls, rootWidget, row, column, rowspan, columnspan, width, height):
        frame = comw.TopLevelFrame(rootWidget = rootWidget, 
                                   row = row, column = column, 
                                   columnSpan = columnspan, rowSpan = rowspan,
                                   width = width,
                                   height = height)

        frame.forceFixedDimentions(width, height)
        cls.topLevelFrames[frame.prefix] = frame

        return frame

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
        import UI.widgets_collection.mainTOC.manager as mtocm
        import UI.widgets_collection.mainEntry.manager as mem
        import UI.widgets_collection.secondaryImages.manager as secim
        import UI.widgets_collection.summary.manager as summ
        import UI.widgets_collection.videoPlayer.manager as vipm
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

        dimensions = _u.getMonitorsAreas()[0]
        width = dimensions[2] # 1500
        height = dimensions[3] - 50 # 850

        halfWidth = int(width / 2)

        cls.winRoot = cls.__createMainRoot(width, height, 0, 0)

        rightFrame = cls.addTopLevelFrame(rootWidget = cls.winRoot,
                                          row = 0, column = 1, 
                                          rowspan = 1, columnspan = 1,
                                          width = halfWidth, height = height)
        rightTopFrame = cls.addTopLevelFrame(rootWidget = rightFrame,
                                          row = 0, column = 0, 
                                          rowspan = 1, columnspan = 1,
                                          width = halfWidth, height = 50)
        rightSecondFrame = cls.addTopLevelFrame(rootWidget = rightFrame,
                                          row = 1, column = 0, 
                                          rowspan = 1, columnspan = 1,
                                          width = 10, height = 10)
        rightThirdFrame = cls.addTopLevelFrame(rootWidget = rightFrame,
                                          row = 2, column = 0, 
                                          rowspan = 1, columnspan = 1,
                                          width = 10, height = 10)
        rightBottomFrame = cls.addTopLevelFrame(rootWidget = rightFrame,
                                          row = 3, column = 0, 
                                          rowspan = 1, columnspan = 1,
                                          width = halfWidth, height = 10)

        leftFrame = cls.addTopLevelFrame(rootWidget = cls.winRoot,
                                         row = 0, column = 0, 
                                         rowspan = 1, columnspan = 1,
                                         width = halfWidth, height = height)
        leftTopFrame = cls.addTopLevelFrame(rootWidget = leftFrame,
                                         row = 0, column = 0, 
                                         rowspan = 1, columnspan = 1,
                                         width = halfWidth, height = 100)
        leftMiddleFrame = cls.addTopLevelFrame(rootWidget = leftFrame,
                                         row = 1, column = 0, 
                                         rowspan = 1, columnspan = 1,
                                         width = 100, height = 100)
        leftBottomFrame = cls.addTopLevelFrame(rootWidget = leftFrame,
                                         row = 2, column = 0, 
                                         rowspan = 1, columnspan = 1,
                                         width = halfWidth, height = 100)

        # create startup menu
        log.autolog("-- Srartup of other menus started: ")
        mainMenuManager = mm.MathMenuManager(rightBottomFrame)
        log.autolog("Started '{0}' UI manager".format("main menu"))
        mainTOCmanager = mtocm.MainTOCManager(rightSecondFrame)
        log.autolog("Started '{0}' UI manager".format("mainTOC menu"))
        mainEntryManager = mem.MainEntryMenuManager(rightThirdFrame)
        log.autolog("Started '{0}' UI manager".format("mainEntry menu"))
        pdfReadersMenuManager = pdfrm.PdfReadersManager(leftMiddleFrame)
        log.autolog("Started '{0}' UI manager".format("pdfReader menu"))
        secondaryImagesManager = secim.SecondaryImagesManager(leftBottomFrame)
        log.autolog("Started '{0}' UI manager".format("secondary images menu"))
        summaryManager = summ.SummaryManager(leftBottomFrame)
        log.autolog("Started '{0}' UI manager".format("summary menu"))
        videoPlayerManager = vipm.VideoPLayerManager(leftBottomFrame)
        log.autolog("Started '{0}' UI manager".format("video player manager menu"))
        messageMenuManager = mesm.MessageMenuManager()
        log.autolog("Started '{0}' UI manager".format("message menu"))
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
        excerciseLineNoteManager = enm.ExcerciseLineNoteManager()
        log.autolog("Started '{0}' UI manager".format("excercise note menu"))
        excerciseSolutionManager = eslnm.ExcerciseSolutionManager()
        log.autolog("Started '{0}' UI manager".format("excercise solution menu"))
        excerciseExtraManager = eextm.ExcerciseExtraManager()
        log.autolog("Started '{0}' UI manager".format("excercise extra menu"))

        log.autolog("-- Srartup  of other menus ended.")

        pdfReadersMenuManager.show()
        mainTOCmanager.show()
        mainEntryManager.show()
        mainMenuManager.show()

        rightTopFrame.render()
        rightSecondFrame.render()
        rightThirdFrame.render()
        # rightBottomFrame.render()

        rightFrame.render()

        leftTopFrame.render()
        leftMiddleFrame.render()
        leftBottomFrame.render()
        leftFrame.render()

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