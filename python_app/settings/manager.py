import settings.settings as s
import _utils._utils_main as _u
import _utils.logging as log


class Manager:  
    class Book:
        def getPathFromName(bookName):
            bookPaths = s.Settings.readProperty(s.Settings.PubProp.booksPaths_ID)
            if bookName in bookPaths.keys():
                bookPath = bookPaths[bookName]
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
        

        @classmethod
        def getListOfBooksNames(cls):
            return list(cls.getListBooksPathsDict().keys())
       
        @classmethod
        def getListOfBooksPaths(cls):
            return list(cls.getListBooksPathsDict().values())

        def getListBooksPathsDict():
            booksPathsDict = s.Settings.readProperty(s.Settings.PubProp.booksPaths_ID)
            return booksPathsDict

        @classmethod
        def getBookPath(cls, bookName):
            bookPathsDict = cls.getListBooksPathsDict()
            if bookName in list(bookPathsDict.keys()):
                return bookPathsDict[bookName]
            else:
                return _u.Token.NotDef.str_t