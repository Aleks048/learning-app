import os

import _utils._utils_main as _u
import _utils.logging as log
import file_system.section_fs as sfs
import file_system.book_fs as bfs

class Paths:
    
    class Section:
        sectionFolderName = "subsections"
        
        @classmethod
        def getAbs_curr(cls):
            currBookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
            section = sfs.SectionCurrent.getSectionNameWprefix()
            return cls.getAbs(currBookPath, section)

        @classmethod
        def getRel_curr(cls):
            currSec = sfs.SectionCurrent.getSectionNameWprefix()
            return cls.getRel(currSec)

        @classmethod
        def getAbs(cls, bookPath, section):
            relFilepath = cls.getRel(section)
            return os.path.join(bookPath, relFilepath)

        @classmethod
        def getRel(cls, sec):
            if sec == _u.Token.NotDef.str_t:              
                return ""

            sectionsPathSeparator = \
                bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator_ID)

            pathList = sec.split(sectionsPathSeparator)
            
            for i in range(len(pathList) - 1, 0, -1):
                pathList[i] = ".".join(pathList[:i + 1])
            sectionFullPath = pathList
            sectionFullPath = os.path.join(cls.sectionFolderName, *sectionFullPath)
            return sectionFullPath

    class Screenshot:
        @classmethod
        def getAbs_curr(cls):
            currSubsection = sfs.SectionCurrent.getSectionNameWprefix()
            currBookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
            return  os.path.join(Paths.Section.getAbs(currBookPath, currSubsection), 
                                sfs.SectionCurrent.getSectionNameWprefix() + "_images")

        @classmethod
        def getRel_curr(cls):
            currSection = sfs.SectionCurrent.readCurrSection()
            return cls.getRel(currSection)

        @classmethod
        def getRel(cls, secNameWPrefix):
            if secNameWPrefix == _u.Token.NotDef.str_t:
                return "Screenshot location not defined yet."
            else:
                return  os.path.join(Paths.Section.getRel(secNameWPrefix),
                                    secNameWPrefix + "_images")

        @classmethod
        def getAbs(cls, bookPath,  secNameWPrefix):
            return  os.path.join(Paths.Section.getAbs(bookPath, secNameWPrefix), 
                                secNameWPrefix + "_images")
    
    class TexFiles:
        class Output:
            @classmethod
            def getAbs_curr(cls):
                currSubsection = sfs.SectionCurrent.getSectionNameWprefix()
                currBookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
                return cls.getAbs(currBookPath, currSubsection)

            def getAbs(bookPath, secName):
                return os.path.join(Paths.Section.getAbs(bookPath, secName), "_out")
            
            class PDF:
                def getAbs_curr(cls):
                    currSubsection = sfs.SectionCurrent.getSectionNameWprefix()
                    currBookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
                    return cls.getAbs(currBookPath, currSubsection)

                def getAbs(bookPath, secName):
                    return os.path.join(Paths.TexFiles.Output.getAbs(bookPath, secName), secName + "_main.pdf")


        def getSectionFromPath_Whole_WPrefix(filepath):
            # we get it from the parent folder name
            return filepath.split("/")[-2]
        
        def getBooknameFromPath(filepath):
            bookPaths = _u.Settings.readProperty(_u.Settings.PubProp.booksPaths_ID)
            for n,p in bookPaths.items():
                if p in filepath:
                    return n

        class Content:
            @classmethod
            def getAbs_curr(cls):
                currSubsection = sfs.SectionCurrent.getSectionNameWprefix()
                currBookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
                return cls.getAbs(currBookPath, currSubsection)

            def getAbs(bookPath, secName):
                return os.path.join(Paths.Section.getAbs(bookPath, secName), 
                                    secName + "_con.tex")
        
        class TOC:
            @classmethod
            def getAbs_curr(cls):
                currSubsection = sfs.SectionCurrent.getSectionNameWprefix()
                currBookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
                return cls.getAbs(currBookPath, currSubsection)

            def getAbs(bookPath, secName):
                return os.path.join(Paths.Section.getAbs(bookPath, secName), 
                                    secName + "_toc.tex")
        
        class Main:  
            @classmethod   
            def getAbs_curr(cls):
                currSubsection = sfs.SectionCurrent.getSectionNameWprefix()
                currBookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
                return cls.getAbs(currBookPath, currSubsection)
            
            def getAbs(bookPath, secName):
                return os.path.join(Paths.Section.getAbs(bookPath, secName), 
                                    secName + "_main.tex")

    class PDF:
        @classmethod
        def getAbs_curr(cls):
            currSubsection = sfs.SectionCurrent.getSectionNameWprefix()
            currBookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
            return cls.getAbs(currBookPath, currSubsection)

        def getAbs(bookPath, secNameWprefix):
            sectionDirPath = Paths.Section.getAbs(bookPath, secNameWprefix)
            return os.path.join(sectionDirPath, secNameWprefix + "_main.pdf")