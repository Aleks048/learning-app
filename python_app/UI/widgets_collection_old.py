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

def getLabel(mainWinRoot, text):
    return tk.Label(mainWinRoot, text = text)


def getCheckboxes_TOC(mainWinRoot, namePrefix = ""):
    wv.UItkVariables.createTOCVar.set(True)
    
    createTOC_CB = tk.Checkbutton(mainWinRoot, 
                                name = namePrefix.lower() + "_create_toc", 
                                text = "TOC cr",
                                variable = wv.UItkVariables.createTOCVar, 
                                onvalue = 1, 
                                offvalue = 0)
    
    TOCWithImage_CB = tk.Checkbutton(mainWinRoot, 
                                    name = namePrefix.lower() + "_toc_w_image",  
                                    text = "TOC w i",
                                    variable = wv.UItkVariables.TOCWithImageVar, 
                                    onvalue = 1, 
                                    offvalue = 0)
    
    return createTOC_CB, TOCWithImage_CB




def getGlobalLinksAdd_Widgets(mainWinRoot, prefixName = ""):
    def addLinkToTexFile(imIDX, linkName, contenfFilepath, 
                        bookName, topSection, subsection):
        #
        # add link to the current section file
        #
        # read content file
        log.autolog("Updating file: " + contenfFilepath)
        lines = _u.readFile(contenfFilepath)
        positionToAdd = 0
        while positionToAdd < len(lines):
            line = lines[positionToAdd]
            # find the line with id
            if "id: " + imIDX in line:
                # find the line with global links start
                while "\myGlLinks{" not in line:
                    positionToAdd +=1
                    line = lines[positionToAdd]
                # find the line with global links end
                while "myGlLink" in line:
                    positionToAdd += 1   
                    line = lines[positionToAdd]
                break
            positionToAdd += 1
        
        url = "KIK:/" + bookName + "." + topSection + "." + subsection + "." + imIDX
        lineToAdd = "        \href{" + url + "}{" + linkName + "}\n"
        outlines = lines[:positionToAdd]
        outlines.append(lineToAdd)
        outlines.extend(lines[positionToAdd:])
        
        with open(contenfFilepath, "+w") as f:
            for line in outlines:
                f.write(line + "\n")


    def addGlLinkCallback():
        bookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
        bookName = _u.Settings.readProperty(_u.Settings.PubProp.currBookName_ID)
        secPrefix = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_prefix_ID)
        
        sourceSectionPath = fsm.Wr.SectionCurrent.getSectionNameNoPrefix()
        sourceSectionNameWprefix = fsm.Wr.SectionCurrent.getSectionNameWprefix()
        sourceLinkName = wv.UItkVariables.glLinkSourceImLink.get()
        sourceIDX = fsm.Wr.Links.LinkDict.get(sourceSectionPath)[sourceLinkName]
        sourceSectionFilepath = fsm.Wr.Paths.Section.getAbs(bookPath, sourceSectionPath)
        sourceContentFilepath = fsm.Wr.Paths.TexFiles.Content.getAbs(bookPath, sourceSectionNameWprefix)
        sourceMainFilepath = fsm.Wr.Paths.TexFiles.Main.getAbs(bookPath, sourceSectionNameWprefix)
        # sourceTOCFilepath = fsm.Wr.Paths.TexFiles.TOC.getAbs(bookPath, sourceSectionNameWprefix)
        sourcePDFFilepath = fsm.Wr.Paths.PDF.getAbs(bookPath, sourceSectionNameWprefix)
        sourcePDFFilename = sourcePDFFilepath.split("/")[-1]
        
        targetSectionPath = wv.UItkVariables.glLinktargetSections.get()
        targetSectionNameWprefix = secPrefix + "_" + targetSectionPath
        targetLinkName = wv.UItkVariables.glLinkTargetImLink.get()
        targetIDX = fsm.Wr.Links.LinkDict.get(targetSectionPath)[targetLinkName]
        targetSectionFilepath = fsm.Wr.Paths.Section.getAbs(bookPath, targetSectionPath)
        targetContentFilepath = fsm.Wr.Paths.TexFiles.Content.getAbs(bookPath, targetSectionNameWprefix)
        targetMainFilepath = fsm.Wr.Paths.TexFiles.Main.getAbs(bookPath, targetSectionNameWprefix)
        # targetTOCFilepath = fsm.Wr.Paths.TexFiles.TOC.getAbs(bookPath, targetSectionNameWprefix)
        targetPDFFilepath = fsm.Wr.Paths.PDF.getAbs(bookPath, targetSectionNameWprefix)
        targetPDFFilename = targetPDFFilepath.split("/")[-1]

        #
        # check that the section exists
        #

        sectionInfo = fsm.Wr.BookInfoStructure.readProperty(targetSectionPath)
        if sectionInfo == None:
            msg = "The path: '" + targetSectionPath + "' does not exist"
            log.autolog(msg)
            wmes.MessageMenu.createMenu(msg)
            return
        
        topSection = targetSectionPath.split(".")[0]
        subsection = ".".join(targetSectionPath.split(".")[1:])
        addLinkToTexFile(sourceIDX,
                        targetSectionPath + "\_" + targetLinkName,
                        sourceContentFilepath,
                        bookName,
                        topSection,
                        subsection)

        # add return link 
        
        sourceTopSection = sourceSectionPath.split(".")[0]
        sourceSubection = ".".join(sourceSectionPath.split(".")[1:])
        addLinkToTexFile(targetIDX, 
                        sourceSectionPath + "\_" + sourceLinkName,
                        targetContentFilepath,
                        bookName,
                        sourceTopSection,
                        sourceSubection)

        #
        # rebuild the pdfs
        #
        tff.Wr.TexFile.buildSubsectionPdf(sourceSectionFilepath,
                                        sourceMainFilepath,
                                        sourceSectionNameWprefix)
        tff.Wr.TexFile.buildSubsectionPdf(targetSectionFilepath,
                                        targetMainFilepath,
                                        targetSectionNameWprefix)

    createGlLinkBTN = tk.Button(mainWinRoot, text = "Create gl link", 
                        name = prefixName.lower() + "_addGlobalLink" + "BTN",
                        command = lambda: addGlLinkCallback())

    createGlLinkETR = tk.Entry(mainWinRoot,
                            width = 5,
                            textvariable = wv.UItkVariables.glLinktargetSections,
                            name = prefixName.lower() + "_addGlobalLink" + wu.Data.ENT.entryWidget_ID)
    
    return createGlLinkBTN, createGlLinkETR

