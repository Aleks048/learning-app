import subprocess

class FinderCalls:
    def openFile(filepath):
        cmd = "open file://" + filepath
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()
currFilesystemApp = FinderCalls