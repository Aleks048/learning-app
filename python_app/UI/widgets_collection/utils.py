from tkinter import ttk
from PIL import Image, ImageTk
import os
import tkinter as tk

import UI.widgets_wrappers as ww
import file_system.file_system_facade as fsf
import data.constants as dc
import _utils.pathsAndNames as _upan
import settings.facade as sf
import _utils._utils_main as _u



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
                   row = 0, column = 0, columnspan = 1):
    pilIm = Image.open(imagePath)
    pilIm.thumbnail(imageSize, Image.ANTIALIAS)
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
                            mainImgBindData = None):
    # mainImage
    currBookName = sf.Wr.Manager.Book.getCurrBookName()
    imagePath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBookName,
                                                                   subsection,
                                                                   imIdx)

    mainWidgetName = _upan.Names.UI.getMainEntryWidgetName(subsection, imIdx)
    img, imLabel = getImageWidget(rootLabel, imagePath, 
                                  mainWidgetName, imPadLeft,
                                  row = 3, column = 0, columnspan = 100)

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
                               skippConditionFn = lambda *args: False):
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
                                            row = i + 4, column = 0, columnspan = 1000)
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