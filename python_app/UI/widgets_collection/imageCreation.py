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



class AddExtraImage_BTN(ww.currUIImpl.Button):
    data = {"column" : 3, "row" : 1, "padx" : 0, "pady" : 0, "sticky" : tk.E}
    name = "_imageGenerationAddImBTN"
    text= "addIm"
    
    def __init__(self, patentWidget, prefix):
        super().__init__(prefix, self.name, self.text, patentWidget, self.data, self.cmd)

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
    data = {"column" : 3, "row" : 1, "padx" : 0, "pady" : 0, "sticky" : tk.W}
    name = "_imageGenerationRestartBTN"
    text= "restart"

    def __init__(self, patentWidget, prefix):
        super().__init__(prefix, self.name, self.text, 
                        patentWidget, self.data, self.cmd)

    def cmd(self):
        wv.UItkVariables.buttonText.set("imNum")
        sectionImIndex = fsm.Wr.Links.ImIDX.get_curr()
        wv.UItkVariables.imageGenerationEntryText.set(sectionImIndex)


class ImageCreation:
    pass
