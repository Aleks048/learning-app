import os
import json

import _utils._utils_main as _u
import _utils.logging as log
import file_system.book_fs as bfs
import _utils.pathsAndNames as _upan

import outside_calls.outside_calls_facade as ocf
import settings.facade as sf

class OriginalMaterialStructure:
    '''
    Structure to store the original pdf and other required material.
    '''

    originalMaterialBaseRelPath = "originalMaterial/"

    template = {
        "books": {
        }
    }
    
    class PubProp:
        materials = "materials"

        # book props
        path = "Path"
        currPage = "CurrPage"

    bookTemplate = {
        PubProp.path : "Path",
        PubProp.currPage : "CurrPage"
    }


    @classmethod
    def createStructure(cls, bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()):
        origMatAbsPath = _upan.Paths.OriginalMaterial.getAbs(bookPath)
        
        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(origMatAbsPath):   
            log.autolog("\
The structure was not present. Will create it.\n\
Creating path: '{0}'".format(origMatAbsPath))
            ocf.Wr.FsAppCalls.createFile(origMatAbsPath)
        
        # create file to track original materials with names and paths
        structureFile = cls.__getJSONfilepath()
        ocf.Wr.FsAppCalls.createFile(structureFile)
        _u.JSON.createFromTemplate(structureFile, cls.template)
    
    @classmethod
    def addOriginalMaterial(cls, filePath, structureRelPath, materialName):
        log.autolog("Adding material: '{0}' to rel path: '{1}'".format(structureRelPath, structureRelPath))
        
        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        basePath =  _upan.Paths.OriginalMaterial.getAbs(bookPath)
        originnalMaterialDestinationPath = os.path.join(basePath, structureRelPath)

        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(originnalMaterialDestinationPath):   
            log.autolog("Path '{0}' does not exist. Will create it.".format(originnalMaterialDestinationPath))
            createdFile = ocf.Wr.FsAppCalls.createFile(originnalMaterialDestinationPath)
            if not createdFile:
                return False
        
        # update curr material let path
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.currOriginalMaterialRelPath,
                                            structureRelPath)
        
        # update data structure to keep the dict of books and paths to them
        cls.setMaterialPath(materialName, originnalMaterialDestinationPath)
        cls.setMaterialPath(materialName, 1)
         
        
        log.autolog("Copying file '{0}' to '{1}'".format(filePath, originnalMaterialDestinationPath))
        ocf.Wr.FsAppCalls.copyFile(filePath, originnalMaterialDestinationPath)

    @classmethod
    def getOriginalMaterialsNames(cls):
        origMatDict = cls.__getMaterailsDict()
        return list(origMatDict.keys())

    @classmethod
    def getMaterialPath(cls, bookName):
        books = cls.__getMaterailsDict()
        try:
            return books[bookName][OriginalMaterialStructure.PubProp.path]
        except:
            log.autolog("No book with name '{0}'".format(bookName))
            return None
    
    @classmethod
    def getMaterialCurrPage(cls, bookName):
        books = cls.__getMaterailsDict()
        
        try:
            return books[bookName][OriginalMaterialStructure.PubProp.currPage]
        except:
            log.autolog("No book with name '{0}'".format(bookName))
            return None
    
    @classmethod
    def setMaterialPath(cls, materialName, materialPath):
        books = cls.__getMaterailsDict()   
        books[materialName][OriginalMaterialStructure.PubProp.path] = materialPath
        cls.__updateMaterialDict(books)
    
    @classmethod
    def setMaterialCurrPage(cls, materialName, currPage):
        books = cls.__getMaterailsDict()
        books[materialName][OriginalMaterialStructure.PubProp.currPage] = currPage
        cls.__updateMaterialDict(books)
        
    @classmethod
    def __getJSONfilepath(cls,  bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()) -> str:
        origMatAbsPath = _upan.Paths.OriginalMaterial.getAbs(bookPath)
        # create file to track original materials with names and paths
        return os.path.join(origMatAbsPath, "origMat.json")
    
    @classmethod
    def __updateMaterialDict(cls, newMatDict):
        jsonFilepath = cls.__getJSONfilepath()
        _u.JSON.updateProperty(jsonFilepath, 
                               OriginalMaterialStructure.PubProp.materials,
                               newMatDict)
        pass
    
    @classmethod
    def __getMaterailsDict(cls) -> dict:
        jsonFilepath = cls.__getJSONfilepath()
        
        return _u.JSON.readProperty(jsonFilepath,
                                    cls.PubProp.materials)