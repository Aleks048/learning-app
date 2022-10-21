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

def createSectionForCurrBook(sectionPath):
    # add to Sections structure
    fs.SectionInfoStructure.addSection(sectionPath)
    
    # add to BookInfo structure
    fs.BookInfoStructure.addSection(sectionPath)

    # add to TOC structure
    # fs.SectionInfoStructure.addSection(sectionPath)


    pass

def removeSection():
    pass

def passMarerialToBook():
    pass

def backupBookToDB():
    pass

def loadBookFromDB():
    pass