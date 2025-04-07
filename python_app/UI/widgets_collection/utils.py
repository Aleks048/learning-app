from PIL import Image
import time
from threading import Thread
import os

import UI.widgets_wrappers as ww
import UI.widgets_data as wd
import UI.widgets_facade as wf
import UI.widgets_collection.common as comw

import file_system.file_system_facade as fsf
import data.constants as dc
import data.temp as dt
import _utils.pathsAndNames as _upan
import settings.facade as sf
import _utils._utils_main as _u
import outside_calls.outside_calls_facade as ocf
import generalManger.generalManger as gm
import tex_file.tex_file_facade as tff


def getGroupImg(subsection, currImGroupName):
    gi = str(list(fsf.Data.Sec.imagesGroupsList(subsection).keys()).index(currImGroupName))
    groupImgPath = _upan.Paths.Screenshot.Images.getGroupImageAbs(sf.Wr.Manager.Book.getCurrBookName(), 
                                            subsection,
                                            gi)

    if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(groupImgPath):
        result = Image.open(groupImgPath)
    else:
        result = \
            fsf.Wr.SectionInfoStructure.rebuildGroupOnlyImOnlyLatex(subsection,
                                                                    currImGroupName)

    shrink = 0.8
    result.thumbnail([int(result.size[0] * shrink),int(result.size[1] * shrink)], Image.LANCZOS)
    result = ww.currUIImpl.UIImage(result)

    return result

def getEntryImg(tex, subsection, imIdx):
    currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
    entryImgPath = _upan.Paths.Screenshot.Images.getMainEntryTexImageAbs(currBookPath, 
                                                                        subsection, 
                                                                        imIdx)

    if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryImgPath):
        result = Image.open(entryImgPath)
    else:
        result = tff.Wr.TexFileUtils.fromTexToImage(tex, 
                                                    entryImgPath,
                                                    fixedWidth = 700)

    return result

def bindWidgetTextUpdatable(event, getTextFunc, setTextFunc, 
                                   updateImageFunc = lambda *args: None,
                                   changeOnEtrFunc = lambda *args: None,
                                   changeOnLabelBackFunc = lambda *args: None,):
    widget = event.widget

    def __bringImageWidgetBack(event, imageWidget, setTextFunc, updateImageFunc, changeOnLabelBackFunc):
        newText = event.widget.getData()

        setTextFunc(newText, imageWidget)
        updateImageFunc(imageWidget)
        
        event.widget.hide()
        imageWidget.updateLabel()
        imageWidget.render()

        changeOnLabelBackFunc(widget)

    subsectionLabel = comw.MultilineText_ETR(widget.rootWidget, 
                                        "subsectionETR_" + widget.name, 
                                        widget.row, widget.column, 
                                        "", # NOTE: not used anywhere  
                                        getTextFunc(widget))
    subsectionLabel.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                            [lambda e, w = widget, sf = setTextFunc,  uf = updateImageFunc, bf = changeOnLabelBackFunc,
                             *args: __bringImageWidgetBack(e, w, sf, uf, bf)])
    subsectionLabel.forceFocus()
    subsectionLabel.render()
    widget.hide()
    changeOnEtrFunc(widget)

def bindChangeColorOnInAndOut(widget, shouldBeRed = False, shouldBeBrown = False):
    def __changeTextColorBlue(event = None, *args):
        event.widget.changeColor("blue")

    def __changeTextColorBrown(event = None, *args):
        event.widget.changeColor("brown")

    def __changeTextColorRed(event = None, *args):
        event.widget.changeColor("red")

    def __changeTextColorWhite(event = None, *args):
        event.widget.changeColor("white")
    
    widget.rebind([ww.currUIImpl.Data.BindID.enterWidget], [__changeTextColorBlue])
    if not shouldBeRed:
        widget.rebind([ww.currUIImpl.Data.BindID.leaveWidget], [__changeTextColorWhite])
    else:
        widget.rebind([ww.currUIImpl.Data.BindID.leaveWidget], [__changeTextColorRed])
    
    if shouldBeBrown:
        widget.rebind([ww.currUIImpl.Data.BindID.leaveWidget], [__changeTextColorBrown])

