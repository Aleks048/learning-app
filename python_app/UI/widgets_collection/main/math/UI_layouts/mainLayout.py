import os
import tkinter as tk

import file_system.file_system_facade as fsf
import tex_file.tex_file_facade as tff

import _utils.logging as log
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan

import outside_calls.outside_calls_facade as ocf

import UI.widgets_wrappers as ww

import UI.widgets_collection.main.math.manager as mmm
import layouts.layouts_manager as lm

import data.constants as dc
import data.temp as dt


class SwitchToCurrSectionLayout_BTN(ww.currUIImpl.Button,
                                    dc.AppCurrDataAccessToken):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 4, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_swritchToCurrSectionLayout_BTN"
        text= "To section"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        data, 
                        self.cmd)

    def cmd(self):
        tff.Wr.TexFile.buildCurrentSubsectionPdf()
        # switch UI
        mathMenuManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken, mmm.MathMenuManager)
        mathMenuManager.switchUILayout(mmm.LayoutManagers._Section)
        # switch other apps
        lm.Wr.SectionLayout.set()


class ChooseSubsection_OM(ww.currUIImpl.OptionMenu):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 2},
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
        subsection = self.getData()
        sections = fsf.Wr.BookInfoStructure.readProperty(fsf.PropIDs.Book.sections_ID)
        topSection = self.notify(ChooseTopSection_OM)
        sections[topSection]["prevSubsectionPath"] = subsection
        fsf.Wr.BookInfoStructure.updateProperty(fsf.PropIDs.Book.sections_ID , sections)
        
        fsf.Wr.BookInfoStructure.updateProperty(fsf.PropIDs.Book.currSection_ID , subsection)
        
        self.notify(ImageGeneration_ETR, fsf.Wr.Links.ImIDX.get(subsection))

        self.notify(ScreenshotLocation_LBL)

        lm.Wr.MainLayout.set()
    
    def receiveNotification(self, broadcasterType, newOptionList = [], prevSubsectionPath = "", *args) -> None:
        if broadcasterType == ChooseTopSection_OM:
            self.updateOptions(newOptionList)
            self.setData(prevSubsectionPath)

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
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }
        name = "_chooseSection_optionMenu"

        topSectionsList = fsf.Wr.BookInfoStructure.getTopSectionsList()
        topSectionsList.sort(key = int)

        if topSectionsList == []:
            topSectionsList = ["No top sec yet."]

        super().__init__(prefix, 
                        name, 
                        topSectionsList,
                        patentWidget, 
                        renderData, 
                        self.cmd)
        
        currTopSection = fsf.Wr.BookInfoStructure.readProperty(fsf.PropIDs.Book.currTopSection_ID)
        self.setData(currTopSection)
    
    def cmd(self):
        topSection = self.getData()
        log.autolog("switching to top section: " + topSection)

        # update top section
        fsf.Wr.BookInfoStructure.updateProperty(fsf.PropIDs.Book.currTopSection_ID , 
                                                topSection)
        
        # update subsection
        sections = fsf.Wr.BookInfoStructure.readProperty(fsf.PropIDs.Book.sections_ID)
        prevSubsectionPath = sections[topSection]["prevSubsectionPath"]
        fsf.Wr.BookInfoStructure.updateProperty(fsf.PropIDs.Book.currSection_ID, 
                                                prevSubsectionPath)

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
        self.notify(ScreenshotLocation_LBL)

        # update image index widget
        self.notify(ImageGeneration_ETR, 
                    fsf.Wr.Links.ImIDX.get(prevSubsectionPath))
        
        lm.Wr.MainLayout.set()
    
    def receiveNotification(self, broadcasterType):
        if broadcasterType == ChooseSubsection_OM:
            return self.getData()
    
    def render(self, widjetObj=None, renderData=..., **kwargs):
        topSectionsList = fsf.Wr.BookInfoStructure.getTopSectionsList()
        topSectionsList.sort(key = int)
        if topSectionsList == []:
            topSectionsList = ["No top sec yet."]
        
        self.setData(topSectionsList)

        currTopSection = fsf.Wr.BookInfoStructure.readProperty(fsf.PropIDs.Book.currTopSection_ID)
        self.setData(currTopSection)

        return super().render(widjetObj, renderData, **kwargs)


