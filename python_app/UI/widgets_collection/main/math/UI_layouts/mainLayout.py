import os
import tkinter as tk
import time
import re

import file_system.file_system_facade as fsf
import tex_file.tex_file_facade as tff

import _utils._utils_main as _u
import _utils.pathsAndNames as _upan

import outside_calls.outside_calls_facade as ocf

import UI.widgets_wrappers as ww
import UI.widgets_collection.main.math.manager as mmm
import UI.widgets_collection.main.math.UI_layouts.common as commw
import UI.widgets_collection.common as comw
import UI.widgets_manager as wm

import layouts.layouts_facade as lf

import data.constants as dc
import data.temp as dt

import settings.facade as sf

import scripts.osascripts as oscr
import outside_calls.outside_calls_facade as oscf

import generalManger.generalManger as gm


class LatestExtraImForEntry_LBL(ww.currUIImpl.Label):
    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 4, "row" : 14},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_latestExtraImForEntry_LBL_text"

        text_curr = self.getText(True)
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data, 
                        text = text_curr)
    
    def getText(self, init = False):
        currSection = fsf.Data.Book.currSection
        entriesDict = fsf.Data.Sec.imLinkDict(currSection)
        extraImagesDict = fsf.Data.Sec.extraImagesDict(currSection)
        
        if init:
            if type(entriesDict) == dict:
                latestEntry = list(entriesDict.keys())[-1]
            else:
                latestEntry = _u.Token.NotDef.str_t
        else:
            latestEntry = self.notify(commw.SourceImageLinks_OM)

        latestExtraImName = "No"

        if type(extraImagesDict) == dict:
            if latestEntry in list(extraImagesDict.keys()):
                latestExtraImName = extraImagesDict[latestEntry][-1]
        else:
            latestExtraImName = _u.Token.NotDef.str_t

        return "E IM: \"" + latestExtraImName + "\""

    def receiveNotification(self, broadcasterName, data = None):
        self.render()
    
    def render(self):
        text_curr = self.getText()
        self.changeText(text_curr)
        return super().render()


class ReAddAllNotesFromTheOMPage_BTN(ww.currUIImpl.Button,
                  dc.AppCurrDataAccessToken):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 15},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_reAddNotes"
        text= "ReAdd notes"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        data, 
                        self.cmd)

    def cmd(self):
        import generalManger.generalManger as gm

        omName = fsf.Data.Book.currOrigMatName
        fileName = fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsFilename(omName)
        cmd = oscr.get_PageOfSkimDoc_CMD(fileName)
        currPage, _ = _u.runCmdAndGetResult(cmd)

        if currPage != None:
            currPage = currPage.split("page ")[1]
            currPage = currPage.split(" ")[0]

        gm.GeneralManger.readdNotesToPage(currPage)

class ShowFirstEntryOfTheCurrPage(ww.currUIImpl.Button):
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 4, "row" : 17},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_ShowFirstEntryOfTheCurrPage"
        text= "Show CP Entry"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        data, 
                        self.cmd)

    def cmd(self):
        origMatName = fsf.Data.Book.currOrigMatName
        materialFilename = \
            fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsFilename(origMatName)

        cmd = oscr.get_PageOfSkimDoc_CMD(materialFilename)
        frontSkimDocumentPage, _ = _u.runCmdAndGetResult(cmd)

        if len(frontSkimDocumentPage.split("page ")) < 2:
            return
        
        if frontSkimDocumentPage != None:
            page = frontSkimDocumentPage.split("page ")[1]
            page = page.split(" ")[0]
        topSectionsList = fsf.Wr.BookInfoStructure.getTopSectionsList()

        for tSection in topSectionsList:
            subsectionsList = fsf.Wr.BookInfoStructure.getSubsectionsList(tSection)

            for subsection in subsectionsList:
                imLinkOMPageDict = fsf.Data.Sec.imLinkOMPageDict(subsection)
                origMatNameDict = fsf.Data.Sec.origMatNameDict(subsection)

                if origMatNameDict != _u.Token.NotDef.dict_t:
                    for eIdx in range(len(origMatNameDict)):
                        if origMatNameDict[str(eIdx)] == origMatName:
                            if str(imLinkOMPageDict[str(eIdx)]) == str(page):
                                self.notify(comw.TOC_BOX, [subsection, str(eIdx)])
                                break

