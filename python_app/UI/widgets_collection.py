import os
import tkinter as tk
from tkinter import messagebox
from threading import Thread

import _utils._utils_main as _u
import file_system.file_system_main as fs
import UI.widgets_vars as wv
import UI.widgets_utils as wu
import layouts.layouts_utils as lu
import layouts.layouts_manager as lm
import tex_file.create_tex_file as t




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


def getAddImage_BTN(cls, mainWinRoot, prefixName = ""):
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


def getGlobalLinksAdd_Widgets(cls, mainWinRoot, prefixName = ""):
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


@classmethod
def getTextEntryButton_imageGeneration(cls, mainWinRoot, prefixName = ""):
    wv.UItkVariables.imageGenerationEntryText = tk.StringVar()
    imageProcessingETR = tk.Entry(mainWinRoot, 
                                width = 8,
                                textvariable =  wv.UItkVariables.imageGenerationEntryText,
                                name=prefixName.lower() + "_imageGeneration_" + wu.entryWidget_ID)

    chapterImIndex = _u.BookSettings.ChapterProperties.getCurrChapterImIndex()
    wv.UItkVariables.imageGenerationEntryText.set(chapterImIndex)

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



class Layout:
    
    @classmethod
    def showCurrentLayout(cls, mainWinRoot):
        l_Name = _u.Settings.currLayout

        #TODO: need to be reworked
        layoutClass = [i for i in lm.listOfLayoutClasses if i.__name__.replace(_u.Settings.PubProp.currLayout_ID,"") == l_Name][0]
        layoutClass.set(mainWinRoot)
        wu.hideAllWidgets(mainWinRoot)

        for e in mainWinRoot.winfo_children():
            if layoutClass.__name__.lower() in e._name:
                if (wu.entryWidget_ID in e._name):
                    e.focus_set()
                e.grid()


    @classmethod
    def getOptionsMenu_Layouts(cls, mainWinRoot, namePrefix = ""):
        def layoutOptionMenuCallback(layout_name_vatying):
            _u.Settings.currLayout = layout_name_vatying.get()
            cls.showCurrentLayout(mainWinRoot)
        
        listOfLayouts = _u.Settings.readProperty(_u.Settings.PubProp.currLayout_ID)
        layout_name_vatying = tk.StringVar()
        layout_name_vatying.set(listOfLayouts[0])

        frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_layouts_optionMenu", background="Blue")        
        layouts_optionMenu = tk.OptionMenu(frame, layout_name_vatying, *listOfLayouts, command= lambda x: layoutOptionMenuCallback(layout_name_vatying))
        
        layouts_optionMenu.grid(row=0, column=0)
        
        return frame

class ChooseBookSection:

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
        def chapterChoosingCallback(chapter):
            print("chapterChoosingCallback - switching to chapter: " + chapter.get())
            
            fs.BookInfoStructure.updateProperty(fs.BookInfoStructure.currSection_ID , chapter.get())

            chapterImIndex = _u.BookSettings.ChapterProperties.getCurrChapterImIndex()
            wv.UItkVariables.imageGenerationEntryText.set(chapterImIndex)

            
            wu.Screenshot.setValueScreenshotLoaction()
            
            subchaptersList = wu._getSubchaptersListForCurrChapter()
            wu._updateOptionMenuOptionsList(mainWinRoot, "_chooseSubchapter_optionMenu", subchaptersList)
            currSubchapter = _u.BookSettings.ChapterProperties.getChapterLatestSubchapter(fs.BookInfoStructure.readProperty(fs.BookInfoStructure.currSection_ID)[2:])
            wv.UItkVariables.subchapter.set(currSubchapter)
            fs.BookInfoStructure.updateProperty(fs.BookInfoStructure.currSectionFull_ID, subchaptersList[0])

            currLayoutClass = _u.Settings.Layout.getCurrLayoutClass()
            currLayoutClass.pyAppHeight = mainWinRoot.winfo_height()
            currLayoutClass.set(mainWinRoot)
            lu.moveWholeBookToChapter()


        chapter = tk.StringVar()
        chapter.set(fs.BookInfoStructure.readProperty(fs.BookInfoStructure.currSection_ID))

        book_name = _u.Settings.readProperty(_u.Settings.Book.getCurrentBookFolderName())

        pathToBooks = _u.getPathToBooks()
        chaptersList = []
        chaptersList.extend([i for i in os.listdir(pathToBooks + "/" + book_name) if i[:2]=="ch"])
        chaptersList.sort(key=lambda x: -1 if x[2:]=="" else int(x[2:]))
        
        frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_chooseChapter_optionMenu", background="Blue")
        chapter_menu = tk.OptionMenu(frame, chapter, *chaptersList, command= lambda x: chapterChoosingCallback(chapter))
        chapter_menu.grid(row = 0, column = 0)

        return frame

    
    @classmethod
    def getOptionMenu_ChooseSubchapter(cls, mainWinRoot, namePrefix = ""):
        def subchapterChoosingCallback(subchapter):
            _u.BookSettings.ChapterProperties.updateChapterLatestSubchapter(fs.BookInfoStructure.readProperty(fs.BookInfoStructure.currSection_ID)[2:],
                                                                    subchapter.get())
            fs.BookInfoStructure.updateProperty(fs.BookInfoStructure.PubProp.currSection_ID, subchapter.get())
        

        wv.UItkVariables.subchapter  = tk.StringVar()
        subchapter =wv.UItkVariables.subchapter
        subchapter.set(_u.BookSettings.readProperty(fs.BookInfoStructure.PubProp.currSection_ID))
        
        subchaptersList = wu._getSubchaptersListForCurrChapter()

        frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_chooseSubchapter_optionMenu", background="Blue")
        subchapter_menu = tk.OptionMenu(frame, subchapter, *subchaptersList, command= lambda x: subchapterChoosingCallback(subchapter))
        subchapter_menu.grid(row = 0, column = 0)
        return frame
    
