import sys
import os

import _utils._utils_main as _u
import _utils.logging as log

'''
working with Settings
'''

class IdTokens:
    class Apps:
        skim_ID = "skim"
        vsCode_ID = "vscode"
        finder_ID = "finder"
    
    class Misc:
        wholeBook_ID= "whole_book"

class Settings:

    class PubProp:
        #current settings
        currState_ID = "currentState"
        currBookPath_ID = currState_ID + "_BookPath"
        currBookName_ID = currState_ID + "_BookName"
        currLayout_ID = currState_ID + "_Layout"        
        currScreenshotLocation_ID = currState_ID + "_ScreenshotLocation"

        booksPaths_ID = "booksPaths"
    
    #common
    booksSettingsName = "booksProcessingSettings.json"
    
    @classmethod
    def __getSettingsFileFilepath(cls):
        return os.environ['BOOKS_SETTINGS_PATH'] + cls.booksSettingsName

    @classmethod 
    def readProperty(cls, propertyName):
        # if cs.Data.Settings.data[propertyName] != None:
        #     return cs.Data.Settings.data[propertyName]
        # else:
        return _u.JSON.readProperty(cls.__getSettingsFileFilepath(), propertyName)

    @classmethod
    def updateProperty(cls, propertyName, newValue):
        _u.JSON.updateProperty(cls.__getSettingsFileFilepath(), propertyName, newValue)

