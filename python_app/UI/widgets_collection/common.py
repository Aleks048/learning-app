from PIL import Image, ImageOps
from threading import Thread
import subprocess
import copy

import UI.widgets_wrappers as ww
import UI.widgets_facade as wf

from UI.widgets_collection.utils import getGroupImg, getEntryImg, bindChangeColorOnInAndOut

import settings.facade as sf
import data.constants as dc
import data.temp as dt
import outside_calls.outside_calls_facade as ocf
import file_system.file_system_facade as fsm
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import UI.widgets_collection.utils as _uuicom
import UI.widgets_data as wd


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

class MultilineText_ETR(ww.currUIImpl.MultilineText):
    def __init__(self, parentWidget, prefix, row, column, imLineIdx, text:str, width = 70, *args, **kwargs):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }

        name = "_MultilineText_ETR_"

        self.imIdx = None
        self.eImIdx = None
        self.subsection = None
        self.etrWidget = None
        self.lineImIdx = None

        self.root = parentWidget

        self.defaultText = text

        while text[-2:] == "\n":
            text = text[:-2]

        text = text.rstrip()

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
     
        super().__init__(prefix,
                         name,
                         parentWidget, 
                         renderData,
                         text = text,
                         wrap = None, 
                         width = width, 
                         height = newHeight, 
                         *args, 
                         **kwargs)

        self.rebind([ww.currUIImpl.Data.BindID.Keys.ctrlv],
                    [lambda *args: self.pasteTextFromClipboard(*args)])
        self.rebind_()

    def rebind_(self, keys = [], funcs = []):
        self.rebind(keys, funcs)
        
        def __boldenText(*args):
            self.wrapSelectedText("\\textbf{", "}")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdb],
                    [lambda *args: __boldenText(*args)])
        

        def __underlineText(*args):
             self.wrapSelectedText("\\underline{", "}")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdu],
                  [lambda *args: __underlineText(*args)])

        def __addNote(*args):
            self.addTextAtStart("\\textbf{NOTE:} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdn],
                  [lambda *args: __addNote(*args)])

        def __addNoteInPlace(*args):
            self.addTextAtCurrent("\\textbf{NOTE:} ")\

        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdshn],
                  [lambda *args: __addNoteInPlace(*args)])

        def __addDef(*args):
            self.addTextAtCurrent("\\textbf{DEF:} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdd],
                  [lambda *args: __addDef(*args)])

        def __addProposion(*args):
            self.addTextAtCurrent("\\textbf{Proposition:} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdshp],
                  [lambda *args: __addProposion(*args)])

        def __addExample(*args):
            self.addTextAtStart("\\textbf{EX:} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmde],
                  [lambda *args: __addExample(*args)])

        def __addLemma(*args):
            self.addTextAtStart("\\textbf{Lemma:} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdl],
                  [lambda *args: __addLemma(*args)])

        def __addCorollary(*args):
            self.addTextAtStart("\\textbf{Corollary:} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdshc],
                  [lambda *args: __addCorollary(*args)])

        def __addCode(*args):
            self.addTextAtStart("\\textbf{Code:} ")

        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmddc],
                    [lambda *args: __addCode(*args)])

        def __addExcercise(*args):
            self.addTextAtStart("\\textbf{\\underline{EXCERCISE:}} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdshe],
                    [lambda *args: __addExcercise(*args)])

        def __addTheorem(*args):
            self.addTextAtStart("\\textbf{Theorem:} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdt],
                    [lambda *args: __addTheorem(*args)])

        def __addProof(*args):
            self.addTextAtStart("proof")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdp],
                  [lambda *args: __addProof(*args)])

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

        if wd.Data.MainEntryLayout.currSize == wd.Data.MainEntryLayout.large:
            newHeight = self.maxHeight + wd.Data.MainEntryLayout.large
        else:
            newHeight = min(newHeight, self.maxHeight)

        self.setCanvasHeight(min(newHeight, self.maxHeight)) #+ wd.Data.MainEntryLayout.currSize)

        if scrollTOC:
            self.notify(TOC_BOX, 
                        data = {EntryWindow_BOX.Notifyers.IDs.changeHeight: \
                                    [newHeight, self.subsection, self.imIdx, True]})
        else:
            self.notify(TOC_BOX, 
                        data = {EntryWindow_BOX.Notifyers.IDs.changeHeight: \
                                    [newHeight, self.subsection, self.imIdx, False]})

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

    def __AddEntryWidget(self, imIdx, subsection, frame):
        if type(fsm.Data.Sec.leadingEntry(subsection)) != dict:
            return

        #NOTE: we should try to have the imports at the top
        from UI.factories.factoriesFacade import EntryWidgetFactoryEntryWindow

        if fsm.Data.Sec.leadingEntry(subsection).get(imIdx) != None:
            leadingEntry = fsm.Data.Sec.leadingEntry(subsection)[imIdx]

            if fsm.Data.Sec.showSubentries(subsection).get(leadingEntry) != None:
                showSubentries = fsm.Data.Sec.showSubentries(subsection)[leadingEntry]
            else:
                showSubentries = True

            if (showSubentries != _u.Token.NotDef.str_t) and (not showSubentries):
                return
        
        entryWidgetFactory = EntryWidgetFactoryEntryWindow(subsection, imIdx, 0, 0)
        entryWidgetFactory.produceEntryWidgetsForFrame(frame, 0)
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
        self.maxHeight = height
        self.originalHeight = height

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
                        height = self.maxHeight,
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
        if self.subsectionWidgetManagers.get(subsection) != None:
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
        #NOTE: we should try to have the imports at the top
        from UI.factories.factoriesFacade import EntryWidgetFactoryTOC

        row = list(self.subsectionWidgetManagers[subsection].entriesWidgetManagers.keys()).index(imIdx)

        etm = self.subsectionWidgetManagers[subsection].entriesWidgetManagers.pop(imIdx)
        frame = etm.entryFrame.rootWidget
        etm.entryFrame.destroy()

        newIdx = str(int(imIdx) + 1)

        if fsm.Data.Book.entryImOpenInTOC_UI == imIdx:
            fsm.Data.Book.entryImOpenInTOC_UI = newIdx

        entryWidgetFactory = EntryWidgetFactoryTOC(subsection, newIdx, 0, 0)
        entryWidgetFactory.produceEntryWidgetsForFrame(frame, row)
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

    def _isSubsectionHidden(self, subsection):
        subsectionsHidden:list = fsm.Data.Book.subsectionsHiddenInTOC_UI
        for subsecHidden in subsectionsHidden:
            subsectionList = subsection.split(".")
            subsectionHiddenList = subsecHidden.split(".")

            subsectionIsHidden = True

            for i in range(len(subsectionHiddenList)):
                if i >= len(subsectionList):
                    return False

                if subsectionHiddenList[i] != subsectionList[i]:
                    subsectionIsHidden = False
                    break

            if subsectionIsHidden and (len(subsection) > len(subsecHidden)):
                return True

        return False

    def onSubsectionShowHide(self, subsection):
        subsectionsHidden:list = fsm.Data.Book.subsectionsHiddenInTOC_UI

        if subsection not in subsectionsHidden:
            # show subsections
            subsections:list = fsm.Wr.BookInfoStructure.getSubsectionsList(subsection)
            
            for i in range(len(subsections)):
                self.addSubsectionEntry(subsections[i], i)
            return

        # hide subsection
        if self._isSubsectionHidden(subsection):
            self.__removeSubsection(subsection)

        self.subsectionWidgetManagers[subsection].removeAllSubsections()

        for k in list(self.subsectionWidgetManagers.keys()).copy():
            if len(k) > len(subsection):
                if k[:len(subsection) + 1] == (subsection + "."):
                    self.subsectionWidgetManagers.pop(k)

    def onSubsectionOpen(self, subsection):
        if wd.Data.General.singleSubsection:
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