# update the image links om
def updateImLinksOM(winMainRoot, secPath):
    if secPath != "":
        currChImageLinks = fsm.Wr.Links.LinkDict.getCurrImLinksSorted(secPath)
        wu.updateOptionMenuOptionsList(winMainRoot, 
                                    "target_SecImIDX", 
                                    currChImageLinks,
                                    wv.UItkVariables.glLinkTargetImLink,
                                    lambda *argv: None)
        wv.UItkVariables.glLinkTargetImLink.set(currChImageLinks[-1])

def getGlLinkSectionAndSubsection_OM(mainWinRoot, namePrefix = ""):
    '''
    functions that retrun options menus for choosing chapter
    '''

    def _subsectionChoosingCallback(mainWinRoot):
        sectiopPath =  wv.UItkVariables.glLinktargetSubSection.get()
        wv.UItkVariables.glLinktargetSections.set(sectiopPath)
        updateImLinksOM(mainWinRoot, wv.UItkVariables.glLinktargetSections.get())


    def _topSectionChoosingCallback(mainWinRoot):
        topSec = wv.UItkVariables.glLinktargetSections.get()
        subsectionsList = fsm.getSubsectionsList(topSec)
        subsectionsList.sort()

        # subsection option menu widget
        wu.updateOptionMenuOptionsList(mainWinRoot, 
                                        "_GlLink_chooseSubsecion_optionMenu", 
                                        subsectionsList, 
                                        wv.UItkVariables.glLinktargetSubSection,
                                        _subsectionChoosingCallback) 


    wv.UItkVariables.topSection.set(
        fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currTopSection_ID)
    )

    topSectionsList = fsm.getTopSectionsList()
    topSectionsList.sort(key = int)
    subsectionsList = fsm.getSubsectionsList(topSectionsList[0])

    frameTop = tk.Frame(mainWinRoot, 
                    name = namePrefix.lower() + "_GlLink_chooseSection_optionMenu", 
                    background = "Blue")
    
    wv.UItkVariables.glLinktargetTopSection = tk.StringVar()
    wv.UItkVariables.glLinktargetTopSection.set(topSectionsList[0])
    topSection_menu = tk.OptionMenu(frameTop, 
                                    wv.UItkVariables.glLinktargetTopSection , 
                                    *topSectionsList, 
                                    command= lambda x: _topSectionChoosingCallback(mainWinRoot))
    topSection_menu.grid(row = 0, column = 0)
    

    frameSub = tk.Frame(mainWinRoot, 
                    name = namePrefix.lower() + "_GlLink_chooseSubsection_optionMenu", 
                    background = "Blue")

    wv.UItkVariables.glLinktargetSubSection = tk.StringVar()
    wv.UItkVariables.glLinktargetSubSection.set(subsectionsList[0])
    subection_menu = tk.OptionMenu(frameSub, 
                                    wv.UItkVariables.glLinktargetSubSection , 
                                    *subsectionsList, 
                                    command= lambda x: _subsectionChoosingCallback(mainWinRoot))
    subection_menu.grid(row = 0, column = 0)

    return frameTop, frameSub


