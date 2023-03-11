import file_system.file_system_facade as fsm
import _utils.logging as log
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import settings.facade as sf
import outside_calls.fsApp_calls as fsc
import tex_file.tex_file_facade as tff



import subprocess

class MacLatex:
    def buildPDF(bookpath, subsectionWPrefix):
        tff.Wr.TexFilePopulate.populateMainFile(subsectionWPrefix, bookpath)

        subsectionDir = _upan.Paths.Section.getAbs(bookpath, subsectionWPrefix)
        mainTexFilepath = _upan.Paths.TexFiles.Main.getAbs(bookpath, subsectionWPrefix)
        cmd = "\
    pushd {1}\n\
        CMD=\"pdflatex  --shell-escape -synctex=1 -interaction=nonstopmode -file-line-error -output-directory={1}/_out {0}\"\n\
        echo \"Running command:\"$CMD\n\
        $CMD\n\
    \n\
    popd".format(mainTexFilepath, subsectionDir, subsectionWPrefix)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        output, err = p.communicate()
        err = err.decode("utf-8")
        if err != "":
            log.autolog("While building the error occured: '{0}'.".format(err))
        
        log.autolog("Built subsection: '{0}'.".format(subsectionWPrefix))
        
        # move generated pdf
        mainPDFFilepath = _upan.Paths.PDF.getAbs(bookpath, subsectionWPrefix)
        outputPDF = _upan.Paths.TexFiles.Output.PDF.getAbs(bookpath, subsectionWPrefix)
        fsc.currFilesystemApp.copyFile(outputPDF, mainPDFFilepath)


    @classmethod 
    def buildCurrentSubsectionPdf(cls):
        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        subsection = fsm.Wr.SectionCurrent.getSectionNameWprefix()
        
        cls.buildPDF(bookPath, subsection)

currLatecDistro = MacLatex