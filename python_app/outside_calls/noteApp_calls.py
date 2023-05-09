import os

class GoodNotes:
    def openPage(link):
        os.system("open -a GoodNotes \"{0}\"".format(link))
    pass

currNoteApp = GoodNotes