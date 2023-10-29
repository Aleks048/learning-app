from tkinter import ttk
from PIL import Image, ImageTk
import os
import tkinter as tk
from tkinter import scrolledtext

import UI.widgets_wrappers as ww
import UI.widgets_data as wd
import file_system.file_system_facade as fsf
import data.constants as dc
import _utils.pathsAndNames as _upan
import settings.facade as sf
import _utils._utils_main as _u



class MultilineText_ETR(scrolledtext.ScrolledText):
    imIdx = None
    subsection = None
    etrWidget = None
    lineImIdx = None

    def __init__(self, patentWidget, prefix, row, column, imLineIdx, text):
        self.defaultText = text
        self.row = row
        self.column = column

        super().__init__(patentWidget, wrap=tk.WORD, 
                         width = 70, height = 5)
        self.insert(tk.END, text)
    
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

    def render(self):
        self.grid(row = self.row, column = self.column)


class ImageSize_ETR(ww.currUIImpl.TextEntry):
    subsection = None
    imIdx = None
    textETR = None

    def __init__(self, patentWidget, prefix, row, column, imIdx, text):
        name = "_imageSizeTOC_ETR" + str(imIdx)
        self.defaultText = text

        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }


        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wd.Data.ENT.defaultTextColor,
                                            "font": ('Georgia 14')},
            ww.TkWidgets.__name__ : {"width": 3}
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
    
    def __init__(self, root, prefix, row, column, columnspan = 1, *args, **kwargs) -> None:
        self.row = row
        self.column = column
        self.columnspan = columnspan

        super().__init__(root, name = prefix, *args, **kwargs)
    
    def render(self):
        self.grid(row = self.row, column = self.column,
                  columnspan = self.columnspan, sticky=tk.NW)

    def generateEvent(self, event, *args, **kwargs):
        self.event_generate(event, *args, **kwargs)

    def getChildren(self):
        return self.winfo_children()


def bindChangeColorOnInAndOut(widget:TOCLabelWithClick, shouldBeRed = False):
    def __changeTextColorBlue(event = None, *args):
        event.widget.configure(foreground="blue")

    def __changeTextColorRed(event = None, *args):
        event.widget.configure(foreground="red")

    def __changeTextColorWhite(event = None, *args):
        event.widget.configure(foreground="white")
    
    widget.rebind([ww.currUIImpl.Data.BindID.enterWidget], [__changeTextColorBlue])
    if not shouldBeRed:
        widget.rebind([ww.currUIImpl.Data.BindID.leaveWidget], [__changeTextColorWhite])
    else:
        widget.rebind([ww.currUIImpl.Data.BindID.leaveWidget], [__changeTextColorRed])


def getImageWidget(root, imagePath, widgetName, 
                   imPad = 0, imageSize = [450, 200], 
                   row = 0, column = 0, columnspan = 1,
                   resizeFactor = 1.0):
    pilIm = Image.open(imagePath)
    pilIm.thumbnail([i * resizeFactor for i in imageSize], Image.LANCZOS)
    img = ImageTk.PhotoImage(pilIm)

    imLabel = TOCLabelWithClick(root, prefix = widgetName, image = img, padding = [imPad, 0, 0, 0],
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
                                  row = 3, column = 0, columnspan = 100,
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
                               resizeFactor = 1.0):
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
                                            row = i + 4, column = 0, columnspan = 1000,
                                            resizeFactor = resizeFactor)
            displayedImagesContainer.append(eImg)

            outLabels.append(eimLabel)

            imageBaloon.bind(eimLabel, "{0}".format(eImText))
    return outLabels


def closeAllImages(gpframe, showAll, isWidgetLink):
    '''
    close all images of children of the widget
    '''
    for parent in gpframe.getChildren():
        for child in parent.getChildren():
            if "contentOfImages_" in str(child):
                subsection = str(child).split("_")[-2].replace("$", ".")
                idx = str(child).split("_")[-1]
                alwaysShow = fsf.Data.Sec.tocWImageDict(subsection)[idx] == "1"

                if (not alwaysShow) or showAll: 
                    child.clicked = False
                else: 
                    child.clicked = True

            if "contentGlLinksOfImages_" in str(child):
                child.clicked = False

            if dc.UIConsts.imageWidgetID in str(child):
                subsection = str(child).split("_")[-2].replace("$", ".")
                idx = str(child).split("_")[-1]
                alwaysShow = fsf.Data.Sec.tocWImageDict(subsection)[idx] == "1"

                if (not alwaysShow) or showAll or isWidgetLink: 
                    try:
                        child.destroy()
                    except:
                        pass