from tkinter import ttk
import tkinter as tk

import UI.widgets_wrappers as ww
import file_system.file_system_facade as fsf
import data.constants as dc
import UI.widgets_collection.common as comw



class TOCFrame(ttk.Frame):
    def __init__(self, root, prefix, row, column, columnspan = 1, *args, **kwargs) -> None:
        self.row = row
        self.column = column
        self.columnspan = columnspan

        super().__init__(root, name = prefix, *args, **kwargs)

    def render(self):
        self.grid(row = self.row, column = self.column, 
                  columnspan = self.columnspan, sticky=tk.NW)

    def getChildren(self):
        return self.winfo_children()

class TOCLabelWithClick(ttk.Label):
    '''
    this is used to run different commands on whether the label was clicked even or odd times
    '''
    clicked = False
    imIdx = ""
    subsection = ""
    imagePath = ""
    group = ""
    image = None
    alwaysShow = None
    shouldShowExMenu = False

    def rebind(self, keys, cmds):
        for i in range(len(keys)):
            key = keys[i]
            cmd = cmds[i]

            if key == ww.TkWidgets.Data.BindID.allKeys:
                self.bind_all(key, lambda event: cmd(event))
            else:
                self.bind(key, cmd)
    
    def __init__(self, root, prefix, row, column, columnspan = 1, *args, **kwargs) -> None:
        self.row = row
        self.column = column
        self.columnspan = columnspan

        super().__init__(root, name = prefix, *args, **kwargs)
    
    def render(self):
        self.grid(row = self.row, column = self.column,
                  columnspan = self.columnspan, sticky=tk.NW)

    def generateEvent(self, event, *args, **kwargs):
        self.event_generate(event, *args, **kwargs)

    def getChildren(self):
        return self.winfo_children()


def closeAllImages(gpframe, showAll, isWidgetLink):
    '''
    close all images of children of the widget
    '''
    for parent in gpframe.getChildren():
        for child in parent.getChildren():
            if "contentOfImages_" in str(child):
                subsection = str(child).split("_")[-2].replace("$", ".")
                idx = str(child).split("_")[-1]
                alwaysShow = fsf.Data.Sec.tocWImageDict(subsection)[idx] == "1"

                if (not alwaysShow) or showAll: 
                    child.clicked = False
                else: 
                    child.clicked = True

            if "contentGlLinksOfImages_" in str(child):
                child.clicked = False

            if dc.UIConsts.imageWidgetID in str(child):
                subsection = str(child).split("_")[-2].replace("$", ".")
                idx = str(child).split("_")[-1]
                alwaysShow = fsf.Data.Sec.tocWImageDict(subsection)[idx] == "1"

                if (not alwaysShow) or showAll or isWidgetLink: 
                    try:
                        child.destroy()
                    except:
                        pass