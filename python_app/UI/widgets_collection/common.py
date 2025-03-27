from PIL import Image
import Pmw
import os
import re
import time
from threading import Thread
import sys

import UI.widgets_wrappers as ww
import UI.widgets_facade as wf
import UI.widgets_collection.toc.toc as tocw
import settings.facade as sf
import data.constants as dc
import data.temp as dt
import outside_calls.outside_calls_facade as ocf
import file_system.file_system_facade as fsm
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import tex_file.tex_file_facade as tff
import UI.widgets_collection.utils as _uuicom
import UI.widgets_data as wd
import generalManger.generalManger as gm

class ImageText_ETR(ww.currUIImpl.TextEntry):
    subsection = None
    imIdx = None
    textETR = None
    etrWidget = None # note this is set top the object so the <ENTER> bind workss

    def __init__(self, patentWidget, prefix, row, column, imIdx, text):
        name = "_textImageTOC_ETR" + str(imIdx)
        self.defaultText = text

        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }


        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wd.Data.ENT.defaultTextColor,
                                            "font": ('Georgia 14')},
            ww.TkWidgets.__name__ : {"width": 40}
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


class ImageGroupOM(ww.currUIImpl.OptionMenu):
    def __init__(self,
                 listOfOptions, 
                 rootWidget, 
                 subsection,
                 imIdx,
                 tocBox,
                 column,
                 currImGroupName = None):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : column, 
                                            "row" : 0,
                                            "columnspan" : 3},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, 
                                     "sticky" : ww.currUIImpl.Orientation.NW}
        }

        name = "GroupOM_"

        self.imIdx = imIdx
        self.subsection = subsection
        self.tocBox = tocBox

        prefix = "_Group_" + subsection.replace(".", "_") + "_" + imIdx

        super().__init__(prefix, 
                         name,
                         listOfOptions,
                         rootWidget,
                         data,
                         defaultOption = currImGroupName,
                         cmd = self.chooseGroupCmd)
                        
    def chooseGroupCmd(self):
        imagesGroupList:list = list(fsm.Data.Sec.imagesGroupsList(self.subsection).keys())
        imagesGroupDict = fsm.Data.Sec.imagesGroupDict(self.subsection)
        imagesGroupDict[self.imIdx] =  imagesGroupList.index(self.getData())
        fsm.Data.Sec.imagesGroupDict(self.subsection, imagesGroupDict)

        
        for w in wd.Data.Reactors.entryChangeReactors.values():
            if "onGroupChange" in dir(w):
                w.onGroupChange(self.subsection, self.imIdx)

class EntryShowPermamentlyCheckbox(ww.currUIImpl.Checkbox):
    def __init__(self, parent, subsection, imIdx, prefix, row, column):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        name = "_EntryShowPermamentlyCheckbox_"

        self.subsection = subsection
        self.imIdx = str(imIdx)

        tocWImageDict = fsm.Data.Sec.tocWImageDict(self.subsection)
        if tocWImageDict == _u.Token.NotDef.dict_t:
            alwaysShow = "0"
        else:
            alwaysShow = tocWImageDict[self.imIdx]

        super().__init__(prefix,
                         name,
                         parent, 
                         renderData,
                         command = lambda *args: self.__cmd())
        self.setData(int(alwaysShow))

    def __cmd(self):
        tocWImageDict = fsm.Data.Sec.tocWImageDict(self.subsection)
        tocWImageDict[self.imIdx] = str(self.getData())
        fsm.Data.Sec.tocWImageDict(self.subsection, tocWImageDict)


        for w in wd.Data.Reactors.entryChangeReactors.values():
            if "onAlwaysShowChange" in dir(w):
                w.onAlwaysShowChange(self.subsection, self.imIdx)
    
    def render(self):
        tocWImageDict = fsm.Data.Sec.tocWImageDict(self.subsection)
        newData = _u.Token.NotDef.str_t

        if tocWImageDict.get(self.imIdx) != None:
            newData = tocWImageDict[self.imIdx]

        self.setData(newData)
        return super().render(self.renderData)


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


def getGroupImg(subsection, currImGroupName):
    gi = str(list(fsm.Data.Sec.imagesGroupsList(subsection).keys()).index(currImGroupName))
    groupImgPath = _upan.Paths.Screenshot.Images.getGroupImageAbs(sf.Wr.Manager.Book.getCurrBookName(), 
                                            subsection,
                                            gi)

    if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(groupImgPath):
        result = Image.open(groupImgPath)
    else:
        result = \
            fsm.Wr.SectionInfoStructure.rebuildGroupOnlyImOnlyLatex(subsection,
                                                                    currImGroupName)

    shrink = 0.8
    result.thumbnail([int(result.size[0] * shrink),int(result.size[1] * shrink)], Image.LANCZOS)
    result = ww.currUIImpl.UIImage(result)

    return result


