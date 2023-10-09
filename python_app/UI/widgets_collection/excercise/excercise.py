import tkinter as tk
import Pmw

import UI.widgets_wrappers as ww
import UI.widgets_collection.utils as _ucomw

class ExcerciseImage(ww.currUIImpl.Frame):
    displayedImages = []
    ssubsection = None
    entryIdx = None

    def __init__(self, parentWidget):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0, "columnspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.NW}
        }
        name = "_excerciseImage_LBL"
        prefix = ""

        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data)
    
    def render(self, **kwargs):
                
        # get an image from the
        widget = self.widgetObj

        for child in widget.winfo_children():
            child.destroy()

        balloon = Pmw.Balloon(widget)
        self.imLabel = _ucomw.addMainEntryImageWidget(widget, 
                                                      self.subsection, self.entryIdx,
                                                      120, self.displayedImages, balloon)
        exImLabels = _ucomw.addExtraEntryImagesWidgets(widget, 
                                                       self.subsection, self.entryIdx,
                                                       120, self.displayedImages, balloon)
        self.imLabel.render()
        for l in exImLabels:
            l.render()
        self.imLabel.focus_force()
        return super().render(**kwargs)
    
    # def receiveNotification(self, broadcasterType, data = None, secPath = None):
    #     if broadcasterType == ChooseTopSection_OM:
    #         newText = self.__getSectionPath_Formatted(secPath)
    #         self.changeText(newText)
        
    #     if broadcasterType == ChooseSubsection_OM:
    #         newText = self.__getSectionPath_Formatted(secPath)
    #         self.changeText(newText)
        
    #     if broadcasterType == ModifySubsection_BTN:
    #         newText = self.__getSectionPath_Formatted(secPath)
    #         self.changeText(newText)
        
    # def __getCurrSectionPath_Formatted(self):
    #     currSecName = fsf.Wr.SectionCurrent.getSectionNameNoPrefix()

    #     return self.__getSectionPath_Formatted(currSecName)
        
    # def __getSectionPath_Formatted(self, secName):
    #     name = fsf.Data.Sec.text(secName)
    #     startPage = fsf.Data.Sec.start(secName)

    #     return "working section path: {0}. Name: '{1}'. Start page: '{2}'".format(secName, name, startPage)

    # def render(self, widjetObj=None, renderData=..., **kwargs):
    #     text = self.__getCurrSectionPath_Formatted()
    #     self.changeText(text)

    #     return super().render(widjetObj, renderData, **kwargs)

class ExcerciseRoot(ww.currUIImpl.RootWidget):
    pass