def getTargetImageLinks_OM(mainWinRoot, prefixName = "", secPath = ""):
    frame = tk.Frame(mainWinRoot, name = prefixName + "_target_SecImIDX" + "_OM")
    if secPath != "":
        currChImageLinks = fsm.Wr.Links.LinkDict.getCurrImLinksSorted(secPath)
        wv.UItkVariables.glLinkTargetImLink.set(currChImageLinks[-1])
    else:
        currChImageLinks = _u.Token.NotDef.list_t
        wv.UItkVariables.glLinkTargetImLink.set(_u.Token.NotDef.str_t)
    
    imIDX_OM = tk.OptionMenu(frame,
                    wv.UItkVariables.glLinkTargetImLink,
                    *currChImageLinks)
    imIDX_OM.grid(row=0, column=0)
    
    return frame

def getSourceImageLinks_OM(mainWinRoot, prefixName = "", secPath = ""):
    frame = tk.Frame(mainWinRoot, name = prefixName + "_source_SecImIDX" + "_OM")
    if secPath != "":
        currChImageLinks = fsm.Wr.Links.LinkDict.getCurrImLinksSorted(secPath)
        wv.UItkVariables.glLinkSourceImLink.set(currChImageLinks[-1])
    else:
        currChImageLinks = _u.Token.NotDef.list_t
        wv.UItkVariables.glLinkSourceImLink.set(_u.Token.NotDef.str_t)
    
    imIDX_OM = tk.OptionMenu(frame,
                    wv.UItkVariables.glLinkSourceImLink,
                    *currChImageLinks
                    )
    imIDX_OM.grid(row=0, column=0)
    
    return frame

def getChangeSubsectionToTheFront(mainWinRoot, prefixName = ""):
    '''
    Change subsection by grabbing the name and top name from the front skim document
    '''
    def callback():
        # get the name of the front skim document
        cmd = oscr.get_NameOfFrontSkimDoc_CMD()
        frontSkimDocumentName = str(subprocess.check_output(cmd, shell=True))
        
        # get subsection and top section from it
        frontSkimDocumentName = frontSkimDocumentName.replace("\\n", "")
        frontSkimDocumentName = frontSkimDocumentName.split("_")[1]
        topSection = frontSkimDocumentName.split(".")[0]
        subsection = frontSkimDocumentName
        
        cmd = oscr.get_NameOfFrontSkimDoc_CMD()
        imIDX = int(str(subprocess.check_output(cmd, shell=True)).split(" ")[1])

        # close current section vscode
        _, windowID, _ = _u.getOwnersName_windowID_ofApp(
                            "vscode",
                             fsm.Wr.SectionCurrent.readCurrSection())
        
        if (windowID != None):
            cmd = oscr.closeVscodeWindow(dt.OtherAppsInfo.VsCode.section_pid, subsection)
            subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()

        #change the current subsection for the app
        fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.currTopSection_ID, topSection)
        fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.currSection_ID, subsection)
        
        mon_width, _ = _u.getMonitorSize()
        width = int(mon_width / 2)
        height = 70
        wu.showCurrentLayout(mainWinRoot, 
                            width, 
                            height)
        # lm.Wr.SectionLayout.set(mainWinRoot, width, height)
        currChImageLinks = fsm.Wr.Links.LinkDict.getCurrImLinksSorted(subsection)
        wu.updateOptionMenuOptionsList(mainWinRoot, 
                                    "source_SecImIDX", 
                                    currChImageLinks,
                                    wv.UItkVariables.glLinkSourceImLink,
                                    lambda *argv: None)
        wv.UItkVariables.glLinkSourceImLink.set(currChImageLinks[-1])

    return tk.Button(mainWinRoot, 
                    name = prefixName + "_changeSubsection",
                    text = "change subsecttion",
                    command = lambda: callback())


