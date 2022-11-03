import os
from unicodedata import name

import _utils._utils_main as _u
import file_system.file_system_main as fs

'''
Facade for Filesystem
'''

class Data:
    pass

class Wrappers:
    class BookInfoStructure(fs.BookInfoStructure):
        pass

    class SectionInfoStructure(fs.SectionInfoStructure):
        pass

    class TOCStructure(fs.TOCStructure):
        pass

    class OriginalMaterialStructure(fs.OriginalMaterialStructure):
        pass


class PropIDs:
    class SectionProperties_IDs(fs.SectionInfoStructure.PubProp):
        pass

    class BookProperties_IDs(fs.BookInfoStructure.PubProp):
        pass

    class TOCProperties_IDs(fs.TOCStructure.PubPro):
        pass



def createNewBook(bookName):
    # check if a book with name exists and ask
    # if we want to delete and proceed
    booksPath = _u.getPathToBooks()
    bookPath = booksPath + "/" + bookName

    if os.path.exists(bookPath):
        print("createNewBook - the book path exists")
        print("bookPath:" + bookPath)
        # TODO: ask the user we we should proceed.
        raise

    os.system("mkdir -p " + bookPath)

    #set the current book in Settings
    _u.Settings.Book.addNewBook(bookName, bookPath)

    #
    #create bookInfo structure
    #
    fs.BookInfoStructure.createStructure()

    #create sections structure
    fs.SectionInfoStructure.createStructure()

    #create TOCstructure
    fs.TOCStructure.createStructure()

    # create originalMaterialStructure
    fs.OriginalMaterialStructure.createStructure()

def addSectionForCurrBook(sectionPath):
    # add to Sections structure
    fs.SectionInfoStructure.addSection(sectionPath)
    
    # add to BookInfo structure
    fs.BookInfoStructure.addSection(sectionPath)

    # add to TOC structure
    fs.TOCStructure.addSection(sectionPath)

def _updateSectionProperty(sectionPath, propertyName, newValue):
    # thange the TOC
    fs.TOCStructure.updateTOCfiles(sectionPath, propertyName, newValue)
    
    # change the section.json
    sectionJSONPath = fs.BookInfoStructure.readProperty(sectionPath)["path"]
    fullPropertyName =fs.TOCStructure.PubPro.getPropertyFormPath(sectionPath, propertyName)
    _u.updateJSONProperty(sectionJSONPath, fullPropertyName, newValue)

def updateSectionStartPage(sectionPath, newValue):
    _updateSectionProperty(sectionPath, fs.TOCStructure.PubPro.start_ID, newValue)

def updateSectionFinishPage(sectionPath, newValue):
    _updateSectionProperty(sectionPath, fs.TOCStructure.PubPro.finish_ID, newValue)

def updateSectionTOCText(sectionPath, newValue):
    _updateSectionProperty(sectionPath, fs.TOCStructure.PubPro.text_ID, newValue)

def updateSectionProperty(sectionPath, propertyName, newValue):
    print("propertyName")
    print(propertyName)
    fs.SectionInfoStructure.updateProperty(sectionPath, propertyName, newValue)

def getSubsectionsList(sectionPath = ""):
    sections_ID = fs.BookInfoStructure.PubProp.sections_ID
    outSubsectionsList = []

    if sectionPath == "":
        subsections = fs.BookInfoStructure.readProperty(sections_ID)
    else:
        subsections = fs.BookInfoStructure.readProperty(sectionPath)[sections_ID]
    

    subsectionsNamesList = list(subsections.keys())
    subsectionsList = list(subsections.values())
    while subsectionsList != []:
        section = subsectionsList[0]
        sectionName = subsectionsNamesList[0]

        bottomSubsection = True
        for subSecName, subSec in section[sections_ID].items():
            bottomSubsection = False
            subsectionsList.append(subSec)
            subsectionsNamesList.append(subSecName)
        
        if bottomSubsection:
            outSubsectionsList.append(sectionName)
        
        subsectionsList.pop(0)
        subsectionsNamesList.pop(0)
    
    return outSubsectionsList
    
def getTopSectionsList():
    sections = fs.BookInfoStructure.readProperty(fs.BookInfoStructure.PubProp.sections_ID)

    return list(sections.keys())

def removeSection():
    # # remove to Sections structure
    # fs.SectionInfoStructure.removeSection(sectionPath)
    
    # # remove BookInfo structure
    # fs.BookInfoStructure.removeSection(sectionPath)

    # # remove TOC structure
    # fs.SectionInfoStructure.removeSection(sectionPath)
    pass

def moveSection():
    pass

def passMarerialToBook():
    # original structure add material

    # add to original material list
    pass

def backupBookToDB():
    pass

def loadBookFromDB():
    pass