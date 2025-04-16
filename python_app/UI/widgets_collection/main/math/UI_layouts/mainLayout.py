import time
import re
from threading import Thread

import file_system.file_system_facade as fsf

import _utils._utils_main as _u
import _utils.pathsAndNames as _upan

import outside_calls.outside_calls_facade as ocf

import UI.widgets_wrappers as ww
import UI.widgets_facade as wf
import UI.widgets_data as wd
import UI.widgets_collection.main.math.manager as mmm
import UI.widgets_collection.main.math.UI_layouts.common as commw
import UI.widgets_collection.common as comw
import UI.widgets_manager as wm
import UI.widgets_collection.utils as _uuicom
import UI.factories.factoriesFacade as wff

import data.constants as dc
import data.temp as dt

import _utils.logging as log

import settings.facade as sf

import scripts.osascripts as oscr
import outside_calls.outside_calls_facade as oscf

import generalManger.generalManger as gm


class ShowAllSubsections_BTN(ww.currUIImpl.Button):
    prevHiddenSubsections = _u.Token.NotDef.list_t.copy()
    showAll = True

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 13},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        name = "_ShowAllSubsections"
        text= "Show subsections"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        data, 
                        self.cmd)

    def cmd(self):
        if self.showAll:
            self.prevHiddenSubsections = fsf.Data.Book.subsectionsHiddenInTOC_UI
            fsf.Data.Book.subsectionsHiddenInTOC_UI = _u.Token.NotDef.list_t.copy()
        else:
            fsf.Data.Book.subsectionsHiddenInTOC_UI = self.prevHiddenSubsections
        
        self.showAll = not self.showAll
        self.notify(comw.TOC_BOX)


class ShowHideLinks_BTN(ww.currUIImpl.Button,
                  dc.AppCurrDataAccessToken):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 13},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        name = "_ShowHideLinks"
        text= "Show/Hide Links"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        data, 
                        self.cmd)

    def cmd(self):
        self.notify(comw.TOC_BOX)


class ExitApp_BTN(ww.currUIImpl.Button,
                  dc.AppCurrDataAccessToken):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 4, "row" : 13},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        name = "_exitApp"
        text= "ExitApp"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        data, 
                        self.cmd)

    def cmd(self):
        import generalManger.generalManger as gm

        self.notify(comw.TOC_BOX)

        gm.GeneralManger.exitApp()
        

class ChooseOriginalMaterial_OM(ww.currUIImpl.OptionMenu):
    prevChoice = ""

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 14},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }
        name = "_chooseOriginalMaterial_OM"

        origMatNames = fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsNames()

        super().__init__(prefix, 
                        name, 
                        origMatNames,
                        patentWidget, 
                        renderData, 
                        self.cmd)
        
        #TODO: set the data to currOrigMaterialName
        currOrigMatName = fsf.Data.Book.currOrigMatName
        self.setData(currOrigMatName)
        self.prevChoice = currOrigMatName
    
    def cmd(self):
        origMatName = self.getData()
        self.prevChoice = origMatName

        origMatCurrPage = fsf.Wr.OriginalMaterialStructure.getMaterialCurrPage(origMatName)
                    
        fsf.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(origMatName, origMatCurrPage)

        pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                wf.Wr.MenuManagers.PdfReadersManager)
        pdfReadersManager.show(page = int(origMatCurrPage))

        '''
        This was used when the pdf app was separate. need to see what is needed before deletion!
        '''

        # update book settings
        fsf.Data.Book.currOrigMatName = origMatName
    
    def render(self):
        names = fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsNames()
        self.updateOptions(names)

        currOrigMatName = fsf.Data.Book.currOrigMatName
        self.setData(currOrigMatName)

        return super().render(self.renderData)

