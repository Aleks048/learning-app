import UI.widgets_collection.excercise.excercise as exw

import UI.widgets_manager as wm
import UI.widgets_facade as wf
import UI.widgets_collection.excercise.excercise as exw
import UI.widgets_data as wd

import file_system.file_system_facade as fsf
import settings.facade as sf
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import outside_calls.outside_calls_facade as ocf
import data.temp as dt


class LayoutManagers:

    class ExcerciseLayout(wm.MenuLayout_Interface):
        prefix = "_ExcerciseLayout_"
        subsection = _u.Token.NotDef.str_t
        imIdx = _u.Token.NotDef.str_t

        showExcerciseIm = True

        def __init__(self, winRoot):
            appDimensions = [720, 800, 0, 0]
            super().__init__(winRoot, appDimensions)
            self.excerciseImage = exw.ExcerciseImage(winRoot, self.prefix)
            self.addWidget(self.excerciseImage)
            self.excercise_BOX = exw.Excercise_BOX(winRoot, self.prefix)
            self.addWidget(self.excercise_BOX)
            self.addExcerciseLine_BTN = exw.AddExcerciseLine_BTN(winRoot, self.prefix)
            self.addWidget(self.addExcerciseLine_BTN)
            self.hideExcerciseImage = exw.HideExcerciseImage(winRoot, self.prefix)
            self.addWidget(self.hideExcerciseImage)
            addExcerciseLine_ETR = exw.AddExcerciseLine_ETR(winRoot, self.prefix)
            self.addWidget(addExcerciseLine_ETR)
            self.moveTOCtoExcerciseEntry_BTN = exw.MoveTOCtoExcerciseEntry_BTN(winRoot, self.prefix)
            self.addWidget(self.moveTOCtoExcerciseEntry_BTN)
            hideAllETRsWindow_BTN = exw.HideAllETRsWindow_BTN(winRoot, self.prefix)
            self.addWidget(hideAllETRsWindow_BTN)
            self.showSolutions_BTN = exw.ShowSolutions_BTN(winRoot, self.prefix)
            self.addWidget(self.showSolutions_BTN)
            self.showExtra_BTN = exw.ShowExtra_BTN(winRoot, self.prefix)
            self.addWidget(self.showExtra_BTN)

            self.addExcerciseLine_BTN.addListenerWidget(addExcerciseLine_ETR)
            addExcerciseLine_ETR.addListenerWidget(self.addExcerciseLine_BTN)
            self.addExcerciseLine_BTN.addListenerWidget(self.excercise_BOX)
            hideAllETRsWindow_BTN.addListenerWidget(self.excercise_BOX)

            winRoot.setGeometry(*self.appDimensions)

        def show(self):
            pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                            wf.Wr.MenuManagers.PdfReadersManager)
            pdfReadersManager.unbind()

            self.excerciseImage.subsection = self.subsection
            self.excerciseImage.entryIdx = self.imIdx

            self.hideExcerciseImage.subsection = self.subsection
            self.hideExcerciseImage.imIdx = self.imIdx

            self.moveTOCtoExcerciseEntry_BTN.subsection = self.subsection
            self.moveTOCtoExcerciseEntry_BTN.imIdx = self.imIdx

            self.addExcerciseLine_BTN.subsection = self.subsection
            self.addExcerciseLine_BTN.imIdx = self.imIdx

            self.excercise_BOX.subsection = self.subsection
            self.excercise_BOX.imIdx = self.imIdx

            self.showSolutions_BTN.subsection = self.subsection
            self.showSolutions_BTN.imIdx = self.imIdx
            self.showExtra_BTN.subsection = self.subsection
            self.showExtra_BTN.imIdx = self.imIdx

            super().show()

            # resize the solution box in respect to the size of the excercise image
            self.excerciseImage.update()

            if self.showExcerciseIm:
                canvasHeight = 730 - 20 - self.excerciseImage.getHeight()
            else:
                canvasHeight = 730 - 20

            self.excercise_BOX.setCanvasHeight(canvasHeight)
            self.excercise_BOX.originalHeight = canvasHeight
            self.excercise_BOX.update()

            currBookpath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            fullPathToEntryJSON = _upan.Paths.Entry.JSON.getAbs(currBookpath, 
                                                                self.subsection, 
                                                                self.imIdx)

            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(fullPathToEntryJSON):
                lines = fsf.Wr.EntryInfoStructure.readProperty(self.subsection,
                                                            self.imIdx, 
                                                            fsf.Wr.EntryInfoStructure.PubProp.entryLinesList)
                self.excercise_BOX.latestLineIdxToscrollTo = str(len(lines) - 1)
            else:
                self.excercise_BOX.latestLineIdxToscrollTo = str(0)

            if not self.showExcerciseIm:
                self.excerciseImage.hide()

            self.excercise_BOX.render()

        def changeHeight(self):
            self.excercise_BOX.setCanvasHeight(self.excercise_BOX.originalHeight - wd.Data.ExcerciseLayout.currSize)
            self.excerciseImage.setCanvasHeight(self.excerciseImage.originalHeight + wd.Data.ExcerciseLayout.currSize)
    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class ExcerciseManager(wm.MenuManager_Interface):
    imIdx = 0
    shown = False
    showManinExcerciseIm = True

    def __init__(self):

        winRoot = exw.ExcerciseRoot(50, 50)
        layouts = []
        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))
            
        self.subsection = fsf.Data.Book.currSection
        currLayout = layouts[0]
        currLayout.subsection = self.subsection
        
        super().__init__(winRoot,
                        layouts,
                        currLayout)

        winRoot.ExcerciseBox = self.layouts[0].excercise_BOX
        winRoot.AddExcerciseBTN = self.layouts[0].addExcerciseLine_BTN
        winRoot.hide()

    def changeLayoutHeight(self):
        self.layouts[0].changeHeight()

    def show(self, showManinExcerciseIm = None):
        self.layouts[0].subsection = self.subsection
        self.layouts[0].imIdx = self.imIdx
        self.shown = True

        if showManinExcerciseIm != None:
            self.showManinExcerciseIm = showManinExcerciseIm
    
        self.layouts[0].showExcerciseIm = self.showManinExcerciseIm

        return super().show()
    
    def hide(self):
        self.shown = False

        return super().hide()
        