class ShowAllSubsections_BTN(ww.currUIImpl.Button):
    prevHiddenSubsections = _u.Token.NotDef.list_t.copy()
    showAll = True

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 17},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
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


class RebuildCurrentSubsectionLatex_BTN(ww.currUIImpl.Button,
                  dc.AppCurrDataAccessToken):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 2, "row" : 15},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_RebuildCurrentSubsectionLatex"
        text= "Rebuild Latex"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        data, 
                        self.cmd)

    def receiveNotification(self, broadcasterType) -> None:
        if broadcasterType == commw.AddGlobalLink_BTN:
            self.cmd()

    def cmd(self):
        subsection = _upan.Current.Names.Section.name()
        fsf.Wr.SectionInfoStructure.rebuildSubsectionLatex(subsection,
                                                           _upan.Names.Group.formatGroupText,
                                                           _upan.Names.Subsection.getSubsectionPretty,
                                                           _upan.Names.Subsection.getTopSectionPretty)
        self.notify(comw.TOC_BOX)

class ScrollToCurrSubsectionAndBack_BTN(ww.currUIImpl.Button,
                  dc.AppCurrDataAccessToken):
    toSubsection = True

    currTopSection = None 
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 5, "row" : 13},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_ScrollToCurrSubsectionAndBack_BTN"
        text= "Scroll"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        data, 
                        self.cmd)

        self.currTopSection = fsf.Data.Book.currTopSection 
        self.subsection = fsf.Data.Book.subsectionOpenInTOC_UI
        self.imIdx = fsf.Data.Book.entryImOpenInTOC_UI

    def cmd(self):
        self.toSubsection = not self.toSubsection
        self.notify(comw.TOC_BOX,
                    [self.currTopSection,
                    self.subsection,
                    self.imIdx])

    def receiveNotification(self, broadcasterType) -> None:
        self.currTopSection = fsf.Data.Book.currTopSection 
        self.subsection = fsf.Data.Book.subsectionOpenInTOC_UI
        self.imIdx = fsf.Data.Book.entryImOpenInTOC_UI

    


class ExitApp_BTN(ww.currUIImpl.Button,
                  dc.AppCurrDataAccessToken):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 4, "row" : 15},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
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
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 16},
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
        # close original material document
        fsf.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(self.prevChoice)
        prevChoiceID = fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsFilename(self.prevChoice)
        _, _, oldPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, 
                                                    prevChoiceID)     
        
        if oldPID != None:
            lf.Wr.LayoutsManager.closePDFwindow(prevChoiceID, oldPID)
        
        time.sleep(0.3)

        # open another original material
        origMatName = self.getData()
        self.prevChoice = origMatName

        origMatPath = fsf.Wr.OriginalMaterialStructure.getMaterialPath(origMatName)
        origMatCurrPage = fsf.Wr.OriginalMaterialStructure.getMaterialCurrPage(origMatName)

        ocf.Wr.PdfApp.openPDF(origMatPath, origMatCurrPage)

        zoomLevel = fsf.Wr.OriginalMaterialStructure.getMaterialZoomLevel(origMatName)
        pdfToken:str = origMatPath.split("/")[-1].replace(".pdf", "")
        cmd = oscr.setDocumentScale(pdfToken, zoomLevel)
        _u.runCmdAndWait(cmd)

        width, height = _u.getMonitorSize()
        halfWidth = int(width / 2)

        newChoiceID = fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsFilename(origMatName)
        _, _, newPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, 
                                                    newChoiceID)
        while newPID == None:
            time.sleep(0.1)
            _, _, newPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, 
                                                    newChoiceID)
        cmd = oscr.getMoveWindowCMD(newPID, [halfWidth, height, 0, 0], newChoiceID)
        _u.runCmdAndWait(cmd)

        # update book settings
        fsf.Data.Book.currOrigMatName = origMatName
    
    def render(self, widjetObj=None, renderData=..., **kwargs):
        names = fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsNames()
        self.updateOptions(names)

        currOrigMatName = fsf.Data.Book.currOrigMatName
        self.setData(currOrigMatName)

        return super().render(widjetObj, renderData, **kwargs)


