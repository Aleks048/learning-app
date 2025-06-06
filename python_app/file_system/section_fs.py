import os
from threading import Thread
import time
import re

import file_system.book_fs as bfs
import file_system.entry_fs as efs
import file_system.links as l
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import _utils.logging as log
import outside_calls.outside_calls_facade as ocf
import settings.facade as sf
import data.temp as dt
import tex_file.tex_file_facade as tff
import generalManger.generalManger as gm

class SectionInfoStructure:
    '''
    Structure to store sections and .tex files and images
    '''

    currStucturePath = ""

    # for later: add if the section should generate the pdf.
    # currPage = "currentPage"
    # currImageID = "currImageID"
    # currImageName = "currImageName"
    # currLinkName = "currLinkName"

    class PubProp:
        name = "_name"
        latestSubchapter = "_latestSubchapter"
        subSections = "_subSections"

        #subsection summary
        subsectionSummaryText = "_subsectionSummary"

        #imagesProperties
        imageProp = "_imageProp"
        imageContentFileMoveLinesNumber = "_imageContentFileMoveLinesNumber"
        imageTOCFileMoveLinesNumber = "_imageContentFileMoveLinesNumber"
        imLinkDict = "imLinkDict"
        imLinkOMPageDict = "imLinkOMPageDict"
        imGlobalLinksDict = "imGlobalLinksDict"
        origMatNameDict = "origMatNameDict"
        extraImagesDict = "extraImagesDict"
        tocWImageDict = "tocWImageDict"
        imagesGroupDict = "imagesGroupDict"
        imageUIResize = "imageUIResize"
        imageText = "imageText"
        extraImText = "extraImText"
        textOnly = "textOnly"

        # link to note taking app
        notesAppLink = "_notesAppLink"

        # TOC properties
        text = "TOC_text"
        start = "TOC_sectionStart"
        finish = "TOC_sectionFinish"

        #list of image groups
        imagesGroupsList = "imagesGroupsList"

        level = "_level"
        levelData = "_levelData"

        # image figures data
        figuresData = "_figuresData"
        figuresLabelsData = "_figuresLabelsData"

        # code data
        bookCodeFile = "_bookCodeFile"
        subsectionCodeFile = "_subsectionCodeFile"

        #wiki pages
        wikiPages = "_wikiPages"
        #isVideo
        isVideo = "_isVideo"
        videoPosition = "_videoPosition"

        #leading entry
        leadingEntry = "_leadingEntry"
        showSubentries = "_showSubentries"

    class PrivProp:
        tocData = "_tocData"

    sectionPrefixForTemplate = ""
    sectionPathForTemplate = ""

    @classmethod
    def _getTemplate(cls, level = 0):
        sectionInfo_template = {
            cls.PubProp.name: _u.Token.NotDef.str_t,
            cls.PubProp.latestSubchapter: _u.Token.NotDef.str_t,
            cls.PubProp.notesAppLink: _u.Token.NotDef.str_t,
            cls.PubProp.subsectionSummaryText: _u.Token.NotDef.str_t,
            cls.PubProp.isVideo: False,
            cls.PubProp.imagesGroupsList: {"No group": True},
            cls.PubProp.levelData: {
                cls.PubProp.level: str(level),
            },
            cls.PrivProp.tocData: {
                cls.PubProp.text: _u.Token.NotDef.str_t,
                cls.PubProp.start: _u.Token.NotDef.str_t,
                cls.PubProp.finish: _u.Token.NotDef.str_t
            },
            cls.PubProp.imageProp: {
                cls.PubProp.imageContentFileMoveLinesNumber: _u.Token.NotDef.str_t,
                cls.PubProp.imageTOCFileMoveLinesNumber: _u.Token.NotDef.str_t,
                cls.PubProp.imLinkDict: _u.Token.NotDef.dict_t.copy(),
                cls.PubProp.imLinkOMPageDict: _u.Token.NotDef.dict_t.copy(),
                cls.PubProp.imGlobalLinksDict: _u.Token.NotDef.dict_t.copy(),
                cls.PubProp.origMatNameDict : _u.Token.NotDef.dict_t.copy(),
                cls.PubProp.extraImagesDict : _u.Token.NotDef.dict_t.copy(),
                cls.PubProp.tocWImageDict : _u.Token.NotDef.dict_t.copy(),
                cls.PubProp.imagesGroupDict : _u.Token.NotDef.dict_t.copy(),
                cls.PubProp.imageUIResize : _u.Token.NotDef.dict_t.copy(),
                cls.PubProp.imageText : _u.Token.NotDef.dict_t.copy(),
                cls.PubProp.extraImText : _u.Token.NotDef.dict_t.copy(),
                cls.PubProp.textOnly : _u.Token.NotDef.dict_t.copy(),
                cls.PubProp.figuresData : _u.Token.NotDef.dict_t.copy(),
                cls.PubProp.figuresLabelsData : _u.Token.NotDef.dict_t.copy(),
                cls.PubProp.bookCodeFile : _u.Token.NotDef.dict_t.copy(),
                cls.PubProp.subsectionCodeFile : _u.Token.NotDef.dict_t.copy(),
                cls.PubProp.wikiPages:  _u.Token.NotDef.dict_t.copy(),
                cls.PubProp.videoPosition:  _u.Token.NotDef.dict_t.copy(),
                cls.PubProp.leadingEntry:  _u.Token.NotDef.dict_t.copy(),
                cls.PubProp.showSubentries:  _u.Token.NotDef.dict_t.copy()
            }
        }
        return sectionInfo_template

    @classmethod
    def getDefaultTemplateValue(cls, propertyName):
        template = cls._getTemplate()
        for k,v in template.items():
            if k == propertyName:
                return template[k] , ""
            if type(v) == dict:
                for k2,_ in v.items():
                    if k2 == propertyName:
                        return v[k2], k

    def getSectionJSONKeyPrefixFormPath(path):
        sectionPathSeparator = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator) 
        secPrefix = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix)
        return secPrefix + "_" + path.replace(sectionPathSeparator, "_")   

    def createStructure(bookName):
        subsectionPath = _upan.Paths.Section.getBaseAbs(bookName)
        ocf.Wr.FsAppCalls.createDir(subsectionPath)
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.currSection,
                                            _u.Token.NotDef.str_t)
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.currTopSection, 
                                            _u.Token.NotDef.str_t)
        return

    @classmethod
    def __createSubsectionFiles(cls, bookpath, sectionPath):
        dirPathToSection_curr = _upan.Paths.Section.getAbs(bookpath, sectionPath)

        sectionPathSeparator = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator) 

        depth = len(sectionPath.split(sectionPathSeparator))

        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(dirPathToSection_curr):
            msg = "The sections structure was not present will create it.\n" + \
                    "Creating path: '{0}'".format(dirPathToSection_curr)
            log.autolog(msg)
            
            # create folders
            _waitDummy = ocf.Wr.FsAppCalls.createDir(dirPathToSection_curr)
            sectionJSONfilepath = _upan.Paths.Section.JSON.getAbs(bookpath, sectionPath)

            with open(sectionJSONfilepath, "w+") as f:
                jsonObj = _u.json.dumps(cls._getTemplate(depth), indent = 4)
                f.write(jsonObj)

            # create images folder
            imagesFolderFSPath = \
                ocf.Wr.FsAppCalls.createDir(_upan.Paths.Screenshot.getAbs(bookpath, sectionPath))
            imagesFolderFSPath = \
                ocf.Wr.FsAppCalls.createDir(_upan.Paths.TexFiles.Output.getAbs(bookpath, sectionPath))
            

        # copy the settings 
        vscodeSettings = os.path.join(os.getenv("BOOKS_TEMPLATES_PATH"), "settings.json")
        vscodeSettingsDirPath = os.path.join(dirPathToSection_curr, ".vscode")
        ocf.Wr.FsAppCalls.createDir(vscodeSettingsDirPath)
        ocf.Wr.FsAppCalls.copyFile(vscodeSettings, os.path.join(vscodeSettingsDirPath, "settings.json"))

    @classmethod
    def __createTopSectionFiles(cls, bookpath, sectionPath):
        dirPathToSection_curr = _upan.Paths.Section.getAbs(bookpath, sectionPath)

        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(dirPathToSection_curr):
            msg = "The top sections structure was not present will create it.\n" + \
                    "Creating path: '{0}'".format(dirPathToSection_curr)
            log.autolog(msg)
            
            # create folders
            _waitDummy = ocf.Wr.FsAppCalls.createDir(dirPathToSection_curr)

    @classmethod
    def __moveSubsectionData(cls, bookpath, sourceSubsection, targetSubsection):
        cls.updateProperty(sourceSubsection,
                            cls.PubProp.name,
                            targetSubsection,
                            bookpath)
        newLevel = str(len(targetSubsection.split(".")))
        cls.updateProperty(sourceSubsection,
                            cls.PubProp.level,
                            newLevel,
                            bookpath)

    @classmethod
    def __moveSectionFiles(cls, bookpath, sourceSection, targetSection):
        sourceSectionPath = _upan.Paths.Section.getAbs(bookpath, sourceSection)
        targetSectionPath = _upan.Paths.Section.getAbs(bookpath, targetSection)
        ocf.Wr.FsAppCalls.moveFolder(sourceSectionPath, targetSectionPath)

    @classmethod
    def __copySectionFiles(cls, bookpath, sourceSection, targetSection):
        sourceSectionPath = _upan.Paths.Section.getAbs(bookpath, sourceSection)
        targetSectionPath = _upan.Paths.Section.getAbs(bookpath, targetSection)
        ocf.Wr.FsAppCalls.copyFile(sourceSectionPath, targetSectionPath)

    @classmethod
    def __deleteSectionFiles(cls, bookpath, sourceSection):
        sourceSectionPath = _upan.Paths.Section.getAbs(bookpath, sourceSection)
        ocf.Wr.FsAppCalls.removeDir(sourceSectionPath)

    @classmethod
    def __moveSectionLinks(cls, bookpath, sourceSectionPath, targetSectionPath):
        cls.updateProperty(targetSectionPath, 
                           cls.PubProp.imGlobalLinksDict,
                           _u.Token.NotDef.dict_t.copy(),
                           bookpath)
        linkEntriesList = list(cls.readProperty(sourceSectionPath,
                                                cls.PubProp.imGlobalLinksDict,
                                                bookpath).keys())

        for entryIdx in linkEntriesList:
            gm.GeneralManger.RetargetGlLink(targetSectionPath, entryIdx,
                                            sourceSectionPath, entryIdx)

    @classmethod
    def moveSection(cls, bookpath, sourceSectionPath, targetSectionPath, shouldRebuild = True):   
        allSubsectionsList = bfs.BookInfoStructure.getSubsectionsList()

        targetSectionPathList:list = targetSectionPath.split(".")
        tempPath = targetSectionPathList.pop(0)

        for tp in targetSectionPathList:
            if tempPath not in allSubsectionsList:
                cls.addSection(bookpath, tempPath)
                cls.rebuildSubsectionImOnlyLatex(tempPath,
                                _upan.Names.Subsection.getSubsectionPretty)
            
            tempPath += "." + tp

        subsections = bfs.BookInfoStructure.getSubsectionsList(sourceSectionPath)

        cls.__moveSubsectionData(bookpath, sourceSectionPath, targetSectionPath)
        cls.__copySectionFiles(bookpath, sourceSectionPath, targetSectionPath)
        cls.__moveSectionLinks(bookpath, sourceSectionPath, targetSectionPath)

        for subsection in subsections:
            newSubsection = subsection.replace(sourceSectionPath, targetSectionPath)
            cls.__moveSubsectionData(bookpath, subsection, newSubsection)
            if shouldRebuild:
                cls.rebuildSubsectionImOnlyLatex(newSubsection,
                                                 _upan.Names.Subsection.getSubsectionPretty)
        
        if shouldRebuild:
            cls.rebuildSubsectionImOnlyLatex(targetSectionPath,
                                                _upan.Names.Subsection.getSubsectionPretty)

        for subsection in subsections:
            newSubsection = subsection.replace(sourceSectionPath, targetSectionPath)
            cls.__moveSectionLinks(bookpath, subsection, newSubsection)


        #NOTE: need to update the markers

        cls.__deleteSectionFiles(bookpath, sourceSectionPath)

    @classmethod
    def addNewImage(cls, subsection, mainImIdx, imPath, eImIdx, textOnly):
        def __executeAfterImageCreated(subsection, mainImIdx, imPath, eImIdx, textOnly):
            timer = 0

            currBookpath = sf.Wr.Manager.Book.getCurrBookFolderPath()

            isVideo = cls.readProperty(subsection, cls.PubProp.isVideo, currBookpath)

            if (not isVideo) or (eImIdx != None):
                while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imPath):
                    time.sleep(0.3)
                    timer += 1

                    if timer > 50: 
                        _u.log.autolog(f"The image at path '{imPath}' was not created.")
                        return

            if eImIdx == None:
                if not isVideo:
                    imText = _u.getTextFromImage(imPath)
                else:
                    imText = None

                if textOnly:
                    if imText == None:
                        imText = _u.Token.NotDef.str_t
                    else:
                        imText = imText.replace("_", "\_")

                        imText = re.sub(r"([^\\]){", r"\1\\{", imText)
                        imText = re.sub(r"([^\\])}", r"\1\\}", imText)
                        imText = re.sub(r"([a-z]|[A-Z])\u0308", r"\\ddot{\1}", imText)
                        imText = re.sub(r"([a-z]|[A-Z])\u0300", r"\\grave{\1}", imText)
                        imText = re.sub(r"([a-z]|[A-Z])\u0301", r"\\acute{\1}", imText)

                        imText = imText.replace("[", "(")
                        imText = imText.replace("]", ")")
                        imText = imText.replace("\u201c", "\"")
                        imText = imText.replace("\u201d", "\"")
                        imText = imText.replace("\u2014", "-")
                        imText = imText.replace("\ufffd", "")
                        imText = imText.replace("\n", "")
                        imText = imText.replace("\u0000", "fi")
                        imText = imText.replace("\u0394", "\\Delta ")

                imageTextsDict = cls.readProperty(subsection, cls.PubProp.imageText, currBookpath)
                imageTextsDict = {} if imageTextsDict == _u.Token.NotDef.dict_t else imageTextsDict
                imageTextsDict[mainImIdx] = imText
                cls.updateProperty(subsection, cls.PubProp.imageText, imageTextsDict, currBookpath)
            else:
                eImText = _u.getTextFromImage(imPath)
                eImageTextsDict = cls.readProperty(subsection, cls.PubProp.extraImText)
                eImageTextsDict = {} if eImageTextsDict == _u.Token.NotDef.dict_t else eImageTextsDict

                if mainImIdx not in list(eImageTextsDict.keys()):
                    eImageTextsList = []
                else:
                    eImageTextsList = eImageTextsDict[mainImIdx]

                if int(eImIdx) >= len(eImageTextsList):
                    eImageTextsList.append(eImText)
                else:
                    eImageTextsList[int(eImIdx)] = eImText

                eImageTextsDict[mainImIdx] = eImageTextsList
                cls.updateProperty(subsection, cls.PubProp.extraImText, eImageTextsDict, currBookpath)

        t = Thread(\
            target = \
                lambda s = subsection, mi = mainImIdx, ip = imPath, eii = eImIdx, to = textOnly:__executeAfterImageCreated(s, mi, ip, eii, to))
        t.start()


    @classmethod
    def addSection(cls, bookpath, sectionPath):

        # set the curr section to new section
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.currSection, sectionPath)
        # update things here for the book open subsection
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.subsectionOpenInTOC_UI, sectionPath)

        cls.__createSubsectionFiles(bookpath, sectionPath)

        cls.updateProperty(sectionPath, cls.PubProp.name, sectionPath)

    @classmethod
    def addTopSection(cls, bookpath, sectionPath):

        # set the curr section to new section
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.currSection, sectionPath)
        # update things here for the book open subsection
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.subsectionOpenInTOC_UI, sectionPath)

        cls.__createTopSectionFiles(bookpath, sectionPath)
    
    def __shiftTheItemsInTheDict(dict, startShiftIdx, left = True):
        # shift each item of the dict starting from the idx to the left
        outDict = {}

        if left:
            r = range(0, len(list(dict.keys())))
        else:
            r = range(len(list(dict.keys())) - 1, -1, -1)

        for i in r:
            k = list(dict.keys())[i]

            if int(k) < int(startShiftIdx):
                outDict[k] = dict[k]
            else:
                if left:
                    outDict[str(int(k) - 1)] = dict[k]
                else:
                    outDict[str(int(k) + 1)] = dict[k]

        keys = [int(i) for i in list(outDict.keys())]
        keys.sort()
        outDict = {str(i): outDict[str(i)] for i in keys}

        return outDict

    @classmethod
    def insertEntryAfterIdx(cls,
                            sourceSubsection, sourceImIdx, 
                            targetSubsection, targetImIdx,
                            cutEntry):
        # CORE OPERATIONS
        if (sourceSubsection == targetSubsection) and (sourceImIdx == targetImIdx):
            targetImIdx = str(int(targetImIdx) + 1)

         # ask the user if we wnat to proceed.
        cutEntryStr = "CUT" if cutEntry else "COPY"

        msg = "\
Before {4} entry from \n\
'{0}':'{1}'\n\
to '{2}':'{3}'.".format(sourceSubsection, sourceImIdx, 
                        targetSubsection, targetImIdx,
                        cutEntryStr)
        log.autolog(msg)
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)


        cls.shiftEntryUp(targetSubsection, targetImIdx)

        if (sourceSubsection == targetSubsection) and (int(sourceImIdx) > int(targetImIdx)):
            sourceImIdx = str(int(sourceImIdx) + 1)

        cls.__copyEntry(sourceSubsection, sourceImIdx, targetSubsection, targetImIdx)

        if cutEntry:
            log.autolog("Cutting the entry.")
            cls.removeEntry(sourceSubsection, sourceImIdx)

        # update the links on the OM file
        oldImLinkOMPageDict = cls.readProperty(sourceSubsection, cls.PubProp.imLinkOMPageDict).values()
        newImLinkOMPageDict = cls.readProperty(targetSubsection, cls.PubProp.imLinkOMPageDict).values()

        imLinkOMPageDict = sorted(list(oldImLinkOMPageDict) + list(newImLinkOMPageDict))

        sourceGroupsList:dict = cls.readProperty(sourceSubsection, cls.PubProp.imagesGroupsList)
        targetGroupsDict:dict = cls.readProperty(targetSubsection, cls.PubProp.imagesGroupDict)
        targetGroupsList:dict = cls.readProperty(targetSubsection, cls.PubProp.imagesGroupsList)
        group = list(sourceGroupsList.keys())[targetGroupsDict[targetImIdx]]

        if group in list(targetGroupsList.keys()):
            groupIdx = list(targetGroupsList.keys()).index(group)
        else:
            targetGroupsList[group] = True
            groupIdx = len(list(targetGroupsList.keys())) - 1
            cls.updateProperty(targetSubsection, cls.PubProp.imagesGroupsList, targetGroupsList)

        targetGroupsDict = cls.readProperty(targetSubsection, cls.PubProp.imagesGroupDict)
        targetGroupsDict[targetImIdx] = groupIdx
        cls.updateProperty(targetSubsection, cls.PubProp.imagesGroupDict, targetGroupsDict)

        msg = "\
After {4} entry from \n\
'{0}':'{1}'\n\
to '{2}':'{3}'.".format(sourceSubsection, sourceImIdx, 
                        targetSubsection, targetImIdx,
                        cutEntryStr)

        if targetSubsection == sourceSubsection:
            rebuildStartIdx = str(min(int(sourceImIdx), int(targetImIdx)))
        else:
            rebuildStartIdx = sourceImIdx

        if shouldAsk:
            cls.rebuildEntriesBatch(sourceSubsection, rebuildStartIdx)

            if targetSubsection != sourceSubsection:
                cls.rebuildEntriesBatch(targetSubsection, targetImIdx)

        log.autolog(msg)
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

    @classmethod
    def __removeMarker(cls, subsection, imIdx):
        def __updateFile(filepath, oldMarker, newMarker):
            lines = []

            with open(filepath, "r") as f:
                lines = f.readlines()

            for i in range(len(lines)):
                if oldMarker in lines[i]:
                    if newMarker == "":
                        lines[i] = ""
                    else:
                        lines[i] = lines[i].replace(oldMarker, newMarker)

            with open(filepath, "w") as f:
                f.writelines(lines)

        bookCodeFiles:dict = cls.readProperty(subsection, cls.PubProp.bookCodeFile)
        bookCodeFilesSorted = list(bookCodeFiles.keys())
        bookCodeFilesSorted.sort(key = lambda k: int(k.split("_")[0]))

        if len(bookCodeFilesSorted) != 0:
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

            bookCodeFilesRoot = _upan.Paths.Book.Code.getAbs(bookPath)

            for k in bookCodeFilesSorted:
                relPath = bookCodeFiles[k]

                if relPath[0] == "/":
                    relPath = relPath[1:]

                filepath = os.path.join(bookCodeFilesRoot, relPath)

                if int(k.split("_")[0]) == int(imIdx):
                    oldMarker = _upan.Names.codeLineMarkerBook(subsection, imIdx)
                    __updateFile(filepath, oldMarker, "")
                elif int(k.split("_")[0]) > int(imIdx):
                    oldMarker = _upan.Names.codeLineMarkerBook(subsection, k)
                    newKey =  str(int(k.split("_")[0]) - 1) 

                    if len(k.split("_")) > 1:
                        newKey += "_" + k.split("_")[1]

                    newMarker = _upan.Names.codeLineMarkerBook(subsection, newKey)
                    __updateFile(filepath, oldMarker, newMarker)

                    bookCodeFiles[newKey] = bookCodeFiles[k]

            largestKey = bookCodeFilesSorted[-1].split("_")[0]

            for k in bookCodeFilesSorted:
                if k.split("_")[0] == largestKey:
                    bookCodeFiles.pop(k)

            cls.updateProperty(subsection, cls.PubProp.bookCodeFile, bookCodeFiles)

        subsectionCodeFiles:dict = cls.readProperty(subsection, cls.PubProp.subsectionCodeFile)

        subsectionCodeFilesSorted = list(subsectionCodeFiles.keys())
        subsectionCodeFilesSorted.sort(key = lambda k: int(k.split("_")[0]))

        if len(subsectionCodeFilesSorted) != 0:
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            subsectionCodeFilesRoot = _upan.Paths.Section.getCodeRootAbs(bookPath,
                                                                         subsection)

            for k in subsectionCodeFilesSorted:
                relPath = subsectionCodeFiles[k]

                if relPath[0] == "/":
                    relPath = relPath[1:]

                filepath = os.path.join(subsectionCodeFilesRoot, relPath)

                if int(k.split("_")[0]) == int(imIdx):
                    oldMarker = _upan.Names.codeLineMarkerSubsection(subsection, imIdx)
                    __updateFile(filepath, oldMarker, "")
                elif int(k.split("_")[0]) > int(imIdx):
                    oldMarker = _upan.Names.codeLineMarkerSubsection(subsection, k)
                    newKey =  str(int(k.split("_")[0]) - 1) 

                    if len(k.split("_")) > 1:
                        newKey += "_" + k.split("_")[1]

                    newMarker = _upan.Names.codeLineMarkerSubsection(subsection, newKey)
                    __updateFile(filepath, oldMarker, newMarker)
                    subsectionCodeFiles[newKey] = subsectionCodeFiles[k]

            for k in subsectionCodeFilesSorted:
                if k.split("_")[0] == largestKey:
                    subsectionCodeFiles.pop(k)

            cls.updateProperty(subsection, cls.PubProp.subsectionCodeFile, subsectionCodeFiles)

    @classmethod
    def removeEntry(cls, subsection, imIdx):
        import generalManger.generalManger as gm            
        
        # track all the changes berore and after removal
        msg = "Before removing the subsection: '{0}_{1}'.".format(subsection, imIdx)
        log.autolog(msg)

        if shouldConfirm:
            ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

        currBookName = sf.Wr.Manager.Book.getCurrBookName()
        imagesPath = _upan.Paths.Screenshot.getAbs(currBookName, subsection)

        extraImagesDict = cls.readProperty(subsection, cls.PubProp.extraImagesDict)
        imGlobalLinksDict = cls.readProperty(subsection, cls.PubProp.imGlobalLinksDict)

        # remove the marker
        cls.__removeMarker(subsection, imIdx)

        # move the extra images
        if imIdx in list(extraImagesDict.keys()):
            extraImNames = extraImagesDict[imIdx]

            if extraImNames != None:
                for extraImIdx in range(len(extraImNames)):
                    extraImFilename = _upan.Names.getExtraImageFilename(imIdx, subsection, extraImIdx)
                    ocf.Wr.FsAppCalls.deleteFile(os.path.join(imagesPath, extraImFilename + ".png"))
        

        imLinkDict = cls.readProperty(subsection, cls.PubProp.imLinkDict)

        currBookpath = sf.Wr.Manager.Book.getCurrBookFolderPath()

        if imIdx == list(imLinkDict.keys())[-1]:
            imName = _upan.Names.getImageName(imIdx)
            ocf.Wr.FsAppCalls.deleteFile(os.path.join(imagesPath, imName + ".png"))
            imTexPath = _upan.Paths.Screenshot.Images.getMainEntryTexImageAbs(currBookpath,
                                                                              subsection,
                                                                              imIdx)
            ocf.Wr.FsAppCalls.deleteFile(imTexPath)
        else:
            # take care of the rest of the images in the subsesction
            for imLinkId in list(imLinkDict.keys()):
                if int(imLinkId) > int(imIdx):
                    # move the main image files
                    imNameOld = _upan.Names.getImageName(imLinkId)
                    imNameNew = _upan.Names.getImageName(str(int(imLinkId) - 1))
                    ocf.Wr.FsAppCalls.moveFile(os.path.join(imagesPath, imNameOld + ".png"),
                                            os.path.join(imagesPath, imNameNew + ".png"))
                    imTexNameOld = _upan.Paths.Screenshot.Images.getMainEntryTexImageAbs(currBookpath,
                                                                                         subsection,
                                                                                         imLinkId)
                    imTexNameNew = _upan.Paths.Screenshot.Images.getMainEntryTexImageAbs(currBookpath,
                                                                                         subsection,
                                                                                         str(int(imLinkId) - 1))
                    ocf.Wr.FsAppCalls.moveFile(imTexNameOld, imTexNameNew)

                    # move the extra images
                    if imLinkId in list(extraImagesDict.keys()):
                        extraImNames = extraImagesDict[imLinkId]

                        if extraImNames != None:
                            for extraImIdx in range(len(extraImNames)):
                                extraImOldFilename = _upan.Names.getExtraImageFilename(imLinkId, subsection, extraImIdx)
                                extraImNewFilename = _upan.Names.getExtraImageFilename(str(int(imLinkId) - 1), subsection, extraImIdx)

                                ocf.Wr.FsAppCalls.moveFile(os.path.join(imagesPath, extraImOldFilename + ".png"),
                                                            os.path.join(imagesPath, extraImNewFilename + ".png"))

        # NOTE: not used at this time
        # update the tex files
        #tff.Wr.TexFileModify.removeImageFromCon(currBookName, subsection, imIdx)
        
        # remove all the global links that lead to this entry
        if imIdx in list(imGlobalLinksDict.keys()):
            glLinksListImDict = imGlobalLinksDict[imIdx]

            if type(glLinksListImDict) == dict:
                for glLink in list(glLinksListImDict.keys()):
                    if "KIK" in glLinksListImDict[glLink]:
                        llinkSubsection = glLink.split("_")[0]
                        llinkIdx = glLink.split("_")[1]
                        gm.GeneralManger.RemoveGlLink(llinkSubsection, subsection,
                                                      imIdx, llinkIdx)

        # update links to other images
        imLinkDictKeys = [i for i in list(imGlobalLinksDict.keys()) if int(i) > int(imIdx)] 
        imLinkDictKeys.sort(key = int)

        for imLinkId in imLinkDictKeys:
            glLinksListImDict = imGlobalLinksDict[imLinkId]

            if type(glLinksListImDict) == dict:
                gm.GeneralManger.RetargetGlLink(subsection, str(int(imLinkId) - 1),
                                                subsection, imLinkId)

        imLinkDict.pop(imIdx, None)
        imLinkDict = cls.__shiftTheItemsInTheDict(imLinkDict, imIdx)

        if imLinkDict == {}:
            imLinkDict = _u.Token.NotDef.dict_t.copy()

        cls.updateProperty(subsection, cls.PubProp.imLinkDict, imLinkDict)

        imLinkOMPageDict:dict = cls.readProperty(subsection, cls.PubProp.imLinkOMPageDict)
        imLinkOMPageDict.pop(imIdx, None)
        imLinkOMPageDict = cls.__shiftTheItemsInTheDict(imLinkOMPageDict, imIdx)

        if imLinkOMPageDict == {}:
            imLinkOMPageDict = _u.Token.NotDef.dict_t.copy()

        cls.updateProperty(subsection, cls.PubProp.imLinkOMPageDict, imLinkOMPageDict)

        origMatNameDict = cls.readProperty(subsection, cls.PubProp.origMatNameDict)
        origMatNameDict.pop(imIdx, None)
        origMatNameDict = cls.__shiftTheItemsInTheDict(origMatNameDict, imIdx)

        if origMatNameDict == {}:
            origMatNameDict = _u.Token.NotDef.dict_t.copy()

        cls.updateProperty(subsection, cls.PubProp.origMatNameDict, origMatNameDict)

        imageUIResize = cls.readProperty(subsection, cls.PubProp.imageUIResize)

        imageUIResize = {k:v for k,v in imageUIResize.items() if int(k.split("_")[0]) > int(imIdx)}
        newImageUIResize = {}
        imageUIResizeKeysSorted = list(imageUIResize.keys())
        imageUIResizeKeysSorted.sort(key = lambda k: int(k.split("_")[0]))

        for k in imageUIResizeKeysSorted:
            newImageUIResize[k] = imageUIResize[k]
        
        imageUIResize = newImageUIResize
        imageUIResize = {str(int(k) - 1) if len(k.split("_")) == 1 else str(int(k.split("_")[0]) - 1) + "_" + k.split("_")[1]:v\
                          for k,v in imageUIResize.items() if int(k.split("_")[0]) > int(imIdx)}
        imageUIResizeOrig = cls.readProperty(subsection, cls.PubProp.imageUIResize)

        for k,v in imageUIResizeOrig.items():
            if int(k.split("_")[0]) <= int(imIdx):
                imageUIResize[k] = v

        if imageUIResize == {}:
            imageUIResize = _u.Token.NotDef.dict_t.copy()

        cls.updateProperty(subsection, cls.PubProp.imageUIResize, imageUIResize)

        figuresData = cls.readProperty(subsection, cls.PubProp.figuresData)

        figuresData = {k:v for k,v in figuresData.items() if int(k.split("_")[0]) > int(imIdx)}
        newFiguresData = {}
        figuresDataKeysSorted = list(figuresData.keys())
        figuresDataKeysSorted.sort(key = lambda k: int(k.split("_")[0]))

        for k in figuresDataKeysSorted:
            newFiguresData[k] = figuresData[k]
        
        figuresData = newFiguresData
        figuresData = {str(int(k) - 1) if len(k.split("_")) == 1 else str(int(k.split("_")[0]) - 1) + "_" + k.split("_")[1]:v\
                          for k,v in figuresData.items() if int(k.split("_")[0]) > int(imIdx)}
        figuresDataOrig = cls.readProperty(subsection, cls.PubProp.figuresData)

        for k,v in figuresDataOrig.items():
            if int(k.split("_")[0]) <= int(imIdx):
                figuresData[k] = v

        if figuresData == {}:
            figuresData = _u.Token.NotDef.dict_t.copy()

        cls.updateProperty(subsection, cls.PubProp.figuresData, figuresData)

        figuresLabelsData = cls.readProperty(subsection, cls.PubProp.figuresLabelsData)

        figuresLabelsData = {k:v for k,v in figuresLabelsData.items() if int(k.split("_")[0]) > int(imIdx)}
        newFiguresLabelsData = {}
        figuresLabelsDataKeysSorted = list(figuresLabelsData.keys())
        figuresLabelsDataKeysSorted.sort(key = lambda k: int(k.split("_")[0]))

        for k in figuresLabelsDataKeysSorted:
            newFiguresLabelsData[k] = figuresLabelsData[k]
        
        figuresLabelsData = newFiguresLabelsData
        figuresLabelsData = {str(int(k) - 1) if len(k.split("_")) == 1 else str(int(k.split("_")[0]) - 1) + "_" + k.split("_")[1]:v\
                          for k,v in figuresLabelsData.items() if int(k.split("_")[0]) > int(imIdx)}
        figuresLabelsDataOrig = cls.readProperty(subsection, cls.PubProp.figuresLabelsData)

        for k,v in figuresLabelsDataOrig.items():
            if int(k.split("_")[0]) < int(imIdx):
                figuresLabelsData[k] = v

        if figuresLabelsData == {}:
            figuresLabelsData = _u.Token.NotDef.dict_t.copy()

        cls.updateProperty(subsection, cls.PubProp.figuresLabelsData, figuresLabelsData)

        extraImagesDict = cls.readProperty(subsection, cls.PubProp.extraImagesDict)
        extraImNames = extraImagesDict.pop(imIdx, None)
        extraImagesDict = cls.__shiftTheItemsInTheDict(extraImagesDict, imIdx)

        if extraImagesDict == {}:
            extraImagesDict = _u.Token.NotDef.dict_t.copy()

        cls.updateProperty(subsection, cls.PubProp.extraImagesDict, extraImagesDict)

        tocWImageDict = cls.readProperty(subsection, cls.PubProp.tocWImageDict)
        tocWImageDict.pop(imIdx, None)

        if tocWImageDict == {}:
            tocWImageDict = _u.Token.NotDef.dict_t.copy()

        tocWImageDict = cls.__shiftTheItemsInTheDict(tocWImageDict, imIdx)
        cls.updateProperty(subsection, cls.PubProp.tocWImageDict, tocWImageDict)

        imagesGroupDict = cls.readProperty(subsection, cls.PubProp.imagesGroupDict)
        imagesGroupDict.pop(imIdx, None)

        if imagesGroupDict == {}:
            imagesGroupDict = _u.Token.NotDef.dict_t.copy()

        imagesGroupDict = cls.__shiftTheItemsInTheDict(imagesGroupDict, imIdx)
        cls.updateProperty(subsection, cls.PubProp.imagesGroupDict, imagesGroupDict)

        textOnlyDict = cls.readProperty(subsection, cls.PubProp.textOnly)
        textOnlyDict.pop(imIdx, None)

        if textOnlyDict == {}:
            textOnlyDict = _u.Token.NotDef.dict_t.copy()

        textOnlyDict = cls.__shiftTheItemsInTheDict(textOnlyDict, imIdx)
        cls.updateProperty(subsection, cls.PubProp.textOnly, textOnlyDict)

        imagesText = cls.readProperty(subsection, cls.PubProp.imageText)
        imagesText.pop(imIdx, None)

        if imagesText == {}:
            imagesText = _u.Token.NotDef.dict_t.copy()

        imagesText = cls.__shiftTheItemsInTheDict(imagesText, imIdx)
        cls.updateProperty(subsection, cls.PubProp.imageText, imagesText)

        wikiPages = cls.readProperty(subsection, cls.PubProp.wikiPages)
        wikiPages.pop(imIdx, None)

        if wikiPages == {}:
            wikiPages = _u.Token.NotDef.dict_t.copy()

        wikiPages = cls.__shiftTheItemsInTheDict(wikiPages, imIdx)
        cls.updateProperty(subsection, cls.PubProp.wikiPages, wikiPages)

        videoPosition = cls.readProperty(subsection, cls.PubProp.videoPosition)
        videoPosition.pop(imIdx, None)

        if videoPosition == {}:
            videoPosition = _u.Token.NotDef.dict_t.copy()

        videoPosition = cls.__shiftTheItemsInTheDict(videoPosition, imIdx)
        cls.updateProperty(subsection, cls.PubProp.videoPosition, videoPosition)

        leadingEntry = cls.readProperty(subsection, cls.PubProp.leadingEntry)
        leadingEntry = {k:v for k, v in leadingEntry.items() if str(v) != str(imIdx)}

        for k,v in leadingEntry.items():
            if int(v) > int(imIdx):
                leadingEntry[k] = str(int(v) - 1)

        cls.updateProperty(subsection, cls.PubProp.leadingEntry, leadingEntry)

        leadingEntry = cls.readProperty(subsection, cls.PubProp.leadingEntry)
        leadingEntry.pop(imIdx, None)

        if leadingEntry == {}:
            leadingEntry = _u.Token.NotDef.dict_t.copy()

        leadingEntry = cls.__shiftTheItemsInTheDict(leadingEntry, imIdx)
        cls.updateProperty(subsection, cls.PubProp.leadingEntry, leadingEntry)

        showSubentries = cls.readProperty(subsection, cls.PubProp.showSubentries)
        showSubentries.pop(imIdx, None)

        if showSubentries == {}:
            showSubentries = _u.Token.NotDef.dict_t.copy()

        showSubentries = cls.__shiftTheItemsInTheDict(showSubentries, imIdx)
        cls.updateProperty(subsection, cls.PubProp.showSubentries, showSubentries)

        extraImTextDict = cls.readProperty(subsection, cls.PubProp.extraImText)
        extraImTextDict.pop(imIdx, None)
        extraImTextDict = cls.__shiftTheItemsInTheDict(extraImTextDict, imIdx)

        if extraImTextDict == {}:
            extraImTextDict = _u.Token.NotDef.dict_t.copy()

        cls.updateProperty(subsection, cls.PubProp.extraImText, extraImTextDict)

        msg = "After removing the subsection: '{0}_{1}'.".format(subsection, imIdx)
        log.autolog(msg)

        if shouldConfirm:
            # update the links on the OM file

            efs.EntryInfoStructure.removeEntry(subsection, imIdx, currBookName)

            # track all the changes berore and after removal

            cls.rebuildEntriesBatch(subsection, imIdx)
            ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

    @classmethod
    def __shiftMarkerUp(cls, subsection, imIdx):
        def __updateFile(filepath, oldMarker, newMarker):
            lines = []

            with open(filepath, "r") as f:
                lines = f.readlines()

            for i in range(len(lines)):
                lines[i] = lines[i].replace(oldMarker, newMarker)

            with open(filepath, "w") as f:
                f.writelines(lines)

        bookCodeFiles:dict = cls.readProperty(subsection, cls.PubProp.bookCodeFile)
        bookCodeFilesSorted = list(bookCodeFiles.keys())
        bookCodeFilesSorted.sort(key = lambda k: int(k), reverse = True)

        if len(bookCodeFilesSorted) != 0:
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

            bookCodeFilesRoot = _upan.Paths.Book.Code.getAbs(bookPath)

            for k in bookCodeFilesSorted:
                if int(k) >= int(imIdx):
                    relPath = bookCodeFiles[k]

                    if relPath[0] == "/":
                        relPath = relPath[1:]

                    filePath = os.path.join(bookCodeFilesRoot, relPath)

                    oldMarker = _upan.Names.codeLineMarkerBook(subsection, k)
                    newMarker = _upan.Names.codeLineMarkerBook(subsection, str(int(k) + 1))
                    __updateFile(filePath, oldMarker, newMarker)

                    bookCodeFiles[str(int(k) + 1)] = bookCodeFiles[k]

            if bookCodeFiles.get(imIdx) != None:
                bookCodeFiles.pop(imIdx)

            cls.updateProperty(subsection, cls.PubProp.bookCodeFile, bookCodeFiles)

        currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        subsectionCodeFilesRoot =_upan.Paths.Section.getCodeRootAbs(currBookPath, subsection)
        subsectionCodeFiles:dict = cls.readProperty(subsection, cls.PubProp.subsectionCodeFile)

        subsectionCodeFilesSorted = list(subsectionCodeFiles.keys())
        subsectionCodeFilesSorted.sort(key = lambda k: int(k), reverse = True)

        if len(subsectionCodeFilesSorted) != 0:
            for k in subsectionCodeFilesSorted:
                if int(k) >= int(imIdx):
                    relPath = subsectionCodeFiles[k]

                    if relPath[0] == "/":
                        relPath = relPath[1:]

                    filePath = os.path.join(subsectionCodeFilesRoot, relPath)

                    oldMarker = _upan.Names.codeLineMarkerSubsection(subsection, k)
                    newMarker = _upan.Names.codeLineMarkerSubsection(subsection, str(int(k) + 1))
                    __updateFile(filePath, oldMarker, newMarker)

                    subsectionCodeFiles[str(int(k) + 1)] = subsectionCodeFiles[k]

            if subsectionCodeFiles.get(imIdx) != None:
                subsectionCodeFiles.pop(imIdx)

            cls.updateProperty(subsection, cls.PubProp.subsectionCodeFile, subsectionCodeFiles)

    @classmethod
    def shiftEntryUp(cls, subsection, imIdx):
        import generalManger.generalManger as gm

        # track all the changes berore and after removal
        msg = "Before shifting the subsection entries the subsection: '{0}_{1}'.".format(subsection, imIdx)
        log.autolog(msg)

        if shouldConfirm:
            ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

        currBookName = sf.Wr.Manager.Book.getCurrBookName()
        imagesPath = _upan.Paths.Screenshot.getAbs(currBookName, subsection)

        # shift the markers up
        cls.__shiftMarkerUp(subsection, imIdx)

        imLinkDict = cls.readProperty(subsection, cls.PubProp.imLinkDict)

        # deal with the links
        imGlobalLinksDict = cls.readProperty(subsection, cls.PubProp.imGlobalLinksDict)

        linksKeysSorted = [i for i in list(imGlobalLinksDict.keys()) if int(i) >= int(imIdx)]
        linksKeysSorted.sort(key = int, reverse = True)

        # shift all the global links that lead to this entry
        for linkIdx in linksKeysSorted:
            linksDictType = type(imGlobalLinksDict[linkIdx])

            if linksDictType == dict:
                gm.GeneralManger.RetargetGlLink(subsection, str(int(linkIdx) + 1),
                                                subsection, linkIdx)

        #deal with the excercises
        for i in range(len(list(imLinkDict.keys())) - 1, -1, -1):
            entryImIdx = list(imLinkDict.keys())[i]
            if int(entryImIdx) >= int(imIdx):
                oldEntryLinesPath = _upan.Paths.Entry.getAbs(currBookName, subsection, entryImIdx)

                if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(oldEntryLinesPath):
                    lines = efs.EntryInfoStructure.readProperty(subsection,
                                                                entryImIdx, 
                                                                efs.EntryInfoStructure.PubProp.entryLinesList)

                    for lineIdx in range(len(lines) - 1, -1, -1):
                        savePath = _upan.Paths.Entry.getAbs(currBookName, subsection, entryImIdx)
                        oldFilename = _upan.Names.Entry.Line.name(entryImIdx, lineIdx)
                        oldPath = os.path.join(savePath, oldFilename)
                        newFilename = _upan.Names.Entry.Line.name(str(int(entryImIdx) + 1), lineIdx)
                        newPath = os.path.join(savePath, newFilename)
                        ocf.Wr.FsAppCalls.moveFile(oldPath, newPath)

                    oldName = efs.EntryInfoStructure.readProperty(subsection,
                                                                entryImIdx, 
                                                                efs.EntryInfoStructure.PubProp.name)
                    efs.EntryInfoStructure.updateProperty(subsection,
                                                        entryImIdx, 
                                                        efs.EntryInfoStructure.PubProp.name,
                                                        str(int(oldName) + 1))

                    newEntryLinesPath = _upan.Paths.Entry.getAbs(currBookName, 
                                                                subsection,
                                                                str(int(entryImIdx) + 1))
                    ocf.Wr.FsAppCalls.moveFolder(oldEntryLinesPath, newEntryLinesPath)

        # move the extra images
        extraImagesDict = cls.readProperty(subsection, cls.PubProp.extraImagesDict)
        extraImFilenames = []

        if imIdx in list(extraImagesDict.keys()):
            extraImNames = extraImagesDict[imIdx]

            if extraImNames != None:
                for extraImIdx in range(len(extraImNames)):
                    extraImFilename = _upan.Names.getExtraImageFilename(imIdx, subsection, extraImIdx)
                    extraImFilename = os.path.join(imagesPath, extraImFilename + ".png")

                    newExtraImFilename = _upan.Names.getExtraImageFilename(str(int(imIdx) + 1), subsection, extraImIdx)
                    newExtraImFilename = os.path.join(imagesPath, newExtraImFilename + ".png")
                    extraImFilenames.append([extraImFilename,
                                             newExtraImFilename])

        for i in range(len(extraImFilenames) - 1, -1):
            ocf.Wr.FsAppCalls.moveFile(extraImFilenames[i][0], extraImFilenames[i][1])

        # take care of the of the images in the subsesction
        for i in range(len(list(imLinkDict.keys())) - 1, -1, -1):
            imLinkId = list(imLinkDict.keys())[i]

            if int(imLinkId) >= int(imIdx):
                # move the main image files
                imNameOld = _upan.Names.getImageName(imLinkId)
                imNameNew = _upan.Names.getImageName(str(int(imLinkId) + 1))
                ocf.Wr.FsAppCalls.moveFile(os.path.join(imagesPath, imNameOld + ".png"),
                                        os.path.join(imagesPath, imNameNew + ".png"))

                currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                oldEntryImgPath = _upan.Paths.Screenshot.Images.getMainEntryTexImageAbs(currBookPath,
                                                                                     subsection, 
                                                                                     imLinkId)
                newEntryImgPath =_upan.Paths.Screenshot.Images.getMainEntryTexImageAbs(currBookPath,
                                                                                    subsection,
                                                                                    str(int(imLinkId) + 1))
                ocf.Wr.FsAppCalls.moveFile(oldEntryImgPath, newEntryImgPath)

                # move the extra images
                if imLinkId in list(extraImagesDict.keys()):
                    extraImNames = extraImagesDict[imLinkId]

                    if extraImNames != None:
                        for extraImIdx in range(len(extraImNames)):
                            extraImOldFilename = _upan.Names.getExtraImageFilename(imLinkId, subsection, extraImIdx)
                            extraImNewFilename = _upan.Names.getExtraImageFilename(str(int(imLinkId) + 1), subsection, extraImIdx)

                            ocf.Wr.FsAppCalls.moveFile(os.path.join(imagesPath, extraImOldFilename + ".png"),
                                                        os.path.join(imagesPath, extraImNewFilename + ".png"))


        def updateProperty(propertyName):
            dataDict = cls.readProperty(subsection, propertyName)
            dataDict = cls.__shiftTheItemsInTheDict(dataDict, imIdx, False)
            cls.updateProperty(subsection, propertyName, dataDict)

        leadingEntry = cls.readProperty(subsection, cls.PubProp.leadingEntry)

        for k,v in leadingEntry.items():
            if int(v) >= int(imIdx):
                leadingEntry[k] = str(int(imIdx) + 1)

        cls.updateProperty(subsection, cls.PubProp.leadingEntry, leadingEntry)

        properties = [
            cls.PubProp.imLinkDict,
            cls.PubProp.imLinkOMPageDict,
            cls.PubProp.origMatNameDict,
            cls.PubProp.extraImagesDict,
            cls.PubProp.tocWImageDict,
            cls.PubProp.imagesGroupDict,
            cls.PubProp.imageText,
            cls.PubProp.extraImText,
            cls.PubProp.textOnly,
            cls.PubProp.wikiPages,
            cls.PubProp.videoPosition,
            cls.PubProp.leadingEntry,
            cls.PubProp.showSubentries,
        ]

        for p in properties:
            updateProperty(p)

        imageUIResize = cls.readProperty(subsection, cls.PubProp.imageUIResize)
        imageUIResize = {k:v for k,v in imageUIResize.items() if int(k.split("_")[0]) >= int(imIdx)}
        newImageUIResize = {}
        imageUIResizeKeysSorted = list(imageUIResize.keys())
        imageUIResizeKeysSorted.sort(key = lambda k: int(k.split("_")[0]), reverse = True)

        for k in imageUIResizeKeysSorted:
            newImageUIResize[k] = imageUIResize[k]
        
        imageUIResize = newImageUIResize
        imageUIResize = \
            {str(int(k) + 1) if len(k.split("_")) == 1 else str(int(k.split("_")[0]) + 1) + "_" + k.split("_")[1]:v\
              for k,v in imageUIResize.items() if int(k.split("_")[0]) >= int(imIdx)}

        imageUIResizeOrig = cls.readProperty(subsection, cls.PubProp.imageUIResize)

        for k,v in imageUIResizeOrig.items():
            if int(k.split("_")[0]) < int(imIdx):
                imageUIResize[k] = v

        if imageUIResize == {}:
            imageUIResize = _u.Token.NotDef.dict_t.copy()

        cls.updateProperty(subsection, cls.PubProp.imageUIResize, imageUIResize)

        figuresLabelsData = cls.readProperty(subsection, cls.PubProp.figuresLabelsData)
        figuresLabelsData = {k:v for k,v in figuresLabelsData.items() if int(k.split("_")[0]) >= int(imIdx)}
        newFiguresLabelsData = {}
        figuresLabelsDataKeysSorted = list(figuresLabelsData.keys())
        figuresLabelsDataKeysSorted.sort(key = lambda k: int(k.split("_")[0]), reverse = True)

        for k in figuresLabelsDataKeysSorted:
            newFiguresLabelsData[k] = figuresLabelsData[k]
        
        figuresLabelsData = newFiguresLabelsData
        figuresLabelsData = \
            {str(int(k) + 1) if len(k.split("_")) == 1 else str(int(k.split("_")[0]) + 1) + "_" + k.split("_")[1]:v\
              for k,v in figuresLabelsData.items() if int(k.split("_")[0]) >= int(imIdx)}

        figuresLabelsDataOrig = cls.readProperty(subsection, cls.PubProp.figuresLabelsData)

        for k,v in figuresLabelsDataOrig.items():
            if int(k.split("_")[0]) <= int(imIdx):
                figuresLabelsData[k] = v

        if figuresLabelsData == {}:
            figuresLabelsData = _u.Token.NotDef.dict_t.copy()

        cls.updateProperty(subsection, cls.PubProp.figuresLabelsData, figuresLabelsData)

        figuresData = cls.readProperty(subsection, cls.PubProp.figuresData)
        figuresData = {k:v for k,v in figuresData.items() if int(k.split("_")[0]) >= int(imIdx)}
        newFiguresData = {}
        figuresDataKeysSorted = list(figuresData.keys())
        figuresDataKeysSorted.sort(key = lambda k: int(k.split("_")[0]), reverse = True)

        for k in figuresDataKeysSorted:
            newFiguresData[k] = figuresData[k]
        
        figuresData = newFiguresData
        figuresData = \
            {str(int(k) + 1) if len(k.split("_")) == 1 else str(int(k.split("_")[0]) + 1) + "_" + k.split("_")[1]:v\
              for k,v in figuresData.items() if int(k.split("_")[0]) >= int(imIdx)}

        figuresDataOrig = cls.readProperty(subsection, cls.PubProp.figuresData)

        for k,v in figuresDataOrig.items():
            if int(k.split("_")[0]) < int(imIdx):
                figuresData[k] = v

        if figuresData == {}:
            figuresData = _u.Token.NotDef.dict_t.copy()

        cls.updateProperty(subsection, cls.PubProp.figuresData, figuresData)

        msg = "After shifting the subsection: '{0}_{1}'.".format(subsection, imIdx)
        log.autolog(msg)

        if shouldConfirm:
            oldEntryImOpenInTOC_UI = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.entryImOpenInTOC_UI)
            bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.entryImOpenInTOC_UI,
                                                 str(int(oldEntryImOpenInTOC_UI) + 1))

            # update the links on the OM file
            imLinkOMPageDict = cls.readProperty(subsection, cls.PubProp.imLinkOMPageDict)

            # track all the changes after removal
            ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

            cls.rebuildEntriesBatch(subsection, imIdx)

    @classmethod
    def __copyEntry(cls, subsection, imIdx, targetSubsection, targetImIdx):
        import generalManger.generalManger as gm

        # track all the changes berore and after removal
        msg = "Before moving the subsection entries the subsection: '{0}_{1}'.".format(subsection, imIdx)
        log.autolog(msg)

        currBookName = sf.Wr.Manager.Book.getCurrBookName()

        imLinkDict = cls.readProperty(subsection, cls.PubProp.imLinkDict)

        #deal with the excercises
        oldEntryLinesPath = _upan.Paths.Entry.getAbs(currBookName, subsection, imIdx)

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(oldEntryLinesPath):
            newEntryLinesPath = _upan.Paths.Entry.getAbs(currBookName, 
                                                        targetSubsection,
                                                        targetImIdx)
            ocf.Wr.FsAppCalls.copyFile(oldEntryLinesPath, newEntryLinesPath)

            lines = efs.EntryInfoStructure.readProperty(subsection,
                                                        imIdx, 
                                                        efs.EntryInfoStructure.PubProp.entryLinesList)

            for lineIdx in range(len(lines) - 1, -1, -1):
                savePath = _upan.Paths.Entry.getAbs(currBookName, targetSubsection, targetImIdx)
                oldFilename = _upan.Names.Entry.Line.name(imIdx, lineIdx)
                oldPath = os.path.join(savePath, oldFilename)
                newFilename = _upan.Names.Entry.Line.name(targetImIdx, lineIdx)
                newPath = os.path.join(savePath, newFilename)
                # NOTE: we move since we moved the folder before and now only need to change the
                # images names
                if oldPath != newPath:
                    ocf.Wr.FsAppCalls.moveFile(oldPath, newPath)
            

            efs.EntryInfoStructure.updateProperty(targetSubsection,
                                                  targetImIdx, 
                                                  efs.EntryInfoStructure.PubProp.name,
                                                  targetImIdx)


        # copy the extra images
        extraImagesDict = cls.readProperty(subsection, cls.PubProp.extraImagesDict)
        extraImFilenames = []

        if imIdx in list(extraImagesDict.keys()):
            extraImNames = extraImagesDict[imIdx]

            if extraImNames != None:
                for extraImIdx in range(len(extraImNames)):
                    eImagePath = _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(currBookName,
                                                                                     subsection,
                                                                                     imIdx,
                                                                                     extraImIdx)
                    newEImagePath = _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(currBookName,
                                                                                     targetSubsection,
                                                                                     targetImIdx,
                                                                                     extraImIdx)

                    extraImFilenames.append([eImagePath,
                                             newEImagePath])

        for i in range(len(extraImFilenames)):
            ocf.Wr.FsAppCalls.copyFile(extraImFilenames[i][0], extraImFilenames[i][1])

        tex = tff.Wr.TexFileUtils.fromEntryToLatexTxt(targetImIdx, imLinkDict[imIdx])
        tff.Wr.TexFileUtils.fromTexToImage(tex,
                                           _upan.Paths.Screenshot.Images.getMainEntryTexImageAbs(currBookName,
                                                                                                 targetSubsection,
                                                                                                 targetImIdx),
                                           fixedWidth = 700)
        
        oldsSecreenshotPath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBookName, 
                                                                                 subsection,
                                                                                 imIdx)
        newsecreenshotPath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBookName, 
                                                                                targetSubsection,
                                                                                targetImIdx)
        
        ocf.Wr.FsAppCalls.copyFile(oldsSecreenshotPath, newsecreenshotPath)

        # deal with the links
        imGlobalLinksDict = cls.readProperty(subsection, cls.PubProp.imGlobalLinksDict)

        linksKeysSorted = list(imGlobalLinksDict.keys())
        linksKeysSorted.sort(key = int, reverse = True)

        # global links
        targetTopSection = targetSubsection.split(".")[0]

        if imIdx in list(imGlobalLinksDict.keys()):
            linksDict = imGlobalLinksDict[imIdx].copy()

            if type(linksDict) == dict:
                # update the return links in other subsections
                gm.GeneralManger.CopyGlLink(targetSubsection, targetImIdx, 
                                                subsection, imIdx)

        def updateProperty(propertyName):
            dataDict = cls.readProperty(subsection, propertyName)

            if imIdx not in list(dataDict.keys()):
                return

            data = dataDict[imIdx]
            targetDataDict = cls.readProperty(targetSubsection, propertyName)
            targetDataDict[targetImIdx] = data
            cls.updateProperty(targetSubsection, propertyName, targetDataDict)

        propertiesList = [
                         cls.PubProp.imLinkDict,
                         cls.PubProp.imLinkOMPageDict,
                         cls.PubProp.extraImagesDict,
                         cls.PubProp.origMatNameDict,
                         cls.PubProp.tocWImageDict,
                         cls.PubProp.imagesGroupDict,
                         cls.PubProp.imageText,
                         cls.PubProp.extraImText,
                         cls.PubProp.textOnly,
                         cls.PubProp.wikiPages,
                         cls.PubProp.videoPosition,
                         cls.PubProp.leadingEntry,
                         cls.PubProp.showSubentries,
                         ]

        imageUIResize = cls.readProperty(subsection, cls.PubProp.imageUIResize)
        imageUIResize = {k:v for k,v in imageUIResize.items() if int(k.split("_")[0]) == int(imIdx)}

        targetImageUIResize = cls.readProperty(targetSubsection, cls.PubProp.imageUIResize)

        for k,v in imageUIResize.items():
            if len(k.split("_")) == 2:
                targetImageUIResize[targetImIdx + "_" + k.split("_")[1]] = v
            else:
                targetImageUIResize[targetImIdx] = v

        cls.updateProperty(targetSubsection, cls.PubProp.imageUIResize, targetImageUIResize)

        figuresData = cls.readProperty(subsection, cls.PubProp.figuresData)
        figuresData = {k:v for k,v in figuresData.items() if int(k.split("_")[0]) == int(imIdx)}

        targetFiguresData = cls.readProperty(targetSubsection, cls.PubProp.figuresData)

        for k,v in figuresData.items():
            if len(k.split("_")) == 2:
                targetFiguresData[targetImIdx + "_" + k.split("_")[1]] = v
            else:
                targetFiguresData[targetImIdx] = v

        cls.updateProperty(targetSubsection, cls.PubProp.figuresData, targetFiguresData)

        figuresLabelsData = cls.readProperty(subsection, cls.PubProp.figuresLabelsData)
        figuresLabelsData = {k:v for k,v in figuresLabelsData.items() if int(k.split("_")[0]) == int(imIdx)}

        targetFiguresLabelsData = cls.readProperty(targetSubsection, cls.PubProp.figuresLabelsData)

        for k,v in figuresLabelsData.items():
            if len(k.split("_")) == 2:
                targetFiguresLabelsData[targetImIdx + "_" + k.split("_")[1]] = v
            else:
                targetFiguresLabelsData[targetImIdx] = v

        cls.updateProperty(targetSubsection, cls.PubProp.figuresLabelsData, targetFiguresLabelsData)

        for p in propertiesList:
            updateProperty(p)

        # track all the changes berore and after removal
        msg = "After copying the entry: '{0}_{1}'.".format(subsection, imIdx)
        log.autolog(msg)

    @classmethod
    def removeExtraIm(cls, subsection, mainImIdx, eImIdx = None):
        def __updateFile(filepath, oldMarker, newMarker):
            lines = []

            with open(filepath, "r") as f:
                lines = f.readlines()

            for i in range(len(lines)):
                if oldMarker in lines[i]:
                    if newMarker == "":
                        lines[i] = ""
                    else:
                        lines[i] = lines[i].replace(oldMarker, newMarker)

            with open(filepath, "w") as f:
                f.writelines(lines)

        currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        extraImagesDict = cls.readProperty(subsection, cls.PubProp.extraImagesDict, currBookPath)
        extraImTextDict = cls.readProperty(subsection, cls.PubProp.extraImText, currBookPath)
        imageUIResize = cls.readProperty(subsection, cls.PubProp.imageUIResize, currBookPath)
        figuresData = cls.readProperty(subsection, cls.PubProp.figuresData, currBookPath)
        figuresLabelsData = cls.readProperty(subsection, cls.PubProp.figuresLabelsData, currBookPath)
        bookCodeFile = cls.readProperty(subsection, cls.PubProp.bookCodeFile, currBookPath)
        subsectionCodeFile = cls.readProperty(subsection, cls.PubProp.subsectionCodeFile, currBookPath)

        eImList:list = extraImagesDict.pop(mainImIdx).copy()

        if extraImTextDict.get(mainImIdx) != None:
            eImTextsList:list = extraImTextDict.pop(mainImIdx).copy()
        else:
            eImTextsList:list = []

        if eImIdx != None:
            if bookCodeFile.get(mainImIdx + "_" + str(eImIdx)) != None:
                bookCodePath = _upan.Paths.Book.Code.getAbs(currBookPath)
                relFilepath = bookCodeFile.get(mainImIdx + "_" + str(eImIdx))
                filepath = os.path.join(bookCodePath, relFilepath)
                marker = _upan.Names.codeLineMarkerBook(subsection, mainImIdx + "_" + str(eImIdx))
                __updateFile(filepath, marker, "")
            if subsectionCodeFile.get(mainImIdx + "_" + str(eImIdx)) != None:
                bookCodePath = _upan.Paths.Section.getCodeRootAbs(currBookPath)
                relFilepath = subsectionCodeFile.get(mainImIdx + "_" + str(eImIdx))
                filepath = os.path.join(bookCodePath, relFilepath)
                marker = _upan.Names.codeLineMarkerSubsection(subsection, mainImIdx + "_" + str(eImIdx))
                __updateFile(filepath, marker, "")

            try:
                eImList.pop(eImIdx)
                eImTextsList.pop(eImIdx)
            except:
                pass

            if imageUIResize.get(mainImIdx + "_" + str(eImIdx)) != None:
                imageUIResize.pop(mainImIdx + "_" + str(eImIdx))
            if figuresData.get(mainImIdx + "_" + str(eImIdx)) != None:
                figuresData.pop(mainImIdx + "_" + str(eImIdx))
            if figuresLabelsData.get(mainImIdx + "_" + str(eImIdx)) != None:
                figuresLabelsData.pop(mainImIdx + "_" + str(eImIdx))
            if bookCodeFile.get(mainImIdx + "_" + str(eImIdx)) != None:
                bookCodeFile.pop(mainImIdx + "_" + str(eImIdx))
            if subsectionCodeFile.get(mainImIdx + "_" + str(eImIdx)) != None:
                subsectionCodeFile.pop(mainImIdx + "_" + str(eImIdx))

            extraImFilepath = _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(currBookPath,
                                                                                    subsection,
                                                                                    mainImIdx,
                                                                                    eImIdx)
            ocf.Wr.FsAppCalls.deleteFile(extraImFilepath)

            extraImCodeFilepath:str = _upan.Paths.Entry.getCodeProjAbs(currBookPath, subsection, mainImIdx)
            codeFolderbaseName = _upan.Names.codeProjectBaseName()
            currExtraImCodeFilepath = extraImCodeFilepath.replace(codeFolderbaseName,
                                                                      codeFolderbaseName + "_" + str(eImIdx))

            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(currExtraImCodeFilepath):
                ocf.Wr.FsAppCalls.removeDir(currExtraImCodeFilepath)

            for i in range(eImIdx, len(eImList)):
                # remove entry code project

                currExtraImCodeFilepath = extraImCodeFilepath.replace(codeFolderbaseName,
                                                                      codeFolderbaseName + "_" + str(i))
                nextExtraImCodeFilepath = extraImCodeFilepath.replace(codeFolderbaseName,
                                                                      codeFolderbaseName + "_" + str(i + 1))

                if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(nextExtraImCodeFilepath):
                    ocf.Wr.FsAppCalls.moveFolder(nextExtraImCodeFilepath, currExtraImCodeFilepath)

                if imageUIResize.get(mainImIdx + "_" + str(i + 1)) != None:
                    imageUIResize[mainImIdx + "_" + str(i)] =\
                                                            imageUIResize[mainImIdx + "_" + str(i + 1)]
                    imageUIResize.pop(mainImIdx + "_" + str(i + 1))

                if figuresData.get(mainImIdx + "_" + str(i + 1)) != None:
                    figuresData[mainImIdx + "_" + str(i)] =\
                                                            figuresData[mainImIdx + "_" + str(i + 1)]
                    figuresData.pop(mainImIdx + "_" + str(i + 1))

                if figuresLabelsData.get(mainImIdx + "_" + str(i + 1)) != None:
                    figuresLabelsData[mainImIdx + "_" + str(i)] =\
                                                            figuresLabelsData[mainImIdx + "_" + str(i + 1)]
                    figuresLabelsData.pop(mainImIdx + "_" + str(i + 1))

                if bookCodeFile.get(mainImIdx + "_" + str(i + 1)) != None:
                    bookCodeFile[mainImIdx + "_" + str(i)] =\
                                                            bookCodeFile[mainImIdx + "_" + str(i + 1)]
                    relFilepath = bookCodeFile.get(mainImIdx + "_" + str(i + 1)) 
                    bookCodeFile.pop(mainImIdx + "_" + str(i + 1))
                    bookCodePath = _upan.Paths.Book.Code.getAbs(currBookPath)
                    filepath = os.path.join(bookCodePath, relFilepath)
                    newMarker = _upan.Names.codeLineMarkerBook(subsection, mainImIdx + "_" + str(i + 1))
                    oldMarker = _upan.Names.codeLineMarkerBook(subsection, mainImIdx + "_" + str(i))
                    tempMarker = _upan.Names.codeLineMarkerBook(subsection, mainImIdx + "_" + str(100))
                    __updateFile(filepath, oldMarker, tempMarker)
                    __updateFile(filepath, newMarker, oldMarker)
                    __updateFile(filepath, tempMarker, newMarker)

                if subsectionCodeFile.get(mainImIdx + "_" + str(i + 1)) != None:
                    subsectionCodeFile[mainImIdx + "_" + str(i)] =\
                                                            subsectionCodeFile[mainImIdx + "_" + str(i + 1)]
                    relFilepath = subsectionCodeFile.get(mainImIdx + "_" + str(i + 1)) 
                    subsectionCodeFile.pop(mainImIdx + "_" + str(i + 1))
                    bookCodePath = _upan.Paths.Section.getCodeRootAbs(currBookPath)
                    filepath = os.path.join(bookCodePath, relFilepath)
                    newMarker = _upan.Names.codeLineMarkerSubsection(subsection, mainImIdx + "_" + str(i + 1))
                    oldMarker = _upan.Names.codeLineMarkerSubsection(subsection, mainImIdx + "_" + str(i))
                    tempMarker = _upan.Names.codeLineMarkerSubsection(subsection, mainImIdx + "_" + str(100))
                    __updateFile(filepath, oldMarker, tempMarker)
                    __updateFile(filepath, newMarker, oldMarker)
                    __updateFile(filepath, tempMarker, newMarker)

                sourceExtraImFilepath = \
                    _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(currBookPath,
                                                                        subsection,
                                                                        mainImIdx,
                                                                        i + 1)
                targetextraImFilepath = \
                    _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(currBookPath,
                                                                        subsection,
                                                                        mainImIdx,
                                                                        i)
                ocf.Wr.FsAppCalls.moveFile(sourceExtraImFilepath, targetextraImFilepath)
            
            entryFsPath = _upan.Paths.Entry.getAbs(currBookPath, subsection, mainImIdx)

            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryFsPath):
                entryNotesList:dict = efs.EntryInfoStructure.readProperty(subsection,
                                                                    mainImIdx,
                                                                    efs.EntryInfoStructure.PubProp.entryNotesList,
                                                                    currBookPath)
                eImIdxStr = str(eImIdx + 1)

                if entryNotesList.get(eImIdxStr) != None:
                    entryNotesList.pop(eImIdxStr)

                sourceFile = _upan.Paths.Entry.NoteImage.getAbs(currBookPath, subsection, mainImIdx, eImIdxStr)
                ocf.Wr.FsAppCalls.deleteFile(sourceFile)

                sortedKeys = list(entryNotesList.keys())
                sortedKeys.sort(key = lambda k: int(k))
                for k in sortedKeys:
                    if int(k) > int(eImIdxStr):
                        val = entryNotesList.pop(k)
                        entryNotesList[str(int(k) - 1)] = val
                        destFile = _upan.Paths.Entry.NoteImage.getAbs(currBookPath, subsection, mainImIdx, str(int(k) - 1))
                        sourceFile = _upan.Paths.Entry.NoteImage.getAbs(currBookPath, subsection, mainImIdx, k)
                        ocf.Wr.FsAppCalls.moveFile(sourceFile, destFile)

                efs.EntryInfoStructure.updateProperty(subsection, mainImIdx,
                                                        efs.EntryInfoStructure.PubProp.entryNotesList,
                                                        entryNotesList,
                                                        currBookPath)

        # NOTE: this is left here for 
        # elif eImName != None:
        #     eImList.remove(eImName)
        #     eImTextsList.remove(eImName)

        if eImList != []:
            extraImagesDict[mainImIdx] = eImList
        if eImTextsList != []:
            extraImTextDict[mainImIdx] = eImTextsList

        cls.updateProperty(subsection, cls.PubProp.extraImagesDict, extraImagesDict, currBookPath)
        cls.updateProperty(subsection, cls.PubProp.extraImText, extraImTextDict, currBookPath)
        cls.updateProperty(subsection, cls.PubProp.imageUIResize, imageUIResize, currBookPath)
        cls.updateProperty(subsection, cls.PubProp.figuresData, figuresData, currBookPath)
        cls.updateProperty(subsection, cls.PubProp.figuresLabelsData, figuresLabelsData, currBookPath)
        cls.updateProperty(subsection, cls.PubProp.bookCodeFile, bookCodeFile, currBookPath)
        cls.updateProperty(subsection, cls.PubProp.subsectionCodeFile, subsectionCodeFile, currBookPath)

    @classmethod
    def moveExtraIm(cls, subsection, mainImIdx, eImIdx, destEimIdx):
        def __updateFile(filepath, oldMarker, newMarker):
            lines = []

            with open(filepath, "r") as f:
                lines = f.readlines()

            for i in range(len(lines)):
                if oldMarker in lines[i]:
                    if newMarker == "":
                        lines[i] = ""
                    else:
                        lines[i] = lines[i].replace(oldMarker, newMarker)

            with open(filepath, "w") as f:
                f.writelines(lines)

        currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        extraImagesDict = cls.readProperty(subsection, cls.PubProp.extraImagesDict, currBookPath)
        extraImTextDict = cls.readProperty(subsection, cls.PubProp.extraImText, currBookPath)
        imageUIResize = cls.readProperty(subsection, cls.PubProp.imageUIResize, currBookPath)
        figuresData = cls.readProperty(subsection, cls.PubProp.figuresData, currBookPath)
        figuresLabelsData = cls.readProperty(subsection, cls.PubProp.figuresLabelsData, currBookPath)
        bookCodeFile = cls.readProperty(subsection, cls.PubProp.bookCodeFile, currBookPath)
        subsectionCodeFile = cls.readProperty(subsection, cls.PubProp.subsectionCodeFile, currBookPath)

        # update markers
        if bookCodeFile.get(mainImIdx + "_" + str(eImIdx)) != None:
            oldRelFilepath = bookCodeFile.get(mainImIdx + "_" + str(eImIdx)) 
            bookCodePath = _upan.Paths.Book.Code.getAbs(currBookPath)
            filepath = os.path.join(bookCodePath, oldRelFilepath)
            newMarker = _upan.Names.codeLineMarkerBook(subsection, mainImIdx + "_" + str(destEimIdx))
            oldMarker = _upan.Names.codeLineMarkerBook(subsection, mainImIdx + "_" + str(eImIdx))
            tempMarker = _upan.Names.codeLineMarkerBook(subsection, mainImIdx + "_" + str(100))

            if bookCodeFile.get(mainImIdx + "_" + str(destEimIdx)) != None:
                newRelFilepath = bookCodeFile.get(mainImIdx + "_" + str(destEimIdx)) 
                destFilepath = os.path.join(bookCodePath, newRelFilepath)
                __updateFile(filepath, oldMarker, tempMarker)
                __updateFile(destFilepath, newMarker, oldMarker)
                __updateFile(filepath, tempMarker, newMarker)
            else:
                __updateFile(filepath, oldMarker, newMarker)

        if subsectionCodeFile.get(mainImIdx + "_" + str(eImIdx)) != None:
            oldRelFilepath = subsectionCodeFile.get(mainImIdx + "_" + str(eImIdx)) 
            bookCodePath = _upan.Paths.Section.getCodeRootAbs(currBookPath)
            filepath = os.path.join(bookCodePath, oldRelFilepath)
            newMarker = _upan.Names.codeLineMarkerSubsection(subsection, mainImIdx + "_" + str(destEimIdx))
            oldMarker = _upan.Names.codeLineMarkerSubsection(subsection, mainImIdx + "_" + str(eImIdx))
            tempMarker = _upan.Names.codeLineMarkerSubsection(subsection, mainImIdx + "_" + str(100))

            if subsectionCodeFile.get(mainImIdx + "_" + str(destEimIdx)) != None:
                newRelFilepath = subsectionCodeFile.get(mainImIdx + "_" + str(destEimIdx)) 
                destFilepath = os.path.join(bookCodePath, newRelFilepath)
                __updateFile(filepath, oldMarker, tempMarker)
                __updateFile(destFilepath, newMarker, oldMarker)
                __updateFile(filepath, tempMarker, newMarker)
            else:
                __updateFile(filepath, oldMarker, newMarker)

        entryFsPath = _upan.Paths.Entry.getAbs(currBookPath, subsection, mainImIdx)

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryFsPath):
            entryNotesList:dict = efs.EntryInfoStructure.readProperty(subsection,
                                                                mainImIdx,
                                                                efs.EntryInfoStructure.PubProp.entryNotesList,
                                                                currBookPath)
            destEimIdxStr = str(destEimIdx + 1)
            eImIdxStr = str(eImIdx + 1)

            if (entryNotesList.get(eImIdxStr) != None)\
                and (entryNotesList.get(destEimIdxStr) != None):
                entryNotesList[eImIdxStr], entryNotesList[destEimIdxStr] = \
                    entryNotesList[destEimIdxStr], entryNotesList[eImIdxStr]
            elif entryNotesList.get(eImIdxStr) != None:
                entryNotesList[destEimIdxStr] = entryNotesList[eImIdxStr]
                entryNotesList.pop(eImIdxStr)
            elif entryNotesList.get(destEimIdxStr) != None:
                entryNotesList[eImIdxStr] = entryNotesList[destEimIdxStr]
                entryNotesList.pop(destEimIdxStr)

            destFile = _upan.Paths.Entry.NoteImage.getAbs(currBookPath, subsection, mainImIdx, destEimIdxStr)
            sourceFile = _upan.Paths.Entry.NoteImage.getAbs(currBookPath, subsection, mainImIdx, eImIdxStr)
            tempFile = _upan.Paths.Entry.NoteImage.getAbs(currBookPath, subsection, mainImIdx, "100")

            ocf.Wr.FsAppCalls.moveFile(sourceFile, tempFile)
            ocf.Wr.FsAppCalls.moveFile(destFile, sourceFile)
            ocf.Wr.FsAppCalls.moveFile(tempFile, destFile)
            ocf.Wr.FsAppCalls.deleteFile(tempFile)

            efs.EntryInfoStructure.updateProperty(subsection, mainImIdx,
                                                    efs.EntryInfoStructure.PubProp.entryNotesList,
                                                    entryNotesList,
                                                    currBookPath)

        eImList:list = extraImagesDict.pop(mainImIdx).copy()

        if (int(eImIdx) >= len(eImList)) or (int(destEimIdx) >= len(eImList))\
            or ((int(eImIdx) < 0)) or ((int(destEimIdx) < 0)):
            return

        eImTextsList:list = extraImTextDict.pop(mainImIdx).copy()

        if eImIdx != None:
            eImList[eImIdx], eImList[destEimIdx] = \
                eImList[destEimIdx], eImList[int(eImIdx)]
            eImTextsList[eImIdx], eImTextsList[destEimIdx] = \
                eImTextsList[destEimIdx], eImTextsList[int(eImIdx)]

            sourceSizeEImIdx =  mainImIdx + "_" + str(eImIdx)
            destSizeEImIdx =  mainImIdx + "_" + str(destEimIdx)

            if (imageUIResize.get(sourceSizeEImIdx) != None)\
                and (imageUIResize.get(destSizeEImIdx) != None):
                imageUIResize[sourceSizeEImIdx], imageUIResize[destSizeEImIdx] = \
                    imageUIResize[destSizeEImIdx], imageUIResize[sourceSizeEImIdx]
            elif imageUIResize.get(sourceSizeEImIdx) != None:
                imageUIResize[destSizeEImIdx] = imageUIResize[sourceSizeEImIdx]
                imageUIResize.pop(sourceSizeEImIdx)
            elif imageUIResize.get(destSizeEImIdx) != None:
                imageUIResize[sourceSizeEImIdx] = imageUIResize[destSizeEImIdx]
                imageUIResize.pop(destSizeEImIdx)

            if (figuresLabelsData.get(sourceSizeEImIdx) != None)\
                and (figuresLabelsData.get(destSizeEImIdx) != None):
                figuresLabelsData[sourceSizeEImIdx], figuresLabelsData[destSizeEImIdx] = \
                    figuresLabelsData[destSizeEImIdx], figuresLabelsData[sourceSizeEImIdx]
            elif figuresLabelsData.get(sourceSizeEImIdx) != None:
                figuresLabelsData[destSizeEImIdx] = figuresLabelsData[sourceSizeEImIdx]
                figuresLabelsData.pop(sourceSizeEImIdx)
            elif figuresLabelsData.get(destSizeEImIdx) != None:
                figuresLabelsData[sourceSizeEImIdx] = figuresLabelsData[destSizeEImIdx]
                figuresLabelsData.pop(destSizeEImIdx)

            if (figuresData.get(sourceSizeEImIdx) != None)\
                and (figuresData.get(destSizeEImIdx) != None):
                figuresData[sourceSizeEImIdx], figuresData[destSizeEImIdx] = \
                    figuresData[destSizeEImIdx], figuresData[sourceSizeEImIdx]
            elif figuresData.get(sourceSizeEImIdx) != None:
                figuresData[destSizeEImIdx] = figuresData[sourceSizeEImIdx]
                figuresData.pop(sourceSizeEImIdx)
            elif figuresData.get(destSizeEImIdx) != None:
                figuresData[sourceSizeEImIdx] = figuresData[destSizeEImIdx]
                figuresData.pop(destSizeEImIdx)

            if (bookCodeFile.get(sourceSizeEImIdx) != None)\
                and (bookCodeFile.get(destSizeEImIdx) != None):
                bookCodeFile[sourceSizeEImIdx], bookCodeFile[destSizeEImIdx] = \
                    bookCodeFile[destSizeEImIdx], bookCodeFile[sourceSizeEImIdx]
            elif bookCodeFile.get(sourceSizeEImIdx) != None:
                bookCodeFile[destSizeEImIdx] = bookCodeFile[sourceSizeEImIdx]
                bookCodeFile.pop(sourceSizeEImIdx)
            elif bookCodeFile.get(destSizeEImIdx) != None:
                bookCodeFile[sourceSizeEImIdx] = bookCodeFile[destSizeEImIdx]
                bookCodeFile.pop(destSizeEImIdx)

            if (subsectionCodeFile.get(sourceSizeEImIdx) != None)\
                and (subsectionCodeFile.get(destSizeEImIdx) != None):
                subsectionCodeFile[sourceSizeEImIdx], subsectionCodeFile[destSizeEImIdx] = \
                    subsectionCodeFile[destSizeEImIdx], subsectionCodeFile[sourceSizeEImIdx]
            elif subsectionCodeFile.get(sourceSizeEImIdx) != None:
                subsectionCodeFile[destSizeEImIdx] = subsectionCodeFile[sourceSizeEImIdx]
                subsectionCodeFile.pop(sourceSizeEImIdx)
            elif subsectionCodeFile.get(destSizeEImIdx) != None:
                subsectionCodeFile[sourceSizeEImIdx] = subsectionCodeFile[destSizeEImIdx]
                subsectionCodeFile.pop(destSizeEImIdx)

        if eImList != []:
            extraImagesDict[mainImIdx] = eImList
        if eImTextsList != []:
            extraImTextDict[mainImIdx] = eImTextsList
        
        tempExtraImFilepath = _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(currBookPath,
                                                                                  subsection,
                                                                                  mainImIdx,
                                                                                  int(eImIdx) + 100)
        extraImFilepath = _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(currBookPath,
                                                                                  subsection,
                                                                                  mainImIdx,
                                                                                  eImIdx)
        nextExtraImFilepath = _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(currBookPath,
                                                                                  subsection,
                                                                                  mainImIdx,
                                                                                  destEimIdx)
        ocf.Wr.FsAppCalls.moveFile(extraImFilepath, tempExtraImFilepath)
        ocf.Wr.FsAppCalls.moveFile(nextExtraImFilepath, extraImFilepath)
        ocf.Wr.FsAppCalls.moveFile(tempExtraImFilepath, nextExtraImFilepath)

        codeFolderbaseName = _upan.Names.codeProjectBaseName()

        tempExtraImCodeFilepath:str = _upan.Paths.Entry.getCodeProjAbs(currBookPath, subsection, mainImIdx)
        tempExtraImCodeFilepath = tempExtraImCodeFilepath.replace(codeFolderbaseName,
                                                                  codeFolderbaseName + "_" + str(int(eImIdx) + 100))
        extraImCodeFilepath:str = _upan.Paths.Entry.getCodeProjAbs(currBookPath, subsection, mainImIdx)
        extraImCodeFilepath = extraImCodeFilepath.replace(codeFolderbaseName,
                                                          codeFolderbaseName + "_" + str(eImIdx))
        nextExtraImCodeFilepath:str = _upan.Paths.Entry.getCodeProjAbs(currBookPath, subsection, mainImIdx)
        nextExtraImCodeFilepath = nextExtraImCodeFilepath.replace(codeFolderbaseName,
                                                                  codeFolderbaseName + "_" + str(destEimIdx))

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(nextExtraImCodeFilepath)\
           and ocf.Wr.FsAppCalls.checkIfFileOrDirExists(extraImCodeFilepath):
            ocf.Wr.FsAppCalls.moveFolder(extraImCodeFilepath, tempExtraImCodeFilepath)
            ocf.Wr.FsAppCalls.moveFolder(nextExtraImCodeFilepath, extraImCodeFilepath)
            ocf.Wr.FsAppCalls.moveFolder(tempExtraImCodeFilepath, nextExtraImCodeFilepath)
        elif ocf.Wr.FsAppCalls.checkIfFileOrDirExists(extraImCodeFilepath):
            ocf.Wr.FsAppCalls.moveFolder(extraImCodeFilepath, nextExtraImCodeFilepath)

        cls.updateProperty(subsection, cls.PubProp.extraImagesDict, extraImagesDict, currBookPath)
        cls.updateProperty(subsection, cls.PubProp.extraImText, extraImTextDict, currBookPath)
        cls.updateProperty(subsection, cls.PubProp.imageUIResize, imageUIResize, currBookPath)
        cls.updateProperty(subsection, cls.PubProp.figuresData, figuresData, currBookPath)
        cls.updateProperty(subsection, cls.PubProp.figuresLabelsData, figuresLabelsData, currBookPath)
        cls.updateProperty(subsection, cls.PubProp.bookCodeFile, bookCodeFile, currBookPath)
        cls.updateProperty(subsection, cls.PubProp.subsectionCodeFile, subsectionCodeFile, currBookPath)

    @classmethod
    def getEntryImText(cls, subsection, imIdx):
        currBookpath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        entryImTexts = cls.readProperty(subsection, cls.PubProp.imageText, currBookpath)
        entryEImTextDict = cls.readProperty(subsection, cls.PubProp.extraImText, currBookpath)

        if entryImTexts == None:
            entryImText = ""
        elif imIdx not in list(entryImTexts.keys()):
            entryImText = ""                  
        else:
            entryImText = entryImTexts[imIdx].replace("\n", "")
        
        if imIdx in list(entryEImTextDict.keys()):
            for t in  entryEImTextDict[imIdx]:
                entryImText += t

        return entryImText

    @classmethod
    def rebuildEntriesBatch(cls, subsection, startImIdx):
        imLinkDict = cls.readProperty(subsection, cls.PubProp.imLinkDict)

        for k, v in imLinkDict.items():
            if int(k) >= int(startImIdx):
                imTexOnly = cls.readProperty(subsection, cls.PubProp.textOnly)[k]
                cls.rebuildEntryLatex(subsection,
                                    k,
                                    v,
                                    imTexOnly)

    @classmethod
    def rebuildEntryLatex(cls, 
                          subsection,
                          imIdx,
                          linkText,
                          textonly):
        currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        entryImgPath = _upan.Paths.Screenshot.Images.getMainEntryTexImageAbs(currBookPath, 
                                                                        subsection, 
                                                                        imIdx)

        tex = tff.Wr.TexFileUtils.fromEntryToLatexTxt(imIdx, linkText)

        tff.Wr.TexFileUtils.fromTexToImage(tex, entryImgPath, fixedWidth = 700)

    @classmethod
    def rebuildTopSectionLatex(cls, topSection,
                               createPrettyTopSection):
        currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        topsSctionImgPath = _upan.Paths.Screenshot.Images.getTopSectionEntryImageAbs(currBookPath, 
                                                                                    topSection)
        tex = tff.Wr.TexFileUtils.formatEntrytext(createPrettyTopSection(topSection))

        return tff.Wr.TexFileUtils.fromTexToImage(tex, topsSctionImgPath, padding = 20, imageColor = "#ed8a82")

    @classmethod
    def rebuildSubsectionImOnlyLatex(cls, subsection,
                                        createPrettySubSection):
        tex = tff.Wr.TexFileUtils.formatEntrytext(createPrettySubSection(subsection))
        subsectionImgPath = _upan.Paths.Screenshot.Images.getSubsectionEntryImageAbs(
                                                        sf.Wr.Manager.Book.getCurrBookName(), 
                                                        subsection)

        currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        subsectionLevel = int(cls.readProperty(subsection, cls.PubProp.level, currBookPath), 16)
        color = hex(int("4287f5", 16) >> subsectionLevel)[2:]

        if len(color) < 6:
            color = "8" + color

        return tff.Wr.TexFileUtils.fromTexToImage(tex, subsectionImgPath, padding = 10, imageColor = f"#{color}")

    @classmethod
    def rebuildGroupOnlyImOnlyLatex(cls, subsection,
                                        groupName,
                                        gi = None):
        currBookpath = sf.Wr.Manager.Book.getCurrBookFolderPath()

        if gi == None:
            gi = str(list(cls.readProperty(subsection,
                                        cls.PubProp.imagesGroupsList,
                                        currBookpath).keys()).index(groupName))

        groupImgPath = _upan.Paths.Screenshot.Images.getGroupImageAbs(sf.Wr.Manager.Book.getCurrBookName(), 
                                                                    subsection,
                                                                    gi)
        tex = tff.Wr.TexFileUtils.formatEntrytext(groupName)

        return tff.Wr.TexFileUtils.fromTexToImage(tex, groupImgPath, 
                                                  padding = 10, imageColor="#109464",
                                                  imSize = 600)

    @classmethod
    def rebuildSubsectionLatex(cls, subsection,
                               fromGroupNameToFilename,
                               createPrettySubSection,
                               createPrettyTopSection):
        # rebuild entries
        cls.rebuildEntriesBatch(subsection, "0")

        groups = cls.readProperty(subsection, cls.PubProp.imagesGroupsList)

        # rebuild groups
        for g in groups:
            cls.rebuildGroupOnlyImOnlyLatex(subsection,
                                            g)

        # subsection image
        cls.rebuildSubsectionImOnlyLatex(subsection,
                                         createPrettySubSection)

        # top section image
        topSection = subsection.split(".")[0]
        cls.rebuildTopSectionLatex(topSection,
                                   createPrettyTopSection)

        # rebuild web links
        imGlLinkDict = cls.readProperty(subsection, cls.PubProp.imGlobalLinksDict)
        currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

        for k, ld in imGlLinkDict.items():
            if ld != _u.Token.NotDef.str_t:
                for ln, lk in ld.items():
                    if "http" in lk:
                        latexTxt = tff.Wr.TexFileUtils.formatEntrytext(ln)
                        linkFilepath = _upan.Paths.Screenshot.Images.getWebLinkImageAbs(currBookPath,
                                                                                        subsection,
                                                                                        k,
                                                                                        ln)
                        tff.Wr.TexFileUtils.fromTexToImage(latexTxt, linkFilepath)

    @classmethod
    def __removeLinksForSubsection(cls, subsection):
        glLinks = cls.readProperty(subsection, cls.PubProp.imGlobalLinksDict)
        for entryIdx in list(glLinks.keys()):
            if type(glLinks[entryIdx]) == dict:
                sourceLinks = glLinks[entryIdx].copy()

                for sl, slfull in sourceLinks.items():
                    if "KIK:" in slfull:
                        slsubsection = sl.split("_")[0]
                        slImIdx = sl.split("_")[1]
                        gm.GeneralManger.RemoveGlLink(slsubsection, subsection, entryIdx, slImIdx)

    @classmethod
    def removeSection(cls, sectionPath):
        # removing the links
        cls.__removeLinksForSubsection(sectionPath)

        subsections = bfs.BookInfoStructure.getSubsectionsList(sectionPath)

        for subsection in subsections:
            cls.__removeLinksForSubsection(subsection)
            

        currBookpath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        cls.__deleteSectionFiles(currBookpath,
                                 sectionPath)

    @classmethod
    def readProperty(cls, sectionPath, propertyName, bookPath = None):
        if bookPath == None:
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        
        fullPathToSection = _upan.Paths.Section.JSON.getAbs(bookPath, sectionPath)

        sectionPathSeparator = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator)
        
        sectionPathForTemplate = sectionPath.replace(sectionPathSeparator, "_")

        if sectionPathForTemplate == _u.Token.NotDef.str_t:
            return _u.Token.NotDef.str_t
        else:
            try:
                out = _u.JSON.readProperty(fullPathToSection, 
                                            propertyName)
            except:
                defaultData = cls.getDefaultTemplateValue(propertyName)
                out = defaultData[0]
                parentpropertyName = None if defaultData[1] == "" else defaultData[1]
                _u.JSON.createProperty(fullPathToSection, propertyName, parentpropertyName, out)
                    
            # if type(out) == dict:
            #     if out != _u.Token.NotDef.dict_t:
            #         if _u.Token.NotDef.str_t in out.keys():
            #             out.pop(_u.Token.NotDef.str_t, None)

            return out

    @classmethod
    def updateProperty(cls, sectionPath, propertyName, newValue, bookPath = None):
        if bookPath == None:
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

        template = cls._getTemplate()

        # sort the dict
        if (type(newValue) == dict) \
            and (propertyName in list(template[cls.PubProp.imageProp].keys())):
            keysSorted = list(newValue.keys())
            keysSorted.sort(key = int)
            newValue = {i: newValue[i] for i in keysSorted} 
        
        # if newValue != _u.Token.NotDef.dict_t:
        #     if type(newValue) == dict:
        #         if _u.Token.NotDef.str_t in newValue.keys():
        #             newValue.pop(_u.Token.NotDef.str_t, None)
        
        fullPathToSection = _upan.Paths.Section.JSON.getAbs(bookPath, sectionPath)

        _u.JSON.updateProperty(fullPathToSection, 
                            propertyName,
                            newValue)


class SectionCurrent:
    def getSubsectionsListForCurrTopSection():
        currSectionPath = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.currTopSection)
        childrensList = bfs.BookInfoStructure.getSubsectionsList(currSectionPath)
        return childrensList

    @classmethod
    def getSectionNameWprefix(cls):
        sectionPrefix = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix)
        currSection = cls.getSectionNameNoPrefix()
        if currSection == _u.Token.NotDef.str_t:
            return _u.Token.NotDef.str_t
        return sectionPrefix + "_" + currSection

    @classmethod
    def getSectionNameNoPrefix(cls):
        currSection = _upan.Current.Names.Section.name()
        return currSection

    @classmethod
    def getImIDX(cls):
        currSectionPath = _upan.Current.Names.Section.name()
        return l.ImIDX.get(currSectionPath)

    @classmethod
    def getCurrLinkIdxDict(cls):
        currSectionPath = _upan.Current.Names.Section.name()
        return l.LinkDict.get(currSectionPath)

    @classmethod
    def setImLinkAndIDX(cls, linkName, imIDX):
        currSectionPath = _upan.Current.Names.Section.name()
        l.LinkDict.set(currSectionPath, linkName, imIDX)