import os
import tkinter as tk
from tkinter import messagebox
from threading import Thread

import layouts.layouts_main as layouts_main
import _utils._utils_main  as _u
import tex_file.create_tex_file as t 

'''
UI tk primvars
'''
class UItkVariables:
    needRebuild = None
    buttonText = None
    createTOCVar = None
    TOCWithImageVar = None
    subchapter = None
    imageGenerationEntryText = None
    scrshotPath = None
    currCh = None
    currSubch = None


'''
Class to store the widgets required for the menus
'''
class UIWidgets:
    showChapterWidgets = False

    entryWidget_ID = "ETR"

    listOfLayouts = _u.Settings.readProperty(_u.Settings.layouts_ID)
    listOfLayoutClasses = [getattr(layouts_main, layoutName + _u.Settings.layoutClass_ID) for layoutName in listOfLayouts]
    

    def showMessage(text):
        # Create an instance of tkinter frame or window
        win = tk.Tk()

        # Set the size of the tkinter window
        win.geometry("350x350")

        
        messagebox.showinfo('Processing knoledge', text)

        win.bind("<Enter>", win.destroy())

        win.mainloop()


    def confirmationWindow(inText, onYesFunction, *args):
        root = tk.Tk()
        root.title("Confirmation")

        def onYesCallback():
            root.destroy()
            Thread(target=lambda: onYesFunction(*args)).start()
    
    
        l1=tk.Label(root, image="::tk::icons::question")
        l1.grid(row=0, column=0, pady=(7, 0), padx=(10, 30), sticky="e")
        l2=tk.Label(root,text= inText)
        l2.grid(row=0, column=1, columnspan=3, pady=(7, 10), sticky="w")
    
        b1=tk.Button(root,text="Yes",command = onYesCallback, width = 10)
        b1.grid(row=1, column=1, padx=(2, 35), sticky="e")
        b2=tk.Button(root,text="No",command=root.destroy,width = 10)
        b2.grid(row=1, column=2, padx=(2, 35), sticky="e")
        
        def onYesCallbackWrapper(e):
            onYesCallback()
        root.bind("<Return>", onYesCallbackWrapper)
        root.bind("<Escape>", lambda e: root.destroy())

        root.mainloop()
        

    '''
    hide all of the widgets in the mainWinRoot
    '''
    @classmethod
    def hideAllWidgets(cls, mainWinRoot):
        for e in mainWinRoot.winfo_children():
            # clear all entries
            if (cls.entryWidget_ID in e._name):
                if ("_imageGeneration_" not in e._name):
                    e.delete(0, 'end')
            e.grid_remove()


    @classmethod
    def showCurrentLayout(cls, mainWinRoot):
        l_Name = _u.Settings.currLayout
        layoutClass = [i for i in cls.listOfLayoutClasses if i.__name__.replace(_u.Settings.layoutClass_ID,"") == l_Name][0]
        layoutClass.set(mainWinRoot)
        UIWidgets.hideAllWidgets(mainWinRoot)

        for e in mainWinRoot.winfo_children():
            if layoutClass.__name__.lower() in e._name:
                if (cls.entryWidget_ID in e._name):
                    e.focus_set()
                e.grid()


    '''
    option menu to to get layouts
    '''
    @classmethod
    def getOptionsMenu_Layouts(cls, mainWinRoot, namePrefix = ""):
        def layoutOptionMenuCallback(layout_name_vatying):
            _u.Settings.currLayout = layout_name_vatying.get()
            UIWidgets.showCurrentLayout(mainWinRoot)
        
        listOfLayouts = _u.Settings.readProperty(_u.Settings.layouts_ID)
        layout_name_vatying = tk.StringVar()
        layout_name_vatying.set(listOfLayouts[0])

        frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_layouts_optionMenu", background="Blue")        
        layouts_optionMenu = tk.OptionMenu(frame, layout_name_vatying, *listOfLayouts, command= lambda x: layoutOptionMenuCallback(layout_name_vatying))
        
        layouts_optionMenu.grid(row=0, column=0)
        
        return frame


    '''
    button to open the current full text in skim
    '''
    def getButton_OpenFullBook(mainWinRoot):
        screenHalfWidth, screenHeight = _u.getMonitorSize()
        screenHalfWidth = str(int(screenHalfWidth / 2))
        screenHeight = str(screenHeight)

        def openFullTextButtonCallback():
            wholeBookDimensions = ["0", "0", screenHalfWidth, screenHeight]
            layouts_main.openWholeBook([wholeBookDimensions[2], wholeBookDimensions[3]], [wholeBookDimensions[0], wholeBookDimensions[1]])
        
        openFullTextButtonText = tk.StringVar()
        openFullTextButtonText.set("Current book is :\n" +  _u.Settings.readProperty(_u.Settings.currBookName_ID))
        
        return tk.Button(mainWinRoot, name = "openFullBook_button", textvariable = openFullTextButtonText, width = 10, command = openFullTextButtonCallback)


    '''
    create a text widget with the current folder where the images are saved
    '''  
    class Screenshot:
        
        def getScreenshotLocation():
            if UItkVariables.scrshotPath.get() == "":
                return "Current screenshot dir: " + _u.getCurrentScreenshotDir()
            else:
                return "Current screenshot dir: " + UItkVariables.scrshotPath.get()


        def setScreenshotLoaction():
            UItkVariables.scrshotPath.set(_u.getCurrentScreenshotDir())


        @classmethod
        def getText_CurrentScreenshotDir(cls, mainWinRoot, namePref = ""):
            canvas= tk.Canvas(mainWinRoot,name = namePref.lower() + "_showCurrScreenshotLocation_text", width=520, height= 25)

            UItkVariables.scrshotPath = tk.StringVar()
            currScrshDir = UItkVariables.scrshotPath

            currScrshDir.set(cls.getScreenshotLocation())
            
            txt = canvas.create_text(30, 10, anchor="nw", text=currScrshDir.get())

            def on_change(varname, index, mode):
                canvas.itemconfigure(txt, text=cls.getScreenshotLocation())
            
            currScrshDir.trace_variable('w', on_change)

            return canvas


    class ChooseBookChapter:
        '''
        option menu to choose a book to open and work on
        '''
        @classmethod
        def getOptionsMenu_ChooseBook(cls, mainWinRoot, namePrefix = ""):
            def bookMenuChooseCallback(book_name):
                _u.Settings.updateProperty(_u.Settings.currBookPath_ID, _u.getPathToBooks() + \
                                            book_name.get() + \
                                            "/" + _u.Settings.wholeBook_ID + \
                                            "/" + _u.Settings.wholeBook_ID + ".pdf")


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
        def getOptionMenu_ChooseChapter(cls, mainWinRoot, namePrefix = ""):
            '''
            functions that retrun options menus for choosing chapter
            '''
            def chapterChoosingCallback(chapter):
                print("chapterChoosingCallback - switching to chapter: " + chapter.get())
                
                _u.Settings.updateProperty(_u.Settings.currChapter_ID , chapter.get())

                chapterImIndex = _u.ChaptersSettings.ChapterProperties.getCurrChapterImIndex()
                UItkVariables.imageGenerationEntryText.set(chapterImIndex)

                UIWidgets.Screenshot.setScreenshotLoaction()
                
                subchaptersList = cls._getSubchaptersListForCurrChapter()
                cls._updateOptionMenuOptionsList(mainWinRoot, "_chooseSubchapter_optionMenu", subchaptersList)
                currSubchapter = _u.ChaptersSettings.ChapterProperties.getChapterLatestSubchapter(_u.Settings.readProperty(_u.Settings.currChapter_ID)[2:])
                UItkVariables.subchapter.set(currSubchapter)
                _u.Settings.updateProperty(_u.Settings.currChapterFull_ID, subchaptersList[0])

                currLayoutClass = layouts_main.getCurrLayoutClass()
                currLayoutClass.pyAppHeight = mainWinRoot.winfo_height()
                currLayoutClass.set(mainWinRoot)
                layouts_main.moveWholeBookToChapter()


            chapter = tk.StringVar()
            chapter.set(_u.Settings.readProperty(_u.Settings.currChapter_ID))

            book_name = _u.Settings.readProperty(_u.Settings.currBookName_ID)

            pathToBooks = _u.getPathToBooks()
            chaptersList = []
            chaptersList.extend([i for i in os.listdir(pathToBooks + "/" + book_name) if i[:2]=="ch"])
            chaptersList.sort(key=lambda x: -1 if x[2:]=="" else int(x[2:]))
            
            frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_chooseChapter_optionMenu", background="Blue")
            chapter_menu = tk.OptionMenu(frame, chapter, *chaptersList, command= lambda x: chapterChoosingCallback(chapter))
            chapter_menu.grid(row = 0, column = 0)

            return frame


        def _updateOptionMenuOptionsList(mainWinRoot, menuID, newMenuOptions):

            def subchapterChoosingCallback(value):
                UItkVariables.subchapter.set(value)
                _u.ChaptersSettings.ChapterProperties.updateChapterLatestSubchapter(_u.Settings.readProperty(_u.Settings.currChapter_ID)[2:],
                                                                        value)
                _u.Settings.updateProperty(_u.Settings.currChapterFull_ID, value)


            for e in mainWinRoot.winfo_children():
                if menuID in e._name:
                    for om in e.winfo_children():
                        om['menu'].delete(0, 'end')
                        for choice in newMenuOptions:
                            om['menu'].add_command(label=choice, 
                                                command= lambda value=choice: subchapterChoosingCallback(value))
                            UItkVariables.subchapter.set(newMenuOptions[0])


        def _getSubchaptersListForCurrChapter():
            pathToBooks = _u.getPathToBooks()
            currChapter = _u.Settings.readProperty(_u.Settings.currChapter_ID)
            currBookName = _u.Settings.readProperty(_u.Settings.currBookName_ID)
            return [i[3:] for i in os.listdir(pathToBooks + "/" + currBookName + "/" + currChapter + "/" + _u.Settings.relToSubchapters_Path) if "ch_" in i]

       
        @classmethod
        def getOptionMenu_ChooseSubchapter(cls, mainWinRoot, namePrefix = ""):
            def subchapterChoosingCallback(subchapter):
                _u.ChaptersSettings.ChapterProperties.updateChapterLatestSubchapter(_u.Settings.readProperty(_u.Settings.currChapter_ID)[2:],
                                                                        subchapter.get())
                _u.Settings.updateProperty(_u.Settings.currChapterFull_ID, subchapter.get())
            

            UItkVariables.subchapter  = tk.StringVar()
            subchapter = UItkVariables.subchapter
            subchapter.set(_u.Settings.readProperty(_u.Settings.currChapterFull_ID))
            
            subchaptersList = cls._getSubchaptersListForCurrChapter()

            frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_chooseSubchapter_optionMenu", background="Blue")
            subchapter_menu = tk.OptionMenu(frame, subchapter, *subchaptersList, command= lambda x: subchapterChoosingCallback(subchapter))
            subchapter_menu.grid(row = 0, column = 0)
            return frame
    

    def getCheckboxes_TOC(mainWinRoot, namePrefix = ""):
        UItkVariables.createTOCVar = tk.IntVar()
        UItkVariables.createTOCVar.set(1)
        createTOC_CB = tk.Checkbutton(mainWinRoot, name = namePrefix.lower() + "_create_toc", text = "TOC cr",
                                    variable = UItkVariables.createTOCVar, onvalue = 1, offvalue = 0)
        UItkVariables.TOCWithImageVar = tk.IntVar()
        TOCWithImage_CB = tk.Checkbutton(mainWinRoot, name = namePrefix.lower() + "_toc_w_image",  text = "TOC w i",
                                    variable = UItkVariables.TOCWithImageVar, onvalue = 1, offvalue = 0)
        
        return createTOC_CB, TOCWithImage_CB


    def getImageGenerationRestart_BTN(mainWinRoot, namePrefix = ""):
        def restartBTNcallback():
            UItkVariables.buttonText.set("imNum")
            chapterImIndex = _u.ChaptersSettings.ChapterProperties.getCurrChapterImIndex()
            UItkVariables.imageGenerationEntryText.set(chapterImIndex)
        

        restart_BTN = tk.Button(mainWinRoot,
                                name = namePrefix.lower() + "_imageGenerationRestartBTN",
                                text= "restart", 
                                command = restartBTNcallback)
        
        return restart_BTN


    @classmethod
    def getAddImage_BTN(cls, mainWinRoot, prefixName = ""):
        def addImBTNcallback():
            currImID = str(int(_u.Settings.readProperty(_u.Settings.currImageID_ID)) - 1)
            currentSubchapter = _u.Settings.readProperty(_u.Settings.currChapterFull_ID)
            
            # screenshot
            imName = ""

            # get name of the image from the text field
            for w in mainWinRoot.winfo_children():
                if "_imageGeneration_" + cls.entryWidget_ID in w._name:
                    imName = w.get()
            
            extraImagePath = _u.getCurrentScreenshotDir() \
                                + currImID + "_" + currentSubchapter \
                                + "_" + imName
            
            if os.path.isfile(extraImagePath + ".png"):
                def takeScreencapture(savePath):
                    os.system("screencapture -ix " + savePath)
                    UItkVariables.needRebuild.set(True)
                cls.confirmationWindow("The file exists. Overrite?", takeScreencapture, extraImagePath + ".png")
            else:
                os.system("screencapture -ix " + extraImagePath + ".png")
                UItkVariables.needRebuild.set(True)

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


    '''
    create entry and process button for image generation
    '''
    @classmethod
    def getTextEntryButton_imageGeneration(cls, mainWinRoot, prefixName = ""):
        UItkVariables.imageGenerationEntryText = tk.StringVar()
        imageProcessingETR = tk.Entry(mainWinRoot, 
                                    width = 8,
                                    textvariable =  UItkVariables.imageGenerationEntryText,
                                    name=prefixName.lower() + "_imageGeneration_" + cls.entryWidget_ID)

        chapterImIndex = _u.ChaptersSettings.ChapterProperties.getCurrChapterImIndex()
        UItkVariables.imageGenerationEntryText.set(chapterImIndex)

        dataFromUser = [-1, -1, -1]
        UItkVariables.buttonText = tk.StringVar()

        def _storeInputDataAndChange(nextButtonName, f = lambda *args: None, i = 0):
            # NOTE: not sure what is going on but "dataFromUser" refused to clean 
            # so had to pass i to set the position explicitly and set it to [-1, -1, -1] before
            dataFromUser[i] = imageProcessingETR.get()
            f()
            UItkVariables.buttonText.set(nextButtonName)


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
tell application \"" + _u.Settings.skim_ID + "\"\n\
    tell document \"" + _u.Settings.readProperty(_u.Settings.currChapterFull_ID) + "_main.pdf" + "\"\n\
        delay 0.1\n\
        go to page " + str(dataFromUser[0]) + "\n\
        end tell\n\
end tell'"

            return scriptFile


        def _createTexForTheProcessedImage():
            currentSubchapter = _u.Settings.readProperty(_u.Settings.currChapterFull_ID)

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

            if UItkVariables.createTOCVar.get():
                if UItkVariables.TOCWithImageVar.get():
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
            _u.Settings.updateProperty(_u.Settings.currImageID_ID, dataFromUser[0])
            _u.Settings.updateProperty(_u.Settings.currLinkName_ID, dataFromUser[1])
            
            # POPULATE THE MAIN FILE
            t.TexFile._populateMainFile()
            
            
            # take a screenshot
            if os.path.isfile(imageAnscriptPath + ".png"):
                def takeScreencapture(savePath):
                    os.system("screencapture -ix " + savePath + ".png")
                    UItkVariables.needRebuild.set(True)
                        #create a sript associated with image
                    with open(savePath + ".sh", "w+") as f:
                        for l in _createImageScript():
                            f.write(l)
                    os.system("chmod +x " + savePath + ".sh")
                    #update curr image index for the chapter
                    nextImNum = str(int(dataFromUser[0]) + 1)
                    _u.ChaptersSettings.ChapterProperties.updateChapterImageIndex(_u.Settings.readProperty(_u.Settings.currChapter_ID)[2:],
                                                                        nextImNum)
                    _u.Settings.updateProperty(_u.Settings.currImageID_ID, nextImNum)
                    UItkVariables.imageGenerationEntryText.set(nextImNum)
                    UItkVariables.buttonText.set("imNum")
                
                cls.confirmationWindow("The file exists. Overrite?", takeScreencapture, imageAnscriptPath)
            else:
                os.system("screencapture -ix " + imageAnscriptPath + ".png")
                UItkVariables.needRebuild.set(True)
                #create a sript associated with image
                with open(imageAnscriptPath + ".sh", "w+") as f:
                    for l in _createImageScript():
                        f.write(l)
                os.system("chmod +x " + imageAnscriptPath + ".sh")
                #update curr image index for the chapter
                nextImNum = str(int(dataFromUser[0]) + 1)
                _u.ChaptersSettings.ChapterProperties.updateChapterImageIndex(_u.Settings.readProperty(_u.Settings.currChapter_ID)[2:],
                                                                    nextImNum)
                _u.Settings.updateProperty(_u.Settings.currImageID_ID, nextImNum)
                UItkVariables.imageGenerationEntryText.set(nextImNum)

        buttonNamesToFunc = {"imNum": lambda *args: UItkVariables.imageGenerationEntryText.set(""),
                            "imLink":_createTexForTheProcessedImage}
        buttonNames = list(buttonNamesToFunc.keys())
       
        UItkVariables.buttonText.set(buttonNames[0])

        def buttonCallback():
            for i in range(len(buttonNames)):
                if buttonNames[i] == UItkVariables.buttonText.get():
                    _storeInputDataAndChange(buttonNames[(i+1)%len(buttonNames)], 
                                            buttonNamesToFunc[buttonNames[i]], i)
                    break

        processButton = tk.Button(mainWinRoot, 
                                name = prefixName.lower() + "_imageGeneration_processButton",
                                textvariable = UItkVariables.buttonText, 
                                command= buttonCallback)
        
        return [imageProcessingETR, processButton]


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


    @classmethod
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
                currBookPath = _u.Settings.getBookFolderPath()
                with open(currBookPath + "/" + sections[0] + "/subchapters" + "/".join(subsections)) as f:
                    targetLines = f.readlines()

        
        createGlLinkBTN = tk.Button(mainWinRoot, text = "Create gl link", 
                            name = prefixName.lower() + "addGlobalLinkBTN",
                            command = addClLinkCallback)

        targetSections = tk.StringVar()
        createGlLinkETR = tk.Entry(mainWinRoot,
                                width = 5,
                                textvariable = targetSections,
                                name = prefixName.lower() + "addGlobalLink" + UIWidgets.entryWidget_ID)
        
        return createGlLinkBTN, createGlLinkETR