class SwitchToCurrSectionLayout_BTN(ww.currUIImpl.Button,
                                    dc.AppCurrDataAccessToken):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 5, "row" : 16},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_swritchToCurrSectionLayout_BTN"
        text= "To Section L"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        data, 
                        self.cmd)

    def cmd(self):
        # switch UI
        mathMenuManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken, mmm.MathMenuManager)
        mathMenuManager.switchUILayout(mmm.LayoutManagers._Section)
        
        # switch other apps
        lf.Wr.SectionLayout.set()


class ChooseSubsection_OM(ww.currUIImpl.OptionMenu):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 1, "row" : 15},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }
        name = "_chooseSubsecion_optionMenu"

        subsectionsList = fsf.Wr.SectionCurrent.getSubsectionsListForCurrTopSection()

        if subsectionsList == []:
            subsectionsList = ["No subsec yet."]

        super().__init__(prefix, 
                        name, 
                        subsectionsList,
                        patentWidget, 
                        renderData, 
                        self.cmd)
        
        currSubsection = _upan.Current.Names.Section.name()
        self.setData(currSubsection)
    
    def cmd(self):
        newSubsection = self.getData()

        # close current subsection FS window
        currSection = fsf.Data.Book.currSection
        if newSubsection != currSection:
            lf.Wr.LayoutsManager.closeFSWindow(currSection)

        # open new subsection
        sections = fsf.Data.Book.sections
        topSection = fsf.Data.Book.currTopSection
        sections[topSection]["prevSubsectionPath"] = newSubsection
        fsf.Data.Book.sections = sections
        fsf.Data.Book.currSection = newSubsection

        self.notify(ImageGeneration_ETR, fsf.Wr.Links.ImIDX.get(newSubsection))

        self.notify(ScreenshotLocation_LBL)

        self.notify(commw.SourceImageLinks_OM)

        lf.Wr.MainLayout.set()

    def updateOptions(self, newMenuOptions):
        self.notify(ImageGenerationRestart_BTN)
        return super().updateOptions(newMenuOptions)

    def receiveNotification(self, broadcasterType, newOptionList = [], prevSubsectionPath = "", *args) -> None:
        if broadcasterType == ChooseTopSection_OM:
            self.updateOptions(newOptionList)
            self.setData(prevSubsectionPath)   
        elif broadcasterType == comw.TOC_BOX:
            self.render()

    def render(self, widjetObj=None, renderData=..., **kwargs):
        subsectionsList = fsf.Wr.SectionCurrent.getSubsectionsListForCurrTopSection()

        if subsectionsList == []:
            subsectionsList = ["No subsec yet."]

        self.updateOptions(subsectionsList)

        currSubsection = _upan.Current.Names.Section.name()
        self.setData(currSubsection)

        return super().render(widjetObj, renderData, **kwargs)


class ChooseTopSection_OM(ww.currUIImpl.OptionMenu):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 15},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }
        name = "_chooseSection_optionMenu"

        topSectionsList = fsf.Wr.BookInfoStructure.getTopSectionsList()
        if topSectionsList != _u.Token.NotDef.list_t:
            topSectionsList.sort(key = int)

        if topSectionsList == []:
            topSectionsList = ["No top sec yet."]

        super().__init__(prefix, 
                        name, 
                        topSectionsList,
                        patentWidget, 
                        renderData, 
                        self.cmd)
        
        currTopSection = fsf.Data.Book.currTopSection
        self.setData(currTopSection)
    
    def cmd(self):

        topSection = self.getData()

        # update top section
        fsf.Data.Book.currTopSection = topSection
        
        # update subsection
        sections = fsf.Data.Book.sections
        prevSubsectionPath = sections[topSection]["prevSubsectionPath"]
        
        # close current subsection FS window
        currSection = fsf.Data.Book.currSection
        
        if currSection != prevSubsectionPath:
            lf.Wr.LayoutsManager.closeFSWindow(currSection)
            fsf.Data.Book.currSection = prevSubsectionPath

        # update image index
        secionImIndex = fsf.Wr.Links.ImIDX.get(prevSubsectionPath)        
        

        subsectionsList = fsf.Wr.SectionCurrent.getSubsectionsListForCurrTopSection()
        subsectionsList.sort()
        
        #
        # Update other widgets
        #

        # subsection option menu widget
        # notify choose subsection OM
        self.notify(ChooseSubsection_OM, subsectionsList, prevSubsectionPath)

        # update screenshot widget
        self.notify(commw.SourceImageLinks_OM)

        # update screenshot widget
        self.notify(ScreenshotLocation_LBL)

        # update image index widget
        self.notify(ImageGeneration_ETR, 
                    fsf.Wr.Links.ImIDX.get(prevSubsectionPath))
        
        lf.Wr.MainLayout.set()
    
    def receiveNotification(self, broadcasterType):
        if broadcasterType == ChooseSubsection_OM:
            return self.getData()
        elif broadcasterType == comw.TOC_BOX:
            self.render()
    
    def render(self, widjetObj=None, renderData=..., **kwargs):
        topSectionsList = fsf.Wr.BookInfoStructure.getTopSectionsList()
        if topSectionsList != _u.Token.NotDef.list_t:
            topSectionsList.sort(key = int)
        
        if topSectionsList == []:
            topSectionsList = ["No top sec yet."]
        
        self.setData(topSectionsList)

        currTopSection = fsf.Data.Book.currTopSection
        self.setData(currTopSection)

        return super().render(widjetObj, renderData, **kwargs)