class ScreenshotLocation_LBL(ww.currUIImpl.Label):
    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 1, "row" : 2, "columnspan": 4},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_showCurrScreenshotLocation_text"
        text = _upan.Current.Paths.Screenshot.rel_formatted()
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data, 
                        text = text)
    
    def receiveNotification(self, broadcasterName, data = None):
        if broadcasterName == ChooseTopSection_OM:
            self.changeText(_upan.Current.Paths.Screenshot.rel_formatted())
        if broadcasterName == ChooseSubsection_OM:
            self.changeText(_upan.Current.Paths.Screenshot.rel_formatted())
    
    def render(self, widjetObj=None, renderData=..., **kwargs):
        text = _upan.Current.Paths.Screenshot.rel_formatted()
        self.changeText(text)
        return super().render(widjetObj, renderData, **kwargs)

class addToTOC_CHB(ww.currUIImpl.Checkbox):
    def __init__(self, parentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_create_toc"
        text = "add TOC entry"
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = renderData, 
                        text = text)
        self.setData(True)
        
    def receiveNotification(self, broadcasterName):
        return self.getData()

class addToTOCwImage_CHB(ww.currUIImpl.Checkbox):   
    def __init__(self, parentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 1, "row" : 1},
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
        return self.getData()

class ImageGeneration_BTN(ww.currUIImpl.Button):
    labelOptions = ["imIdx", "imName"]
    dataFromUser = [-1, -1]

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 2, "row" : 1},
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
            bookName = _u.Settings.readProperty(_u.Settings.PubProp.currBookName_ID)
            currSubsection = _upan.Current.Names.Section.name()

            # ADD CONTENT ENTRY TO THE PROCESSED CHAPTER
            tff.Wr.TexFileModify.addProcessedImage(self.dataFromUser[0], self.dataFromUser[1])

            if self.notify(addToTOC_CHB):
                if self.notify(addToTOCwImage_CHB):
                    # TOC ADD ENTRY WITH IMAGE
                   tff.Wr.TexFileModify.addImageLinkToTOC_wImage(self.dataFromUser[0], self.dataFromUser[1])
                else:  
                    # TOC ADD ENTRY WITHOUT IMAGE
                   tff.Wr.TexFileModify.addImageLinkToTOC_woImage(self.dataFromUser[0], self.dataFromUser[1])
            
            imagePath = os.path.join(_upan.Current.Paths.Screenshot.abs,
                                    str(self.dataFromUser[0]) + "_" + currSubsection + "_" + str(self.dataFromUser[1]))

            # STOTE IMNUM, IMNAME AND LINK
            fsf.Wr.SectionCurrent.setImLinkAndIDX(self.dataFromUser[1], self.dataFromUser[0])
            
            # POPULATE THE MAIN FILE
            tff.Wr.TexFile._populateMainFile()
            
            # take a screenshot
            if ocf.Wr.fsAppCalls.checkIfFileExists(imagePath):
                def takeScreencapture(iPath):
                    ocf.Wr.ScreenshotCalls.takeScreenshot(iPath)
                    nextImNum = str(int(self.dataFromUser[0]) + 1)
                    self.notify(ImageGeneration_ETR, nextImNum)
                    self.updateLabel(self.labelOptions[0])
                
                # wmes.ConfirmationMenu.createMenu("The file exists. Overrite?", 
                #                                 takeScreencapture, 
                #                                 imagePath)
            else:
                ocf.Wr.ScreenshotCalls.takeScreenshot(imagePath)
                nextImNum = str(int(self.dataFromUser[0]) + 1)
                self.notify(ImageGeneration_ETR, nextImNum)
        
        buttonNamesToFunc = {self.labelOptions[0]: lambda *args: self.notify(ImageGeneration_ETR, ""),
                            self.labelOptions[1]: _createTexForTheProcessedImage}

        for i in range(len(self.labelOptions)):
            if self.labelOptions[i] == self.text:
                nextButtonName = self.labelOptions[(i+1)%len(self.labelOptions)]
                sectionImIndex = fsf.Wr.Links.ImIDX.get_curr()
                self.dataFromUser[i] = self.notify(ImageGeneration_ETR, sectionImIndex) 
                buttonNamesToFunc[self.labelOptions[i]]()
                self.updateLabel(nextButtonName)
                break


    def receiveNotification(self, broadcasterType):
        if broadcasterType == ImageGenerationRestart_BTN:
            self.updateLabel(self.labelOptions[0])

