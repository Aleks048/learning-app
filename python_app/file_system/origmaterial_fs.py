import os

import _utils._utils_main as _u
import _utils.logging as log
import file_system.book_fs as bfs


class OriginalMaterialStructure:
    '''
    Structure to store the original pdf and other required material.
    '''

    originalMaterialBaseRelPath = "originalMaterial/"
    
    @classmethod
    def createStructure(cls):
        bookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
        getAbsPath = cls._getBaseAbsPath(bookPath)
        if not os.path.exists(getAbsPath):   
            log.autolog("The structure was not present. Will create it.")
            log.autolog("Creating path: " + getAbsPath)
            _waitDummy = os.makedirs(getAbsPath)
    
    @classmethod
    def addOriginalMaterial(cls, name, filePath, structureRelPath):
        log.autolog("Adding material: '" + name + "' to rel path: " + structureRelPath)
        bookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
        basePath = cls._getBaseAbsPath(bookPath)
        originnalMaterialDestinationPath = os.path.join(basePath, structureRelPath)
        log.autolog(originnalMaterialDestinationPath)
        if not os.path.exists(originnalMaterialDestinationPath):   
            log.autolog("Path '" 
                        + originnalMaterialDestinationPath 
                        + "'does not exist will create it")
            _waitDummy = os.makedirs(originnalMaterialDestinationPath)
        
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.originalMaterialRelPath_ID,
                                            structureRelPath)

        cmd = "cp " + filePath + " " + os.path.join(originnalMaterialDestinationPath) 
        log.autolog("Exacuting command: '" + cmd + "'")
        os.system(cmd)
    
    @classmethod
    def _getBaseAbsPath(cls, bookPath):
        return os.path.join(bookPath, cls.originalMaterialBaseRelPath)
    
