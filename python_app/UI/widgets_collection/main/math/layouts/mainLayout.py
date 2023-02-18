import os
import subprocess
import tkinter as tk
from threading import Thread

import UI.widgets_vars as wv 
import UI.widgets_utils as wu
import UI.widgets_messages as wmes

import file_system.file_system_manager as fsm
import tex_file.tex_file_facade as tff

import _utils.logging as log
import _utils._utils_main as _u

import data.constants as d
import data.temp as dt
import scripts.osascripts as oscr

import outside_calls.outside_calls_facade as ocf

import UI.widgets_wrappers as ww
import UI.widgets_manager as wm

class ImageGeneration_BTN(ww.currUIImpl.Button):
    labelOptions = ["imIdx", "imName"]

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
        dataFromUser = [-1, -1]
        
        def _createTexForTheProcessedImage():
            bookName = _u.Settings.readProperty(_u.Settings.PubProp.currBookName_ID)
            currSubsection = fsm.Wr.SectionCurrent.readCurrSection()

            

            # ADD CONTENT ENTRY TO THE PROCESSED CHAPTER
            tff.Wr.TexFileModify.addProcessedImage(dataFromUser[0], dataFromUser[1])

            if wv.UItkVariables.createTOCVar.get():
                if wv.UItkVariables.TOCWithImageVar.get():
                    # TOC ADD ENTRY WITH IMAGE
                    with open(fsm.Wr.Paths.TexFiles.TOC.getAbs_curr(), 'a') as f:
                        toc_add_image = d.Links.Local.getIdxLineMarkerLine(dataFromUser[0]) + " \n"
                        toc_add_image += "\
    \\mybox{\n\
        \\link[" + dataFromUser[0] + \
        "]{" + dataFromUser[1] + "} \\image[0.5]{" + \
        dataFromUser[0] + "_" + currSubsection + "_" + dataFromUser[1] + "}\n\
    }\n\n\n"
                        f.write(toc_add_image)
                else:  
                    # TOC ADD ENTRY WITHOUT IMAGE
                    with open(fsm.Wr.Paths.TexFiles.TOC.getAbs_curr(), 'a') as f:
                        toc_add_text = d.Links.Local.getIdxLineMarkerLine(dataFromUser[0]) + " \n"
                        toc_add_text += "\
    \\mybox{\n\
        \\link[" + dataFromUser[0] + "]{" + dataFromUser[1] + "} \\textbf{!}\n\
    }\n\n\n"
                        f.write(toc_add_text)
                

            #create a script to run on page change
            imagePath = os.path.join(fsm.Wr.Paths.Screenshot.getAbs_curr(),
                                    dataFromUser[0] + "_" + currSubsection + "_" + dataFromUser[1])

            # STOTE IMNUM, IMNAME AND LINK
            fsm.Wr.SectionCurrent.setImLinkAndIDX(dataFromUser[1], dataFromUser[0])
            
            # POPULATE THE MAIN FILE
            tff.Wr.TexFile._populateMainFile()
            
            
            # take a screenshot
            imIDX = dataFromUser[0]
            pdfFilepath = fsm.Wr.Paths.PDF.getAbs_curr()
            if os.path.isfile(imagePath + ".png"):
                def takeScreencapture(iPath, sPath):
                    os.system("screencapture -ix " + iPath + ".png")
                    wv.UItkVariables.needRebuild.set(True)
                    # update curr image index for the chapter
                    nextImNum = str(int(dataFromUser[0]) + 1)
                    wv.UItkVariables.imageGenerationEntryText.set(nextImNum)
                    wv.UItkVariables.buttonText.set("imNum")
                
                wmes.ConfirmationMenu.createMenu("The file exists. Overrite?", 
                                                takeScreencapture, 
                                                currSubsection,
                                                bookName)
            else:
                os.system("screencapture -ix " + imagePath + ".png")
                wv.UItkVariables.needRebuild.set(True)
                #update curr image index for the chapter
                nextImNum = str(int(dataFromUser[0]) + 1)
                wv.UItkVariables.imageGenerationEntryText.set(nextImNum)
        
        buttonNamesToFunc = {self.labelOptions[0]: lambda *args: self.notify(ImageGeneration_ETR, ""),
                            self.labelOptions[1]: _createTexForTheProcessedImage}

        for i in range(len(self.labelOptions)):
            if self.labelOptions[i] == self.text:
                nextButtonName = self.labelOptions[(i+1)%len(self.labelOptions)]
                sectionImIndex = fsm.Wr.Links.ImIDX.get_curr()
                dataFromUser[i] = self.notify(ImageGeneration_ETR, sectionImIndex) 
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
        super().__init__(prefix, 
                        name,
                        patentWidget, 
                        data)

        secImIndex = fsm.Wr.Links.ImIDX.get_curr()

        if secImIndex == _u.Token.NotDef.str_t:
            self.updateDafaultText("-1")
        else:
            self.updateDafaultText(str(int(secImIndex) + 1))

    def receiveNotification(self, broadcasterType, dataToSet = None):
        if broadcasterType == ImageGenerationRestart_BTN:
            self.setData(dataToSet)
        elif broadcasterType == ImageGeneration_BTN:
            self.setData(dataToSet)
           

class AddExtraImage_BTN(ww.currUIImpl.Button):
    
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.E}
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
        currentSubsection = fsm.Wr.SectionCurrent.readCurrSection()
        currImID = fsm.Wr.Links.ImIDX.get_curr()
        
        # screenshot
        imName = ""

        # get name of the image from the text field
        # NOTE: need to refactor into a separate function
        for w in self.patentWidget.getChildren():
            if "_imageGeneration_" + wu.Data.ENT.entryWidget_ID in w._name:
                imName = w.get()
        
        extraImagePath = fsm.Wr.Paths.Screenshot.getAbs_curr() \
                            + currImID + "_" + currentSubsection \
                            + "_" + imName
        
        if os.path.isfile(extraImagePath + ".png"):
            def takeScreenshotWrapper(savePath):
                ocf.Wr.ScreenshotCalls.takeScreenshot(savePath)
                wv.UItkVariables.needRebuild.set(True)
            
            wmes.ConfirmationMenu.createMenu("The file exists. Overrite?", 
                                            takeScreenshotWrapper, 
                                            extraImagePath + ".png")
        else:
            ocf.Wr.ScreenshotCalls.takeScreenshot(extraImagePath)
            wv.UItkVariables.needRebuild.set(True)

        tff.Wr.TexFileModify.addExtraImage(currImID, extraImagePath)
        
   
        # return ww.currUIImpl.Button(rootWidget = mainWinRoot, 
        #                 name = prefixName.lower() + "_imageGenerationAddImBTN",
        #                 text= "addIm",
        #                 command = lambda: addImBTNcallback())

class ImageGenerationRestart_BTN(ww.currUIImpl.Button):

    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 3, "row" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
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
