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

import UI.widgets_facade as wf


class LayoutsMenus:
    class SectionLayoutUI:
        pyAppDimensions = [None, None]
        classPrefix = "sectionlayout"

        @classmethod
        def addWidgets(cls, winMainRoot):
            pass
    
    class MainLayoutUI:
        pyAppDimensions = [None, None]
        classPrefix = "mainlayout"

        @classmethod
        def addWidgets(cls, winMainRoot):  
            return          
            mon_width, _ = _u.getMonitorSize()
            cls.pyAppDimensions = [int(mon_width / 2), 90]
            
    
            #
            # switch to sections menus
            #
            chooseSectionsMenusAndbackBtn = SectionsUI.getButton_chooseSectionsMenusAndBack(winMainRoot, cls.classPrefix)
            chooseSectionsMenusAndbackBtn.grid(column = 3, row = 0, padx = 0, pady = 0)

    class WholeVSCodeLayoutUI:
        pyAppDimensions = [None, None]

        @classmethod
        def addWidgets(cls, winMainRoot):
            layoutOM = LayoutsMenus._commonWidgets.getOptionsMenu_Layouts(winMainRoot, cls.__name__)
            layoutOM.grid(column=0, row=0, padx=0, pady=0)
            layoutOM.update()
            cls.pyAppDimensions[0] = layoutOM.winfo_width()
            cls.pyAppDimensions[1] = layoutOM.winfo_height()

    class _commonWidgets:
        @classmethod
        def getOptionsMenu_Layouts(cls, mainWinRoot, namePrefix = ""):
            def layoutOptionMenuCallback(layout_name_vatying):
                _u.Settings.currLayout = layout_name_vatying.get()
               
                _u.Settings.updateProperty(_u.Settings.PubProp.currLayout_ID, layout_name_vatying.get())
                
                for cl in LayoutsMenus.listOfLayoutClasses:
                    if layout_name_vatying.get().lower() in cl.__name__.lower():
                        wu.showCurrentLayout(mainWinRoot, 
                                            cl.pyAppDimensions[0],
                                            cl.pyAppDimensions[1])
                        
                        if "section" in cl.__name__.lower():
                            currSection = fsm.Wr.SectionCurrent.readCurrSection()
                            currChImageLinks = fsm.Wr.Links.LinkDict.getCurrImLinksSorted(currSection)
                            wu.updateOptionMenuOptionsList(mainWinRoot, 
                                                        "source_SecImIDX", 
                                                        currChImageLinks,
                                                        wv.UItkVariables.glLinkSourceImLink,
                                                        lambda *argv: None)
                            
                            # set to the latest link
                            wv.UItkVariables.glLinkSourceImLink.set(currChImageLinks[-1])

                        break 
            
            listOfLayouts = _u.Settings.layoutsList
            layout_name_vatying = tk.StringVar()
            layout_name_vatying.set(listOfLayouts[0])

            frame = tk.Frame(mainWinRoot, 
                            name = namePrefix.lower() + "_layouts_optionMenu", background="Blue")        
            layouts_optionMenu = tk.OptionMenu(frame, 
                                        layout_name_vatying, 
                                        *listOfLayouts, 
                                        command= lambda x: layoutOptionMenuCallback(layout_name_vatying))
            
            layouts_optionMenu.grid(row=0, column=0)
            
            return frame

    listOfLayoutClasses = [MainLayoutUI, SectionLayoutUI]

 
      


