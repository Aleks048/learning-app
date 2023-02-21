import file_system.file_system_manager as fsm
import _utils.logging as log
import subprocess

class MacLatex:
    def buildPDF(bookpath, subsection):
        subsectionDir = fsm.Wr.Paths.Section.getAbs(bookpath, subsection)
        mainTexFilepath = fsm.Wr.Paths.TexFiles.Main.getAbs(bookpath, subsection)
        cmd = "\
    pushd {1}\n\
        CMD=\"pdflatex  --shell-escape -xelatex -synctex=1 -interaction=nonstopmode -file-line-error -output-directory={1}/_out {0}\"\n\
        echo \"Running command:\"$CMD\n\
        $CMD\n\
    \n\
    popd".format(mainTexFilepath, subsectionDir, subsection)
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        log.autolog("Built subsection: {0}".format(subsection))

currLatecDistro = MacLatex