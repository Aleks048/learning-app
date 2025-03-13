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
        self.setData(tocWImageDict[self.imIdx])
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
        for ch in self.scrollable_frame.getChildren().copy():
            ch.destroy()

        if (self.subsection != None):
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
        if fsm.Data.Sec.leadingEntry(subsection).get(imIdx) != None:
            leadingEntry = fsm.Data.Sec.leadingEntry(subsection)[imIdx]

            if fsm.Data.Sec.showSubentries(subsection).get(leadingEntry) != None:
                showSubentries = fsm.Data.Sec.showSubentries(subsection)[leadingEntry]
            else:
                showSubentries = True

            if (showSubentries != _u.Token.NotDef.str_t) and (not showSubentries):
                return
        
        entryWidgetFactory = _uuicom.EntryWidgetFactoryEntryWindow(subsection, imIdx, frame, self, 0, 0)
        entryWidgetFactory.produceEntryWidgetsForFrame()
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
        self.entryWidgetManagers = {}

        # used to filter toc data when the search is performed
        self.filterToken = ""
        self.searchSubsectionsText = False
        self.showAll = None
        self.shouldScroll = None

        self.subsectionWidgetFrames = {}

        self.subsectionClicked = _u.Token.NotDef.str_t
        self.entryClicked = _u.Token.NotDef.str_t
        self.secondEntryClicked = None

        self.renderFromTOCWindow = False

        self.secondEntryClickedImIdx = _u.Token.NotDef.str_t
        self.secondEntrySubsectionClicked = _u.Token.NotDef.str_t

        self.widgetToScrollTo = None

        self.currEntryWidget = None
        self.currSubsectionWidget = None

        self.showSubsectionsForTopSection = {}
        self.displayedImages = []
        self.parent = None
        self.openedMainImg = None

        self.showLinks = None
        self.showLinksForSubsections = []
        self.linksOpenImage = set()
        self.linksOpenImageWidgets = {}

        self.entryCopySubsection = None
        self.entryCopyImIdx = None

        self.cutEntry = False

        self.subsectionContentLabels = []

        self.currSecondRowLabels = []
        self.linkFrames = []

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
        etm = self.entryWidgetManagers[subsection + "_" + imIdx]
        etm.updateEntryImage()

    def onRetakeAfter(self, subsection, imIdx, eImidx = _u.Token.NotDef.str_t):
        etm = self.entryWidgetManagers[subsection + "_" + imIdx]

        if eImidx == _u.Token.NotDef.str_t:
            etm.updateMainImage()
        else:
            etm.updateExtraImage(eImidx)


    def onImageResize(self, subsection, imIdx, eImIdx):
        etm = self.entryWidgetManagers[subsection + "_" + imIdx]
        if eImIdx == None:
            etm.updateMainImage()
        else:
            etm.updateExtraImage(eImIdx)
        etm.updateResizeEtrText()

    def onAlwaysShowChange(self, subsection, imIdx):
        etm = self.entryWidgetManagers[subsection + "_" + imIdx]
        if etm.alwaysShow():
            etm.showImages()
        else:
            etm.hideImages()
        
        for ch in etm.rowFrame2.getChildren():
            ch.render()

        etmMain = self.entryWidgetManagers[fsm.Data.Book.subsectionOpenInTOC_UI + 
                                           "_" + fsm.Data.Book.entryImOpenInTOC_UI]
        self.shouldScroll = True
        self.scrollIntoView(None, etmMain.entryFrame)

    def onFullEntryMove(self):
        currSubsection = fsm.Data.Book.subsectionOpenInTOC_UI
        currEntryIdx = fsm.Data.Book.entryImOpenInTOC_UI
        hash = currSubsection + "_" + currEntryIdx

        shownEntryFrame = None

        for k, efm in self.entryWidgetManagers.items():
            subsection = k.split("_")[0]
            imIdx = k.split("_")[1]
            if k != hash:
                if (fsm.Data.Sec.tocWImageDict(subsection)[imIdx] == "1"):
                    efm.changeFullMoveColor(True)
                    efm.setFullImageLabelNotClicked()
                else:
                    if efm.imagesShown:
                        efm.hideImages()
                        efm.changeFullMoveColor(True)
            else:
                efm.showImages()
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
        etm = self.entryWidgetManagers[subsection + "_" + mainImIdx]
        eImFrame = etm.addExtraImIdx(extraImIdx)
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
        etm = self.entryWidgetManagers[subsection + "_" + imIdx]
        etm.deleteExtraImage(eImIdx)

    def onExtraImMove(self, subsection, imIdx, eImIdx, moveUp:bool):
        etm = self.entryWidgetManagers[subsection + "_" + imIdx]
        eImFrame = etm.moveExtraIm(eImIdx, moveUp)

        # if eImFrame != None:
        #     self.shouldScroll = True
        #     self.scrollIntoView(None, eImFrame)

    def onEntryShift(self, subsection, imIdx):

        etm = self.entryWidgetManagers.pop(subsection + "_" + imIdx)
        frame = etm.entryFrame.rootWidget
        etm.entryFrame.destroy()

        newIdx = str(int(imIdx) + 1)

        if fsm.Data.Book.entryImOpenInTOC_UI == imIdx:
            fsm.Data.Book.entryImOpenInTOC_UI = newIdx

        entryWidgetFactory = _uuicom.EntryWidgetFactoryTOC(subsection, newIdx, frame, self, 0, 0)
        self.entryWidgetManagers[subsection + "_" + newIdx] = entryWidgetFactory.entryFrameManager
        etmNew = self.entryWidgetManagers[subsection + "_" + newIdx]

        entryWidgetFactory.produceEntryWidgetsForFrame()

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
        self.widgetToScrollTo = None
        self.__renderWithoutScroll()

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

                
        entryWidgetFactory = _uuicom.EntryWidgetFactoryTOC(subsection, imIdx, frame, self, 0, 0)
        self.entryWidgetManagers[subsection + "_" + imIdx] = entryWidgetFactory.entryFrameManager
        entryWidgetFactory.produceEntryWidgetsForFrame()
        return

    def receiveNotification(self, broadcasterType, data = None, entryClicked = None):
        import UI.widgets_collection.main.math.UI_layouts.mainLayout as mui
        if (EntryWindow_BOX in broadcasterType.__bases__) or (EntryWindow_BOX == broadcasterType):
            if data.get(EntryWindow_BOX.Notifyers.IDs.changeHeight) != None:
                data = data.get(EntryWindow_BOX.Notifyers.IDs.changeHeight)

                entryWidgetHeight = data[0]
                self.setCanvasHeight(680 - entryWidgetHeight)
                if data[1] != None:
                    if data[3]:
                        self.shouldScroll = True
                        # self.scrollIntoView(None, self.showImagesLabels[str(data[1]) + str(data[2])])
                        self.shouldScroll = False
            elif data.get(EntryWindow_BOX.Notifyers.IDs.rerenderAndSetMain) != None:
                data = data.get(EntryWindow_BOX.Notifyers.IDs.rerenderAndSetMain)
                if data[2]:
                    self.render()
                    # self.showImagesLabels[str(data[0]) + str(data[1])].generateEvent(ww.currUIImpl.Data.BindID.mouse1)
            elif data.get(EntryWindow_BOX.Notifyers.IDs.setMain) != None:
                data = data.get(EntryWindow_BOX.Notifyers.IDs.setMain)
                # self.showImagesLabels[str(data[0]) + str(data[1])].generateEvent(ww.currUIImpl.Data.BindID.mouse1)
        elif broadcasterType == mui.ExitApp_BTN:
            tsList = fsm.Wr.BookInfoStructure.getTopSectionsList()

            sections = fsm.Data.Book.sections

            for ts in tsList:
                if ts == _u.Token.NotDef.str_t:
                    return

                sections[ts]["showSubsections"] = str(int(self.showSubsectionsForTopSection[ts]))

            fsm.Data.Book.sections = sections
        elif broadcasterType == mui.ImageGeneration_BTN:
            subsection = data[0]
            imIdx = data[1]
            self.entryClicked = entryClicked

            fsm.Data.Book.subsectionOpenInTOC_UI = subsection
            fsm.Data.Book.entryImOpenInTOC_UI = imIdx

            self.AddEntryWidget(imIdx, subsection, self.subsectionWidgetFrames[subsection])

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onFullEntryMove" in dir(w):
                    w.onFullEntryMove()
        elif broadcasterType == mui.ImageGroupAdd_BTN:
            self.__renderWithScrollAfter()
        elif broadcasterType == mui.ShowAllSubsections_BTN:
            self.__renderWithScrollAfter()
        elif broadcasterType == mui.ShowHideLinks_BTN:
            self.showLinks = not self.showLinks
            self.showLinksForSubsections = []
            self.__renderWithScrollAfter()
        elif broadcasterType == tocw.Filter_ETR:
            self.showAll = True
            self.filterToken = data[0]
            self.searchSubsectionsText = data[1]
            self.hide()
            self.showSubsectionsForTopSection = {}
            self.__renderWithoutScroll()
        else:
            self.__renderWithScrollAfter()

    def addTOCEntry(self, subsection, level, row):
        def openPdfOnStartOfTheSection(widget:_uuicom.TOCLabelWithClick):
            def __cmd(event = None, *args):
                # open orig material on page
                origMatNameDict = fsm.Data.Sec.origMatNameDict(subsection)
                omName = origMatNameDict[list(origMatNameDict.keys())[-1]]

                if str(omName) == _u.Token.NotDef.str_t:
                    # when there is no entries yet we use the current origMaterial name
                    omName = fsm.Data.Book.currOrigMatName

                subsectionStartPage = fsm.Data.Sec.start(subsection)
                fsm.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(omName, subsectionStartPage)

                pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.PdfReadersManager)
                pdfReadersManager.show(page = int(subsectionStartPage))

                event.widget.changeColor("white")
            
            widget.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])

        def __openContentOfTheSection(frame:_uuicom.TOCFrame, label:_uuicom.TOCLabelWithClick):
            self.subsectionWidgetFrames[subsection] = frame

            def __cmd(event, subsection, *args):
                # open orig material on page

                links:dict = fsm.Data.Sec.imLinkDict(subsection)

                def closeAllSubsections():
                    self.currSecondRowLabels = []
                    self.linkFrames = []

                    for wTop1 in event.widget.getGrandParent().getChildren():
                        for wTop2 in wTop1.getChildren().copy():
                            if "labelwithclick".lower() in str(wTop2.name).lower():
                                wTop2.clicked = False
                            if ("frame".lower()  in str(wTop2.name).lower()) \
                                or ("contentDummyFr_".lower() in str(wTop2).lower()):
                                for wTop3 in wTop2.getChildren().copy():
                                    wTop3.destroy()
                                wTop2.destroy()
                            else:
                                for wTop3 in wTop2.getChildren().copy():
                                    wTop3.destroy()

                # 4 : event of mouse click
                # 19 : event of being rendered
                if ((not label.clicked) and (int(event.type) == 4)) or\
                    ((self.subsectionClicked == subsection) and (int(event.type) == 19)):
                    fsm.Data.Book.subsectionOpenInTOC_UI = subsection
                    if ((not label.clicked) and (int(event.type) == 4)):
                        fsm.Data.Book.currSection = subsection

                    if not self.showAll:
                        closeAllSubsections()

                    i = 0

                    for conWidget in self.subsectionContentLabels:
                        if conWidget.subsection != subsection:
                            conWidget.clicked = False

                    subSecID = _upan.Names.UI.getWidgetSubsecId(subsection)

                    if subsection != fsm.Data.Book.currSection:
                        return

                    for k,_ in links.items():             
                        if ((subsection != fsm.Data.Book.currSection)\
                            or (topSection != fsm.Data.Book.currTopSection))\
                            and (not self.showAll):
                            continue
                        else:
                            i += 1   
                            self.AddEntryWidget(k, subsection, frame)       


                    dummyFrame = _uuicom.TOCFrame(frame, prefix = "contentDummyFr_" + subSecID,
                                        row = i + 1, column = 0)
                    dummyEntryPage = _uuicom.TOCLabelWithClick(dummyFrame, 
                                                    text ="\n", 
                                                    prefix = "contentDummy_" + subSecID,
                                                    row=0, column=0)
                    dummyEntryPage.render()
                    dummyFrame.render()

                    if int(event.type) == 4:
                        label.clicked = True

                        if not label.alwaysShow:
                            self.subsectionClicked = subsection
                    
                    if not(self.showAll):
                        # fsm.Data.Book.subsectionOpenInTOC_UI = subsection
                        fsm.Data.Book.currSection = subsection
                        # fsm.Data.Book.currTopSection = subsection.split(".")[0]
                        # fsm.Data.Book.entryImOpenInTOC_UI = "-1"

                        import UI.widgets_collection.main.math.UI_layouts.mainLayout as mui
                        self.notify(mui.ScreenshotLocation_LBL)

                    self.scrollIntoView(event)
                else:
                    if int(event.type) == 4:
                        if not self.showAll:
                            closeAllSubsections()

                        label.clicked = False

                        if not label.alwaysShow:
                            self.subsectionClicked = _u.Token.NotDef.str_t

                    self.scrollIntoView(event)

                event.widget.changeColor("white")
            
            label.rebind([ww.currUIImpl.Data.BindID.mouse1], [lambda e, subsection = subsection: __cmd(e, subsection)])

            if ((self.subsectionClicked == subsection) and (level != 0)) or self.showAll:
                label.generateEvent(ww.currUIImpl.Data.BindID.mouse1)

        def openContentOfTheTopSection(frame:_uuicom.TOCFrame, label:_uuicom.TOCLabelWithClick):
            def __cmd(event = None, *args):
                
                # 4 : event of mouse click
                # 19 : event of being rendered
                if ((not label.clicked) and (int(event.type) == 4)) or\
                    ((self.showSubsectionsForTopSection[subsection] == True) and (int(event.type) == 19)) or\
                    self.showAll:
                    fsm.Data.Book.currTopSection = subsection
                    label.clicked = True
                    self.showSubsectionsForTopSection[subsection] = True
                    self.widgetToScrollTo = None
                    self.__renderWithScrollAfter()
                else:
                    if int(event.type) == 4:
                        self.subsectionClicked = _u.Token.NotDef.str_t
                        self.entryClicked = _u.Token.NotDef.str_t
                        self.showSubsectionsForTopSection[subsection] = False
                        self.displayedImages = []
                        self.openedMainImg = None

                        self.showSubsectionsForTopSection[subsection] = False
                        self.__renderWithScrollAfter()

                event.widget.changeColor("white")
            
            label.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])

        if level != 0:
            topSection = subsection.split(".")[0]

            if not self.showSubsectionsForTopSection[topSection]:
                return

        topSection = subsection.split(".")[0]
        
        frameName = subsection.replace(".", "")

        locFrame = _uuicom.TOCFrame(self.scrollable_frame, 
                            prefix = frameName,
                            row = row, column = 0)
        super().addTOCEntry(locFrame, row, 0)

        nameId = "subsecLabel_" + subsection 
        nameId = nameId.replace(".", "")


        def updateSubsection(event, *args):
            widget = event.widget
            subsection = widget.subsection

            def __bringImageWidgetBack(event, imageWidget):
                newText = event.widget.getData()

                if subsection in list(fsm.Data.Book.sections.keys()):
                    sections = fsm.Data.Book.sections
                    sections[subsection]["name"] = newText
                    fsm.Data.Book.sections = sections
                    fsm.Wr.SectionInfoStructure.rebuildTopSectionLatex(event.widget.subsection,
                                                                    _upan.Names.Subsection.getTopSectionPretty)
                else:
                    fsm.Data.Sec.text(event.widget.subsection, newText)
                    fsm.Wr.SectionInfoStructure.rebuildSubsectionImOnlyLatex(event.widget.subsection,
                                                                    _upan.Names.Subsection.getSubsectionPretty)
                
                event.widget.hide()
                imageWidget.updateSubsectionImage()
                imageWidget.render()

            sectionName = ""
            if subsection in list(fsm.Data.Book.sections.keys()):
                sectionName = fsm.Data.Book.sections[subsection]["name"]
            else:
                sectionName = fsm.Data.Sec.text(subsection)

            subsectionLabel = _uuicom.MultilineText_ETR(locFrame, 
                                                        "subsectionETR" + subsection, 
                                                        0, 0, 
                                                        "", # NOTE: not used anywhere  
                                                        sectionName)
            subsectionLabel.subsection = subsection
            subsectionLabel.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                                    [lambda e, *args: __bringImageWidgetBack(e, widget)])
            subsectionLabel.forceFocus()
            subsectionLabel.render()

        currSubsectionHidden = False
        hiddenSubsections = fsm.Data.Book.subsectionsHiddenInTOC_UI
        if not self.showAll:
            for hiddensSubsection in hiddenSubsections:
                if (subsection.startswith(hiddensSubsection)) and (subsection != hiddensSubsection):
                    currSubsectionHidden = True
                    break

        if level == 0:
            if subsection != self.subsectionAsETR.subsection:
                topSectionImgPath = _upan.Paths.Screenshot.Images.getTopSectionEntryImageAbs(
                                                            sf.Wr.Manager.Book.getCurrBookName(),
                                                            subsection)

                if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(topSectionImgPath):
                    result = Image.open(topSectionImgPath)
                else:
                    result = fsm.Wr.SectionInfoStructure.rebuildTopSectionLatex(subsection,
                                                                                _upan.Names.Subsection.getTopSectionPretty)

                shrink = 0.8
                result.thumbnail([int(result.size[0] * shrink),int(result.size[1] * shrink)], Image.LANCZOS)
                result = ww.currUIImpl.UIImage(result)

                subsectionLabel = _uuicom.TOCLabelWithClick(root = locFrame,
                                                            image = result,
                                                            prefix = "_topSection" + nameId, 
                                                            padding = [0, 20, 0, 0],
                                                            row = 0, column= 0)
                subsectionLabel.image = result
                subsectionLabel.subsection = subsection
                subsectionLabel.rebind([ww.currUIImpl.Data.BindID.mouse2],
                                        [updateSubsection])
                openPdfOnStartOfTheSection(subsectionLabel)
                subsectionLabel.render()
        else:
            if not currSubsectionHidden:
                if subsection != self.subsectionAsETR.subsection:
                    subsectionImgPath = _upan.Paths.Screenshot.Images.getSubsectionEntryImageAbs(
                                                            sf.Wr.Manager.Book.getCurrBookName(), 
                                                            subsection)

                    if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(subsectionImgPath):
                        result = Image.open(subsectionImgPath)
                    else:
                        result = \
                            fsm.Wr.SectionInfoStructure.rebuildSubsectionImOnlyLatex(subsection, 
                                                                                 _upan.Names.Subsection.getSubsectionPretty)

                    shrink = 0.8
                    result.thumbnail([int(result.size[0] * shrink),int(result.size[1] * shrink)], Image.LANCZOS)
                    result = ww.currUIImpl.UIImage(result)

                    subsectionLabel = _uuicom.TOCLabelWithClick(locFrame, 
                                                                image = result, 
                                                                prefix = "_subsecion" + nameId,
                                                                row = 0, column= 0)
                    subsectionLabel.image = result
                    subsectionLabel.subsection = subsection
                    subsectionLabel.rebind([ww.currUIImpl.Data.BindID.mouse2],
                                            [updateSubsection])
                    openPdfOnStartOfTheSection(subsectionLabel)

                subsectionLabel.render()

        if level != 0:
            if (not currSubsectionHidden) or self.showAll:
                openContentLabel = _uuicom.TOCLabelWithClick(locFrame, text = "[content]", 
                                                    prefix = "subsecContent" + subsection.replace(".", ""),
                                                    row = 0, column= 1)

                openContentLabel.subsection = subsection

                if subsection == fsm.Data.Book.currSection:
                    self.currSubsectionWidget = openContentLabel

                hiddenSubsections = fsm.Data.Book.subsectionsHiddenInTOC_UI

                if (topSection == fsm.Data.Book.currTopSection)\
                    and (not self.showAll)\
                    and (subsection not in hiddenSubsections):
                    __openContentOfTheSection(locFrame, openContentLabel)
                elif self.showAll:
                    __openContentOfTheSection(locFrame, openContentLabel)

                _uuicom.bindChangeColorOnInAndOut(openContentLabel)

                self.subsectionContentLabels.append(openContentLabel)

                if self.showAll or (subsection == fsm.Data.Book.currSection):
                    openContentLabel.clicked = False

                rebuildLatex = _uuicom.TOCLabelWithClick(locFrame, text = "[rebuild latex]",
                                                prefix = "subsecRebuild" + subsection.replace(".", ""),
                                                row = 0, column = 4)
                rebuildLatex.subsection = subsection

                _uuicom.bindChangeColorOnInAndOut(rebuildLatex)

                def rebuildSubsectionLatexWrapper(subsection):
                    fsm.Wr.SectionInfoStructure.rebuildSubsectionLatex(subsection,
                                                                    _upan.Names.Group.formatGroupText,
                                                                    _upan.Names.Subsection.getSubsectionPretty,
                                                                    _upan.Names.Subsection.getTopSectionPretty)
                    self.__renderWithScrollAfter()

                rebuildLatex.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                    [lambda e, *args: rebuildSubsectionLatexWrapper(e.widget.subsection)])

                if fsm.Data.Sec.isVideo(subsection):
                    showVideo = _uuicom.TOCLabelWithClick(locFrame, text = "[show video]",
                                                    prefix = "showVideo" + subsection.replace(".", ""),
                                                    row = 0, column = 6)
                    showVideo.subsection = subsection

                    _uuicom.bindChangeColorOnInAndOut(showVideo)

                    def showSubsectiionVideoWrapper(subsection):  
                        videoPlayerManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                    wf.Wr.MenuManagers.VideoPlayerManager)
                        videoPlayerManager.show(subsection, "0")

                    showVideo.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                        [lambda e, *args: showSubsectiionVideoWrapper(e.widget.subsection)])

                def __updateStartPage(e, subsection, *args):
                    newStartPage = e.widget.getData()
                    fsm.Data.Sec.start(subsection, newStartPage)
                    omName = fsm.Data.Book.currOrigMatName
                    
                    fsm.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(omName, newStartPage)

                    pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                            wf.Wr.MenuManagers.PdfReadersManager)
                    pdfReadersManager.show(page = int(newStartPage))

                startPage = fsm.Data.Sec.start(subsection)
                changeStartPage = _uuicom.ImageSize_ETR(locFrame,
                                                        prefix = "updateStartPageEntryText" + subsection.replace(".", ""),
                                                        row = 0, 
                                                        column = 3,
                                                        imIdx = -1,
                                                        text = startPage)
                changeStartPage.subsection = subsection
                changeStartPage.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                        [lambda e, *args:__updateStartPage(e, changeStartPage.subsection, *args)])

                def __updateSubsectionPath(e, subsection, *args):
                    targetSubsection = e.widget.getData()
                    sourceSubsection = subsection

                    # ask the user if we wnat to proceed.
                    msg = "Do you want to move \n\n subsection\n'{0}' \n\nto \n'{1}'?".format(sourceSubsection, targetSubsection)
                    response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

                    mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                wf.Wr.MenuManagers.MathMenuManager)
                    mainManager.show()

                    if not response:
                        return

                    gm.GeneralManger.moveSubsection(sourceSubsection,
                                                    targetSubsection)
                    self.__renderWithScrollAfter()

                updateSubsectionPath = _uuicom.ImageSize_ETR(locFrame,
                                                        prefix = "updateSubsectionPosEntryText" + subsection.replace(".", ""),
                                                        row = 0, 
                                                        column = 5,
                                                        imIdx = -1,
                                                        text = subsection,
                                                        width = 20)
                updateSubsectionPath.subsection = subsection
                updateSubsectionPath.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                        [lambda e, *args:__updateSubsectionPath(e, updateSubsectionPath.subsection, *args)])

                def __removeSubsection(e, subsection, *args):
                    sourceSubsection = subsection

                    # ask the user if we wnat to proceed.
                    msg = "Do you want to \n\nREMOVE \n\n subsection:\n'{0}'?".format(sourceSubsection)
                    response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

                    mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                wf.Wr.MenuManagers.MathMenuManager)
                    mainManager.show()

                    if not response:
                        return

                    gm.GeneralManger.deleteSubsection(sourceSubsection)
                    self.__renderWithScrollAfter()

                removeSubsection = _uuicom.TOCLabelWithClick(locFrame,
                                                        prefix = "removeSubsectionPosEntryText" + subsection.replace(".", ""),
                                                        row = 0, 
                                                        column = 7,
                                                        text = "[delete]")
                removeSubsection.subsection = subsection
                removeSubsection.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                        [lambda e, *args:__removeSubsection(e, removeSubsection.subsection, *args)])

                hideSubsections = _uuicom.TOCLabelWithClick(locFrame, text = "[show/hide]",
                                                prefix = "subsecShowHide" + subsection.replace(".", ""),
                                                row = 0, column = 2)
                subsectionsList = fsm.Wr.BookInfoStructure.getSubsectionsList(subsection)
                if subsectionsList != []:
                    hideSubsections.changeColor("brown")

                hideSubsections.subsection = subsection

                _uuicom.bindChangeColorOnInAndOut(removeSubsection)

                if subsectionsList != []:
                    _uuicom.bindChangeColorOnInAndOut(hideSubsections, shouldBeBrown = True)
                else:
                    _uuicom.bindChangeColorOnInAndOut(hideSubsections)

                def showHideSubsectionsWrapper(subsection):
                    subsectionsHidden:list = fsm.Data.Book.subsectionsHiddenInTOC_UI

                    if subsection in subsectionsHidden:
                        subsectionsHidden.remove(subsection)
                    else:
                        self.widgetToScrollTo = None
                        self.currEntryWidget = None
                        subsectionsHidden.append(subsection)
                    
                    fsm.Data.Book.subsectionsHiddenInTOC_UI =  subsectionsHidden
                    self.__renderWithScrollAfter()

                hideSubsections.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                       [lambda e, *args: showHideSubsectionsWrapper(e.widget.subsection)])

                openContentLabel.render()
                rebuildLatex.render()

                if fsm.Data.Sec.isVideo(subsection):
                    showVideo.render()
                changeStartPage.render()

                if not self.showAll:
                    hideSubsections.render()
                    updateSubsectionPath.render()
                    removeSubsection.render()
        else:
            openContentLabel = _uuicom.TOCLabelWithClick(locFrame, 
                                                 prefix = "openContentLabel" + subsection.replace(".", ""),
                                                 text = "[content]", padding = [0, 20, 0, 0],
                                                 row = 0, column= 1)

            if subsection in list(self.showSubsectionsForTopSection.keys()):
                openContentLabel.clicked = self.showSubsectionsForTopSection[subsection]
            else:
                self.showSubsectionsForTopSection[subsection] = True
                openContentLabel.clicked = True

            openContentOfTheTopSection(locFrame, openContentLabel)
            _uuicom.bindChangeColorOnInAndOut(openContentLabel)

            openContentLabel.render()

    def populateTOC(self):
        text_curr = fsm.Wr.BookInfoStructure.getSubsectionsAsTOC()

        text_curr_filtered = []

        if self.filterToken != "":
            for i in range(len(text_curr)):
                subsection = text_curr[i][0]

                if "." not in subsection:
                    continue

                imLinkDict = fsm.Data.Sec.imLinkDict(subsection)
                extraImagesDict = fsm.Data.Sec.extraImagesDict(subsection)

                for k,v in imLinkDict.items():
                    entryImText = fsm.Wr.SectionInfoStructure.getEntryImText(subsection, k)

                    if k in list(extraImagesDict.keys()):
                        for t in extraImagesDict[k]:
                            entryImText += t

                    if (self.filterToken.lower() in v.lower()) \
                        or (self.filterToken.lower() in entryImText.lower()):
                        text_curr_filtered.append(text_curr[i])
                        break
        else:
            text_curr_filtered = text_curr

        if (not self.showAll) or (self.filterToken != ""):
            for i in range(len(text_curr_filtered)):
                subsection = text_curr_filtered[i][0]
                topSection = subsection.split(".")[0]
                level = text_curr_filtered[i][1]

                if (topSection == fsm.Data.Book.currTopSection) \
                    or self.showAll:
                    self.showSubsectionsForTopSection[subsection] = True
                else:
                    self.showSubsectionsForTopSection[subsection] = False

                self.addTOCEntry(subsection, level, i)

    def render(self, shouldScroll = False):
        for w in self.entryWidgetManagers.values():
            w.entryFrame.destroy()
        
        self.entryWidgetManagers = {}

        wd.Data.Reactors.entryChangeReactors[self.name] = self
        # import traceback
        
        # for line in traceback.format_stack():
        #     print(line.strip())

        if self.showAll:
            self.showLinksForSubsections = []

        self.subsectionWidgetFrames = {}
        self.shouldScroll = shouldScroll
        self.displayedImages = []
        self.subsectionContentLabels = []
        self.currSecondRowLabels = []
        self.linkFrames = []
        self.showImagesLabels = {}

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
            mainMenuManager.changeLowerSubframeHeight(600)
        
        def __smallerEntry():
            mainMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                            wf.Wr.MenuManagers.MathMenuManager)
            mainMenuManager.changeLowerSubframeHeight(375)
        def __noEntry():
            mainMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                            wf.Wr.MenuManagers.MathMenuManager)
            mainMenuManager.changeLowerSubframeHeight(0)
        return [ww.currUIImpl.Data.BindID.Keys.cmdone, 
                ww.currUIImpl.Data.BindID.Keys.cmdtwo,
                ww.currUIImpl.Data.BindID.Keys.cmdshh], \
               [lambda *args: __largerEntry(), 
                lambda *args: __smallerEntry(),
                lambda *args: __noEntry()]