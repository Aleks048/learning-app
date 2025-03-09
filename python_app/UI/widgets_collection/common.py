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

        if "EntryWindow_BOX" in str(type(self.tocBox)):
            self.tocBox.rerenderAndSetMainTOC()
        else:
            self.tocBox.render()

class EntryShowPermamentlyCheckbox(ww.currUIImpl.Checkbox):
    def __init__(self, parent, subsection, imIdx, prefix, tocBox, row, column):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        name = "_EntryShowPermamentlyCheckbox_"

        self.subsection = subsection
        self.imidx = str(imIdx)
        self.tocBox = tocBox

        tocWImageDict = fsm.Data.Sec.tocWImageDict(self.subsection)
        if tocWImageDict == _u.Token.NotDef.dict_t:
            alwaysShow = "0"
        else:
            alwaysShow = tocWImageDict[self.imidx]

        super().__init__(prefix,
                         name,
                         parent, 
                         renderData,
                         command = lambda *args: self.__cmd())
        self.setData(int(alwaysShow))

    def __cmd(self):
        if self.getData() == None:
            return

        if self.tocBox == None:
            return

        tocWImageDict = fsm.Data.Sec.tocWImageDict(self.subsection)
        tocWImageDict[self.imidx] = str(self.getData())
        fsm.Data.Sec.tocWImageDict(self.subsection, tocWImageDict)

        self.tocBox.render()
        self.tocBox.rerenderAndSetMainTOC()

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

    def __init__(self, parent, subsection, imIdx, row, column, entryFrame):
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
                         renderData)
    
    def __showLinkImages(self, e, frame, *args):
        widget = e.widget
        imLabel = _uuicom.addMainEntryImageWidget(frame, 
                                    widget.subsection, widget.imIdx,
                                    imPadLeft = 120, 
                                    displayedImagesContainer = [])
        imLabel.render()

        def skipProofs(subsection, imIdx, i):
            return "proof" in fsm.Data.Sec.extraImagesDict(subsection)[imIdx][i].lower()

        exImLabels = _uuicom.addExtraEntryImagesWidgets(frame, 
                                                    widget.subsection, widget.imIdx,
                                                    imPadLeft = 120, 
                                                    displayedImagesContainer = [],
                                                    skippConditionFn = skipProofs,
                                                    tocFrame = self)
        for l in exImLabels:
            l.render()
        
        if frame.wasRendered:
            frame.hide()
        else:
            frame.render()
        
        self.entryFrame.updateHeight()

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
        self.linkFullMoveNotification(e.subsection, e.imIdx)

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
                            _uuicom.openOMOnThePageOfTheImage(glLinkLablel, targetSubsection, targetImIdx)
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
                    self.__scrollIntoView(None, ch)

                    break
        else:
            _u.log.autolog("We should not be here.")


    def __scrollIntoView(self, event, widget = None):
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

        if uiResizeEntryIdx.get(self.imIdx) != None:
            resizeFactor = float(uiResizeEntryIdx[self.imIdx])
        else:
            resizeFactor = 1.0

        entryImagesFactory = _uuicom.EntryImagesFactory(self.subsection, self.imIdx)
        imLabel = entryImagesFactory.produceEntryMainImageWidget(self.imagesFrame,
                                                       imPadLeft = 120,
                                                       resizeFactor = resizeFactor)

        imLabel.render()

        def skipProofs(subsection, imIdx, i):
            if dt.AppState.ShowProofs.getData(self.appCurrDataAccessToken):
                return False
            else:
                return "proof" in fsm.Data.Sec.extraImagesDict(subsection)[imIdx][i].lower()

        exImLabels = entryImagesFactory.produceEntryExtraImagesWidgets(self.imagesFrame,
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

        def copyEntryCmd(event, *args):
            widget = event.widget
            self.entryCopySubsection = widget.subsection
            self.entryCopyImIdx = widget.imIdx
            self.cutEntry = False

        def cutEntryCmd(event, *args):
            widget = event.widget
            self.entryCopySubsection = widget.subsection
            self.entryCopyImIdx = widget.imIdx
            self.cutEntry = True

        def retakeImageCmd(event, entrylLabel, *args):
            widget = event.widget
            subsection = widget.subsection
            imIdx = widget.imIdx

            currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            
            msg = "Do you want to retake entry image?"
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

            if not response:
                return

            imagePath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBookPath,
                                                                        subsection,
                                                                        str(imIdx))
            ocf.Wr.FsAppCalls.deleteFile(imagePath)
            figuresLabelsData = fsm.Data.Sec.figuresLabelsData(subsection)
            figuresData = fsm.Data.Sec.figuresData(subsection)

            if figuresLabelsData.get(str(imIdx)) != None:
                figuresLabelsData.pop(str(imIdx))
            
            if figuresData.get(str(imIdx)) != None:
                figuresData.pop(str(imIdx))
            

            fsm.Data.Sec.figuresLabelsData(subsection, figuresLabelsData)
            fsm.Data.Sec.figuresData(subsection, figuresData)

            pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                wf.Wr.MenuManagers.PdfReadersManager)
            pdfReadersManager.show(subsection = subsection,
                                           imIdx = imIdx,
                                           selector = True,
                                           removePrevLabel = True,
                                           withoutRender = True)
            def __cmdAfterImageCreated():
                timer = 0

                while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                    time.sleep(0.3)
                    timer += 1

                    if timer > 50:
                        break

                self.retakeImageNotification(self.subsection, self.imIdx)
                self.updateHeight()
            
            t = Thread(target = __cmdAfterImageCreated, args = [])
            t.start()

        def pasteEntryCmd(event, *args):
            widget = event.widget

            if None in [self.entryCopySubsection, self.entryCopyImIdx] or\
                _u.Token.NotDef.str_t in [self.entryCopySubsection, self.entryCopyImIdx]:
                _u.log.autolog("Did not paste entry. The copy data is not correct.")
                return

            fsm.Wr.SectionInfoStructure.insertEntryAfterIdx(self.entryCopySubsection,
                                                            self.entryCopyImIdx,
                                                            widget.subsection,
                                                            widget.imIdx,
                                                            self.cutEntry,
                                                            shouldAsk = True)
            self.render()

        def removeEntryCmd(event, *args):
            widget = event.widget
            fsm.Wr.SectionInfoStructure.removeEntry(widget.subsection, widget.imIdx)

            def __afterDeletion(*args):
                timer = 0
                while fsm.Data.Sec.figuresLabelsData(subsection).get(widget.imIdx) != None:
                    time.sleep(0.3)
                    timer += 1
                    if timer > 50:
                        break

                pdfReaderManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                                    wf.Wr.MenuManagers.PdfReadersManager)
                pdfReaderManager.show(subsection = widget.subsection, 
                                        imIdx = str(widget.imIdx), 
                                        removePrevLabel = True)

            t = Thread(target = __afterDeletion)
            t.start()

            self.__renderWithScrollAfter()

        def addExtraImCmd(event, l, *args):
            _uuicom.addExtraIm(self.subsection, self.imIdx, False, entryLabel = l)

        def addExtraImProofCmd(event, l, *args):
            _uuicom.addExtraIm(self.subsection, self.imIdx, True, entryLabel = l)


        def copyGlLinkCmd(event, *args):
            widget:_uuicom.TOCLabelWithClick = event.widget
            dt.UITemp.Link.subsection = widget.subsection
            dt.UITemp.Link.imIdx = widget.imIdx

        def resizeEntryImgCMD(event, *args):
            resizeFactor = event.widget.getData()

            # check if the format is right
            if not re.match("^[0-9]\.[0-9]$", resizeFactor):
                _u.log.autolog(\
                    f"The format of the resize factor '{resizeFactor}'is not correct")
                return
            
            subsection = event.widget.subsection
            imIdx = event.widget.imIdx
            
            uiResizeEntryIdx = fsm.Data.Sec.imageUIResize(subsection)

            if (uiResizeEntryIdx == None) \
                or (uiResizeEntryIdx == _u.Token.NotDef.dict_t):
                uiResizeEntryIdx = {}

            uiResizeEntryIdx[imIdx] = resizeFactor

            fsm.Data.Sec.imageUIResize(subsection, uiResizeEntryIdx)
            msg = f"After resize of {subsection} {imIdx}"
            ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

            self.resizeImageNotification(self.subsection, self.imIdx)

        def openExcerciseMenu(event, *args):
            exMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.ExcerciseManager)
            exMenuManger.subsection = event.widget.subsection
            exMenuManger.imIdx = event.widget.imIdx

            event.widget.shouldShowExMenu = not event.widget.shouldShowExMenu
            if (event.widget.shouldShowExMenu):
                exMenuManger.show()
            else:
                exMenuManger.hide()

        def openNoteMenu(event, *args):
            notesMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.NotesManager)
            notesMenuManger.subsection = event.widget.subsection
            notesMenuManger.imIdx = event.widget.imIdx

            event.widget.shouldShowNotesMenu = not event.widget.shouldShowNotesMenu
            if (event.widget.shouldShowNotesMenu):
                notesMenuManger.show()
            else:
                notesMenuManger.hide()

        def openEntryNoteMenu(event, *args):
            notesMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.EntryNotesManager)
            notesMenuManger.subsection = event.widget.subsection
            notesMenuManger.imIdx = event.widget.imIdx

            event.widget.shouldShowNotesMenu = not event.widget.shouldShowNotesMenu
            if (event.widget.shouldShowNotesMenu):
                notesMenuManger.show()
            else:
                notesMenuManger.hide()

        def openWiki(event, *args):
            os.system("\
    /Users/ashum048/books/utils/c++_modules/qt_KIK_Browser/build/Qt_6_8_0_macos-Debug/browser.app/Contents/MacOS/browser \
    http://localhost/wiki/A/User:The_other_Kiwix_guy/Landing")

        def hideLinksImagesFunc(event, *args):
            self.linksOpenImage.clear()

            for k in self.linksOpenImageWidgets.keys():
                im = self.linksOpenImageWidgets[k]
                im.hide()

            self.linksOpenImageWidgets = {}

            self.__renderWithScrollAfter()

        def openBookCodeProjectCmd(event, *args):
            subsection = event.widget.subsection
            imIdx = event.widget.imIdx
            dt.CodeTemp.currCodeFullLink = imIdx

            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            projectPath = _upan.Paths.Book.Code.getAbs(bookPath)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(projectPath):
                _u.log.autolog("Please add a book code project files.")
                return

            ocf.Wr.IdeCalls.openNewWindow(projectPath)

            bookCodeFiles:dict = fsm.Data.Sec.bookCodeFile(subsection)

            if bookCodeFiles.get(imIdx) != None:
                relFilepath = bookCodeFiles.get(imIdx)
                time.sleep(0.5)
                filepath = os.path.join(projectPath, relFilepath)

                if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(filepath):
                    return

                lines = []
                with open(filepath) as f:
                    lines = f.read().splitlines()
                
                marker = _upan.Names.codeLineMarkerBook(subsection, imIdx)

                for i in range(len(lines)):
                    if marker in lines[i]:
                        ocf.Wr.IdeCalls.openNewTab(filepath, i)
                        return

                ocf.Wr.IdeCalls.openNewTab(filepath)

        def openSubsectionCodeProjectCmd(event, *args):
            subsection = event.widget.subsection
            imIdx = event.widget.imIdx
            dt.CodeTemp.currCodeFullLink = imIdx

            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            codeTemplatePath =_upan.Paths.Book.Code.getSubsectionTemplatePathAbs(bookPath)
            codeSubsectionPath =_upan.Paths.Section.getCodeRootAbs(bookPath,
                                                                    subsection)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(codeSubsectionPath):
                ocf.Wr.FsAppCalls.copyFile(codeTemplatePath, codeSubsectionPath)

            ocf.Wr.IdeCalls.openNewWindow(codeSubsectionPath)

            subsectionCodeFiles:dict = fsm.Data.Sec.subsectionCodeFile(subsection)

            if subsectionCodeFiles.get(imIdx) != None:
                relFilepath = subsectionCodeFiles.get(imIdx)
                time.sleep(0.5)
                filepath = os.path.join(codeSubsectionPath, relFilepath)

                if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(filepath):
                    _u.log.autolog(f"Subsection '{filepath}' file not found.")
                    return

                lines = []
                with open(filepath) as f:
                    lines = f.read().splitlines()
                
                marker = _upan.Names.codeLineMarkerSubsection(subsection, imIdx)

                for i in range(len(lines)):
                    if marker in lines[i]:
                        ocf.Wr.IdeCalls.openNewTab(filepath, i)
                        return

                ocf.Wr.IdeCalls.openNewTab(filepath)

        def openEntryCodeProjectCmd(event, *args):
            subsection =  event.widget.subsection
            imIdx =  event.widget.imIdx
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

            entryPath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryPath):
                fsm.Wr.EntryInfoStructure.createStructure(bookPath, subsection, imIdx)

            entryCodeProjFilepath = _upan.Paths.Entry.getCodeProjAbs(bookPath, subsection, imIdx)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryCodeProjFilepath):
                codeProjTemplatePath = \
                    _upan.Paths.Book.Code.getEntryTemplatePathAbs(bookPath)
                ocf.Wr.FsAppCalls.copyFile(codeProjTemplatePath, entryCodeProjFilepath)

            ocf.Wr.IdeCalls.openNewWindow(_upan.Paths.Entry.getCodeProjAbs(bookPath, subsection, imIdx))

        def copyTextToMemCmd(event, *args):
            pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                        wf.Wr.MenuManagers.PdfReadersManager)
            pdfReadersManager.show(subsection = event.widget.subsection,
                                   imIdx = event.widget.imIdx,
                                   selector = True,
                                   getTextOfSelector = True,
                                   withoutRender = True)

        def openProofsMenu(event, *args):
            prMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.ProofsManager)

            event.widget.shouldShowProofMenu = not event.widget.shouldShowProofMenu
            if (event.widget.shouldShowProofMenu):
                prMenuManger.show(subsection =  event.widget.subsection, imIdx = event.widget.imIdx)
            else:
                prMenuManger.hide()

        def updateEntry(event, *args):
            widget = event.widget

            imLinkDict = fsm.Data.Sec.imLinkDict(widget.subsection)
            text = imLinkDict[widget.imIdx]

            textLabelPage = _uuicom.MultilineText_ETR(widget.root, 
                                                        "contentP_" + widget.imIdx + widget.subsection, 
                                                        0,
                                                        0, 
                                                        widget.imageLineIdx, 
                                                        text)
            textLabelPage.imIdx = widget.imIdx
            textLabelPage.subsection = widget.subsection
            #textLabelPage.etrWidget = textLabelPage

            def __getWidgetBack(textEntry:_uuicom.MultilineText_ETR, widget):
                newText = textEntry.getData()
                imLinkDict = fsm.Data.Sec.imLinkDict(textEntry.subsection)
                textOnly = fsm.Data.Sec.textOnly(textEntry.subsection)[textEntry.imIdx]
                imLinkDict[textEntry.imIdx] = newText
                fsm.Data.Sec.imLinkDict(textEntry.subsection, imLinkDict)
                fsm.Wr.SectionInfoStructure.rebuildEntryLatex(textEntry.subsection,
                                                            textEntry.imIdx,
                                                            newText,
                                                            textOnly
                                                            )
                
                widget.render()
                widget.updateImage()
                textEntry.hide()

            textLabelPage.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                                    [lambda *args: __getWidgetBack(textLabelPage, widget)])
            widget.hide()
            textLabelPage.render()
            textLabelPage.forceFocus()

        if imIdx == _u.Token.NotDef.str_t:
            return

        k = imIdx
        i = int(imIdx)

        v = fsm.Data.Sec.imLinkDict(subsection)[k]
        # subSecID = _upan.Names.UI.getWidgetSubsecId(subsection)

        extraImagesDict = fsm.Data.Sec.extraImagesDict(subsection)
        textOnly = fsm.Data.Sec.textOnly(subsection)[str(k)]

        entryImText = fsm.Wr.SectionInfoStructure.getEntryImText(subsection, k)
        
        if k in list(extraImagesDict.keys()):
            for t in extraImagesDict[k]:
                entryImText += t

            currImGroupidx = 0

        topPad = 0
        gridRowStartIdx = 1

        nameId = _upan.Names.Entry.getEntryNameID(subsection, k)

        leadingEntry = fsm.Data.Sec.leadingEntry(subsection)

        if leadingEntry.get(imIdx) != None:
            leftPad = 30
        else:
            leftPad = 0

        tempFrame = _uuicom.TOCFrame(frame,
                                prefix = "contentFr_" + nameId,
                                padding=[leftPad, topPad, 0, 0],
                                row = int(k) + 2, column = 0, columnspan = 100)

        tempFrameRow1 = _uuicom.TOCFrame(tempFrame,
                            prefix = "contentRow1Fr_" + nameId,
                            padding=[0, topPad, 0, 0],
                            row = gridRowStartIdx - 1, 
                            column = 0, columnspan = 100)
        tempFrameRow1.render()

        tempFrameRow2 = _uuicom.TOCFrame(tempFrame,
                            prefix = "contentRow2Fr_" + nameId,
                            padding=[60, topPad, 0, 0],
                            row = gridRowStartIdx, 
                            column = 0, columnspan = 100)
        tempFrameRow2.subsection = subsection
        tempFrameRow2.imIdx = k
        tempFrameRow2.render()

        linkFrame = LinksFrame(tempFrame,
                               self.subsection,
                               self.imIdx,
                               row = gridRowStartIdx + 1, 
                               column = 0,
                               entryFrame = self)
        if self.linkFrameShown:
            linkFrame.render()

        latexTxt = tff.Wr.TexFileUtils.fromEntryToLatexTxt(k, v)
        pilIm = getEntryImg(latexTxt, subsection, k)

        shrink = 0.7
        pilIm.thumbnail([int(pilIm.size[0] * shrink),int(pilIm.size[1] * shrink)], Image.LANCZOS)
        img = ww.currUIImpl.UIImage(pilIm)


        textLabelPage = _uuicom.TOCLabelWithClick(tempFrameRow1,
                                        image = img, 
                                        prefix = "contentP_" + nameId, 
                                        padding= [60, 0, 0, 0],
                                        row = 0, 
                                        column = 0)
        textLabelPage.imIdx = k
        textLabelPage.subsection = subsection
        textLabelPage.etrWidget = textLabelPage
        textLabelPage.imageLineIdx = i
        textLabelPage.entryText = v
        textLabelPage.imagePath = v

        textLabelPage.rebind([ww.currUIImpl.Data.BindID.mouse2],
                                [updateEntry])
        textLabelPage.image = img

        imagesGroupDict:dict = fsm.Data.Sec.imagesGroupDict(subsection)
        imagesGroups = fsm.Data.Sec.imagesGroupsList(subsection)
        currImGroupidx = imagesGroupDict[k]
        currImGroupName = list(imagesGroups.keys())[currImGroupidx]

        imageGroupOM = ImageGroupOM(imagesGroups,
                                   tempFrameRow2, 
                                   subsection,
                                   imIdx,
                                   self,
                                   column = self.__EntryUIs.group.column,
                                   currImGroupName = currImGroupName)

        chkbtnShowPermamently = EntryShowPermamentlyCheckbox(tempFrameRow2, 
                                                             subsection, k, 
                                                             "contentShowAlways_" + nameId,
                                                             self,
                                                             row = 0, 
                                                             column = self.__EntryUIs.alwaysShow.column,)

        showImages = _uuicom.TOCLabelWithClick(tempFrameRow1, 
                                    text = self.__EntryUIs.full.name,
                                    prefix = "contentOfImages_" + nameId,
                                    row = 0,
                                    column = self.__EntryUIs.full.column)
        showImages.imIdx = k
        showImages.subsection = subsection
        showImages.clicked = False

        copyEntry = _uuicom.TOCLabelWithClick(tempFrameRow1,
                                                text = self.__EntryUIs.copy.name,
                                                prefix = "contentCopyEntry" + nameId,
                                                row = 0, 
                                                column = self.__EntryUIs.copy.column)
        copyEntry.imIdx = k
        copyEntry.subsection = subsection
        copyEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [copyEntryCmd])
        copyEntry.rebind([ww.currUIImpl.Data.BindID.shmouse1],
                            [cutEntryCmd])

        pasteAfterEntry = _uuicom.TOCLabelWithClick(tempFrameRow1,
                                                text = self.__EntryUIs.pasteAfter.name,
                                                prefix = "contentPasteAfterEntry" + nameId,
                                                row = 0, 
                                                column = self.__EntryUIs.pasteAfter.column)
        pasteAfterEntry.imIdx = k
        pasteAfterEntry.subsection = subsection
        pasteAfterEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [pasteEntryCmd])

        showLinksForEntry = _uuicom.TOCLabelWithClick(tempFrameRow2,
                                                text = self.__EntryUIs.showLinks.name,
                                                prefix = "contentShowLinksForEntry" + nameId,
                                                row = 0, 
                                                column = self.__EntryUIs.showLinks.column)
        showLinksForEntry.imIdx = k
        showLinksForEntry.subsection = subsection
        showLinksForEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                    [lambda e, lf = linkFrame, *args: self.showLinksForEntryCmd(lf)])

        linkExist = k in list(fsm.Data.Sec.imGlobalLinksDict(subsection).keys())

        if linkExist:
            showLinksForEntry.changeColor("brown")                 

        retakeImageForEntry = _uuicom.TOCLabelWithClick(tempFrameRow2,
                                                text =  self.__EntryUIs.retake.name,
                                                prefix = "contentRetakeImageForEntry" + nameId,
                                                row = 0, 
                                                column =  self.__EntryUIs.retake.column)
        retakeImageForEntry.imIdx = k
        retakeImageForEntry.subsection = subsection
        retakeImageForEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                    [lambda e, l = self, *args: retakeImageCmd(e, l)])

        addExtraImage = _uuicom.TOCLabelWithClick(tempFrameRow2, 
                                            text = self.__EntryUIs.addExtra.name,
                                            prefix = "contentAddExtraImageEntry" + nameId,
                                            row = 0, 
                                            column = self.__EntryUIs.addExtra.column)
        addExtraImage.imIdx = k
        addExtraImage.subsection = subsection
        addExtraImage.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [lambda e, l = self, *args: addExtraImCmd(e, l)])

        addProofImage = _uuicom.TOCLabelWithClick(tempFrameRow2, 
                                            text = self.__EntryUIs.addProof.name,
                                            prefix = "contentAddExtraProofEntry" + nameId,
                                            row = 0, 
                                            column = self.__EntryUIs.addProof.column)
        addProofImage.imIdx = k
        addProofImage.subsection = subsection
        addProofImage.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [lambda e, l = self, *args: addExtraImProofCmd(e, l)])

        copyLinkEntry = _uuicom.TOCLabelWithClick(tempFrameRow1, 
                                            text = self.__EntryUIs.copyLink.name,
                                            prefix = "contentCopyGlLinkEntry" + nameId,
                                            row = 0, 
                                            column = self.__EntryUIs.copyLink.column)
        copyLinkEntry.imIdx = k
        copyLinkEntry.subsection = subsection
        copyLinkEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [copyGlLinkCmd])

        pasteLinkEntry = _uuicom.TOCLabelWithClick(tempFrameRow1,
                                            text = self.__EntryUIs.pasteLink.name,
                                            prefix = "contentPasteGlLinkEntry" + nameId,
                                            row = 0, 
                                            column = self.__EntryUIs.pasteLink.column)
        pasteLinkEntry.imIdx = k
        pasteLinkEntry.subsection = subsection
        pasteLinkEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [self.pasteGlLinkCmd])

        openExUIEntry = _uuicom.TOCLabelWithClick(tempFrameRow1, 
                                        text = self.__EntryUIs.excercises.name, 
                                        prefix = "contentOpenExcerciseUIEntry" + nameId,
                                        row = 0, 
                                        column = self.__EntryUIs.excercises.column,
                                        columnspan = 1)
        openExUIEntry.imIdx = k
        openExUIEntry.subsection = subsection
        openExUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openExcerciseMenu])

        openNoteUIEntry = _uuicom.TOCLabelWithClick(tempFrameRow2, 
                                        text = self.__EntryUIs.note.name, 
                                        prefix = "contentOpenNoteUIEntry" + nameId,
                                        row = 0, 
                                        column = self.__EntryUIs.note.column,
                                        columnspan = 1)
        openNoteUIEntry.imIdx = k
        openNoteUIEntry.subsection = subsection
        openNoteUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openNoteMenu])

        openEntryNoteUIEntry = _uuicom.TOCLabelWithClick(tempFrameRow2, 
                                        text = self.__EntryUIs.entryNote.name, 
                                        prefix = "contentOpenEntryNoteUIEntry" + nameId,
                                        row = 1, 
                                        column = self.__EntryUIs.entryNote.column,
                                        columnspan = 1)
        openEntryNoteUIEntry.imIdx = k
        openEntryNoteUIEntry.subsection = subsection
        openEntryNoteUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openEntryNoteMenu])

        openEntryWikiUIEntry = _uuicom.TOCLabelWithClick(tempFrameRow2, 
                                        text = self.__EntryUIs.wikiNote.name, 
                                        prefix = "contentOpenEntryWikiUIEntry" + nameId,
                                        row = 1, 
                                        column = self.__EntryUIs.wikiNote.column,
                                        columnspan = 1)
        openEntryWikiUIEntry.imIdx = k
        openEntryWikiUIEntry.subsection = subsection
        openEntryWikiUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                    [openWiki])

        copyTextToMem = _uuicom.TOCLabelWithClick(tempFrameRow2, 
                                        text = self.__EntryUIs.copyText.name, 
                                        prefix = "contentCopyTextToMem" + nameId,
                                        row = 1, 
                                        column = self.__EntryUIs.copyText.column,
                                        columnspan = 1)
        copyTextToMem.imIdx = k
        copyTextToMem.subsection = subsection
        copyTextToMem.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [copyTextToMemCmd])
        
        openBookCodeProject = _uuicom.TOCLabelWithClick(tempFrameRow2, 
                                        text = self.__EntryUIs.openBookCodeProject.name, 
                                        prefix = "openBookCodeProject" + nameId,
                                        row = 1, 
                                        column = self.__EntryUIs.openBookCodeProject.column,
                                        columnspan = 1)
        openBookCodeProject.imIdx = k
        openBookCodeProject.subsection = subsection
        openBookCodeProject.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openBookCodeProjectCmd])

        openSubsectionCodeProject = _uuicom.TOCLabelWithClick(tempFrameRow2, 
                                        text = self.__EntryUIs.openSubsectionCodeProject.name, 
                                        prefix = "openSubsectionCodeProject" + nameId,
                                        row = 1, 
                                        column = self.__EntryUIs.openSubsectionCodeProject.column,
                                        columnspan = 1)
        openSubsectionCodeProject.imIdx = k
        openSubsectionCodeProject.subsection = subsection
        openSubsectionCodeProject.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openSubsectionCodeProjectCmd])

        openEntryCodeProject = _uuicom.TOCLabelWithClick(tempFrameRow2, 
                                        text = self.__EntryUIs.openEntryCodeProject.name, 
                                        prefix = "openEntryCodeProject" + nameId,
                                        row = 1, 
                                        column = self.__EntryUIs.openEntryCodeProject.column,
                                        columnspan = 1)
        openEntryCodeProject.imIdx = k
        openEntryCodeProject.subsection = subsection
        openEntryCodeProject.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openEntryCodeProjectCmd])

        fullPathToEntryJSON = _upan.Paths.Entry.JSON.getAbs(sf.Wr.Manager.Book.getCurrBookFolderPath(),
                                                            subsection,
                                                            k)
        entryStructureExists = ocf.Wr.FsAppCalls.checkIfFileOrDirExists(fullPathToEntryJSON)
        excerciseExists = False
        notesExist = False

        self.__AddEntryImages(tempFrame, padding = [leftPad, topPad, 0, 0])
        self.imagesFrame.render()

        if entryStructureExists:
            currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

            # entryLinesList = fsm.Wr.EntryInfoStructure.readProperty(subsection,
            #                                        k,
            #                                        fsm.Wr.EntryInfoStructure.PubProp.entryLinesList,
            #                                        currBookPath)

            # if (entryLinesList != _u.Token.NotDef.list_t) \
            #     and (entryLinesList != []):
            excerciseExists = True
            openExUIEntry.changeColor("brown")

            entryWordDictArr = fsm.Wr.EntryInfoStructure.readProperty(subsection,
                                                    k,
                                                    fsm.Wr.EntryInfoStructure.PubProp.entryWordDictDict,
                                                    currBookPath)

            if (entryWordDictArr != _u.Token.NotDef.dict_t)\
                and (entryWordDictArr != {}):
                notesExist = True
                openNoteUIEntry.changeColor("brown")

        proofExists = False
        exImDict = fsm.Data.Sec.extraImagesDict(subsection)

        if k in list(exImDict.keys()):
            exImNames = exImDict[k]
            proofExists = len([i for i in exImNames if "proof" in i.lower()]) != 0

        openProofsUIEntry = _uuicom.TOCLabelWithClick(tempFrameRow2, 
                                        text = self.__EntryUIs.proof.name, 
                                        prefix = "contentOpenProofsUIEntry" + nameId,
                                        row = 1, 
                                        column = self.__EntryUIs.proof.column)
        if proofExists:
            openProofsUIEntry.changeColor("brown")

        openProofsUIEntry.imIdx = k
        openProofsUIEntry.subsection = subsection
        openProofsUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openProofsMenu])


        uiResizeEntryIdx = fsm.Data.Sec.imageUIResize(subsection)

        if k in list(uiResizeEntryIdx.keys()):
            resizeFactor = float(uiResizeEntryIdx[k])
        else:
            resizeFactor = 1.0

        changeImSize = _uuicom.ImageSize_ETR(tempFrameRow2,
                                        prefix = "contentUpdateEntryText" + nameId,
                                        row = 0, 
                                        column = self.__EntryUIs.changeImSize.column,
                                        imIdx = k,
                                        text = resizeFactor)
        changeImSize.imIdx = k
        changeImSize.subsection = subsection
        changeImSize.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                [resizeEntryImgCMD])

        showLinks = False

        if (showLinks):
            # adding a frame to show global links
            linksFrame = _uuicom.TOCFrame(tempFrame,
                                prefix = "contentLinksFr_" + nameId,
                                row = gridRowStartIdx + 1, column = 0, columnspan = 100)
            linksFrame.subsection = subsection
            linksFrame.imIdx = k

            imGlobalLinksDict = fsm.Data.Sec.imGlobalLinksDict(subsection)

        tocWImageDict = fsm.Data.Sec.tocWImageDict(subsection)

        tempFrameRow1.render()
        textLabelPage.render()

        # addLinkEntry.render()
        addExtraImage.render()
        addProofImage.render()
        copyLinkEntry.render()
        pasteLinkEntry.render()

        if not textOnly:
            retakeImageForEntry.render()

        showLinks = False

        chkbtnShowPermamently.render()
        imageGroupOM.render()

        openExUIEntry.render()
        openProofsUIEntry.render()
        openNoteUIEntry.render()
        openEntryNoteUIEntry.render()
        openEntryWikiUIEntry.render()
        showLinksForEntry.render()
        copyEntry.render()
        pasteAfterEntry.render()
        copyTextToMem.render()
        openBookCodeProject.render()
        openSubsectionCodeProject.render()
        openEntryCodeProject.render()

        if not textOnly:
            changeImSize.render()

        _uuicom.bindChangeColorOnInAndOut(showImages, shouldBeBrown = True)
        _uuicom.bindChangeColorOnInAndOut(copyEntry)
        _uuicom.bindChangeColorOnInAndOut(pasteAfterEntry)
        _uuicom.bindChangeColorOnInAndOut(retakeImageForEntry)
        _uuicom.bindChangeColorOnInAndOut(showLinksForEntry, shouldBeBrown = linkExist)
        _uuicom.bindChangeColorOnInAndOut(addExtraImage)
        _uuicom.bindChangeColorOnInAndOut(addProofImage)
        _uuicom.bindChangeColorOnInAndOut(copyLinkEntry)
        _uuicom.bindChangeColorOnInAndOut(pasteLinkEntry)
        _uuicom.bindChangeColorOnInAndOut(openExUIEntry, shouldBeBrown = excerciseExists)
        _uuicom.bindChangeColorOnInAndOut(openNoteUIEntry, shouldBeBrown = notesExist)
        _uuicom.bindChangeColorOnInAndOut(openEntryNoteUIEntry)
        _uuicom.bindChangeColorOnInAndOut(openEntryWikiUIEntry)
        _uuicom.bindChangeColorOnInAndOut(openProofsUIEntry, shouldBeBrown = proofExists)
        _uuicom.bindChangeColorOnInAndOut(copyTextToMem)
        _uuicom.bindChangeColorOnInAndOut(openBookCodeProject)
        _uuicom.bindChangeColorOnInAndOut(openSubsectionCodeProject)
        _uuicom.bindChangeColorOnInAndOut(openEntryCodeProject)

        tempFrame.render()
        return showImages


