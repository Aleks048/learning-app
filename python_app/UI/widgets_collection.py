import os
import tkinter as tk
from tkinter import messagebox
from threading import Thread

import _utils._utils_main as _u
import file_system.file_system_main as fs
import file_system.file_system_manager as fsm
import UI.widgets_vars as wv
import UI.widgets_utils as wu
import layouts.layouts_utils as lu
import layouts.layouts_manager as lm
import tex_file.create_tex_file as t



def getCheckboxes_TOC(mainWinRoot, namePrefix = ""):
    wv.UItkVariables.createTOCVar = tk.IntVar()
    wv.UItkVariables.createTOCVar.set(1)
    createTOC_CB = tk.Checkbutton(mainWinRoot, name = namePrefix.lower() + "_create_toc", text = "TOC cr",
                                variable = wv.UItkVariables.createTOCVar, onvalue = 1, offvalue = 0)
    wv.UItkVariables.TOCWithImageVar = tk.IntVar()
    TOCWithImage_CB = tk.Checkbutton(mainWinRoot, name = namePrefix.lower() + "_toc_w_image",  text = "TOC w i",
                                variable = wv.UItkVariables.TOCWithImageVar, onvalue = 1, offvalue = 0)
    
    return createTOC_CB, TOCWithImage_CB


def getImageGenerationRestart_BTN(mainWinRoot, namePrefix = ""):
    def restartBTNcallback():
        wv.UItkVariables.buttonText.set("imNum")
        chapterImIndex = _u.BookSettings.ChapterProperties.getCurrSectionImIndex()
        wv.UItkVariables.imageGenerationEntryText.set(chapterImIndex)
    

    restart_BTN = tk.Button(mainWinRoot,
                            name = namePrefix.lower() + "_imageGenerationRestartBTN",
                            text= "restart", 
                            command = restartBTNcallback)
    
    return restart_BTN


def getShowProofs_BTN(mainWinRoot, prefixName = ""):
    showProofsVar = tk.StringVar()
    showProofsVar.set("Hide Proofs")
    def _changeProofsVisibility(hideProofs):
        with open(t.TexFile._getCurrContentFilepath(),"r") as conF:
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
        with open(t.TexFile._getCurrContentFilepath(),"w") as conF:
            _waitDummy = conF.writelines(contentLines)
    
    def getShowProofsCallBack():
        if showProofsVar.get() == "Show Proofs":
            showProofsVar.set("Hide Proofs")
            _changeProofsVisibility(True)
            Thread(target=t.TexFile.buildCurrentSubchapterPdf).start()
        elif showProofsVar.get() == "Hide Proofs":
            showProofsVar.set("Show Proofs")
            _changeProofsVisibility(False)
            Thread(target=t.TexFile.buildCurrentSubchapterPdf).start()
    
    return tk.Button(mainWinRoot, 
                    name = prefixName.lower() + "_showProofsBTN",
                    textvariable = showProofsVar,
                    command = getShowProofsCallBack)


