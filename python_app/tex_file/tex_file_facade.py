import tex_file.tex_file_populate as tfpo
import tex_file.tex_file_modify as tfm
import tex_file.tex_file_process as tfpr
import tex_file.tex_file_utils as tfu

class Data:
    pass

class Wr:
    class TexFilePopulate(tfpo.TexFilePopulate):
        pass

    class TexFileModify(tfm.TexFileModify):
        pass
    
    class TexFileProcess(tfpr.TexFileProcess):
        pass
   
    class TexFileUtils:
        def getUrl(bookName, topSection, subsection, imIDX, linkType: str):
            return tfu.getUrl(bookName, topSection, subsection, imIDX, linkType , True)