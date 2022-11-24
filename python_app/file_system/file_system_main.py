import os
import json
import shutil

import _utils._utils_main as _u
import _utils.logging as log


class TOCStructure:
    '''
    Keeps the toc for the sections and links to them.
    '''

    class PubPro:
        TEXT_MARKER = "[SECTION_TEXT]"
        START_MARKER = "[SECTION_START]" 
        FINISH_MARKER = "[SECTION_FINISH]"
        NAME_MARKER = "[SECTION_NAME]"
        CONTENT_MARKER = "[CONTENT_MARKER]"
        
        text_ID = "TOC_text"
        start_ID = "TOC_sectionStart"
        finish_ID = "TOC_sectionFinish"
        
        propertyToMarker = {
            text_ID: TEXT_MARKER,
            start_ID: START_MARKER,
            finish_ID: FINISH_MARKER
        }
 
        def getPropertyFormPath(path, propertyName):
            separator = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_path_separator_ID)
            sectionPrefix = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_prefix_ID)
            return sectionPrefix + "_" + path.replace(separator, "_") + propertyName

    @classmethod
    def createStructure(cls):
        os.system("mkdir -p " + cls._getTOCDirPath())
        
    @classmethod
    def addSection(cls, sectionPath):
        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_path_separator_ID)

        sectionPathList = sectionPath.split(sectionPathSeparator)
        
        for i,sectionName in enumerate(sectionPathList):
            sectionsList = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_ID)
            sectionData = BookInfoStructure.readProperty(sectionName)
            if sectionData == None:
                continue

            separator = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_path_separator_ID)
            topSectionName = sectionName.split(separator)[0]
            
            sectionsTOCLines = [""]
            
            if i == 0:
                pathToTemplates = os.getenv("BOOKS_TEMPLATES_PATH")
                _waitDummy = os.system("cp " + pathToTemplates + "/TOC_template.tex " + cls._getTOCFilePath(topSectionName))
            
            cls._getTOCLines(sectionData, sectionsTOCLines, 0)

            
            _u.replaceMarkerInFile(cls._getTOCFilePath(topSectionName), cls.PubPro.NAME_MARKER, topSectionName)
            _u.replaceMarkerInFile(cls._getTOCFilePath(topSectionName), cls.PubPro.CONTENT_MARKER, sectionsTOCLines[0])

    
    def _getTOCSectionNameFromSectionPath(sectionPath):
        prefix = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_prefix_ID)
        separator = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_path_separator_ID)
        return prefix + "_" + sectionPath.split(separator)[0]

    @classmethod
    def updateTOCfiles(cls, sectionPath, propertyName, newValue):
        oldPropertyValue = SectionInfoStructure.readProperty(sectionPath, propertyName)

        # update the TOC files
        sectionName = cls._getTOCSectionNameFromSectionPath(sectionPath)
        if oldPropertyValue != "":
            _u.replaceMarkerInFile(cls._getTOCFilePath(sectionName), "[" + oldPropertyValue + "]", "[" + newValue + "]", "[" + sectionPath + "]")
        else:
            marker = cls.PubPro.propertyToMarker[propertyName]
            _u.replaceMarkerInFile(cls._getTOCFilePath(sectionName), "[" + marker  + "]","[" + newValue + "]",  "[" + sectionPath + "]")

    @classmethod
    def _getTOCLines(cls, sectionsData, outLines, level):
        INTEMEDIATE_LINE = cls.PubPro.NAME_MARKER + ":\\\\\n"
        BOTTOM_LINE = "\TOCline{[" + cls.PubPro.TEXT_MARKER + \
            "] [" + cls.PubPro.NAME_MARKER + "]// [" + \
            cls.PubPro.START_MARKER + \
            "] - [" + cls.PubPro.FINISH_MARKER + "]}{[" + \
            cls.PubPro.START_MARKER + "]}" + \
            "\\\\\n"

        DEFAULT_PREFIX_SPACES = " " * 4 + level * " " * 4
    
        for name, section in sectionsData["sections"].items():
            if type(section) == dict:
                if section["sections"] == {}:
                    # add line
                    lineToAdd = DEFAULT_PREFIX_SPACES + BOTTOM_LINE.replace(cls.PubPro.NAME_MARKER, name)
                    outLines[0] = outLines[0] + lineToAdd
                else:
                    lineToAdd = DEFAULT_PREFIX_SPACES + INTEMEDIATE_LINE.replace(cls.PubPro.NAME_MARKER, name)
                    outLines[0] = outLines[0] + lineToAdd
                    cls._getTOCLines(section, outLines, level +1)
    
    def _getTOCDirPath():
        bookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
        return bookPath + BookInfoStructure.TOCbaseRelPath

    @classmethod
    def _getTOCFilePath(cls, topSectionName):
        secprefix = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_prefix_ID)
        tocFolderPath = cls._getTOCDirPath()
        if (os.path.isdir(tocFolderPath)):
            return os.path.join(tocFolderPath, "TOC_" + secprefix + "_" + topSectionName + ".tex")
        else:
            print("_getTOCFilePath - " + "the TOC filepath is not present.")
            print("Will create: " + tocFolderPath)
            _waitDummy = os.system("mkdir " + tocFolderPath)
            return os.path.join(tocFolderPath, "TOC_" + secprefix + "_" + topSectionName + ".tex")


