import subprocess
import os
import shutil

import time
import _utils._utils_main as _u
import _utils.logging as log
import settings.facade as sf

class FinderCalls:

    def copyFile(sourceFilepath, destFilepath):
        return shutil.copy2(sourceFilepath, destFilepath)

    def openFile(filepath):
        cmd = "open -W file://" + filepath + " &"
        _u.runCmdAndWait(cmd)
        log.autolog("Opened file: '{0}'".format(filepath))
    
    @classmethod
    def checkIfImageExists(cls, filepath):
        return cls.checkIfFileOrDirExists(filepath + ".png")
    
    def checkIfFileOrDirExists(filepath):
        return os.path.exists(filepath)
    
    @classmethod
    def createFile(cls, filepath):
        if cls.checkIfFileOrDirExists(filepath):
            return False
        else:
            os.makedirs(filepath, exist_ok=True)
            return True


currFilesystemApp = FinderCalls