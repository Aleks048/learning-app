import os

import scripts.osascripts as oscr
import _utils._utils_main as _u

class GoodNotes:
    def openPage(link):
        cmd = oscr.openNotesAppNotebook(link)
        _u.runCmdAndWait(cmd)

currNoteApp = GoodNotes