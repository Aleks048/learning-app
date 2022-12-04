import os
import json

import _utils.logging as log
import _utils._utils_main as _u

import file_system._utils as _ufs

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
        sectionPathSeparator = \
            BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_path_separator_ID)

        sectionPathList = sectionPath.split(sectionPathSeparator)
        relSectionPath = ""
        for i,p in enumerate(sectionPathList):
            prevRelSectionPath = relSectionPath
            relSectionPath += p if relSectionPath == "" else "." + p

            pathToTopSection = _ufs._getSectionFilepath(relSectionPath)
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

