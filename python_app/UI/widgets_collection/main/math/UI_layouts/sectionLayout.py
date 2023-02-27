import tkinter as tk
from threading import Thread
import subprocess

import UI.widgets_wrappers as ww
import UI.widgets_messages as wmes
import file_system.file_system_manager as fsm
import _utils.logging as log
import tex_file.tex_file_facade as tff
import scripts.osascripts as oscr
import data.temp as dt

import _utils._utils_main as _u


import UI.widgets_collection.main.math.manager as mmm
import layouts.layouts_manager as lm

class SwitchToCurrMainLayout_BTN(ww.currUIImpl.Button):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_swritchToCurrMainLayout_BTN"
        text= "To main"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        data, 
                        self.cmd)

    def cmd(self):
        mmm.MathMenuManager.switchUILayout(mmm.LayoutManagers._Main)
        lm.Wr.MainLayout.set()


class RebuildCurrSection_BTN(ww.currUIImpl.Button):
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0,  "pady" : 0, "sticky" : tk.N,}
        }
        name = "_rebuildCurrSubsec_BTN"
        text = "rebuild"

        super().__init__(prefix, 
                        name,
                        text, 
                        patentWidget,
                        data, 
                        self.cmd)
    
    def cmd(self):
        tff.Wr.TexFile.buildCurrentSubsectionPdf()


class ShowProofs_BTN(ww.currUIImpl.Button):
    labelOptions = ["Show Proofs", "Hide Proofs"]
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 1, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_showProofs_BTN"
        text = self.labelOptions[0]

        super().__init__(prefix, 
                        name,
                        text, 
                        patentWidget,
                        data, 
                        self.cmd)
    
    def cmd(self):
        currLabel = self.getLabel()
        
        if currLabel == self.labelOptions[0]:
            self.updateLabel(self.labelOptions[1])
            self._changeProofsVisibility(True)
        elif currLabel ==  self.labelOptions[1]:
            self.updateLabel(self.labelOptions[0])
            self._changeProofsVisibility(False)
        
        Thread(target= tff.Wr.TexFile.buildCurrentSubsectionPdf).start()
    
    def _changeProofsVisibility(self, hideProofs):
        with open(fsm.Wr.Paths.TexFiles.Content.getAbs_curr(),"r") as conF:
            contentLines = conF.readlines()
        extraImagesStartToken = "% \EXTRA IMAGES START"
        extraImagesEndToken = "% \EXTRA IMAGES END"
        for i in range(len(contentLines)):
            if (extraImagesStartToken in contentLines[i]):
                while (extraImagesEndToken not in contentLines[i]):
                    i += 1
                    line = contentLines[i]
                    if "proof" in line.lower():
                        if hideProofs:
                            contentLines[i] = line.replace("% ", "")
                            log.autolog("\nHiding the proof for line:\n" + contentLines[i])
                        else:
                            contentLines[i] = "% " + line
                            log.autolog("\nShow the proof for line:\n" + contentLines[i])
                    break
        with open(fsm.Wr.Paths.TexFiles.Content.getAbs_curr(),"w") as conF:
            _waitDummy = conF.writelines(contentLines)


class ImageSave_BTN(ww.currUIImpl.Button):
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 2, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_saveImg_BTN"
        text = "saveIM"

        super().__init__(prefix, 
                        name,
                        text, 
                        patentWidget,
                        data, 
                        self.cmd)
    
    def cmd(self):
        cmd = oscr.get_NameOfFrontPreviewDoc_CMD()
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()
        tff.Wr.TexFile.buildCurrentSubsectionPdf()


class SourceImageLinks_OM(ww.currUIImpl.OptionMenu):

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_source_SecImIDX_OM"

        currSecPath = fsm.Wr.SectionCurrent.getSectionNameNoPrefix()
        currChImageLinks = fsm.Wr.Links.LinkDict.getCurrImLinksSorted(currSecPath)
        self.sourceSubsectionImageLinks = currChImageLinks

        super().__init__(prefix, 
                        name, 
                        self.sourceSubsectionImageLinks,
                        patentWidget, 
                        renderData,
                        self.cmd)
        
        self.updateOptions()
    
    def cmd(self):
        pass

    def updateOptions(self, _ = ""):
        currSecPath = fsm.Wr.SectionCurrent.getSectionNameNoPrefix()
        currChImageLinks = fsm.Wr.Links.LinkDict.getCurrImLinksSorted(currSecPath)
        super().updateOptions(currChImageLinks)
        self.setData(currChImageLinks[-1])

    def receiveNotification(self, broadcasterType):
        if broadcasterType == AddGlobalLink_BTN:
            return self.getData()
        else:
            self.updateOptions()


