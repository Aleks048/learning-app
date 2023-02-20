import subprocess
import os

class FinderCalls:
    def openFile(filepath):
        cmd = "open file://" + filepath
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()
    
    def checkIfFileExists(filepath):
        return os.path.isfile(filepath + ".png")
currFilesystemApp = FinderCalls