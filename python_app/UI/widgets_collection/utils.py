from tkinter import ttk
from PIL import Image, ImageTk
import os
import tkinter as tk
from AppKit import NSPasteboard, NSStringPboardType
from tkinter import scrolledtext

import UI.widgets_wrappers as ww
import UI.widgets_data as wd
import file_system.file_system_facade as fsf
import data.constants as dc
import _utils.pathsAndNames as _upan
import settings.facade as sf
import _utils._utils_main as _u
import outside_calls.outside_calls_facade as ocf



class MultilineText_ETR(scrolledtext.ScrolledText):
    imIdx = None
    subsection = None
    etrWidget = None
    lineImIdx = None

    def __init__(self, patentWidget, prefix, row, column, imLineIdx, text, *args, **kwargs):
        self.defaultText = text

        txt = ""
        lineLength = 0

        txtList = text.split(" ")

        for w in txtList:
            lineLength += len(w.replace("\n", "")) + 1
            txt += w + " "

            if ("\n" in w) or (lineLength > 70):
                if not("\n" in w):
                    txt += "\n"

                lineLength = 0

        newHeight = int(len(txt.split("\n"))) + 1
        self.row = row
        self.column = column

        super().__init__(patentWidget, 
                         wrap = None, 
                         width = 70, 
                         height = newHeight, 
                         *args, 
                         **kwargs)
        self.config(spacing1 = 10)
        self.config(spacing2 = 10)
        self.config(spacing3 = 12)
        self.insert(tk.END, text)

        self.config(height = newHeight)
        self.place(x = 0, y = 0)
        self.bind(ww.currUIImpl.Data.BindID.Keys.ctrlv,
                  lambda *args: self.__pasteText(*args))

    def __pasteText(self, *args):
        pos = self.index(tk.INSERT)
        oldText = self.get("0.0", tk.END)

        pb = NSPasteboard.generalPasteboard()
        text:str = pb.stringForType_(NSStringPboardType)

        text = text.replace("\u0000", "fi")

        self.insert(tk.INSERT, text)

    def getData(self):
        binString = self.get('1.0', tk.END)
        bitStringIsEmpty = len([i for i in binString if i=="" or i == "\n"]) == len(binString)

        # removing the unnecessary newlines from the end
        while binString[-1] == "\n":
            binString = binString[:-1]

            if len(binString) == 0:
                binString = _u.Token.NotDef.str_t
                break

        return binString if not bitStringIsEmpty else _u.Token.NotDef.str_t

    def rebind(self, keys, funcs):
        for i in range(len(keys)):
            self.bind(keys[i], funcs[i])
        
        def __boldenText(*args):
            startSelIDX = self.index("sel.first")
            endSelIDX = self.index("sel.last")
            selText = self.get(startSelIDX, endSelIDX)
            boldSelText = f"\\textbf{{{selText}}}"
            self.replace(startSelIDX, endSelIDX, boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdb,
                  lambda *args: __boldenText(*args))

        def __underlineText(*args):
            startSelIDX = self.index("sel.first")
            endSelIDX = self.index("sel.last")
            selText = self.get(startSelIDX, endSelIDX)
            boldSelText = f"\\underline{{{selText}}}"
            self.replace(startSelIDX, endSelIDX, boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdu,
                  lambda *args: __underlineText(*args))

        def __addNote(*args):
            boldSelText = "\\textbf{NOTE:} "
            self.insert("0.0", boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdn,
                  lambda *args: __addNote(*args))

        def __addNoteInPlace(*args):
            boldSelText = "\\textbf{NOTE:} "
            self.insert(tk.INSERT, boldSelText)

        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdshn,
                  lambda *args: __addNoteInPlace(*args))

        def __addDef(*args):
            boldSelText = "\\textbf{DEF:} "
            self.insert(tk.INSERT, boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdd,
                  lambda *args: __addDef(*args))

        def __addProposion(*args):
            boldSelText = "\\textbf{Proposition:} "
            self.insert(tk.INSERT, boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdp,
                  lambda *args: __addProposion(*args))

        def __addExample(*args):
            boldSelText = "\\textbf{EX:} "
            self.insert("0.0", boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmde,
                  lambda *args: __addExample(*args))

        def __addLemma(*args):
            boldSelText = "\\textbf{Lemma:} "
            self.insert("0.0", boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdl,
                  lambda *args: __addLemma(*args))

        def __addExcercise(*args):
            boldSelText = "excercise "
            self.insert("0.0", boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdshe,
                  lambda *args: __addExcercise(*args))

    def render(self):
        self.grid(row = self.row, column = self.column)
    
    def generateEvent(self, event):
        self.event_generate(event)