class MainTOCBox(comw.TOC_BOX):
    def addTopSectionEntry(self, topSection, row):
        self.addSectionWidgets(topSection, row, self.scrollable_frame)


        if (topSection == fsf.Data.Book.currTopSection):
            subsections:list = fsf.Wr.BookInfoStructure.getSubsectionsList(topSection)

            for i in range(len(subsections)):
                self.addSubsectionEntry(subsections[i], i)


    def addSubsectionEntry(self, subsection, row):
        if self._isSubsectionHidden(subsection):
            return

        parentSection = ".".join(subsection.split(".")[:-1])
        
        if self.subsectionWidgetManagers.get(parentSection) == None:
            return

        parentManager = self.subsectionWidgetManagers[parentSection]

        self.addSectionWidgets(subsection, row, parentManager.subsectionChildrenSectionsFrame)

        subsections:list = fsf.Wr.BookInfoStructure.getSubsectionsList(subsection)
            
        for i in range(len(subsections)):
            self.addSubsectionEntry(subsections[i], i)


    def addSectionWidgets(self, subsection, row, parentWidget):
        subsectionFactory = wff.SubsectionWidgetFactoryMainTOC(subsection)

        if subsection == _u.Token.NotDef.str_t:
            return

        super().addSubsectionWidgetsManager(subsection, row, parentWidget, subsectionFactory)

        if subsection == fsf.Data.Book.subsectionOpenInTOC_UI:
            super().openSubsection(subsection)
            super().openEntries(subsection)
        elif subsection == fsf.Data.Book.currTopSection:
            super().openSubsection(subsection)

    def populateTOC(self):
        topSections = fsf.Wr.BookInfoStructure.getTopSectionsList()

        text_curr_filtered = topSections

        for i in range(len(text_curr_filtered)):
            subsection = text_curr_filtered[i]
            self.addTopSectionEntry(subsection, i)
        
        self.notify(ScreenshotLocation_LBL)

    def receiveNotification(self, broadcasterType, data = None, entryClicked = None):
        import UI.widgets_collection.main.math.UI_layouts.mainLayout as mui
        if (comw.EntryWindow_BOX in broadcasterType.__bases__) or (comw.EntryWindow_BOX == broadcasterType):
            if data.get(comw.EntryWindow_BOX.Notifyers.IDs.changeHeight) != None:
                data = data.get(comw.EntryWindow_BOX.Notifyers.IDs.changeHeight)

                entryWidgetHeight = data[0]
                self.setCanvasHeight(680 - entryWidgetHeight)
                if data[1] != None:
                    if data[3]:
                        self.shouldScroll = True
                        # self.scrollIntoView(None, self.showImagesLabels[str(data[1]) + str(data[2])])
                        self.shouldScroll = False
            elif data.get(comw.EntryWindow_BOX.Notifyers.IDs.rerenderAndSetMain) != None:
                data = data.get(comw.EntryWindow_BOX.Notifyers.IDs.rerenderAndSetMain)
                if data[2]:
                    self.render()
                    # self.showImagesLabels[str(data[0]) + str(data[1])].generateEvent(ww.currUIImpl.Data.BindID.mouse1)
            elif data.get(comw.EntryWindow_BOX.Notifyers.IDs.setMain) != None:
                data = data.get(comw.EntryWindow_BOX.Notifyers.IDs.setMain)
                # self.showImagesLabels[str(data[0]) + str(data[1])].generateEvent(ww.currUIImpl.Data.BindID.mouse1)
        elif broadcasterType == mui.ExitApp_BTN:
            tsList = fsf.Wr.BookInfoStructure.getTopSectionsList()

            sections = fsf.Data.Book.sections

            for ts in tsList:
                if ts == _u.Token.NotDef.str_t:
                    return

                sections[ts]["showSubsections"] = str(int(self.showSubsectionsForTopSection[ts]))

            fsf.Data.Book.sections = sections
        elif broadcasterType == mui.ImageGeneration_BTN:
            subsection = data[0]
            imIdx = data[1]
            self.entryClicked = entryClicked

            fsf.Data.Book.subsectionOpenInTOC_UI = subsection
            fsf.Data.Book.entryImOpenInTOC_UI = imIdx

            self.AddEntryWidget(imIdx, 
                                subsection, 
                                self.subsectionWidgetManagers[subsection].entriesFrame)

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onFullEntryMove" in dir(w):
                    w.onFullEntryMove()
        elif broadcasterType == mui.ImageGroupAdd_BTN:
            self.renderWithScrollAfter()
        elif broadcasterType == mui.ShowAllSubsections_BTN:
            self.renderWithScrollAfter()
        elif broadcasterType == mui.ShowHideLinks_BTN:
            self.showLinks = not self.showLinks
            self.showLinksForSubsections = []
            self.renderWithScrollAfter()
        else:
            self.renderWithScrollAfter()

    def onFullEntryMove(self):
        super().onFullEntryMove()
        self.notify(ScreenshotLocation_LBL)

    def render(self, shouldScroll=False):
        super().render(shouldScroll)

