import tkinter as tk
from threading import Thread
import subprocess

import UI.widgets_wrappers as ww
import file_system.file_system_facade as fsm
import _utils.logging as log
import tex_file.tex_file_facade as tff
import scripts.osascripts as oscr
import data.temp as dt
import data.constants as dc

import _utils._utils_main as _u
import _utils.pathsAndNames as _upan

import outside_calls.outside_calls_facade as ocf

import UI.widgets_collection.main.math.manager as mmm
import layouts.layouts_facade as lf

import data.constants as dc
import data.temp as dt

import settings.facade as sf

class SwitchToCurrMainLayout_BTN(ww.currUIImpl.Button,
                                 dc.AppCurrDataAccessToken):

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
        # switch UI
        mathMenuManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken, mmm.MathMenuManager)
        mathMenuManager.switchUILayout(mmm.LayoutManagers._Main)

        # switch other apps
        lf.Wr.MainLayout.set()


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
        ocf.Wr.LatexCalls.buildCurrentSubsectionPdf()


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
            tff.Wr.TexFileModify.changeProofsVisibility(True)
        elif currLabel ==  self.labelOptions[1]:
            self.updateLabel(self.labelOptions[0])
            tff.Wr.TexFileModify.changeProofsVisibility(False)
        
        ocf.Wr.LatexCalls.buildCurrentSubsectionPdf()


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
        _u.runCmdAndWait(cmd)
        ocf.Wr.LatexCalls.buildCurrentSubsectionPdf()