class LinksFrame(ww.currUIImpl.Frame):
    class __EntryUIs:
        class __EntryUIData:
            def __init__(self, name, column) -> None:
                self.name = name
                self.column = column

        fullMove = __EntryUIData("[f]", 2)
        linkImages = __EntryUIData("[i]", 3)
        delete = __EntryUIData("[d]", 4)
        proof = __EntryUIData("[Proof]", 8)

    def __init__(self, parent, subsection, imIdx, row, column, entryFrame, padding = [0, 0, 0, 0]):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : column, "row" : row, "columnspan" : 100},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        name = "_LinksFrame_"

        self.subsection = subsection
        self.imIdx = str(imIdx)
        self.entryFrame = entryFrame

        self.prefix =  _upan.Names.Entry.getEntryNameID(self.subsection, self.imIdx)

        super().__init__(self.prefix,
                         name,
                         parent, 
                         renderData,
                         padding = padding)
    
    def __showLinkImages(self, e, frame, *args):
        widget = e.widget

        entryImagesFactory = _uuicom.EntryImagesFactory(widget.subsection, widget.imIdx)
        imLabel = entryImagesFactory.produceEntryMainImageWidget(rootLabel = frame,
                                                                 imPadLeft = 120)
        imLabel.render()

        def skipProofs(subsection, imIdx, i):
            return "proof" in fsm.Data.Sec.extraImagesDict(subsection)[imIdx][i].lower()


        exImLabels = entryImagesFactory.produceEntryExtraImagesWidgets(rootLabel = frame,
                                                                        imPadLeft = 120,
                                                                        skippConditionFn = skipProofs)
        for l in exImLabels:
            l.render()
        
        if frame.wasRendered:
            frame.hide()
        else:
            frame.render()

    def __delGlLinkCmd(self, event, *args):
        widget = event.widget
        gm.GeneralManger.RemoveGlLink(widget.targetSubssection,
                                        widget.sourceSubssection,
                                        widget.sourceImIdx,
                                        widget.targetImIdx)
        self.render()

    def __delWebLinkCmd(self, event, *args):
        widget = event.widget
        gm.GeneralManger.RemoveWebLink(widget.sourceSubssection,
                                        widget.sourceImIdx,
                                        widget.sourceWebLinkName)
        self.render()

    def __moveLinkFull(self, e, *args):
        fsm.Data.Book.subsectionOpenInTOC_UI = e.widget.subsection
        fsm.Data.Book.entryImOpenInTOC_UI = e.widget.imIdx
        for w in wd.Data.Reactors.entryChangeReactors.values():
            if "onFullEntryMove" in dir(w):
                w.onFullEntryMove()

    def __openWebOfTheImageCmd(self, event, webLink, *args):
        cmd = "open -na 'Google Chrome' --args --new-window \"" + webLink + "\""
        _u.runCmdAndWait(cmd)
    
    def __openProofsMenu(self, event, *args):
        prMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.ProofsManager)

        event.widget.shouldShowProofMenu = not event.widget.shouldShowProofMenu

        if (event.widget.shouldShowProofMenu):
            prMenuManger.show(subsection =  event.widget.subsection, imIdx = event.widget.imIdx)
        else:
            prMenuManger.hide(subsection =  event.widget.subsection, imIdx = event.widget.imIdx)


    def AddLinks(self):
        imGlobalLinksDict = fsm.Data.Sec.imGlobalLinksDict(self.subsection)
        haveLinks = self.imIdx in imGlobalLinksDict.keys()
        glLinkLablel = _uuicom.TOCLabelWithClick(self, 
                                text =  "Links: " if haveLinks else "No links", 
                                prefix = "contentLinksIntroFr_" + self.prefix,
                                padding = [60, 0, 0, 0],
                                row = 0, column = 0)
        glLinkLablel.render()

        if haveLinks:
            glLinks:dict = fsm.Data.Sec.imGlobalLinksDict(self.subsection)[self.imIdx].copy()

            glLinkIdx = 0

            # NOTE: should put all the links into 
            # one frame. This way they will be aligned correctly
            if type(glLinks) == dict:
                for ln, lk in glLinks.items():
                    if "KIK" in lk:
                        # NOTE: probably should be a frame here
                        glLinkImLablel = _uuicom.TOCLabelWithClick(
                                                self, 
                                                prefix = "contentLinksImLabelIntroFr_" + self.prefix + "_" + str(glLinkIdx),
                                                padding = [60, 0, 0, 0],
                                                row = glLinkIdx + 1, column = 0)
                        glLinkImLablel.render()

                        targetSubsection = ln.split("_")[0]
                        targetImIdx = ln.split("_")[1]
                        textOnlyLink = fsm.Data.Sec.textOnly(targetSubsection)[targetImIdx]

                        glLinkSubsectioLbl = _uuicom.TOCLabelWithClick(
                                                glLinkImLablel, 
                                                prefix = "contentGlLinksTSubsection_" + self.prefix + "_" + str(glLinkIdx),
                                                text = targetSubsection + ": ", 
                                                padding = [90, 0, 0, 0],
                                                row = 0, column = 0)
                        glLinkSubsectioLbl.render()

                        imLinkDict = fsm.Data.Sec.imLinkDict(targetSubsection)

                        latexTxt = tff.Wr.TexFileUtils.fromEntryToLatexTxt(ln, imLinkDict[targetImIdx])
                        pilIm = getEntryImg(latexTxt, targetSubsection, targetImIdx)

                        shrink = 0.7
                        pilIm.thumbnail([int(pilIm.size[0] * shrink),int(pilIm.size[1] * shrink)], Image.LANCZOS)
                        img = ww.currUIImpl.UIImage(pilIm)

                        glLinkLablel = _uuicom.TOCLabelWithClick(glLinkImLablel,
                                                    image = img,
                                                    text = ln + ": " + imLinkDict[targetImIdx], 
                                                    prefix = "contentGlLinks_" + self.prefix + "_" + str(glLinkIdx),
                                                    row = 0, column = 1
                                                    )
                        glLinkLablel.subsection = targetSubsection
                        glLinkLablel.imIdx = targetImIdx
                        glLinkLablel.image = img

                        glLinkLablel.render()

                        if not fsm.Data.Sec.isVideo(self.subsection):
                            _uuicom.bindOpenOMOnThePageOfTheImage(glLinkLablel, targetSubsection, targetImIdx)
                        else:
                            _uuicom.openVideoOnThePlaceOfTheImage(glLinkLablel, targetSubsection, targetImIdx)

                        linkLabelFull = _uuicom.TOCLabelWithClick(glLinkImLablel, 
                                                    text = self.__EntryUIs.fullMove.name, 
                                                    prefix = "contentGlLinksTSubsectionFull_" + self.prefix + "_" + str(glLinkIdx),
                                                    row = 0, 
                                                    column = self.__EntryUIs.fullMove.column)
                        linkLabelFull.render()

                        linkLabelFull.subsection = ln.split("_")[0]
                        linkLabelFull.imIdx = ln.split("_")[-1]
                        _uuicom.bindChangeColorOnInAndOut(linkLabelFull)
                        linkLabelFull.rebind([ww.currUIImpl.Data.BindID.mouse1], [self.__moveLinkFull])


                        glLinksShowImages = _uuicom.TOCLabelWithClick(glLinkImLablel, 
                                                        text = self.__EntryUIs.linkImages.name, 
                                                        prefix = "contentGlLinksOfImages_" + self.prefix + "_" + str(glLinkIdx),
                                                        row = 0, 
                                                        column = self.__EntryUIs.linkImages.column)
                        glLinksShowImages.imIdx = ln.split("_")[-1]
                        glLinksShowImages.subsection = ln.split("_")[0]
                        glLinksShowImages.clicked = False
                        _uuicom.bindChangeColorOnInAndOut(glLinksShowImages)

                        renderData = {
                            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 1, "columnspan" : 100},
                            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
                        }
                        imagesFrame = ww.currUIImpl.Frame(prefix = "contentGlLinksOfImages_" + self.prefix + "_" + str(glLinkIdx),
                                            name = "linkImagesFrame", 
                                            rootWidget = glLinkImLablel,
                                            renderData = renderData,
                                            padding = [20, 0, 0, 0])
                        glLinksShowImages.rebind([ww.currUIImpl.Data.BindID.mouse1], 
                                             [lambda e, f= imagesFrame, * args: self.__showLinkImages(e, f)])
                        glLinksShowImages.render()

                        linkLabelDelete = _uuicom.TOCLabelWithClick(glLinkImLablel, 
                                                    text = self.__EntryUIs.delete.name, 
                                                    prefix = "contentGlLinksTSubsectionDel_" + self.prefix + "_" + str(glLinkIdx),
                                                    row = 0,
                                                    column = self.__EntryUIs.delete.column)
                        linkLabelDelete.render()
                        
                        linkLabelDelete.targetSubssection = ln.split("_")[0]
                        linkLabelDelete.sourceSubssection = self.subsection
                        linkLabelDelete.targetImIdx = ln.split("_")[-1]
                        linkLabelDelete.sourceImIdx = self.imIdx

                        linkLabelDelete.rebind([ww.currUIImpl.Data.BindID.mouse1], [self.__delGlLinkCmd])

                        _uuicom.bindChangeColorOnInAndOut(linkLabelDelete)

                        tarProofExists = False
                        tarExImDict = fsm.Data.Sec.extraImagesDict(ln.split("_")[0])

                        if ln.split("_")[-1] in list(tarExImDict.keys()):
                            tarExImNames = tarExImDict[ln.split("_")[-1]]
                            tarProofExists = len([i for i in tarExImNames if "proof" in i.lower()]) != 0
                        
                        if tarProofExists:
                            tarOpenProofsUIEntry = _uuicom.TOCLabelWithClick(glLinkImLablel, 
                                    text = self.__EntryUIs.proof.name, 
                                    prefix = "contentGlLinksTSubsectionProof_" + self.prefix + "_" + str(glLinkIdx),
                                    row = 0, 
                                    column = 5)
                            tarOpenProofsUIEntry.changeColor("brown")

                            tarOpenProofsUIEntry.imIdx = ln.split("_")[1]
                            tarOpenProofsUIEntry.subsection = ln.split("_")[0]
                            tarOpenProofsUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                                        [self.__openProofsMenu])
                            _uuicom.bindChangeColorOnInAndOut(tarOpenProofsUIEntry, shouldBeBrown = True)

                            tarOpenProofsUIEntry.render()

                    elif "http" in lk:
                        # NOTE: should be a frame here!
                        glLinkImLablel = _uuicom.TOCLabelWithClick(
                                                self, 
                                                prefix = "contentWebLinksImLabelIntroFr_" + self.prefix + "_" + str(glLinkIdx),
                                                padding = [60, 0, 0, 0],
                                                row = glLinkIdx + 1, column = 0)
                        glLinkImLablel.render()

                        glLinkSubsectioLbl = _uuicom.TOCLabelWithClick(glLinkImLablel, 
                                                text = "web: ", 
                                                padding = [90, 0, 0, 0],
                                                prefix = "contentGlLinksTSubsection_" + self.prefix + "_" + str(glLinkIdx),
                                                row = glLinkIdx + 1, column = 0)
                        glLinkSubsectioLbl.render()

                        latexTxt = tff.Wr.TexFileUtils.formatEntrytext(ln)
                        currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                        linkFilepath = _upan.Paths.Screenshot.Images.getWebLinkImageAbs(currBookPath,
                                                                        self.subsection,
                                                                        self.imIdx,
                                                                        ln)

                        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(linkFilepath):
                            pilIm = Image.open(linkFilepath)
                        else:
                            pilIm = tff.Wr.TexFileUtils.fromTexToImage(latexTxt, linkFilepath) 

                        shrink = 0.7
                        pilIm.thumbnail([int(pilIm.size[0] * shrink),int(pilIm.size[1] * shrink)], Image.LANCZOS)
                        img = ww.currUIImpl.UIImage(pilIm)

                        glLinkLablel = _uuicom.TOCLabelWithClick(glLinkImLablel,
                                                    image = img,
                                                    text = ln, 
                                                    prefix = "contentGlLinks_" + self.prefix + "_" + str(glLinkIdx),
                                                    row = glLinkIdx + 1, column = 1)
                        glLinkLablel.subsection = self.prefix
                        glLinkLablel.imIdx = self.imIdx
                        glLinkLablel.image = img

                        glLinkLablel.render()

                        glLinkLablel.rebind([ww.currUIImpl.Data.BindID.mouse1], \
                                            [lambda e, wl = lk, *args: self.__openWebOfTheImageCmd(e, wl)])

                        linkLabelDelete = _uuicom.TOCLabelWithClick(glLinkImLablel, 
                                                    text = "[d]", 
                                                    prefix = "contentGlLinksTSubsectionDel_" + self.prefix + "_" + str(glLinkIdx),
                                                    row = glLinkIdx + 1, column = 2)
                        linkLabelDelete.render()

                        linkLabelDelete.sourceSubssection = self.subsection
                        linkLabelDelete.sourceImIdx = self.imIdx
                        linkLabelDelete.sourceWebLinkName = ln

                        linkLabelDelete.rebind([ww.currUIImpl.Data.BindID.mouse1], [self.__delWebLinkCmd])

                        _uuicom.bindChangeColorOnInAndOut(linkLabelDelete)

                    glLinkIdx += 1

    def render(self):
        for ch in self.getChildren().copy():
            ch.destroy()
        
        self.AddLinks()

        super().render(self.renderData)
        self.entryFrame.linkFrameShown = True
    
    def hide(self):
        self.entryFrame.linkFrameShown = False
        return super().hide()