class ScreenshotLocation_LBL(ww.currUIImpl.Label):
    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 2, "columnspan": 5},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.W}
        }
        name = "_showCurrScreenshotLocation_text"

        if "." in fsf.Data.Book.currSection:
            text_curr = _upan.Paths.Screenshot.getRel_formatted()
        else:
            text_curr = _u.Token.NotDef.str_t

        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data, 
                        text = text_curr)
    
    def receiveNotification(self, broadcasterName, data = None):
        if (broadcasterName == comw.TOC_BOX) or (comw.TOC_BOX in broadcasterName.__bases__):
            text = _upan.Paths.Screenshot.getRel_formatted()
            self.changeText(text)
    
    def render(self):
        if "." in fsf.Data.Book.currSection:
            text_curr = _upan.Paths.Screenshot.getRel_formatted()
        else:
            text_curr = _u.Token.NotDef.str_t

        self.changeText(text_curr)
        return super().render()


class TextOnly_CHB(ww.currUIImpl.Checkbox):
    etenriesTextOnlyDefault = 0

    def __init__(self, parentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 5, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.E}
        }
        name = "_NoImgToTOC_CHB"
        text = "Text Only"
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = renderData, 
                        text = text)
        self.etenriesTextOnlyDefault = bool(fsf.Data.Book.etenriesTextOnlyDefault)
        self.setData(self.etenriesTextOnlyDefault)

    def receiveNotification(self, broadcasterName):
        if broadcasterName == ImageGeneration_ETR:
            prevChoice = self.getData()
            self.setData(not prevChoice)
        else:
            outData =  True if self.getData() == 1 else False
            self.setData(self.etenriesTextOnlyDefault)

            return outData


class addToTOCwImage_CHB(ww.currUIImpl.Checkbox):   
    def __init__(self, parentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 4, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        name = "_toc_w_image"
        text = "TOC entry with image"
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData, 
                        text = text)
        self.setData(False)
    
    def receiveNotification(self, broadcasterName):
        if broadcasterName == ImageGeneration_ETR:
            prevChoice = self.getData()
            self.setData(not prevChoice)
        else:
            prevChoice = self.getData()
            self.setData(False)

            return prevChoice


