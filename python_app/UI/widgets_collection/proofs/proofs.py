import tkinter as tk
from tkinter import ttk
import Pmw
from PIL import Image, ImageTk
import time
import os

import UI.widgets_wrappers as ww
import UI.widgets_facade as wf
import UI.widgets_collection.utils as _ucomw
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import data.constants as dc
import file_system.file_system_facade as fsf
import settings.facade as sf
import outside_calls.outside_calls_facade as ocf
import scripts.osascripts as osascr
import UI.widgets_data as wd
import data.temp as dt
import generalManger.generalManger as gm

images = []

class ProofImageLabel(ttk.Label):
    lineImIdx = None

    def __init__(self, root, name, subsection, imIdx, lineIdx):
        self.lineImIdx = str(lineIdx)

        bookName = sf.Wr.Manager.Book.getCurrBookName()

        imagePath = _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(bookName, subsection, imIdx, str(lineIdx))

        pilIm = Image.open(imagePath)
        pilIm.thumbnail([530, 1000], Image.LANCZOS)
        img = ImageTk.PhotoImage(pilIm)
        images.append(img)
        return super().__init__(root, name = name, image = img, padding = [90, 0, 0, 0])


class ProofMainImage(ww.currUIImpl.Frame):
    displayedImages = []
    subsection = None
    entryIdx = None

    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0, "columnspan": 6},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.NW}
        }
        name = "_proofMainImage_LBL"

        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data)
    
    def render(self, **kwargs):
                
        # get an image from the
        widget = self.widgetObj

        for child in widget.winfo_children():
            child.destroy()

        balloon = Pmw.Balloon(widget)
        self.imLabel = _ucomw.addMainEntryImageWidget(widget, 
                                                      self.subsection, self.entryIdx,
                                                      120, self.displayedImages, balloon)
        self.imLabel.render()
        self.imLabel.focus_force()

        def skipProofs(subsection, imIdx, i):
           return "proof" in fsf.Data.Sec.extraImagesDict(subsection)[imIdx][i].lower()

        exImLabels = _ucomw.addExtraEntryImagesWidgets(widget, 
                                                       self.subsection, self.entryIdx,
                                                       120, self.displayedImages, balloon,
                                                       skipProofs)
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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_showProofCurr_text"

        self.parent = parentWidget.widgetObj

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
                label.grid(row = i + 1, column = 0)
            

    def render(self, widjetObj=None, renderData=..., **kwargs):
        global images
        images = []
        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        self.scrollable_frame.focus_force()

        self.addProofLines()

        return super().render(widjetObj, renderData, **kwargs)

class ProofsRoot(ww.currUIImpl.RootWidget):
    pass