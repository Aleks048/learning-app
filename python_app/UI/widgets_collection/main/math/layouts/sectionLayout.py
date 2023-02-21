import tkinter as tk
from threading import Thread
import subprocess

import UI.widgets_wrappers as ww
import file_system.file_system_manager as fsm
import _utils.logging as log
import tex_file.tex_file_facade as tff
import scripts.osascripts as oscr


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