def pasteGlLinkCmd(event, *args):
    widget = event.widget
    sourceSubsection = widget.subsection
    sourceTopSection = sourceSubsection.split(".")[0]
    sourceImIdx = widget.imIdx
    targetSubsection = dt.UITemp.Link.subsection
    targetImIdx = dt.UITemp.Link.imIdx

    excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                wf.Wr.MenuManagers.ExcerciseManager)
    excerciseWidgetShown = excerciseManager.shown

    if targetSubsection != _u.Token.NotDef.str_t\
        and targetImIdx != _u.Token.NotDef.str_t:
        gm.GeneralManger.AddLink(f"{targetSubsection}.{targetImIdx}",
                                sourceSubsection,
                                sourceImIdx,
                                sourceTopSection)

    if excerciseWidgetShown:
        excerciseManager.show()

class EntryWindow_BOX(ww.currUIImpl.ScrollableBox,
                      dc.AppCurrDataAccessToken):
    class __EntryUIs:
        class __EntryUIData:
            def __init__(self, name, column) -> None:
                self.name = name
                self.column = column

        # row 1
        full = __EntryUIData("[f]", 1)
        copyLink = __EntryUIData("[cl]", 3)
        pasteLink = __EntryUIData("[pl]", 4)
        copy = __EntryUIData("[c]", 5)
        pasteAfter = __EntryUIData("[p]", 6)
        excercises = __EntryUIData("[e]", 7)

        # row 2
        showLinks = __EntryUIData("[Links]", 1)
        alwaysShow = __EntryUIData("", 2)
        changeImSize = __EntryUIData("", 3)
        retake = __EntryUIData("[Retake]", 5)
        addExtra = __EntryUIData("[Add image]", 6)
        addProof = __EntryUIData("[Add proof]", 7)
        note = __EntryUIData("[Dictionary]", 8)
        group = __EntryUIData("", 10)

        # row 2.5 
        openBookCodeProject = __EntryUIData("[code:b", 1)
        openSubsectionCodeProject = __EntryUIData(",s", 2)
        openEntryCodeProject = __EntryUIData(",e]", 3)
        shift = __EntryUIData("[Shift Up]", 4)
        entryNote = __EntryUIData("[Note]", 5)
        wikiNote = __EntryUIData("[Wiki]", 6)
        copyText = __EntryUIData("[Copy text]", 7)
        proof = __EntryUIData("[Show proof]", 8)

    class Notifyers:
        class IDs:
            rerenderAndSetMain = "_rerenderAndSetMain"
            changeHeight = "_changeHeight"
            setMain = "_setMain"

    def showLinksForEntryCmd(self, linksFrame):
        if linksFrame.wasRendered:
            linksFrame.hide()
        else:
            linksFrame.render()

        self.updateHeight()

    def __init__(self, parentWidget, prefix):
        self.subsection = None
        self.imIdx = None
        name = "_EntryWindow_BOX_"

        self.linkFrameShown = False
        self.imagesFrame = None

        self.maxHeight = 375

        self.entryManager = None

        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 4, "columnspan": 6},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.W}
        }
        extraOptions = {
            ww.Data.GeneralProperties_ID :{"width" : 350, "height" : self.maxHeight},
            ww.TkWidgets.__name__ : {}
        }
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = renderData,
                        extraOptions= extraOptions,
                        height = self.maxHeight)

    def notificationRetakeImage(self, subsection, imIdx):
        raise NotImplementedError()

    def notificationResizeImage(self, subsection, imIdx):
        raise NotImplementedError()

    def notificationlinkFullMove(self, subsection, imIdx):
        raise NotImplementedError()

    def notificationAfterImageWasCreated(self, subsection, imIdx):
        raise NotImplementedError()

    def receiveNotification(self, broadcasterType, data = None):
        if data != None:
            self.subsection = data[0]
            self.imIdx = data[1]
            self.render()
        else:
            self.render(scrollTOC = False)

    def setMain(self, subsection = None, imIdx = None):
        if subsection != None:
            self.subsection = subsection
        if imIdx != None:
            self.imIdx = imIdx 
        self.notify(TOC_BOX, data = {EntryWindow_BOX.Notifyers.IDs.setMain: [self.subsection, self.imIdx]})
  
    def rerenderAndSetMainTOC(self, shouldScroll = True):
        self.notify(TOC_BOX, 
                    data = {EntryWindow_BOX.Notifyers.IDs.rerenderAndSetMain: [self.subsection, self.imIdx, shouldScroll]})

    def updateHeight(self, scrollTOC = True, updateSecondaryFrame = False):
        newHeight = 10
        for ch in self.scrollable_frame.getChildren():
           newHeight += ch.getHeight()

        newHeight = min(newHeight, self.maxHeight)
        self.setCanvasHeight(min(newHeight, self.maxHeight))

        if scrollTOC:
            self.notify(TOC_BOX, 
                        data = {EntryWindow_BOX.Notifyers.IDs.changeHeight: [newHeight, self.subsection, self.imIdx, True]})
        else:
            self.notify(TOC_BOX, 
                        data = {EntryWindow_BOX.Notifyers.IDs.changeHeight: [newHeight, self.subsection, self.imIdx, False]})

        import UI.widgets_collection.pdfReader.pdfReader as pdfw
        if updateSecondaryFrame:
            self.notify(pdfw.SecondaryImagesFrame, data = [True])
        else:
            self.notify(pdfw.SecondaryImagesFrame)


    def scrollToImage(self, imIdx, eImIdx = None):
        if self.imagesFrame != None:
            for ch in self.imagesFrame.getChildren():
                if (str(ch.imIdx) == str(imIdx)) and (str(ch.eImIdx) == str(eImIdx)):
                    self.scrollIntoView(None, ch)

                    break
        else:
            _u.log.autolog("We should not be here.")


    def scrollIntoView(self, event, widget = None):
        posy = 0

        if widget == None:
            pwidget = event.widget
        else:
            pwidget = widget

        self.update()
        pwidget.update()

        while self.getParent().name.lower() not in pwidget.name.lower():
            if pwidget == None:
                break
            posy += pwidget.getYCoord()
            pwidget = pwidget.getParent()

        pos = posy - self.yPosition()
        height = self.getFrameHeight()
        self.moveY((pos / height))

    def render(self, scrollTOC = True):
        self.scrollable_frame.removeAllChildren()
        # for ch in self.scrollable_frame.getChildren().copy():
        #     ch.destroy()

        if (self.subsection != None) and (str(fsm.Data.Book.entryImOpenInTOC_UI) != _u.Token.NotDef.str_t):
            self.__AddEntryWidget(self.imIdx, self.subsection, self.scrollable_frame)

        super().render(self.renderData)
        self.updateHeight(scrollTOC)

    def pasteGlLinkCmd(self, event, *args):
        pasteGlLinkCmd(event, *args)
        
        self.render()

    def __AddEntryImages(self, rootFrame, padding):
        nameId =_upan.Names.Entry.getEntryNameID(self.subsection, self.imIdx)
        self.imagesFrame = _uuicom.TOCFrame(rootFrame,
                                prefix = "contentFr_" + nameId,
                                padding = padding,
                                row = int(self.imIdx) + 3, column = 0, columnspan = 100)

        uiResizeEntryIdx = fsm.Data.Sec.imageUIResize(self.subsection)

        # if uiResizeEntryIdx.get(self.imIdx) != None:
        #     resizeFactor = float(uiResizeEntryIdx[self.imIdx])
        # else:
        #     resizeFactor = 1.0

        entryImagesFactory = _uuicom.EntryImagesFactory(self.subsection, self.imIdx)
        imLabel = entryImagesFactory.produceEntryMainImageWidget(self.imagesFrame,
                                                       imPadLeft = 120,
                                                       resizeFactor = 1.0)

        imLabel.render()

        def skipProofs(subsection, imIdx, i):
            if dt.AppState.ShowProofs.getData(self.appCurrDataAccessToken):
                return False
            else:
                return "proof" in fsm.Data.Sec.extraImagesDict(subsection)[imIdx][i].lower()

        exImLabels = entryImagesFactory.produceEntryExtraImagesWidgets(rootLabel = self.imagesFrame,
                                                       skippConditionFn = skipProofs,
                                                       entryWidget = self)
        for l in exImLabels:
            l.render()

    def __AddEntryWidget(self, imIdx, subsection, frame):
        if type(fsm.Data.Sec.leadingEntry(subsection)) != dict:
            return

        if fsm.Data.Sec.leadingEntry(subsection).get(imIdx) != None:
            leadingEntry = fsm.Data.Sec.leadingEntry(subsection)[imIdx]

            if fsm.Data.Sec.showSubentries(subsection).get(leadingEntry) != None:
                showSubentries = fsm.Data.Sec.showSubentries(subsection)[leadingEntry]
            else:
                showSubentries = True

            if (showSubentries != _u.Token.NotDef.str_t) and (not showSubentries):
                return
        
        entryWidgetFactory = _uuicom.EntryWidgetFactoryEntryWindow(subsection, imIdx, 0, 0)
        entryWidgetFactory.produceEntryWidgetsForFrame(frame)
        self.entryManager = entryWidgetFactory.entryFrameManager
        return


