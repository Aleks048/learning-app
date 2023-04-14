import os

import tex_file.tex_file_facade as tff
import outside_calls.outside_calls_facade as ocf
import file_system.file_system_facade as fsf
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import _utils.logging as log
import settings.facade as sf

def processCall(callerTexFilePath:str):
    log.autolog("Processing 'populate main file' request: '{0}'.".format(callerTexFilePath))
    # get the section name from the path
    subsectionDir = "/".join(callerTexFilePath.split("/")[:-1])
    subsectionJSONfile = os.path.join(subsectionDir, "sectionInfo.json")
    subsection = _u.JSON.readProperty(subsectionJSONfile, "_name")
    
    callertexFilename = callerTexFilePath.split("/")[-1]
    idx = _upan.Names.getIdxFromSubsectionFilesname(callertexFilename)

    bookPaths = sf.Wr.Manager.Book.getListOfBooksPaths()
    bookPath = ""

    for bp in bookPaths:
        if bp in callerTexFilePath:
            bookPath = bp
            break
    
    # #build subsection the pdf
    ocf.Wr.LatexCalls.buildPDF(bookPath, subsection, idx)