class ImageGeneration_BTN(ww.currUIImpl.Button,
                          dc.AppCurrDataAccessToken):
    labelOptions = ["imIdx", "imName"]
    dataFromUser = [-1, -1]

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        name = "_imageGeneration_process_BTN"
        text = self.labelOptions[0]

        super().__init__(prefix, 
                        name,
                        text, 
                        patentWidget,
                        data, 
                        self.cmd)
    
    def cmd(self):
        def _createTexForTheProcessedImage():
            import generalManger.generalManger as gm 

            if not re.match("^[0-9]+$", str(self.dataFromUser[0])):
                msg = "Incorrect image index \n\nId: '{0}'.".format(self.dataFromUser[0])
                wm.UI_generalManager.showNotification(msg, True)
                return

            addToTOCwIm = self.notify(addToTOCwImage_CHB)
            textOnly = self.notify(TextOnly_CHB)

            msg = "\
Do you want to create entry with \n\nId: '{0}',\n\n Name: '{1}'".format(self.dataFromUser[0], self.dataFromUser[1])
            response = wm.UI_generalManager.showNotification(msg, True)
            
            if not response:
                # self.rootWidget.render()
                self.notify(ImageGeneration_ETR, None)
                return

            currSubsection = fsf.Data.Book.currSection
            entryAdded:bool = gm.GeneralManger.AddEntry(currSubsection, 
                                                        self.dataFromUser[0], 
                                                        self.dataFromUser[1],
                                                        addToTOCwIm,
                                                        textOnly)

            if not entryAdded:
                self.rootWidget.render()
                self.notify(ImageGeneration_ETR, None)
                return
            
            def __afterImageCreated(self):
                currBorrPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

                currImNum = self.dataFromUser[0]
                imagePath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBorrPath,
                                                                            currSubsection,
                                                                            str(currImNum))
                timer = 1

                if not fsf.Data.Sec.isVideo(currSubsection):
                    while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                        time.sleep(0.3)
                        timer += 1

                        if timer > 50:
                            return False

                fsf.Data.Book.subsectionOpenInTOC_UI = currSubsection
                fsf.Data.Book.entryImOpenInTOC_UI = str(currImNum)

                nextImNum = str(int(currImNum) + 1)

                fsf.Data.Book.subsectionOpenInTOC_UI = currSubsection
                fsf.Data.Book.entryImOpenInTOC_UI = currImNum

                self.rootWidget.render()
                self.notify(ImageGeneration_ETR, nextImNum)
                self.updateLabel(self.labelOptions[0])
                self.notify(comw.TOC_BOX, entryClicked = self.dataFromUser[0], data = [currSubsection, currImNum])

            t = Thread(target = __afterImageCreated, args = [self])
            t.start()
            dt.AppState.ShowProofs.setData(self.appCurrDataAccessToken,
                                           False)

        buttonNamesToFunc = {self.labelOptions[0]: lambda *args: self.notify(ImageGeneration_ETR, ""),
                            self.labelOptions[1]: _createTexForTheProcessedImage}

        sectionImIndex = fsf.Wr.Links.ImIDX.get_curr()
        for i in range(len(self.labelOptions)):
            if self.labelOptions[i] == self.text:
                nextButtonName = self.labelOptions[(i+1)%len(self.labelOptions)]
                self.dataFromUser[i] = str(self.notify(ImageGeneration_ETR, sectionImIndex))
                buttonNamesToFunc[self.labelOptions[i]]()
                self.updateLabel(nextButtonName)
                break


    def receiveNotification(self, broadcasterType):
        if broadcasterType == ImageGeneration_ETR:
            self.cmd()
        if broadcasterType == ImageGenerationRestart_BTN:
            self.updateLabel(self.labelOptions[0])

