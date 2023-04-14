import os

import _utils._utils_main as _u
import _utils.logging as log
import file_system.book_fs as bfs
import file_system.section_fs as sfs
import file_system.origmaterial_fs as omfs
import _utils.pathsAndNames as _upan

import settings.facade as sf


class Utils:
    def getSectionNameWPrefix(fullSecName):
        sectionPrefix = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix)
        
        return sectionPrefix + "_" + fullSecName
    def joinTopAndSubsection(topSection, subsection):
        separator = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator)
        
        return topSection + separator + subsection

    def getPDFPageFromPosIDX(posIDX):
        page = str((int(posIDX) % 5) + 1)
        return page
    
    def getTopSection(fullName):
        # 
        # remove prefix and split into subsection and top section
        #

        sectionPrefix = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix)
        
        # remove prefix
        fullName = fullName.replace(sectionPrefix + "_", "")

        separator = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator)
        
        fullName = fullName.split(separator)
        topSection = fullName[0]
        return topSection