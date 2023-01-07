import os
import tkinter as tk
from _utils import _BookChoosingMenus, getPathToBooks

buttonLabel="build LaTeX"
buttonName="build_latex"
pathToBooks = getPathToBooks()

# create UI
master = tk.Tk()
master.title("Propagate changes from template")
master.geometry("320x80")


# chaptersList = ["*"]

def callbackOptionWrapper(event):
    callbackOption()

def createButton(buttonLabel, buttonName):
    buttonText = tk.StringVar()
    buttonText.set(buttonLabel)
    build_latex_button = tk.Button(master, 
                                textvariable = buttonText, 
                                width = 10, 
                                name=buttonName, 
                                command = lambda: callbackButton())
    build_latex_button.pack()

def processChapterTex(chapterName):
    texFiles = [i for i in os.listdir(pathToBooks + book_name.get() + "/" + chapterName) if ".tex" in i]
    for fileName in texFiles:
        fileDirPath = pathToBooks + "/" + book_name.get() + "/" + chapterName + "/" 
        filePath = pathToBooks + "/" + book_name.get() + "/" + chapterName + "/" + fileName
        os.system("${BOOKS_PROCESS_TEX_PATH}../onTexFileSave.sh " + filePath + " " + fileDirPath)

def callbackButton():
    if chapter.get() == "*":
        for ch in chaptersList:
            if ch != "*":
                processChapterTex(ch)
    else:
        processChapterTex(chapter.get())
    pass

def callbackOption():
    global chapter
    global chaptersList

    # destroy the button and the chapters menu
    for widget in master.winfo_children():
        if widget._name != "!optionmenu":
            widget.destroy()
    

    chapter, chapter_menu, chaptersList = _BookChoosingMenus.ChooseBookChapter.getOptionMenu_ChooseChapter(master, book_name)
    chapter_menu.pack()
    createButton(buttonLabel, buttonName)

# functions to bind "enter" and "escape"
def callbackButtonEnterBind(event):
    callbackButton()
def callbackButtonEscBind(event):
    master.destroy()

master.bind('<Return>', callbackButtonEnterBind)
master.bind('<Escape>', callbackButtonEscBind)

# Create the list of books we have
book_name, book_menu = _BookChoosingMenus.createBookChoosingOptionMenu(master, callbackOptionWrapper)
book_menu.pack()

createButton(buttonLabel, buttonName)

master.configure(bg='red')

# master.after(1000, )
tk.mainloop()
