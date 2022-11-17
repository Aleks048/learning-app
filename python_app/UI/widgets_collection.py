import os
import tkinter as tk
from tkinter import messagebox
from threading import Thread

import UI.widgets_vars as wv 
import UI.widgets_utils as wu
import UI.widgets_messages as wmes

import layouts.layouts_manager as lm

import file_system.file_system_manager as fsm
import tex_file.tex_file_manager as t

import _utils.logging as log
import _utils._utils_main as _u

def getLabel(mainWinRoot, text):
    return tk.Label(mainWinRoot, text = text)


def getCheckboxes_TOC(mainWinRoot, namePrefix = ""):
    wv.UItkVariables.createTOCVar.set(True)
    
    createTOC_CB = tk.Checkbutton(mainWinRoot, name = namePrefix.lower() + "_create_toc", text = "TOC cr",
                                variable = wv.UItkVariables.createTOCVar, onvalue = 1, offvalue = 0)
    
    TOCWithImage_CB = tk.Checkbutton(mainWinRoot, name = namePrefix.lower() + "_toc_w_image",  text = "TOC w i",
                                variable = wv.UItkVariables.TOCWithImageVar, onvalue = 1, offvalue = 0)
    
    return createTOC_CB, TOCWithImage_CB


def getImageGenerationRestart_BTN(mainWinRoot, namePrefix = ""):
    def restartBTNcallback():
        wv.UItkVariables.buttonText.set("imNum")
        sectionImIndex = fsm.Wr.SectionInfoStructure.readProperty(fsm.PropIDs.Sec.imIndex_ID)
        wv.UItkVariables.imageGenerationEntryText.set(sectionImIndex)
    

    restart_BTN = tk.Button(mainWinRoot,
                            name = namePrefix.lower() + "_imageGenerationRestartBTN",
                            text= "restart", 
                            command = restartBTNcallback)
    
    return restart_BTN


def getShowProofs_BTN(mainWinRoot, prefixName = ""):
    showProofsVar = tk.StringVar()
    showProofsVar.set("Hide Proofs")
    def _changeProofsVisibility(hideProofs):
        with open(t.Wr.TexFile._getCurrContentFilepath(),"r") as conF:
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
                        else:
                            contentLines[i] = "% " + line
                break
        with open(t.Wr.TexFile._getCurrContentFilepath(),"w") as conF:
            _waitDummy = conF.writelines(contentLines)
    
    def getShowProofsCallBack():
        if showProofsVar.get() == "Show Proofs":
            showProofsVar.set("Hide Proofs")
            _changeProofsVisibility(True)
            Thread(target= t.Wr.TexFile.buildCurrentSubsectionPdf).start()
        elif showProofsVar.get() == "Hide Proofs":
            showProofsVar.set("Show Proofs")
            _changeProofsVisibility(False)
            Thread(target= t.Wr.TexFile.buildCurrentSubsectionPdf).start()
    
    return tk.Button(mainWinRoot, 
                    name = prefixName.lower() + "_showProofsBTN",
                    textvariable = showProofsVar,
                    command = getShowProofsCallBack)