class ImageSize_ETR(ww.currUIImpl.TextEntry):
    subsection = None
    imIdx = None
    textETR = None

    def __init__(self, patentWidget, prefix, row, column, imIdx, text, width = 3):
        name = "_imageSizeTOC_ETR" + str(imIdx)
        self.defaultText = text

        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }


        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wd.Data.ENT.defaultTextColor,
                                            "font": ('Georgia 14')},
            ww.TkWidgets.__name__ : {"width": width}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraBuildOptions,
                        defaultText = self.defaultText)
        super().setData(self.defaultText)

    def receiveNotification(self, _):
        return self.getData()

    def defaultTextCMD(self):
        pass


class TOCFrame(ttk.Frame):
    subsection = None
    imIdx = None

    def __init__(self, root, prefix, row, column, columnspan = 1, *args, **kwargs) -> None:
        self.row = row
        self.column = column
        self.columnspan = columnspan

        super().__init__(root, name = prefix, *args, **kwargs)

    def render(self):
        self.grid(row = self.row, column = self.column, 
                  columnspan = self.columnspan, sticky=tk.NW)

    def getChildren(self):
        return self.winfo_children()

class TOCTextWithClick(tk.Text):
    '''
    this is used to run different commands on whether the label was clicked even or odd times
    '''
    clicked = False
    imIdx = ""
    subsection = ""
    imagePath = ""
    group = ""
    image = None
    alwaysShow = None
    shouldShowExMenu = False
    lineImIdx = _u.Token.NotDef.str_t
    etrWidget = _u.Token.NotDef.str_t

    sticky = None

    tocFrame = None

    eImIdx = None

    targetSubssection = None
    targetImIdx = None
    sourceSubssection = None
    sourceImIdx= None
    sourceWebLinkName = None

    def rebind(self, keys, cmds):
        for i in range(len(keys)):
            key = keys[i]
            cmd = cmds[i]

            if key == ww.TkWidgets.Data.BindID.allKeys:
                self.bind_all(key, lambda event: cmd(event))
            else:
                self.bind(key, cmd)
    
    def __init__(self, root, prefix, row, column, columnspan = 1, sticky = tk.NW, text = "", *args, **kwargs) -> None:
        self.row = row
        self.column = column
        self.columnspan = columnspan
        self.sticky = sticky

        super().__init__(root, name = prefix, *args, **kwargs)
        self.config(spacing1 = 10)
        self.config(spacing2 = 10)
        self.config(spacing3 = 12)
        self.config(wrap = tk.WORD)
        
        self.insert(tk.END, text)   

        # numTextLines = len(text.split("\n"))

        # if numTextLines == 1:
        #     numLinesToAdd = 0 
        # else:
        #     numLinesToAdd = int(numTextLines) - 1

        # numLinesToAdd = int((7/8) * numLinesToAdd)

        txtList = text.split(" ")
        txt = ""
        lineLength = 0

        for w in txtList:
            lineLength += len(w.replace("\n", "")) + 1
            txt += w + " "

            if ("\n" in w) or (lineLength > 113):
                if not("\n" in w):
                    txt += "\n"

                lineLength = 0

        Font_tuple = ("TkFixedFont", 12)
        self.config(font = Font_tuple)
        self.config(width = 85)
        self.config(height = int(len(txt.split("\n"))))
        self.config(background = "#394d43")
        self.config(state=tk.DISABLED)
        self.place(x = 0, y = 0)
    
    def render(self):
        self.grid(row = self.row, column = self.column,
                  columnspan = self.columnspan, sticky = self.sticky)

    def generateEvent(self, event, *args, **kwargs):
        self.event_generate(event, *args, **kwargs)

    def getChildren(self):
        return self.winfo_children()