def getRebuildCurrentSubsec_BTN(mainWinRoot, prefixName = ""):
    def rebuildBtnCallback():
        tff.Wr.TexFile.buildCurrentSubsectionPdf()
        
    return tk.Button(mainWinRoot, 
                    name = prefixName.lower() + "_rebuildCurrSubsec",
                    text = "rebuild", 
                    fg = 'black', bg = 'red' ,
                    command = lambda: rebuildBtnCallback())


class LayoutsMenus:
    class SectionLayoutUI:
        pyAppDimensions = [None, None]
        classPrefix = "sectionlayout"

        @classmethod
        def addWidgets(cls, winMainRoot):

            dummyEntry = tk.Entry(winMainRoot, text = "Dummy", name = cls.classPrefix + "_dummyFocusEntry")
            dummyEntry.grid(column=2, row=0, padx=0, pady=0)
            dummyEntry.focus_set()

            getGlLinkSectionAndSubsection_OM(winMainRoot, cls.classPrefix)

            createGlLinkBTN, createGlLinkETR = getGlobalLinksAdd_Widgets(winMainRoot, cls.classPrefix)
            createGlLinkETR.grid(column=4, row=0, padx=0, pady=0)
            createGlLinkBTN.grid(column=5, row=0, padx=0, pady=0)
            
            createGlLinkETR.bind('<Return>',
                                lambda e: updateImLinksOM(winMainRoot, wv.UItkVariables.glLinktargetSections.get()))
            
            targetImageLinksOM = getTargetImageLinks_OM(winMainRoot, cls.classPrefix)
            targetImageLinksOM.grid(column=5, row=2, padx=0, pady=0)

            currSection = fsm.Wr.SectionCurrent.readCurrSection()
            sourceImageLinksOM = getSourceImageLinks_OM(winMainRoot, cls.classPrefix, currSection)
            sourceImageLinksOM.grid(column=4, row=2, padx=0, pady=0)

            changeSection_BTN = getChangeSubsectionToTheFront(winMainRoot, cls.classPrefix)
            changeSection_BTN.grid(column=0, row=2, padx=0, pady=0)


            rebuildCurrSec_BTN = getRebuildCurrentSubsec_BTN(winMainRoot, cls.classPrefix)
            rebuildCurrSec_BTN.grid(row = 2, column = 1)

            targetTopSectionOM, targetSubsectionOM = getGlLinkSectionAndSubsection_OM(winMainRoot, cls.classPrefix)
            targetTopSectionOM.grid(row = 2, column = 2)
            targetSubsectionOM.grid(row = 2, column = 3)

            mon_width, _ = _u.getMonitorSize()
            cls.pyAppDimensions[0] = int(mon_width / 2)
            cls.pyAppDimensions[1] = 70
    
    class MainLayoutUI:
        pyAppDimensions = [None, None]
        classPrefix = "mainlayout"

        @classmethod
        def addWidgets(cls, winMainRoot):            
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


