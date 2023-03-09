import file_system.file_system_facade as fsm
import _utils.logging as log
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import settings.facade as sf


import subprocess

class MacLatex:
    def buildPDF(bookpath, subsection):
        subsectionDir = _upan.Paths.Section.getAbs(bookpath, subsection)
        mainTexFilepath = _upan.Paths.TexFiles.Main.getAbs(bookpath, subsection)
        cmd = "\
    pushd {1}\n\
        CMD=\"pdflatex  --shell-escape -xelatex -synctex=1 -interaction=nonstopmode -file-line-error -output-directory={1}/_out {0}\"\n\
        echo \"Running command:\"$CMD\n\
        $CMD\n\
    \n\
    popd".format(mainTexFilepath, subsectionDir, subsection)
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        log.autolog("Built subsection: {0}".format(subsection))


    @classmethod 
    def buildCurrentSubsectionPdf(cls):
        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        subsection = fsm.Wr.SectionCurrent.getSectionNameNoPrefix()
        
        cls.buildPDF(bookPath, subsection)

    def buildSubsectionPdf(subsection, bookName):
        sectionNameWprefix = subsection
        bookPath = bookName 
        sectionFolder = _upan.Paths.TexFiles.Main.getAbs(bookPath, subsection)
        mainTexFilepath = _upan.Paths.Section.getAbs(bookPath, subsection)
        log.autolog("build: " + mainTexFilepath)
        
        # NOTE: we add "_con.tex" to comply with what is called when the file is saved
        cmd = "echo 3 | ${BOOKS_ON_FILE_SAVE_PATH}/s_onTexFileSave.sh" \
                            " " + mainTexFilepath + \
                            " " + sectionFolder + \
                            " " + sectionNameWprefix + "_con.tex > /dev/null 2>&1"
        
        subprocess.call(cmd, shell=True)
        return True

currLatecDistro = MacLatex