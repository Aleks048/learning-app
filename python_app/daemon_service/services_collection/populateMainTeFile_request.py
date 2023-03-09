import tex_file.tex_file_facade as tff
import outside_calls.latex_calls as lc
import file_system.file_system_facade as fsm
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import shutil
import _utils.logging as log
import settings.facade as sf

def processCall(callerTexFile):
    # get the section name from the path
    log.autolog("Hip:" + callerTexFile)
    subsectionName = _upan.Current.Paths.TexFiles.Paths.TexFiles.getSectionFromPath_Whole_WPrefix(callerTexFile)
    bookName =  sf.Wr.Manager.Book.getCurrBookName()
    bookPaths = sf.Wr.Manager.Book.getCurrBookFolderPath()
    bookPath = bookPaths[bookName]
    
    # populate the main file
    tff.Wr.TexFile.populateMainFile(subsectionName, bookPath)
    
    #build subsection the pdf
    lc.currLatecDistro.buildPDF(bookPath, subsectionName)
    
    # move generated pdf
    mainPDFFilepath = _upan.Paths.PDF.getAbs(bookPath, subsectionName)
    outputPDF = _upan.Paths.TexFiles.Output.PDF.getAbs(bookPath, subsectionName)
    shutil.copy(outputPDF, mainPDFFilepath)
