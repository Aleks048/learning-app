from tkinter import ttk
import fitz
from PIL import Image
from threading import Thread
import time
import io
import re
import copy
import subprocess

import UI.widgets_wrappers as ww
import UI.widgets_manager as wm
import UI.widgets_collection.utils as uw
import UI.widgets_facade as wf
import UI.widgets_collection.utils as _ucomw
import UI.widgets_collection.common as comw
import UI.widgets_data as wd
import _utils._utils_main as _u
import data.temp as dt
import _utils.pathsAndNames as _upan
import data.constants as dc
import file_system.file_system_facade as fsf
import settings.facade as sf
import outside_calls.outside_calls_facade as ocf

class SubsectionSummaryLink:
    def __init__(self, text, subsection, imIdx):
        self.text = text
        self.subsection = subsection
        self.imIdx = imIdx


class SubsectionSummaryText(ww.currUIImpl.MultilineText):
    def __init__(self, rootWidget):
        self.row = 1
        self.column = 0

        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : self.column, "row" : self.row, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NE}
        }

        extraOptions = {
            ww.Data.GeneralProperties_ID :{"width" : 300, "height" : 300},
            ww.TkWidgets.__name__ : {}
        }
        
        self.subsection = None
        self.name = "_subsectionSummary_"

        super().__init__(prefix = "", 
                         name = self.name, 
                         rootWidget = rootWidget, 
                         renderData = renderData,
                         extraOptions = extraOptions,
                         text = "",
                         width = 100,
                         height = 8)

        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdshv],
                    [self.__pasteLink])


    def __pasteLink(self, widget):
        link = f"[{dt.UITemp.Link.imIdx}|{dt.UITemp.Link.subsection}:{dt.UITemp.Link.imIdx}]"
        widget.addTextAtCurrent(link)

    def changeText(self, newText):
        self.updateText(newText)
        self.setData(newText)

    def updateLabel(self):
        newText = fsf.Data.Sec.subsectionSummaryText(self.subsection)

        newTextList = re.split(r"(\[[^\|]*\|[^\]]*\])", newText)

        links = []

        for i in range(len(newTextList)):
            if len (newTextList[i]) > 0:
                if newTextList[i][0] == "[":
                    links.append(newTextList[i])
                    newTextList[i] = "[" + newTextList[i].split("|")[1][:-1] + "]"

        newText = "".join(newTextList)

        self.changeText(newText)

        def moveToEntry(ppath):
            imIdx = ppath.split(":")[-1]
            subsection = ppath.split(":")[0]

            if subsection != fsf.Data.Book.subsectionOpenInTOC_UI:
                fsf.Data.Book.subsectionOpenInTOC_UI = subsection

                for w in wd.Data.Reactors.entryChangeReactors.values():
                    if "onSubsectionOpen" in dir(w):
                        w.onSubsectionOpen(subsection)

            fsf.Data.Book.entryImOpenInTOC_UI = imIdx

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onFullEntryMove" in dir(w):
                    w.onFullEntryMove()


        for l in links:
            text = "[" + l.split("|")[1][:-1] + "]"
            path = l.split("|")[1][:-1]
            self.makeLink(text, lambda p = path, *args: moveToEntry(p))

    def __makeLockable(self):
        def __getText(widget):
            return fsf.Data.Sec.subsectionSummaryText(self.subsection)

        def __setText(newText, widget):
            fsf.Data.Sec.subsectionSummaryText(self.subsection, newText)
        
        def __changeOnEtrFunc(widget):
            pass
        
        def __changeOnLabelBackFunc(widget):
            pass

        self.rebind([ww.currUIImpl.Data.BindID.mouse2],
                        [lambda e, g = __getText, 
                                    s = __setText, 
                                    c = __changeOnEtrFunc, 
                                    b = __changeOnLabelBackFunc, 
                                    pl = self.__pasteLink, *args:
                                                    uw.bindWidgetTextUpdatable(e, g, s, 
                                                        changeOnEtrFunc = c,
                                                        changeOnLabelBackFunc = b,
                                                        etrWidth = 100,
                                                        etrHeight = 8,
                                                        pasteLambda = self.__pasteLink)])

    def render(self):
        super().render(self.renderData)

        self.updateLabel()
        self.makeUneditable()
        self.__makeLockable()

class SummaryRoot(ww.currUIImpl.Frame):
    def __init__(self, rootWidget, width, height):
        name = "_SummaryRoot_"
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 0, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NE}
        }
        extraOptions = {
            ww.Data.GeneralProperties_ID :{"width" : width, "height" : height},
            ww.TkWidgets.__name__ : {}
        }
        super().__init__("", name, rootWidget, renderData = renderData, extraOptions = extraOptions)
