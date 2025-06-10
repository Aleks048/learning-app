import platform

import _utils._utils_main as _u

class ScreenshotApp:
    def takeScreenshot(savePath):
        if platform.system() == "Darwin":
            _u.runCmdAndWait("screencapture -ix '{0}'".format(savePath))
        elif platform.system() == "Windows":
            #TODO: possible implementation https://stackoverflow.com/a/48669645
            raise NotImplementedError()

currScreenshotApp = ScreenshotApp