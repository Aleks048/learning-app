import tex_file.tex_file_manager as tfm
import outside_calls.latex_calls as lc
import file_system.file_system_manager as fsm
import _utils._utils_main as _u

def processCall(callerTexFile):
    # get the section name from the path
    subsectionName = fsm.Wr.Paths.TexFiles.getSectionFromPath_Whole_WPrefix(callerTexFile)
    print("hip::"+ subsectionName)
    bookName =  fsm.Wr.Paths.TexFiles.getBooknameFromPath(callerTexFile)
    print("hip::"+ bookName)
    bookPaths = _u.Settings.readProperty(_u.Settings.PubProp.booksPaths_ID)
    bookPath = bookPaths[bookName]
    # populate the main file
    tfm.Wr.TexFile.populateMainFile(subsectionName, bookPath)
    print("hip::"+ subsectionName)
    #build subsection the pdf
    lc.buildPDF(subsectionName)