def getAddImage_BTN(mainWinRoot, prefixName = ""):
    def addImBTNcallback():
        currImID = str(int(_u.BookSettings.readProperty(_u.BookSettings.CurrentStateProperties.Section.currImageID_ID)) - 1)
        currentSubchapter = _u.BookSettings.readProperty(_u.BookSettings.CurrentStateProperties.Book.currSectionFull_ID)
        
        # screenshot
        imName = ""

        # get name of the image from the text field
        for w in mainWinRoot.winfo_children():
            if "_imageGeneration_" + wu.entryWidget_ID in w._name:
                imName = w.get()
        
        extraImagePath = _u.getCurrentScreenshotDir() \
                            + currImID + "_" + currentSubchapter \
                            + "_" + imName
        
        if os.path.isfile(extraImagePath + ".png"):
            def takeScreencapture(savePath):
                os.system("screencapture -ix " + savePath)
                wv.UItkVariables.needRebuild.set(True)
            cls.confirmationWindow("The file exists. Overrite?", takeScreencapture, extraImagePath + ".png")
        else:
            os.system("screencapture -ix " + extraImagePath + ".png")
            wv.UItkVariables.needRebuild.set(True)

        # update the content file
        marker = "THIS IS CONTENT id: " + currImID
        with open(t.TexFile._getCurrContentFilepath(), "r+") as f:
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
        
        t.TexFile._populateMainFile()
    
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
        t.TexFile.buildCurrentSubchapterPdf()
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
            cls.showMessage("The sections and name should be in a '" + sectionsStringSeparator + "' separated string.")
        else:
            linkName = sections[-1]
            targetSection = sections[0]
            subsections = sections[1:-1]

            # get current file page
            currFilePage = _u.getpageOfcurrentDoc()
            #update the current file link

            # get target tex file position
            currBookPath = _u.Settings.Book.getCurrBookFolderPath()
            with open(currBookPath + "/" + sections[0] + "/subchapters" + "/".join(subsections)) as f:
                targetLines = f.readlines()

    
    createGlLinkBTN = tk.Button(mainWinRoot, text = "Create gl link", 
                        name = prefixName.lower() + "addGlobalLinkBTN",
                        command = addClLinkCallback)

    targetSections = tk.StringVar()
    createGlLinkETR = tk.Entry(mainWinRoot,
                            width = 5,
                            textvariable = targetSections,
                            name = prefixName.lower() + "addGlobalLink" + wu.entryWidget_ID)
    
    return createGlLinkBTN, createGlLinkETR


