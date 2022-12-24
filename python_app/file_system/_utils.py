import os

import _utils._utils_main as _u
import _utils.logging as log
import file_system.book_fs as bfs
import file_system.section_fs as sfs
import file_system.origmaterial_fs as omfs
import file_system.paths as p


class Utils:
    def getSectionNameWPrefix(secName):
        sectionPrefix = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix_ID)
        
        return sectionPrefix + "_" + secName


@classmethod
def getWholeBookPath(cls):
    path = os.path.join(_u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID),
                    omfs.OriginalMaterialStructure.originalMaterialBaseRelPath,
                    _u.Settings.PubProp.wholeBook_ID + ".pdf")
    print(path)
    return path



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
    pathToSectionFolder = \
        _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
    pathToSectionFolder = os.path.join(pathToSectionFolder, 
                                    bfs.BookInfoStructure.sectionsInfoBaseRelPath)
    return pathToSectionFolder