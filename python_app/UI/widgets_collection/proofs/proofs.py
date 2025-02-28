
import UI.widgets_wrappers as ww
import UI.widgets_facade as wf
import UI.widgets_collection.utils as _ucomw
import _utils._utils_main as _u
import data.constants as dc
import file_system.file_system_facade as fsf
import data.temp as dt

class ProofImageLabel(ww.currUIImpl.Frame):
    def __init__(self, root, prefix, subsection, imIdx, lineIdx):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : lineIdx + 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        self.displayedImages = []
        self.subsection = subsection
        self.imIdx = imIdx
        self.eImIdx = lineIdx
        name = "_ProofImageLabel_" + imIdx + str(lineIdx)

        self.lineImIdx = str(lineIdx)

        super().__init__(prefix, 
                         name, 
                         root, 
                         renderData = data)
    def render(self, **kwargs):
        exImLabel = _ucomw.addExtraEntryImagesWidgets(self, 
                                                       self.subsection, str(self.imIdx),
                                                       imPadLeft = 120, 
                                                       displayedImagesContainer = self.displayedImages,
                                                       leftMove = 700)[int(self.eImIdx)]
        exImLabel.render()
        return super().render(**kwargs)
   

class ProofMainImage(ww.currUIImpl.Frame):

    def __init__(self, parentWidget, prefix):
        self.displayedImages = []
        self.subsection = None
        self.entryIdx = None

        self.imLabel = None
        self.exImLabels = None

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
                                                      displayedImagesContainer = self.displayedImages,
                                                      leftMove = 700)
        self.imLabel.render()
        self.imLabel.forceFocus()

        def skipProofs(subsection, imIdx, i):
           return "proof" in fsf.Data.Sec.extraImagesDict(subsection)[imIdx][i].lower()

        self.exImLabels = _ucomw.addExtraEntryImagesWidgets(self, 
                                                       self.subsection, self.entryIdx,
                                                       imPadLeft = 120, 
                                                       displayedImagesContainer = self.displayedImages,
                                                       skippConditionFn = skipProofs,
                                                       leftMove = 700)
        for l in self.exImLabels:
            l.render()

        return super().render(**kwargs)

    def hide(self, **kwargs):
        if self.imLabel != None:
            self.imLabel.destroy()
            self.imLabel = None
        if self.exImLabels != None:
            for l in self.exImLabels:
                l.destroy()
            self.exImLabels = None
        return super().hide(**kwargs)

class EntryImages_BOX(ww.currUIImpl.ScrollableBox,
                    dc.AppCurrDataAccessToken):

    def __init__(self, parentWidget, prefix, windth = 700, height = 300):
        self.subsection = None
        self.imIdx = None

        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0, "columnspan" : 6, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.W}
        }
        name = "_EntryImages_BOX"

        super().__init__(prefix,
                        name,
                        parentWidget,
                        renderData = data,
                        height = height,
                        width = windth,
                        makeScrollable = False)
        
        self.imagesFrame = ProofMainImage(self.scrollable_frame, prefix)


    def render(self):
        self.imagesFrame.subsection = self.subsection
        self.imagesFrame.entryIdx = self.imIdx
        self.imagesFrame.render()
        imagesHeight = max([i.getHeight() for i in self.imagesFrame.imLabel.getChildren()]) + 10

        for l in self.imagesFrame.exImLabels:
            imagesHeight += max([i.getHeight() for i in l.getChildren()]) + 10

        newHeight = min(imagesHeight, 300)
        self.setCanvasHeight(newHeight)

        return super().render(self.renderData)

# class MoveTOCtoProofEntry_BTN(ww.currUIImpl.Button,
#                                   dc.AppCurrDataAccessToken):
#     subsection = None
#     imIdx = None

#     def __init__(self, patentWidget, prefix):
#         renderData = {
#             ww.Data.GeneralProperties_ID :{"column" : 4, "row" : 2},
#             ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
#         }
#         text = "Move TOC"
#         name = "_MoveTOCToEntry_BTN"
#         super().__init__(prefix, 
#                         name, 
#                         text, 
#                         patentWidget, 
#                         renderData, 
#                         self.cmd)

#     def cmd(self):
#         mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
#                                                           wf.Wr.MenuManagers.MathMenuManager)
#         mainManager.moveTocToEntry(self.subsection, self.imIdx)

class Proof_BOX(ww.currUIImpl.ScrollableBox,
                    dc.AppCurrDataAccessToken):

    def __init__(self, parentWidget, prefix, windth = 700, height = 600):
        self.subsection = None
        self.imIdx = None

        self.currLineCopyIdx = _u.Token.NotDef.int_t

        self.lineIdxShownInText = []
        self.displayedImages = []

        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 1, "columnspan" : 6, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.W}
        }
        name = "_showProofCurr_text"

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

        '''
        for each extra Image add widgets:
        '''

        for i in range(len(extraImagesForEntry)):
            if "proof" in extraImagesForEntry[i].lower():
                # image
                if extraImagesForEntry[i] != None:
                    label = ProofImageLabel(self.scrollable_frame, "linesImageIMG_" + str(i), 
                                                self.subsection, self.imIdx, i)
                    # label.rebind([ww.currUIImpl.Data.BindID.mouse1], [lambda e, *args: _ucomw.openImageManager(e, leftMove = 700)])
                    label.render()

    def hide(self, **kwargs):
        self.displayedImages = []
        self.lineIdxShownInText = []
        return super().hide(**kwargs)     

    def render(self):
        for w in self.getChildren().copy():
            w.destroy()

        self.forceFocus()

        self.addProofLines()

        return super().render(self.renderData)

class ProofsRoot(ww.currUIImpl.RootWidget,
                 dc.AppCurrDataAccessToken):
    def __init__(self, width, height, subsection, imIdx):
        self.subsection = subsection
        self.imIdx = imIdx
        super().__init__(width, height)
        self.bindClosing(self.__onClosing)

    def __onClosing(self):
        proofsManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.ProofsManager)
        proofsManager.hide(self.subsection, self.imIdx) 