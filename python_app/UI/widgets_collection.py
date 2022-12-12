import os
import subprocess
import tkinter as tk
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


def getImageGenerationRestart_BTN(mainWinRoot, namePrefix = ""):
    def restartBTNcallback():
        wv.UItkVariables.buttonText.set("imNum")
        sectionImIndex = fsm.Wr.Links.ImIDX.get_curr()
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
        with open(fsm.Wr.Paths.TexFiles.Content.getAbs_curr(),"r") as conF:
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
                            log.autolog("\nHiding the proof for line:\n" + contentLines[i])
                        else:
                            contentLines[i] = "% " + line
                            log.autolog("\nShow the proof for line:\n" + contentLines[i])
                    break
        with open(fsm.Wr.Paths.TexFiles.Content.getAbs_curr(),"w") as conF:
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
        currentSubsection = fsm.Wr.SectionCurrent.readCurrSection()
        currImID = fsm.Wr.Links.ImIDX.get_curr()
        
        # screenshot
        imName = ""

        # get name of the image from the text field
        for w in mainWinRoot.winfo_children():
            if "_imageGeneration_" + wu.Data.ENT.entryWidget_ID in w._name:
                imName = w.get()
        
        extraImagePath = fsm.Wr.Paths.Screenshot.getAbs_curr() \
                            + currImID + "_" + currentSubsection \
                            + "_" + imName
        
        if os.path.isfile(extraImagePath + ".png"):
            def takeScreencapture(savePath):
                os.system("screencapture -ix " + savePath)
                wv.UItkVariables.needRebuild.set(True)
            wmes.ConfirmationMenu.createMenu("The file exists. Overrite?", 
                                            takeScreencapture, 
                                            extraImagePath + ".png")
        else:
            os.system("screencapture -ix " + extraImagePath + ".png")
            wv.UItkVariables.needRebuild.set(True)

        # update the content file
        marker = "THIS IS CONTENT id: " + currImID
        with open(fsm.Wr.Paths.TexFiles.Content.getAbs_curr(), "r+") as f:
            contentLines = f.readlines()
            lineNum = [i for i in range(len(contentLines)) if marker in contentLines[i]][0]
            extraImagesMarker = "% \\EXTRA IMAGES END"
            while extraImagesMarker not in contentLines[lineNum]:
                lineNum += 1
            outLines = contentLines[:lineNum]
            extraImageLine = "\\\\\myStIm{" + extraImagePath + "}\n"
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
    def addLinkToTexFile(imIDX, scriptPath, linkName, contenfFilepath):
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
        
        lineToAdd = "        \href{file:" + scriptPath + "}{" + linkName + "}\n"
        outlines = lines[:positionToAdd]
        outlines.append(lineToAdd)
        outlines.extend(lines[positionToAdd:])
        
        with open(contenfFilepath, "+w") as f:
            for line in outlines:
                f.write(line + "\n")


    def addGlLinkCallback():
        bookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
        secPrefix = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_prefix_ID)
        
        sourceSectionPath = fsm.Wr.SectionCurrent.getSectionNameNoPrefix()
        sourceSectionNameWprefix = fsm.Wr.SectionCurrent.getSectionNameWprefix()
        sourceLinkName = wv.UItkVariables.glLinkSourceImLink.get()
        sourceIDX = fsm.Wr.Links.LinkDict.get(sourceSectionPath)[sourceLinkName]
        sourceSectionFilepath = fsm.Wr.Paths.Section.getAbs(bookPath, sourceSectionPath)
        sourceContentFilepath = fsm.Wr.Paths.TexFiles.Content.getAbs(bookPath, sourceSectionNameWprefix)
        sourceMainFilepath = fsm.Wr.Paths.TexFiles.Main.getAbs(bookPath, sourceSectionNameWprefix)
        sourceTOCFilepath = fsm.Wr.Paths.TexFiles.TOC.getAbs(bookPath, sourceSectionNameWprefix)
        sourcePDFFilepath = fsm.Wr.Paths.PDF.getAbs(bookPath, sourceSectionNameWprefix)
        sourcePDFFilename = sourcePDFFilepath.split("/")[-1]
        
        targetSectionPath = wv.UItkVariables.glLinktargetSections.get()
        targetSectionNameWprefix = secPrefix + "_" + targetSectionPath
        targetLinkName = wv.UItkVariables.glLinkTargetImLink.get()
        targetIDX = fsm.Wr.Links.LinkDict.get(targetSectionPath)[targetLinkName]
        targetSectionFilepath = fsm.Wr.Paths.Section.getAbs(bookPath, targetSectionPath)
        targetContentFilepath = fsm.Wr.Paths.TexFiles.Content.getAbs(bookPath, targetSectionNameWprefix)
        targetMainFilepath = fsm.Wr.Paths.TexFiles.Main.getAbs(bookPath, targetSectionNameWprefix)
        targetTOCFilepath = fsm.Wr.Paths.TexFiles.TOC.getAbs(bookPath, targetSectionNameWprefix)
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

        #
        # Create the link script
        #
        sDirPath = fsm.Wr.Paths.Scripts.Links.Global.getAbs(bookPath, sourceSectionNameWprefix)
        sName = sourceSectionPath + "_" + sourceIDX + "." + sourceLinkName + "__" \
            + targetSectionPath + "_" + targetIDX + "." + targetLinkName + ".sh"
        sPath = os.path.join(sDirPath, sName)
        with open(sPath , "w+") as f:
            for line in fsm.Wr.Links.LinkDict.getGlobalLinkScriptLines(targetIDX, 
                                                            targetPDFFilename,
                                                            targetPDFFilepath):
                f.write(line)
        log.autolog("Hippo" + sPath)
        os.system("chmod +rwx " + sPath)

        addLinkToTexFile(sourceIDX, 
                        sPath, 
                        targetSectionPath + "\_" + targetLinkName,
                        sourceContentFilepath)

        # add return link 
        
        returnScriptDirPath = fsm.Wr.Paths.Scripts.Links.Global.getAbs(bookPath, targetSectionNameWprefix)
        returnScriptName = targetSectionPath + "_" + targetIDX + "." + targetLinkName + "__" \
                        + sourceSectionPath + "_" + sourceIDX + "." + sourceLinkName +  ".sh"
        returnSctiptPath = os.path.join(returnScriptDirPath, returnScriptName)
        with open(returnSctiptPath , "w+") as f:
            for line in fsm.Wr.Links.LinkDict.getGlobalLinkScriptLines(sourceIDX,
                                                            sourcePDFFilename,
                                                            sourcePDFFilepath):
                f.write(line)
        log.autolog("Hoppo" + returnSctiptPath)
        os.system("chmod +rwx " + returnSctiptPath)

        addLinkToTexFile(targetIDX, 
                        returnSctiptPath, 
                        sourceSectionPath + "\_" + sourceLinkName,
                        targetContentFilepath)

        #
        # rebuild the pdfs
        #
        t.Wr.TexFile.buildSubsectionPdf(sourceSectionFilepath,
                                        sourceMainFilepath,
                                        sourceSectionNameWprefix)
        t.Wr.TexFile.buildSubsectionPdf(targetSectionFilepath,
                                        targetMainFilepath,
                                        targetSectionNameWprefix)

    createGlLinkBTN = tk.Button(mainWinRoot, text = "Create gl link", 
                        name = prefixName.lower() + "_addGlobalLink" + "BTN",
                        command = addGlLinkCallback)

    createGlLinkETR = tk.Entry(mainWinRoot,
                            width = 5,
                            textvariable = wv.UItkVariables.glLinktargetSections,
                            name = prefixName.lower() + "_addGlobalLink" + wu.Data.ENT.entryWidget_ID)
    
    return createGlLinkBTN, createGlLinkETR