class SourceImageLinks_OM(ww.currUIImpl.OptionMenu):

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_source_SecImIDX_OM"

        currSecPath = fsm.Wr.SectionCurrent.getSectionNameNoPrefix()
        self.sourceSubsectionImageLinks = list(fsm.Wr.Links.LinkDict.get(currSecPath).keys())
        self.sourceSubsectionImageLinks.sort(key = int)

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
        self.sourceSubsectionImageLinks = list(fsm.Wr.Links.LinkDict.get(currSecPath).keys())
        self.sourceSubsectionImageLinks.sort(key = int)

        super().updateOptions(self.sourceSubsectionImageLinks)
        self.setData(self.sourceSubsectionImageLinks[-1])

    def render(self, widjetObj=None, renderData=..., **kwargs):
        self.updateOptions()
        return super().render(widjetObj, renderData, **kwargs)

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
        imLink:str = self.getData()
        toBeRemoved = imLink.split(":")[0]
        self.notify(AddGlobalLink_ETR, secPath + "." + toBeRemoved)

    def updateOptions(self, secPath):
        num = list(fsm.Wr.Links.LinkDict.get(secPath).keys())
        names = list(fsm.Wr.Links.LinkDict.get(secPath).values())
        formatted = []

        for i in range(len(num)):
            formatted.append("{0}:{1}".format(num[i], names[i]))

        return super().updateOptions(formatted)

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

        topSectionsList = fsm.Wr.BookInfoStructure.getTopSectionsList()
        if topSectionsList != _u.Token.NotDef.list_t:
            topSectionsList.sort(key = int)
        
        self.subsectionsList = fsm.Wr.BookInfoStructure.getSubsectionsList(topSectionsList[0])

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
            subsectionsList = fsm.Wr.BookInfoStructure.getSubsectionsList(data)
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

        self.topSectionsList = fsm.Wr.BookInfoStructure.getTopSectionsList()

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
        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        bookName = sf.Wr.Manager.Book.getCurrBookName()
        
        sourceSubsection = fsm.Wr.SectionCurrent.getSectionNameNoPrefix()
        sourceTopSection = sourceSubsection.split(".")[0]
        sourceIDX = self.notify(SourceImageLinks_OM)

        wholeLinkPath = self.notify(AddGlobalLink_ETR).split(".")
        targetSubsection = ".".join(wholeLinkPath[:-1])
        targetTopSection = targetSubsection.split(".")[0]
        targetIDX = wholeLinkPath[-1]

        # add target to the source links
        sourseSectionGlobalLinksDict = fsm.Data.Sec.imGlobalLinksDict(sourceSubsection)
        
        if sourceIDX not in list(sourseSectionGlobalLinksDict.keys()):
            sourceImGlobalLinksDict = {}
        elif sourseSectionGlobalLinksDict[sourceIDX] == _u.Token.NotDef.dict_t:
            sourceImGlobalLinksDict = {}
        else:
            sourceImGlobalLinksDict = sourseSectionGlobalLinksDict[sourceIDX]
        
        targetUrl = tff.Wr.TexFileUtils.getUrl(bookName, targetTopSection, targetSubsection, 
                                                targetIDX, "full", False)
        targetUrlLinkName = targetSubsection + "_" + targetIDX
        
        if targetUrlLinkName not in list(sourceImGlobalLinksDict.keys()):
            sourceImGlobalLinksDict[targetUrlLinkName] = targetUrl
            if sourseSectionGlobalLinksDict == _u.Token.NotDef.dict_t:
                sourseSectionGlobalLinksDict = {}
            
            sourseSectionGlobalLinksDict[sourceIDX] = sourceImGlobalLinksDict
            fsm.Data.Sec.imGlobalLinksDict(sourceSubsection, sourseSectionGlobalLinksDict)
        else:
            log.autolog("The link: '{0}' is already present.".format(targetUrl))

        # add target to the target info
        targetSectionGlobalLinksDict = fsm.Data.Sec.imGlobalLinksDict(targetSubsection)
        
        if targetIDX not in list(targetSectionGlobalLinksDict.keys()):
            targetImGlobalLinksDict = {}
        elif targetSectionGlobalLinksDict[targetIDX] == _u.Token.NotDef.dict_t:
            targetImGlobalLinksDict = {}
        else:
            targetImGlobalLinksDict = targetSectionGlobalLinksDict[targetIDX]

        sourceUrl = tff.Wr.TexFileUtils.getUrl(bookName, sourceTopSection, sourceSubsection, 
                                                sourceIDX, "full", False)
        sourceUrlLinkName = sourceSubsection + "_" + sourceIDX
        
        if sourceUrlLinkName not in list(targetImGlobalLinksDict.keys()):
            targetImGlobalLinksDict[sourceUrlLinkName] = sourceUrl
        else:
            log.autolog("the link: '{0}' is already present.".format(targetUrl))

        if targetSectionGlobalLinksDict == _u.Token.NotDef.dict_t:
            targetSectionGlobalLinksDict = {}

        targetSectionGlobalLinksDict[targetIDX] = targetImGlobalLinksDict
        fsm.Data.Sec.imGlobalLinksDict(targetSubsection, targetSectionGlobalLinksDict)

        #
        # rebuild the pdfs
        #
        ocf.Wr.LatexCalls.buildPDF(bookPath, sourceSubsection, sourceIDX)
        ocf.Wr.LatexCalls.buildPDF(bookPath, targetSubsection, targetIDX)


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
        def __cmd(event, *args):
            if event.keysym == ww.currUIImpl.Data.BindID.Keys.enter:
                lambda _: self.notify(TargetImageLinks_OM, self.getData())
        return [ww.currUIImpl.Data.BindID.allKeys] , [__cmd]


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
            lf.Wr.LayoutsManager.closeIDEWindow(subsection, dt.OtherAppsInfo.VsCode.section_pid)

        #change the current subsection for the app
        fsm.Data.Book.currTopSection = topSection
        fsm.Data.Book.currSection = subsection
        

        # rerender the layout???
        # mon_width, _ = _u.getMonitorSize()
        # width = int(mon_width / 2)
        # height = 70
        # wu.showCurrentLayout(mainWinRoot, 
        #                     width, 
        #                     height)
        # lf.Wr.SectionLayout.set(mainWinRoot, width, height)

        self.notify(SourceImageLinks_OM, subsection)
