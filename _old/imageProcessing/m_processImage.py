import os
import subprocess
import tkinter as tk
from pathlib import Path
from _utils._utils_main import UIWidgets, Settings
import json
# from tkinter import 


def addImageProcessingUI(root):
    outElements = []

    currScreenShotDirText = UIWidgets.Screenshot.getText_CurrentScreenshotDir(root)

    UIGwidgets = UIWidgets.getTextEntryButton_imageGeneration(root)
    entry = UIGwidgets[0]
    processButton = UIGwidgets[1]

    outElements.append(currScreenShotDirText)
    outElements.append(entry)
    outElements.append(processButton)
    
    # currScreenShotDirText.pack()
    # entry.pack()
    # processButton.pack()

    # root.bind('<Return>', escCallback)
    # root.bind("<Escape>",lambda e: root.destroy())
    return outElements


if __name__=="__main__":
    root = tk.Tk()
    outElements = addImageProcessingUI(root)
    for e in outElements:
        e.pack()
    tk.mainloop()