def getWidgets_imageGeneration_ETR_BTN(mainWinRoot, prefixName = ""):
    secImIndex = fsm.Wr.Links.ImIDX.get_curr()
    if secImIndex == _u.Token.NotDef.str_t:
        wv.UItkVariables.imageGenerationEntryText.set("-1")
    else:
        wv.UItkVariables.imageGenerationEntryText.set(str(int(secImIndex) + 1))
    
    imageProcessingETR = tk.Entry(mainWinRoot, 
                                width = 8,
                                textvariable =  wv.UItkVariables.imageGenerationEntryText,
                                name=prefixName.lower() + "_imageGeneration_" + wu.Data.ENT.entryWidget_ID)

    dataFromUser = [-1, -1]

    def _storeInputDataAndChange(nextButtonName, f = lambda *args: None, i = 0):
        # NOTE: not sure what is going on but "dataFromUser" refused to clean 
        # so had to pass i to set the position explicitly and set it to [-1, -1, -1] before
        dataFromUser[i] = imageProcessingETR.get()
        f()
        wv.UItkVariables.buttonText.set(nextButtonName)


    def _createTexForTheProcessedImage():
        currsubsection = fsm.Wr.SectionCurrent.readCurrSection()

        extraImagePath = os.path.join(fsm.Wr.Paths.Screenshot.getAbs_curr(),
                                    dataFromUser[0] + "_" + currsubsection + "_" + dataFromUser[1])

        # ADD CONTENT ENTRY TO THE PROCESSED CHAPTER
        with open(fsm.Wr.Paths.TexFiles.Content.getAbs_curr(), 'a') as f:
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
                with open(fsm.Wr.Paths.TexFiles.TOC.getAbs_curr(), 'a') as f:
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
                with open(fsm.Wr.Paths.TexFiles.TOC.getAbs_curr(), 'a') as f:
                    toc_add_text = "\
% THIS IS CONTENT id: " + dataFromUser[0] + " \n\
\\mybox{\n\
    \\link[" + dataFromUser[0] + "]{" + dataFromUser[1] + "} \\textbf{!}\n\
}\n\n\n"
                    f.write(toc_add_text)
            

        #create a script to run on page change
        imagePath = os.path.join(fsm.Wr.Paths.Screenshot.getAbs_curr(),
                                dataFromUser[0] + "_" + currsubsection + "_" + dataFromUser[1])
        scriptPath = os.path.join(fsm.Wr.Paths.Scripts.Links.Local.getAbs_curr(),
                                dataFromUser[0] + "_" + currsubsection + "_" + dataFromUser[1])

        # STOTE IMNUM, IMNAME AND LINK
        fsm.Wr.SectionCurrent.setImLinkAndIDX(dataFromUser[1], dataFromUser[0])
        
        # POPULATE THE MAIN FILE
        t.Wr.TexFile._populateMainFile()
        
        
        # take a screenshot
        imIDX = dataFromUser[0]
        contentFilepath = fsm.Wr.Paths.TexFiles.Content.getAbs_curr()
        tocFilepath = fsm.Wr.Paths.TexFiles.TOC.getAbs_curr()
        pdfName = fsm.Wr.SectionCurrent.getSectionPdfName()
        pdfFilepath = fsm.Wr.Paths.PDF.getAbs_curr()
        if os.path.isfile(imagePath + ".png"):
            def takeScreencapture(iPath, sPath):
                os.system("screencapture -ix " + iPath + ".png")
                wv.UItkVariables.needRebuild.set(True)
                # create a sript associated with page
                with open(sPath + ".sh", "w+") as f:
                    lines = fsm.Wr.Links.LinkDict.getLocalLinkScriptLines(imIDX, 
                                                                    contentFilepath, 
                                                                    tocFilepath, 
                                                                    pdfName,
                                                                    pdfFilepath)
                    for line in lines:
                        f.write(line)
                os.system("chmod +x " + sPath + ".sh")
                # update curr image index for the chapter
                nextImNum = str(int(dataFromUser[0]) + 1)
                wv.UItkVariables.imageGenerationEntryText.set(nextImNum)
                wv.UItkVariables.buttonText.set("imNum")
            
            wmes.ConfirmationMenu.createMenu("The file exists. Overrite?", 
                                            takeScreencapture, 
                                            imagePath, 
                                            scriptPath,
                                            pdfFilepath)
        else:
            os.system("screencapture -ix " + imagePath + ".png")
            wv.UItkVariables.needRebuild.set(True)
            #create a sript associated with image
            with open(scriptPath + ".sh", "w+") as f:
                lines = fsm.Wr.Links.LinkDict.getLocalLinkScriptLines(imIDX, 
                                                                contentFilepath, 
                                                                tocFilepath, 
                                                                pdfName,
                                                                pdfFilepath)
                for line in lines:
                    f.write(line)
            os.system("chmod +x " + scriptPath + ".sh")
            #update curr image index for the chapter
            nextImNum = str(int(dataFromUser[0]) + 1)
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
        cmd = "osascript -e '\n\
tell application \"" + _u.Settings._appsIDs.skim_ID + "\" to return name of front document\n\
'"
        frontSkimDocumentName = str(subprocess.check_output(cmd, shell=True))
        
        # get subsection and top section from it
        frontSkimDocumentName = frontSkimDocumentName.replace("\\n", "")
        frontSkimDocumentName = frontSkimDocumentName.split("_")[1]
        topSection = frontSkimDocumentName.split(".")[0]
        subsection = frontSkimDocumentName
        
        cmd = "osascript -e '\n\
tell application \"" + _u.Settings._appsIDs.skim_ID + "\" to return current page of front document\n\
'"
        imIDX = int(str(subprocess.check_output(cmd, shell=True)).split(" ")[1])

        # close current section vscode
        _, windowID = _u.getOwnersName_windowID_ofApp(
                            "vscode",
                             fsm.Wr.SectionCurrent.readCurrSection())
        
        if (windowID != None):
            osascript = "osascript -e '\
    tell application \"System Events\" to tell process \""  + _u.Settings._appsIDs.vsCode_ID + "\"\n\
	    tell window " + windowID + "\n\
            click button 1\n\
	    end tell\n\
    end tell'"
            os.system(osascript)

        #change the current subsection for the app
        fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.currTopSection_ID, topSection)
        fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.currSection_ID, subsection)
        
        mon_width, _ = _u.getMonitorSize()
        width = int(mon_width / 2)
        height = 70
        lm.Wr.SectionLayout.set(mainWinRoot, width, height)
        currChImageLinks = fsm.Wr.Links.LinkDict.getCurrImLinksSorted(subsection)
        wu.updateOptionMenuOptionsList(mainWinRoot, 
                                    "source_SecImIDX", 
                                    currChImageLinks,
                                    wv.UItkVariables.glLinkSourceImLink,
                                    lambda *argv: None)
        wv.UItkVariables.glLinkSourceImLink.set(currChImageLinks[-1])
        
        #move run susection script to move to desired position
        localScriptsDir = fsm.Wr.Paths.Scripts.Links.Local.getAbs_curr()

        sctiptPath = os.path.join(localScriptsDir, str(imIDX) + "*" + currChImageLinks[imIDX - 1] + "*.sh")
        log.autolog("running script: " + sctiptPath)
        os.system("chmod +rwx " + sctiptPath)
        os.system(sctiptPath)

    return tk.Button(mainWinRoot, 
                    name = prefixName + "_changeSubsection",
                    text = "change subsecttion",
                    command = callback)


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
            
            # update the image links om
            def updateImLinksOM(secPath):
                if secPath != "":
                    currChImageLinks = fsm.Wr.Links.LinkDict.getCurrImLinksSorted(secPath)
                    wu.updateOptionMenuOptionsList(winMainRoot, 
                                                "target_SecImIDX", 
                                                currChImageLinks,
                                                wv.UItkVariables.glLinkTargetImLink,
                                                lambda *argv: None)
                    wv.UItkVariables.glLinkTargetImLink.set(currChImageLinks[-1])
            
            createGlLinkETR.bind('<Return>',
                                lambda e: updateImLinksOM(wv.UItkVariables.glLinktargetSections.get()))
            
            targetImageLinksOM = getTargetImageLinks_OM(winMainRoot, cls.classPrefix)
            targetImageLinksOM.grid(column=5, row=2, padx=0, pady=0)

            currSection = fsm.Wr.SectionCurrent.readCurrSection()
            sourceImageLinksOM = getSourceImageLinks_OM(winMainRoot, cls.classPrefix, currSection)
            sourceImageLinksOM.grid(column=4, row=2, padx=0, pady=0)

            changeSection_BTN = getChangeSubsectionToTheFront(winMainRoot, cls.classPrefix)
            changeSection_BTN.grid(column=0, row=2, padx=0, pady=0)

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
            # layout: 
            #
            layoutOM = LayoutsMenus._commonWidgets.getOptionsMenu_Layouts(winMainRoot, cls.classPrefix)
            layoutOM.grid(column = 1, row = 0, padx = 0, pady = 0)

            #
            # image generation:
            #
            imageGenerationUI = getWidgets_imageGeneration_ETR_BTN(winMainRoot, cls.classPrefix)
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
            currScrShotDirText = \
                wu.Screenshot.getText_CurrentScreenshotDirWidget(winMainRoot, cls.classPrefix)
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
                        
                        if "section" in cl.__name__.lower():
                            currSection = fsm.Wr.SectionCurrent.readCurrSection()
                            currChImageLinks = fsm.Wr.Links.LinkDict.getCurrImLinksSorted(currSection)
                            wu.updateOptionMenuOptionsList(mainWinRoot, 
                                                        "source_SecImIDX", 
                                                        currChImageLinks,
                                                        wv.UItkVariables.glLinkSourceImLink,
                                                        lambda *argv: None)
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
    
    @classmethod
    def _topSectionChoosingCallback(cls, mainWinRoot):
        log.autolog("switching to top section: " + wv.UItkVariables.topSection.get())

        # update top section
        fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.currTopSection_ID , 
                                                wv.UItkVariables.topSection.get())
        
        # update subsection
        sections = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_ID)
        prevSubsectionPath = sections[wv.UItkVariables.topSection.get()]["prevSubsectionPath"]
        fsm.Wr.BookInfoStructure.updateProperty(fsm.PropIDs.Book.currSection_ID, prevSubsectionPath)

        # update image index
        secionImIndex = fsm.Wr.Links.ImIDX.get(prevSubsectionPath)
        wv.UItkVariables.imageGenerationEntryText.set(secionImIndex)         
        

        subsectionsList = wu.getSubsectionsListForCurrTopSection()
        subsectionsList.sort()
        
        #
        # Update other widgets
        #

        # subsection option menu widget
        wu.updateOptionMenuOptionsList(mainWinRoot, 
                                        "_chooseSubsecion_optionMenu", 
                                        subsectionsList, 
                                        wv.UItkVariables.subsection,
                                        cls._subsectionChoosingCallback)        
        wv.UItkVariables.subsection.set(prevSubsectionPath)

        # update screenshot widget
        wu.Screenshot.setValueScreenshotLoaction()

        # update image index widget
        wv.UItkVariables.imageGenerationEntryText.set(fsm.Wr.Links.ImIDX.get(wv.UItkVariables.subsection.get()))

        # update Layout widget
        widgetDimensions = LayoutsMenus.MainLayoutUI.pyAppDimensions
        lm.Wr.MainLayout.set(mainWinRoot, *widgetDimensions)

    @classmethod
    def getOptionMenu_ChooseTopSection(cls, mainWinRoot, namePrefix = ""):
        '''
        functions that retrun options menus for choosing chapter
        '''
        wv.UItkVariables.topSection.set(
            fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currTopSection_ID)
        )

        topSectionsList = fsm.getTopSectionsList()
        topSectionsList.sort(key = int)

        frame = tk.Frame(mainWinRoot, 
                        name = namePrefix.lower() + "_chooseSection_optionMenu", 
                        background = "Blue")
        
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
        
        wv.UItkVariables.imageGenerationEntryText.set(fsm.Wr.Links.ImIDX.get(subsection.get()))

        wu.Screenshot.setValueScreenshotLoaction()
        
        # update Layout
        widgetDimensions = LayoutsMenus.MainLayoutUI.pyAppDimensions
        lm.Wr.MainLayout.set(mainWinRoot, *widgetDimensions)

        

    @classmethod
    def getOptionMenu_ChooseSubsection(cls, mainWinRoot, namePrefix = ""):
        subsection =wv.UItkVariables.subsection
        subsection.set(fsm.Wr.SectionCurrent.readCurrSection())
        
        subsectionsList = wu.getSubsectionsListForCurrTopSection()


        frame = tk.Frame(mainWinRoot, 
                        name = namePrefix.lower() + "_chooseSubsecion_optionMenu", 
                        background="Blue")
        
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
    def getButton_chooseSectionsMenusAndBack(cls, mainWinRoot, prefixName = ""):
        def chooseChaptersMenusAndBackCallback():
            # hide all of the menus
            wu.hideAllWidgets(mainWinRoot)
            if not _u.Settings.UI.showMainWidgetsNext:
                mainWinRoot.columnconfigure(0, weight = 1)
                mainWinRoot.columnconfigure(1, weight = 1)
                mainWinRoot.columnconfigure(2, weight = 3)
                mainWinRoot.columnconfigure(3, weight = 1)
                
                # show the sections UI
                for w in mainWinRoot.winfo_children():
                    if cls.sectionsPrefix.lower() in w._name:
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

