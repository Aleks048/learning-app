import os
import tkinter as tk
from tkinter import messagebox
from threading import Thread

import _utils._utils_main as _u
import file_system.file_system_main as fs
import UI.widgets_vars as wv
import UI.widgets_utils as wu

'''
UI tk primvars
'''
class UItkVariables:
    needRebuild = None
    buttonText = None
    createTOCVar = None
    TOCWithImageVar = None
    subchapter = None
    imageGenerationEntryText = None
    scrshotPath = None
    currCh = None
    currSubch = None

def addConfirmationWidgets(mainWinRoot, inText, onYesFunction):

    l1=tk.Label(mainWinRoot, image="::tk::icons::question")
    l2=tk.Label(mainWinRoot,text= inText)

    b1=tk.Button(mainWinRoot,text="Yes",command = onYesFunction, width = 10)
    b2=tk.Button(mainWinRoot,text="No",command= mainWinRoot.destroy,width = 10)

    return l1, l2, b1, b2


class ChooseBookSection:

    def getOptionsMenu_ChooseBook(mainWinRoot, namePrefix = ""):
        def bookMenuChooseCallback(bookNameStVar):
            bookName = bookNameStVar.get()
            bookPaths = _u.Settings.readProperty(_u.Settings.PubProp.booksPaths_ID)
            bookPath = bookPaths[bookName]
            _u.Settings.Book.setCurrentBook(bookName, bookPath)


        default_book_name="Select a a book"

        '''
        functions that retrun options menus for choosing book
        '''
        book_name = tk.StringVar()
        book_name.set(default_book_name)

        # Create the list of books we have
        listOfBooksNames = _u.getListOfBooks()
        print(listOfBooksNames)

        frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_chooseBook_optionMenu", background="Blue")
        book_menu = tk.OptionMenu(frame, book_name, 
                                *listOfBooksNames, command= lambda x: bookMenuChooseCallback(book_name))
        book_menu.grid(row=0, column = 0)
        
        return frame

    
    @classmethod
    def getOptionMenu_ChooseTopSection(cls, mainWinRoot, namePrefix = ""):
        '''
        functions that retrun options menus for choosing chapter
        '''
        def chapterChoosingCallback(chapter):
            print("chapterChoosingCallback - switching to chapter: " + chapter.get())
            
            fs.BookInfoStructure.updateProperty(fs.BookInfoStructure.currSection_ID , chapter.get())

            chapterImIndex = _u.BookSettings.ChapterProperties.getCurrChapterImIndex()
            wv.UItkVariables.imageGenerationEntryText.set(chapterImIndex)

            
            wu.Screenshot.setValueScreenshotLoaction()
            
            subchaptersList = wu._getSubchaptersListForCurrChapter()
            wu._updateOptionMenuOptionsList(mainWinRoot, "_chooseSubchapter_optionMenu", subchaptersList)
            currSubchapter = _u.BookSettings.ChapterProperties.getChapterLatestSubchapter(fs.BookInfoStructure.readProperty(fs.BookInfoStructure.currSection_ID)[2:])
            UItkVariables.subchapter.set(currSubchapter)
            fs.BookInfoStructure.updateProperty(fs.BookInfoStructure.currSectionFull_ID, subchaptersList[0])

            currLayoutClass = _u.Settings.Layout.getCurrLayoutClass()
            currLayoutClass.pyAppHeight = mainWinRoot.winfo_height()
            currLayoutClass.set(mainWinRoot)
            layouts_main.moveWholeBookToChapter()


        chapter = tk.StringVar()
        chapter.set(fs.BookInfoStructure.readProperty(fs.BookInfoStructure.currSection_ID))

        book_name = _u.Settings.readProperty(_u.Settings.getCurrentBookFolderName())

        pathToBooks = _u.getPathToBooks()
        chaptersList = []
        chaptersList.extend([i for i in os.listdir(pathToBooks + "/" + book_name) if i[:2]=="ch"])
        chaptersList.sort(key=lambda x: -1 if x[2:]=="" else int(x[2:]))
        
        frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_chooseChapter_optionMenu", background="Blue")
        chapter_menu = tk.OptionMenu(frame, chapter, *chaptersList, command= lambda x: chapterChoosingCallback(chapter))
        chapter_menu.grid(row = 0, column = 0)

        return frame

    
    @classmethod
    def getOptionMenu_ChooseSubchapter(cls, mainWinRoot, namePrefix = ""):
        def subchapterChoosingCallback(subchapter):
            _u.BookSettings.ChapterProperties.updateChapterLatestSubchapter(fs.BookInfoStructure.readProperty(fs.BookInfoStructure.currSection_ID)[2:],
                                                                    subchapter.get())
            _u.BookSettings.updateProperty(_u.BookSettings.CurrentStateProperties.Book.currSectionFull_ID, subchapter.get())
        

        UItkVariables.subchapter  = tk.StringVar()
        subchapter = UItkVariables.subchapter
        subchapter.set(_u.BookSettings.readProperty(_u.BookSettings.CurrentStateProperties.Book.currSectionFull_ID))
        
        subchaptersList = cls._getSubchaptersListForCurrChapter()

        frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_chooseSubchapter_optionMenu", background="Blue")
        subchapter_menu = tk.OptionMenu(frame, subchapter, *subchaptersList, command= lambda x: subchapterChoosingCallback(subchapter))
        subchapter_menu.grid(row = 0, column = 0)
        return frame
    