class TOC_BOX(ww.currUIImpl.ScrollableBox,
              dc.AppCurrDataAccessToken):
    # this data structure is used to store the
    # entry image widget that is turned into ETR for update
    class entryAsETR:
        subsection = _u.Token.NotDef.str_t
        imIdx = _u.Token.NotDef.str_t
        widget = None

        upddatedTextSubsection = _u.Token.NotDef.str_t
        upddatedTextImIdx = _u.Token.NotDef.str_t

        def reset(self):
            self.subsection = _u.Token.NotDef.str_t
            self.imIdx = _u.Token.NotDef.str_t
            self.widget = None

    class extraImAsETR:
        subsection = _u.Token.NotDef.str_t
        imIdx = _u.Token.NotDef.str_t
        eImIdx = _u.Token.NotDef.str_t
        widget = None

        upddatedText = _u.Token.NotDef.str_t
        upddatedTextExtraImIdx = _u.Token.NotDef.str_t

        def reset(self):
            self.subsection = _u.Token.NotDef.str_t
            self.imIdx = _u.Token.NotDef.str_t
            self.eImIdx = _u.Token.NotDef.str_t
            self.widget = None

    class entryTextOnlyAsETR:
        subsection = _u.Token.NotDef.str_t
        imIdx = _u.Token.NotDef.str_t
        widget = None

        def reset(self):
            self.subsection = _u.Token.NotDef.str_t
            self.imIdx = _u.Token.NotDef.str_t
            self.widget = None

    class subsectionAsETR:
        subsection = _u.Token.NotDef.str_t
        widget = None

        def reset(self):
            self.subsection = _u.Token.NotDef.str_t
            self.widget = None

    class groupAsETR:
        subsection = _u.Token.NotDef.str_t
        group = _u.Token.NotDef.str_t
        widget = None

        def reset(self):
            self.subsection = _u.Token.NotDef.str_t
            self.group = _u.Token.NotDef.str_t
            self.widget = None


    def __init__(self, parentWidget, prefix, windth = 700, height = 300, 
                 showAll = False, makeScrollable = True, shouldScroll = True,
                 showLinks = False):
        self.subsectionWidgetManagers = {}

        # used to filter toc data when the search is performed
        self.filterToken = ""
        self.searchSubsectionsText = False
        self.showAll = None
        self.shouldScroll = None
        self.subsectionClicked = _u.Token.NotDef.str_t
        self.entryClicked = _u.Token.NotDef.str_t

        self.showSubsectionsForTopSection = {}
        self.parent = None
        self.showLinks = None
        self.showLinksForSubsections = []
        self.linksOpenImage = set()
        self.linksOpenImageWidgets = {}

        self.entryCopySubsection = None
        self.showImagesLabels = {}

        self.currentEntrySubsection = None
        self.currentEntryImIdx = None

        self.updatedWidget = None

        self.showLinksForCurrWidget = True

        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 3, "columnspan" : 6, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.W}
        }
        name = "_showCurrScreenshotLocation_text"

        self.parent = parentWidget
        self.showAll = showAll
        self.showLinks = showLinks

        self.entryAsETR = TOC_BOX.entryAsETR()
        self.extraImAsETR = TOC_BOX.extraImAsETR()
        self.entryTextOnlyAsETR = TOC_BOX.entryTextOnlyAsETR()
        self.subsectionAsETR = TOC_BOX.entryAsETR()

        self.subsectionClicked = fsm.Data.Book.subsectionOpenInTOC_UI
        self.entryClicked = fsm.Data.Book.entryImOpenInTOC_UI
        self.shouldScroll = shouldScroll

        tsList = fsm.Wr.BookInfoStructure.getTopSectionsList()

        if tsList != _u.Token.NotDef.list_t:
            for ts in tsList:
                if self.showAll:
                    self.showSubsectionsForTopSection[ts] = True
                else:
                    self.showSubsectionsForTopSection[ts] = bool(int(fsm.Data.Book.sections[ts]["showSubsections"]))

        super().__init__(prefix,
                        name,
                        parentWidget,
                        renderData = data,
                        height = height,
                        width = windth,
                        makeScrollable = makeScrollable)

    def renderWithoutScroll(self):
        self.__renderWithoutScroll()

    def renderWithScrollAfter(self):
        self.__renderWithScrollAfter()

    def scrollToEntry(self, subsection, imIdx):
        if "." not in subsection:
            return

        # move toc to
        self.subsectionClicked = subsection
        self.showSubsectionsForTopSection[subsection.split(".")[0]] = True
        self.entryClicked = imIdx

        # update to show the group when we show the entry
        groupsList = fsm.Data.Sec.imagesGroupsList(self.subsectionClicked)
        imGroupDict = fsm.Data.Sec.imagesGroupDict(self.subsectionClicked)
        groupsListKeys = groupsList.keys()

        if self.entryClicked in list(imGroupDict.keys()):
            idx = imGroupDict[self.entryClicked]
        else:
            return

        if idx != _u.Token.NotDef.str_t:
            groupName = list(groupsListKeys)[idx]
            groupsList[groupName] = True
            fsm.Data.Sec.imagesGroupsList(self.subsectionClicked, groupsList)

    def scrollIntoView(self, event, widget = None):
        if not self.shouldScroll:
            return

        posy = 0


        if widget == None:
            pwidget = event.widget
        else:
            pwidget = widget

        self.update()
        pwidget.update()

        if widget == None:
            _u.log.autolog("Cant scroll to widget since it is None.")
            return

        widget.update()

        while pwidget != self.parent:
            if pwidget == None:
                break
            posy += pwidget.getYCoord()
            pwidget = pwidget.getParent()
            pwidget.update()

        posy = 0

        if widget == None:
            pwidget = event.widget
        else:
            pwidget = widget

        while pwidget != self.parent:
            if pwidget == None:
                break
            posy += pwidget.getYCoord()
            pwidget = pwidget.getParent()
            pwidget.update()

        pos = posy - self.yPosition()
        height = self.getFrameHeight()
        self.moveY((pos / height))
    
    def __renderWithScrollAfter(self):
        entryForFullMove = str(fsm.Data.Book.entryImOpenInTOC_UI)

        self.shouldScroll = False
        self.render()
        self.shouldScroll = True

        fsm.Data.Book.entryImOpenInTOC_UI = entryForFullMove
        if str(fsm.Data.Book.entryImOpenInTOC_UI) != _u.Token.NotDef.str_t:
            self.onFullEntryMove()

    def __renderWithoutScroll(self):
        self.shouldScroll = False
        self.render()
        self.shouldScroll = True

    def showLinksForEntryCmd(self, event, subsection = None, imIdx = None,
                             dontHide = False, *args):
        if event != None:
            widget = event.widget
            subsection = widget.subsection
            imIdx =  widget.imIdx
            dontHide = self.showLinksForCurrWidget
            self.showLinksForCurrWidget = not self.showLinksForCurrWidget
        else:
            subsection = subsection
            imIdx = imIdx

        liskShpowId = subsection + "_" + imIdx

        linkShouldBePresent = True

        if not dontHide:
            for l in self.showLinksForSubsections:
                if liskShpowId in l:
                    self.showLinksForSubsections = []
                    self.linksOpenImage.clear()

                    for k in self.linksOpenImageWidgets.keys():
                        im = self.linksOpenImageWidgets[k]
                        im.hide()

                    self.linksOpenImageWidgets = {}

                    linkShouldBePresent = False
                break

        if linkShouldBePresent:
            imGlobalLinksDict = fsm.Data.Sec.imGlobalLinksDict(subsection)
            if type(imGlobalLinksDict) == dict:
                if imIdx in list(imGlobalLinksDict.keys()):
                    glLinks:dict = imGlobalLinksDict[imIdx]

                    for ln in glLinks:
                        if not self.showLinks:
                            self.showLinksForSubsections.append(subsection + "_" + imIdx + "_" + ln)

                    self.showLinksForSubsections.append(liskShpowId)

        self.__renderWithoutScroll()
        self.scrollToEntry(subsection, imIdx)

    def onMainLatexImageUpdate(self, subsection, imIdx):
        etm = self.subsectionWidgetManagers[subsection].entriesWidgetManagers[imIdx]
        etm.updateEntryImage()

    def onRetakeAfter(self, subsection, imIdx, eImidx = _u.Token.NotDef.str_t):
        etm = self.subsectionWidgetManagers[subsection].entriesWidgetManagers[imIdx]

        if eImidx == _u.Token.NotDef.str_t:
            etm.updateMainImage()
        else:
            etm.updateExtraImage(eImidx)

    def onImageResize(self, subsection, imIdx, eImIdx):
        etm = self.subsectionWidgetManagers[subsection].entriesWidgetManagers[imIdx]
        if eImIdx == None:
            etm.updateMainImage()
        else:
            etm.updateExtraImage(eImIdx)
        etm.updateResizeEtrText()

    def onAlwaysShowChange(self, subsection, imIdx):
        etm = self.subsectionWidgetManagers[subsection].entriesWidgetManagers[imIdx]
        currSubsection = fsm.Data.Book.subsectionOpenInTOC_UI
        currEntryIdx = fsm.Data.Book.entryImOpenInTOC_UI

        if etm.alwaysShow():
            if ((subsection != currSubsection) or (imIdx != currEntryIdx)) or (dt.UITemp.Layout.noMainEntryShown):
                etm.showImages()
        else:
            etm.hideImages()
        
        if (subsection == currSubsection) or (imIdx == currEntryIdx):
            for ch in etm.rowFrame2.getChildren():
                ch.render()

        etmMain = \
            self.subsectionWidgetManagers[fsm.Data.Book.subsectionOpenInTOC_UI].entriesWidgetManagers[fsm.Data.Book.entryImOpenInTOC_UI]
        self.shouldScroll = True
        self.scrollIntoView(None, etmMain.entryFrame)

    def onFullEntryMove(self):
        currSubsection = fsm.Data.Book.subsectionOpenInTOC_UI
        currEntryIdx = fsm.Data.Book.entryImOpenInTOC_UI

        shownEntryFrame = None

        if currSubsection == _u.Token.NotDef.str_t:
            return
        if self.subsectionWidgetManagers.get(currSubsection) == None:
            return

        for imIdx, efm in self.subsectionWidgetManagers[currSubsection].entriesWidgetManagers.items():
            if imIdx != currEntryIdx:
                if (fsm.Data.Sec.tocWImageDict(currSubsection)[imIdx] == "1"):
                    efm.changeFullMoveColor(True)

                    if not efm.imagesShown:
                        efm.showImages()

                    efm.hideRow2()
                    efm.setFullImageLabelNotClicked()
                else:
                    if efm.imagesShown:
                        efm.hideImages()
                    efm.changeFullMoveColor(True)
                    efm.hideRow2()
            else:
                efm.showRow2()

                if dt.UITemp.Layout.noMainEntryShown:
                    efm.showImages()
                else:
                    if efm.imagesShown:
                        efm.hideImages()

                efm.changeFullMoveColor(False)
                shownEntryFrame = efm.entryFrame

        if shownEntryFrame != None:
            #NOTE: this seems to fix an issue when the scrolling happens before
            #      canvas update and the widget is not seen
            def th(tocWidget, frame):
                tocWidget.shouldScroll = True
                tocWidget.scrollIntoView(None, frame)
            t = Thread(target = th, args = [self, shownEntryFrame])
            t.start()

    def onAddExtraImage(self, subsection, mainImIdx, extraImIdx):
        etm = self.subsectionWidgetManagers[subsection].entriesWidgetManagers[mainImIdx]

        def th(tocWidget, frame):
            tocWidget.shouldScroll = True
            tocWidget.scrollIntoView(None, frame)

        t = Thread(target = th, args = [self, etm.entryFrame])
        t.start()
        # if eImFrame != None:
        #     self.scrollIntoView(None, eImFrame)

    def pasteGlLinkCmd(self, event, *args):
        pasteGlLinkCmd(event, *args)
        self.notify(EntryWindow_BOX)

    def onSetLeadingEntry(self, subsection, imIdx):
        fsm.Data.Book.subsectionOpenInTOC_UI = subsection
        fsm.Data.Book.entryImOpenInTOC_UI = imIdx
        self.__renderWithScrollAfter()

    def onShowSubentries(self, subsection, imIdx):
        fsm.Data.Book.subsectionOpenInTOC_UI = subsection
        fsm.Data.Book.entryImOpenInTOC_UI = imIdx
        self.__renderWithScrollAfter()

    def onGroupChange(self, subsection, imIdx):
        fsm.Data.Book.subsectionOpenInTOC_UI = subsection
        fsm.Data.Book.entryImOpenInTOC_UI = imIdx
        self.__renderWithScrollAfter()

    def onPaste(self, subsection, imIdx):
        if None in [dt.UITemp.Copy.subsection, dt.UITemp.Copy.imIdx] or\
            _u.Token.NotDef.str_t in [dt.UITemp.Copy.subsection, dt.UITemp.Copy.imIdx]:
            _u.log.autolog("Did not paste entry. The copy data is not correct.")
            return

        fsm.Wr.SectionInfoStructure.insertEntryAfterIdx(dt.UITemp.Copy.subsection,
                                                        dt.UITemp.Copy.imIdx,
                                                        subsection,
                                                        imIdx,
                                                        dt.UITemp.Copy.cut,
                                                        shouldAsk = True)
        #TODO: we should optimise this
        self.render()

    def onExtraImDelete(self, subsection, imIdx, eImIdx):
        etm = self.subsectionWidgetManagers[subsection].entriesWidgetManagers[imIdx]
        etm.deleteExtraImage(eImIdx)

    def onExtraImMove(self, subsection, imIdx, eImIdx, moveUp:bool):
        etm = self.subsectionWidgetManagers[subsection].entriesWidgetManagers[imIdx]
        eImFrame = etm.moveExtraIm(eImIdx, moveUp)

        # if eImFrame != None:
        #     self.shouldScroll = True
        #     self.scrollIntoView(None, eImFrame)

    def onEntryShift(self, subsection, imIdx):
        etm = self.subsectionWidgetManagers[subsection].entriesWidgetManagers.pop(imIdx)
        frame = etm.entryFrame.rootWidget
        etm.entryFrame.destroy()

        newIdx = str(int(imIdx) + 1)

        if fsm.Data.Book.entryImOpenInTOC_UI == imIdx:
            fsm.Data.Book.entryImOpenInTOC_UI = newIdx

        entryWidgetFactory = _uuicom.EntryWidgetFactoryTOC(subsection, newIdx, 0, 0)
        entryWidgetFactory.produceEntryWidgetsForFrame(frame)
        self.self.subsectionWidgetManagers[subsection].entriesWidgetManagers[newIdx] = entryWidgetFactory.entryFrameManager
        etmNew = self.self.subsectionWidgetManagers[subsection].entriesWidgetManagers[newIdx]


        def th(tocWidget, frame, subsection, newidx):
            tocWidget.shouldScroll = True
            if fsm.Data.Book.entryImOpenInTOC_UI == newIdx:
                for w in wd.Data.Reactors.entryChangeReactors.values():
                    if "onFullEntryMove" in dir(w):
                        w.onFullEntryMove()
            else:
                tocWidget.scrollIntoView(None, frame)


        t = Thread(target = th, args = [self, etmNew.entryFrame, subsection, newIdx])
        t.start()

    def onEntryDelete(self, subsection, imIdx):
        self.__renderWithoutScroll()

    def onRebuildSubsectionLatex(self, subsection):
        self.render()

    def onSubsectionShowHide(self, subsection):
        subsectionsHidden:list = fsm.Data.Book.subsectionsHiddenInTOC_UI

        if subsection not in subsectionsHidden:
            # show subsections
            subsections:list = fsm.Wr.BookInfoStructure.getSubsectionsList(subsection)
            
            for i in range(len(subsections)):
                self.addSubsectionEntry(subsections[i], i)
            return

        # hide subsection
        for subsec, m in self.subsectionWidgetManagers.copy().items():
            for subsecHidden in subsectionsHidden:
                if len(subsec) > len(subsecHidden):
                    if subsec[:len(subsecHidden)] == subsecHidden:
                        self.__removeSubsection(subsec)

        self.subsectionWidgetManagers[subsection].removeAllSubsections()

    def onSubsectionOpen(self, subsection):
        for subsec, m in self.subsectionWidgetManagers.items():
            if len(subsec.split(".")) != 1:
                m.closeSubsection()

        manager = self.subsectionWidgetManagers[subsection]
        manager.entriesFrame.render()

        self.subsectionWidgetManagers[subsection].addEntryWidgetsForSubsection()
        
        self.shouldScroll = True
        self.scrollIntoView(None, manager.subsectionFrame)

    def onTopSectionOpen(self, topSection):
        self.render()
        manager = self.subsectionWidgetManagers[topSection]
        self.shouldScroll = True
        self.scrollIntoView(None, manager.subsectionFrame)

    def __removeSubsection(self, subsection):
        manager = self.subsectionWidgetManagers.pop(subsection)
        manager.subsectionFrame.hide()
        manager.subsectionFrame.destroy()

    def onTopSectionClose(self, topSection):
        for k,v in self.subsectionWidgetManagers.copy().items():
            manTopSection = k.split(".")[0]
            if (manTopSection == topSection) and (topSection != k):
                self.__removeSubsection(k)

    def onSubsectionClose(self, subsection):
        manager = self.subsectionWidgetManagers[subsection]
        manager.closeSubsection()

    def AddEntryWidget(self, imIdx, subsection, frame):
        if subsection != fsm.Data.Book.subsectionOpenInTOC_UI:
            return

        if str(imIdx) == _u.Token.NotDef.str_t:
            return

        if fsm.Data.Sec.leadingEntry(subsection).get(imIdx) != None:
            leadingEntry = fsm.Data.Sec.leadingEntry(subsection)[imIdx]

            if fsm.Data.Sec.showSubentries(subsection).get(leadingEntry) != None:
                showSubentries = fsm.Data.Sec.showSubentries(subsection)[leadingEntry]
            else:
                showSubentries = True

            if (showSubentries != _u.Token.NotDef.str_t) and (not showSubentries):
                return
             
        self.subsectionWidgetManagers[subsection].addEntryWidget(imIdx)
        return

    def addSubsectionWidgetsManager(self, subsection, row, parentWidget, subsectionFactory):
        subsectionFactory.produceSubsectionWidgets(parentWidget, row)
        self.subsectionWidgetManagers[subsection] = subsectionFactory.widgetManager

    def openSubsection(self, subsection):
        self.subsectionWidgetManagers[subsection].openSubsection()
    
    def openEntries(self, subsection, filterText = ""):
        self.subsectionWidgetManagers[subsection].addEntryWidgetsForSubsection(filterText)

    def render(self, shouldScroll = False):
        for sm in self.subsectionWidgetManagers.values():
            for w in sm.entriesWidgetManagers.values():
                w.entryFrame.destroy()

        self.subsectionWidgetManagers = {}

        wd.Data.Reactors.entryChangeReactors[self.name] = self
        wd.Data.Reactors.subsectionChangeReactors[self.name] = self
        # import traceback
        
        # for line in traceback.format_stack():
        #     print(line.strip())

        if self.showAll:
            self.showLinksForSubsections = []

        self.shouldScroll = shouldScroll

        # for the search toc we show material for all top sections
        if self.showAll:
            self.showSubsectionsForTopSection = {}
            tsList = fsm.Wr.BookInfoStructure.getTopSectionsList()

            if tsList != _u.Token.NotDef.list_t:
                for ts in tsList:
                    self.showSubsectionsForTopSection[ts] = True

        for child in self.getChildren().copy():
            child.destroy()

        if self.showSubsectionsForTopSection == {}:
            tsList = fsm.Wr.BookInfoStructure.getTopSectionsList()

            if tsList != _u.Token.NotDef.list_t:
                for ts in tsList:
                    self.showSubsectionsForTopSection[ts] = bool(int(fsm.Data.Book.sections[ts]["showSubsections"]))

        self.populateTOC()

        super().render(self.renderData)

        if fsm.Data.Book.entryImOpenInTOC_UI != _u.Token.NotDef.str_t:
            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onFullEntryMove" in dir(w):
                    w.onFullEntryMove()
        return

class MainRoot(ww.currUIImpl.RootWidget):

    def __init__(self, width, height):
        super().__init__(width, height, self.__bindCmd)
    
    def __bindCmd(self):
        def __largerEntry():
            mainMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                            wf.Wr.MenuManagers.MathMenuManager)
            dt.UITemp.Layout.noMainEntryShown = False
            mainMenuManager.changeLowerSubframeHeight(600)
        
        def __smallerEntry():
            mainMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                            wf.Wr.MenuManagers.MathMenuManager)
            dt.UITemp.Layout.noMainEntryShown = False
            mainMenuManager.changeLowerSubframeHeight(375)
        def __noEntry():
            mainMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                            wf.Wr.MenuManagers.MathMenuManager)
            dt.UITemp.Layout.noMainEntryShown = True
            mainMenuManager.changeLowerSubframeHeight(0)
        return [ww.currUIImpl.Data.BindID.Keys.cmdone, 
                ww.currUIImpl.Data.BindID.Keys.cmdtwo,
                ww.currUIImpl.Data.BindID.Keys.cmdshh], \
               [lambda *args: __largerEntry(), 
                lambda *args: __smallerEntry(),
                lambda *args: __noEntry()]