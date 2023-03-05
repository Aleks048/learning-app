import subprocess
import os
import shutil

class FinderCalls:

    def copyFile(sourceFilepath, destFilepath):
        return shutil.copy2(sourceFilepath, destFilepath)

    def openFile(filepath):
        cmd = "open file://" + filepath
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()
    
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