def addExtraIm(subsection, mainImIdx, isProof, entryLabel = None, event = None):
    extraImIdx = _u.Token.NotDef.str_t
    extraImagesDict = fsf.Data.Sec.extraImagesDict(subsection)

    if not isProof:
        if mainImIdx in list(extraImagesDict.keys()):
            extraImText = "con" + str(len(extraImagesDict[mainImIdx]))
        else:
            extraImText = "con0"
    else:
        extraImText = "proof"

    gm.GeneralManger.AddExtraImageForEntry(mainImIdx, subsection, extraImIdx, extraImText)

    def __afterEImagecreated(mainImIdx, subsection, 
                                extraImageIdx, extraImText, event,
                                entryLabel):            
        extraImagesDict = fsf.Data.Sec.extraImagesDict(subsection).copy()
        extraImagesList = []

        if extraImagesDict == _u.Token.NotDef.dict_t:
            extraImagesDict = {}

        if mainImIdx in list(extraImagesDict.keys()):
            extraImagesList = extraImagesDict[mainImIdx]

        if extraImageIdx == _u.Token.NotDef.str_t:
            extraImageIdx = len(extraImagesList) - 1

        currBokkPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        extraImagePath_curr = _upan.Paths.Screenshot.getAbs(currBokkPath, subsection)

        extraImageName = _upan.Names.getExtraImageFilename(mainImIdx, subsection, extraImageIdx)
        extraImagePathFull = os.path.join(extraImagePath_curr, extraImageName + ".png")
        timer = 0

        while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(extraImagePathFull):
            time.sleep(0.3)
            timer += 1

            if timer > 50:
                _u.log.autolog(f"\
The correct extra image was not created for \n\
'{subsection}':'{mainImIdx}' with id '{extraImageIdx}' and text '{extraImText}'")
                return False

        for w in wd.Data.Reactors.entryChangeReactors.values():
            if "onAddExtraImage" in dir(w):
                w.onAddExtraImage(subsection, mainImIdx, extraImageIdx)
        
        return
        if entryLabel != None:
            if entryLabel != None:
                if type(entryLabel) == TOCLabelWithClick:
                    #this comes from the main TOC menu
                    entryLabel.generateEvent(ww.currUIImpl.Data.BindID.mouse1)
                else:
                    # this comes from the Entry menu
                    entryLabel.notificationAfterImageWasCreated(entryLabel.subsection, entryLabel.imIdx)
                    updateSecondaryFrame = str(mainImIdx) != str(fsf.Data.Book.entryImOpenInTOC_UI)
                    entryLabel.updateHeight(scrollTOC = True, updateSecondaryFrame = updateSecondaryFrame)
                    entryLabel.scrollToImage(entryLabel.imIdx, extraImageIdx)

        if event != None:
            mathMenuManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                        wf.Wr.MenuManagers.MathMenuManager)
            mathMenuManager.scrollToWidget(event, None)

    t = Thread(target = __afterEImagecreated, 
            args = [mainImIdx, subsection, extraImIdx, extraImText, event, entryLabel])
    t.start()

def bindOpenOMOnThePageOfTheImage(widget, targetSubsection, targetImIdx, eImidx = None):
    def __cmd(event = None, *args): 
        pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.PdfReadersManager)
        
        pdfReadersManager.moveToEntry(targetSubsection, targetImIdx, eImidx, forcePageChange = True)

    widget.rebind([ww.currUIImpl.Data.BindID.cmdMouse1], [__cmd])

def openVideoOnThePlaceOfTheImage(widget, targetSubsection, targetImIdx, eImidx = None):
    def __cmd(event = None, *args): 
        pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.PdfReadersManager)
        
        pdfReadersManager.changeSize([720, 517, 0, 352])
        videoManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.VideoPlayerManager)
        
        videoManager.show(targetSubsection, targetImIdx)

    widget.rebind([ww.currUIImpl.Data.BindID.cmdMouse1], [__cmd])

def closeAllImages(gpframe, showAll, isWidgetLink, secondIm = [None, None], linkIdx = None):
    '''
    close all images of children of the widget
    '''
    parents = gpframe.getChildren().copy()
    for parent in parents:
        # NOTE this is not an ideal hack to get the
        children =  parent.getChildren().copy()
        for child in children:
            gChildren = child.getChildren().copy()
            for gChild in gChildren:
                if "contentOfImages_".lower() in str(gChild.name).lower():
                    subsection = str(gChild.name).split("_")[-4].replace("$", ".")
                    idx = str(gChild.name).split("_")[-3]

                    alwaysShow = False
                    if idx !=  "-1":
                        alwaysShow = fsf.Data.Sec.tocWImageDict(subsection)[idx] == "1"

                    if (not alwaysShow) or showAll: 
                        gChild.clicked = False
                    else: 
                        gChild.clicked = True

                    if "Row2" in str(child):
                        child.destroy()
            if "contentGlLinksOfImages_" in str(child.name):
                child.clicked = False

            # deal with extra images
            if dc.UIConsts.imageWidgetID.lower() in str(child.name).lower():
                subsection = str(child.name).split("_")[-4].replace("$", ".")
                idx = str(child.name).split("_")[-3].replace("-", "_").split("_")[0]

                alwaysShow = False
                if idx !=  "-1":
                    alwaysShow = fsf.Data.Sec.tocWImageDict(subsection)[idx] == "1"

                if ((not alwaysShow) or showAll or isWidgetLink) and\
                    ([subsection,idx] != secondIm):

                    if isWidgetLink:
                        if idx == linkIdx:
                            child.destroy()
                        else:
                            continue
                    
                    child.destroy()