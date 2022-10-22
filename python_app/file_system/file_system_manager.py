import os
from unicodedata import name

import _utils._utils_main as _u
import file_system.file_system_main as fs


def createNewBook(bookName):
    # check if a book with name exists and ask
    # if we want to delete and proceed
    booksPath = _u.getPathToBooks()
    bookPath = booksPath + "/" + bookName

    if os.path.exists(bookPath):
        print("createNewBook - the book path exists")
        # TODO: ask the user we we should proceed.
        raise

    os.system("mkdir -p " + bookPath)

    #set the current book in Settings
    _u.Settings.setCurrentBook(bookName, bookPath)

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

def _changeSectionProperty(sectionPath, propertyName, newValue):
    # thange the TOC
    fs.TOCStructure.updateTOCfiles(sectionPath, propertyName, newValue)
    
    # change the section.json
    sectionJSONPath = fs.BookInfoStructure.readProperty(sectionPath)["path"]
    fullPropertyName =fs.TOCStructure.TOC_SECTION_PROPERTIES.getPropertyFormPath(sectionPath, propertyName)
    _u.updateJSONProperty(sectionJSONPath, fullPropertyName, newValue)

def changeSectionStartPage(sectionPath, newValue):
    _changeSectionProperty(sectionPath, fs.TOCStructure.TOC_SECTION_PROPERTIES.start_ID, newValue)

def changeSectionFinishPage(sectionPath, newValue):
    _changeSectionProperty(sectionPath, fs.TOCStructure.TOC_SECTION_PROPERTIES.finish_ID, newValue)

def changeSectionTOCText(sectionPath, newValue):
    _changeSectionProperty(sectionPath, fs.TOCStructure.TOC_SECTION_PROPERTIES.text_ID, newValue)

def removeSection():
    # # remove to Sections structure
    # fs.SectionInfoStructure.removeSection(sectionPath)
    
    # # remove BookInfo structure
    # fs.BookInfoStructure.removeSection(sectionPath)

    # # remove TOC structure
    # fs.SectionInfoStructure.removeSection(sectionPath)
    pass

def passMarerialToBook():
    # original structure add material

    # add to original material list
    pass

def backupBookToDB():
    pass

def loadBookFromDB():
    pass