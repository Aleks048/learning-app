import data.constants as dc
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import _utils.logging as log
import settings.facade as sf
import file_system.file_system_facade as fsf

class TexFileProcess:
    @classmethod
    def getTocLine(cls, bookName, subsectionFull, subsection, imIdx):
        bookPath = sf.Wr.Manager.Book.getPathFromName(bookName)
        tocTexFilepath = _upan.Paths.TexFiles.TOC.getAbs(bookPath, subsectionFull)
        line = cls.__getIdxLine(imIdx, tocTexFilepath)

        extraLines = fsf.Data.Sec.imageTOCFileMoveLinesNumber(subsection)
        
        if extraLines == _u.Token.NotDef.str_t:
            extraLines = fsf.Data.Book.imageTOCFileMoveLinesNumber
        
        line = str(int(line) + int(extraLines))
        
        return line
    
    @classmethod
    def getConLine(cls, bookName, subsectionFull, subsection, imIdx):
        bookPath = sf.Wr.Manager.Book.getPathFromName(bookName)
        conTexFilepath = _upan.Paths.TexFiles.Content.getAbs(bookPath, subsectionFull)
        line = cls.__getIdxLine(imIdx, conTexFilepath)

        extraLines = fsf.Data.Sec.imageTOCFileMoveLinesNumber(subsection)
        
        if extraLines == _u.Token.NotDef.str_t:
            extraLines = fsf.Data.Book.imageTOCFileMoveLinesNumber

        line = str(int(line) + int(extraLines))

        return line
    
    def __getIdxLine(imIdx, filepath):
        imMarker = dc.Links.Local.getIdxLineMarkerLine(imIdx)
        line, _ = _u.findPositionsOfMarkerInFile(filepath, imMarker)
        
        return line[0]