class ScreenshotLocation_LBL(ww.currUIImpl.Label):
    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 2, "columnspan": 5},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_showCurrScreenshotLocation_text"
        text_curr = _upan.Paths.Screenshot.getRel_formatted()
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data, 
                        text = text_curr)
    
    def receiveNotification(self, broadcasterName, data = None):
        if broadcasterName == ChooseTopSection_OM:
            text = _upan.Paths.Screenshot.getRel_formatted()
            self.changeText(text)
        elif broadcasterName == ChooseSubsection_OM:
            text = _upan.Paths.Screenshot.getRel_formatted()
            self.changeText(text)
        elif broadcasterName == comw.TOC_BOX:
            text = _upan.Paths.Screenshot.getRel_formatted()
            self.changeText(text)
    
    def render(self):
        text_curr = _upan.Paths.Screenshot.getRel_formatted()
        self.changeText(text_curr)
        return super().render()


class TextOnly_CHB(ww.currUIImpl.Checkbox):
    etenriesTextOnlyDefault = 0

    def __init__(self, parentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 5, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.E}
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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
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
                msg = "Incorrect image index \nId: '{0}'.".format(self.dataFromUser[0])
                wm.UI_generalManager.showNotification(msg, True)

                mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                            mmm.MathMenuManager)
                mainManager.show()

                return

            addToTOCwIm = self.notify(addToTOCwImage_CHB)
            textOnly = self.notify(TextOnly_CHB)

            msg = "\
Do you want to create entry with \nId: '{0}', Name: '{1}'".format(self.dataFromUser[0], self.dataFromUser[1])
            response = wm.UI_generalManager.showNotification(msg, True)

            mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                        mmm.MathMenuManager)
            mainManager.show()
            
            if not response:
                return

            currSubsection = fsf.Data.Book.currSection
            entryAdded:bool = gm.GeneralManger.AddEntry(currSubsection, 
                                                        self.dataFromUser[0], 
                                                        self.dataFromUser[1],
                                                        addToTOCwIm,
                                                        textOnly)

            if not entryAdded:
                return
            
            currImNum = self.dataFromUser[0]
            nextImNum = str(int(currImNum) + 1)
            self.notify(ImageGeneration_ETR, nextImNum)
            self.notify(comw.TOC_BOX, entryClicked = self.dataFromUser[0])
            self.notify(commw.SourceImageLinks_OM)
            self.notify(LatestExtraImForEntry_LBL)
            self.updateLabel(self.labelOptions[0])
        
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
        if broadcasterType == AddExtraImage_BTN:
            self.updateLabel(self.labelOptions[0])
            return self.dataFromUser[0]