def getAddImage_BTN(mainWinRoot, prefixName = ""):
    def addImBTNcallback():
        currentSubsection = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currSection_ID)
        currImID = fsm.Wr.SectionInfoStructure.readProperty(currentSubsection, fsm.PropIDs.Sec.imIndex_ID)
        
        # screenshot
        imName = ""

        # get name of the image from the text field
        for w in mainWinRoot.winfo_children():
            if "_imageGeneration_" + wu.Data.ENT.entryWidget_ID in w._name:
                imName = w.get()
        
        extraImagePath = _u.DIR.Screenshot.getCurrentAbs() \
                            + currImID + "_" + currentSubsection \
                            + "_" + imName
        
        if os.path.isfile(extraImagePath + ".png"):
            def takeScreencapture(savePath):
                os.system("screencapture -ix " + savePath)
                wv.UItkVariables.needRebuild.set(True)
            wmes.ConfirmationMenu.createMenu("The file exists. Overrite?", takeScreencapture, extraImagePath + ".png")
        else:
            os.system("screencapture -ix " + extraImagePath + ".png")
            wv.UItkVariables.needRebuild.set(True)

        # update the content file
        marker = "THIS IS CONTENT id: " + currImID
        with open(t.Wr.TexFile._getCurrContentFilepath(), "r+") as f:
            contentLines = f.readlines()
            lineNum = [i for i in range(len(contentLines)) if marker in contentLines[i]][0]
            extraImagesMarker = "% \\EXTRA IMAGES END"
            while extraImagesMarker not in contentLines[lineNum]:
                lineNum += 1
            outLines = contentLines[:lineNum]
            extraImageLine = "\
\\\\\myStIm{" + extraImagePath + "}\n"
            outLines.append(extraImageLine)
            outLines.extend(contentLines[lineNum:])

            f.seek(0)
            f.writelines(outLines)
        
        t.Wr.TexFile._populateMainFile()
    
    return tk.Button(mainWinRoot, 
                    name = prefixName.lower() + "_imageGenerationAddImBTN",
                    text= "addIm",
                    command = addImBTNcallback)


def getSaveImage_BTN(mainWinRoot, prefixName = ""):
    def saveImageCallBack():
        _waitDummy = os.system("osascript -e '\
        tell application \"Preview\" to save the front document\n\
        tell application \"System Events\" to tell process \"Preview\"\n\
            tell front window \n\
                click button 1\n\
            end tell\n\
        end tell\
        '")
        t.Wr.TexFile.buildCurrentSubsectionPdf()
    return tk.Button(mainWinRoot, 
                    name = prefixName.lower() + "_saveImgBTN",
                    text = "saveIM",
                    command = saveImageCallBack)


def getGlobalLinksAdd_Widgets(mainWinRoot, prefixName = ""):
    def addClLinkCallback():
        sections = targetSections.get()
        sectionsStringSeparator = " "
        sections = sections.split(sectionsStringSeparator)
        if len(sections) < 3:
            wmes.MessageMenu.createMenu("The sections and name should be in a '" + sectionsStringSeparator + "' separated string.")
        else:
            linkName = sections[-1]
            targetSection = sections[0]
            subsections = sections[1:-1]

            # get current file page
            currFilePage = _u.getpageOfcurrentDoc()
            #update the current file link

            # get target tex file position
            currBookPath = _u.Settings.Book.getCurrBookFolderPath()
            subsectionPath = os.path.join(currBookPath, sections[0], "subchapters", *subsections)
            with open(subsectionPath) as f:
                targetLines = f.readlines()

    
    createGlLinkBTN = tk.Button(mainWinRoot, text = "Create gl link", 
                        name = prefixName.lower() + "addGlobalLinkBTN",
                        command = addClLinkCallback)

    targetSections = tk.StringVar()
    createGlLinkETR = tk.Entry(mainWinRoot,
                            width = 5,
                            textvariable = targetSections,
                            name = prefixName.lower() + "addGlobalLink" + wu.Data.ENT.entryWidget_ID)
    
    return createGlLinkBTN, createGlLinkETR


