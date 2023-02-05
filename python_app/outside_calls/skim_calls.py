import os
import subprocess
import _utils._utils_main as _u
import _utils.logging as log
import file_system.file_system_manager as fsm

def openSubsectionPDF(positionIDX, topSection, subsecPath, bookName):
    fullSecpath = fsm.Wr.Utils.joinTopAndSubsection(topSection, subsecPath)
    secNameWPrefix = fsm.Wr.Utils.getSectionNameWPrefix(fullSecpath)
    pdfPage = fsm.Wr.Utils.getPDFPageFromPosIDX(positionIDX)
    bookPath = _u.getBookPath(bookName)
    if bookPath == _u.Token.NotDef.str_t:
        log.autolog("Could not find the path for the book with name '" 
                    + bookName + "'. Abropt processing link :'" + secNameWPrefix + "'.")
        return

    pdfPath = fsm.Wr.Paths.PDF.getAbs(bookPath, secNameWPrefix)

    # open pdf in skim on the desired page
    url = "skim://{0}#page={1}".format(pdfPath, pdfPage)
    subprocess.Popen(['open', url])