class ImageSize_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix, row, column, imIdx, text, width = 3):
        self.subsection = None
        self.imIdx = None
        self.eImIdx = None
        self.textETR = None

        name = "_imageSizeTOC_ETR" + str(imIdx) + "_" + str(self.eImIdx)
        self.defaultText = text

        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
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

class TOCFrame(ww.currUIImpl.Frame):
    def __init__(self, root, prefix, row, column, columnspan = 1, padding = [0, 0, 0, 0]) -> None:
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : column, "row" : row, "columnspan": columnspan},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        name = "_TOCFrame"

        self.subsection = None
        self.imIdx = None

        self.row = row
        self.column = column
        self.columnspan = columnspan

        super().__init__(prefix, name, root, renderData, padding = padding)

class TOCTextWithClick(ww.currUIImpl.Label):
    '''
    this is used to run different commands on whether the label was clicked even or odd times
    '''

    def __init__(self, root, prefix, row, column, columnspan = 1, sticky = ww.currUIImpl.Orientation.NW, text = ""):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : column, "row" : row, "columnspan": columnspan},
            ww.TkWidgets.__name__ : {"padx" : 10, "pady" : 10, "sticky" : sticky}
        }

        name = "_TOCTextWithClick_"

        self.clicked = False
        self.text = text
        
        self.row = row
        self.column = column
        self.columnspan = columnspan
        self.sticky = sticky

        super().__init__(prefix, name, root, renderData, text = self.text)

        self.setStyle(ww.currUIImpl.Data.Styles.entryText)

    def hide(self, **kwargs):
        return super().hide(**kwargs)

    # def __getattr__(self, name: str):
    #     return self.__dict__[f"_{name}"]

    # def __setattr__(self, name, value):
    #     self.__dict__[f"_{name}"] = value

class TOCTextWithClickTextOnlyEntry(TOCTextWithClick):
    width = 60

    def __init__(self, root, prefix, row, column, columnspan=1, sticky=ww.currUIImpl.Orientation.NW, text=""):
        super().__init__(root, prefix, row, column, columnspan, sticky, text)
        self.setWrapLength(self.width * 9)
        self.setWidth(self.width)

    def updateLabel(self):
        self.changeText(fsm.Data.Sec.imageText(self.subsection)[self.imIdx])
        self.setWidth(self.width)

