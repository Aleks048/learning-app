from PIL import Image
from threading import Thread

import UI.widgets_wrappers as ww
import UI.widgets_facade as wf
import UI.factories.factoriesFacade as wff
import UI.widgets_collection.utils as wcu

import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import data.constants as dc
import file_system.file_system_facade as fsf
import settings.facade as sf
import outside_calls.outside_calls_facade as ocf
import UI.widgets_data as wd
import data.temp as dt

class ImageText_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix, row, column, imLineIdx, text):
        name = "_textImage_ETR" + str(imLineIdx)
        self.defaultText = text
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row, "columnspan": 7},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }


        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wd.Data.ENT.defaultTextColor,
                                            "font": ('Georgia 14')},
            ww.TkWidgets.__name__ : {"width": 60, "fg": "white"}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraBuildOptions,
                        defaultText = self.defaultText)
        super().setData(self.defaultText)
        self.setTextColor("white")
    
    def receiveNotification(self, _):
        return self.getData()
    
    def defaultTextCMD(self):
        pass


class ExcerciseImageLabel(ww.currUIImpl.Label):
    def __init__(self, root, prefix, subsection, imIdx, lineIdx, row, column, text = _u.Token.NotDef.str_t):
        self.lineImIdx = str(lineIdx)

        self.subsection = subsection
        self.bookName = sf.Wr.Manager.Book.getCurrBookName()
        self.imIdx = imIdx
        self.lineIdx = lineIdx

        data = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }

        name = "_ExcerciseImageLabel_"

        if text ==  _u.Token.NotDef.str_t:
            bookName = sf.Wr.Manager.Book.getCurrBookName()

            imagePath = _upan.Paths.Entry.LineImage.getAbs(bookName, subsection, imIdx, lineIdx)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                fsf.Wr.EntryInfoStructure.rebuildLine(subsection, 
                                                      imIdx, 
                                                      lineIdx, 
                                                      text,
                                                      currBookPath)

            pilIm = Image.open(imagePath)
            pilIm.thumbnail([530, 1000], Image.LANCZOS)
            self.image = ww.currUIImpl.UIImage(pilIm)
            return super().__init__(prefix, name, root, data, image = self.image, padding = [0, 0, 0, 0])
        else:
            return super().__init__(prefix, name, root, data, text = text, padding = [0, 0, 0, 0])

    def updateImage(self):
        imagePath = _upan.Paths.Entry.LineImage.getAbs(self.bookName, 
                                                       self.subsection, 
                                                       self.imIdx, 
                                                       self.lineIdx)
        pilIm = Image.open(imagePath)
        pilIm.thumbnail([530, 1000], Image.LANCZOS)
        self.image = ww.currUIImpl.UIImage(pilIm)
        return super().updateImage(self.image)


class ExcerciseImage(ww.currUIImpl.ScrollableBox):
    subsection = None
    entryIdx = None

    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0, "columnspan": 6},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        name = "_excerciseImage_LBL"

        self.originalHeight = 300

        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data,
                        height = 300)
    
    def hide(self, **kwargs):
        for child in self.getChildren().copy():
            child.destroy()
        return super().hide(**kwargs)

    def render(self, **kwargs):
        for child in self.getChildren().copy():
            child.destroy()

        entryImagesFactory = wff.EntryImagesFactory(self.subsection, self.entryIdx)
        self.imLabel = entryImagesFactory.produceEntryMainImageWidget(rootLabel = self.scrollable_frame,
                                                                        imPadLeft = 120)
        self.imLabel.render()
        self.imLabel.forceFocus()

        def skipProofs(subsection, imIdx, i):
           return "proof" in fsf.Data.Sec.extraImagesDict(subsection)[imIdx][i].lower()


        exImLabels = entryImagesFactory.produceEntryExtraImagesWidgets(rootLabel = self.scrollable_frame,
                                                                        imPadLeft = 120,
                                                                        skippConditionFn = skipProofs,
                                                                        createExtraWidgets = False)
        for l in exImLabels:
            l.render()

        return super().render(**kwargs)


class AddExcerciseLine_BTN(ww.currUIImpl.Button,
                           dc.AppCurrDataAccessToken):
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 1, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        text = "Add"
        name = "_AddExcerciseLine_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        text = self.notify(AddExcerciseLine_ETR)
        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        structureCreated = fsf.Wr.EntryInfoStructure.addLine(self.subsection, self.imIdx, text, bookPath)

        # update the box UI
        self.notify(Excercise_BOX)

        if structureCreated:
            mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.MathMenuManager)
            mainManager.moveTocToEntry(self.subsection, self.imIdx)


    def receiveNotification(self, broadcasterType):
        if broadcasterType == AddExcerciseLine_ETR:
            self.cmd()