class ImageGeneration_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "columnspan": 6}
        }
        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {},
            ww.TkWidgets.__name__ : {"width": 240}
        }
        name = "_imageGeneration_ETR"
        defaultText = "0"

        super().__init__(prefix, 
                        name,
                        patentWidget, 
                        data,
                        extraBuildOptions,
                        defaultText = defaultText)

        secImIndex = fsf.Wr.Links.ImIDX.get_curr()

        if secImIndex == _u.Token.NotDef.str_t:
            self.updateDafaultText(defaultText)
        else:
            self.updateDafaultText(str(int(secImIndex) + 1))
        
        def __boldenText(*args):
            startSelIDX = self.widgetObj.index("sel.first")
            endSelIDX = self.widgetObj.index("sel.last")
            selText = self.widgetObj.get(startSelIDX, endSelIDX)
            boldSelText = f"\\textbf{{{selText}}}"
            self.widgetObj.replace(startSelIDX, endSelIDX, boldSelText)
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.cmdb,
                            lambda *args: __boldenText(*args))

        def __underlineText(*args):
            startSelIDX = self.widgetObj.index("sel.first")
            endSelIDX = self.widgetObj.index("sel.last")
            selText = self.widgetObj.get(startSelIDX, endSelIDX)
            boldSelText = f"\\underline{{{selText}}}"
            self.widgetObj.replace(startSelIDX, endSelIDX, boldSelText)
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.cmdu,
                  lambda *args: __underlineText(*args))

        def __addNote(*args):
            boldSelText = "\\textbf{NOTE:} "
            self.widgetObj.insert("0", boldSelText)
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.cmdn,
                  lambda *args: __addNote(*args))

        def __addNoteInPlace(*args):
            boldSelText = "\\textbf{NOTE:} "
            self.widgetObj.insert(tk.INSERT, boldSelText)

        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.cmdshn,
                            lambda *args: __addNoteInPlace(*args))

        def __addDef(*args):
            boldSelText = "\\textbf{DEF:} "
            self.widgetObj.insert(tk.INSERT, boldSelText)
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.cmdd,
                  lambda *args: __addDef(*args))

        def __addProposion(*args):
            boldSelText = "\\textbf{Proposition:} "
            self.widgetObj.insert(tk.INSERT, boldSelText)
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.cmdp,
                  lambda *args: __addProposion(*args))

        def __addExample(*args):
            boldSelText = "\\textbf{EX:} "
            self.widgetObj.insert("0", boldSelText)
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.cmde,
                  lambda *args: __addExample(*args))

        def __addExample(*args):
            boldSelText = "excercise "
            self.widgetObj.insert("0", boldSelText)
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.cmdshe,
                  lambda *args: __addExample(*args))

        def __notifyImGenerationBtn(*args):
            self.notify(ImageGeneration_BTN)
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.shenter,
                  lambda *args: __notifyImGenerationBtn(*args))

        def __notifyImGenerationRestartBtn(*args):
            self.notify(ImageGenerationRestart_BTN)
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.escape,
                  lambda *args: __notifyImGenerationRestartBtn(*args))

        def __notifyAlwaysShowChBx(*args):
            self.notify(addToTOCwImage_CHB)
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.cmdshi,
                  lambda *args: __notifyAlwaysShowChBx(*args))

        def __notifyTextOnlyChBx(*args):
            self.notify(TextOnly_CHB)
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.cmdsht,
                  lambda *args: __notifyTextOnlyChBx(*args))

    def receiveNotification(self, broadcasterType, dataToSet = None):
        if broadcasterType == ImageGenerationRestart_BTN:
            currImIdx = int(fsf.Wr.SectionCurrent.getImIDX())
            nextImIdx = str(currImIdx + 1)
            self.setData(nextImIdx)
            self.widgetObj.focus_force()
            return
        elif broadcasterType == ImageGeneration_BTN:
            prevData = self.getData()

            if prevData == "":
                prevData = _u.Token.NotDef.str_t

            self.setData(dataToSet)
            self.widgetObj.focus_force()
            return prevData
        elif broadcasterType == ChooseSubsection_OM or broadcasterType == ChooseTopSection_OM:
            # TODO: find a nicer wahy without checking the dict
            imDict = fsf.Wr.SectionCurrent.getCurrLinkIdxDict()
            currIdx = fsf.Wr.SectionCurrent.getImIDX()
            currIdx = int(currIdx)
            nextIdx = str(currIdx + 1)

            if imDict == _u.Token.NotDef.dict_t:
                self.setData(currIdx)
            else:
                self.setData(nextIdx)
        elif broadcasterType == AddExtraImage_BTN:
            return self.getData()
        elif broadcasterType == ImageGroupAdd_BTN:
            return self.getData()
        elif broadcasterType == commw.AddWebLink_BTN:
            return self.getData()
    
    def render(self, **kwargs):
        secImIndex = fsf.Wr.Links.ImIDX.get_curr()

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


