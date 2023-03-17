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
        
        p = subprocess.Popen(['open', url])
        p.wait()
        _waitDummy = p.communicate()
        log.autolog("Opened {0} in skim.".format(pdfPath))
    
    @classmethod
    def openSubsectionPDF(cls, positionIDX, topSection, subsecPath, bookName):
        fullSecpath = fsm.Wr.Utils.joinTopAndSubsection(topSection, subsecPath)
        secNameWPrefix = fsm.Wr.Utils.getSectionNameWPrefix(fullSecpath)
        pdfPage = fsm.Wr.Utils.getPDFPageFromPosIDX(positionIDX)
        bookPath = sf.Wr.Manager.Book.getPathFromName(bookName)
        if bookPath == _u.Token.NotDef.str_t:
            log.autolog("Could not find the path for the book with name '" 
                        + bookName + "'. Abropt processing link :'" + secNameWPrefix + "'.")
            return

        pdfPath = _upan.Paths.PDF.getAbs(bookPath, secNameWPrefix)

        cls.openPDF(pdfPath, pdfPage)

currPdfApp = SkimCalls
        