import os
import tkinter as tk
import time
import re
from threading import Thread

import file_system.file_system_facade as fsf
import tex_file.tex_file_facade as tff

import _utils._utils_main as _u
import _utils.pathsAndNames as _upan

import outside_calls.outside_calls_facade as ocf

import UI.widgets_wrappers as ww
import UI.widgets_facade as wf
import UI.widgets_collection.main.math.manager as mmm
import UI.widgets_collection.main.math.UI_layouts.common as commw
import UI.widgets_collection.common as comw
import UI.widgets_manager as wm

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


class ExitApp_BTN(ww.currUIImpl.Button,
                  dc.AppCurrDataAccessToken):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 4, "row" : 13},
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
        # close original material document
        # fsf.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(self.prevChoice)
        # prevChoiceID = fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsFilename(self.prevChoice)
        # _, _, oldPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, 
        #                                             prevChoiceID)     
        
        # if oldPID != None:
        #     lf.Wr.LayoutsManager.closePDFwindow(prevChoiceID, oldPID)
        
        # time.sleep(0.3)

        # open another original material

        # origMatPath = fsf.Wr.OriginalMaterialStructure.getMaterialPath(origMatName)
        # ocf.Wr.PdfApp.openPDF(origMatPath, origMatCurrPage)

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
        # width, height = _u.getMonitorSize()
        # halfWidth = int(width / 2)

        # newChoiceID = fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsFilename(origMatName)
        # _, _, newPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, 
        #                                             newChoiceID)
        # while newPID == None:
        #     time.sleep(0.1)
        #     _, _, newPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, 
        #                                             newChoiceID)
        # cmd = oscr.getMoveWindowCMD(newPID, [halfWidth, height, 0, 0], newChoiceID)
        # _u.runCmdAndWait(cmd)

        # update book settings
        fsf.Data.Book.currOrigMatName = origMatName
    
    def render(self, widjetObj=None, renderData=..., **kwargs):
        names = fsf.Wr.OriginalMaterialStructure.getOriginalMaterialsNames()
        self.updateOptions(names)

        currOrigMatName = fsf.Data.Book.currOrigMatName
        self.setData(currOrigMatName)

        return super().render(widjetObj, renderData, **kwargs)

class ScreenshotLocation_LBL(ww.currUIImpl.Label):
    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 2, "columnspan": 5},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
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
        if broadcasterName == comw.TOC_BOX:
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
                msg = "Incorrect image index \n\nId: '{0}'.".format(self.dataFromUser[0])
                wm.UI_generalManager.showNotification(msg, True)

                mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                            mmm.MathMenuManager)
                mainManager.show()

                return

            addToTOCwIm = self.notify(addToTOCwImage_CHB)
            textOnly = self.notify(TextOnly_CHB)

            msg = "\
Do you want to create entry with \n\nId: '{0}',\n\n Name: '{1}'".format(self.dataFromUser[0], self.dataFromUser[1])
            response = wm.UI_generalManager.showNotification(msg, True)
            
            if not response:
                mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                            mmm.MathMenuManager)
                mainManager.show()
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

                while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                    time.sleep(0.3)
                    timer += 1

                    if timer > 50:
                        return False

                nextImNum = str(int(currImNum) + 1)

                self.rootWidget.render()
                self.notify(ImageGeneration_ETR, nextImNum)
                self.updateLabel(self.labelOptions[0])
                self.notify(comw.TOC_BOX, entryClicked = self.dataFromUser[0])

            t = Thread(target = __afterImageCreated, args = [self])
            t.start()
            dt.AppState.ShowProofs.setData(self.appCurrDataAccessToken,
                                           False)
            mainManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                            mmm.MathMenuManager)
            mainManager.show()
        
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

        if "." in fsf.Data.Book.currSection:
            secImIndex = fsf.Wr.Links.ImIDX.get_curr()
        else:
            secImIndex = _u.Token.NotDef.str_t

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
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.cmdshp,
                  lambda *args: __addProposion(*args))

        def __addProof(*args):
            boldSelText = "proof"
            self.widgetObj.insert("0", boldSelText)
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.cmdp,
                  lambda *args: __addProof(*args))

        def __addExample(*args):
            boldSelText = "\\textbf{EX:} "
            self.widgetObj.insert("0", boldSelText)
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.cmde,
                  lambda *args: __addExample(*args))

        def __addLemma(*args):
            boldSelText = "\\textbf{Lemma:} "
            self.widgetObj.insert("0", boldSelText)
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.cmdl,
                  lambda *args: __addLemma(*args))
        
        def __addCorollary(*args):
            boldSelText = "\\textbf{Corollary:} "
            self.widgetObj.insert("0", boldSelText)
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.cmdshc,
                  lambda *args: __addCorollary(*args))

        def __addCode(*args):
            boldSelText = "\\textbf{Code:} "
            self.widgetObj.insert("0", boldSelText)
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.cmddc,
                  lambda *args: __addCode(*args))

        def __addExcecise(*args):
            boldSelText = "\\textbf{\\underline{EXCERCISE:}} "
            self.widgetObj.insert("0", boldSelText)
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.cmdshe,
                  lambda *args: __addExcecise(*args))

        def __addTheorem(*args):
            boldSelText = "\\textbf{Theorem:} "
            self.widgetObj.insert("0", boldSelText)
        
        self.widgetObj.bind(ww.currUIImpl.Data.BindID.Keys.cmdt,
                  lambda *args: __addTheorem(*args))

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
            if "." in fsf.Data.Book.currSection:
                currImIdx = int(fsf.Wr.SectionCurrent.getImIDX())
            else:
                currImIdx = _u.Token.NotDef.int_t

            nextImIdx = str(currImIdx + 1)
            self.setData(nextImIdx)
            self.widgetObj.focus_force()
            return
        elif broadcasterType == ImageGeneration_BTN:
            prevData = self.getData()

            if prevData == "":
                prevData = _u.Token.NotDef.str_t

            if dataToSet != None:
                self.setData(dataToSet)

            self.widgetObj.focus_force()

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
Do you want to add \n\n\
group: '{0}' \n\n\
to subsection: '{1}'?".format(groupName, currSubsection)
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
