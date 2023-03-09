import os

import _utils._utils_main as _u
import _utils.logging as log

import file_system.file_system_facade as fsf
import settings.facade as sf


class Paths:
    class OriginalMaterial:
        class MainBook:
            def getAbs(bookPath):
                originalMaterialbasePath = Paths.OriginalMaterial.getAbs(bookPath)
                relMainBookPath = fsf.Wr.BookInfoStructure.readProperty(fsf.PropIDs.Book.originalMaterialRelPath_ID)
                log.autolog(originalMaterialbasePath)
                log.autolog(relMainBookPath)
                return os.path.join(originalMaterialbasePath, relMainBookPath)

            @classmethod
            def getCurrAbs(cls):
               bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
               return cls.getAbs(bookPath)
                
        
        def getAbs(bookPath):
            return os.path.join(bookPath, fsf.Wr.OriginalMaterialStructure.originalMaterialBaseRelPath)

        @classmethod        
        def getCurrAbs(cls):
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            return cls.getAbs(bookPath)
    
    class Section:
        sectionFolderName = "subsections"

        @classmethod
        def getAbs(cls, bookPath, section):
            relFilepath = cls.getRel(section)
            return os.path.join(bookPath, relFilepath)

        @classmethod
        def getRel(cls, sec):
            if sec == _u.Token.NotDef.str_t:              
                return ""

            sectionsPathSeparator = fsf.Wr.BookInfoStructure.readProperty(fsf.PropIDs.Book.sections_path_separator_ID)

            pathList = sec.split(sectionsPathSeparator)
            
            for i in range(len(pathList) - 1, 0, -1):
                pathList[i] = ".".join(pathList[:i + 1])
            sectionFullPath = pathList
            sectionFullPath = os.path.join(cls.sectionFolderName, *sectionFullPath)
            return sectionFullPath

    class Screenshot:
        def getRel(secNameWPrefix):
            if secNameWPrefix == _u.Token.NotDef.str_t:
                return "Screenshot location not defined yet."
            else:
                return  os.path.join(Paths.Section.getRel(secNameWPrefix),
                                    secNameWPrefix + "_images")

        def getAbs(bookPath,  secNameWPrefix):
            return  os.path.join(Paths.Section.getAbs(bookPath, secNameWPrefix), 
                                secNameWPrefix + "_images")
    
    class TexFiles:
        class Output:
            def getAbs(bookPath, secName):
                return os.path.join(Paths.Section.getAbs(bookPath, secName), "_out")
            
            class PDF:
                def getAbs(bookPath, secName):
                    return os.path.join(Paths.TexFiles.Output.getAbs(bookPath, secName), secName + "_main.pdf")


        class Content:
            def getAbs(bookPath, secName):
                return os.path.join(Paths.Section.getAbs(bookPath, secName), 
                                    secName + "_con.tex")
        
        class TOC:
            def getAbs(bookPath, secName):
                return os.path.join(Paths.Section.getAbs(bookPath, secName), 
                                    secName + "_toc.tex")
        
        class Main:
            def getAbs(bookPath, secName):
                return os.path.join(Paths.Section.getAbs(bookPath, secName), 
                                    secName + "_main.tex")

    class PDF:
        def getAbs(bookPath, secNameWprefix):
            sectionDirPath = Paths.Section.getAbs(bookPath, secNameWprefix)
            return os.path.join(sectionDirPath, secNameWprefix + "_main.pdf")

class Names:
    pass

class Current:
    class Paths:
        class Section:
            def abs():
                currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                section = Current.Names.Section.name_wPrefix()
                return Paths.Section.getAbs(currBookPath, section)

            def rel():
                currSec = Current.Names.Section.name_wPrefix()
                return Paths.Section.getRel(currSec)
        
        
        class Screenshot:
            def abs():
                currSubsection = Current.Names.Section.name_wPrefix()
                currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                return  Paths.Screenshot.getAbs(currBookPath, currSubsection)

            def rel():
                currSection = Current.Names.Section.name()
                return Paths.Screenshot.getRel(currSection)
            
            @classmethod
            def rel_formatted(cls):
                '''
                Used in the main layout Label
                '''
                relPath = cls.rel()

                currSecName = fsf.Wr.SectionCurrent.getSectionNameNoPrefix()
                name = fsf.Wr.SectionInfoStructure.readProperty(currSecName, fsf.PropIDs.Sec.name_ID)
                startPage = fsf.Wr.SectionInfoStructure.readProperty(currSecName, fsf.PropIDs.Sec.startPage_ID)
                currSecName = fsf.Wr.SectionCurrent.getSectionNameNoPrefix()

                text = "Sec path: '{0}'. Name: '{1}'. St page: '{2}'.".format(currSecName, name, startPage)

                text += " Im dir:  '{0}'".format(relPath) if relPath != "" else "No direction yet."
                return text
        

        class TexFiles:
            class Output:
                def abs():
                    currSubsection = Current.Names.Section.name_wPrefix()
                    currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                    return Paths.TexFiles.Output.getAbs(currBookPath, currSubsection)
            
                class PDF:
                    def abs():
                        currSubsection = Current.Names.Section.name_wPrefix()
                        currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                        return Paths.TexFiles.Output.PDF.getAbs(currBookPath, currSubsection)


            class Content:
                def abs():
                    currSubsection =Current.Names.Section.name_wPrefix()
                    currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                    return Paths.TexFiles.Content.getAbs(currBookPath, currSubsection)
            


            class TOC:
                def abs():
                    currSubsection = Current.Names.Section.name_wPrefix()
                    currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                    return Paths.TexFiles.TOC.getAbs(currBookPath, currSubsection)
            
            
            class Main: 
                def abs():
                    currSubsection =Current.Names.Section.name_wPrefix()
                    currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                    return Paths.TexFiles.Main.getAbs(currBookPath, currSubsection)


        class PDF:
            def abs():
                currSubsection = Current.Names.Section.name_wPrefix()
                currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                return Paths.PDF.getAbs(currBookPath, currSubsection) 


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
            @classmethod
            def name_wPrefix(cls, filepath = _u.Token.NotDef.str_t):
                sectionPrefix = fsf.Wr.BookInfoStructure.readProperty(\
                                        fsf.PropIDs.Book.sections_prefix_ID)
                currSection = cls.name()
                if currSection == _u.Token.NotDef.str_t:
                    return _u.Token.NotDef.str_t
                return sectionPrefix + "_" + currSection

            def name():
                return fsf.Wr.BookInfoStructure.readProperty(fsf.PropIDs.Book.currSection_ID)