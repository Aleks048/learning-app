import os

import _utils._utils_main as _u
import _utils.logging as log
import file_system.book_fs as bfs
import _utils.pathsAndNames as _upn

import outside_calls.outside_calls_facade as ocf
import settings.facade as sf

class OriginalMaterialStructure:
    '''
    Structure to store the original pdf and other required material.
    '''

    originalMaterialBaseRelPath = "originalMaterial/"
    
    @classmethod
    def createStructure(cls):
        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        origMatAbsPath = _upn.Paths.OriginalMaterial.getAbs(bookPath)
        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(origMatAbsPath):   
            log.autolog("The structure was not present. Will create it.")
            log.autolog("Creating path: '{0}'".format(origMatAbsPath))
            ocf.Wr.FsAppCalls.createFile(origMatAbsPath)
    
    @classmethod
    def addOriginalMaterial(cls, filePath, structureRelPath):
        log.autolog("Adding material: '{0}' to rel path: '{1}'".format(structureRelPath, structureRelPath))
        
        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        basePath =  _upn.Paths.OriginalMaterial.getAbs(bookPath)
        originnalMaterialDestinationPath = os.path.join(basePath, structureRelPath)

        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(originnalMaterialDestinationPath):   
            log.autolog("Path '{0}' does not exist. Will create it.".format(originnalMaterialDestinationPath))
            createdFile = ocf.Wr.FsAppCalls.createFile(originnalMaterialDestinationPath)
            if not createdFile:
                return False
        
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.originalMaterialRelPath_ID,
                                            structureRelPath)
         
        
        log.autolog("Copying file '{0}' to '{1}'".format(filePath, originnalMaterialDestinationPath))
        ocf.Wr.FsAppCalls.copyFile(filePath, originnalMaterialDestinationPath)
    