class TOC_BOX(ww.currUIImpl.ScrollableBox,
              dc.AppCurrDataAccessToken):
    class __EntryUIs:
        class __EntryUIData:
            def __init__(self, name, column) -> None:
                self.name = name
                self.column = column

        # row 1
        full = __EntryUIData("[f]", 1)
        im = __EntryUIData("[i]", 2)
        copyLink = __EntryUIData("[cl]", 3)
        pasteLink = __EntryUIData("[pl]", 4)
        copy = __EntryUIData("[c]", 5)
        pasteAfter = __EntryUIData("[p]", 6)
        excercises = __EntryUIData("[e]", 7)
        group = __EntryUIData("", 8)

        # row 2
        showLinks = __EntryUIData("[Links]", 1)
        alwaysShow = __EntryUIData("", 2)
        changeImSize = __EntryUIData("", 3)
        delete = __EntryUIData("[Delete]", 4)
        retake = __EntryUIData("[Retake]", 5)
        addExtra = __EntryUIData("[Add exta]", 6)
        addProof = __EntryUIData("[Add proof]", 7)
        showSubentries = __EntryUIData("[Show sub]", 8)
        leadingEntry = __EntryUIData("", 9)
        shift = __EntryUIData("[Shift Up]", 10)
        copyText = __EntryUIData("[Copy text]", 11)

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
        self.groupAsETR = TOC_BOX.groupAsETR()

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

        while pwidget != self.parent:
            if pwidget == None:
                break
            posy += pwidget.getYCoord()
            pwidget = pwidget.getParent()

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

        pos = posy - self.yPosition()
        height = self.getFrameHeight()
        self.moveY((pos / height))
    
    def __renderWithScrollAfter(self):
        self.shouldScroll = False
        self.render()
        self.shouldScroll = True

        if self.currEntryWidget != None:
            self.currEntryWidget.clicked = False
            self.currEntryWidget.generateEvent(ww.currUIImpl.Data.BindID.mouse1)

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

    def pasteGlLinkCmd(self, event, *args):
        pasteGlLinkCmd(event, *args)
        self.notify(EntryWindow_BOX)

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

    def onFullEntryMove(self):
        currSubsection = fsm.Data.Book.subsectionOpenInTOC_UI
        currEntryIdx = fsm.Data.Book.entryImOpenInTOC_UI
        hash = currSubsection + currEntryIdx

        shownEntryFrame = None

        for k, efm in self.entryWidgetManagers.items():
            if k != hash:
                efm.hideImages()
                efm.changeFullMoveColor(True)
            else:
                efm.showImages()
                efm.changeFullMoveColor(False)
                shownEntryFrame = efm.entryFrame

        if shownEntryFrame != None:
            self.shouldScroll = True
            self.scrollIntoView(None, shownEntryFrame)

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
        
                
        entryWidgetFactory = _uuicom.EntryWidgetFactory(subsection, imIdx, frame, self, 0, 0)
        self.entryWidgetManagers[subsection + imIdx] = entryWidgetFactory.entryFrameManager
        entryWidgetFactory.produceEntryWidgetsForTOCFrame()

        return

        def __showIMagesONClick(event, label:_uuicom.TOCLabelWithClick, subSecID, 
                                shouldScroll = False, 
                                imPad = 120, link = False, textOnly = False,
                                tempRow = None,
                                *args):
            label:_uuicom.TOCLabelWithClick = event.widget
            imIdx = label.imIdx
            subsection = label.subsection

            for w in self.currSecondRowLabels:
                if (w.subsection == subsection) and (w.imIdx == imIdx):
                    w.render()

                    if not self.showAll:
                        self.currentEntrySubsection = subsection
                        self.currentEntryImIdx = imIdx
                else:
                    w.hide()

            if int(event.type) == 4:
                self.subsectionClicked = subsection
                fsm.Data.Book.subsectionOpenInTOC_UI = subsection
                self.entryClicked = imIdx
                fsm.Data.Book.entryImOpenInTOC_UI = imIdx

            if int(event.type) == 4:
                self.notify(EntryWindow_BOX, data = [subsection, imIdx])

            uiResizeEntryIdx = fsm.Data.Sec.imageUIResize(subsection)

            for k,w in self.showImagesLabels.items():
                if k == subsection + imIdx:
                    showImages = self.showImagesLabels[subsection + imIdx]
                    showImages.changePermamentColor("brown")
                else:
                    showImages = self.showImagesLabels[k]
                    showImages.changePermamentColor("white")

            if label.alwaysShow:
                tframe = label.getGrandParent()
                bindData  = [[ww.currUIImpl.Data.BindID.customTOCMove], 
                            [lambda event: self.scrollIntoView(event)]]
                

                uiResizeEntryIdx = fsm.Data.Sec.imageUIResize(subsection)

                if uiResizeEntryIdx.get(imIdx) != None:
                    resizeFactor = float(uiResizeEntryIdx[imIdx])
                else:
                    resizeFactor = 1.0

                imLabel = _uuicom.addMainEntryImageWidget(tframe, subsection, imIdx, 
                                                                    imPad, self.displayedImages, 
                                                                    bindData, resizeFactor = resizeFactor,
                                                                    tocBox = self)

                imLabel.render()
                if int(event.type) == 4:
                    self.scrollIntoView(None, imLabel)
                
                def skipProofAndExtra(subsection, imIdx, exImIdx):
                    extraImages = fsm.Data.Sec.extraImagesDict(subsection)[imIdx]
                    eImText = extraImages[exImIdx]
                    return (("proof" in eImText.lower())\
                            or (("proof" in eImText.lower()) and self.showAll))\
                            or (("extra") in eImText.lower())

                exImLabels = _uuicom.addExtraEntryImagesWidgets(tframe, subsection, imIdx,
                                                                imPadLeft = imPad, 
                                                                displayedImagesContainer = self.displayedImages,
                                                                skippConditionFn = skipProofAndExtra, 
                                                                tocFrame = self, 
                                                                createExtraWidgets = True)
                for l in exImLabels:
                    l.render()

            if tempRow != None:
                tempRow.render()
            return

        def openSecondaryImage(widget:_uuicom.TOCLabelWithClick):
            def __cmd(event = None, *args):
                widget = event.widget
                imIdx = widget.imIdx
                subsection = widget.subsection

                pdfMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                                        wf.Wr.MenuManagers.PdfReadersManager)
                pdfMenuManager.addSecondaryFrame(subsection, imIdx)
            
            widget.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])

        def shiftEntryCmd(event, *args):
            widget = event.widget
            fsm.Wr.SectionInfoStructure.shiftEntryUp(widget.subsection,
                                                        widget.imIdx)
            self.widgetToScrollTo = None
            self.__renderWithScrollAfter()

        def copyEntryCmd(event, *args):
            widget = event.widget
            self.entryCopySubsection = widget.subsection
            self.entryCopyImIdx = widget.imIdx
            self.cutEntry = False

        def cutEntryCmd(event, *args):
            widget = event.widget
            self.entryCopySubsection = widget.subsection
            self.entryCopyImIdx = widget.imIdx
            self.cutEntry = True

        def retakeImageCmd(event, entrylLabel, *args):
            widget = event.widget
            subsection = widget.subsection
            imIdx = widget.imIdx

            currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            
            msg = "Do you want to retake entry image?"
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

            if not response:
                return

            imagePath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBookPath,
                                                                        subsection,
                                                                        str(imIdx))
            ocf.Wr.FsAppCalls.deleteFile(imagePath)
            figuresLabelsData = fsm.Data.Sec.figuresLabelsData(subsection)
            figuresData = fsm.Data.Sec.figuresData(subsection)

            if figuresLabelsData.get(str(imIdx)) != None:
                figuresLabelsData.pop(str(imIdx))
            
            if figuresData.get(str(imIdx)) != None:
                figuresData.pop(str(imIdx))
            

            fsm.Data.Sec.figuresLabelsData(subsection, figuresLabelsData)
            fsm.Data.Sec.figuresData(subsection, figuresData)

            dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                wf.Wr.MenuManagers.PdfReadersManager).show(subsection = subsection,
                                                                            imIdx = imIdx,
                                                                            selector = True,
                                                                            removePrevLabel = True)
            def __cmdAfterImageCreated(self):
                timer = 0

                while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                    time.sleep(0.3)
                    timer += 1

                    if timer > 50:
                        break
                
                entrylLabel.generateEvent(ww.currUIImpl.Data.BindID.mouse1)
            
            t = Thread(target = __cmdAfterImageCreated, args = [self])
            t.start()

        def pasteEntryCmd(event, *args):
            widget = event.widget

            if None in [self.entryCopySubsection, self.entryCopyImIdx] or\
                _u.Token.NotDef.str_t in [self.entryCopySubsection, self.entryCopyImIdx]:
                _u.log.autolog("Did not paste entry. The copy data is not correct.")
                return

            fsm.Wr.SectionInfoStructure.insertEntryAfterIdx(self.entryCopySubsection,
                                                            self.entryCopyImIdx,
                                                            widget.subsection,
                                                            widget.imIdx,
                                                            self.cutEntry,
                                                            shouldAsk = True)
            self.__renderWithScrollAfter()

        def showSubentriesCmd(event, *args):
            widget = event.widget
            
            showSubentries = fsm.Data.Sec.showSubentries(widget.subsection)
            if showSubentries.get(imIdx) != None:
                showSubentries[widget.imIdx] = not showSubentries[widget.imIdx]
            else:
                showSubentries[widget.imIdx] = True
    
            fsm.Data.Sec.showSubentries(widget.subsection, showSubentries)

            self.__renderWithScrollAfter()

        def changeLeadingEntryCmd(event, subsection, imIdx,  *args):
            widget = event.widget

            leadingEntryIdx = widget.getData()

            leadingEntry = fsm.Data.Sec.leadingEntry(subsection)
            leadingEntry[imIdx] = leadingEntryIdx
            fsm.Data.Sec.leadingEntry(subsection, leadingEntry)

            self.__renderWithScrollAfter()

        def removeEntryCmd(event, *args):
            widget = event.widget
            fsm.Wr.SectionInfoStructure.removeEntry(widget.subsection, widget.imIdx)

            def __afterDeletion(*args):
                timer = 0
                while fsm.Data.Sec.figuresLabelsData(subsection).get(widget.imIdx) != None:
                    time.sleep(0.3)
                    timer += 1
                    if timer > 50:
                        break

                pdfReaderManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                                    wf.Wr.MenuManagers.PdfReadersManager)
                pdfReaderManager.show(subsection = widget.subsection, 
                                        imIdx = str(widget.imIdx), 
                                        removePrevLabel = True)

            t = Thread(target = __afterDeletion)
            t.start()

            self.__renderWithScrollAfter()

        def addExtraImCmd(event, l, *args):
            widget:_uuicom.TOCLabelWithClick = event.widget
            _uuicom.addExtraIm(widget.subsection, widget.imIdx, False, entryLabel = l)

        def addExtraImProofCmd(event, l, *args):
            widget:_uuicom.TOCLabelWithClick = event.widget
            _uuicom.addExtraIm(widget.subsection, widget.imIdx, True, entryLabel = l)

        def copyGlLinkCmd(event, *args):
            widget:_uuicom.TOCLabelWithClick = event.widget
            dt.UITemp.Link.subsection = widget.subsection
            dt.UITemp.Link.imIdx = widget.imIdx

        def openExcerciseMenu(event, *args):
            exMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.ExcerciseManager)
            exMenuManger.subsection = event.widget.subsection
            exMenuManger.imIdx = event.widget.imIdx

            event.widget.shouldShowExMenu = not event.widget.shouldShowExMenu
            if (event.widget.shouldShowExMenu):
                exMenuManger.show()
            else:
                exMenuManger.hide()

        def copyTextToMemCmd(event, *args):
            dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                        wf.Wr.MenuManagers.PdfReadersManager).show(subsection = event.widget.subsection,
                                                                    imIdx = event.widget.imIdx,
                                                                    selector = True,
                                                                    getTextOfSelector = True, 
                                                                    withoutRender = True)

        def updateEntry(event, *args):
            widget = event.widget

            imLinkDict = fsm.Data.Sec.imLinkDict(widget.subsection)
            text = imLinkDict[widget.imIdx]

            textLabelPage = _uuicom.MultilineText_ETR(widget.root, 
                                                        "contentP_" + widget.imIdx + widget.subsection, 
                                                        0,
                                                        0, 
                                                        widget.imageLineIdx, 
                                                        text)
            textLabelPage.imIdx = widget.imIdx
            textLabelPage.subsection = widget.subsection
            #textLabelPage.etrWidget = textLabelPage

            def __getWidgetBack(textEntry:_uuicom.MultilineText_ETR, widget):
                newText = textEntry.getData()
                imLinkDict = fsm.Data.Sec.imLinkDict(textEntry.subsection)
                textOnly = fsm.Data.Sec.textOnly(textEntry.subsection)[textEntry.imIdx]
                imLinkDict[textEntry.imIdx] = newText
                fsm.Data.Sec.imLinkDict(textEntry.subsection, imLinkDict)
                fsm.Wr.SectionInfoStructure.rebuildEntryLatex(textEntry.subsection,
                                                            textEntry.imIdx,
                                                            newText,
                                                            textOnly
                                                            )
                
                widget.render()
                widget.updateImage()
                textEntry.hide()

            textLabelPage.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                                    [lambda *args: __getWidgetBack(textLabelPage, widget)])
            widget.hide()
            textLabelPage.render()
            textLabelPage.forceFocus()

        k = imIdx
        i = int(imIdx)

        if fsm.Data.Sec.imLinkDict(subsection).get(k) != None:
            v = fsm.Data.Sec.imLinkDict(subsection)[k]
        else:
            i = 0
            for i in range(50):
                time.sleep(0.1)
                if fsm.Data.Sec.imLinkDict(subsection).get(k) != None:
                    v = fsm.Data.Sec.imLinkDict(subsection)[k]
                    break
            if fsm.Data.Sec.imLinkDict(subsection).get(k) == None:
                sys.exit()
            

        subSecID = _upan.Names.UI.getWidgetSubsecId(subsection)

        extraImagesDict = fsm.Data.Sec.extraImagesDict(subsection)

        subsectionText:str = fsm.Data.Sec.text(subsection)
        textOnly = fsm.Data.Sec.textOnly(subsection)[str(k)]

        entryImText = fsm.Wr.SectionInfoStructure.getEntryImText(subsection, k)
        
        if k in list(extraImagesDict.keys()):
            for t in extraImagesDict[k]:
                entryImText += t

        if self.searchSubsectionsText:
            tokenInSubsectionText = self.filterToken.lower() not in subsectionText.lower()
        else:
            tokenInSubsectionText = True                   

        if (self.filterToken != ""):
            if (self.filterToken.lower() not in v.lower())\
                and (self.filterToken.lower() not in entryImText.lower())\
                and tokenInSubsectionText:
                return

        imagesGroupDict:dict = fsm.Data.Sec.imagesGroupDict(subsection)
        imagesGroupsWShouldShow:list = fsm.Data.Sec.imagesGroupsList(subsection)
        imagesGroups:list = list(imagesGroupsWShouldShow.keys())

        if imagesGroupDict.get(k) != None:
            currImGroupidx = imagesGroupDict[k]
        else:
            currImGroupidx = 0

        if int(k) > 0 :
            entriesList = list(fsm.Data.Sec.imLinkDict(subsection).keys())
            entriesList.sort(key = int)
            idx = entriesList[entriesList.index(k) - 1] #previous entry

            if imagesGroupDict.get(str(idx)) != None:
                if idx == _u.Token.NotDef.str_t:
                    prevImGroupName = _u.Token.NotDef.str_t
                else:
                    prevImGroupName = imagesGroups[imagesGroupDict[idx]]
            else:
                prevImGroupName = _u.Token.NotDef.str_t
        elif k == _u.Token.NotDef.str_t:
            prevImGroupName = imagesGroups[0]
        else:
            if imagesGroupDict.get(k) != None:
                prevImGroupName = imagesGroups[imagesGroupDict[k]]
            else:
                prevImGroupName = imagesGroups[0]

        if currImGroupidx == _u.Token.NotDef.str_t:
            currImGroupidx = 0

        currImGroupName = imagesGroups[currImGroupidx]

        topPad = 0
        gridRowStartIdx = 1

        if currImGroupName != prevImGroupName:
            if not imagesGroupsWShouldShow[currImGroupName]:
                topPad = 0
            elif (k != "0"):
                topPad = 5

        if self.filterToken != "":
            topPad = 0

        nameId = _upan.Names.Entry.getEntryNameID(subsection, k)

        leadingEntry = fsm.Data.Sec.leadingEntry(subsection)

        if leadingEntry.get(imIdx) != None:
            leftPad = 30
        else:
            leftPad = 0

        tempFrame = _uuicom.TOCFrame(frame,
                                prefix = "contentFr_" + nameId,
                                padding=[leftPad, topPad, 0, 0],
                                row = int(k) + 2, column = 0, columnspan = 100)

        if (currImGroupName != prevImGroupName) or (str(k) == "0"):
            imageGroupFrame = _uuicom.TOCFrame(tempFrame,
                                        prefix = "contentImageGroupFr_" + nameId,
                                        padding=[0, topPad, 0, 0], 
                                        row = 0, column = 0, columnspan = 100)
            imageGroupFrame.render()

            if True:#currImGroupName != "No group":

                def __updateGroup(event, *args):
                    widget = event.widget

                    if widget.group == "No group":
                        return

                    imageGroupLabel = _uuicom.MultilineText_ETR(widget.root, 
                                            "contentGroupP_" + widget.subsection + widget.group, 
                                            widget.row, widget.column, 
                                            "", # NOTE: not used anywhere  
                                            widget.group)
                    imageGroupLabel.subsection = widget.subsection

                    def __getImageBack(event, oldGroupName, imageWidget, *args):
                        etr = event.widget
                        newText = etr.getData()
                        imagesGroupsList = \
                            fsm.Data.Sec.imagesGroupsList(etr.subsection).copy()
                        imagesGroupsList = \
                            {k if k != oldGroupName else newText: v for k,v in imagesGroupsList.items()}
                        fsm.Data.Sec.imagesGroupsList(etr.subsection,
                                                        imagesGroupsList)
                        fsm.Wr.SectionInfoStructure.rebuildGroupOnlyImOnlyLatex(subsection,
                                                                                newText)
                        etr.hide()
                        imageWidget.group = newText
                        imageWidget.updateGroupImage()
                        imageWidget.render()

                    imageGroupLabel.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                                            [lambda e, *args: __getImageBack(e, widget.group, widget)])
                    widget.hide()
                    imageGroupLabel.forceFocus()
                    imageGroupLabel.render()

                if (subsection != self.groupAsETR.subsection) or\
                    (currImGroupName != self.groupAsETR.group):
                    img = getGroupImg(subsection, currImGroupName)
                    imageGroupLabel = _uuicom.TOCLabelWithClick(imageGroupFrame, 
                                                image = img, 
                                                prefix = "contentGroupP_" + nameId,
                                                padding = [30, 0, 0, 0], 
                                                row = 0, column = 0)
                    imageGroupLabel.image = img
                    imageGroupLabel.subsection = subsection
                    imageGroupLabel.group = currImGroupName

                    # NOTE: without rebind groups sometimes not shoing up #FIXME
                    imageGroupLabel.rebind([ww.currUIImpl.Data.BindID.mouse2],
                                            [__updateGroup])

                imageGroupLabel.render()

                if currImGroupName != "No group":
                    hideImageGroupLabel = _uuicom.TOCLabelWithClick(imageGroupFrame, 
                                                            text = "[show/hide]",
                                                            prefix = "contentHideImageGroupLabel_" + nameId,
                                                            row = 0, column = 1)

                    if not self.showAll:
                        hideImageGroupLabel.render()

                    hideImageGroupLabel.subsection = subsection
                    hideImageGroupLabel.imIdx = k
                    hideImageGroupLabel.group = currImGroupName

                    _uuicom.bindChangeColorOnInAndOut(hideImageGroupLabel)

                    def __cmd(e):
                        imagesGroupsList = fsm.Data.Sec.imagesGroupsList(e.widget.subsection)
                        imagesGroupsList[e.widget.group] = not imagesGroupsList[e.widget.group]
                        fsm.Data.Sec.imagesGroupsList(e.widget.subsection, imagesGroupsList)
                        self.__renderWithoutScroll()

                    hideImageGroupLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])

                    newGroup = _uuicom.ImageSize_ETR(imageGroupFrame,
                            prefix = "contentNewGroupImageGroupLabel_" + nameId,
                            row = 0, 
                            column = 3,
                            imIdx = k,
                            text = currImGroupName,
                            width = 10)
                    newGroup.subsection = subsection
                    newGroup.render()
                    newGroup.setData(currImGroupName)

                    moveGroup = _uuicom.ImageSize_ETR(imageGroupFrame,
                            prefix = "contentMoveImageGroupLabel_" + nameId,
                            row = 0, 
                            column = 2,
                            imIdx = k,
                            text = subsection + ":" + str(k),
                            width = 10)
                    moveGroup.subsection = subsection
                    moveGroup.imIdx = k

                    def __moveGroup(e, *args): 
                        subsection = e.widget.subsection
                        imIdx = e.widget.imIdx
                        # NOTE: this is a hack but I can't find a better way atm
                        newGroupNameWName = "contentNewGroupImageGroupLabel_".lower()
                        newGroupNameW = [i for i in e.widget.getParent().getChildren() \
                                            if newGroupNameWName.lower() in i.name][0]

                        targetWholePath:str = e.widget.getData()

                        if ":" not in targetWholePath:
                            _u.log.autolog("Incorrect destination path")

                        targetSubsection = targetWholePath.split(":")[0]
                        targetEntryIdx = targetWholePath.split(":")[1]
                        targetGroupName = newGroupNameW.getData() if newGroupNameW.getData() != "" else "No group"
                        sourceSubsection = subsection
                        sourceEntryIdx = imIdx
                        sourceGroupNameIdx = fsm.Data.Sec.imagesGroupDict(sourceSubsection)[sourceEntryIdx]
                        sourceGroupName = list(fsm.Data.Sec.imagesGroupsList(sourceSubsection).keys())[sourceGroupNameIdx]

                        # ask the user if we wnat to proceed.
                        msg = "\
    Do you want to move group \n\nto subsection\n'{0}' \n\nand entry: \n'{1}'\n\n with group name \n'{2}'?".format(targetSubsection, 
                                                                                        targetEntryIdx, 
                                                                                        targetGroupName)
                        response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)


                        if not response:
                            return

                        # UI
                        pdfMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                                        wf.Wr.MenuManagers.PdfReadersManager)
                        pdfMenuManager.saveFigures()

                        gm.GeneralManger.moveGroupToSubsection(sourceSubsection, sourceGroupName,
                                                                targetSubsection, targetGroupName, targetEntryIdx)

                        self.widgetToScrollTo = None
                        self.linkFrames = None
                        self.currSecondRowLabels = None
                        self.__renderWithoutScroll()

                        pdfMenuManager.forceUpdate()
                    moveGroup.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                            [__moveGroup])
                    moveGroup.render()

                gridRowStartIdx = 2

        tempFrameRow1 = _uuicom.TOCFrame(tempFrame,
                            prefix = "contentRow1Fr_" + nameId,
                            padding=[0, topPad, 0, 0],
                            row = gridRowStartIdx - 1, 
                            column = 0, columnspan = 100)

        tempFrameRow2 = _uuicom.TOCFrame(tempFrame,
                            prefix = "contentRow2Fr_" + nameId,
                            padding=[60, topPad, 0, 0],
                            row = gridRowStartIdx, 
                            column = 0, columnspan = 100)
        tempFrameRow2.subsection = subsection
        tempFrameRow2.imIdx = k
        self.currSecondRowLabels.append(tempFrameRow2)

        if currImGroupName not in imagesGroups:
            currImGroupName = imagesGroups[0]
            imagesGroupDict[k] = 0
            fsm.Data.Sec.imagesGroupDict(subsection, imagesGroupDict)

        imagesGroup = ImageGroupOM(imagesGroups,
                                   tempFrameRow1, 
                                   subsection,
                                   imIdx,
                                   self,
                                   column = self.__EntryUIs.group.column,
                                   currImGroupName = currImGroupName)

        latexTxt = tff.Wr.TexFileUtils.fromEntryToLatexTxt(k, v)
        pilIm = getEntryImg(latexTxt, subsection, k)

        shrink = 0.7
        pilIm.thumbnail([int(pilIm.size[0] * shrink),int(pilIm.size[1] * shrink)], Image.LANCZOS)
        img = ww.currUIImpl.UIImage(pilIm)

        if (subsection == self.entryAsETR.subsection)\
            and (k == self.entryAsETR.imIdx) :
            textLabelPage = _uuicom.MultilineText_ETR(tempFrameRow1, 
                                                        "contentP_" + nameId, 
                                                        0,
                                                        0, 
                                                        i, 
                                                        v)
            textLabelPage.imIdx = k
            textLabelPage.subsection = subsection
            textLabelPage.etrWidget = textLabelPage
            textLabelPage.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                                    [updateEntry])
            self.entryAsETR.widget = textLabelPage
            textLabelPage.forceFocus()
        else:
            textLabelPage = _uuicom.TOCLabelWithClick(tempFrameRow1,
                                            image = img, 
                                            prefix = "contentP_" + nameId, 
                                            padding= [60, 0, 0, 0],
                                            row = 0, 
                                            column = 0)
            textLabelPage.imIdx = k
            textLabelPage.subsection = subsection
            textLabelPage.etrWidget = textLabelPage
            textLabelPage.imageLineIdx = i
            textLabelPage.entryText = v
            textLabelPage.imagePath = v

            textLabelPage.rebind([ww.currUIImpl.Data.BindID.mouse2],
                                    [updateEntry])
            textLabelPage.image = img

            if (self.entryAsETR.upddatedTextSubsection == subsection) and\
                (self.entryAsETR.upddatedTextImIdx == k):
                self.entryAsETR.upddatedTextSubsection = None
                self.entryAsETR.upddatedTextImIdx = None
                self.updatedWidget = textLabelPage

        textLabelFull = _uuicom.TOCLabelWithClick(tempFrameRow1, 
                                        text = self.__EntryUIs.im.name, 
                                        prefix = "contentFull_" + nameId,
                                        row = 0, 
                                        column = self.__EntryUIs.im.column)
        textLabelFull.subsection = subsection
        textLabelFull.imIdx = k

        showImages = _uuicom.TOCLabelWithClick(tempFrameRow1, 
                                    text = self.__EntryUIs.full.name,
                                    prefix = "contentOfImages_" + nameId,
                                    row = 0,
                                    column = self.__EntryUIs.full.column)
        showImages.imIdx = k
        showImages.subsection = subsection
        showImages.clicked = False
        self.showImagesLabels[subsection + k] = showImages

        imShouldBeBrown = False

        if (subsection == self.subsectionClicked) and (str(k) == self.entryClicked):
            imShouldBeBrown = True 

        if not textOnly:
            showImages.rebind([ww.currUIImpl.Data.BindID.mouse1, ww.currUIImpl.Data.BindID.customTOCMove],
                            [lambda e, t = tempFrameRow2, *args: __showIMagesONClick(e, showImages, subSecID, True,
                                                                  tempRow = t, *args),
                             lambda e, *args: __showIMagesONClick(e, showImages, subSecID, False,
                                                                  *args)])
        else:
            showImages.rebind([ww.currUIImpl.Data.BindID.mouse1, ww.currUIImpl.Data.BindID.customTOCMove],
                            [lambda e, *args: __showIMagesONClick(e, showImages, subSecID, 
                                                                    True, textOnly = True,
                                                                    *args),
                             lambda e, *args: __showIMagesONClick(e, showImages, subSecID, 
                                                                     False, textOnly = True,
                                                                     *args)])

        if str(imIdx) in fsm.Data.Sec.leadingEntry(subsection).values():
            hasSubentries = True
        else:
            hasSubentries = False

        showSubentries = _uuicom.TOCLabelWithClick(tempFrameRow2,
                                        text = self.__EntryUIs.showSubentries.name,
                                        prefix = "contentShowSubentriesEntry" + nameId,
                                        row = 0, 
                                        column = self.__EntryUIs.showSubentries.column)
        showSubentries.imIdx = k
        showSubentries.subsection = subsection
        showSubentries.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [showSubentriesCmd])
        
        if hasSubentries:
            showSubentries.changeColor("brown") 

        if leadingEntry.get(imIdx) != None:
            leadingEntryText = leadingEntry[imIdx]
        else:
            leadingEntryText = _u.Token.NotDef.str_t

        leadingEntry = _uuicom.ImageSize_ETR(tempFrameRow2,
                                            prefix = "leadingEntry_" + nameId,
                                            row = 0, 
                                            column = self.__EntryUIs.leadingEntry.column,
                                            imIdx = i,
                                            text = leadingEntryText)
        
        leadingEntry.imIdx = k
        leadingEntry.subsection = subsection
        leadingEntry.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                                [lambda e, *args: changeLeadingEntryCmd(e, subsection, imIdx)])

        removeEntry = _uuicom.TOCLabelWithClick(tempFrameRow2,
                                        text = self.__EntryUIs.delete.name,
                                        prefix = "contentRemoveEntry" + nameId,
                                        row = 0, 
                                        column = self.__EntryUIs.delete.column)
        removeEntry.imIdx = k
        removeEntry.subsection = subsection
        removeEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [removeEntryCmd])

        shiftEntry = _uuicom.TOCLabelWithClick(tempFrameRow2,
                                                text = self.__EntryUIs.shift.name,
                                                prefix = "contentShiftEntry" + nameId,
                                                row = 0, 
                                                column = self.__EntryUIs.shift.column)
        shiftEntry.imIdx = k
        shiftEntry.subsection = subsection
        shiftEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [shiftEntryCmd])

        copyEntry = _uuicom.TOCLabelWithClick(tempFrameRow1,
                                                text = self.__EntryUIs.copy.name,
                                                prefix = "contentCopyEntry" + nameId,
                                                row = 0, 
                                                column = self.__EntryUIs.copy.column)
        copyEntry.imIdx = k
        copyEntry.subsection = subsection
        copyEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [copyEntryCmd])
        copyEntry.rebind([ww.currUIImpl.Data.BindID.shmouse1],
                            [cutEntryCmd])

        pasteAfterEntry = _uuicom.TOCLabelWithClick(tempFrameRow1,
                                                text = self.__EntryUIs.pasteAfter.name,
                                                prefix = "contentPasteAfterEntry" + nameId,
                                                row = 0, 
                                                column = self.__EntryUIs.pasteAfter.column)
        pasteAfterEntry.imIdx = k
        pasteAfterEntry.subsection = subsection
        pasteAfterEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [pasteEntryCmd])              

        retakeImageForEntry = _uuicom.TOCLabelWithClick(tempFrameRow2,
                                                text =  self.__EntryUIs.retake.name,
                                                prefix = "contentRetakeImageForEntry" + nameId,
                                                row = 0, 
                                                column =  self.__EntryUIs.retake.column)
        retakeImageForEntry.imIdx = k
        retakeImageForEntry.subsection = subsection
        retakeImageForEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                    [lambda e, l = showImages, *args: retakeImageCmd(e, l)])

        addExtraImage = _uuicom.TOCLabelWithClick(tempFrameRow2, 
                                            text = self.__EntryUIs.addExtra.name,
                                            prefix = "contentAddExtraImageEntry" + nameId,
                                            row = 0, 
                                            column = self.__EntryUIs.addExtra.column)
        addExtraImage.imIdx = k
        addExtraImage.subsection = subsection
        addExtraImage.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [lambda e, l = showImages, *args: addExtraImCmd(e, l)])

        addProofImage = _uuicom.TOCLabelWithClick(tempFrameRow2, 
                                            text = self.__EntryUIs.addProof.name,
                                            prefix = "contentAddExtraProofEntry" + nameId,
                                            row = 0, 
                                            column = self.__EntryUIs.addProof.column)
        addProofImage.imIdx = k
        addProofImage.subsection = subsection
        addProofImage.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [lambda e, l = showImages, *args: addExtraImProofCmd(e, l)])

        copyLinkEntry = _uuicom.TOCLabelWithClick(tempFrameRow1, 
                                            text = self.__EntryUIs.copyLink.name,
                                            prefix = "contentCopyGlLinkEntry" + nameId,
                                            row = 0, 
                                            column = self.__EntryUIs.copyLink.column)
        copyLinkEntry.imIdx = k
        copyLinkEntry.subsection = subsection
        copyLinkEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [copyGlLinkCmd])

        pasteLinkEntry = _uuicom.TOCLabelWithClick(tempFrameRow1,
                                            text = self.__EntryUIs.pasteLink.name,
                                            prefix = "contentPasteGlLinkEntry" + nameId,
                                            row = 0, 
                                            column = self.__EntryUIs.pasteLink.column)
        pasteLinkEntry.imIdx = k
        pasteLinkEntry.subsection = subsection
        pasteLinkEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [self.pasteGlLinkCmd])

        openExUIEntry = _uuicom.TOCLabelWithClick(tempFrameRow1, 
                                        text = self.__EntryUIs.excercises.name, 
                                        prefix = "contentOpenExcerciseUIEntry" + nameId,
                                        row = 0, 
                                        column = self.__EntryUIs.excercises.column,
                                        columnspan = 1)
        openExUIEntry.imIdx = k
        openExUIEntry.subsection = subsection
        openExUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openExcerciseMenu])

        copyTextToMem = _uuicom.TOCLabelWithClick(tempFrameRow2, 
                                        text = self.__EntryUIs.copyText.name, 
                                        prefix = "contentCopyTextToMem" + nameId,
                                        row = 0, 
                                        column = self.__EntryUIs.copyText.column,
                                        columnspan = 1)
        copyTextToMem.imIdx = k
        copyTextToMem.subsection = subsection
        copyTextToMem.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [copyTextToMemCmd])

        for l in self.showLinksForSubsections:
            if subsection + "_" + k in l:
                showLinks = True
                break

        tocWImageDict = fsm.Data.Sec.tocWImageDict(subsection)

        if tocWImageDict == _u.Token.NotDef.dict_t:
            alwaysShow = False
        else:
            alwaysShow = tocWImageDict[k] == "1"

        showImages.alwaysShow = alwaysShow

        if ((((subsection == self.subsectionClicked) and (str(k) == self.entryClicked)) or alwaysShow) or\
            ((subsection == self.secondEntrySubsectionClicked) and (str(k) == self.secondEntryClickedImIdx))):
            showImages.clicked = False

            if (not (subsection == self.subsectionClicked and str(k) == self.entryClicked)):
                showImages.generateEvent(ww.currUIImpl.Data.BindID.customTOCMove)
            else:
                self.widgetToScrollTo = showImages

        if imagesGroupsWShouldShow[currImGroupName] or self.showAll:
            tempFrameRow1.render()
            textLabelPage.render()

            textLabelFull.render()

            showImages.render()

            addExtraImage.render()
            addProofImage.render()
            copyLinkEntry.render()
            pasteLinkEntry.render()

            if not textOnly:
                retakeImageForEntry.render()

            openExUIEntry.render()
            shiftEntry.render()
            copyEntry.render()
            pasteAfterEntry.render()
            copyTextToMem.render()
            showSubentries.render()
            leadingEntry.render()

            if not self.showAll:
                imagesGroup.render()
                removeEntry.render()


        if self.entryAsETR.widget == None:
            if not fsm.Data.Sec.isVideo(subsection):
                _uuicom.openOMOnThePageOfTheImage(textLabelPage, subsection, k)
            else:
                _uuicom.openVideoOnThePlaceOfTheImage(textLabelPage, subsection, k)

        if imShouldBeBrown:
            showImages.changeColor("brown")  


        _uuicom.bindChangeColorOnInAndOut(showImages, shouldBeBrown = imShouldBeBrown)
        _uuicom.bindChangeColorOnInAndOut(showSubentries, shouldBeBrown = hasSubentries)
        _uuicom.bindChangeColorOnInAndOut(removeEntry)
        _uuicom.bindChangeColorOnInAndOut(shiftEntry)
        _uuicom.bindChangeColorOnInAndOut(copyEntry)
        _uuicom.bindChangeColorOnInAndOut(pasteAfterEntry)
        _uuicom.bindChangeColorOnInAndOut(retakeImageForEntry)
        _uuicom.bindChangeColorOnInAndOut(addExtraImage)
        _uuicom.bindChangeColorOnInAndOut(addProofImage)
        _uuicom.bindChangeColorOnInAndOut(copyLinkEntry)
        _uuicom.bindChangeColorOnInAndOut(pasteLinkEntry)
        openSecondaryImage(textLabelFull)
        _uuicom.bindChangeColorOnInAndOut(textLabelFull)
        _uuicom.bindChangeColorOnInAndOut(openExUIEntry, shouldBeBrown = True)
        _uuicom.bindChangeColorOnInAndOut(copyTextToMem)

        tempFrame.render()
        prevImGroupName = currImGroupName
        return showImages

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

            fsm.Data.Book.subsectionOpenInTOC_UI = self.subsectionClicked
            fsm.Data.Book.entryImOpenInTOC_UI = self.entryClicked
        elif broadcasterType == mui.ImageGeneration_BTN:
            subsection = data[0]
            imIdx = data[1]
            self.entryClicked = entryClicked
            addedWidget = self.AddEntryWidget(imIdx, subsection, self.subsectionWidgetFrames[subsection])
            addedWidget.generateEvent(ww.currUIImpl.Data.BindID.mouse1)
            self.shouldScroll = True
            self.scrollIntoView(None, addedWidget)
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
                        fsm.Data.Book.subsectionOpenInTOC_UI = subsection
                        fsm.Data.Book.currSection = subsection
                        fsm.Data.Book.currTopSection = subsection.split(".")[0]
                        fsm.Data.Book.entryImOpenInTOC_UI = "-1"

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

        if self.widgetToScrollTo != None:
            self.widgetToScrollTo.generateEvent(ww.currUIImpl.Data.BindID.mouse1)

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
        return [ww.currUIImpl.Data.BindID.Keys.cmdone, ww.currUIImpl.Data.BindID.Keys.cmdtwo], \
               [lambda *args: __largerEntry(), lambda *args: __smallerEntry()]