def getTextEntryButton_imageGeneration(mainWinRoot, prefixName = ""):
    wv.UItkVariables.imageGenerationEntryText = tk.StringVar()
    print("hi")
    print(type(mainWinRoot))
    imageProcessingETR = tk.Entry(mainWinRoot, 
                                width = 8,
                                textvariable =  wv.UItkVariables.imageGenerationEntryText,
                                name=prefixName.lower() + "_imageGeneration_" + wu.entryWidget_ID)

    secImIndex = _u.getCurrSecImIdx()
    wv.UItkVariables.imageGenerationEntryText.set(secImIndex)

    dataFromUser = [-1, -1, -1]
    wv.UItkVariables.buttonText = tk.StringVar()

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
conIDX=`grep -n \"% THIS IS CONTENT id: " + dataFromUser[0] +"\" \"" + t.TexFile._getCurrContentFilepath() + "\" | cut -d: -f1`\n"
        scriptFile += "\
tocIDX=`grep -n \"% THIS IS CONTENT id: " + dataFromUser[0] +"\" \"" + t.TexFile._getCurrTOCFilepath() + "\" | cut -d: -f1`\n"
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
        scriptFile += "osascript -e '\
tell application \"" + _u.Settings._appsIDs.skim_ID + "\"\n\
    tell document \"" + fs.BookInfoStructure.readProperty(fs.BookInfoStructure.PubProp.currSection_ID) + "_main.pdf" + "\"\n\
        delay 0.1\n\
        go to page " + str(dataFromUser[0]) + "\n\
        end tell\n\
end tell'"

        return scriptFile


    def _createTexForTheProcessedImage():
        currentSubchapter = fs.BookInfoStructure.readProperty(fs.BookInfoStructure.PubProp.currSection_ID)

        extraImagePath = _u.getCurrentScreenshotDir() \
                            + dataFromUser[0] + "_" + currentSubchapter \
                            + "_" + dataFromUser[1]

        # ADD CONTENT ENTRY TO THE PROCESSED CHAPTER
        with open(t.TexFile._getCurrContentFilepath(), 'a') as f:
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
                with open(t.TexFile._getCurrTOCFilepath(), 'a') as f:
                    toc_add_image = "\
% THIS IS CONTENT id: " + dataFromUser[0] + " \n\
\\mybox{\n\
    \\link[" + dataFromUser[0] + \
    "]{" + dataFromUser[1] + "} \\image[0.5]{" + \
    dataFromUser[0] + "_" + currentSubchapter + "_" + dataFromUser[1] + "}\n\
}\n\n\n"
                    f.write(toc_add_image)
            else:  
                # TOC ADD ENTRY WITHOUT IMAGE
                with open(t.TexFile._getCurrTOCFilepath(), 'a') as f:
                    toc_add_text = "\
% THIS IS CONTENT id: " + dataFromUser[0] + " \n\
\\mybox{\n\
    \\link[" + dataFromUser[0] + "]{" + dataFromUser[1] + "} \\textbf{!}\n\
}\n\n\n"
                    f.write(toc_add_text)
            

        #create a script to run on page change
        imageAnscriptPath = _u.getCurrentScreenshotDir() + dataFromUser[0] + \
                            "_" + currentSubchapter + "_" + dataFromUser[1]

        # STOTE IMNUM, IMNAME AND LINK
        fs.BookInfoStructure.updateProperty(_u.BookSettings.CurrentStateProperties.Section.currImageID_ID, dataFromUser[0])
        _u.BookSettings.updateProperty(_u.BookSettings.CurrentStateProperties.Section.currLinkName_ID, dataFromUser[1])
        
        # POPULATE THE MAIN FILE
        t.TexFile._populateMainFile()
        
        
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
                _u.BookSettings.ChapterProperties.updateChapterImageIndex(fs.BookInfoStructure.readProperty(fs.BookInfoStructure.currSection_ID)[2:],
                                                                    nextImNum)
                _u.BookSettings.updateProperty(_u.BookSettings.CurrentStateProperties.Section.currImageID_ID, nextImNum)
                wv.UItkVariables.imageGenerationEntryText.set(nextImNum)
                wv.UItkVariables.buttonText.set("imNum")
            
            cls.confirmationWindow("The file exists. Overrite?", takeScreencapture, imageAnscriptPath)
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
            _u.BookSettings.ChapterProperties.updateChapterImageIndex(fs.BookInfoStructure.readProperty(fs.BookInfoStructure.currSection_ID)[2:],
                                                                nextImNum)
            _u.BookSettings.updateProperty(_u.BookSettings.CurrentStateProperties.Section.currImageID_ID, nextImNum)
            wv.UItkVariables.imageGenerationEntryText.set(nextImNum)

    buttonNamesToFunc = {"imNum": lambda *args: wv.UItkVariables.imageGenerationEntryText.set(""),
                        "imLink":_createTexForTheProcessedImage}
    buttonNames = list(buttonNamesToFunc.keys())
    
    wv.UItkVariables.buttonText.set(buttonNames[0])

    def buttonCallback():
        pass
        # for i in range(len(buttonNames)):
        #     if buttonNames[i] == wv.UItkVariables.buttonText.get():
        #         _storeInputDataAndChange(buttonNames[(i+1)%len(buttonNames)], 
        #                                 buttonNamesToFunc[buttonNames[i]], i)
        #         break

    processButton = tk.Button(mainWinRoot, 
                            name = prefixName.lower() + "_imageGeneration_processButton",
                            textvariable = wv.UItkVariables.buttonText, 
                            command= buttonCallback)
    
    return [imageProcessingETR, processButton]





