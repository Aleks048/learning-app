import os
import sys
import json

sys.path.insert(1, os.getenv("BOOKS_TEMPLATES_PATH"))
import bookInfo_template as bi_t

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

    bookInfoFoldefRelPath = "/bookInfo/"
    bookInfoFilename = "bookInfo.json"

    currSectionFull_ID= "currChapterFull"# need to be removed
    currSection_ID = "currChapter"
    
    version_ID = "version"
    sections_prefix_ID = "sections_prefix"
    sections_ID = "sections"
    
    #currState
    currentState_ID = "currentState"
    currentPage_ID = "currentPage"
    currSection_ID = "currSection"
    currSubsectionsPath_ID = "currSubsectionsPath"

    bookInfoTemplate = {
        version_ID: "0.1",
        sections_prefix_ID: "",
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
            _waitDummy = os.system("touch " + bookInfoFilepath)
        elif os.path.isfile(bookInfoFilepath):
            print("BookInfoStructure.createBookInfoStrunture - the bookInfo file was not present will create it.")
            _waitDummy = os.system("touch " + bookInfoFilepath)
        
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
        print("updateBookInfoStructureProperty - updating property: '" + propertyName +"' with value :'" + newValue + "'.")
        _u.updateJSONProperty(cls._getAsbFilepath(), property, newValue)



class SectionInfoStructure:
    currStucturePath = ""

    # for later: add if the section should generate the pdf.
    currPage_ID = "currentPage"
    currImageID_ID = "currImageID"
    currImageName_ID = "currImageName"
    currLinkName_ID = "currLinkName"

    def createStructure(structuresPath):
        pass

    def readProperty():
        pass

    def updateProperty():
        pass


class WholeBookStructure:
    pass