import os
from unicodedata import name

import _utils._utils_main as _u
import _utils.logging as log
import file_system.origmaterial_fs as omfs
import file_system.section_fs as sfs
import file_system.toc_fs as tocfs
import file_system.book_fs as bfs
import file_system.paths as p
import file_system.links as l
import file_system._utils as fsu

'''
Facade for Filesystem
'''

class Data:
    pass

class Wr:
    class BookInfoStructure(bfs.BookInfoStructure):
        pass

    class SectionInfoStructure(sfs.SectionInfoStructure):
        pass
    
    class SectionCurrent(sfs.SectionCurrent):
        pass

    class TOCStructure(tocfs.TOCStructure):
        pass

    class OriginalMaterialStructure(omfs.OriginalMaterialStructure):
        pass

    class Paths:
        class Screenshot(p.Paths.Screenshot):
            pass
            
        class Scripts(p.Paths.Scripts):
            pass

        class Section(p.Paths.Section):
            pass

        class TexFiles(p.Paths.TexFiles):
            pass
        
        class PDF(p.Paths.PDF):
            pass


    class Links:
        class LinkDict(l.LinkDict):
            pass

        class ImIDX(l.ImIDX):
            pass

        class ImLink(l.ImLink):
            pass

    class Utils(fsu.Utils):
        pass


class PropIDs:
    class Sec(sfs.SectionInfoStructure.PubProp):
        pass

    class Book(bfs.BookInfoStructure.PubProp):
        pass

    class TOC(tocfs.TOCStructure.PubPro):
        pass


def createNewBook(bookName):
    # check if a book with name exists and ask
    # if we want to delete and proceed
    booksPath = _u.getPathToBooks()
    bookPath = os.path.join(booksPath, bookName)

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
    bfs.BookInfoStructure.createStructure()

    #create sections structure
    sfs.SectionInfoStructure.createStructure()

    #create TOCstructure
    tocfs.TOCStructure.createStructure()

    # create originalMaterialStructure
    omfs.OriginalMaterialStructure.createStructure()

def addSectionForCurrBook(sectionPath):
    # add to Sections structure
    sfs.SectionInfoStructure.addSection(sectionPath)
    
    # add to BookInfo structure
    bfs.BookInfoStructure.addSection(sectionPath)

    # add to TOC structure
    tocfs.TOCStructure.addSection(sectionPath)

def _updateSectionProperty(sectionPath, propertyName, newValue):
    # thange the TOC
    tocfs.TOCStructure.updateTOCfiles(sectionPath, propertyName, newValue)
    
    # change the section.json
    sectionJSONPath = bfs.BookInfoStructure.readProperty(sectionPath)["path"]
    fullPropertyName =tocfs.TOCStructure.PubPro.getPropertyFormPath(sectionPath, propertyName)
    _u.JSON.updateProperty(sectionJSONPath, fullPropertyName, newValue)

def updateSectionStartPage(sectionPath, newValue):
    _updateSectionProperty(sectionPath, tocfs.TOCStructure.PubPro.start_ID, newValue)

def updateSectionFinishPage(sectionPath, newValue):
    _updateSectionProperty(sectionPath, tocfs.TOCStructure.PubPro.finish_ID, newValue)

def updateSectionTOCText(sectionPath, newValue):
    _updateSectionProperty(sectionPath, tocfs.TOCStructure.PubPro.text_ID, newValue)

def updateSectionProperty(sectionPath, propertyName, newValue):
    log.autolog(propertyName)
    sfs.SectionInfoStructure.updateProperty(sectionPath, propertyName, newValue)

def getSubsectionsList(sectionPath = ""):
    sections_ID = bfs.BookInfoStructure.PubProp.sections_ID
    outSubsectionsList = []
    
    if sectionPath == _u.Token.NotDef.str_t:
        return []

    if sectionPath == "":
        subsections = bfs.BookInfoStructure.readProperty(sections_ID)
    else:
        subsections = bfs.BookInfoStructure.readProperty(sectionPath)[sections_ID]

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
    sections = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_ID)

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