class LayoutsMenus:


    class ChaptersLayoutUI:
        pyAppDimensions = [None, None]

        @classmethod
        def addWidgets(cls, winMainRoot):
            wv.UItkVariables.needRebuild = tk.BooleanVar()

            layoutOM = LayoutsMenus._commonWidgets.getOptionsMenu_Layouts(winMainRoot, cls.__name__)
            layoutOM.grid(column=0, row=0, padx=0, pady=0)
            layoutOM.update()
            
            showProofsBTN = getShowProofs_BTN(winMainRoot, cls.__name__)
            showProofsBTN.grid(column=1, row=0, padx=0, pady=0)

            dummyEntry = tk.Entry(winMainRoot, text = "Dummy", name = cls.__name__.lower() + "_dummyFocusEntry")
            dummyEntry.grid(column=2, row=0, padx=0, pady=0)
            dummyEntry.focus_set()

            saveImageBTN = getSaveImage_BTN(winMainRoot, cls.__name__)
            saveImageBTN.grid(column=3, row=0, padx=0, pady=0)

            createGlLinkBTN, createGlLinkETR = getGlobalLinksAdd_Widgets(winMainRoot, cls.__name__)
            createGlLinkETR.grid(column=4, row=0, padx=0, pady=0)
            createGlLinkBTN.grid(column=5, row=0, padx=0, pady=0)


            mon_width, _ = _u.getMonitorSize()
            cls.pyAppDimensions[0] = int(mon_width / 2)
            cls.pyAppDimensions[1] = layoutOM.winfo_height() + 5
    
    class MainLayoutUI:
        pyAppDimensions = [None, None]

        @classmethod
        def addWidgets(cls, winMainRoot):
            mon_width, _ = _u.getMonitorSize()
            cls.pyAppDimensions = [int(mon_width / 2), 90]

            #
            # layout: 
            #
            layoutOM = LayoutsMenus._commonWidgets.getOptionsMenu_Layouts(winMainRoot, cls.__name__)
            layoutOM.grid(column = 0, row = 1, padx = 0, pady = 0)

            #
            # image generation:
            #
            imageGenerationUI = getTextEntryButton_imageGeneration(winMainRoot, cls.__name__)
            imageGenerationUI[0].grid(column = 1, row = 0, padx = 0, pady = 0, sticky = tk.N)
            imageGenerationUI[1].grid(column = 1, row = 1, padx = 0, pady = 0, sticky = tk.N)

            addExtraImage = getAddImage_BTN(winMainRoot, cls.__name__)
            addExtraImage.grid(column = 1, row = 0, padx = 0, pady = 0, sticky = tk.E)

            imageGenerationRestartBTN = getImageGenerationRestart_BTN(winMainRoot, cls.__name__)
            imageGenerationRestartBTN.grid(column = 1, row = 0, padx = 0, pady = 0, sticky = tk.W)

            TOCcreate_CB, TOCWithImage_CB = getCheckboxes_TOC(winMainRoot, cls.__name__)
            TOCcreate_CB.grid(column = 1, row = 1, padx = 0, pady = 0, sticky = tk.W)
            TOCWithImage_CB.grid(column = 1, row = 1, padx = 0, pady = 0, sticky = tk.E)
            
            #
            # screenshot:
            #
            currScrShotDirText = wu.Screenshot.getText_CurrentScreenshotDirWidget(winMainRoot, cls.__name__)
            currScrShotDirText.grid(columnspan = 2,row = 2)

            #
            # choose book/top section/subsections
            #
            chooseBookOM = ChooseMaterial.getOptionsMenu_ChooseBook(winMainRoot, cls.__name__)
            chooseBookOM.grid(column = 0, row = 0, padx = 0, pady = 0)

            chooseTopSectionOptionMenu = ChooseMaterial.getOptionMenu_ChooseTopSection(winMainRoot, cls.__name__)
            chooseTopSectionOptionMenu.grid(column = 2, row = 0, padx = 0, pady = 0)

            chooseSubsectionMenu = ChooseMaterial.getOptionMenu_ChooseSubsection(winMainRoot, cls.__name__)
            chooseSubsectionMenu.grid(column = 3, row = 2, padx = 0, pady = 0)
    
            #
            # switch to sections menus
            #
            chooseSectionsMenusAndbackBtn = ChaptersUI.getButton_chooseSectionsMenusAndBack(winMainRoot, cls.__name__)
            chooseSectionsMenusAndbackBtn.grid(column = 3, row = 0, padx = 0, pady = 0)

    class wholeVSCodeLayoutUI:
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
                wu.showCurrentLayout(mainWinRoot)
            
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



