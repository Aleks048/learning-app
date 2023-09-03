import UI.widgets_wrappers as ww
import UI.widgets_collection.main.math.manager as mmm
import UI.widgets_collection.toc.manager as tocm
import UI.widgets_collection.main.math.UI_layouts.mainLayout as mui
import UI.widgets_collection.common as comw
import layouts.layouts_facade as lm
import _utils._utils_main as _u
import data.constants as dc
import data.temp as dt
import tkinter as tk
import scripts.osascripts as oscr
import outside_calls.outside_calls_facade as ocf
import file_system.file_system_facade as fsm


class MainMenuRoot(ww.currUIImpl.RootWidget):
    pass


class Layouts_OM(ww.currUIImpl.OptionMenu,
                 dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix, row = 16, column = 1):
        self.layoutOptions = {
            "Main" : [mmm.LayoutManagers._Main, lm.Wr.MainLayout], 
            "Section" : [mmm.LayoutManagers._Section, lm.Wr.SectionLayout], 
            "WholeVSCode": None}
        
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }
        name = "_layouts_optionMenu"
        listOfLayouts = self.layoutOptions.keys()

        super().__init__(prefix, 
                        name, 
                        listOfLayouts,
                        patentWidget, 
                        renderData, 
                        self.cmd)

        self.setData(list(listOfLayouts)[0])
    
    def cmd(self):
        layoutToSwitchTo = self.getData()
        mathMenuManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken, 
                                                         mmm.MathMenuManager)
        mathMenuManager.switchUILayout(self.layoutOptions[layoutToSwitchTo][0])
        self.layoutOptions[layoutToSwitchTo][1].set()


class SwitchLayoutSectionVSMain_BTN(ww.currUIImpl.Button,
                                    dc.AppCurrDataAccessToken):
    labelOptions = ["To Add/Modify L", "To Main L"]

    def __init__(self, patentWidget, prefix, data = None, name = None, text = None):
        if data == None:
            data = {
                ww.Data.GeneralProperties_ID : {"column" : 2, "row" : 16},
                ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
            }
        if name == None:
            name = "_chooseSubsectionLayout_BTN"
        
        if text == None:
            text = self.labelOptions[0]

        super().__init__(prefix, 
                        name,
                        text, 
                        patentWidget,
                        data, 
                        self.cmd)
    
    def cmd(self):
        mathMenuManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                         mmm.MathMenuManager)
        if type(mathMenuManager.currLayout) == mmm.LayoutManagers._Main:
            # show the sections UI
            mathMenuManager.switchUILayout(mmm.LayoutManagers._AddModifySection)

            self.updateLabel(self.labelOptions[0])

            lm.Wr.MainLayout.set()
        else:
            mathMenuManager.switchUILayout(mmm.LayoutManagers._Main)

            self.updateLabel(self.labelOptions[1])

            lm.Wr.MainLayout.set()

class LayoutsSwitchOrigMatVSMain_BTN(ww.currUIImpl.Button,
                                    dc.AppCurrDataAccessToken):
    labelOptions = ["To Orig Mat L", "To Main L"]

    def __init__(self, patentWidget, prefix, data = None, name = None, text = None):
        if data == None:
            data = {
                ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 16},
                ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
            }
        if name == None:
            name = "_layoutsSwitchOrigMatVSMain_BTN"
        
        if text == None:
            text = self.labelOptions[0]

        super().__init__(prefix, 
                        name,
                        text, 
                        patentWidget,
                        data, 
                        self.cmd)
    
    def cmd(self):
        mathMenuManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                         mmm.MathMenuManager)
        if type(mathMenuManager.currLayout) == mmm.LayoutManagers._Main:
            # show the sections UI
            mathMenuManager.switchUILayout(mmm.LayoutManagers._AddModifyOrigMat)

            self.updateLabel(self.labelOptions[0])

            lm.Wr.MainLayout.set()
        else:
            mathMenuManager.switchUILayout(mmm.LayoutManagers._Main)

            self.updateLabel(self.labelOptions[1])

            lm.Wr.MainLayout.set()