class ImageGeneration_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "columnspan": 6}
        }
        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {},
            ww.TkWidgets.__name__ : {"width": 60}
        }
        name = "_imageGeneration_ETR"
        defaultText = "0"

        super().__init__(prefix, 
                        name,
                        patentWidget, 
                        data,
                        extraBuildOptions,
                        defaultText = defaultText)

        if "." in fsf.Data.Book.currSection:
            secImIndex = fsf.Wr.Links.ImIDX.get_curr()
        else:
            secImIndex = _u.Token.NotDef.str_t

        if secImIndex == _u.Token.NotDef.str_t:
            self.updateDafaultText(defaultText)
        else:
            self.updateDafaultText(str(int(secImIndex) + 1))
        
        def __boldenText(*args):
            self.wrapSelectedText("\\textbf{", "}")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdb],
                    [lambda *args: __boldenText(*args)])

        def __underlineText(*args):
            self.wrapSelectedText("\\underline", "}")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdu],
                    [lambda *args: __underlineText(*args)])

        def __addNote(*args):
            self.addTextAtStart("\\textbf{NOTE:} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdn],
                    [lambda *args: __addNote(*args)])

        def __addNoteInPlace(*args):
            self.addTextAtCurrent("\\textbf{NOTE:} ")

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

        def __addProof(*args):
            self.addTextAtStart("proof")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdp],
                    [lambda *args: __addProof(*args)])

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

        def __addExcecise(*args):
            self.addTextAtStart("\\textbf{\\underline{EXCERCISE:}} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdshe],
                    [lambda *args: __addExcecise(*args)])

        def __addTheorem(*args):
            self.addTextAtStart("\\textbf{Theorem:} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdt],
                    [lambda *args: __addTheorem(*args)])

        def __notifyImGenerationBtn(*args):
            self.notify(ImageGeneration_BTN)
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                    [lambda *args: __notifyImGenerationBtn(*args)])

        def __notifyImGenerationRestartBtn(*args):
            self.notify(ImageGenerationRestart_BTN)
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.escape],
                    [lambda *args: __notifyImGenerationRestartBtn(*args)])

        def __notifyAlwaysShowChBx(*args):
            self.notify(addToTOCwImage_CHB)
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdshi],
                    [lambda *args: __notifyAlwaysShowChBx(*args)])

        def __notifyTextOnlyChBx(*args):
            self.notify(TextOnly_CHB)
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdsht],
                    [lambda *args: __notifyTextOnlyChBx(*args)])

    def receiveNotification(self, broadcasterType, dataToSet = None):
        if broadcasterType == ImageGenerationRestart_BTN:
            if "." in fsf.Data.Book.currSection:
                currImIdx = int(fsf.Wr.SectionCurrent.getImIDX())
            else:
                currImIdx = _u.Token.NotDef.int_t

            nextImIdx = str(currImIdx + 1)
            self.setData(nextImIdx)
            self.forceFocus()
            return
        elif broadcasterType == ImageGeneration_BTN:
            prevData = self.getData()

            if prevData == "":
                prevData = _u.Token.NotDef.str_t

            if dataToSet != None:
                self.setData(dataToSet)

            self.forceFocus()

            return prevData
        elif broadcasterType == ImageGroupAdd_BTN:
            return self.getData()
        elif broadcasterType == commw.AddWebLink_BTN:
            return self.getData()
    
    def render(self, **kwargs):
        if "." in fsf.Data.Book.currSection:
            secImIndex = fsf.Wr.Links.ImIDX.get_curr()
        else:
            secImIndex = _u.Token.NotDef.str_t

        if secImIndex == _u.Token.NotDef.str_t:
            newIDX = "0"
        else:
            if secImIndex != 0:
                newIDX = str(int(secImIndex) + 1)
            else:
                newIDX = "0"
        
        self.updateDafaultText(newIDX)
        self.setData(newIDX)

        return super().render(**kwargs)

    def defaultTextCMD(self):
        pass

class ImageGenerationRestart_BTN(ww.currUIImpl.Button):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 2, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        name = "_imageGenerationRestart"
        text= "restart"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        data, 
                        self.cmd)

    def cmd(self):
        self.notifyAllListeners()

    def receiveNotification(self, broadcasterType):
        self.cmd()  

class ImageGroupAdd_BTN(ww.currUIImpl.Button,
                        dc.AppCurrDataAccessToken):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        name = "_imageGroupAdd"
        text= "Group Add"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        data, 
                        self.cmd)

    def cmd(self):
        # get Data from the entry
        groupName = self.notify(ImageGeneration_ETR)
        currSubsection = fsf.Data.Book.currSection

        # run restart cmd
        self.notify(ImageGenerationRestart_BTN)

        # ask the user if we want to proceed
        msg = "\
Do you want to add \n\n\
group: '{0}' \n\n\
to subsection: '{1}'?".format(groupName, currSubsection)
        response = wm.UI_generalManager.showNotification(msg, True)

        mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                    mmm.MathMenuManager)
        mainManager.show()

        if fsf.Data.Sec.isVideo(currSubsection):
            videoPlayerManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                        wf.Wr.MenuManagers.VideoPlayerManager)
            entriesList = list(fsf.Data.Sec.imLinkDict(currSubsection).keys())
            entriesList.sort(key = int)
            imIdx = entriesList[-1]
            videoPlayerManager.show(currSubsection, str(imIdx))    
        
        if not response:
            return

        # update the groups list for the subsection
        imGroups:dict = fsf.Data.Sec.imagesGroupsList(currSubsection)
        imGroups[groupName] = True
        fsf.Data.Sec.imagesGroupsList(currSubsection, imGroups)

        dt.AppState.UseLatestGroup.setData(self.appCurrDataAccessToken, True)

        # re-render toc
        self.notify(comw.TOC_BOX)