class ChooseMaterial:

    def getOptionsMenu_ChooseBook(mainWinRoot, namePrefix = ""):
        def bookMenuChooseCallback(bookNameStVar):
            bookName = bookNameStVar.get()
            bookPaths = _u.Settings.readProperty(_u.Settings.PubProp.booksPaths_ID)
            bookPath = bookPaths[bookName]
            _u.Settings.Book.setCurrentBook(bookName, bookPath)

            # set UI variables
            wv.UItkVariables.topSection.set(
                fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currTopSection_ID)
            )
            wv.UItkVariables.subsection.set(
                fsm.Wr.SectionCurrent.readCurrSection()
            )
            wv.UItkVariables.imageGenerationEntryText.set(
                fsm.Wr.Links.ImIDX.get(wv.UItkVariables.subsection.get())
            )

        default_book_name="Select a a book"

        '''
        functions that retrun options menus for choosing book
        '''
        book_name = tk.StringVar()
        book_name.set(default_book_name)

        # Create the list of books we have
        listOfBooksNames = _u.getListOfBooks()

        frame = tk.Frame(mainWinRoot, 
                        name = namePrefix.lower() + "_chooseBook_optionMenu",
                        background="Blue")
        book_menu = tk.OptionMenu(frame, 
                                book_name, 
                                *listOfBooksNames, 
                                command= lambda x: bookMenuChooseCallback(book_name))
        book_menu.grid(row=0, column = 0)
        
        return frame
   