class ShowTocWindow_BTN(ww.currUIImpl.Button,
                  dc.AppCurrDataAccessToken):

    def __init__(self, patentWidget, prefix, row =16, column = 4):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_tocWindow"
        text= "TOC win"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        data, 
                        self.cmd)

    def cmd(self):
        UIManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                        tocm.TOCManager)
        
        UIManager.show()



class ShowProofs_BTN(ww.currUIImpl.Button,
                     dc.AppCurrDataAccessToken):
    labelOptions = ["Show Proofs", "Hide Proofs"]
    def __init__(self, patentWidget, prefix, column = 1, row = 0):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_showProofs_BTN"
        if dt.AppState.ShowProofs.getData(self.appCurrDataAccessToken):
            text = self.labelOptions[1]
        else:
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
            dt.AppState.ShowProofs.setData(self.appCurrDataAccessToken,
                                           True)
        elif currLabel ==  self.labelOptions[1]:
            self.updateLabel(self.labelOptions[0])
            dt.AppState.ShowProofs.setData(self.appCurrDataAccessToken,
                                           False)
        
        self.notify(mui.TOC_BOX)
        ocf.Wr.LatexCalls.buildCurrentSubsectionPdf()
    
    def render(self, **kwargs):
        if dt.AppState.ShowProofs.getData(self.appCurrDataAccessToken):
            self.updateLabel(self.labelOptions[1])
        else:
            self.updateLabel(self.labelOptions[0])

        return super().render(**kwargs)


class ImageSave_BTN(ww.currUIImpl.Button):
    def __init__(self, patentWidget, prefix, column = 2, row = 0):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
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
        self.notifyAllListeners()


class SourceImageLinks_OM(ww.currUIImpl.OptionMenu):

    def __init__(self, patentWidget, prefix, column = 3, row = 1):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
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
        self.notifyAllListeners()

    def updateOptions(self, _ = ""):
        currSec = fsm.Data.Book.currSection
        imLinkDict = fsm.Data.Sec.imLinkDict(currSec)
        if type(imLinkDict) == dict:
            self.sourceSubsectionImageLinks = list(imLinkDict.keys())
            self.sourceSubsectionImageLinks.sort(key = int)
        else:
            self.sourceSubsectionImageLinks = _u.Token.NotDef.list_t

        super().updateOptions(self.sourceSubsectionImageLinks)
        self.setData(self.sourceSubsectionImageLinks[-1])

    def render(self, widjetObj=None, renderData=..., **kwargs):
        self.updateOptions()
        return super().render(widjetObj, renderData, **kwargs)

    def receiveNotification(self, broadcasterType):
        if broadcasterType == AddGlobalLink_BTN:
            return self.getData()
        elif broadcasterType == mui.LatestExtraImForEntry_LBL:
            return self.getData()
        elif broadcasterType == AddWebLink_BTN:
            return self.getData()
        else:
            self.updateOptions()


class TargetImageLinks_OM(ww.currUIImpl.OptionMenu):
    def __init__(self, patentWidget, prefix, column = 2, row = 1):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row, "columnspan" : 2},
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
        self.__setGlobalLinksETR(secPath)

    def __setGlobalLinksETR(self, secPath):
        imLink:str = self.getData()
        self.notify(AddGlobalLink_ETR, secPath + "." + imLink.split(":")[0])

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
            self.__setGlobalLinksETR(secPath)


