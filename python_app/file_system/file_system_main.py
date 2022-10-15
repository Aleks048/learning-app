import csv
import os
import sys
import json

sys.path.insert(1, os.getenv("BOOKS_TEMPLATES_PATH"))

import _utils._utils_main as _u

# class File:
#     def __init__(self, name, path, content = "") -> None:
#         self.name = name
#         self.path = path
#         self.content = content

# class Folder:
#     def __init__(self, name, path, files = []) -> None:
#         self.name = name
#         self.path = path
#         self.files = files


# chapterInfoJSON = File("sectionsInfo.json")
# bookInfo = Folder("bookInfo", [chapterInfoJSON])

class TOCStructure:
    TOC_MARKERS = ["[ENTRY_START]", "[ENTRY_FINISH]", "[SECTION_NAME]"]
    
    @classmethod
    def createTOCStructure(cls, section, bookPath):
        pathToTemplates = os.getenv("BOOKS_TEMPLATES_PATH")


        _waitDummy = os.system("cp " + pathToTemplates + "/TOC_template.tex " + cls._getTOCFilePath(bookPath, section))

        _u.replaceMarkerInFile(cls._getTOCFilePath(bookPath, section), cls.TOC_MARKERS[2], section)
        
        # with open(pathToTemplates + "TOC_template.tex", "r") as f:
        #     TOCTemplateLines = f.readlines()
        
        # for i in range(len(TOCTemplateLines)):
        #     if  cls.TOC_MARKERS[2] in TOCTemplateLines[i]:
        #         TOCTemplateLines[i] = TOCTemplateLines[i].replace(cls.TOC_MARKERS[2], section)
        
        # with open(cls._getTOCFilePath(bookPath, section), "w") as f:
        #     f.writelines(TOCTemplateLines)
    
    

    def _getTOCFilePath(bookPath, sectionName):
        tocFolderPath = bookPath + "/" + "TOC"
        if (os.path.isdir(tocFolderPath)):
            return tocFolderPath + "/TOC_sec" + sectionName + ".tex"
        else:
            print("_getTOCFilePath - " + "the TOC filepath is not present. Will create: " + tocFolderPath)
            _waitDummy = os.system("mkdir " + tocFolderPath)
            return tocFolderPath + "/TOC_sec" + sectionName + ".tex"

class BookInfoStructure:
    '''
    The stucture keeps the info about the book
    '''

    bookInfoFoldefRelPath= "/bookInfo/"
    bookInfoFilename = "bookInfo.json"
    sectionsInfoBaseRelPath = "/subsections/"
    sectionsInfoFilename = "sectionInfo.json"

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
        print("BookInfoStructure.updatingProperty - '" + propertyName +"' with value :'" + newValue + "'.")
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
    def _getTemplate(cls):
        sectionInfoEntryPrefix = cls.sectionPrefixForTemplate + "_" + cls.sectionPathForTemplate
        sectionInfo_template = {
                sectionInfoEntryPrefix + "_level":{
                    sectionInfoEntryPrefix + "_depth": "",
                    sectionInfoEntryPrefix + "_level": "",
                },
                sectionInfoEntryPrefix + "_name": "",
                sectionInfoEntryPrefix + "_startPage": "",
                sectionInfoEntryPrefix + "_latestSubchapter": "",
                sectionInfoEntryPrefix + "_imIndex": "",
                sectionInfoEntryPrefix + "_subSections": {}
        }
        return sectionInfo_template

    @classmethod
    def createStructure(cls, sectionPath):
        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.sections_path_separator_ID) 

        dirPathToSection = cls._getSectionFilepath(sectionPath)

        if not os.path.exists(dirPathToSection):

            print("SectionInfoStructure.createStructure - the sections structure was not present will create it.")
            print("Creating path: " + dirPathToSection)
            
            # create files and folders
            _waitDummy = os.system("mkdir -p " + dirPathToSection)
            _waitDummy = os.system("mkdir " + dirPathToSection + "/images")
            _waitDummy = os.system("mkdir " + dirPathToSection + "/pdf")
            
            sectionFolderName = dirPathToSection.split("/")[-1]
            print(dirPathToSection)
            _waitDummy = os.system("touch " + dirPathToSection + "/" + sectionFolderName + "_toc.tex")
            _waitDummy = os.system("touch " + dirPathToSection + "/" + sectionFolderName + "_pic.tex")
        
        # create the json file file 
        relSectionPath = ""
        for p in sectionPath.split(sectionPathSeparator):
            
            relSectionPath += p if relSectionPath == "" else "." + p
            
            cls.sectionPathForTemplate = relSectionPath.replace(sectionPathSeparator, "_")
            cls.sectionPrefixForTemplate = BookInfoStructure.readProperty(BookInfoStructure.sections_prefix_ID)
            
            pathToTopSection = cls._getSectionFilepath(relSectionPath)
            sectionFilepath = pathToTopSection + "/" + BookInfoStructure.sectionsInfoFilename
            with open(sectionFilepath, "w+") as f:
                jsonObj = json.dumps(cls._getTemplate(), indent = 4)
                f.write(jsonObj)
            
            sectionFolderName = pathToTopSection.split("/")[-1]
            mainTemplateFile = os.getenv("BOOKS_TEMPLATES_PATH") + "/" + "main_template.tex"
            _waitDummy = os.system("cp "+ mainTemplateFile + " " + pathToTopSection + "/" + sectionFolderName + "_main.tex")

        # create tex files

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
        print("SectionInfoStructure.readProperty - '" + propertyName)
        fullPathToSection = cls._getSectionFilepath(sectionPath)
        fullPathToSection += "/" + BookInfoStructure.sectionsInfoFilename

        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.sections_path_separator_ID)
        
        sectionPrefixForTemplate = BookInfoStructure.readProperty(BookInfoStructure.sections_prefix_ID)
        sectionPathForTemplate = sectionPath.replace(sectionPathSeparator, "_")
        return _u.readJSONProperty(fullPathToSection, sectionPrefixForTemplate + "_" + sectionPathForTemplate + propertyName)

    @classmethod
    def updateProperty(cls, sectionPath, propertyName, newValue):
        print("SectionInfoStructure.updateProperty - '" + propertyName +"' with value :'" + newValue + "'.")
        
        fullPathToSection = cls._getSectionFilepath(sectionPath)
        fullPathToSection += "/" + BookInfoStructure.sectionsInfoFilename

        sectionPathSeparator = BookInfoStructure.readProperty(BookInfoStructure.sections_path_separator_ID)
        sectionPrefixForTemplate = BookInfoStructure.readProperty(BookInfoStructure.sections_prefix_ID)
        sectionPathForTemplate = sectionPath.replace(sectionPathSeparator, "_")
        _u.updateJSONProperty(fullPathToSection, sectionPrefixForTemplate + "_" + sectionPathForTemplate + propertyName, newValue)


class WholeBookStructure:
    pass