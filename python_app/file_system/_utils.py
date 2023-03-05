import os

import _utils._utils_main as _u
import _utils.logging as log
import file_system.book_fs as bfs
import file_system.section_fs as sfs
import file_system.origmaterial_fs as omfs
import _utils.pathsAndNames as p

import settings.facade as sf


class Utils:
    def getSectionNameWPrefix(fullSecName):
        sectionPrefix = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix_ID)
        
        return sectionPrefix + "_" + fullSecName
    def joinTopAndSubsection(topSection, subsection):
        separator = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator_ID)
        
        return topSection + separator + subsection

    def getPDFPageFromPosIDX(posIDX):
        # at the moment posIDX = sec page
        # but in the future that might not be the case
        return posIDX
    
    def stripFullName_Wprefix(fullName):
        # 
        # remove prefix and split into subsection and top section
        #

        sectionPrefix = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix_ID)
        
        # remove prefix
        fullName = fullName.replace(sectionPrefix + "_", "")

        separator = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator_ID)
        
        fullName = fullName.split(separator)
        topSection = fullName[0]
        subsection = separator.join(fullName[1:])
        return topSection, subsection


def _getSectionFilepath(sectionPath):
    sectionPrefix = \
        bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix_ID)
    sectionsPathSeparator = \
        bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator_ID)

    pathList = sectionPath.split(sectionsPathSeparator)
    pathList[0] = sectionPrefix + "_" + pathList[0]
    
    for i in range(len(pathList) - 1, 0, -1):
        pathList[i] = ".".join(pathList[:i + 1])
    
    sectionFullPath = pathList
    sectionFullPath = os.path.join(*sectionFullPath)
    pathToSection = _getPathToSectionsFolder()
    pathToSection = os.path.join(p.Paths.Section.sectionFolderName, pathToSection, sectionFullPath)
    return pathToSection


def _getPathToSectionsFolder():
    pathToSectionFolder = sf.Wr.Manager.Book.getCurrBookFolderPath()
    pathToSectionFolder = os.path.join(pathToSectionFolder, 
                                    bfs.BookInfoStructure.sectionsInfoBaseRelPath)
    return pathToSectionFolder