class TargetImageLinks_OM(ww.currUIImpl.OptionMenu):

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 2, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_target_SecImIDX_OM"

        self.targetSubsectionImageLinks = _u.Token.NotDef.list_t

        super().__init__(prefix, 
                        name, 
                        self.targetSubsectionImageLinks,
                        patentWidget, 
                        renderData,
                        self.cmd)
    
    def cmd(self):
        secPath = self.notify(TargetSubection_OM)
        imLink = self.getData()
        self.notify(AddGlobalLink_ETR, secPath + "." + imLink)

    def updateOptions(self, secPath):
        currChImageLinks = fsm.Wr.Links.LinkDict.getCurrImLinksSorted(secPath)
        return super().updateOptions(currChImageLinks)

    def receiveNotification(self, broadcasterType, data = None) -> None:
        if broadcasterType == TargetSubection_OM:
            secPath = data
            self.updateOptions(secPath)


class TargetSubection_OM(ww.currUIImpl.OptionMenu):

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 1, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_GlLink_TargetSubsection_OM"

        topSectionsList = fsm.getTopSectionsList()
        topSectionsList.sort(key = int)
        self.subsectionsList = fsm.getSubsectionsList(topSectionsList[0])

        super().__init__(prefix, 
                        name, 
                        self.subsectionsList,
                        patentWidget, 
                        renderData,
                        cmd=self.cmd)
    
    def cmd(self):
        secPath =  self.getData()
        self.notify(TargetImageLinks_OM, secPath)
        # self.notify(AddGlobalLink_ETR, secPath)
    
    def receiveNotification(self, broadcasterType, data = None):
        if broadcasterType == TargetTopSection_OM:
            subsectionsList = fsm.getSubsectionsList(data)
            subsectionsList.sort()
            self.updateOptions(subsectionsList)
            sectiopPath =  self.getData()
            self.notify(TargetImageLinks_OM, sectiopPath)
        elif broadcasterType == TargetImageLinks_OM:
            return self.getData()


class TargetTopSection_OM(ww.currUIImpl.OptionMenu):

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_GlLink_TargetTopSection_OM"

        self.topSectionsList = fsm.getTopSectionsList()

        super().__init__(prefix, 
                        name, 
                        self.topSectionsList,
                        patentWidget, 
                        renderData,
                        cmd=self.cmd)
        
        self.setData(self.topSectionsList[0])
    
    def cmd(self):
        topSec = self.getData()
        self.notify(TargetSubection_OM, topSec)
        self.notify(AddGlobalLink_ETR, topSec)


class AddGlobalLink_BTN(ww.currUIImpl.Button):
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 2, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_addGlobalLink_BTN"
        text = "Create gl link"

        super().__init__(prefix, 
                        name,
                        text, 
                        patentWidget,
                        data, 
                        self.cmd)
    
    def cmd(self):
        bookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
        bookName = _u.Settings.readProperty(_u.Settings.PubProp.currBookName_ID)
        secPrefix = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_prefix_ID)
        
        sourceSectionPath = fsm.Wr.SectionCurrent.getSectionNameNoPrefix()
        sourceSectionNameWprefix = fsm.Wr.SectionCurrent.getSectionNameWprefix()
        sourceLinkName = self.notify(SourceImageLinks_OM)
        sourceIDX = fsm.Wr.Links.LinkDict.get(sourceSectionPath)[sourceLinkName]
        sourceSectionFilepath = fsm.Wr.Paths.Section.getAbs(bookPath, sourceSectionPath)
        sourceContentFilepath = fsm.Wr.Paths.TexFiles.Content.getAbs(bookPath, sourceSectionNameWprefix)
        sourceMainFilepath = fsm.Wr.Paths.TexFiles.Main.getAbs(bookPath, sourceSectionNameWprefix)
        # sourceTOCFilepath = fsm.Wr.Paths.TexFiles.TOC.getAbs(bookPath, sourceSectionNameWprefix)
        sourcePDFFilepath = fsm.Wr.Paths.PDF.getAbs(bookPath, sourceSectionNameWprefix)
        sourcePDFFilename = sourcePDFFilepath.split("/")[-1]
        
        wholeLinkPath = self.notify(AddGlobalLink_ETR).split(".")
        targetSectionPath = ".".join(wholeLinkPath[:-1])
        targetSectionNameWprefix = secPrefix + "_" + targetSectionPath
        targetLinkName = wholeLinkPath[-1]
        targetIDX = fsm.Wr.Links.LinkDict.get(targetSectionPath)[targetLinkName]
        targetSectionFilepath = fsm.Wr.Paths.Section.getAbs(bookPath, targetSectionPath)
        targetContentFilepath = fsm.Wr.Paths.TexFiles.Content.getAbs(bookPath, targetSectionNameWprefix)
        targetMainFilepath = fsm.Wr.Paths.TexFiles.Main.getAbs(bookPath, targetSectionNameWprefix)
        # targetTOCFilepath = fsm.Wr.Paths.TexFiles.TOC.getAbs(bookPath, targetSectionNameWprefix)
        targetPDFFilepath = fsm.Wr.Paths.PDF.getAbs(bookPath, targetSectionNameWprefix)
        targetPDFFilename = targetPDFFilepath.split("/")[-1]

        #
        # check that the section exists
        #

        sectionInfo = fsm.Wr.BookInfoStructure.readProperty(targetSectionPath)
        if sectionInfo == None:
            msg = "The path: '" + targetSectionPath + "' does not exist"
            log.autolog(msg)
            wmes.MessageMenu.createMenu(msg)
            return
        
        topSection = targetSectionPath.split(".")[0]
        subsection = ".".join(targetSectionPath.split(".")[1:])
        tff.Wr.TexFileModify.addLinkToTexFile(sourceIDX,
                                            targetSectionPath + "\_" + targetLinkName,
                                            sourceContentFilepath,
                                            bookName,
                                            topSection,
                                            subsection)

        # add return link 
        
        sourceTopSection = sourceSectionPath.split(".")[0]
        sourceSubection = ".".join(sourceSectionPath.split(".")[1:])
        tff.Wr.TexFileModify.addLinkToTexFile(targetIDX, 
                                            sourceSectionPath + "\_" + sourceLinkName,
                                            targetContentFilepath,
                                            bookName,
                                            sourceTopSection,
                                            sourceSubection)

        #
        # rebuild the pdfs
        #
        tff.Wr.TexFile.buildSubsectionPdf(sourceSectionFilepath,
                                        sourceMainFilepath,
                                        sourceSectionNameWprefix)
        tff.Wr.TexFile.buildSubsectionPdf(targetSectionFilepath,
                                        targetMainFilepath,
                                        targetSectionNameWprefix)