class ShowSolutions_BTN(ww.currUIImpl.Button):
    showSolutions = True
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 5, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        text = "Solutions"
        name = "_ShowSolutions_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        excerciseSolutionManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.ExcerciseSolutionManager)
        if self.showSolutions:
            excerciseSolutionManager.show(self.subsection, self.imIdx)
            self.showSolutions = False
        else:
            excerciseSolutionManager.hide()
            self.showSolutions = True

class ShowExtra_BTN(ww.currUIImpl.Button):
    showSolutions = True
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 6, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        text = "Extra"
        name = "_ShowExtra_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        excerciseExtraManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.ExcerciseExtraManager)
        if self.showSolutions:
            excerciseExtraManager.show(self.subsection, self.imIdx)
            self.showSolutions = False
        else:
            excerciseExtraManager.hide()
            self.showSolutions = True


class HideExcerciseImage(ww.currUIImpl.Button):
    subsection = None
    imIdx = None

    show = False

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        text = "Hide Main Image"
        name = "_HideExcerciseImage_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                          wf.Wr.MenuManagers.ExcerciseManager)
        excerciseManager.show(self.show)
        self.show = not self.show

class HideAllETRsWindow_BTN(ww.currUIImpl.Button):
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 3, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        text = "Hide All ETRs"
        name = "_HideAllETRsWindow_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        self.notify(Excercise_BOX)

class MoveTOCtoExcerciseEntry_BTN(ww.currUIImpl.Button,
                                  dc.AppCurrDataAccessToken):
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 4, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        text = "Move TOC"
        name = "_MoveTOCToEntry_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        excerciseManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.MathMenuManager)
        excerciseManager.moveTocToEntry(self.subsection, self.imIdx)

class AddExcerciseLine_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix):
        name = "_getExcerciseNewLineText_ETR"
        defaultText = "New excercise line text"
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 3, "columnspan": 7},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        extraOptions = {
            ww.Data.GeneralProperties_ID : {"width" : 70},
            ww.TkWidgets.__name__ : {}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraOptions = extraOptions,
                        defaultText = defaultText,
                        bindCmd = self.bindCmd)
    
    def receiveNotification(self, broadcasterType):
        text = self.getData()

        if broadcasterType == AddExcerciseLine_BTN:
            self.setData(self.defaultText)

        if (text != self.defaultText) and (text != ""):
            return text
        else:
            return "-1"
      
    def getData(self, **kwargs):
        text = super().getData(**kwargs)
        return text
      
    def bindCmd(self):
        return [ww.currUIImpl.Data.BindID.Keys.shenter], \
                [lambda *args: self.notify(AddExcerciseLine_BTN)]

def _rebuildLine(*args, **kwargs):
    '''
        used for multithreaded line rebuild
    '''
    t = Thread(target= fsf.Wr.EntryInfoStructure.rebuildLine, 
            args = (args))
    t.start()
    return t

class Excercise_BOX(ww.currUIImpl.ScrollableBox,
                    dc.AppCurrDataAccessToken):

    def __init__(self, parentWidget, prefix, windth = 700, height = 300):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 1, "columnspan" : 7, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.W}
        }
        self.subsection = None
        self.imIdx = None

        self.currLineCopyIdx = _u.Token.NotDef.int_t

        self.lineManagers = {}

        #NOTE: this is overriden each time the manager calls show
        self.originalHeight = height

        name = "_Excercise_BOX"

        super().__init__(prefix,
                        name,
                        parentWidget,
                        renderData = data,
                        height = height,
                        width = windth,
                        makeScrollable = True)

        def on_vertical(event):
            self.scrollY(-1 * event.delta)

        self.rebind(['<Mod1-MouseWheel>'], [on_vertical])

    def __addExcerciseLine(self, lineIdx, row):
        factory = wff.ExcerciseLineFactory(self.subsection, self.imIdx, 
                                           lineIdx = lineIdx, 
                                           row = row)
        self.lineManagers[str(lineIdx)] = factory.produce(self.scrollable_frame)

    def addExcerciseLines(self):
        lines = fsf.Wr.EntryInfoStructure.readProperty(self.subsection,
                                                       self.imIdx, 
                                                       fsf.Wr.EntryInfoStructure.PubProp.entryLinesList)

        for lineIdx in range(len(lines)):
           row = lineIdx
           self.__addExcerciseLine(lineIdx, row)

    def receiveNotification(self, broadcasterType) -> None:
        if broadcasterType == AddExcerciseLine_BTN:
            lines = fsf.Wr.EntryInfoStructure.readProperty(self.subsection,
                                                       self.imIdx, 
                                                       fsf.Wr.EntryInfoStructure.PubProp.entryLinesList)
            lineIdx = len(lines) - 1
            row = lineIdx
            self.__addExcerciseLine(lineIdx, row)
            wcu.scrollIntoView(self, None, self.lineManagers[str(lineIdx)].frame)
        if broadcasterType == HideAllETRsWindow_BTN:
            for m in self.lineManagers.values():
                m.lineEtr.hide()

    def onTextUpdateEtrHide(self, lineIdx):
        if self.lineManagers.get(str(lineIdx)) != None:
            wcu.scrollIntoView(self, None, self.lineManagers[str(lineIdx)].frame)

    def onTextUpdateEtrShow(self, lineIdx):
        if self.lineManagers.get(str(lineIdx)) != None:
            wcu.scrollIntoView(self, None, self.lineManagers[str(lineIdx)].lineEtr)

    def render(self, shouldScroll = True):
        wd.Data.Reactors.excerciseLineChangeReactors[self.name] = self

        for w in self.getChildren().copy():
            w.destroy()

        self.forceFocus()

        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        entryLinesPath = _upan.Paths.Entry.getAbs(bookPath, self.subsection, self.imIdx)

        fullPathToEntryJSON = _upan.Paths.Entry.JSON.getAbs(bookPath, self.subsection, self.imIdx)

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(fullPathToEntryJSON):
            numLines = len(fsf.Wr.EntryInfoStructure.readProperty(self.subsection,
                                                        self.imIdx, 
                                                        fsf.Wr.EntryInfoStructure.PubProp.entryLinesList))
        else:
            numLines = 0

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryLinesPath):
            self.addExcerciseLines()


        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 1 + numLines + 1, "row" : 1 + numLines + 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }

        dummyPostLabel = ww.currUIImpl.Label(str(1 + numLines + 1),
                                             "_excersiePostDummy_",
                                             self.scrollable_frame,
                                             renderData,
                                             text= "\n" * 1000)
        dummyPostLabel.render()


        super().render(self.renderData)

