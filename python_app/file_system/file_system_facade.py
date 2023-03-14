import sys

import _utils._utils_main as _u
import _utils.logging as log

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

class ClassGetProperty(type):
    def __getattribute__(self, __name):
        if "__" in __name:
            return object.__getattribute__(self, __name)

        propertyName = super().__getattribute__(__name)

        module = self.__getbasemodule()

        if "sec" in str(self.__base__).lower():
            def getAttributeForSection(subsection, newValue = None):
                if newValue == None:
                    return module.readProperty(subsection, propertyName)
                else:
                    return module.updateProperty(subsection, 
                                               propertyName, 
                                               newValue)

            return getAttributeForSection

        return module.readProperty(propertyName)
    
    def __setattr__(self, __name: str, __value):
        propertyName = super().__getattribute__(__name)

        module = self.__getbasemodule()
        module.updateProperty(propertyName, __value)
    
    def __getbasemodule(self):
        baseName = str(self.__base__)
        baseName = baseName.split("'")[-2] # get rid of prefix and postfix
        className = baseName.split(".")[-2]
        moduleName = ".".join(baseName.split(".")[:-2])

        return getattr(sys.modules[moduleName], className)


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


class Data:
    class Book(bfs.BookInfoStructure.PubProp,
               metaclass = ClassGetProperty):
        pass
    
    class TOC(tocfs.TOCStructure.PubPro,
              metaclass = ClassGetProperty):
        pass
    
    class Sec(sfs.SectionInfoStructure.PubProp,
              metaclass = ClassGetProperty):
        pass