def getTextEntryButton_imageGeneration(mainWinRoot, prefixName = ""):
    imageProcessingETR = tk.Entry(mainWinRoot, 
                                width = 8,
                                textvariable =  wv.UItkVariables.imageGenerationEntryText,
                                name=prefixName.lower() + "_imageGeneration_" + wu.Data.ENT.entryWidget_ID)

    secImIndex = _u.getCurrSecImIdx()
    wv.UItkVariables.imageGenerationEntryText.set(secImIndex)

    dataFromUser = [-1, -1, -1]

    def _storeInputDataAndChange(nextButtonName, f = lambda *args: None, i = 0):
        # NOTE: not sure what is going on but "dataFromUser" refused to clean 
        # so had to pass i to set the position explicitly and set it to [-1, -1, -1] before
        dataFromUser[i] = imageProcessingETR.get()
        f()
        wv.UItkVariables.buttonText.set(nextButtonName)


    def _createImageScript():
        scriptFile = ""
        scriptFile += "#!/bin/bash\n"
        scriptFile += "\
conIDX=`grep -n \"% THIS IS CONTENT id: " + dataFromUser[0] +"\" \"" + t.Wr.TexFile._getCurrContentFilepath() + "\" | cut -d: -f1`\n"
        scriptFile += "\
tocIDX=`grep -n \"% THIS IS CONTENT id: " + dataFromUser[0] +"\" \"" + t.Wr.TexFile._getCurrTOCFilepath() + "\" | cut -d: -f1`\n"
        scriptFile += "\
if [ \"$conIDX\" != \"\" ]\n\
then\n\
osascript -  $conIDX <<EOF\n\
    on run argv\n\
        tell application \"code\"\n\
            activate\n\
            tell application \"System Events\"\n\
                keystroke \"1\" using {command down}\n\
                delay 0.1\n\
                keystroke \"g\" using {control down}\n\
                keystroke item 1 of argv + 20\n\
                keystroke return\n\
            end tell\n\
        end tell\n\
    end run\n\
EOF\n\
fi\n"
        scriptFile += "\
if [ \"$tocIDX\" != \"\" ]\n\
then\n\
osascript - $tocIDX <<EOF\n\
    on run argv\n\
        tell application \"code\"\n\
            activate\n\
            tell application \"System Events\"\n\
                keystroke \"2\" using {command down}\n\
                delay 0.1\n\
                keystroke \"g\" using {control down}\n\
                keystroke item 1 of argv\n\
                keystroke return\n\
            end tell\n\
        end tell\n\
    end run\n\
EOF\n\
fi\n"
        pdfName = _u.getCurrentSectionPdfName()
        scriptFile += "osascript -e '\
tell application \"" + _u.Settings._appsIDs.skim_ID + "\"\n\
    tell document \"" + pdfName + "\"\n\
        delay 0.1\n\
        go to page " + str(dataFromUser[0]) + "\n\
        end tell\n\
end tell'"

        return scriptFile


    def _createTexForTheProcessedImage():
        currsubsection = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currSection_ID)

        extraImagePath = _u.DIR.Screenshot.getCurrentAbs() \
                            + dataFromUser[0] + "_" + currsubsection \
                            + "_" + dataFromUser[1]

        # ADD CONTENT ENTRY TO THE PROCESSED CHAPTER
        with open(t.Wr.TexFile._getCurrContentFilepath(), 'a') as f:
            add_page = "\n\n\
% THIS IS CONTENT id: " + dataFromUser[0] + " \n\
    % TEXT BEFORE MAIN IMAGE\n\
    \n\
    \n\
    % TEXT BEFORE MAIN IMAGE\n\
    \\def\\imnum{" + dataFromUser[0] + "}\n\
    \\def\\linkname{" + dataFromUser[1] + "}\n\
    \\hyperdef{TOC}{\\linkname}{}\n\
    \myTarget{" + extraImagePath + "}{\\linkname\\imnum}\n\
    % TEXT AFTER MAIN IMAGE\n\
    \n\
    \n\
    % TEXT AFTER MAIN IMAGE\n\
    % \EXTRA IMAGES START\n\
    % \EXTRA IMAGES END\n\
    % TEXT AFTER EXTRA IMAGES\n\
    \n\
    \n\
    % TEXT AFTER EXTRA IMAGES\n\
    \\\\\\rule{\\textwidth}{0.4pt}\n\
    \\\\\\myGlLinks{\n\
        % \\myGlLink{}{}\n\
    }\n\
    \\\\Local links: \n\
    \\TOC\\newpage\n"
                
            f.write(add_page)

        if wv.UItkVariables.createTOCVar.get():
            if wv.UItkVariables.TOCWithImageVar.get():
                # TOC ADD ENTRY WITH IMAGE
                with open(t.Wr.TexFile._getCurrTOCFilepath(), 'a') as f:
                    toc_add_image = "\
% THIS IS CONTENT id: " + dataFromUser[0] + " \n\
\\mybox{\n\
    \\link[" + dataFromUser[0] + \
    "]{" + dataFromUser[1] + "} \\image[0.5]{" + \
    dataFromUser[0] + "_" + currsubsection + "_" + dataFromUser[1] + "}\n\
}\n\n\n"
                    f.write(toc_add_image)
            else:  
                # TOC ADD ENTRY WITHOUT IMAGE
                with open(t.Wr.TexFile._getCurrTOCFilepath(), 'a') as f:
                    toc_add_text = "\
% THIS IS CONTENT id: " + dataFromUser[0] + " \n\
\\mybox{\n\
    \\link[" + dataFromUser[0] + "]{" + dataFromUser[1] + "} \\textbf{!}\n\
}\n\n\n"
                    f.write(toc_add_text)
            

        #create a script to run on page change
        imageAnscriptPath = _u.DIR.Screenshot.getCurrentAbs() + dataFromUser[0] + \
                            "_" + currsubsection + "_" + dataFromUser[1]

        # STOTE IMNUM, IMNAME AND LINK
        fsm.Wr.SectionInfoStructure.updateProperty(currsubsection, fsm.PropIDs.Sec.imIndex_ID, dataFromUser[0])
        fsm.Wr.SectionInfoStructure.updateProperty(currsubsection, fsm.PropIDs.Sec.imLinkName_ID, dataFromUser[1])
        
        # POPULATE THE MAIN FILE
        t.Wr.TexFile._populateMainFile()
        
        
        # take a screenshot
        if os.path.isfile(imageAnscriptPath + ".png"):
            def takeScreencapture(savePath):
                os.system("screencapture -ix " + savePath + ".png")
                wv.UItkVariables.needRebuild.set(True)
                    #create a sript associated with image
                with open(savePath + ".sh", "w+") as f:
                    for l in _createImageScript():
                        f.write(l)
                os.system("chmod +x " + savePath + ".sh")
                #update curr image index for the chapter
                nextImNum = str(int(dataFromUser[0]) + 1)
                fsm.Wr.SectionInfoStructure.updateProperty(
                        currsubsection, 
                        fsm.PropIDs.Sec.imIndex_ID,
                        nextImNum)
                wv.UItkVariables.imageGenerationEntryText.set(nextImNum)
                wv.UItkVariables.buttonText.set("imNum")
            
            wmes.ConfirmationMenu.createMenu("The file exists. Overrite?", takeScreencapture, imageAnscriptPath)
        else:
            os.system("screencapture -ix " + imageAnscriptPath + ".png")
            wv.UItkVariables.needRebuild.set(True)
            #create a sript associated with image
            with open(imageAnscriptPath + ".sh", "w+") as f:
                for l in _createImageScript():
                    f.write(l)
            os.system("chmod +x " + imageAnscriptPath + ".sh")
            #update curr image index for the chapter
            nextImNum = str(int(dataFromUser[0]) + 1)
            fsm.Wr.SectionInfoStructure.updateProperty(
                        currsubsection, 
                        fsm.PropIDs.Sec.imIndex_ID,
                        nextImNum)
            wv.UItkVariables.imageGenerationEntryText.set(nextImNum)

    buttonNamesToFunc = {"imNum": lambda *args: wv.UItkVariables.imageGenerationEntryText.set(""),
                        "imLink":_createTexForTheProcessedImage}
    buttonNames = list(buttonNamesToFunc.keys())
    
    wv.UItkVariables.buttonText.set(buttonNames[0])

    def buttonCallback():
        for i in range(len(buttonNames)):
            if buttonNames[i] == wv.UItkVariables.buttonText.get():
                _storeInputDataAndChange(buttonNames[(i+1)%len(buttonNames)], 
                                        buttonNamesToFunc[buttonNames[i]], i)
                break

    processButton = tk.Button(mainWinRoot, 
                            name = prefixName.lower() + "_imageGeneration_processButton",
                            textvariable = wv.UItkVariables.buttonText, 
                            command= buttonCallback)
    
    return [imageProcessingETR, processButton]