class TOCCanvasWithclick(ww.currUIImpl.Canvas):
    class Label:
        def __init__(self, subsection, imIdx, canvas, 
                     startX, startY, endX, endY,
                     omPage, 
                     labelStartX = None, labelStartY = None):
            self.canvas = canvas
            self.subsection = subsection

            self.id = None
            self.handleId = None
            self.handleId2 = None
            self.tag = None

            self.eImIdx = None

            self.label = None
            self.line = None

            self.movingHandle2 = False

            if len(imIdx.split("_")) == 1:
                self.imIdx = imIdx
            else:
                self.imIdx = imIdx.split("_")[0]
                self.eImIdx = imIdx.split("_")[1]

            self.startX = startX

            if labelStartX == None:
                self.labelStartX = self.startX - 85 if labelStartX == None else labelStartX
            else:
                self.labelStartX = labelStartX

            self.startY = startY

            if labelStartY == None:
                self.labelStartY = self.startY if labelStartY == None else labelStartY
            else:
                self.labelStartY = labelStartY

            self.endX = endX
            self.endY = endY

            self.omPage = omPage

            self.draw()

        def __labelCmd(self, *args):
            mainMathManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                            wf.Wr.MenuManagers.MathMenuManager)
            mainMathManager.moveTocToEntry(self.subsection, self.imIdx)


        def draw(self):
            text = f"{self.subsection}:{self.imIdx}"

            if self.eImIdx != None:
                text += f"_{self.eImIdx}"

            subsecId = self.subsection.replace(".", "_")
            prefix = f"{subsecId}_{self.imIdx}"

            if self.eImIdx != None:
                prefix += f"_{self.eImIdx}"

            name = "_CanvasButton_"
            renderData = {
                ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 0},
                ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.W}
            }
            self.label = ww.currUIImpl.Button(prefix = prefix,
                                 name = name,
                                 text = text,
                                 rootWidget = self.canvas,
                                 renderData = renderData,
                                 cmd = self.__labelCmd
                                 )

            self.label.setStyle("Canvas.TMenubutton")
            self.id = self.canvas.createButton(self.labelStartX, 
                                               self.labelStartY, 
                                               anchor = ww.currUIImpl.Orientation.NW, 
                                               buttonWidget = self.label,
                                               tags = f"button:{self.subsection}:{self.imIdx}")
            self.handleId = self.canvas.createRectangle(self.labelStartX, 
                                        self.labelStartY,
                                        self.labelStartX + 10,
                                        self.labelStartY + 40,
                                        fill = "green",
                                        tags = f"buttonRect:{self.subsection}:{self.imIdx}")
            self.handleId2 = self.canvas.createRectangle(self.labelStartX + 70, 
                                        self.labelStartY,
                                        self.labelStartX + 80,
                                        self.labelStartY - 10,
                                        fill = "green",
                                        tags = f"buttonRect:{self.subsection}:{self.imIdx}")

            def __drawLine(self):
                self.line = self.canvas.createRectangle(self.startX - 5, self.startY,
                                                    self.startX + 1, self.endY,
                                                    fill = "red",
                                                    tags = f"entryLineRect:{self.subsection}:{self.imIdx}")

            def __deleteLine(self):
                if self.line != None:
                    self.canvas.deleteByTag(self.line)
                    self.line = None              

            self.label.rebind(["<Enter>", "<Leave>"], 
                              [lambda *args: __drawLine(self), lambda *args: __deleteLine(self)])

        def moveCenter(self, x, y, handle2 = False):
            width = 80
            height = 40

            if self.movingHandle2:
                handle2 = True

            if not handle2:
                self.labelStartX = x 
                self.labelStartY = y - height
            else:
                self.movingHandle2 = True
                self.labelStartX = x - width
                self.labelStartY = y 

            self.redraw()

        def redraw(self):
            self.deleteLabel()
            self.draw()

        def select(self):
            self.canvas.deleteByTag(self.handleId)
            self.canvas.deleteByTag(self.handleId2)
            if self.label != None:
                self.handleId = self.canvas.createRectangle(self.labelStartX, 
                                        self.labelStartY,
                                        self.labelStartX + 10,
                                        self.labelStartY + 40,
                                        fill = "yellow",
                                        tags = f"buttonRect:{self.subsection}:{self.imIdx}")
                self.handleId2 = self.canvas.createRectangle(self.labelStartX + 70, 
                                        self.labelStartY,
                                        self.labelStartX + 80,
                                        self.labelStartY - 10,
                                        fill = "yellow",
                                        tags = f"buttonRect:{self.subsection}:{self.imIdx}")

        def unselect(self):
            self.canvas.deleteByTag(self.handleId) 
            self.canvas.deleteByTag(self.handleId2) 
            if self.label != None:
                self.handleId = self.canvas.createRectangle(self.labelStartX, 
                                        self.labelStartY,
                                        self.labelStartX + 10,
                                        self.labelStartY + 40,
                                        fill = "green",
                                        tags = f"buttonRect:{self.subsection}:{self.imIdx}")
                self.handleId2 = self.canvas.createRectangle(self.labelStartX + 70,
                                            self.labelStartY,
                                            self.labelStartX + 80,
                                            self.labelStartY - 10,
                                            fill = "green",
                                            tags = f"buttonRect:{self.subsection}:{self.imIdx}")

        def deleteLabel(self):
            if self.id != None:
                self.canvas.deleteByTag(self.id)
                self.canvas.labels = [i for i in self.canvas.labels if i.id != self.id]
                self.label.hide()
                self.id = None
            if self.handleId != None:
                self.canvas.deleteByTag(self.handleId)
                self.canvas.deleteByTag(self.handleId2)
                self.handleId = None
                self.handleId2 = None


        def toDict(self):
            return {
                        "page" : self.omPage,
                        "coords" : [self.startX, self.startY,
                                    self.endX, self.endY],
                        "labelCoords" : [self.labelStartX, self.labelStartY]
                    }

    class Rectangle:
        alpha = 0.3

        cornerWidgetsColor = "black"
        cornerWidgetsOutline = "blue"

        def __init__(self, startX, startY, endX, endY, canvas, color = None) -> None:
            self.startX = startX
            self.startY = startY
            self.endX = endX
            self.endY = endY

            self.id = None
            self.tag = None
            self.color = "yellow"

            if color != None:
                self.color = color
            
            self.cornerWidgetsIds = [None, None, None, None]
            self.imageContainer = None

            self.canvas = canvas
            
            self.draw()
            
            self.tag = f"rectangle_{self.id}"

        @classmethod
        def rectangleFromDict(cls, attrDict:dict, canvas):
            rect = cls(attrDict["startX"],
                       attrDict["startY"],
                       attrDict["endX"],
                       attrDict["endY"],
                       canvas,
                       attrDict["color"]
                       )

            for k,v in attrDict.items():
                setattr(rect, k, v)

            return rect

        def toDict(self):
            propList = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
            propToFilterOut = ["id", "canvas", "imageContainer", "cornerWidgetsColor", "cornerWidgetsIds", "cornerWidgetsOutline"]
            propList = [i for i in propList if i not in propToFilterOut]
            propDict = {"type": "rectangle"}

            for k in propList:
                propDict[k] = getattr(self, k)

            return propDict

        def showCornerWidgets(self):
            self.deleteCornerWidgets()
            radius = 5

            self.cornerWidgetsIds[0] = self.canvas.createOval(self.startX - radius, 
                                                            self.startY - radius,
                                                            self.startX + radius, 
                                                            self.startY + radius,
                                                            fill = self.cornerWidgetsColor, 
                                                            outline = self.cornerWidgetsOutline,
                                                            tags = "cornerWidget")
            self.cornerWidgetsIds[1] = self.canvas.createOval(self.endX - radius, 
                                                            self.startY - radius,
                                                            self.endX + radius, 
                                                            self.startY + radius, 
                                                            fill = self.cornerWidgetsColor, 
                                                            outline = self.cornerWidgetsOutline,
                                                            tags = "cornerWidget")
            self.cornerWidgetsIds[2] = self.canvas.createOval(self.startX - radius, 
                                                            self.endY - radius,
                                                            self.startX + radius, 
                                                            self.endY + radius, 
                                                            fill = self.cornerWidgetsColor, 
                                                            outline = self.cornerWidgetsOutline,
                                                            tags = "cornerWidget")
            self.cornerWidgetsIds[3] = self.canvas.createOval(self.endX - radius, 
                                                            self.endY - radius,
                                                            self.endX + radius, 
                                                            self.endY + radius, 
                                                            fill = self.cornerWidgetsColor, 
                                                            outline = self.cornerWidgetsOutline,
                                                            tags = "cornerWidget")

        def moveCorner(self, x, y, cornerIdx):
            if cornerIdx == 0:
                self.startX = x
                self.startY = y
            elif cornerIdx == 1:
                self.endX = x
                self.startY = y
            elif cornerIdx == 2:
                self.startX = x
                self.endY = y
            elif cornerIdx == 3:
                self.endX = x
                self.endY = y

            self.redraw()
            self.showCornerWidgets()

        def moveCenter(self, x, y):
            width = abs(self.startX - self.endX)
            height = abs(self.startY - self.endY)

            leftHalfWidth = int(width / 2)
            rightHalfWidth = width - leftHalfWidth
            topHalfHight = int(height / 2)
            bottomHalfHight = height - topHalfHight

            self.startX = x - leftHalfWidth
            self.endX = x + rightHalfWidth
            self.startY = y - topHalfHight
            self.endY = y + bottomHalfHight

            self.redraw()
            self.showCornerWidgets()

        def redraw(self):
            self.deleteRectangle()
            self.draw()
        
        def draw(self):
            alpha = int(self.alpha * 255)

            if self.color == "white":
                fill = (255,255,255)
            else:
                fill = (232,255,25) + (alpha,)

            x1, y1, x2, y2 = self.startX, self.startY, self.endX, self.endY
            image = Image.new('RGBA', (abs(int(x2-x1)), abs(int(y2-y1))), fill)
            self.imageContainer = ww.currUIImpl.UIImage(image)

            if not self.canvas.selectingZone:
                self.id =  self.canvas.createImage(x1, y1, 
                                                   image = self.imageContainer, 
                                                   anchor=ww.currUIImpl.Orientation.NW, 
                                                   tag = self.tag)
            else:
                self.id =  self.canvas.createPolygon([x1, y1, x2, y1, x2, y2, x1, y2], 
                                                    fill = '',
                                                    outline = "black",
                                                    tags = self.tag)

        def deleteCornerWidgets(self):      
            for w in self.cornerWidgetsIds:
                if w != None:
                    self.canvas.deleteByTag(w)
            
            self.cornerWidgetsIds = [None, None, None, None]

        def deleteRectangle(self):
            if self.id != None:
                self.deleteCornerWidgets()
                self.canvas.deleteByTag(self.id)

                if self.canvas.drawing:
                    self.canvas.rectangles = [i for i in self.canvas.rectangles if i != None]
                    self.canvas.rectangles = [i for i in self.canvas.rectangles if i.id != self.id]

    def release(self, event):
        if self.movingFigure != None:
            if type(self.movingFigure) == TOCCanvasWithclick.Label:
                self.labels.append(self.movingFigure)
                self.movingFigure.movingHandle2 = False

        self.movingFigure = None
        self.resizingFigure = None

        keys = ["<Mod1-s>", "<Delete>"]
        cmds = [lambda *args: self.saveFigures(stampChanges = True),
                lambda *args: self.deleteSelectedRectangle()]
        self.rebind(keys, cmds)

        if self.selectingZone \
            and self.lastRecrangle != None:
            x = self.lastRecrangle.startX
            y =  self.lastRecrangle.startY
            x1 = self.lastRecrangle.endX
            y1 = self.lastRecrangle.endY
            self.lastRecrangle.deleteRectangle()

            if "image" in dir(self.image):
                im = self.image.image
            else:
                im = self.image
            im = im.crop([x - 1, y - 1, x1 + 1, y1 + 1])

            if self.getTextOfSelector:
                text = _u.getTextFromImage(None, im)

                subprocess.run("pbcopy", text=True, input=text)
                self.selectingZone = False
                self.getTextOfSelector = False
                self.lastRecrangle = None
                self.startCoord = []
                return

            currBookpath = sf.Wr.Manager.Book.getCurrBookFolderPath()

            imPath = ""

            if (self.eImIdx == None) or (self.eImIdx == _u.Token.NotDef.int_t):
                imPath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBookpath, 
                                                                            self.subsection, 
                                                                            self.imIdx)
            else:
                imPath = _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(currBookpath, 
                                                                             self.subsection,
                                                                             self.imIdx,
                                                                             self.eImIdx)

            if (self.eImIdx == None) or (self.eImIdx == _u.Token.NotDef.int_t):
                OMName = fsm.Data.Book.currOrigMatName
                fsm.Wr.OriginalMaterialStructure.setMaterialCurrPage(OMName, self.omPage)
                imLinkOMPageDict = fsm.Data.Sec.imLinkOMPageDict(self.subsection)
                imLinkOMPageDict[self.imIdx] = str(self.omPage)
                fsm.Data.Sec.imLinkOMPageDict(self.subsection, imLinkOMPageDict)

                self.labels.append(TOCCanvasWithclick.Label(self.subsection,
                                                            self.imIdx,
                                                            self,
                                                            x, y, x1, y1,
                                                            self.omPage,
                                                            x - 85, y))
            else:
                self.labels.append(TOCCanvasWithclick.Label(self.subsection,
                                                            f"{self.imIdx}_{self.eImIdx}",
                                                            self,
                                                            x, y, x1, y1,
                                                            self.omPage,
                                                            x - 85, y))
            self.saveFigures()

            im.save(imPath)

            self.selectingZone = False
            self.getTextOfSelector = False
            self.lastRecrangle = None
            self.startCoord = []
            return

        else:
            if self.drawing:
                self.rectangles.append(self.lastRecrangle)
                self.drawing = False

            self.saveFigures()

            self.lastRecrangle = None
            self.startCoord = []

    def clickOnFigure(self, event):
        if self.drawing:
            return

        x1 = event.x
        y1 = event.y

        overlapIds = self.findOverlapping(x1, y1, x1, y1)
        if len(overlapIds) != 0:
            overlapId = overlapIds[-1]

            for l in self.labels:
                if (overlapId == l.handleId) or (overlapId == l.handleId2):
                    l.select()
                else:
                    l.unselect()

            for r in self.rectangles:
                if r != None:
                    for i in range(len(r.cornerWidgetsIds)):
                        if r.cornerWidgetsIds[i] == overlapId:
                            self.draw(event)
                            return

                    if (overlapId == r.id):
                        if (r.cornerWidgetsIds == [None, None, None, None]):
                            self.selectedRectangle = r
                            r.showCornerWidgets()
                    else:
                        r.deleteCornerWidgets()

    def draw(self, event):
        x1 = event.x
        y1 = event.y

        if self.resizingFigure != None:
            self.resizingFigure[0].moveCorner(x1, y1,
                                              self.resizingFigure[1])
            return

        if self.movingFigure != None:
            self.movingFigure.moveCenter(x1, y1)
            return

        if not self.drawing:
            overlapIds = self.findOverlapping(x1, y1, x1, y1)

            if len(overlapIds) != 0:
                overlapId = overlapIds[-1]

                for l in self.labels:
                    if (overlapId == l.handleId) or (overlapId == l.handleId2):
                        self.movingFigure = l

                        if overlapId == l.handleId:
                            l.moveCenter(x1, y1)
                        else:
                            l.moveCenter(x1, y1, True)
                        return

                for r in self.rectangles:
                    if r != None:
                        for i in range(len(r.cornerWidgetsIds)):
                            if r.cornerWidgetsIds[i] == overlapId:
                                self.resizingFigure = [r, i]
                                r.moveCorner(x1, y1, i)
                                return

                        if overlapId == r.id:
                            self.movingFigure = r
                            r.moveCenter(x1, y1)
                            return

        self.drawing = True

        if self.startCoord == []:
            self.startCoord = [x1, y1]

        startx = min(self.startCoord[0], x1)
        starty = min(self.startCoord[1], y1)
        endx = max(self.startCoord[0], x1)
        endy = max(self.startCoord[1], y1)

        cws = self.findByTag("cornerWidget")
        for cw in cws:
            self.delete(cw)

        if self.lastRecrangle != None:
            self.lastRecrangle.deleteRectangle()

        if int(event.state) == 257:
            self.lastRecrangle = TOCCanvasWithclick.Rectangle(startx, starty, endx, endy, 
                                                            self, "white")
        else:
            self.lastRecrangle = TOCCanvasWithclick.Rectangle(startx, starty, endx, endy, 
                                                            self)

    def readFigures(self, *args):
        figuresList = []

        omBookName = fsm.Data.Book.currOrigMatName
        zoomLevel = int(fsm.Wr.OriginalMaterialStructure.getMaterialZoomLevel(omBookName))
        pageSize = fsm.Wr.OriginalMaterialStructure.getMaterialPageSize(omBookName)
        pageSize = [int(i) for i in pageSize]
        pageSizeZoomAffected = [zoomLevel, int((zoomLevel / pageSize[0]) * pageSize[1])]
        widthScale = pageSizeZoomAffected[0] / pageSize[0]
        heightScale = pageSizeZoomAffected[1] / pageSize[1]

        if not self.isPdfPage:
            figuresData = fsm.Data.Sec.figuresData(self.subsection)

            if (self.eImIdx == None) or (str(self.eImIdx) == _u.Token.NotDef.str_t):
                if figuresData.get(self.imIdx) != None:
                    figuresList = copy.deepcopy(figuresData[str(self.imIdx)])
            else:
                if figuresData.get(f"{self.imIdx}_{self.eImIdx}") != None:
                    figuresList = copy.deepcopy(figuresData[f"{self.imIdx}_{self.eImIdx}"])
                else:
                    return
        else:
            figuresList = \
                fsm.Wr.OriginalMaterialStructure.getMaterialPageFigures(omBookName, self.omPage)

            if type(figuresList) != str:
                figuresList = copy.copy(figuresList)

            # NOTE: inafficient and need to be optimised
            subsections = [i for i in fsm.Wr.BookInfoStructure.getSubsectionsList() if "." in i]

            for i in range(len(subsections) - 1, -1, -1):
                subsection = subsections[i]
                subsectionStartPage = int(fsm.Data.Sec.start(subsection))

                if subsectionStartPage > int(self.omPage) + 10:
                    continue

                figuresLabelsData = fsm.Data.Sec.figuresLabelsData(subsection).copy()
               
                for k, l in figuresLabelsData.items():
                    if type(l) == dict:
                        if l["page"] == self.omPage:
                            labelToAdd = TOCCanvasWithclick.Label(subsection,
                                                                k,
                                                                self,
                                                                l["coords"][0] * widthScale,
                                                                l["coords"][1] * heightScale,
                                                                l["coords"][2] * widthScale,
                                                                l["coords"][3] * heightScale,
                                                                self.omPage,
                                                                l["labelCoords"][0] * widthScale,
                                                                l["labelCoords"][1] * heightScale)
                            self.labels.append(labelToAdd)

        self.rectangles = []

        for f in figuresList:
            if type(f) != str:
                if f.get("type") != None:
                    f.pop("type")

                if self.isPdfPage:
                    f["endX"] = f["endX"] * widthScale
                    f["endY"] = f["endY"] * heightScale
                    f["startX"] = f["startX"] * widthScale
                    f["startY"] = f["startY"] * heightScale
                elif (self.resizeFactor != 1.0):
                    f["endX"] = float(f["endX"]) *  (1.0 / self.resizeFactor)
                    f["endY"] = float(f["endY"]) *  (1.0 / self.resizeFactor)
                    f["startX"] = float(f["startX"]) *  (1.0 / self.resizeFactor)
                    f["startY"] = float(f["startY"]) *  (1.0 / self.resizeFactor)

            rect = TOCCanvasWithclick.Rectangle.rectangleFromDict(f, self)
            self.rectangles.append(rect)

    def saveFigures(self, stampChanges = False, *args):
        figuresList = []

        omBookName = fsm.Data.Book.currOrigMatName
        zoomLevel = int(fsm.Wr.OriginalMaterialStructure.getMaterialZoomLevel(omBookName))
        pageSize = fsm.Wr.OriginalMaterialStructure.getMaterialPageSize(omBookName)
        pageSize = [int(i) for i in pageSize]
        pageSizeZoomAffected = [zoomLevel, int((zoomLevel / pageSize[0]) * pageSize[1])]
        widthScale = pageSize[0] / pageSizeZoomAffected[0]
        heightScale = pageSize[1] / pageSizeZoomAffected[1]

        for i in range(len(self.rectangles)):
            if self.rectangles[i] != None:
                f= self.rectangles[i].toDict()

                if self.isPdfPage:
                    f["endX"] = f["endX"] * widthScale
                    f["endY"] = f["endY"] * heightScale
                    f["startX"] = f["startX"] * widthScale
                    f["startY"] = f["startY"] * heightScale
                elif self.resizeFactor != 1.0:
                    f["endX"] = float(f["endX"]) *  self.resizeFactor
                    f["endY"] = float(f["endY"]) *  self.resizeFactor
                    f["startX"] = float(f["startX"]) *  self.resizeFactor
                    f["startY"] = float(f["startY"]) *  self.resizeFactor

                figuresList.append(f)
            else:
                self.rectangles.pop(i)

        if not self.isPdfPage:
            figuresData = fsm.Data.Sec.figuresData(self.subsection)

            if (self.eImIdx == None) or (self.eImIdx == _u.Token.NotDef.int_t):
                figuresData[self.imIdx] = figuresList
            else:
                figuresData[f"{self.imIdx}_{self.eImIdx}"] = figuresList

            fsm.Data.Sec.figuresData(self.subsection, figuresData)
            
            mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.scrollToLatestClickedWidget()
        else:
            omBookName = fsm.Data.Book.currOrigMatName
            fsm.Wr.OriginalMaterialStructure.setMaterialPageFigures(omBookName, self.omPage, figuresList)

            for l in self.labels:
                f = l.toDict()

                coords = []
                coords.append(f["coords"][0] * widthScale)
                coords.append(f["coords"][1] * heightScale)
                coords.append(f["coords"][2] * widthScale)
                coords.append(f["coords"][3] * heightScale)
                f["coords"] = coords

                labelCoords = []
                labelCoords.append(f["labelCoords"][0] * widthScale)
                labelCoords.append(f["labelCoords"][1] * heightScale)
                f["labelCoords"] = labelCoords

                figuresLabelsData = fsm.Data.Sec.figuresLabelsData(l.subsection)

                if l.eImIdx == None:
                    figuresLabelsData[l.imIdx] = f
                else:
                    figuresLabelsData[f"{l.imIdx}_{l.eImIdx}"] = f

                fsm.Data.Sec.figuresLabelsData(l.subsection, figuresLabelsData)

        if stampChanges:
            msg = "\
        After saving the figures'."
            _u.log.autolog(msg)
            ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

            proofsManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.ProofsManager)
            proofsManager.refresh(self.subsection, self.imIdx)


    def deleteSelectedRectangle(self, *args):
        if self.selectedRectangle != None:
            for i in range(len(self.rectangles)):
                if self.rectangles[i].id == self.selectedRectangle.id:
                    r = self.rectangles.pop(i)
                    r.deleteRectangle()
                    self.selectedRectangle = None

                    self.saveFigures()

                    mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                wf.Wr.MenuManagers.MathMenuManager)
                    mainManager.scrollToLatestClickedWidget()
                    break

    def __init__(self, root, prefix, row, column, imIdx, subsection, 
                 columnspan = 1, sticky = ww.currUIImpl.Orientation.NW, 
                 image = None, extraImIdx = None,
                 makeDrawable = True, 
                 isPdfPage = False, page = None,
                 resizeFactor = 1.0,
                 imagePath = "",
                 *args, **kwargs) -> None:
        self.root = root

        self.row = row
        self.column = column
        self.columnspan = columnspan
        self.sticky = sticky
        self.image = image
        self.imIdx = imIdx
        self.subsection = subsection
        self.eImIdx = extraImIdx
        self.isPdfPage = isPdfPage
        self.omPage = page
        self.imagePath  = _u.Token.NotDef.str_t
        self.etrWidget = _u.Token.NotDef.no_t
        
        self.imagePath = imagePath
        self.makeDrawable = makeDrawable

        self.imageResize = None
        self.startCoord = []

        self.rectangles = []
        self.labels = []
        self.drawing = False
        self.lastRecrangle = None
        
        self.selectedRectangle = None

        self.selectingZone = False
        self.getTextOfSelector = False

        self.movingFigure = None
        self.resizingFigure = None

        self.__btnClickFuncId = None

        self.resizeFactor = resizeFactor

        if "width" in dir(self.image):
            self.width = self.image.width()
            self.height = self.image.height()
        else:
            self.width = self.image.getWidth()
            self.height = self.image.getHeight()

        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        name = "_Canvas_"

        super().__init__(prefix, name, root, renderData, image, self.width, self.height)
        self.readFigures()

        if makeDrawable:
            if not self.isPdfPage:
                keys, cmds = self.__bindCmd()
                self.rebind(keys, cmds)
            else:
                keys = ["<Enter>", "<Leave>"]

                def __b(*args):
                    keys, cmds = self.__bindCmd()
                    self.rebind(keys, cmds)
                def __ub(*args):
                    keys = self.__unbindCmd()
                    self.unbind(keys)

                cmds = [__b, __ub]
                self.rebind(keys, cmds)

    def refreshImage(self, addBrownBorder = True):
        self.pilIm = Image.open(self.imagePath)
        pilIm = self.pilIm

        newWidth = self.image.getWidth()
        newHeight = self.image.getHeight()
        
        pilIm = pilIm.resize([int(newWidth), int(newHeight)], Image.LANCZOS)

        if addBrownBorder:
            pilIm = ImageOps.expand(pilIm, border = 2, fill = "brown")

        self.image = ww.currUIImpl.UIImage(pilIm)

        super().refreshImage(self.backgroundImage, self.image)

        self.readFigures()

        if self.makeDrawable:
            if not self.isPdfPage:
                keys, cmds = self.__bindCmd()
                self.rebind(keys, cmds)
            else:
                keys = ["<Enter>", "<Leave>"]

                def __b(*args):
                    keys, cmds = self.__bindCmd()
                    self.rebind(keys, cmds)
                def __ub(*args):
                    keys = self.__unbindCmd()
                    self.unbind(keys)

                cmds = [__b, __ub]
                self.rebind(keys, cmds)

    def getEntryWidget(self, subsection, imIdx , eImIdx = None):
        for l in self.labels:
            if (l.subsection == subsection) and (str(l.imIdx) == str(imIdx)):
                if eImIdx == None:
                    return l
                else:
                    if str(l.eImIdx) == str(eImIdx):
                        return l

        return None

    def __bindCmd(self, *args):
        return ["<Shift-B1-Motion>", "<B1-Motion>", "<Button-1>", "<ButtonRelease-1>"],\
               [self.draw, self.draw, self.clickOnFigure, self.release]

    def __unbindCmd(self, *args):
        return ["<Shift-B1-Motion>", "<B1-Motion>", "<Button-1>", 
                "<ButtonRelease-1>", "<Mod1-s>", "<Delete>"]

