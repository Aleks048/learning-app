import settings.settings as s
import _utils._utils_main as _u
import _utils.logging as log


class Manager:  
    class Book:
        def getNameFromPath(bookPath):
            bookPathsDict = s.Settings.readProperty(s.Settings.PubProp.booksPaths_ID)
            for bookName in bookPathsDict.keys():
                tempBookPath = bookPathsDict[bookName]
                if tempBookPath == bookPath:
                    return bookName
            
            log.autolog("No name for book with path '{0}'. Something is wrong!".format(bookPath))
            return _u.Token.NotDef.str_t

        def getPathFromName(bookName):
            bookPathsDict = s.Settings.readProperty(s.Settings.PubProp.booksPaths_ID)
            if bookName in bookPathsDict.keys():
                bookPath = bookPathsDict[bookName]
                return bookPath
            else:
                log.autolog("No path for book with name '{0}'. Something is wrong!".format(bookName))
                return _u.Token.NotDef.str_t

        @classmethod
        def addNewBook(cls, bookName, bookPath):
            cls.setCurrentBook(bookName, bookPath)
            booksPaths = s.Settings.readProperty(s.Settings.PubProp.booksPaths_ID)
            booksPaths[bookName] = bookPath
            s.Settings.updateProperty(s.Settings.PubProp.booksPaths_ID, booksPaths)

        def setCurrentBook(bookName, bookPath):
            s.Settings.updateProperty(s.Settings.PubProp.currBookPath_ID, bookPath)
            s.Settings.updateProperty(s.Settings.PubProp.currBookName_ID, bookName)

        def getCurrBookFolderPath():
            return s.Settings.readProperty(s.Settings.PubProp.currBookPath_ID)
        
        def getCurrBookName():
            return s.Settings.readProperty(s.Settings.PubProp.currBookName_ID)
        

        @classmethod
        def getListOfBooksNames(cls):
            return list(cls.getListBooksPathsDict().keys())
       
        @classmethod
        def getListOfBooksPaths(cls):
            return list(cls.getListBooksPathsDict().values())

        def getListBooksPathsDict():
            booksPathsDict = s.Settings.readProperty(s.Settings.PubProp.booksPaths_ID)
            return booksPathsDict