class StartupMenu:
    def getStartup_BTN(winRoot, callback):
        return tk.Button(winRoot,
                        name = "_startupConfirmBTN",
                        text= "start", 
                        command = callback)

    def getBookChoosing_OM(winRoot, callback):
        default_book_name="Select a a book"

        '''
        functions that retrun options menus for choosing book
        '''
        wv.StartupUItkVariables.bookChoice.set(default_book_name)

        # Create the list of books we have
        listOfBooksNames = _u.getListOfBooks()

        frame = tk.Frame(winRoot, name = "chooseBook_optionMenu", background="Blue")
        book_menu = tk.OptionMenu(frame, 
                                wv.StartupUItkVariables.bookChoice, 
                                *listOfBooksNames, 
                                command= lambda x: callback)
        book_menu.grid(row=0, column = 0)
        return frame
    
    def getTextEntry_ETR(winRoot, entryNname, dataVar, defaultText):
        dataVar.set(defaultText)
        entry = tk.Entry(winRoot, 
                        width = 50,
                        textvariable = dataVar, 
                        fg = wu.Data.ENT.defaultTextColor,
                        name = entryNname + wu.Data.ENT.entryWidget_ID)

        entry.bind("<FocusIn>",  
                        lambda *args: wu.addDefaultTextToETR(entry, dataVar, defaultText))
        entry.bind("<FocusOut>", 
                            lambda *args: wu.addDefaultTextToETR(entry, dataVar, defaultText))
        return entry

    def addNewBook_BTN(winRoot, callback):
        return tk.Button(winRoot,
                        name = "_addBookBTN",
                        text= "addBook", 
                        command = callback)