class TOCLabelWithClick(ww.currUIImpl.Label):
    '''
    this is used to run different commands on whether the label was clicked even or odd times
    '''
    def __init__(self, root, prefix, row, column, columnspan = 1, 
                 sticky = ww.currUIImpl.Orientation.NW, padding = [0, 0 ,0, 0], image = None, text = None) -> None:   
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row, "columnspan" : columnspan},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : sticky}
        }
        name = "_TOCLabelWithClick_"

        self.root = root
        self.clicked = False
        self.imIdx = ""
        self.eImIdx = ""
        self.subsection = ""
        self.imagePath = ""
        self.group = ""
        self.image = image
        self.text = text
        self.alwaysShow = None
        self.shouldShowExMenu = False
        self.shouldShowProofMenu = False
        self.shouldShowNotesMenu = False
        self.lineImIdx = _u.Token.NotDef.str_t
        self.solImIdx = _u.Token.NotDef.str_t
        self.etrWidget = _u.Token.NotDef.str_t
        self.sticky = None
        self.tocFrame = None
        self.eImIdx = None
        self.targetSubssection = None
        self.targetImIdx = None
        self.sourceSubssection = None
        self.sourceImIdx= None
        self.sourceWebLinkName = None
        self.dictWord = None
        self.dictText = None

        self.imageLineIdx = None
        self.entryText = None

        self.imagePath = None

        self.row = row
        self.column = column
        self.columnspan = columnspan
        self.sticky = sticky

        super().__init__(prefix, name, root, 
                            renderData, 
                            image = self.image,
                            text = self.text,
                            padding = padding)

    def updateImage(self, image):
        super().updateImage(image)

    def changePermamentColor(self, newColor):
        super().changeColor(newColor)
        if newColor == "brown":
            bindChangeColorOnInAndOut(self, shouldBeBrown = True)
        else:
            bindChangeColorOnInAndOut(self, shouldBeBrown = False)

