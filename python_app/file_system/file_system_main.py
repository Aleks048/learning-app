import csv
import os
from re import template
import sys
import json

sys.path.insert(1, os.getenv("BOOKS_TEMPLATES_PATH"))

import _utils._utils_main as _u

class TOCStructure:
    TOC_MARKERS = ["[ENTRY_START]", "[ENTRY_FINISH]", "[SECTION_NAME]","[CONTENT_MARKER]"]

    text_ID = "text"

    TOCInfoTemplate = {

    }

    @classmethod
    def createTOCStructure(cls):
        pathToTemplates = os.getenv("BOOKS_TEMPLATES_PATH")

        sectionsList = BookInfoStructure.readProperty(BookInfoStructure.sections_ID)

        for sectionName, sectionData in sectionsList.items():
            sectionsTOCLines = [""]
            cls._getTOCLines(sectionData, sectionsTOCLines, 0)
            _waitDummy = os.system("cp " + pathToTemplates + "/TOC_template.tex " + cls._getTOCFilePath(sectionName))
            _u.replaceMarkerInFile(cls._getTOCFilePath(sectionName), cls.TOC_MARKERS[2], sectionName)      
            _u.replaceMarkerInFile(cls._getTOCFilePath(sectionName), cls.TOC_MARKERS[3], sectionsTOCLines[0])      
        
        # crate TOCinfo.json
        print(cls._getTOCDirPath() + BookInfoStructure.TOCFilename)

        with open(cls._getTOCinfoFilepath(), "w+") as f:
            jsonObj = json.dumps(sectionsList, indent = 4)
            f.write(jsonObj)

    @classmethod
    def updateProperty(cls, sectionPath, propertyName, newValue):
        sectionList = _u.readJSONProperty(cls._getTOCinfoFilepath(), sectionPath)
        sectionList[propertyName] = newValue
    
    @classmethod
    def readProperty(cls, sectionPath, propertyName):
        section = _u.readJSONProperty(cls._getTOCinfoFilepath(), sectionPath)
        if propertyName in section.keys():
            return section[propertyName]
        else: 
            return None

    @classmethod
    def _getTOCinfoFilepath(cls):
        return cls._getTOCDirPath() + BookInfoStructure.TOCFilename

    @classmethod
    def _getTOCLines(cls, sectionsList, outLines, level):
        INTEMEDIATE_LINE = "[SECTION_NAME]:\\\\\n"
        BOTTOM_LINE = "\TOCline{Text [SECTION_NAME]// [ENTRY_START] - [ENTRY_FINISH]}{[ENTRY_START]}\\\\\n"

        DEFAULT_PREFIX_SPACES = " " * 4
    
        for name, section in sectionsList.items():
            if type(section) == dict:
                if section["isBottom"] == True:
                    # add line
                    lineToAdd = DEFAULT_PREFIX_SPACES + level * " " * 4 + BOTTOM_LINE.replace(cls.TOC_MARKERS[2], name)
                    outLines[0] = outLines[0] + lineToAdd
                else:
                    lineToAdd = DEFAULT_PREFIX_SPACES + level * " " * 4 + INTEMEDIATE_LINE.replace(cls.TOC_MARKERS[2], name)
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
    
    originalMaterialBaseRelPath = "/original_material/"

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
        # if type(newValue) != dict and type(newValue) != list :
        #     print("BookInfoStructure.updateProperty - '" + propertyName + 
        #             "' with value :'" + newValue + "'.")
        # else:
        #     print("BookInfoStructure.updateProperty - '" + propertyName +"' with value :'")
        #     print(newValue)
        #     print("'.")
        _u.updateJSONProperty(cls._getAsbFilepath(), propertyName, newValue)


class SectionInfoStructure:
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
                    "TOC_text":"",
                    "TOC_sectionStart":""
                    "TOC_sectionEnd"
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
            print(dirPathToSection)
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
                if i != len(sectionPathList) - 1:
                    parentProperty[relSectionPath] = {
                        "path": sectionFilepath,
                        "isBottom": False,
                        "sections": {}
                    }
                else:
                    parentProperty[relSectionPath] = {
                        "path": sectionFilepath,
                        "isBottom": True,
                        "sections": {}
                    }
            
            if i == 0:
                if relSectionPath not in bookInfoSections.keys():
                    parentProperty = bookInfoSections
                    addBookInfoSection(parentProperty)
            else:
                parentProperty = _u.readDictProperty(bookInfoSections, prevRelSectionPath)
                
                if (relSectionPath not in parentProperty.keys()) \
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
        # print("SectionInfoStructure.readProperty - '" + propertyName + "'")
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
    
    @classmethod
    def createOriginalMaterialStructure(cls):
        getAbsPath = cls._getBaseAbsPath()
        if not os.path.exists(getAbsPath):
            print("OriginalMaterialStructure.createOriginalMaterialStructure - the structure was not present. Will create it.")
            print("Creating path: " + getAbsPath)
            _waitDummy = os.system("mkdir -p " + getAbsPath)

    def _getBaseAbsPath():
        bookPath = _u.Settings.readProperty(_u.Settings.currBookPath_ID)
        return bookPath + "/" + BookInfoStructure.originalMaterialBaseRelPath

    def addOriginalMaterialFolder(relPath):
        pass

    def addOriginalMaterialMainPDF():
        pass