class MainEntryBox(comw.EntryWindow_BOX): 
    def notificationRetakeImage(self, subsection, imIdx):
        super().setMain(subsection, imIdx)

    def notificationResizeImage(self, subsection, imIdx):
        super().setMain(subsection, imIdx)

    def notificationlinkFullMove(self, subsection, imIdx):
        super().setMain(subsection, imIdx)

    def notificationAfterImageWasCreated(self, subsection, imIdx):
        super().setMain(subsection, imIdx)

    def onLinksShow(self, subsection, imIdx):
        super().updateHeight()

    def onAddExtraImage(self, subsection, mainImIdx, extraImIdx):
        etm = self.entryManager
        if etm != None:
            eImFrame = etm.addExtraImIdx(extraImIdx)
            if eImFrame != None:
                self.scrollIntoView(None, eImFrame)
                self.updateHeight()

    def onTextOnlyTextUpdate(self):
        self.updateHeight()

    def onEntryTextUpdate(self):
        self.updateHeight()

    def onShowLinks(self):
        self.updateHeight()

    def onRemoveLink(self):
        self.updateHeight()

    def onFullEntryMove(self):
        if fsf.Data.Book.entryImOpenInTOC_UI != _u.Token.NotDef.str_t:
            self.subsection = fsf.Data.Book.subsectionOpenInTOC_UI
            self.imIdx = fsf.Data.Book.entryImOpenInTOC_UI
            self.render()
        else:
            #TODO: should update the height()
            self.hideAllWithChildren()
            self.updateHeight()


    def onImageResize(self, subsection, imIdx, eImIdx):
        if (subsection == self.subsection) and (imIdx == self.imIdx):
            if self.entryManager != None:
                if eImIdx == None:
                    self.entryManager.updateMainImage()
                else:
                    self.entryManager.updateExtraImage(eImIdx)
                self.entryManager.updateResizeEtrText()

    def onRetakeAfter(self, subsection, imIdx, eImidx = _u.Token.NotDef.str_t):
        if self.entryManager != None:
            self.entryManager.updateMainImage()

    def onAlwaysShowChange(self, subsection, imIdx):
        if self.entryManager != None:
            for ch in self.entryManager.rowFrame2.getChildren():
                ch.render()

    def onPasteLink(self):
        if self.entryManager != None:
            self.linkFrameShown = True
            self.render()

    def onMainLatexImageUpdate(self, subsection, imIdx):
        if self.entryManager != None:
            etm = self.entryManager
            etm.updateEntryImage()

    def onEntryShift(self, subsection, imIdx):
        pass

    def onExtraImDelete(self, subsection, imIdx, eImIdx):
        if self.entryManager != None:
            etm = self.entryManager
            etm.deleteExtraImage(eImIdx)

    def onExtraImMove(self, subsection, imIdx, eImIdx, moveUp:bool):
        if self.entryManager != None:
            etm = self.entryManager
            eImFrame = etm.moveExtraIm(eImIdx, moveUp)

            if eImFrame != None:
                self.shouldScroll = True
                self.scrollIntoView(None, eImFrame)

    def render(self, scrollTOC=True):
        wd.Data.Reactors.entryChangeReactors[self.name] = self
        wd.Data.Reactors.subsectionChangeReactors[self.name] = self
        super().render(scrollTOC)

        if self.linkFrameShown:
            self.entryManager.linksFrameManager.showLinks()

class ImageCreation:
    pass
