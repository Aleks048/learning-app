import os
from functools import wraps

import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import _utils.logging as log

import file_system.file_system_facade as fsf
import settings.facade as sf


def bookNameArg_dec(func):
    '''
    allows to provide bookname or bookpath to get the path
    '''
    @wraps(func)
    def wrapper(bookId = _u.Token.NotDef.str_t, subSection = _u.Token.NotDef.str_t):
        if bookId == _u.Token.NotDef.str_t:
            bookId = sf.Wr.Manager.Book.getCurrBookFolderPath()
        
        if subSection == _u.Token.NotDef.str_t:
            subSection = fsf.Data.Book.currSection
        
        if bookId in sf.Wr.Manager.Book.getListOfBooksPaths():
            return func(bookId, subSection)
        else:
            bookPath = sf.Wr.Manager.Book.getPathFromName(bookId)
            return func(bookPath, subSection)
    
    return wrapper
class Paths:
    class OriginalMaterial:
        class MainBook:
            @bookNameArg_dec
            def getAbs(bookPath, *args):
                currMaterialName = fsf.Data.Book.currOrigMatName
                return fsf.omfs.OriginalMaterialStructure.getMaterialPath(currMaterialName)      
        
        @bookNameArg_dec
        def getAbs(bookPath, *args):
            return os.path.join(bookPath, fsf.Wr.OriginalMaterialStructure.originalMaterialBaseRelPath)
    
    class Section:
        sectionFolderName = "subsections"

        @bookNameArg_dec
        def getAbs(bookPath, section, *args):
            relFilepath = Paths.Section.getRel(bookPath, section)
            return os.path.join(bookPath, relFilepath)
        
        @bookNameArg_dec
        def getRel(_, subsection, *args):
            if subsection == _u.Token.NotDef.str_t:              
                return ""

            sectionsPathSeparator = fsf.Data.Book.sections_path_separator

            pathList = subsection.split(sectionsPathSeparator)
            pathList[0] = _upan.Names.addSectionPrefixToName(pathList[0])

            for i in range(len(pathList) - 1, 0, -1):
                pathList[i] = ".".join(pathList[:i + 1])
            
            sectionFullPath = pathList
            sectionFullPath = os.path.join(Paths.Section.sectionFolderName, *sectionFullPath)
            return sectionFullPath

    class Screenshot:
        @bookNameArg_dec
        def getRel(bookPath, subsection):
            secNameWPrefix = _upan.Names.addSectionPrefixToName(subsection)
            if secNameWPrefix == _u.Token.NotDef.str_t:
                return "Screenshot location not defined yet."
            else:
                return  os.path.join(Paths.Section.getRel(bookPath, subsection),
                                    secNameWPrefix + "_images")

        @bookNameArg_dec
        def getAbs(bookPath,  subsection):
            secNameWPrefix = _upan.Names.addSectionPrefixToName(subsection)
            return  os.path.join(Paths.Section.getAbs(bookPath, subsection), 
                                secNameWPrefix + "_images")
        
        @bookNameArg_dec
        def getRel_formatted(*args):
            '''
            Used in the main layout Label
            '''

            currSecName = fsf.Data.Book.currSection
            name = fsf.Data.TOC.text(currSecName)
            startPage = fsf.Data.TOC.start(currSecName)
            endPage = fsf.Data.TOC.finish(currSecName)

            text = "Sec path: '{0}'. Name: '{1}'. Start p: '{2}'. End p: '{3}'.".format(currSecName, 
                                                                                        name, 
                                                                                        startPage,
                                                                                        endPage)

            return text
    
    class TexFiles:
        class Output:
            @bookNameArg_dec
            def getAbs(bookPath, subsection):
                return os.path.join(Paths.Section.getAbs(bookPath, subsection), "_out")
            
            class PDF:
                @bookNameArg_dec
                def getAbs(bookPath, subsection):
                    secNameWPrefix = _upan.Names.addSectionPrefixToName(subsection)
                    return os.path.join(Paths.TexFiles.Output.getAbs(bookPath, subsection), secNameWPrefix + "_main.pdf")


        class Content:
            @bookNameArg_dec
            def getAbs(bookPath, subsection):
                secNameWPrefix = _upan.Names.addSectionPrefixToName(subsection)
                return os.path.join(Paths.Section.getAbs(bookPath, subsection), 
                                    secNameWPrefix + "_con.tex")
        
        class TOC:
            @bookNameArg_dec
            def getAbs(bookPath, subsection):
                secNameWPrefix = _upan.Names.addSectionPrefixToName(subsection)
                return os.path.join(Paths.Section.getAbs(bookPath, subsection), 
                                    secNameWPrefix + "_toc.tex")
        
        class Main:
            @bookNameArg_dec
            def getAbs(bookPath, subsection):
                secNameWPrefix = _upan.Names.addSectionPrefixToName(subsection)
                return os.path.join(Paths.Section.getAbs(bookPath, subsection), 
                                    secNameWPrefix + "_main.tex")

    class PDF:
        @bookNameArg_dec
        def getAbs(bookPath, subsection):
            secNameWPrefix = _upan.Names.addSectionPrefixToName(subsection)
            sectionDirPath = Paths.Section.getAbs(bookPath, subsection)
            return os.path.join(sectionDirPath, secNameWPrefix + "_main.pdf")

class Names:
    def addSectionPrefixToName(subsection):
        return fsf.Data.Book.sections_prefix + "_" + subsection
    
    def removeSectionPrefixFromName(subsection:str):
        return subsection.replace(fsf.Data.Book.sections_prefix + "_", "")
    
    def getImageName(imIdx, subsection):
        return imIdx + "__" + subsection
    
    @classmethod
    def getExtraImageName(cls, mainImIdx, subsection, extraImName):
        return cls.getImageName(mainImIdx, subsection) + "__e__{0}".format(extraImName)

class Current:
    class Names:
        class Book:            
            def name(filepath = _u.Token.NotDef.str_t):
                if filepath != _u.Token.NotDef.str_t:
                    bookPaths = sf.Wr.Manager.Book.getListOfBooksPaths()
                    for n,p in bookPaths.items():
                        if p in filepath:
                            return n
                else:
                    pass
        
        class Section:
            class Screenshot:
                def name_wPrefix():
                    return Current.Names.Section.name_wPrefix() + "_images"

            @classmethod
            def name_wPrefix(cls, filepath = _u.Token.NotDef.str_t):
                sectionPrefix = fsf.Data.Book.sections_prefix

                currSection = cls.name()
                if currSection == _u.Token.NotDef.str_t:
                    return _u.Token.NotDef.str_t
                return sectionPrefix + "_" + currSection

            def name():
                return fsf.Data.Book.currSection