class TargetSubection_OM(ww.currUIImpl.OptionMenu):
    def __init__(self, patentWidget, prefix, column = 1, row = 1):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_GlLink_TargetSubsection_OM"

        # if topSectionsList != _u.Token.NotDef.list_t:
        #     topSectionsList.sort(key = int)
        
        currTopSection = fsm.Data.Book.currTopSection

        self.subsectionsList = fsm.Wr.BookInfoStructure.getSubsectionsList(currTopSection)

        super().__init__(prefix, 
                        name, 
                        self.subsectionsList,
                        patentWidget, 
                        renderData,
                        cmd=self.cmd)

        subsections = fsm.Wr.BookInfoStructure.getSubsectionsList(currTopSection)
        currSubsection = fsm.Data.Book.currSection

        if currSubsection == subsections[0]:
            self.setData(currSubsection)
        else:
            currSubsIdx = subsections.index(currSubsection)
            self.setData(subsections[currSubsIdx - 1])
    
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

    def __init__(self, patentWidget, prefix, column = 0, row = 1):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_GlLink_TargetTopSection_OM"

        self.topSectionsList = fsm.Wr.BookInfoStructure.getTopSectionsList()
        self.topSectionsList.sort(key = int)

        super().__init__(prefix, 
                        name, 
                        self.topSectionsList,
                        patentWidget, 
                        renderData,
                        cmd=self.cmd)
        
        currTopSection = fsm.Data.Book.currTopSection

        self.setData(currTopSection)
    
    def cmd(self):
        topSec = self.getData()
        self.notify(TargetSubection_OM, topSec)
        # self.notify(AddGlobalLink_ETR, topSec)


class AddGlobalLink_BTN(ww.currUIImpl.Button,
                        dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix, column = 2, row = 2):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
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
    
    def receiveNotification(self, broadcasterType, data, *args) -> None:
        if broadcasterType == comw.TOC_BOX:
            import generalManger.generalManger as gm
            # we render the toc widget from the main win.
            # NOTE: done in a weird way since we call it from the toc window
            mmManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                        mmm.MathMenuManager)

            targetSubsection = data[0]
            targetImIdx = data[1]

            sourceSubsection = fsm.Wr.SectionCurrent.getSectionNameNoPrefix()
            sourceTopSection = sourceSubsection.split(".")[0]
            sourceIDX = self.notify(SourceImageLinks_OM)

            if sourceIDX == None:
                sourceIDX = mmManager.getSelectedImIdx()

            gm.GeneralManger.AddLink(f"{targetSubsection}.{targetImIdx}",
                                     sourceSubsection,
                                     sourceIDX,
                                     sourceTopSection)
            
            mmManager.renderTocWidget()

    def cmd(self):
        import generalManger.generalManger as gm

        sourceSubsection = fsm.Wr.SectionCurrent.getSectionNameNoPrefix()
        sourceTopSection = sourceSubsection.split(".")[0]
        sourceIDX = self.notify(SourceImageLinks_OM)

        wholeLinkPathStr = self.notify(AddGlobalLink_ETR)

        gm.GeneralManger.AddLink(wholeLinkPathStr, sourceSubsection, sourceIDX, sourceTopSection)
        self.notify(comw.TOC_BOX)


class AddGlobalLink_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix, column = 0, row = 2):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row, "columnspan" : 2},
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
        elif broadcasterType == AddWebLink_BTN:
            return self.getData()

    def bindCmd(self):
        def __cmd(event, *args):
            if event.keysym == ww.currUIImpl.Data.BindID.Keys.enter:
                lambda _: self.notify(TargetImageLinks_OM, self.getData())
        return [ww.currUIImpl.Data.BindID.allKeys] , [__cmd]



class AddWebLink_BTN(ww.currUIImpl.Button,
                        dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix, column = 3, row = 2):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_addWebLink_BTN"
        text = "Create web link"

        super().__init__(prefix,
                        name,
                        text,
                        patentWidget,
                        data,
                        self.cmd)
    
    def cmd(self):
        import generalManger.generalManger as gm

        sourceSubsection = fsm.Wr.SectionCurrent.getSectionNameNoPrefix()
        sourceTopSection = sourceSubsection.split(".")[0]
        sourceIDX = self.notify(SourceImageLinks_OM)

        webAddress = self.notify(AddGlobalLink_ETR)
        linkName = self.notify(mui.ImageGeneration_ETR)

        gm.GeneralManger.AddWebLink(linkName, webAddress, sourceSubsection, sourceIDX, sourceTopSection)
        self.notify(comw.TOC_BOX)