class BookInfoStructure:
    '''
    The stucture keeps the info about the book
    '''

    bookInfoFoldefRelPath= "/bookInfo/"
    bookInfoFilename = "bookInfo.json"
    sectionsInfoBaseRelPath = "subsections/"
    sectionsInfoFilename = "sectionInfo.json"

    TOCbaseRelPath = "/TOC/"
    TOCFilename = "TOCinfo.json"

    currSectionFull_ID= "currChapterFull"# need to be removed
    
    class PubProp:
        version_ID = "version"
        sections_prefix_ID = "sections_prefix"
        sections_path_separator_ID = "sections_path_separator"
        sections_ID = "sections"
        
        #currState
        currentState_ID = "currentState"
        currentPage_ID = "currentPage"
        currTopSection_ID = "currTopSection"
        currSection_ID = "currSection"

        #imagesProperties
        imageProp_ID = "imageProp"
        imageContentFileMoveLinesNumber_ID = "imageContentFileMoveLinesNumber"
        imageTOCFileMoveLinesNumber_ID = "imageContentFileMoveLinesNumber"

    bookInfoTemplate = {
        PubProp.version_ID: "0.1",
        PubProp.sections_prefix_ID: "sec",
        PubProp.sections_path_separator_ID: ".",
        PubProp.sections_ID: {
        },
        PubProp.currentState_ID: {
            PubProp.currentPage_ID: "",
            PubProp.currSection_ID: "",
            PubProp.currTopSection_ID: ""
        },
        PubProp.imageProp_ID: {
            PubProp.imageContentFileMoveLinesNumber_ID: "20",
            PubProp.imageTOCFileMoveLinesNumber_ID: "0"
        }
    }

    @classmethod
    def createStructure(cls, bookInfoFilepath = ""):
        if bookInfoFilepath == "":
            bookInfoFilepath = cls._getAsbFilepath()
        
        expectedFileDir = os.path.join("/", *bookInfoFilepath.split("/")[:-1])
        
        log.autolog("The bookInfo structure was not present will create it at: " + expectedFileDir)
        if not os.path.exists(expectedFileDir):
            _waitDummy = os.makedirs(expectedFileDir)
        
        with open(bookInfoFilepath, "w+") as f:
            jsonObj = json.dumps(cls.bookInfoTemplate, indent = 4)
            f.write(jsonObj)

    @classmethod
    def addSection(cls, sectionPath):
        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_path_separator_ID)

        sectionPathList = sectionPath.split(sectionPathSeparator)
        relSectionPath = ""
        for i,p in enumerate(sectionPathList):
            prevRelSectionPath = relSectionPath
            relSectionPath += p if relSectionPath == "" else "." + p

            pathToTopSection = SectionInfoStructure._getSectionFilepath(relSectionPath)
            sectionFilepath = os.path.join(pathToTopSection, BookInfoStructure.sectionsInfoFilename)

            # update the book info
            bookInfoSections = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_ID)
            
            def addBookInfoSection(parentProperty):
                parentProperty[relSectionPath] = {
                    "path": sectionFilepath,
                    "sections": {}
                }
            def addBookInfoTopSection(parentProperty):
                parentProperty[relSectionPath] = {
                    "path": sectionFilepath,
                    "prevSubsectionPath":"",
                    "sections": {}
                }
            
            if i == 0:
                if relSectionPath not in bookInfoSections.keys():
                    parentProperty = bookInfoSections
                    addBookInfoTopSection(parentProperty)
            else:
                parentProperty = _u.DICT.readProperty(bookInfoSections, prevRelSectionPath)
                
                if (relSectionPath not in parentProperty["sections"].keys()) \
                    and (type(parentProperty) == dict \
                    and "sections" in parentProperty.keys()):
                    addBookInfoSection(parentProperty["sections"])
                
                _u.DICT.updateProperty(bookInfoSections, prevRelSectionPath, parentProperty)
            
            BookInfoStructure.updateProperty(BookInfoStructure.PubProp.sections_ID, bookInfoSections)

    @classmethod
    def _getRelFilepath(cls):
        return cls.bookInfoFoldefRelPath + cls.bookInfoFilename
    
    @classmethod
    def _getAsbFilepath(cls):
        bookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
        return bookPath + cls._getRelFilepath()

    @classmethod
    def readProperty(cls, property):
        return _u.JSON.readProperty(cls._getAsbFilepath(), property)

    @classmethod
    def updateProperty(cls, propertyName, newValue):
        _u.JSON.updateProperty(cls._getAsbFilepath(), propertyName, newValue)