'''
chapters menu widgets
'''
class ChaptersUI:
    chaptersPrefix = "chaptersID"

    @classmethod
    def setChaptersUI(cls, mainWinRoot):
        chooseChapter_MenusBtn = cls.getButton_chooseChaptersMenusAndBack(mainWinRoot, cls.chaptersPrefix)
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
        
        UItkVariables.currCh = tk.StringVar()
        UItkVariables.currSubch = tk.StringVar()
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
    def getButton_chooseChaptersMenusAndBack(cls, mainWinRoot, prefixName = ""):
        def chooseChaptersMenusAndBackCallback():
            # hide all of the menus
            UIWidgets.hideAllWidgets(mainWinRoot)

            if UIWidgets.showChapterWidgets:
                mainWinRoot.columnconfigure(0, weight = 1)
                mainWinRoot.columnconfigure(1, weight = 3)
                mainWinRoot.columnconfigure(2, weight = 1)
                mainWinRoot.columnconfigure(3, weight = 3)
                
                for w in mainWinRoot.winfo_children():
                    if cls.chaptersPrefix.lower() in w._name:
                        w.grid()
                chooseChapter_MenusBtn_Label.set("chapters")
                UIWidgets.showChapterWidgets = not UIWidgets.showChapterWidgets
            else:
                mainWinRoot.columnconfigure(0, weight = 1)
                mainWinRoot.columnconfigure(1, weight = 1)
                mainWinRoot.columnconfigure(2, weight = 1)
                mainWinRoot.columnconfigure(2, weight = 0)
                UIWidgets.showCurrentLayout(mainWinRoot)  
                chooseChapter_MenusBtn_Label.set("layout") 
                UIWidgets.showChapterWidgets = not UIWidgets.showChapterWidgets

        
        # show getBack Button
        chooseChapter_MenusBtn_Label = tk.StringVar()
        chooseChapter_MenusBtn_Label.set("chapters") 
        chooseChapter_MenusBtn = tk.Button(mainWinRoot, name = prefixName.lower() + "_chooseChapterLayoutBtn", textvariable = chooseChapter_MenusBtn_Label, command = chooseChaptersMenusAndBackCallback)
        
        return chooseChapter_MenusBtn


    @classmethod
    def getEntries_currChAndSubchapter(cls, mainWinRoot, prefixName = ""):
        currCh_ETR = tk.Entry(mainWinRoot, 
                            width = 5,
                            textvariable = UItkVariables.currCh, 
                            name = prefixName.lower() +  "_setCurrChapter_" + UIWidgets.entryWidget_ID)
        currSubch_ETR = tk.Entry(mainWinRoot, 
                            width = 5, 
                            textvariable = UItkVariables.currSubch, 
                            name = prefixName.lower() +  "_setCurrSubchapter_" + UIWidgets.entryWidget_ID)
        
        return currCh_ETR, currSubch_ETR


    @classmethod
    def getWidgets_setChapterName(cls, mainWinRoot, prefixName = ""):
        entry_setChapterName = tk.Entry(mainWinRoot, name = prefixName.lower() +  "_setChapterName_" + UIWidgets.entryWidget_ID)
        button_setChapterName = tk.Button(mainWinRoot, name = prefixName.lower() +  "_setChapterNameBTN", text="setChapterName", command = lambda *args: ChaptersUI.ChapterProperties.updateChapterName(UItkVariables.currCh.get(), entry_setChapterName.get()))
        
        return entry_setChapterName, button_setChapterName            


    @classmethod
    def getWidgets_setChapterStartPage(cls, mainWinRoot, prefixName = ""):
        entry_setChapterStartPage = tk.Entry(mainWinRoot, name = prefixName.lower() +  "_setChapterStartPage_" + UIWidgets.entryWidget_ID)
        button_setChapterStartPage = tk.Button(mainWinRoot, name = prefixName.lower() + "_setChapterStartPageBTN", text="setChapterStartPage", command = lambda *args: ChaptersUI.ChapterProperties.updateChapterStartPage(UItkVariables.currCh.get(), entry_setChapterStartPage.get()))
        
        return entry_setChapterStartPage, button_setChapterStartPage 


    @classmethod
    def getWidgets_setSubchapterName(cls, mainWinRoot, prefixName = ""):
        entry_setSubchapterName = tk.Entry(mainWinRoot, name = prefixName.lower() + "_setSubchapterName_" + UIWidgets.entryWidget_ID)
        button_setSubchapterName = tk.Button(mainWinRoot, name = prefixName.lower() + "_setSubchapterNameBTN", text="setSubhapterName", command = lambda *args: ChaptersUI.SubchaptersProperties.updateSubchapterName(UItkVariables.currSubch.get(), entry_setSubchapterName.get()))
        
        return entry_setSubchapterName, button_setSubchapterName


    @classmethod
    def getWidgets_setSubchapterStartPage(cls, mainWinRoot, prefixName = ""):
        entry_setSubchapterStartpage = tk.Entry(mainWinRoot, name = prefixName.lower() + "_setSubchapterStartPage_" + UIWidgets.entryWidget_ID)
        button_setSubchapterStartPage = tk.Button(mainWinRoot, name = prefixName.lower() + "_setSubchapterStartPageBTN", text="setSubhapterStartName", command = lambda *args : ChaptersUI.SubchaptersProperties.updateSubchapterStartPage(UItkVariables.currSubch.get(), entry_setSubchapterStartpage.get()))
        
        return entry_setSubchapterStartpage, button_setSubchapterStartPage


    @classmethod
    def getButton_createNewChapter(cls, mainWinRoot, prefixName = ""):
        def createNewChapterBTNcallback():
            chNum = None
            chName = None
            chStartPage = None
            for e in mainWinRoot.winfo_children():
                if  "_setCurrChapter_" + UIWidgets.entryWidget_ID in e._name:
                    chNum = e.get()
                elif "_setChapterName_" + UIWidgets.entryWidget_ID in e._name:
                    chName = e.get()
                elif "_setChapterStartPage_" + UIWidgets.entryWidget_ID in e._name:
                    chStartPage = e.get()
            _u.ChaptersSettings.ChapterProperties.addChapter(chNum, chName, chStartPage)
        
        return tk.Button(mainWinRoot, name = prefixName.lower() + "_createNewChapterBTN", text="New", command = createNewChapterBTNcallback)
    

    @classmethod
    def getButton_removeChapter(cls, mainWinRoot, prefixName = ""):
        def removeBTNcallback():
            chNum = None
            for e in mainWinRoot.winfo_children():
                if  "_setCurrChapter_" + UIWidgets.entryWidget_ID in e._name:
                    chNum = e.get()
                    break
            _u.ChaptersSettings.ChapterProperties.removeChapter(chNum)
        
        return tk.Button(mainWinRoot, name = prefixName.lower() + "_removeChapterBTN", text="Del", command = removeBTNcallback)
    

    @classmethod
    def getButton_createNewSubchapter(cls, mainWinRoot, prefixName = ""):
        def createNewChapterBTNcallback():
            chNum = None
            subchNum = None
            subchName = None
            subchStartPage = None
            for e in mainWinRoot.winfo_children():
                if  "_setCurrSubchapter_" + UIWidgets.entryWidget_ID in e._name:
                    subchNum = e.get()
                    chNum = subchNum.split(".")[0]
                elif "_setSubchapterName_" + UIWidgets.entryWidget_ID in e._name:
                    subchName = e.get()
                elif "_setSubchapterStartPage_" + UIWidgets.entryWidget_ID in e._name:
                    subchStartPage = e.get()
            
            _u.ChaptersSettings.SubchaptersProperties.addSubchapter(chNum, subchNum, subchName, subchStartPage)
        
        return tk.Button(mainWinRoot, 
                        name = prefixName.lower() + "_createNewSubchapterBTN", 
                        text="New", 
                        command = createNewChapterBTNcallback)


    @classmethod
    def getButton_removeSubchapter(cls, mainWinRoot, prefixName = ""):
        def removeBTNcallback():
            chNum = None
            for e in mainWinRoot.winfo_children():
                if  "_setCurrSubchapter_" + UIWidgets.entryWidget_ID in e._name:
                    subchNum = e.get()
                    chNum = subchNum.split(".")[0]
            
            _u.ChaptersSettings.SubchaptersProperties.removeSubchapter(chNum, subchNum)
        
        return tk.Button(mainWinRoot, 
                        name = prefixName.lower() + "_removeSubchapterBTN", 
                        text="Del", 
                        command = removeBTNcallback)