class AddGlobalLink_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 2, "columnspan" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        defaultText = ""
        name = "_addGlobalLink_ETR"

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        bindCmd = self.bindCmd,
                        defaultText = defaultText,
                        )

        super().setData(self.defaultText)
    
    def receiveNotification(self, broadcasterType, data = None):
        if broadcasterType == AddGlobalLink_BTN:
            return self.getData()
        elif broadcasterType == TargetTopSection_OM:
            newText = str(data) + "."
            self.updateDafaultText(newText)
            self.setData(newText)
        elif broadcasterType == TargetSubection_OM:
            self.updateDafaultText(data)
            self.setData(data)
        elif broadcasterType == TargetImageLinks_OM:
            self.updateDafaultText(data)
            self.setData(data)
        elif broadcasterType == AddGlobalLink_BTN:
            return self.getData()
    
    def bindCmd(self):
        return [ww.currUIImpl.Data.BindID.enter] , [lambda _: self.notify(TargetImageLinks_OM, self.getData())]


class ChangeSubsection_BTN(ww.currUIImpl.Button):
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_changeSubsection_BTN"
        text = "change subsecttion"

        super().__init__(prefix, 
                        name,
                        text, 
                        patentWidget,
                        data, 
                        self.cmd)
    
    def cmd(self):
        # get the name of the front skim document
        cmd = oscr.get_NameOfFrontSkimDoc_CMD()
        frontSkimDocumentName = str(subprocess.check_output(cmd, shell=True))
        
        # get subsection and top section from it
        frontSkimDocumentName = frontSkimDocumentName.replace("\\n", "")
        frontSkimDocumentName = frontSkimDocumentName.split("_")[1]
        topSection = frontSkimDocumentName.split(".")[0]
        subsection = frontSkimDocumentName
        
        imIDX_page = int(frontSkimDocumentName.split(" ")[1])

        # close current section vscode
        _, windowID, _ = _u.getOwnersName_windowID_ofApp(
                            "vscode",
                             fsm.Wr.SectionCurrent.readCurrSection())
        
        if (windowID != None):
            cmd = oscr.closeVscodeWindow(dt.OtherAppsInfo.VsCode.section_pid, subsection)
            subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()

        #change the current subsection for the app
        fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.currTopSection_ID, topSection)
        fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.currSection_ID, subsection)
        

        # rerender the layout???
        # mon_width, _ = _u.getMonitorSize()
        # width = int(mon_width / 2)
        # height = 70
        # wu.showCurrentLayout(mainWinRoot, 
        #                     width, 
        #                     height)
        # lm.Wr.SectionLayout.set(mainWinRoot, width, height)

        self.notify(SourceImageLinks_OM, subsection)