class SectionInfoStructure:
    '''
    Structure to store sections and .tex files and images
    '''

    currStucturePath = ""

    # for later: add if the section should generate the pdf.
    # currPage_ID = "currentPage"
    # currImageID_ID = "currImageID"
    # currImageName_ID = "currImageName"
    # currLinkName_ID = "currLinkName"

    class PubProp:
        name_ID = "_name"
        startPage_ID = "_startPage"
        latestSubchapter_ID = "_latestSubchapter"
        subSections_ID = "_subSections"

        #imagesProperties
        imageProp_ID = "_imageProp"
        imageContentFileMoveLinesNumber_ID = "_imageContentFileMoveLinesNumber"
        imageTOCFileMoveLinesNumber_ID = "_imageContentFileMoveLinesNumber"
        imLinkDict_ID = "imLinkDict"

    class PrivProp:
        tocData_ID = "_tocData"

        level_ID = "_level"

        levelData_ID = "_levelData"
        levelData_depth_ID = "_depth"
        levelData_level_ID = "_level"

    sectionPrefixForTemplate = ""
    sectionPathForTemplate = ""

    @classmethod
    def _getTemplate(cls, depth, level):
        sectionInfoEntryPrefix = cls.sectionPathForTemplate
        sectionInfo_template = {
                sectionInfoEntryPrefix + cls.PubProp.name_ID: _u.notDefinedToken,
                sectionInfoEntryPrefix + cls.PubProp.startPage_ID: _u.notDefinedToken,
                sectionInfoEntryPrefix + cls.PubProp.latestSubchapter_ID: _u.notDefinedToken,
                # sectionInfoEntryPrefix + cls.PubProp.subSections_ID: [],
                sectionInfoEntryPrefix + cls.PrivProp.levelData_ID:{
                    sectionInfoEntryPrefix + cls.PrivProp.levelData_depth_ID: str(depth),
                    sectionInfoEntryPrefix + cls.PrivProp.levelData_level_ID: str(level),
                },
                sectionInfoEntryPrefix + cls.PrivProp.tocData_ID:{
                    sectionInfoEntryPrefix + TOCStructure.PubPro.text_ID: _u.notDefinedToken,
                    sectionInfoEntryPrefix + TOCStructure.PubPro.start_ID: _u.notDefinedToken,
                    sectionInfoEntryPrefix + TOCStructure.PubPro.finish_ID: _u.notDefinedToken
                },
                sectionInfoEntryPrefix + cls.PubProp.imageProp_ID: {
                    sectionInfoEntryPrefix + cls.PubProp.imageContentFileMoveLinesNumber_ID: _u.notDefinedToken,
                    sectionInfoEntryPrefix + cls.PubProp.imageTOCFileMoveLinesNumber_ID: _u.notDefinedToken,
                    sectionInfoEntryPrefix + cls.PubProp.imLinkDict_ID: _u.notDefinedDictToken
                }
                
        }
        return sectionInfo_template

    def getSectionJSONKeyPrefixFormPath(path):
        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_path_separator_ID) 
        secPrefix = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_prefix_ID)
        return secPrefix + "_" + path.replace(sectionPathSeparator, "_")   

    @classmethod
    def createStructure(cls):
        os.makedirs(cls._getPathToSectionsFolder())
        BookInfoStructure.updateProperty(BookInfoStructure.PubProp.currentPage_ID, _u.notDefinedToken)
        BookInfoStructure.updateProperty(BookInfoStructure.PubProp.currSection_ID, _u.notDefinedToken)
        BookInfoStructure.updateProperty(BookInfoStructure.PubProp.currTopSection_ID, _u.notDefinedToken)
        return

    @classmethod
    def addSection(cls, sectionPath):
        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_path_separator_ID) 

        numLevels = len(sectionPath.split(sectionPathSeparator))

        dirPathToSection = cls._getSectionFilepath(sectionPath)

        if not os.path.exists(dirPathToSection):

            print("SectionInfoStructure.addSection - the sections structure was not present will create it.")
            print("Creating path: " + dirPathToSection)
            
            # create files and folders
            sectionFolderName = dirPathToSection.split("/")[-1]
            _waitDummy = os.system("mkdir -p " + dirPathToSection)
            _waitDummy = os.makedirs(os.path.join(dirPathToSection, sectionFolderName + "_images"))
            
            _waitDummy = open(os.path.join(dirPathToSection, sectionFolderName + "_toc.tex"), "w").close()
            _waitDummy = open(os.path.join(dirPathToSection, sectionFolderName + "_con.tex"), "w").close()
        
        # create the json file file, _out folder, main.tex
        relSectionPath = ""
        sectionPathList = sectionPath.split(sectionPathSeparator)
        for i,p in enumerate(sectionPathList):
            relSectionPath += p if relSectionPath == "" else "." + p
            
            cls.sectionPathForTemplate = cls.getSectionJSONKeyPrefixFormPath(relSectionPath)
            
            pathToTopSection = cls._getSectionFilepath(relSectionPath)
            sectionFilepath = os.path.join(pathToTopSection, BookInfoStructure.sectionsInfoFilename)
            
            with open(sectionFilepath, "w+") as f:
                jsonObj = json.dumps(cls._getTemplate(numLevels, i + 1), indent = 4)
                f.write(jsonObj)
            
            
            sectionFolderName = pathToTopSection.split("/")[-1]
            mainTemplateFile = os.path.join(os.getenv("BOOKS_TEMPLATES_PATH"),"main_template.tex")
            if not os.path.exists(os.path.join(pathToTopSection,"_out")):
                _waitDummy = os.makedirs(os.path.join(pathToTopSection,"_out"))
                _waitDummy = shutil.copy(mainTemplateFile, os.path.join(pathToTopSection, sectionFolderName + "_main.tex"))

    def _getPathToSectionsFolder():
        pathToSectionFolder = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
        pathToSectionFolder = os.path.join(pathToSectionFolder, BookInfoStructure.sectionsInfoBaseRelPath)
        return pathToSectionFolder

    @classmethod
    def _getSectionFilepath(cls, sectionPath):
        sectionPrefix = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_prefix_ID)
        sectionsPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_path_separator_ID)

        pathList = sectionPath.split(sectionsPathSeparator)
        pathList[0] = sectionPrefix + "_" + pathList[0]
        
        for i in range(len(pathList) - 1, 0, -1):
            pathList[i] = ".".join(pathList[:i + 1])
        sectionFullPath = pathList
        sectionFullPath = os.path.join(*sectionFullPath)
        pathToSection = cls._getPathToSectionsFolder()
        pathToSection = os.path.join(pathToSection, sectionFullPath)

        return pathToSection
    
    @classmethod
    def readProperty(cls, sectionPath, propertyName):
        fullPathToSection = cls._getSectionFilepath(sectionPath)
        fullPathToSection = os.path.join(fullPathToSection, BookInfoStructure.sectionsInfoFilename)

        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_path_separator_ID)
        
        sectionPrefixForTemplate = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_prefix_ID)
        sectionPathForTemplate = sectionPath.replace(sectionPathSeparator, "_")
        if sectionPathForTemplate == _u.notDefinedToken:
            return ""
        else:
            return _u.JSON.readProperty(fullPathToSection, sectionPrefixForTemplate + "_" + sectionPathForTemplate + propertyName)

    @classmethod
    def updateProperty(cls, sectionPath, propertyName, newValue):        
        fullPathToSection = cls._getSectionFilepath(sectionPath)
        fullPathToSection = os.path.join(fullPathToSection, BookInfoStructure.sectionsInfoFilename)

        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_path_separator_ID)
        sectionPrefixForTemplate = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_prefix_ID)
        sectionPathForTemplate = sectionPath.replace(sectionPathSeparator, "_")
        _u.JSON.updateProperty(fullPathToSection, sectionPrefixForTemplate + "_" + sectionPathForTemplate + propertyName, newValue)


