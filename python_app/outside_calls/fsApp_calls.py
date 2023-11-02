import subprocess
import os
import shutil

import time
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

    def copyFile(sourceFilepath, destFilepath):
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