class ChooseMaterial:

    def getOptionsMenu_ChooseBook(mainWinRoot, namePrefix = ""):
        def bookMenuChooseCallback(bookNameStVar):
            bookName = bookNameStVar.get()
            bookPaths = _u.Settings.readProperty(_u.Settings.PubProp.booksPaths_ID)
            bookPath = bookPaths[bookName]
            _u.Settings.Book.setCurrentBook(bookName, bookPath)


        default_book_name="Select a a book"

        '''
        functions that retrun options menus for choosing book
        '''
        book_name = tk.StringVar()
        book_name.set(default_book_name)

        # Create the list of books we have
        listOfBooksNames = _u.getListOfBooks()
        print(listOfBooksNames)

        frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_chooseBook_optionMenu", background="Blue")
        book_menu = tk.OptionMenu(frame, book_name, 
                                *listOfBooksNames, command= lambda x: bookMenuChooseCallback(book_name))
        book_menu.grid(row=0, column = 0)
        
        return frame
    
    @classmethod
    def getOptionMenu_ChooseTopSection(cls, mainWinRoot, namePrefix = ""):
        '''
        functions that retrun options menus for choosing chapter
        '''
        def sectionChoosingCallback():
            topSection = wv.UItkVariables.topSection
            print("chapterChoosingCallback - switching to chapter: " + topSection.get())
            fs.BookInfoStructure.updateProperty(fs.BookInfoStructure.PubProp.currTopSection_ID , topSection.get())
            chapterImIndex = _u.BookSettings.ChapterProperties.getCurrSectionImIndex()
            wv.UItkVariables.imageGenerationEntryText.set(chapterImIndex)         
            
            #
            # Update other widgets
            #
            subsectionsList = wu._getSubsectionsListForCurrTopSection()
            wu._updateOptionMenuOptionsList(mainWinRoot, "_chooseSubchapter_optionMenu", subsectionsList, cls._subsectionChoosingCallback)
            
            sections = fs.BookInfoStructure.readProperty(fs.BookInfoStructure.PubProp.sections_ID)
            prevSubsectionPath = sections[topSection.get()]["prevSubsectionPath"]
            wv.UItkVariables.subsection.set(prevSubsectionPath)

            fs.BookInfoStructure.updateProperty(fs.BookInfoStructure.PubProp.currSection_ID, prevSubsectionPath)
            # screenshot
            wu.Screenshot.setValueScreenshotLoaction()

            #
            # update Layout
            #
            # currLayoutClass = _u.Settings.Layout.getCurrLayoutClass()
            # currLayoutClass.pyAppHeight = mainWinRoot.winfo_height()
            # currLayoutClass.set(mainWinRoot)
            # lu.moveWholeBookToChapter()

        wv.UItkVariables.topSection = tk.StringVar()
        wv.UItkVariables.topSection.set(fs.BookInfoStructure.readProperty(fs.BookInfoStructure.PubProp.currTopSection_ID))

        topSectionsList = fsm.getTopSectionsList()
        
        frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_chooseSection_optionMenu", background = "Blue")
        topSection_menu = tk.OptionMenu(frame, 
                                        wv.UItkVariables.topSection , 
                                        *topSectionsList, 
                                        command= lambda x: sectionChoosingCallback())
        topSection_menu.grid(row = 0, column = 0)

        return frame
    
    def _subsectionChoosingCallback():
            subsection = wv.UItkVariables.subsection
            sections = fs.BookInfoStructure.readProperty(fs.BookInfoStructure.PubProp.sections_ID)
            sections[wv.UItkVariables.topSection.get()]["prevSubsectionPath"] = subsection.get()
            fs.BookInfoStructure.updateProperty(fs.BookInfoStructure.PubProp.sections_ID , sections)
            
            fs.BookInfoStructure.updateProperty(fs.BookInfoStructure.PubProp.currSection_ID , subsection.get())
            
            wu.Screenshot.setValueScreenshotLoaction()

    @classmethod
    def getOptionMenu_ChooseSubsection(cls, mainWinRoot, namePrefix = ""):
        

        wv.UItkVariables.subsection  = tk.StringVar()
        subsection =wv.UItkVariables.subsection
        subsection.set(_u.BookSettings.readProperty(fs.BookInfoStructure.PubProp.currSection_ID))
        
        subsectionsList = wu._getSubsectionsListForCurrTopSection()

        frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_chooseSubchapter_optionMenu", background="Blue")
        subchapter_menu = tk.OptionMenu(frame, 
                                        subsection, 
                                        *subsectionsList, 
                                        command = lambda *args: cls._subsectionChoosingCallback(),
                                        )
        subchapter_menu.grid(row = 0, column = 0)
        return frame
   

