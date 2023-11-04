import os
import shutil
import pathlib
from distutils.dir_util import copy_tree

import _utils._utils_main as _u
import _utils.logging as log
import settings.facade as sf

class FinderCalls:
    @classmethod
    def deleteFile(cls, filepath):
        if cls.checkIfFileOrDirExists(filepath):
            os.remove(filepath)
        else:
            log.autolog("Could not remove filepath: '{0}'. It does not seem to exist.".format(filepath))

    @classmethod
    def moveFile(cls, sourceFilepath, destFilepath):
        cls.copyFile(sourceFilepath, destFilepath)
        cls.deleteFile(sourceFilepath)

    @classmethod
    def copyFile(cls, sourceFilepath, destFilepath):
        sourceFilepath_pl = pathlib.Path(sourceFilepath)
        destFolder = pathlib.Path(destFilepath).parent

        if not cls.checkIfFileOrDirExists(destFolder):
            os.makedirs(destFolder, exist_ok=True)

        if not sourceFilepath_pl.is_file():
            return copy_tree(sourceFilepath, destFilepath)

        return shutil.copy2(sourceFilepath, destFilepath)

    def moveFolder(sourceFilepath, destFilepath):
        return shutil.move(sourceFilepath, destFilepath)

    def openFile(filepath):
        cmd = "open file://" + filepath + " &"
        _u.runCmdAndWait(cmd)
        log.autolog("Opened file: '{0}'".format(filepath))
    
    @classmethod
    def checkIfImageExists(cls, filepath):
        return cls.checkIfFileOrDirExists(filepath + ".png")
    
    def checkIfFileOrDirExists(filepath):
        return os.path.exists(filepath)
    
    @classmethod
    def createDir(cls, filepath):
        if cls.checkIfFileOrDirExists(filepath):
            return False
        else:
            os.makedirs(filepath, exist_ok=True)
            return True
    
    @classmethod
    def removeDir(cls, filepath):
        if not cls.checkIfFileOrDirExists(filepath):
            return False
        else:
            shutil.rmtree(filepath)
            return True
    
    def createFile(filepath):
        open(filepath, "w").close()


currFilesystemApp = FinderCalls