class TOCLabelWithClickEntry(TOCLabelWithClick):
    def updateLabel(self):
        pilIm = getEntryImg("no", self.subsection, self.imIdx)

        shrink = 0.7
        pilIm.thumbnail([int(pilIm.size[0] * shrink),int(pilIm.size[1] * shrink)], Image.LANCZOS)
        self.image = ww.currUIImpl.UIImage(pilIm)
        super().updateImage(self.image)

class TOCLabelWithClickGroup(TOCLabelWithClick):
    def updateLabel(self):
        self.image = getGroupImg(self.subsection, self.group)
        super().updateImage(self.image)

class TOCLabeWithClickSubsection(TOCLabelWithClick):   
    def updateLabel(self):
        if self.subsection in list(fsm.Data.Book.sections.keys()):
            topSectionImgPath = _upan.Paths.Screenshot.Images.getTopSectionEntryImageAbs(
                                                            sf.Wr.Manager.Book.getCurrBookName(),
                                                            self.subsection)

            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(topSectionImgPath):
                self.result = Image.open(topSectionImgPath)
            else:
                self.result = fsm.Wr.SectionInfoStructure.rebuildTopSectionLatex(self.subsection,
                                                                            _upan.Names.Subsection.getTopSectionPretty)
            result = self.result
            shrink = 0.8
            result.thumbnail([int(result.size[0] * shrink),int(result.size[1] * shrink)], Image.LANCZOS)
            self.image = ww.currUIImpl.UIImage(result)
            super().updateImage(self.image)
        else:
            subsectionImgPath = _upan.Paths.Screenshot.Images.getSubsectionEntryImageAbs(
                                                            sf.Wr.Manager.Book.getCurrBookName(), 
                                                            self.subsection)

            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(subsectionImgPath):
                self.result = Image.open(subsectionImgPath)
            else:
                self.result = \
                    fsm.Wr.SectionInfoStructure.rebuildSubsectionImOnlyLatex(self.subsection, 
                                                                            _upan.Names.Subsection.getSubsectionPretty)
            result = self.result
            shrink = 0.8
            result.thumbnail([int(result.size[0] * shrink),int(result.size[1] * shrink)], Image.LANCZOS)
            self.image = ww.currUIImpl.UIImage(result)
            super().updateImage(self.image)