'''
chapters menu widgets
'''
class ChaptersUI:
    chaptersPrefix = "chaptersID"

    @classmethod
    def setChaptersUI(cls, mainWinRoot):
        chooseChapter_MenusBtn = cls.getButton_chooseSectionsMenusAndBack(mainWinRoot, cls.chaptersPrefix)
        chooseChapter_MenusBtn.grid(row = 2, column = 3)
        entry_setChapterName, button_setChapterName = cls.getWidgets_setChapterName(mainWinRoot,  cls.chaptersPrefix)
        entry_setChapterName.grid(row = 0, column = 0)
        button_setChapterName.grid(row = 0, column = 1)
        entry_setChapterStartPage, button_setChapterStartPage = cls.getWidgets_setChapterStartPage(mainWinRoot,  cls.chaptersPrefix)
        entry_setChapterStartPage.grid(row = 1, column = 0)
        button_setChapterStartPage.grid(row = 1, column = 1)
        entry_setSubchapterName, button_setSubchapterName = cls.getWidgets_setSubchapterName(mainWinRoot,  cls.chaptersPrefix)
        entry_setSubchapterName.grid(row = 0, column = 2)
        button_setSubchapterName.grid(row = 0, column = 3)
        entry_setSubchapterStartpage, button_setSubchapterStartPage = cls.getWidgets_setSubchapterStartPage(mainWinRoot,  cls.chaptersPrefix)
        entry_setSubchapterStartpage.grid(row = 1, column = 2)
        button_setSubchapterStartPage.grid(row = 1, column = 3)
        
        wv.UItkVariables.currCh = tk.StringVar()
        wv.UItkVariables.currSubch = tk.StringVar()
        currCh_ETR, currSubch_ETR = cls.getEntries_currChAndSubchapter(mainWinRoot, cls.chaptersPrefix)
        currCh_ETR.grid(row = 2, column = 0, sticky = tk.N)
        currSubch_ETR.grid(row = 2, column = 2, sticky = tk.N)


        addCh_BTN = cls.getButton_createNewChapter(mainWinRoot, cls.chaptersPrefix)
        removeCh_BTN = cls.getButton_removeChapter(mainWinRoot, cls.chaptersPrefix)
        addCh_BTN.grid(row = 2, column = 0,sticky = tk.W)
        removeCh_BTN.grid(row = 2, column = 0, sticky = tk.E)
        
        addSubch_BTN = cls.getButton_createNewSubchapter(mainWinRoot, cls.chaptersPrefix)
        removeSubch_BTN = cls.getButton_removeSubchapter(mainWinRoot, cls.chaptersPrefix)
        addSubch_BTN.grid(row = 2, column = 2,sticky = tk.W)
        removeSubch_BTN.grid(row = 2, column = 2,sticky = tk.E)


    @classmethod
    def getButton_chooseSectionsMenusAndBack(cls, mainWinRoot, prefixName = ""):
        def chooseChaptersMenusAndBackCallback():
            # hide all of the menus
            wu.hideAllWidgets(mainWinRoot)

            if _u.Settings.UI.showChapterWidgets:
                mainWinRoot.columnconfigure(0, weight = 1)
                mainWinRoot.columnconfigure(1, weight = 3)
                mainWinRoot.columnconfigure(2, weight = 1)
                mainWinRoot.columnconfigure(3, weight = 3)
                
                for w in mainWinRoot.winfo_children():
                    if cls.chaptersPrefix.lower() in w._name:
                        w.grid()
                chooseChapter_MenusBtn_Label.set("chapters")
                _u.Settings.UI.showChapterWidgets = not _u.Settings.UI.showChapterWidgets
            else:
                mainWinRoot.columnconfigure(0, weight = 1)
                mainWinRoot.columnconfigure(1, weight = 1)
                mainWinRoot.columnconfigure(2, weight = 1)
                mainWinRoot.columnconfigure(2, weight = 0)
                wu.showCurrentLayout(mainWinRoot)  
                chooseChapter_MenusBtn_Label.set("layout") 
                _u.Settings.UI.showChapterWidgets = not _u.Settings.UI.showChapterWidgets

        
        # show getBack Button
        chooseChapter_MenusBtn_Label = tk.StringVar()
        chooseChapter_MenusBtn_Label.set("chapters") 
        chooseChapter_MenusBtn = tk.Button(mainWinRoot, name = prefixName.lower() + "_chooseChapterLayoutBtn", textvariable = chooseChapter_MenusBtn_Label, command = chooseChaptersMenusAndBackCallback)
        
        return chooseChapter_MenusBtn


    @classmethod
    def getEntries_currChAndSubchapter(cls, mainWinRoot, prefixName = ""):
        currCh_ETR = tk.Entry(mainWinRoot, 
                            width = 5,
                            textvariable = wv.UItkVariables.currCh, 
                            name = prefixName.lower() +  "_setCurrChapter_" + wu.entryWidget_ID)
        currSubch_ETR = tk.Entry(mainWinRoot, 
                            width = 5, 
                            textvariable = wv.UItkVariables.currSubch, 
                            name = prefixName.lower() +  "_setCurrSubchapter_" + wu.entryWidget_ID)
        
        return currCh_ETR, currSubch_ETR


    @classmethod
    def getWidgets_setChapterName(cls, mainWinRoot, prefixName = ""):
        entry_setChapterName = tk.Entry(mainWinRoot, name = prefixName.lower() +  "_setChapterName_" + wu.entryWidget_ID)
        button_setChapterName = tk.Button(mainWinRoot, 
                                name = prefixName.lower() +  "_setChapterNameBTN", 
                                text="setChapterName", 
                                command = lambda *args: _u.BookSettings.ChapterProperties.updateChapterName(wv.UItkVariables.currCh.get(), entry_setChapterName.get()))
        
        return entry_setChapterName, button_setChapterName            


    @classmethod
    def getWidgets_setChapterStartPage(cls, mainWinRoot, prefixName = ""):
        entry_setChapterStartPage = tk.Entry(mainWinRoot, name = prefixName.lower() +  "_setChapterStartPage_" + wu.entryWidget_ID)
        button_setChapterStartPage = tk.Button(mainWinRoot, 
                        name = prefixName.lower() + "_setChapterStartPageBTN", 
                        text="setChapterStartPage", 
                        command = lambda *args: _u.BookSettings.ChapterProperties.updateChapterStartPage(wv.UItkVariables.currCh.get(), 
                        entry_setChapterStartPage.get()))
        
        return entry_setChapterStartPage, button_setChapterStartPage 


    @classmethod
    def getWidgets_setSubchapterName(cls, mainWinRoot, prefixName = ""):
        entry_setSubchapterName = tk.Entry(mainWinRoot, name = prefixName.lower() + "_setSubchapterName_" + wu.entryWidget_ID)
        button_setSubchapterName = tk.Button(mainWinRoot, 
                        name = prefixName.lower() + "_setSubchapterNameBTN", 
                        text="setSubhapterName", 
                        command = lambda *args: _u.BookSettings.SubchaptersProperties.updateSubchapterName(wv.UItkVariables.currSubch.get(), entry_setSubchapterName.get()))
        
        return entry_setSubchapterName, button_setSubchapterName


    @classmethod
    def getWidgets_setSubchapterStartPage(cls, mainWinRoot, prefixName = ""):
        entry_setSubchapterStartpage = tk.Entry(mainWinRoot, 
                                                name = prefixName.lower() 
                                                    + "_setSubchapterStartPage_" 
                                                    + wu.entryWidget_ID
                                                )
        button_setSubchapterStartPage = tk.Button(mainWinRoot, 
                                                name = prefixName.lower() 
                                                    + "_setSubchapterStartPageBTN", 
                                                text="setSubhapterStartName", 
                                                command = lambda *args : _u.BookSettings.SubchaptersProperties.updateSubchapterStartPage(wv.UItkVariables.currSubch.get(), entry_setSubchapterStartpage.get()))
        
        return entry_setSubchapterStartpage, button_setSubchapterStartPage


    @classmethod
    def getButton_createNewChapter(cls, mainWinRoot, prefixName = ""):
        def createNewChapterBTNcallback():
            chNum = None
            chName = None
            chStartPage = None
            for e in mainWinRoot.winfo_children():
                if  "_setCurrChapter_" + wu.entryWidget_ID in e._name:
                    chNum = e.get()
                elif "_setChapterName_" + wu.entryWidget_ID in e._name:
                    chName = e.get()
                elif "_setChapterStartPage_" + wu.entryWidget_ID in e._name:
                    chStartPage = e.get()
            _u.BookSettings.ChapterProperties.addChapter(chNum, chName, chStartPage)
        
        return tk.Button(mainWinRoot, 
                        name = prefixName.lower() + "_createNewChapterBTN", 
                        text="New", 
                        command = createNewChapterBTNcallback)
    

    @classmethod
    def getButton_removeChapter(cls, mainWinRoot, prefixName = ""):
        def removeBTNcallback():
            chNum = None
            for e in mainWinRoot.winfo_children():
                if  "_setCurrChapter_" + wu.entryWidget_ID in e._name:
                    chNum = e.get()
                    break
            _u.BookSettings.ChapterProperties.removeChapter(chNum)
        
        return tk.Button(mainWinRoot, 
                        name = prefixName.lower() + "_removeChapterBTN", 
                        text="Del", 
                        command = removeBTNcallback)
    

    @classmethod
    def getButton_createNewSubchapter(cls, mainWinRoot, prefixName = ""):
        def createNewChapterBTNcallback():
            chNum = None
            subchNum = None
            subchName = None
            subchStartPage = None
            for e in mainWinRoot.winfo_children():
                if  "_setCurrSubchapter_" + wu.entryWidget_ID in e._name:
                    subchNum = e.get()
                    chNum = subchNum.split(".")[0]
                elif "_setSubchapterName_" + wu.entryWidget_ID in e._name:
                    subchName = e.get()
                elif "_setSubchapterStartPage_" + wu.entryWidget_ID in e._name:
                    subchStartPage = e.get()
            
            _u.BookSettings.SubchaptersProperties.addSubchapter(chNum, subchNum, subchName, subchStartPage)
        
        return tk.Button(mainWinRoot, 
                        name = prefixName.lower() + "_createNewSubchapterBTN", 
                        text="New", 
                        command = createNewChapterBTNcallback)


    @classmethod
    def getButton_removeSubchapter(cls, mainWinRoot, prefixName = ""):
        def removeBTNcallback():
            chNum = None
            for e in mainWinRoot.winfo_children():
                if  "_setCurrSubchapter_" + wu.entryWidget_ID in e._name:
                    subchNum = e.get()
                    chNum = subchNum.split(".")[0]
            
            _u.BookSettings.SubchaptersProperties.removeSubchapter(chNum, subchNum)
        
        return tk.Button(mainWinRoot, 
                        name = prefixName.lower() + "_removeSubchapterBTN", 
                        text="Del", 
                        command = removeBTNcallback)

