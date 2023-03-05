import _utils._utils_main as _u

import file_system.origmaterial_fs as omfs
import file_system.section_fs as sfs
import file_system.toc_fs as tocfs
import file_system.book_fs as bfs
import file_system._utils as fsu
import file_system.links as l
import file_system.file_system_manager as fsm

'''
Facade for Filesystem
'''

class Data:
    pass

class Wr:
    class FileSystemManager(fsm.FileSystemManager):
        pass
    
    class BookInfoStructure(bfs.BookInfoStructure):
        pass

    class SectionInfoStructure(sfs.SectionInfoStructure):
        pass
    
    class SectionCurrent(sfs.SectionCurrent):
        pass

    class TOCStructure(tocfs.TOCStructure):
        pass

    class OriginalMaterialStructure(omfs.OriginalMaterialStructure):
        pass


    class Links:
        class LinkDict(l.LinkDict):
            pass

        class ImIDX(l.ImIDX):
            pass

        class ImLink(l.ImLink):
            pass

    class Utils(fsu.Utils):
        pass


class PropIDs:
    class Sec(sfs.SectionInfoStructure.PubProp):
        pass

    class Book(bfs.BookInfoStructure.PubProp):
        pass

    class TOC(tocfs.TOCStructure.PubPro):
        pass