class TOCLabelWithClick(ttk.Label):
    '''
    this is used to run different commands on whether the label was clicked even or odd times
    '''
    clicked = False
    imIdx = ""
    subsection = ""
    imagePath = ""
    group = ""
    image = None
    alwaysShow = None
    shouldShowExMenu = False
    lineImIdx = _u.Token.NotDef.str_t
    etrWidget = _u.Token.NotDef.str_t

    sticky = None

    tocFrame = None

    eImIdx = None

    targetSubssection = None
    targetImIdx = None
    sourceSubssection = None
    sourceImIdx= None
    sourceWebLinkName = None

    def rebind(self, keys, cmds):
        for i in range(len(keys)):
            key = keys[i]
            cmd = cmds[i]

            if key == ww.TkWidgets.Data.BindID.allKeys:
                self.bind_all(key, lambda event: cmd(event))
            else:
                self.bind(key, cmd)
    
    def __init__(self, root, prefix, row, column, columnspan = 1, sticky = tk.NW, *args, **kwargs) -> None:
        self.row = row
        self.column = column
        self.columnspan = columnspan
        self.sticky = sticky

        super().__init__(root, name = prefix, *args, **kwargs)
    
    def render(self):
        self.grid(row = self.row, column = self.column,
                  columnspan = self.columnspan, sticky = self.sticky)

    def generateEvent(self, event, *args, **kwargs):
        self.event_generate(event, *args, **kwargs)

    def getChildren(self):
        return self.winfo_children()


def bindChangeColorOnInAndOut(widget:TOCLabelWithClick, shouldBeRed = False, shouldBeBrown = False):
    def __changeTextColorBlue(event = None, *args):
        event.widget.configure(foreground="blue")

    def __changeTextColorBrown(event = None, *args):
        event.widget.configure(foreground="brown")

    def __changeTextColorRed(event = None, *args):
        event.widget.configure(foreground="red")

    def __changeTextColorWhite(event = None, *args):
        event.widget.configure(foreground="white")
    
    widget.rebind([ww.currUIImpl.Data.BindID.enterWidget], [__changeTextColorBlue])
    if not shouldBeRed:
        widget.rebind([ww.currUIImpl.Data.BindID.leaveWidget], [__changeTextColorWhite])
    else:
        widget.rebind([ww.currUIImpl.Data.BindID.leaveWidget], [__changeTextColorRed])
    
    if shouldBeBrown:
        widget.rebind([ww.currUIImpl.Data.BindID.leaveWidget], [__changeTextColorBrown])


def getImageWidget(root, imagePath, widgetName, 
                   imPad = 0, imageSize = [450, 1000], 
                   row = 0, column = 0, columnspan = 1,
                   resizeFactor = 1.0):
    if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
        pilIm = Image.open(imagePath)
        pilIm.thumbnail([i * resizeFactor for i in imageSize], Image.LANCZOS)
        img = ImageTk.PhotoImage(pilIm)

        imLabel = TOCLabelWithClick(root, prefix = widgetName, image = img, padding = [imPad, 0, 0, 0],
                                    row = row, column = column, columnspan = columnspan)
    else:
        img = None
        imLabel = TOCLabelWithClick(root, prefix = widgetName, text = "-1", padding = [imPad, 0, 0, 0],
                                    row = row, column = column, columnspan = columnspan)

    imLabel.imagePath = imagePath
    imLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], 
                [lambda event, *args: os.system("open " + "\"" + event.widget.imagePath + "\"")])
    return img, imLabel


def addMainEntryImageWidget(rootLabel,
                            subsection, imIdx,
                            imPadLeft, 
                            displayedImagesContainer,
                            imageBaloon,
                            mainImgBindData = None,
                            resizeFactor = 1.0):
    # mainImage
    currBookName = sf.Wr.Manager.Book.getCurrBookName()
    imagePath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBookName,
                                                                   subsection,
                                                                   imIdx)

    mainWidgetName = _upan.Names.UI.getMainEntryWidgetName(subsection, imIdx)
    img, imLabel = getImageWidget(rootLabel, imagePath, 
                                  mainWidgetName, imPadLeft,
                                  row = 4, column = 0, columnspan = 100,
                                  resizeFactor = resizeFactor)

    displayedImagesContainer.append(img)

    if mainImgBindData != None:
        imLabel.rebind(*mainImgBindData)

    imLinkDict = fsf.Data.Sec.imLinkDict(subsection)

    if type(imLinkDict) == dict:
        if str(imIdx) in list(imLinkDict.keys()):
            imText = imLinkDict[str(imIdx)]
        else:
            imText = _u.Token.NotDef.str_t
    else:
        imText = _u.Token.NotDef.str_t

    imageBaloon.bind(imLabel, "{0}".format(imText))
    return imLabel