class ExcerciseRoot(ww.currUIImpl.RootWidget):
    ExcerciseBox:Excercise_BOX = None
    AddExcerciseBTN:AddExcerciseLine_BTN = None

    def __init__(self, width, height, bindCmd=...):
        super().__init__(width, height, self.bindCmd)  
        self.bindClosing(self.__onClosing)  

    def bindCmd(self):
        def __scrollUp(*args):
            if self.ExcerciseBox != None:
                self.ExcerciseBox.scrollY(1)
        def __scrollDown(*args):
            if self.ExcerciseBox != None:
                self.ExcerciseBox.scrollY(-1)
        def __addLine(*args):
            if self.AddExcerciseBTN != None:
                self.AddExcerciseBTN.cmd()
        
        def __updateHeight():
            excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                          wf.Wr.MenuManagers.ExcerciseManager)
            excerciseManager.changeLayoutHeight()
        def __layoutSmallMainImage(*args):
            wd.Data.ExcerciseLayout.currSize = wd.Data.ExcerciseLayout.small
            __updateHeight()
        def __layoutRegularMainImage(*args):
            wd.Data.ExcerciseLayout.currSize = wd.Data.ExcerciseLayout.normal
            __updateHeight()
        def __layoutLargeMainImage(*args):
            wd.Data.ExcerciseLayout.currSize = wd.Data.ExcerciseLayout.large
            __updateHeight()

        def __bind(*args):
            self.rebind([ww.currUIImpl.Data.BindID.Keys.shdown, 
                        ww.currUIImpl.Data.BindID.Keys.shup,
                        ww.currUIImpl.Data.BindID.Keys.cmdshs,
                        ww.currUIImpl.Data.BindID.Keys.cmdzero,
                        ww.currUIImpl.Data.BindID.Keys.cmdminus,
                        ww.currUIImpl.Data.BindID.Keys.cmdplus,
                        ], \
                        [__scrollUp, __scrollDown, __addLine, 
                        __layoutSmallMainImage, __layoutRegularMainImage, __layoutLargeMainImage])
        def __unbind(*args):
            self.unbind([ww.currUIImpl.Data.BindID.Keys.shdown, 
                        ww.currUIImpl.Data.BindID.Keys.shup,
                        ww.currUIImpl.Data.BindID.Keys.cmdshs,
                        ww.currUIImpl.Data.BindID.Keys.cmdzero,
                        ww.currUIImpl.Data.BindID.Keys.cmdminus,
                        ww.currUIImpl.Data.BindID.Keys.cmdplus,
                        ])
        
        return [ww.currUIImpl.Data.BindID.enterWidget, ww.currUIImpl.Data.BindID.leaveWidget],\
               [__bind, __unbind]

    def __onClosing(self):
        excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                          wf.Wr.MenuManagers.ExcerciseManager)
        excerciseManager.hide()

        msg = "\
After updating the excercises.".format()
        _u.log.autolog(msg)
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)