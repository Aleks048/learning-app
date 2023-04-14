import os
import subprocess
from threading import Thread
import _utils._utils_main as _u
import _utils.logging as log
import file_system.file_system_facade as fsm
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import settings.facade as sf

class SkimCalls:
    def openPDF(pdfPath, pdfPage = _u.Token.NotDef.str_t):
        if pdfPage == _u.Token.NotDef.str_t:
            url = "skim://{0}".format(pdfPath)
        else:
            url = "skim://{0}#page={1}".format(pdfPath, pdfPage)
        
        _u.runCmdAndWait('open ' + url)
        log.autolog("Opened {0} in skim on page '{1}'.".format(pdfPath, pdfPage))
    
    @classmethod
    def openSubsectionPDF(cls, positionIDX, subsecPath, bookName):
        pdfPage = fsm.Wr.Utils.getPDFPageFromPosIDX(positionIDX)
        bookPath = sf.Wr.Manager.Book.getPathFromName(bookName)
        if bookPath == _u.Token.NotDef.str_t:
            log.autolog("Could not find the path for the book with name '{0}'. \n\
                        Abropt processing link :'{1}'.".format(bookName, subsecPath))
            return

        pdfPath = _upan.Paths.PDF.getAbs(bookPath, subsecPath, positionIDX)

        cls.openPDF(pdfPath, pdfPage)

currPdfApp = SkimCalls
        