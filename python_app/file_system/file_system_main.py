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
    
    def updateTOCfile():
        pass

    def _getTOCFilePath(bookPath, sectionName):
        tocFolderPath = bookPath + "/" + "TOC"
        if (os.path.isdir(tocFolderPath)):
            return tocFolderPath + "/TOC_sec" + sectionName + ".tex"
        else:
            print("_getTOCFilePath - " + "the TOC filepath is not present. Will create: " + tocFolderPath)
            _waitDummy = os.system("mkdir " + tocFolderPath)
            return tocFolderPath + "/TOC_sec" + sectionName + ".tex"

class BookInfoStructure:
    bookInfoFoldefRelPath = "/bookInfo/"
    bookInfoFilename = "bookInfo.json"

    @classmethod
    def createBookInfoStrunture(cls, bookPath):
        expectedFileDir = "/".join((bookPath + cls._getBookInfoRelFilepath()).split("/")[:-1])
        if not os.path.exists(expectedFileDir):
            print("BookInfoStructure.createBookInfoStrunture - the bookInfo structure was not present will create it.")
            _waitDummy = os.system("mkdir -p " + expectedFileDir)
            _waitDummy = os.system("touch " + bookPath + cls._getBookInfoRelFilepath())
        elif os.path.isfile(bookPath + cls._getBookInfoRelFilepath()):
            print("BookInfoStructure.createBookInfoStrunture - the bookInfo file was not present will create it.")
            _waitDummy = os.system("touch " + bookPath + cls._getBookInfoRelFilepath())

        
        with open(bookPath + cls._getBookInfoRelFilepath(), "w+") as f:
            jsonObj = json.dumps(bi_t.bookInfo_template, indent = 4)
            f.write(jsonObj)

    @classmethod
    def _getBookInfoRelFilepath(cls):
        return cls.bookInfoFoldefRelPath + cls.bookInfoFilename

    @classmethod
    def updateBookInfoStructureProperty(bookPath, propertyName, newValue):
        _u.updateJSONProperty(bookPath, propertyName, newValue)


class WholeBookStructure:
    pass

class SubsectionsStructure:
    pass