def addExtraEntryImagesWidgets(rootLabel, 
                               subsection, imIdx,
                               imPadLeft, 
                               displayedImagesContainer,
                               imageBaloon, 
                               skippConditionFn = lambda *args: False,
                               resizeFactor = 1.0,
                               tocFrame = None):
    outLabels = []
    # extraImages
    if imIdx in list(fsf.Data.Sec.extraImagesDict(subsection).keys()):
        currBookName = sf.Wr.Manager.Book.getCurrBookName()
        extraImages = fsf.Data.Sec.extraImagesDict(subsection)[imIdx]

        for i in range(0, len(extraImages)):
            if skippConditionFn(subsection, imIdx, i):
                continue

            eImText = extraImages[i]

            extraImFilepath = _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(currBookName,
                                                                                  subsection,
                                                                                  imIdx,
                                                                                  i)

            eImWidgetName = _upan.Names.UI.getExtraEntryWidgetName(subsection,
                                                                   imIdx,
                                                                   i)

            eImg, eimLabel = getImageWidget(rootLabel, extraImFilepath, 
                                            eImWidgetName, imPadLeft,
                                            row = i + 5, column = 0, columnspan = 1000,
                                            resizeFactor = resizeFactor)
            removeEntry = TOCLabelWithClick(rootLabel,
                                            text = "[delete]",
                                            prefix = "delete_" + eImWidgetName,
                                            row =  i + 5, 
                                            column = 0,
                                            sticky = tk.NW)
            removeEntry.imIdx = imIdx
            removeEntry.subsection = subsection
            removeEntry.eImIdx = i
            removeEntry.tocFrame = tocFrame

            def delEIm(event, *args):
                widget:TOCLabelWithClick = event.widget
                fsf.Wr.SectionInfoStructure.removeExtraIm(widget.subsection,
                                                          widget.imIdx,
                                                          eImIdx = widget.eImIdx)
                
                if widget.tocFrame != None:
                    tocFrame.render()

            removeEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],[delEIm])

            bindChangeColorOnInAndOut(removeEntry)
            removeEntry.render()

            displayedImagesContainer.append(eImg)

            outLabels.append(eimLabel)

            imageBaloon.bind(eimLabel, "{0}".format(eImText))

    return outLabels


def closeAllImages(gpframe, showAll, isWidgetLink, secondIm = [None, None], linkIdx = None):
    '''
    close all images of children of the widget
    '''
    for parent in gpframe.getChildren():
        # NOTE this is not an ideal hack to get the 
        if "getChildren" in dir(parent):
            for child in parent.getChildren():
                if "getChildren" in dir(child):
                    for gChild in child.getChildren():
                        if "contentOfImages_" in str(gChild):
                            subsection = str(gChild).split("_")[-2].replace("$", ".")
                            idx = str(gChild).split("_")[-1]
                            alwaysShow = fsf.Data.Sec.tocWImageDict(subsection)[idx] == "1"

                            if (not alwaysShow) or showAll: 
                                gChild.clicked = False
                            else: 
                                gChild.clicked = True

                            if "Row2" in str(child):
                                child.destroy()

                if "contentGlLinksOfImages_" in str(child):
                    child.clicked = False

                if dc.UIConsts.imageWidgetID in str(child):
                    subsection = str(child).split("_")[-2].replace("$", ".")
                    idx = str(child).split("_")[-1]
                    alwaysShow = fsf.Data.Sec.tocWImageDict(subsection)[idx] == "1"

                    if ((not alwaysShow) or showAll or isWidgetLink) and\
                        ([subsection,idx] != secondIm):

                        if isWidgetLink:
                            if idx == linkIdx:
                                child.destroy()
                            else:
                                continue
                        try:
                            child.destroy()
                        except:
                            pass