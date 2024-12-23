import data.constants as dc
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import _utils.logging as log
import settings.facade as sf
import file_system.file_system_facade as fsf

class TexFileProcess:
    
    @classmethod
    def getConLine(cls, bookName, subsection, imIdx):
        conTexFilepath = _upan.Paths.TexFiles.Content.getAbs(bookName, subsection, imIdx)
        line = cls.__getIdxLine(imIdx, conTexFilepath)

        extraLines = fsf.Data.Sec.imageContentFileMoveLinesNumber(subsection)
        
        if extraLines == _u.Token.NotDef.str_t:
            extraLines = fsf.Data.Book.imageContentFileMoveLinesNumber

        line = str(int(line) + int(extraLines))
        return line
    
    def __getIdxLine(imIdx, filepath):
        imMarker = dc.Links.Local.getIdxLineMarkerLine(imIdx)
        line, _ = _u.findPositionsOfMarkerInFile(filepath, imMarker)
        
        return line[0]