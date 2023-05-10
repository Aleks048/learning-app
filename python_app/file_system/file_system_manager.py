import os
from unicodedata import name

import _utils.logging as log
import file_system.origmaterial_fs as omfs
import file_system.section_fs as sfs
import file_system.book_fs as bfs

import outside_calls.outside_calls_facade as ocf

import settings.facade as sf


class FileSystemManager:
    def addNewBook(bookName, bookPathDir):
        # TODO:check if a book with name exists and ask
        # if we want to delete and proceed
        # booksPath = _u.getPathToBooks()
        # bookPath = os.path.join(booksPath, bookName)

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(bookPathDir):
            log.autolog("The book at path '{0}' already exists!".format(bookPathDir))
            # TODO: ask the user we we should proceed.
            return False
        
        ocf.Wr.FsAppCalls.createDir(bookPathDir)

        #
        #create bookInfo structure
        #
        bfs.BookInfoStructure.createStructure()

        #create sections structure
        sfs.SectionInfoStructure.createStructure(bookName)

        # create originalMaterialStructure
        omfs.OriginalMaterialStructure.createStructure()

        return True


    def addOriginalMaterial(pathToSourceFile, relStructurePath, materialName):
        omfs.OriginalMaterialStructure.addOriginalMaterial(pathToSourceFile,
                                                            relStructurePath,
                                                            materialName)

    def addSectionForCurrBook(sectionPath):
        bookpath = sf.Wr.Manager.Book.getCurrBookFolderPath()

        # add to Sections structure
        sfs.SectionInfoStructure.addSection(bookpath, sectionPath)
        
        # add to BookInfo structure
        bfs.BookInfoStructure.addSection(sectionPath)


    def removeSection(secPath):
        # remove to Sections structure
        sfs.SectionInfoStructure.removeSection(secPath)
        
        # # remove BookInfo structure
        # fs.BookInfoStructure.removeSection(sectionPath)

        # # remove TOC structure
        # fs.SectionInfoStructure.removeSection(sectionPath)
        pass

# def moveSection():
#     pass

# def passMarerialToBook():
#     # original structure add material

#     # add to original material list
#     pass

# def backupBookToDB():
#     pass

# def loadBookFromDB():
#     pass