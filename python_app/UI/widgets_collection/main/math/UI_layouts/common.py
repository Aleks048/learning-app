from threading import Thread

import UI.widgets_wrappers as ww
import UI.widgets_collection.main.math.manager as mmm
import UI.widgets_collection.mainTOC.manager as mtocm
import UI.widgets_collection.toc.manager as tocm
import UI.widgets_collection.main.math.UI_layouts.mainLayout as mui
import UI.widgets_collection.common as comw
import UI.widgets_facade as wf
import data.constants as dc
import data.temp as dt
import outside_calls.outside_calls_facade as ocf
import file_system.file_system_facade as fsm


class SwitchLayoutSectionVSMain_BTN(ww.currUIImpl.Button,
                                    dc.AppCurrDataAccessToken):
    labelOptions = ["To Add/Modify L", "To Main L"]

    def __init__(self, patentWidget, prefix, data = None, name = None, text = None):
        if data == None:
            data = {
                ww.Data.GeneralProperties_ID : {"column" : 2, "row" : 13},
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
        # pdfMenuManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
        #                                                 wf.Wr.MenuManagers.PdfReadersManager)
        # pdfMenuManager.layouts[0].pfdReader_BOX.updateScrollerPosition()

        mathMenuManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                         mmm.MathMenuManager)

        if type(mathMenuManager.currLayout) == mmm.LayoutManagers._Main:
            # show the sections UI
            mathMenuManager.switchUILayout(mmm.LayoutManagers._AddModifySection)

            self.updateLabel(self.labelOptions[0])
        else:
            secPath = fsm.Data.Book.subsectionOpenInTOC_UI
            currIdx = fsm.Data.Book.entryImOpenInTOC_UI

            mainTOCManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                            mtocm.MainTOCManager)

            mainTOCManager.moveTocToEntry(secPath, currIdx)

            mathMenuManager.switchUILayout(mmm.LayoutManagers._Main)

            self.updateLabel(self.labelOptions[1])

            # lm.Wr.MainLayout.set(withPdfChange = False)

            mainTOCManager.moveTocToCurrEntry()
            mainTOCManager.scrollToCurrSubsecrtionWidget()

class LayoutsSwitchOrigMatVSMain_BTN(ww.currUIImpl.Button,
                                    dc.AppCurrDataAccessToken):
    labelOptions = ["To Orig Mat L", "To Main L"]

    def __init__(self, patentWidget, prefix, data = None, name = None, text = None):
        if data == None:
            data = {
                ww.Data.GeneralProperties_ID : {"column" : 5, "row" : 13},
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

            # lm.Wr.MainLayout.set()
        else:
            mathMenuManager.switchUILayout(mmm.LayoutManagers._Main)

            self.updateLabel(self.labelOptions[1])

            # lm.Wr.MainLayout.set()

class ShowTocWindow_BTN(ww.currUIImpl.Button,
                  dc.AppCurrDataAccessToken):

    def __init__(self, patentWidget, prefix, row =14, column = 4):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
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

        self.notify(comw.TOC_BOX)
        ocf.Wr.LatexCalls.buildCurrentSubsectionPdf()
    
    def render(self, **kwargs):
        if dt.AppState.ShowProofs.getData(self.appCurrDataAccessToken):
            self.updateLabel(self.labelOptions[1])
        else:
            self.updateLabel(self.labelOptions[0])

        return super().render(**kwargs)

class AddGlobalLink_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix, column = 0, row = 2):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row, "columnspan" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        defaultText = ""
        name = "_addGlobalLink_ETR"

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        defaultText = defaultText,
                        )

        super().setData(self.defaultText)
    
    def receiveNotification(self, broadcasterType, data = None):
        if broadcasterType == AddWebLink_BTN:
            return self.getData()

class AddWebLink_BTN(ww.currUIImpl.Button,
                        dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix, column = 2, row = 2):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
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
        sourceIDX = fsm.Data.Book.entryImOpenInTOC_UI

        webAddress = self.notify(AddGlobalLink_ETR)
        linkName = self.notify(mui.ImageGeneration_ETR)

        gm.GeneralManger.AddWebLink(linkName, webAddress, sourceSubsection, sourceIDX, sourceTopSection)
        self.notify(comw.TOC_BOX)

class MainMenuRoot(ww.currUIImpl.Frame):
    def __init__(self, rootWidget):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 1, "row" : 0, "columnspan": 1},#
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NE}
        }
        name = "MainMenuRoot"
        prefix = ""

        super().__init__(prefix, name, rootWidget, renderData)

        self.rebind([ww.currUIImpl.Data.BindID.enterWidget],
                    [lambda *args: self.forceFocus()])

    def render(self, changePdfReader = True):
        # origMatName = fsm.Data.Book.currOrigMatName
        # fsm.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(origMatName)

        def __showPdf(*args):
            pdfMenuManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.PdfReadersManager)
            if not pdfMenuManager.shown:
                pdfMenuManager.show(changePrevPos = False)
                pdfMenuManager.show(changePrevPos = False)

        if changePdfReader:
            t = Thread(target= __showPdf)
            t.start()

        return super().render()