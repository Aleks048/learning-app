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

    class TOC_SECTION_PROPERTIES:
        TEXT_MARKER = "[SECTION_TEXT]"
        START_MARKER = "[SECTION_START]" 
        FINISH_MARKER = "[SECTION_FINISH]"
        NAME_MARKER = "[SECTION_NAME]"
        CONTENT_MARKER = "[CONTENT_MARKER]"
        
        text_ID = "TOC_text"
        sectionStart_ID = "TOC_sectionStart"
        sectionFinish_ID = "TOC_sectionFinish"
        
        proipertyToMarker = {
            text_ID: TEXT_MARKER,
            sectionStart_ID: START_MARKER,
            sectionFinish_ID: FINISH_MARKER
        }
 
        def getPropertyFormPath(path, propertyName):
            separator = BookInfoStructure.readProperty(BookInfoStructure.sections_path_separator_ID)
            sectionPrefix = BookInfoStructure.readProperty(BookInfoStructure.sections_prefix_ID)
            return sectionPrefix + "_" + path.replace(separator, "_") + propertyName

    @classmethod
    def createStructure(cls):
        pathToTemplates = os.getenv("BOOKS_TEMPLATES_PATH")

        sectionsList = BookInfoStructure.readProperty(BookInfoStructure.sections_ID)

        for sectionName, sectionData in sectionsList.items():
            sectionsTOCLines = [""]
            cls._getTOCLines(sectionData, sectionsTOCLines, 0)
            _waitDummy = os.system("cp " + pathToTemplates + "/TOC_template.tex " + cls._getTOCFilePath(sectionName))
            _u.replaceMarkerInFile(cls._getTOCFilePath(sectionName), cls.TOC_SECTION_PROPERTIES.NAME_MARKER, sectionName)
            _u.replaceMarkerInFile(cls._getTOCFilePath(sectionName), cls.TOC_SECTION_PROPERTIES.CONTENT_MARKER, sectionsTOCLines[0])

    def _getTOCSectionNameFromSectionPath(sectionPath):
        separator = BookInfoStructure.readProperty(BookInfoStructure.sections_path_separator_ID)
        return sectionPath.split(separator)[0]

    @classmethod
    def updateProperty(cls, sectionPath, propertyName, newValue):
        oldPropertyValue = cls.readProperty(sectionPath, propertyName)

        sectionJSONPath = BookInfoStructure.readProperty(sectionPath)["path"]
        fullPropertyName = cls.TOC_SECTION_PROPERTIES.getPropertyFormPath(sectionPath, propertyName)
        _u.updateJSONProperty(sectionJSONPath, fullPropertyName, newValue)

        # update the TOC files
        sectionName = cls._getTOCSectionNameFromSectionPath(sectionPath)
        if oldPropertyValue != "":
            _u.replaceMarkerInFile(cls._getTOCFilePath(sectionName), "[" + oldPropertyValue + "]", "[" + newValue + "]", "[" + sectionPath + "]")
        else:
            marker = cls.TOC_SECTION_PROPERTIES.proipertyToMarker[propertyName]
            _u.replaceMarkerInFile(cls._getTOCFilePath(sectionName), "[" + marker  + "]","[" + newValue + "]",  "[" + sectionPath + "]")
        
    
    @classmethod
    def readProperty(cls, sectionPath, propertyName):
        sectionJSONPath = BookInfoStructure.readProperty(sectionPath)["path"]
        fullPropertyName = cls.TOC_SECTION_PROPERTIES.getPropertyFormPath(sectionPath, propertyName)
        return _u.readJSONProperty(sectionJSONPath, fullPropertyName)

    @classmethod
    def _getTOCLines(cls, sectionsData, outLines, level):
        INTEMEDIATE_LINE = cls.TOC_SECTION_PROPERTIES.NAME_MARKER + ":\\\\\n"
        BOTTOM_LINE = "\TOCline{" + cls.TOC_SECTION_PROPERTIES.TEXT_MARKER + \
            " [" + cls.TOC_SECTION_PROPERTIES.NAME_MARKER + "]// [" + \
            cls.TOC_SECTION_PROPERTIES.START_MARKER + \
            "] - [" + cls.TOC_SECTION_PROPERTIES.FINISH_MARKER + "]}{[" + \
            cls.TOC_SECTION_PROPERTIES.START_MARKER + "]}" + \
            "\\\\\n"

        DEFAULT_PREFIX_SPACES = " " * 4 + level * " " * 4
    
        for name, section in sectionsData["sections"].items():
            if type(section) == dict:
                if section["sections"] == {}:
                    # add line
                    lineToAdd = DEFAULT_PREFIX_SPACES + BOTTOM_LINE.replace(cls.TOC_SECTION_PROPERTIES.NAME_MARKER, name)
                    outLines[0] = outLines[0] + lineToAdd
                else:
                    lineToAdd = DEFAULT_PREFIX_SPACES + INTEMEDIATE_LINE.replace(cls.TOC_SECTION_PROPERTIES.NAME_MARKER, name)
                    outLines[0] = outLines[0] + lineToAdd
                    cls._getTOCLines(section, outLines, level +1)
    
    def _getTOCDirPath():
        bookPath = _u.Settings.readProperty(_u.Settings.currBookPath_ID)
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
        version_ID: "0.1",
        sections_prefix_ID: "",
        sections_path_separator_ID: ".",
        sections_ID: {
        },
        currentState_ID: {
            currentPage_ID: "",
            currSection_ID: "",
            currSubsectionsPath_ID: ""
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
    currPage_ID = "currentPage"
    currImageID_ID = "currImageID"
    currImageName_ID = "currImageName"
    currLinkName_ID = "currLinkName"


    sectionPrefixForTemplate = ""
    sectionPathForTemplate = ""

    @classmethod
    def _getTemplate(cls, depth, level):
        sectionInfoEntryPrefix = cls.sectionPathForTemplate
        sectionInfo_template = {
                sectionInfoEntryPrefix + "_level":{
                    sectionInfoEntryPrefix + "_depth": str(depth),
                    sectionInfoEntryPrefix + "_level": str(level),
                },
                sectionInfoEntryPrefix + "_name": "",
                sectionInfoEntryPrefix + "_startPage": "",
                sectionInfoEntryPrefix + "_latestSubchapter": "",
                sectionInfoEntryPrefix + "_imIndex": "",
                sectionInfoEntryPrefix + "_subSections": [],
                sectionInfoEntryPrefix + "_tocInfo":{
                    sectionInfoEntryPrefix + "TOC_text":"",
                    sectionInfoEntryPrefix + "TOC_sectionStart":"",
                    sectionInfoEntryPrefix + "TOC_sectionFinish":""
                }
        }
        return sectionInfo_template

    def getSectionJSONKeyPrefixFormPath(path):
        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.sections_path_separator_ID) 
        secPrefix = BookInfoStructure.readProperty(BookInfoStructure.sections_prefix_ID)
        return secPrefix + "_" + path.replace(sectionPathSeparator, "_")
        

    @classmethod
    def createStructure(cls, sectionPath):
        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.sections_path_separator_ID) 

        numLevels = len(sectionPath.split(sectionPathSeparator))

        dirPathToSection = cls._getSectionFilepath(sectionPath)

        if not os.path.exists(dirPathToSection):

            print("SectionInfoStructure.createStructure - the sections structure was not present will create it.")
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
            prevRelSectionPath = relSectionPath
            relSectionPath += p if relSectionPath == "" else "." + p
            
            cls.sectionPathForTemplate = cls.getSectionJSONKeyPrefixFormPath(relSectionPath)
            sectionPrefixForTemplate = BookInfoStructure.readProperty(BookInfoStructure.sections_prefix_ID)
            
            pathToTopSection = cls._getSectionFilepath(relSectionPath)
            sectionFilepath = pathToTopSection + "/" + BookInfoStructure.sectionsInfoFilename
            
            with open(sectionFilepath, "w+") as f:
                jsonObj = json.dumps(cls._getTemplate(numLevels, i + 1), indent = 4)
                f.write(jsonObj)
            
            
            sectionFolderName = pathToTopSection.split("/")[-1]
            mainTemplateFile = os.getenv("BOOKS_TEMPLATES_PATH") + "/" + "main_template.tex"
            _waitDummy = os.system("mkdir " + pathToTopSection + "/_out")
            _waitDummy = os.system("cp "+ mainTemplateFile + " " + pathToTopSection + "/" + sectionFolderName + "_main.tex")

            # update the book info
            bookInfoSections = BookInfoStructure.readProperty(BookInfoStructure.sections_ID)
            
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
            
            BookInfoStructure.updateProperty(BookInfoStructure.sections_ID, bookInfoSections)
        


    @classmethod
    def _getSectionFilepath(cls, sectionPath):
        sectionPrefix = BookInfoStructure.readProperty(BookInfoStructure.sections_prefix_ID)
        sectionsPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.sections_path_separator_ID)

        pathList = sectionPath.split(sectionsPathSeparator)
        pathList[0] = sectionPrefix + "_" + pathList[0]
        
        for i in range(len(pathList) - 1, 0, -1):
            pathList[i] = ".".join(pathList[:i + 1])
        sectionFullPath = pathList
        sectionFullPath = "/".join(sectionFullPath)
        pathToSection = _u.Settings.readProperty(_u.Settings.currBookPath_ID)
        pathToSection += "/" + BookInfoStructure.sectionsInfoBaseRelPath
        pathToSection += "/" + sectionFullPath

        return pathToSection
    
    @classmethod
    def readProperty(cls, sectionPath, propertyName):
        fullPathToSection = cls._getSectionFilepath(sectionPath)
        fullPathToSection += "/" + BookInfoStructure.sectionsInfoFilename

        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.sections_path_separator_ID)
        
        sectionPrefixForTemplate = BookInfoStructure.readProperty(BookInfoStructure.sections_prefix_ID)
        sectionPathForTemplate = sectionPath.replace(sectionPathSeparator, "_")
        return _u.readJSONProperty(fullPathToSection, sectionPrefixForTemplate + "_" + sectionPathForTemplate + propertyName)

    @classmethod
    def updateProperty(cls, sectionPath, propertyName, newValue):        
        fullPathToSection = cls._getSectionFilepath(sectionPath)
        fullPathToSection += "/" + BookInfoStructure.sectionsInfoFilename

        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.sections_path_separator_ID)
        sectionPrefixForTemplate = BookInfoStructure.readProperty(BookInfoStructure.sections_prefix_ID)
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
            print("OriginalMaterialStructure.createOriginalMaterialStructure - the structure was not present. Will create it.")
            print("Creating path: " + getAbsPath)
            _waitDummy = os.system("mkdir -p " + getAbsPath)

    def _getBaseAbsPath():
        bookPath = _u.Settings.readProperty(_u.Settings.currBookPath_ID)
        return bookPath + "/" + BookInfoStructure.originalMaterialBaseRelPath