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
import UI.widgets_collection.mainTOC.manager as mtocm
import UI.widgets_collection.main.math.UI_layouts.common as commw
import UI.widgets_collection.common as comw
import UI.widgets_manager as wm
import UI.factories.factoriesFacade as wff

import data.constants as dc
import data.temp as dt

import settings.facade as sf


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

        gm.GeneralManger.ExitApp()
        

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
            text = text.replace("\n", "") 
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
                mainTOCManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                            mtocm.MainTOCManager)
                mainTOCManager.addEntry(currSubsection, currImNum)

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
            pdfReadersManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                        wf.Wr.MenuManagers.PdfReadersManager)
            entriesList = list(fsf.Data.Sec.imLinkDict(currSubsection).keys())
            entriesList.sort(key = int)
            imIdx = entriesList[-1]
            pdfReadersManager.showVideo(currSubsection, str(imIdx))    
        
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
