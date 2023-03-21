import _utils._utils_main as _u

class VsCodeCalls:
    def openNewWindow(paths):
        cmd = "code -n "+ paths + " &"
        _u.runCmdAndWait(cmd)
    
    def openNewTab(paths):
        cmd = "code "+ paths
        _u.runCmdAndWait(cmd)

currIdeApp = VsCodeCalls