import subprocess
from threading import Thread

import file_system.file_system_facade as fsm
import _utils.logging as log
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import settings.facade as sf
import outside_calls.fsApp_calls as fsc
import tex_file.tex_file_facade as tff


class MacLatex:
    def buildPDF(bookpath, subsection, imIdx = _u.Token.NotDef.str_t):
        return
        def __build():
            tff.Wr.TexFilePopulate.populateMainFile(subsection, bookpath, imIdx)

            subsectionDir = _upan.Paths.Section.getAbs(bookpath, subsection)
            mainTexFilepath = _upan.Paths.TexFiles.Main.getAbs(bookpath, subsection, imIdx)

            subsectionWPrefix = _upan.Names.addSectionPrefixToName(subsection)

            cmd = "\
        pushd {1}\n\
            CMD=\"pdflatex  --shell-escape -synctex=1 -interaction=nonstopmode -file-line-error -output-directory={1}/_out {0}\"\n\
            echo \"Running command:\"$CMD\n\
            $CMD\n\
        \n\
        popd".format(mainTexFilepath, subsectionDir, subsectionWPrefix)
            
            _, err = _u.runCmdAndGetResult(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            if err != "":
                log.autolog("While building the error occured: '{0}'.".format(err))
            
            log.autolog("Built subsection: '{0}' from file '{1}'.".format(subsection, mainTexFilepath))
            
            # move generated pdf
            mainPDFFilepath = _upan.Paths.PDF.getAbs(bookpath, subsection, imIdx)
            outputPDF = _upan.Paths.TexFiles.Output.PDF.getAbs(bookpath, subsection, imIdx)
            fsc.currFilesystemApp.copyFile(outputPDF, mainPDFFilepath)
        t = Thread(target = __build)
        t.start()

    @classmethod 
    def buildCurrentSubsectionPdf(cls):
        return
        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        subsection = fsm.Wr.SectionCurrent.getSectionNameNoPrefix()
        
        cls.buildPDF(bookPath, subsection)

currLatecDistro = MacLatex