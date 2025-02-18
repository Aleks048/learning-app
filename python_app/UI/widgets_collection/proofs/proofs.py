import Pmw
from PIL import Image

import UI.widgets_wrappers as ww
import UI.widgets_facade as wf
import UI.widgets_collection.utils as _ucomw
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import data.constants as dc
import file_system.file_system_facade as fsf
import settings.facade as sf
import data.temp as dt

class ProofImageLabel(ww.currUIImpl.Label):
    def __init__(self, root, prefix, subsection, imIdx, lineIdx):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : lineIdx + 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        name = "ProofImLabel" + imIdx + str(lineIdx)

        self.lineImIdx = str(lineIdx)

        bookName = sf.Wr.Manager.Book.getCurrBookName()

        imagePath = _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(bookName, subsection, imIdx, str(lineIdx))

        pilIm = Image.open(imagePath)
        pilIm.thumbnail([530, 1000], Image.LANCZOS)
        self.image = ww.currUIImpl.UIImage(pilIm)

        return super().__init__(prefix, name, root, data,
                                image = self.image, 
                                padding = [90, 0, 0, 0])


class ProofMainImage(ww.currUIImpl.Frame):
    displayedImages = []
    subsection = None
    entryIdx = None

    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0, "columnspan": 6},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        name = "_proofMainImage_LBL"

        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data)
    
    def render(self, **kwargs):

        for child in self.getChildren().copy():
            child.destroy()

        self.imLabel = _ucomw.addMainEntryImageWidget(self, 
                                                      self.subsection, self.entryIdx,
                                                      imPadLeft = 120, 
                                                      displayedImagesContainer = self.displayedImages)
        self.imLabel.render()
        self.imLabel.forceFocus()

        def skipProofs(subsection, imIdx, i):
           return "proof" in fsf.Data.Sec.extraImagesDict(subsection)[imIdx][i].lower()

        exImLabels = _ucomw.addExtraEntryImagesWidgets(self, 
                                                       self.subsection, self.entryIdx,
                                                       imPadLeft = 120, 
                                                       displayedImagesContainer = self.displayedImages,
                                                       skippConditionFn = skipProofs)
        for l in exImLabels:
            l.render()

        return super().render(**kwargs)

class MoveTOCtoProofEntry_BTN(ww.currUIImpl.Button,
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
        mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.MathMenuManager)
        mainManager.moveTocToEntry(self.subsection, self.imIdx)

class HideProofsWindow_BTN(ww.currUIImpl.Button,
                              dc.AppCurrDataAccessToken):
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 2, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        text = "Hide"
        name = "_HideProofsWindow_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        proofsManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.ProofsManager)
        proofsManager.hide()


class Proof_BOX(ww.currUIImpl.ScrollableBox,
                    dc.AppCurrDataAccessToken):
    subsection = None
    imIdx = None

    currLineCopyIdx = _u.Token.NotDef.int_t

    lineIdxShownInText = []
    currEtr = _u.Token.NotDef.dict_t.copy()

    displayedImages = []

    def __init__(self, parentWidget, prefix, windth = 700, height = 500):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 1, "columnspan" : 6, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.W}
        }
        name = "_showProofCurr_text"

        self.images = []

        super().__init__(prefix,
                        name,
                        parentWidget,
                        renderData = data,
                        height = height,
                        width = windth,
                        makeScrollable = False)

    def addProofLines(self):
        extraImagesForSubsection = fsf.Data.Sec.extraImagesDict(self.subsection)

        if self.imIdx not in list(extraImagesForSubsection.keys()):
            return
        
        extraImagesForEntry = extraImagesForSubsection[self.imIdx]
        extraImagesForEntry = \
            [i if "proof" in i.lower() else None for i in extraImagesForEntry]

        '''
        for each extra Image add widgets:
        '''

        for i in range(len(extraImagesForEntry)):
            # image
            if extraImagesForEntry[i] != None:
                label = ProofImageLabel(self.scrollable_frame, "linesImageIMG_" + str(i), 
                                            self.subsection, self.imIdx, i)
                self.images.append(label.image)
                label.render()

    def hide(self, **kwargs):
        self.images = []
        return super().hide(**kwargs)     

    def render(self):
        for w in self.getChildren().copy():
            w.destroy()

        self.forceFocus()

        self.addProofLines()

        return super().render(self.renderData)

class ProofsRoot(ww.currUIImpl.RootWidget):
    pass