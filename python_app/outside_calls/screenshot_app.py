import os

import _utils._utils_main as _u

class ScreenshotApp:
    def takeScreenshot(savePath):
        _u.runCmdAndWait("screencapture -ix '{0}'".format(savePath))

currScreenshotApp = ScreenshotApp