'''
chapters menu widgets
'''
class SectionsUI:
    sectionsPrefix = "sections_"

    class WidgetNames:
        class Top:
            Section = "setCurrTopSection_"
            Name = "setTopSectionName_"
            StPage = "setTopSectionStartPage_"
        class Sub:
            Subsection = "setCurrSubsection_"
            Name = "setSubsectionName_"
            StPage = "setSubsectionStartPage_"


    @classmethod
    def setSectionsUI(cls, mainWinRoot):
        chooseSectionMenus_Btn = cls.getButton_chooseSectionsMenusAndBack(mainWinRoot, 
                                                                        cls.sectionsPrefix)
        chooseSectionMenus_Btn.grid(row = 1, column = 2)
        entry_setSectionName, button_setSectionName = cls.getWidgets_setSectionName(mainWinRoot,  
                                                                                    cls.sectionsPrefix)
        entry_setSectionName.grid(row = 0, column = 0)
        button_setSectionName.grid(row = 0, column = 1)
        entry_setSectionStartPage, button_setSectionStartPage = \
            cls.getWidgets_setSectionStartPage(mainWinRoot,  cls.sectionsPrefix)
        entry_setSectionStartPage.grid(row = 1, column = 0)
        button_setSectionStartPage.grid(row = 1, column = 1)

        sectionPath_ETR = cls.getEntrie_setNewSectionPath(mainWinRoot, cls.sectionsPrefix)
        sectionPath_ETR.grid(row = 0, column = 2, sticky = tk.N)     
        addSec_BTN = cls.getButton_createNewSection(mainWinRoot, cls.sectionsPrefix)
        removeSec_BTN = cls.getButton_removeTopSection(mainWinRoot, cls.sectionsPrefix)
        addSec_BTN.grid(row = 0, column = 2,sticky = tk.W)
        removeSec_BTN.grid(row = 0, column = 2,sticky = tk.E)


    @classmethod
    def getEntrie_setNewSectionPath(cls, mainWinRoot, prefixName = ""):
        sectionPath_ETR = tk.Entry(mainWinRoot, 
                            width = 5,
                            textvariable = wv.UItkVariables.currCh, 
                            name = prefixName.lower() 
                                    + cls.WidgetNames.Top.Section 
                                    + wu.Data.ENT.entryWidget_ID)
        
        return sectionPath_ETR


    @classmethod
    def getWidgets_setSectionName(cls, mainWinRoot, prefixName = ""):
        def setTopSectionNameCallback():
            currTopSection = \
                fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currTopSection_ID)
            
            fsm.Wr.SectionInfoStructure.updateProperty(currTopSection, 
                                                    fsm.PropIDs.Sec.name_ID, 
                                                    entry_setChapterName.get())
        
        entry_setChapterName = tk.Entry(mainWinRoot, 
                            name = prefixName.lower() 
                                +  cls.WidgetNames.Top.Name
                                + wu.Data.ENT.entryWidget_ID
                            )
        button_setChapterName = tk.Button(mainWinRoot, 
                            name = prefixName.lower() +  cls.WidgetNames.Top.Name + "BTN", 
                            text="setTopSectionName", 
                            command = lambda: setTopSectionNameCallback())
        
        return entry_setChapterName, button_setChapterName            


    @classmethod
    def getWidgets_setSectionStartPage(cls, mainWinRoot, prefixName = ""):
        def setTopSectionStartPageCallback():
            currTopSection = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currTopSection_ID)
            fsm.Wr.SectionInfoStructure.updateProperty(currTopSection, 
                                                    fsm.PropIDs.Sec.startPage_ID, 
                                                    entry_setTopSectionStartPage.get()
                                                    )

        entry_setTopSectionStartPage = tk.Entry(mainWinRoot, 
                                            name = prefixName.lower() 
                                                + cls.WidgetNames.Top.StPage
                                                + wu.Data.ENT.entryWidget_ID
                                            )
        button_setTopSectionStartPage = tk.Button(mainWinRoot, 
                        name = prefixName.lower() + cls.WidgetNames.Top.StPage + "BTN", 
                        text="setTopSectionStartPage", 
                        command = lambda: setTopSectionStartPageCallback())
        
        return entry_setTopSectionStartPage, button_setTopSectionStartPage

    @classmethod
    def getButton_createNewSection(cls, mainWinRoot, prefixName = ""):
        def createNewBTNcallback():
            secPath = None
            secName = None
            secStartPage = None
            
            for e in mainWinRoot.winfo_children():
                if  cls.WidgetNames.Top.Section + wu.Data.ENT.entryWidget_ID in e._name:
                    secPath = e.get()
                elif cls.WidgetNames.Top.Name + wu.Data.ENT.entryWidget_ID in e._name:
                    secName = e.get()
                elif cls.WidgetNames.Top.StPage + wu.Data.ENT.entryWidget_ID in e._name:
                    secStartPage = e.get()
            
            # TODO: check that the structure exists and ask user if we should proceed
            fsm.addSectionForCurrBook(secPath)
            separator = \
                fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_path_separator_ID)
            topSectionName = secPath.split(separator)[0]
            fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.currTopSection_ID, topSectionName)
            fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.currSection_ID, secPath)
            sections = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_ID)
            sections[topSectionName]["prevSubsectionPath"] = secPath
            fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.sections_ID, sections)

            fsm.Wr.SectionInfoStructure.updateProperty(secPath, 
                                                    fsm.PropIDs.Sec.name_ID,
                                                    secName)            
            fsm.Wr.SectionInfoStructure.updateProperty(secPath, 
                                                    fsm.PropIDs.Sec.startPage_ID, 
                                                    secStartPage)

            #
            # update ui
            #
            topSections = \
                list(fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_ID).keys())
            subsections = wu.getSubsectionsListForCurrTopSection()
            wu.updateOptionMenuOptionsList(mainWinRoot, 
                                        "_chooseSection_optionMenu",
                                        topSections, 
                                        wv.UItkVariables.topSection,
                                        ChooseMaterial._topSectionChoosingCallback
                                        ) 
            wv.UItkVariables.topSection.set(topSectionName)
            
            wu.updateOptionMenuOptionsList(mainWinRoot, 
                                        "_chooseSubsecion_optionMenu",
                                        subsections,
                                        wv.UItkVariables.subsection,
                                        ChooseMaterial._subsectionChoosingCallback
                                        ) 
            wv.UItkVariables.subsection.set(secPath)

            wv.UItkVariables.imageGenerationEntryText.set("1")

            # update screenshot widget
            wu.Screenshot.setValueScreenshotLoaction()
        
        return tk.Button(mainWinRoot, 
                        name = prefixName.lower() + "_createNewTopSection_" + "BTN", 
                        text="New", 
                        command = lambda: createNewBTNcallback())
    

    @classmethod
    def getButton_removeTopSection(cls, mainWinRoot, prefixName = ""):
        # TODO: the remove functionality is not yet implemented
        def removeBTNcallback():
            pass
            # chNum = None
            # for e in mainWinRoot.winfo_children():
            #     if  "_setCurrChapter_" + wu.Data.ENT.entryWidget_ID in e._name:
            #         chNum = e.get()
            #         break
            # _u.BookSettings.ChapterProperties.removeChapter(chNum)
        
        return tk.Button(mainWinRoot, 
                        name = prefixName.lower() + "_removeTopSectionBTN", 
                        text="Del", 
                        command = lambda: removeBTNcallback())