class MainRoot(ww.currUIImpl.RootWidget):

    def __init__(self, width, height):
        super().__init__(width, height, self.__bindCmd)
    
    def __bindCmd(self):
        def __largerEntry():
            mainMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                            wf.Wr.MenuManagers.MathMenuManager)
            dt.UITemp.Layout.noMainEntryShown = False
            wd.Data.MainEntryLayout.currSize = wd.Data.MainEntryLayout.large
            mainMenuManager.changeLowerSubframeHeight()
        
        def __normalEntry():
            mainMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                            wf.Wr.MenuManagers.MathMenuManager)
            dt.UITemp.Layout.noMainEntryShown = False
            wd.Data.MainEntryLayout.currSize = wd.Data.MainEntryLayout.normal
            mainMenuManager.changeLowerSubframeHeight()
        
        def __smallerEntry():
            mainMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                            wf.Wr.MenuManagers.MathMenuManager)
            dt.UITemp.Layout.noMainEntryShown = False
            wd.Data.MainEntryLayout.currSize = wd.Data.MainEntryLayout.small
            mainMenuManager.changeLowerSubframeHeight()
        
        def __noEntry():
            mainMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                            wf.Wr.MenuManagers.MathMenuManager)
            dt.UITemp.Layout.noMainEntryShown = True
            wd.Data.MainEntryLayout.currSize = wd.Data.MainEntryLayout.no
            mainMenuManager.changeLowerSubframeHeight() 

        def __changeLinksSize():
            wd.Data.MainEntryLayout.largeLinks = not wd.Data.MainEntryLayout.largeLinks
            mainMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                            wf.Wr.MenuManagers.MathMenuManager)
            mainMenuManager.changeLinksSize() 

        def __changeOpeningSingleSubsection(*args):
            wd.Data.General.singleSubsection = not wd.Data.General.singleSubsection

        return [ww.currUIImpl.Data.BindID.Keys.cmdnine, 
                ww.currUIImpl.Data.BindID.Keys.cmdeight,
                ww.currUIImpl.Data.BindID.Keys.cmdseven,
                ww.currUIImpl.Data.BindID.Keys.cmdsix,
                ww.currUIImpl.Data.BindID.Keys.cmdsho,
                ww.currUIImpl.Data.BindID.Keys.cmdshh], \
               [lambda *args: __largerEntry(), 
                lambda *args: __normalEntry(),
                lambda *args: __smallerEntry(),
                lambda *args: __noEntry(),
                lambda *args: __changeLinksSize(),
                __changeOpeningSingleSubsection]