class LayoutsMenus:
    

    class SectionLayoutUI:
        pyAppDimensions = [None, None]
        classPrefix = "sectionlayout"

        @classmethod
        def addWidgets(cls, winMainRoot):
            layoutOM = LayoutsMenus._commonWidgets.getOptionsMenu_Layouts(winMainRoot, cls.classPrefix)
            layoutOM.grid(column=0, row=0, padx=0, pady=0)
            layoutOM.update()
            
            showProofsBTN = getShowProofs_BTN(winMainRoot, cls.classPrefix)
            showProofsBTN.grid(column=1, row=0, padx=0, pady=0)

            dummyEntry = tk.Entry(winMainRoot, text = "Dummy", name = cls.classPrefix + "_dummyFocusEntry")
            dummyEntry.grid(column=2, row=0, padx=0, pady=0)
            dummyEntry.focus_set()

            saveImageBTN = getSaveImage_BTN(winMainRoot, cls.classPrefix)
            saveImageBTN.grid(column=3, row=0, padx=0, pady=0)

            createGlLinkBTN, createGlLinkETR = getGlobalLinksAdd_Widgets(winMainRoot, cls.classPrefix)
            createGlLinkETR.grid(column=4, row=0, padx=0, pady=0)
            createGlLinkBTN.grid(column=5, row=0, padx=0, pady=0)


            mon_width, _ = _u.getMonitorSize()
            cls.pyAppDimensions[0] = int(mon_width / 2)
            cls.pyAppDimensions[1] = layoutOM.winfo_height() + 5
    
    class MainLayoutUI:
        pyAppDimensions = [None, None]
        classPrefix = "mainlayout"

        @classmethod
        def addWidgets(cls, winMainRoot):            
            mon_width, _ = _u.getMonitorSize()
            cls.pyAppDimensions = [int(mon_width / 2), 90]

            #
            # layout: 
            #
            layoutOM = LayoutsMenus._commonWidgets.getOptionsMenu_Layouts(winMainRoot, cls.classPrefix)
            layoutOM.grid(column = 1, row = 0, padx = 0, pady = 0)

            #
            # image generation:
            #
            imageGenerationUI = getTextEntryButton_imageGeneration(winMainRoot, cls.classPrefix)
            imageGenerationUI[0].grid(column = 2, row = 0, padx = 0, pady = 0, sticky = tk.N)
            imageGenerationUI[1].grid(column = 2, row = 1, padx = 0, pady = 0, sticky = tk.N)

            addExtraImage = getAddImage_BTN(winMainRoot, cls.classPrefix)
            addExtraImage.grid(column = 3, row = 1, padx = 0, pady = 0, sticky = tk.E)

            imageGenerationRestartBTN = getImageGenerationRestart_BTN(winMainRoot, cls.classPrefix)
            imageGenerationRestartBTN.grid(column = 3, row = 1, padx = 0, pady = 0, sticky = tk.W)

            TOCcreate_CB, TOCWithImage_CB = getCheckboxes_TOC(winMainRoot, cls.classPrefix)
            TOCcreate_CB.grid(column = 1, row = 1, padx = 0, pady = 0, sticky = tk.W)
            TOCWithImage_CB.grid(column = 1, row = 1, padx = 0, pady = 0, sticky = tk.E)
            
            #
            # screenshot:
            #
            currScrShotDirText = wu.Screenshot.getText_CurrentScreenshotDirWidget(winMainRoot, cls.classPrefix)
            currScrShotDirText.grid(columnspan = 3,row = 2, column = 1)

            #
            # choose book/top section/subsections
            #
            chooseBookOM = ChooseMaterial.getOptionsMenu_ChooseBook(winMainRoot, cls.classPrefix)
            chooseBookOM.grid(column = 0, row = 0, padx = 0, pady = 0)

            chooseTopSectionOptionMenu = ChooseMaterial.getOptionMenu_ChooseTopSection(winMainRoot, cls.classPrefix)
            chooseTopSectionOptionMenu.grid(column = 0, row = 1, padx = 0, pady = 0)

            chooseSubsectionMenu = ChooseMaterial.getOptionMenu_ChooseSubsection(winMainRoot, cls.classPrefix)
            chooseSubsectionMenu.grid(column = 0, row = 2, padx = 0, pady = 0)
    
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
            
            listOfLayouts = _u.Settings.layoutsList
            layout_name_vatying = tk.StringVar()
            layout_name_vatying.set(listOfLayouts[0])

            frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_layouts_optionMenu", background="Blue")        
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
                fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currSection_ID)
            )
            wv.UItkVariables.imageGenerationEntryText.set(
                fsm.Wr.SectionInfoStructure.readProperty(wv.UItkVariables.subsection.get(), 
                                                        fsm.PropIDs.Sec.imIndex_ID)
            )

        default_book_name="Select a a book"

        '''
        functions that retrun options menus for choosing book
        '''
        book_name = tk.StringVar()
        book_name.set(default_book_name)

        # Create the list of books we have
        listOfBooksNames = _u.getListOfBooks()

        frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_chooseBook_optionMenu", background="Blue")
        book_menu = tk.OptionMenu(frame, book_name, 
                                *listOfBooksNames, command= lambda x: bookMenuChooseCallback(book_name))
        book_menu.grid(row=0, column = 0)
        
        return frame
    
    @classmethod
    def _topSectionChoosingCallback(cls, mainWinRoot):
        log.autolog("switching to top section: " + wv.UItkVariables.topSection.get())

        # update top section
        fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.currTopSection_ID , wv.UItkVariables.topSection.get())
        
        # update subsection
        sections = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_ID)
        prevSubsectionPath = sections[wv.UItkVariables.topSection.get()]["prevSubsectionPath"]
        fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.currSection_ID, prevSubsectionPath)

        # update image index
        secionImIndex = fsm.Wr.SectionInfoStructure.readProperty(prevSubsectionPath, fsm.PropIDs.Sec.imIndex_ID)
        wv.UItkVariables.imageGenerationEntryText.set(secionImIndex)         
        

        subsectionsList = wu.getSubsectionsListForCurrTopSection()
        subsectionsList.sort()
        #
        # Update other widgets
        #

        # subsection
        wu.updateOptionMenuOptionsList(mainWinRoot, 
                                        "_chooseSubsecion_optionMenu", 
                                        subsectionsList, 
                                        wv.UItkVariables.subsection,
                                        cls._subsectionChoosingCallback)        
        wv.UItkVariables.subsection.set(prevSubsectionPath)

        # update screenshot widget
        wu.Screenshot.setValueScreenshotLoaction()

        # update image index widget
        wv.UItkVariables.imageGenerationEntryText.set(
                fsm.Wr.SectionInfoStructure.readProperty(wv.UItkVariables.subsection.get(), 
                                                    fsm.PropIDs.Sec.imIndex_ID)
        )

        # update Layout
        widgetDimensions = LayoutsMenus.MainLayoutUI.pyAppDimensions
        lm.Wr.MainLayout.set(mainWinRoot, *widgetDimensions)

    @classmethod
    def getOptionMenu_ChooseTopSection(cls, mainWinRoot, namePrefix = ""):
        '''
        functions that retrun options menus for choosing chapter
        '''
        wv.UItkVariables.topSection.set(fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currTopSection_ID))

        topSectionsList = fsm.getTopSectionsList()
        topSectionsList.sort(key = int)

        frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_chooseSection_optionMenu", background = "Blue")
        
        if topSectionsList == []:
            topSectionsList = ["No top sec yet."]
            # #return text if there is not top sections yet
            # text = tk.Text(frame, width=15, height=1, name = namePrefix.lower() + "_noSectionText")
            # text.insert("1.0", "No top sec yet.")
            # text.grid(row = 0, column = 0)
            
            # return frame
        
        topSection_menu = tk.OptionMenu(frame, 
                                        wv.UItkVariables.topSection , 
                                        *topSectionsList, 
                                        command= lambda x: cls._topSectionChoosingCallback(mainWinRoot))
        topSection_menu.grid(row = 0, column = 0)

        return frame
    
    def _subsectionChoosingCallback(mainWinRoot):
        subsection = wv.UItkVariables.subsection
        sections = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_ID)
        sections[wv.UItkVariables.topSection.get()]["prevSubsectionPath"] = subsection.get()
        fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.sections_ID , sections)
        
        fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.currSection_ID , subsection.get())
        
        wv.UItkVariables.imageGenerationEntryText.set(
            fsm.Wr.SectionInfoStructure.readProperty(subsection.get(), 
                                                fsm.PropIDs.Sec.imIndex_ID)
        )

        wu.Screenshot.setValueScreenshotLoaction()
        
        # update Layout
        widgetDimensions = LayoutsMenus.MainLayoutUI.pyAppDimensions
        lm.Wr.MainLayout.set(mainWinRoot, *widgetDimensions)

        

    @classmethod
    def getOptionMenu_ChooseSubsection(cls, mainWinRoot, namePrefix = ""):
        subsection =wv.UItkVariables.subsection
        subsection.set(fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currSection_ID))
        
        subsectionsList = wu.getSubsectionsListForCurrTopSection()


        frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_chooseSubsecion_optionMenu", background="Blue")
        
        if subsectionsList == []:
            subsectionsList = ["No subsec yet."]
            # text = tk.Text(frame, width=18, height=1, name = namePrefix.lower() + "_noSubsectionText")
            # text.insert("1.0", "No subsec yet.")
            # text.grid(row = 0, column = 0)
            
            # return frame
            
        subchapter_menu = tk.OptionMenu(frame, 
                                        subsection, 
                                        *subsectionsList, 
                                        command = lambda *args: cls._subsectionChoosingCallback(mainWinRoot),
                                        )
        subchapter_menu.grid(row = 0, column = 0)
        
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
        chooseSectionMenus_Btn = cls.getButton_chooseSectionsMenusAndBack(mainWinRoot, cls.sectionsPrefix)
        chooseSectionMenus_Btn.grid(row = 1, column = 2)
        entry_setSectionName, button_setSectionName = cls.getWidgets_setSectionName(mainWinRoot,  cls.sectionsPrefix)
        entry_setSectionName.grid(row = 0, column = 0)
        button_setSectionName.grid(row = 0, column = 1)
        entry_setSectionStartPage, button_setSectionStartPage = cls.getWidgets_setSectionStartPage(mainWinRoot,  cls.sectionsPrefix)
        entry_setSectionStartPage.grid(row = 1, column = 0)
        button_setSectionStartPage.grid(row = 1, column = 1)

        sectionPath_ETR = cls.getEntrie_setNewSectionPath(mainWinRoot, cls.sectionsPrefix)
        sectionPath_ETR.grid(row = 0, column = 2, sticky = tk.N)     
        addSec_BTN = cls.getButton_createNewSection(mainWinRoot, cls.sectionsPrefix)
        removeSec_BTN = cls.getButton_removeTopSection(mainWinRoot, cls.sectionsPrefix)
        addSec_BTN.grid(row = 0, column = 2,sticky = tk.W)
        removeSec_BTN.grid(row = 0, column = 2,sticky = tk.E)


    @classmethod
    def getButton_chooseSectionsMenusAndBack(cls, mainWinRoot, prefixName = ""):
        def chooseChaptersMenusAndBackCallback():
            # hide all of the menus
            wu.hideAllWidgets(mainWinRoot)
            if not _u.Settings.UI.showMainWidgetsNext:
                mainWinRoot.columnconfigure(0, weight = 1)
                mainWinRoot.columnconfigure(1, weight = 1)
                mainWinRoot.columnconfigure(2, weight = 3)
                mainWinRoot.columnconfigure(3, weight = 1)
                
                for w in mainWinRoot.winfo_children():
                    if cls.sectionsPrefix.lower() in w._name:
                        log.autolog(w._name)
                        w.grid()
                chooseChapter_MenusBtn_Label.set("sections")
                _u.Settings.UI.showMainWidgetsNext = True
            else:
                mainWinRoot.columnconfigure(0, weight = 1)
                mainWinRoot.columnconfigure(1, weight = 3)
                mainWinRoot.columnconfigure(2, weight = 1)
                mainWinRoot.columnconfigure(3, weight = 3)
                for w in mainWinRoot.winfo_children():
                    if LayoutsMenus.MainLayoutUI.classPrefix in w._name:
                        w.grid()
                wu.showCurrentLayout(mainWinRoot, *LayoutsMenus.MainLayoutUI.pyAppDimensions)  
                chooseChapter_MenusBtn_Label.set("layout") 
                _u.Settings.UI.showMainWidgetsNext = False

        
        # show getBack Button
        chooseChapter_MenusBtn_Label = tk.StringVar()
        chooseChapter_MenusBtn_Label.set("sections") 
        chooseChapter_MenusBtn = tk.Button(mainWinRoot,
                                         name = prefixName.lower() 
                                                + "_chooseChapterLayoutBtn", 
                                        textvariable = chooseChapter_MenusBtn_Label, 
                                        command = chooseChaptersMenusAndBackCallback)
        
        return chooseChapter_MenusBtn


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
                            command = setTopSectionNameCallback)
        
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
                        command = setTopSectionStartPageCallback)
        
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
            separator = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_path_separator_ID)
            topSectionName = secPath.split(separator)[0]
            fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.currTopSection_ID, topSectionName)
            fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.currSection_ID, secPath)
            sections = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_ID)
            sections[topSectionName]["prevSubsectionPath"] = secPath
            fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.sections_ID, sections)


            fsm.Wr.SectionInfoStructure.updateProperty(secPath, fsm.PropIDs.Sec.name_ID, secName)            
            fsm.Wr.SectionInfoStructure.updateProperty(secPath, fsm.PropIDs.Sec.startPage_ID, secStartPage)
           

            # update ui
            topSections = list(fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_ID).keys())
            subsections = wu.getSubsectionsListForCurrTopSection()
            wu.updateOptionMenuOptionsList(mainWinRoot, 
                                        "_chooseSection_optionMenu",
                                        topSections, 
                                        wv.UItkVariables.topSection,
                                        ChooseMaterial._topSectionChoosingCallback
                                        ) 
            wu.updateOptionMenuOptionsList(mainWinRoot, 
                                        "_chooseSubsecion_optionMenu",
                                        subsections,
                                        wv.UItkVariables.subsection,
                                        ChooseMaterial._subsectionChoosingCallback
                                        ) 
        
        return tk.Button(mainWinRoot, 
                        name = prefixName.lower() + "_createNewTopSection_" + "BTN", 
                        text="New", 
                        command = createNewBTNcallback)
    

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
                        command = removeBTNcallback)