class OriginalMaterialStructure:
    '''
    Structure to store the original pdf and other required material.
    '''

    originalMaterialBaseRelPath = "originalMaterial/"
    
    @classmethod
    def createStructure(cls):
        getAbsPath = cls._getBaseAbsPath()
        if not os.path.exists(getAbsPath):   
            log.autolog("The structure was not present. Will create it.")
            log.autolog("Creating path: " + getAbsPath)
            _waitDummy = os.makedirs(getAbsPath)
    
    @classmethod
    def addOriginalMaterial(cls, name, filePath, structureRelPath):
        log.autolog("Adding material: '" + name + "' to rel path: " + structureRelPath)
        basePath = cls._getBaseAbsPath()
        originnalMaterialDestinationPath = os.path.join(basePath, structureRelPath)
        log.autolog(originnalMaterialDestinationPath)
        if not os.path.exists(originnalMaterialDestinationPath):   
            log.autolog("Path '" + originnalMaterialDestinationPath + "'does not exist will create it")
            _waitDummy = os.makedirs(originnalMaterialDestinationPath)
        cmd = "cp " + filePath + " " + os.path.join(originnalMaterialDestinationPath) 
        log.autolog("Exacuting command: '" + cmd + "'")
        os.system(cmd)

    @classmethod
    def _getBaseAbsPath(cls):
        bookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
        return os.path.join(bookPath, cls.originalMaterialBaseRelPath)