class ImageGeneration_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 2, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        name = "_imageGeneration_ETR"
        defaultText = "1"

        super().__init__(prefix, 
                        name,
                        patentWidget, 
                        data,
                        defaultText = defaultText)

        secImIndex = fsf.Wr.Links.ImIDX.get_curr()

        if secImIndex == _u.Token.NotDef.str_t:
            self.updateDafaultText(self.defaultText)
        else:
            self.updateDafaultText(str(int(secImIndex) + 1))

    def receiveNotification(self, broadcasterType, dataToSet = None):
        if broadcasterType == ImageGenerationRestart_BTN:
            currImIdx = str(int(fsf.Wr.SectionCurrent.getImIDX()) + 1)
            self.setData(currImIdx)
        elif broadcasterType == ImageGeneration_BTN:
            prevData = self.getData()
            log.autolog(dataToSet)
            self.setData(dataToSet)
            return prevData
        elif broadcasterType == ChooseTopSection_OM:
            currIdx = fsf.Wr.SectionCurrent.getImIDX()
            currIdx = 0 if currIdx == '' else int(currIdx)
            nextIdx = str(currIdx + 1)
            self.setData(nextIdx)
        elif broadcasterType == ChooseSubsection_OM:
            currIdx = fsf.Wr.SectionCurrent.getImIDX()
            currIdx = 0 if currIdx == '' else int(currIdx)
            nextIdx = str(currIdx + 1)
            self.setData(nextIdx)
        elif broadcasterType == AddExtraImage_BTN:
            return self.getData()
    
    def render(self, **kwargs):
        secImIndex = fsf.Wr.Links.ImIDX.get_curr()

        if secImIndex == _u.Token.NotDef.str_t:
            self.updateDafaultText("1")
        else:
            self.updateDafaultText(str(int(secImIndex) + 1))

        return super().render(**kwargs)

    def defaultTextCMD(self):
        pass

class AddExtraImage_BTN(ww.currUIImpl.Button):  
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 1, "row" : 0},
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
        currentSubsection = _upan.Current.Names.Section.name()
        currImID = fsf.Wr.Links.ImIDX.get_curr()
        
        # screenshot
        imName = ""

        # get name of the image from the text field
        # NOTE: need to refactor into a separate function
        imName = self.notify(ImageGeneration_ETR)
        
        extraImagePath = _upan.Current.Paths.Screenshot.abs() \
                            + currImID + "_" + currentSubsection \
                            + "_" + imName
        
        if os.path.isfile(extraImagePath + ".png"):
            def takeScreenshotWrapper(savePath):
                ocf.Wr.ScreenshotCalls.takeScreenshot(savePath)
            
            # wmes.ConfirmationMenu.createMenu("The file exists. Overrite?", 
            #                                 takeScreenshotWrapper, 
            #                                 extraImagePath + ".png")
        else:
            ocf.Wr.ScreenshotCalls.takeScreenshot(extraImagePath)

        tff.Wr.TexFileModify.addExtraImage(currImID, extraImagePath)
        
   
        # return ww.currUIImpl.Button(rootWidget = mainWinRoot, 
        #                 name = prefixName.lower() + "_imageGenerationAddImBTN",
        #                 text= "addIm",
        #                 command = lambda: addImBTNcallback())

class ImageGenerationRestart_BTN(ww.currUIImpl.Button):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
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

class ImageCreation:
    pass
