import tkinter as tk
from tkinter import ttk
import os

import UI.widgets_wrappers as ww
import file_system.file_system_facade as fsf
import _utils.pathsAndNames as _upan
import outside_calls.outside_calls_facade as ocf
import tex_file.tex_file_facade as tff
import settings.facade as sf

import data.constants as dc
import data.temp as dt
import UI.widgets_collection.toc.manager as tocm

class Hide_BTN(ww.currUIImpl.Button,
                         dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 5, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }
        text = "Hide"
        name = "_decline_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        tocManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                            tocm.TOCManager)
        tocManager.hide()


class LabelWithClick(ttk.Label):
    '''
    this is used to run different commands on whether the label was clicked even or odd times
    '''
    clicked = False



class TOC_BOX(ww.currUIImpl.ScrollableBox):
    subsection = ""
    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0, "columnspan" : 5},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_showCurrScreenshotLocation_text"

        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data,
                        height=500,
                        width=500)
    
    def receiveNotification(self, broadcasterName, data = None):
        pass
    
    def render(self, widjetObj=None, renderData=..., **kwargs):
        return super().render(widjetObj, renderData, **kwargs)
    
    def addTOCEntry(self, subsection, level, idx):
        def openPdfOnStartOfTheSection(widget):
            def __cmd(event = None, *args):
                # open orig material on page
                subsectionStartPage = fsf.Data.Sec.start(subsection)
                origMaterialBookFSPath_curr = _upan.Paths.OriginalMaterial.MainBook.getAbs()
                ocf.Wr.PdfApp.openPDF(origMaterialBookFSPath_curr, subsectionStartPage)

                event.widget.configure(foreground="white")
            
            widget.bind(ww.currUIImpl.Data.BindID.mouse1, __cmd)

        def bindChangeColorOnInAndOut(widget):
            def __changeTextColorBlue(event = None, *args):
                event.widget.configure(foreground="blue")
            
            def __changeTextColorBlack(event = None, *args):
                event.widget.configure(foreground="white")
            
            widget.bind(ww.currUIImpl.Data.BindID.enterWidget, __changeTextColorBlue)
            widget.bind(ww.currUIImpl.Data.BindID.leaveWidget, __changeTextColorBlack)
        
        def openOMOnThePageOfTheImage(widget, imIdx):
            def __cmd(event = None, *args):
                # open orig material on page
                imLinkOMPageDict = fsf.Data.Sec.imLinkOMPageDict(subsection)
                page = imLinkOMPageDict[imIdx]
                origMaterialBookFSPath_curr = _upan.Paths.OriginalMaterial.MainBook.getAbs()
                ocf.Wr.PdfApp.openPDF(origMaterialBookFSPath_curr, page)
            
            widget.bind( ww.currUIImpl.Data.BindID.mouse1, __cmd)
        
        def openSectionOnIdx(widget, imIdx):
            def __cmd(event = None, *args):
                # open orig material on page
                imLinkOMPageDict = fsf.Data.Sec.imLinkOMPageDict(subsection)
                bookName = sf.Wr.Manager.Book.getCurrBookName()
                currTopSection = fsf.Data.Book.currTopSection

                url = tff.Wr.TexFileUtils.getUrl(bookName, currTopSection, subsection, imIdx, "full", notLatex=True)
                
                os.system("open {0}".format(url))
                event.widget.configure(foreground="white")
            
            widget.bind(ww.currUIImpl.Data.BindID.mouse1, __cmd)
       
        def openContentOfTheSection(frame, label):
            def __cmd(event = None, *args):
                # open orig material on page

                links:dict = fsf.Data.Sec.imLinkDict(subsection)
                
                if not label.clicked:
                    i = 0

                    for k,v in links.items():
                        tempFrame = ttk.Frame(frame, name = "contentFr" + str(i))
                        
                        testEntryPage = ttk.Label(tempFrame, text = k + ": " + v, name = "contentP" + str(i))
                        testEntryFull = ttk.Label(tempFrame, text = "[full]", name = "contentFull" + str(i))
                        
                        testEntryPage.grid(row=0, column=0, sticky=tk.NW)
                        testEntryFull.grid(row=0, column=1, sticky=tk.NW)
                        
                        openOMOnThePageOfTheImage(testEntryPage, k)
                        bindChangeColorOnInAndOut(testEntryPage)
                        openSectionOnIdx(testEntryFull, k)
                        bindChangeColorOnInAndOut(testEntryFull)

                        tempFrame.grid(row=i + 2, column=2, sticky=tk.NW)
                        i += 1
                    
                    label.clicked = True
                else:
                    for child in frame.winfo_children():
                        if "content" in str(child):
                            child.destroy()
                    label.clicked = False

                event.widget.configure(foreground="white")
            
            label.bind(ww.currUIImpl.Data.BindID.mouse1, __cmd)
        
        prefix = ""
        if level != 0:
            prefix = "|" + int(level) * 4 * "-" + " "

        currBokkpath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        sectionFilepath = _upan.Paths.Section.JSON.getAbs(currBokkpath, subsection)
        
        subsectionText = ""

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(sectionFilepath):
            subsectionText = fsf.Data.Sec.text(subsection)
        
        if level == 0:
            subsectionText = fsf.Data.Book.sections[subsection]["name"]
       
        prettySubsections = prefix + subsection + ": " + subsectionText + "\n"
        
        locFrame = ttk.Frame(self.scrollable_frame)
        super().addTOCEntry(locFrame, idx, 0)

        subsectionLabel = ttk.Label(locFrame, text = prettySubsections)
        openPdfOnStartOfTheSection(subsectionLabel)
        bindChangeColorOnInAndOut(subsectionLabel)

        subsectionLabel.grid(row = 0, column= 0, sticky=tk.NW)

        if level != 0:
            openContentLabel = LabelWithClick(locFrame, text = "[content]")
            openContentOfTheSection(locFrame, openContentLabel)
            bindChangeColorOnInAndOut(openContentLabel)

            openContentLabel.grid(row = 0, column= 1, sticky=tk.NW)
        

    def populateTOC(self):
        text_curr = fsf.Wr.BookInfoStructure.getSubsectionsAsTOC()
        
        for i in range(len(text_curr)):
            self.addTOCEntry(text_curr[i][0], text_curr[i][1], i)

    def render(self, widjetObj=None, renderData=..., **kwargs):
        for child in self.scrollable_frame.winfo_children():
            child.destroy()
        
        self.populateTOC()

        return super().render(widjetObj, renderData, **kwargs)


class TOCRoot(ww.currUIImpl.RootWidget):
    pass