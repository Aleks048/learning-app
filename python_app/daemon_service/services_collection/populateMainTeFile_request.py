import tex_file.tex_file_facade as tff
import outside_calls.outside_calls_facade as ocf
import file_system.file_system_facade as fsm
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import shutil
import _utils.logging as log
import settings.facade as sf

def processCall(callerTexFilePath):
    log.autolog("Processing 'populate main file' request: '{0}'.".format(callerTexFilePath))
    # get the section name from the path
    subsectionName = callerTexFilePath.split("/")[-1]
    subsectionName = "_".join(subsectionName.split("_")[:-1])

    bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
    
    # #build subsection the pdf
    ocf.Wr.LatexCalls.buildPDF(bookPath, subsectionName)
