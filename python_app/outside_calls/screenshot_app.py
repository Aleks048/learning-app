import os

class ScreenshotApp:
    def takeScreenshot(savePath):
        os.system("screencapture -ix " + savePath + ".png")

currScreenshotApp = ScreenshotApp