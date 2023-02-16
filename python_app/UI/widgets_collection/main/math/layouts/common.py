import tkinter as tk

import _utils._utils_main as _u

import UI.widgets_wrappers as ww
import UI.widgets_utils as wu

class MainMenuRoot(ww.currUIImpl.RootWidget):
    pass


class Layouts_OM(ww.currUIImpl.OptionMenu):
    renderData = {
        ww.Data.GeneralProperties_ID : {"column" : 1, "row" : 0},
        ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
    }
    name = "_layouts_optionMenu"

    def __init__(self, patentWidget, prefix):
        self.listOfLayouts = _u.Settings.layoutsList

        super().__init__(prefix, self.name, self.listOfLayouts,
                        patentWidget, self.renderData, self.cmd)

        self.setData(self.listOfLayouts[0])
    
    def cmd(self):
        _u.Settings.currLayout = self.getData()

        # call layout manager to change the UI
               
        # _u.Settings.updateProperty(_u.Settings.PubProp.currLayout_ID, self.getData())
        
        


        for cl in LayoutsMenus.listOfLayoutClasses:
            if self.getData().lower() in cl.__name__.lower():
                wu.showCurrentLayout(mainWinRoot, 
                                    cl.pyAppDimensions[0],
                                    cl.pyAppDimensions[1])
                
                #update the section layout UI
                # if "section" in cl.__name__.lower():
                #     currSection = fsm.Wr.SectionCurrent.readCurrSection()
                #     currChImageLinks = fsm.Wr.Links.LinkDict.getCurrImLinksSorted(currSection)
                #     wu.updateOptionMenuOptionsList(mainWinRoot, 
                #                                 "source_SecImIDX", 
                #                                 currChImageLinks,
                #                                 wv.UItkVariables.glLinkSourceImLink,
                #                                 lambda *argv: None)
                    
                #     # set to the latest link
                #     wv.UItkVariables.glLinkSourceImLink.set(currChImageLinks[-1])
                # break 