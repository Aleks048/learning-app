import os

class Data:
    class Book:
        """
        Book
        """
        pass

    class Section:
        """
        Section
        """
        pass

    class Settings:
        """
        Settings
        """
        currState_ID = "currentState"
        data = {
            currState_ID : None,
            currState_ID + "_BookPath": None,
            currState_ID + "_BookName": None,
            currState_ID + "_Layout": None,     
            currState_ID + "_ScreenshotLocation": None,
            "whole_book": None,
            "booksPaths": None
        }
