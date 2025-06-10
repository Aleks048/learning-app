import platform

import _utils._utils_main as _u

class ScreenshotApp:
    def takeScreenshot(savePath):
        if platform.system() == "Darwin":
            _u.runCmdAndWait("screencapture -ix '{0}'".format(savePath))
        elif platform.system() == "Windows":
            raise NotImplementedError()
currScreenshotApp = ScreenshotApp