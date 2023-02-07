import tex_file.tex_file_manager as tfm
import outside_calls.latex_calls as lc
import file_system.file_system_manager as fsm
import _utils._utils_main as _u
import shutil
import _utils.logging as log

def processCall(callerTexFile):
    # get the section name from the path
    subsectionName = fsm.Wr.Paths.TexFiles.getSectionFromPath_Whole_WPrefix(callerTexFile)
    bookName =  fsm.Wr.Paths.TexFiles.getBooknameFromPath(callerTexFile)
    bookPaths = _u.Settings.readProperty(_u.Settings.PubProp.booksPaths_ID)
    bookPath = bookPaths[bookName]
    
    # populate the main file
    tfm.Wr.TexFile.populateMainFile(subsectionName, bookPath)
    
    #build subsection the pdf
    lc.currLatecDistro.buildPDF(bookPath, subsectionName)
    
    # move generated pdf
    mainPDFFilepath = fsm.Wr.Paths.PDF.getAbs(bookPath, subsectionName)
    outputPDF = fsm.Wr.Paths.TexFiles.Output.PDF.getAbs(bookPath, subsectionName)
    shutil.copy(outputPDF, mainPDFFilepath)