class AddExtraImage_BTN(ww.currUIImpl.Button,
                        dc.AppCurrDataAccessToken):  
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 1, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text= "addExtraIm"
        name = "_imageGenerationAddIm"

        super().__init__(prefix, 
                        name,
                        text, 
                        patentWidget,
                        data, 
                        self.cmd)

    def cmd(self):
        mainImIdx = self.notify(ImageGeneration_BTN)
        extraImageIdx = _u.Token.NotDef.str_t

        if "_" in mainImIdx:
            # NOTE: here we obtain the extra image index together with the mainImIdx
            mainAndExtraIndex = mainImIdx.split("_")

            for idx in mainAndExtraIndex:
                if not re.match("^[0-9]+$", idx):
                    msg = "Incorrect image index \nId: '{0}'.".format(idx)
                    wm.UI_generalManager.showNotification(msg, True)

                    mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                                mmm.MathMenuManager)
                    mainManager.show()

                    return

            mainImIdx = mainAndExtraIndex[0]
            extraImageIdx = mainAndExtraIndex[1]
        else:
            if not re.match("^[0-9]+$", mainImIdx):
                msg = "Incorrect main image index \nId: '{0}'.".format(mainImIdx)
                wm.UI_generalManager.showNotification(msg, True)

                mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                            mmm.MathMenuManager)
                mainManager.show()

                return

        
        if mainImIdx == _u.Token.NotDef.str_t:
            mainImIdx = fsf.Wr.Links.ImIDX.get_curr()
       
        extraImText = self.notify(ImageGeneration_ETR)
        
        currentSubsection = _upan.Current.Names.Section.name()

        self.addExtraIm(currentSubsection, mainImIdx, extraImageIdx, extraImText)

    def addExtraIm(self, subsection, mainImIdx, extraImageIdx, extraImText, notifyMainTextLabel = True):
        msg = "\
Do you want to add extra image to: '{0}' with name: '{1}'?".format(mainImIdx, extraImText)
        response = wm.UI_generalManager.showNotification(msg, True)

        mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                    mmm.MathMenuManager)
        mainManager.show()
        
        if not response:
            return

        gm.GeneralManger.AddExtraImageForEntry(mainImIdx, subsection, extraImageIdx, extraImText)

        if notifyMainTextLabel:
            self.notify(LatestExtraImForEntry_LBL)
        # NOTE: I turned it off since it breaks stuff and I don't use this system at the moment
        # tff.Wr.TexFileModify.addExtraImage(mainImIdx, str(extraImageIdx))

        self.notify(comw.TOC_BOX, entryClicked = mainImIdx)
    
    def receiveNotification(self, broadcasterType, data, *args, **kwargs):
        subsection = data[0]  
        mainImIdx = data[1]
        extraImIdx = _u.Token.NotDef.str_t
        extraImagesDict = fsf.Data.Sec.extraImagesDict(subsection)

        if mainImIdx in list(extraImagesDict.keys()):
            extraImText = "con" + str(len(extraImagesDict[mainImIdx]))
        else:
            extraImText = "con0"

        self.addExtraIm(subsection, mainImIdx, extraImIdx, extraImText, False)
    

class ImageGenerationRestart_BTN(ww.currUIImpl.Button):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 2, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.NW}
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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.NW}
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
Do you want to add \n\
group: '{0}' to\n\
subsection: '{1}'?".format(groupName, currSubsection)
        response = wm.UI_generalManager.showNotification(msg, True)

        mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                    mmm.MathMenuManager)
        mainManager.show()
        
        if not response:
            return

        # update the groups list for the subsection
        imGroups:dict = fsf.Data.Sec.imagesGroupsList(currSubsection)
        imGroups[groupName] = True
        fsf.Data.Sec.imagesGroupsList(currSubsection, imGroups)

        dt.AppState.UseLatestGroup.setData(self.appCurrDataAccessToken, True)

        # re-render toc
        self.notify(comw.TOC_BOX)



class ImageCreation:
    pass
