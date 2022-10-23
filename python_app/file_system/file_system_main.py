import csv
import os
from re import template
import sys
import json

sys.path.insert(1, os.getenv("BOOKS_TEMPLATES_PATH"))

import _utils._utils_main as _u

class TOCStructure:
    '''
    Keeps the toc for the sections and links to them.
    '''

    class TocPubPro:
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
            separator = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_path_separator_ID)
            sectionPrefix = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_prefix_ID)
            return sectionPrefix + "_" + path.replace(separator, "_") + propertyName

    @classmethod
    def createStructure(cls):
        os.system("mkdir -p " + cls._getTOCDirPath())
        
    @classmethod
    def addSection(cls, sectionPath):
        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_path_separator_ID)

        sectionPathList = sectionPath.split(sectionPathSeparator)
        
        for i,sectionName in enumerate(sectionPathList):
            sectionsList = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_ID)
            sectionData = BookInfoStructure.readProperty(sectionName)
            if sectionData == None:
                continue

            separator = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_path_separator_ID)
            sectionPrefix = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_prefix_ID)
            topSectionName = sectionPrefix + "_" + sectionName.split(separator)[0]
            
            sectionsTOCLines = [""]
            
            if i == 0:
                pathToTemplates = os.getenv("BOOKS_TEMPLATES_PATH")
                _waitDummy = os.system("cp " + pathToTemplates + "/TOC_template.tex " + cls._getTOCFilePath(topSectionName))
            
            cls._getTOCLines(sectionData, sectionsTOCLines, 0)

            
            _u.replaceMarkerInFile(cls._getTOCFilePath(topSectionName), cls.TocPubPro.NAME_MARKER, topSectionName)
            _u.replaceMarkerInFile(cls._getTOCFilePath(topSectionName), cls.TocPubPro.CONTENT_MARKER, sectionsTOCLines[0])

    
    def _getTOCSectionNameFromSectionPath(sectionPath):
        prefix = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_prefix_ID)
        separator = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_path_separator_ID)
        return prefix + "_" + sectionPath.split(separator)[0]

    @classmethod
    def updateTOCfiles(cls, sectionPath, propertyName, newValue):
        oldPropertyValue = SectionInfoStructure.readProperty(sectionPath, propertyName)

        # update the TOC files
        sectionName = cls._getTOCSectionNameFromSectionPath(sectionPath)
        if oldPropertyValue != "":
            _u.replaceMarkerInFile(cls._getTOCFilePath(sectionName), "[" + oldPropertyValue + "]", "[" + newValue + "]", "[" + sectionPath + "]")
        else:
            marker = cls.TocPubPro.propertyToMarker[propertyName]
            _u.replaceMarkerInFile(cls._getTOCFilePath(sectionName), "[" + marker  + "]","[" + newValue + "]",  "[" + sectionPath + "]")

    @classmethod
    def _getTOCLines(cls, sectionsData, outLines, level):
        INTEMEDIATE_LINE = cls.TocPubPro.NAME_MARKER + ":\\\\\n"
        BOTTOM_LINE = "\TOCline{[" + cls.TocPubPro.TEXT_MARKER + \
            "] [" + cls.TocPubPro.NAME_MARKER + "]// [" + \
            cls.TocPubPro.START_MARKER + \
            "] - [" + cls.TocPubPro.FINISH_MARKER + "]}{[" + \
            cls.TocPubPro.START_MARKER + "]}" + \
            "\\\\\n"

        DEFAULT_PREFIX_SPACES = " " * 4 + level * " " * 4
    
        for name, section in sectionsData["sections"].items():
            if type(section) == dict:
                if section["sections"] == {}:
                    # add line
                    lineToAdd = DEFAULT_PREFIX_SPACES + BOTTOM_LINE.replace(cls.TocPubPro.NAME_MARKER, name)
                    outLines[0] = outLines[0] + lineToAdd
                else:
                    lineToAdd = DEFAULT_PREFIX_SPACES + INTEMEDIATE_LINE.replace(cls.TocPubPro.NAME_MARKER, name)
                    outLines[0] = outLines[0] + lineToAdd
                    cls._getTOCLines(section, outLines, level +1)
    
    def _getTOCDirPath():
        bookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
        return bookPath + BookInfoStructure.TOCbaseRelPath

    @classmethod
    def _getTOCFilePath(cls, sectionName):
        tocFolderPath = cls._getTOCDirPath()
        if (os.path.isdir(tocFolderPath)):
            return tocFolderPath + "/TOC_" + sectionName + ".tex"
        else:
            print("_getTOCFilePath - " + "the TOC filepath is not present.")
            print("Will create: " + tocFolderPath)
            _waitDummy = os.system("mkdir " + tocFolderPath)
            return tocFolderPath + "/TOC_" + sectionName + ".tex"


