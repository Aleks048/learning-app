import os
import tkinter as tk
from _utils._utils_main import _BookChoosingMenus, getPathToBooks


# create UI
master = tk.Tk()
master.title("Set screenshot location")
master.geometry("320x80")

def optionMenuChooseBookCallback(event):
    global chapter_name
    for widget in master.winfo_children():
        if widget._name != "!optionmenu":
            widget.destroy()
    chapter_name, chapter_menu, _ = _BookChoosingMenus.ChooseBookChapter.getOptionMenu_ChooseChapter(master, book_name, optionMenuChooseChapterCallback)
    chapter_menu.pack()

# Create the optionMenu of books we have
book_name, book_menu = _BookChoosingMenus.createBookChoosingOptionMenu(master, optionMenuChooseBookCallback)
book_menu.pack()

def optionMenuChooseChapterCallback(event):
    pathToScreenshot = getPathToBooks() + book_name.get() + "/" + chapter_name.get() + "/images"
    # os.system("defaults write com.apple.screencapture location " + pathToScreenshot)

# Create the optionMenu of chapter we have in  book we chose
chapter_name, chapter_menu, _ = _BookChoosingMenus.ChooseBookChapter.getOptionMenu_ChooseChapter(master, book_name, optionMenuChooseChapterCallback)
chapter_menu.pack()


def escapeBind(event):
    master.destroy()
master.bind('<Escape>', escapeBind)

master.configure(bg='red')

# master.after(1000, )
tk.mainloop()