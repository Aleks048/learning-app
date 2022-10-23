import tkinter as tk

import _utils._utils_main as _u


def getOptionsMenu_ChooseBook(mainWinRoot, namePrefix = ""):
    def bookMenuChooseCallback(bookNameStVar):
        bookName = bookNameStVar.get()
        bookPaths = _u.Settings.readProperty(_u.Settings.PubProp.booksPaths_ID)
        bookPath = bookPaths[bookName]
        _u.Settings.setCurrentBook(bookName, bookPath)


    default_book_name="Select a a book"

    '''
    functions that retrun options menus for choosing book
    '''
    book_name = tk.StringVar()
    book_name.set(default_book_name)

    # Create the list of books we have
    listOfBooksNames = _u.getListOfBooks()

    frame = tk.Frame(mainWinRoot, name = namePrefix.lower() + "_chooseBook_optionMenu", background="Blue")
    book_menu = tk.OptionMenu(frame, book_name, 
                            *listOfBooksNames, command= lambda x: bookMenuChooseCallback(book_name))
    book_menu.grid(row=0, column = 0)
    
    return frame