class BookInfoStructure:
    '''
    The stucture keeps the info about the book
    '''

    bookInfoFoldefRelPath= "/bookInfo/"
    bookInfoFilename = "bookInfo.json"
    sectionsInfoBaseRelPath = "/subsections/"
    sectionsInfoFilename = "sectionInfo.json"
    
    originalMaterialBaseRelPath = "/originalMaterial/"

    TOCbaseRelPath = "/TOC/"
    TOCFilename = "TOCinfo.json"

    currSectionFull_ID= "currChapterFull"# need to be removed
    currSection_ID = "currChapter"
    
    class BookInfoPubProp:
        version_ID = "version"
        sections_prefix_ID = "sections_prefix"
        sections_path_separator_ID = "sections_path_separator"
        sections_ID = "sections"
        
        #currState
        currentState_ID = "currentState"
        currentPage_ID = "currentPage"
        currSection_ID = "currSection"
        currSubsectionsPath_ID = "currSubsectionsPath"

    bookInfoTemplate = {
        BookInfoPubProp.version_ID: "0.1",
        BookInfoPubProp.sections_prefix_ID: "sec",
        BookInfoPubProp.sections_path_separator_ID: ".",
        BookInfoPubProp.sections_ID: {
        },
        BookInfoPubProp.currentState_ID: {
            BookInfoPubProp.currentPage_ID: "",
            BookInfoPubProp.currSection_ID: "",
            BookInfoPubProp.currSubsectionsPath_ID: ""
        }
    }

    @classmethod
    def createStructure(cls, bookInfoFilepath = ""):
        if bookInfoFilepath == "":
            bookInfoFilepath = cls._getAsbFilepath()
        
        expectedFileDir = "/".join((bookInfoFilepath).split("/")[:-1])
        
        if not os.path.exists(expectedFileDir):
            print("BookInfoStructure.createBookInfoStrunture - the bookInfo structure was not present will create it.")
            _waitDummy = os.system("mkdir -p " + expectedFileDir)
        
        with open(bookInfoFilepath, "w+") as f:
            jsonObj = json.dumps(cls.bookInfoTemplate, indent = 4)
            f.write(jsonObj)

    @classmethod
    def addSection(cls, sectionPath):
        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_path_separator_ID)

        sectionPathList = sectionPath.split(sectionPathSeparator)
        relSectionPath = ""
        for i,p in enumerate(sectionPathList):
            prevRelSectionPath = relSectionPath
            relSectionPath += p if relSectionPath == "" else "." + p

            pathToTopSection = SectionInfoStructure._getSectionFilepath(relSectionPath)
            sectionFilepath = pathToTopSection + "/" + BookInfoStructure.sectionsInfoFilename

            # update the book info
            bookInfoSections = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_ID)
            
            def addBookInfoSection(parentProperty):
                parentProperty[relSectionPath] = {
                    "path": sectionFilepath,
                    "sections": {}
                }
            
            if i == 0:
                if relSectionPath not in bookInfoSections.keys():
                    parentProperty = bookInfoSections
                    addBookInfoSection(parentProperty)
            else:
                parentProperty = _u.readDictProperty(bookInfoSections, prevRelSectionPath)
                
                if (relSectionPath not in parentProperty["sections"].keys()) \
                    and (type(parentProperty) == dict \
                    and "sections" in parentProperty.keys()):
                    addBookInfoSection(parentProperty["sections"])
                
                _u.updateDictProperty(bookInfoSections, prevRelSectionPath, parentProperty)
            
            BookInfoStructure.updateProperty(BookInfoStructure.BookInfoPubProp.sections_ID, bookInfoSections)

    @classmethod
    def _getRelFilepath(cls):
        return cls.bookInfoFoldefRelPath + cls.bookInfoFilename
    
    @classmethod
    def _getAsbFilepath(cls):
        bookPath = _u.Settings.getCurrBookFolderPath()
        return bookPath + cls._getRelFilepath()

    @classmethod
    def readProperty(cls, property):
        return _u.readJSONProperty(cls._getAsbFilepath(), property)

    @classmethod
    def updateProperty(cls, propertyName, newValue):
        _u.updateJSONProperty(cls._getAsbFilepath(), propertyName, newValue)


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

    class SecPubProp:
        name_ID = "_name"
        startPage_ID = "_startPage"
        latestSubchapter_ID = "_latestSubchapter"
        imIndex_ID = "_imIndex"
        subSections_ID = "_subSections"

    class SecPrivateProp:
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
                sectionInfoEntryPrefix + cls.SecPubProp.name_ID: "",
                sectionInfoEntryPrefix + cls.SecPubProp.startPage_ID: "",
                sectionInfoEntryPrefix + cls.SecPubProp.latestSubchapter_ID: "",
                sectionInfoEntryPrefix + cls.SecPubProp.imIndex_ID: "",
                sectionInfoEntryPrefix + cls.SecPubProp.subSections_ID: [],
                sectionInfoEntryPrefix + cls.SecPrivateProp.levelData_ID:{
                    sectionInfoEntryPrefix + cls.SecPrivateProp.levelData_depth_ID: str(depth),
                    sectionInfoEntryPrefix + cls.SecPrivateProp.levelData_level_ID: str(level),
                },
                sectionInfoEntryPrefix + cls.SecPrivateProp.tocData_ID:{
                    sectionInfoEntryPrefix + TOCStructure.TocPubPro.text_ID: "",
                    sectionInfoEntryPrefix + TOCStructure.TocPubPro.start_ID: "",
                    sectionInfoEntryPrefix + TOCStructure.TocPubPro.finish_ID: ""
                }
        }
        return sectionInfo_template

    def getSectionJSONKeyPrefixFormPath(path):
        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_path_separator_ID) 
        secPrefix = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_prefix_ID)
        return secPrefix + "_" + path.replace(sectionPathSeparator, "_")   

    @classmethod
    def createStructure(cls):
        print("SectionInfoStructure.create structure - empty sectionPath given. Will only crerate the top folder.")
        os.system("mkdir -p " + cls._getPathToSectionsFolder())
        return

    @classmethod
    def addSection(cls, sectionPath):
        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_path_separator_ID) 

        numLevels = len(sectionPath.split(sectionPathSeparator))

        dirPathToSection = cls._getSectionFilepath(sectionPath)

        if not os.path.exists(dirPathToSection):

            print("SectionInfoStructure.addSection - the sections structure was not present will create it.")
            print("Creating path: " + dirPathToSection)
            
            # create files and folders
            _waitDummy = os.system("mkdir -p " + dirPathToSection)
            _waitDummy = os.system("mkdir " + dirPathToSection + "/images")
            
            sectionFolderName = dirPathToSection.split("/")[-1]
            _waitDummy = os.system("touch " + dirPathToSection + "/" + sectionFolderName + "_toc.tex")
            _waitDummy = os.system("touch " + dirPathToSection + "/" + sectionFolderName + "_pic.tex")
        
        # create the json file file, _out folder, main.tex
        relSectionPath = ""
        sectionPathList = sectionPath.split(sectionPathSeparator)
        for i,p in enumerate(sectionPathList):
            relSectionPath += p if relSectionPath == "" else "." + p
            
            cls.sectionPathForTemplate = cls.getSectionJSONKeyPrefixFormPath(relSectionPath)
            
            pathToTopSection = cls._getSectionFilepath(relSectionPath)
            sectionFilepath = pathToTopSection + "/" + BookInfoStructure.sectionsInfoFilename
            
            with open(sectionFilepath, "w+") as f:
                jsonObj = json.dumps(cls._getTemplate(numLevels, i + 1), indent = 4)
                f.write(jsonObj)
            
            
            sectionFolderName = pathToTopSection.split("/")[-1]
            mainTemplateFile = os.getenv("BOOKS_TEMPLATES_PATH") + "/" + "main_template.tex"
            _waitDummy = os.system("mkdir " + pathToTopSection + "/_out")
            _waitDummy = os.system("cp "+ mainTemplateFile + " " + pathToTopSection + "/" + sectionFolderName + "_main.tex")

    def _getPathToSectionsFolder():
        pathToSectionFolder = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
        pathToSectionFolder += "/" + BookInfoStructure.sectionsInfoBaseRelPath
        return pathToSectionFolder

    @classmethod
    def _getSectionFilepath(cls, sectionPath):
        sectionPrefix = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_prefix_ID)
        sectionsPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_path_separator_ID)

        pathList = sectionPath.split(sectionsPathSeparator)
        pathList[0] = sectionPrefix + "_" + pathList[0]
        
        for i in range(len(pathList) - 1, 0, -1):
            pathList[i] = ".".join(pathList[:i + 1])
        sectionFullPath = pathList
        sectionFullPath = "/".join(sectionFullPath)
        pathToSection = cls._getPathToSectionsFolder()
        pathToSection += "/" + sectionFullPath

        return pathToSection
    
    @classmethod
    def readProperty(cls, sectionPath, propertyName):
        fullPathToSection = cls._getSectionFilepath(sectionPath)
        fullPathToSection += "/" + BookInfoStructure.sectionsInfoFilename

        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_path_separator_ID)
        
        sectionPrefixForTemplate = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_prefix_ID)
        sectionPathForTemplate = sectionPath.replace(sectionPathSeparator, "_")
        return _u.readJSONProperty(fullPathToSection, sectionPrefixForTemplate + "_" + sectionPathForTemplate + propertyName)

    @classmethod
    def updateProperty(cls, sectionPath, propertyName, newValue):        
        fullPathToSection = cls._getSectionFilepath(sectionPath)
        fullPathToSection += "/" + BookInfoStructure.sectionsInfoFilename

        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_path_separator_ID)
        sectionPrefixForTemplate = BookInfoStructure.readProperty(BookInfoStructure.BookInfoPubProp.sections_prefix_ID)
        sectionPathForTemplate = sectionPath.replace(sectionPathSeparator, "_")
        _u.updateJSONProperty(fullPathToSection, sectionPrefixForTemplate + "_" + sectionPathForTemplate + propertyName, newValue)


class OriginalMaterialStructure:
    '''
    Structure to store the original pdf and other required material.
    '''
    
    @classmethod
    def createStructure(cls):
        getAbsPath = cls._getBaseAbsPath()
        if not os.path.exists(getAbsPath):
            print("OriginalMaterialStructure.createStructure - the structure was not present. Will create it.")
            print("Creating path: " + getAbsPath)
            _waitDummy = os.system("mkdir -p " + getAbsPath)

    def _getBaseAbsPath():
        bookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
        return bookPath + "/" + BookInfoStructure.originalMaterialBaseRelPath