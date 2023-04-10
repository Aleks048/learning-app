import _utils._utils_main as _u
import _utils.logging as log

class VsCodeCalls:
    def openNewWindow(paths):
        cmd = "code -n "+ paths + " &"
        _u.runCmdAndWait(cmd)
    
    def openNewTab(path, line = 0):
        cmd = "code -g {0}:{1}:0".format(path, line) + " &"
        _u.runCmdAndWait(cmd)

currIdeApp = VsCodeCalls