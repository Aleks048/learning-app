import os
import shutil

import file_system.book_fs as bfs
import file_system.section_fs as sfs
import _utils._utils_main as _u
import _utils.logging as log
import outside_calls.outside_calls_facade as ocf

import settings.facade as sf

class TOCStructure:
    '''
    Keeps the toc for the sections and links to them.
    '''

    class PubPro:
        TEXT_MARKER = "[SECTION_TEXT]"
        START_MARKER = "[SECTION_START]" 
        FINISH_MARKER = "[SECTION_FINISH]"
        NAME_MARKER = "[SECTION_NAME]"
        CONTENT_MARKER = "[CONTENT_MARKER]"
        
        text = "TOC_text"
        start = "TOC_sectionStart"
        finish = "TOC_sectionFinish"
        
        propertyToMarker = {
            text: TEXT_MARKER,
            start: START_MARKER,
            finish: FINISH_MARKER
        }
 
        def getPropertyFormPath(path, propertyName):
            separator = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator)
            sectionPrefix = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix)
            return sectionPrefix + "_" + path.replace(separator, "_") + propertyName

    @classmethod
    def createStructure(cls):
        os.system("mkdir -p " + cls._getTOCDirPath())
        
    @classmethod
    def addSection(cls, sectionPath):
        sectionPathSeparator = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator)

        sectionPathList = sectionPath.split(sectionPathSeparator)
        
        for i,sectionName in enumerate(sectionPathList):
            sectionsList = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections)
            sectionData = bfs.BookInfoStructure.readProperty(sectionName)
            if sectionData == None:
                continue

            separator = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator)
            topSectionName = sectionName.split(separator)[0]
            
            sectionsTOCLines = [""]
            
            if i == 0:
                pathToTemplates = os.getenv("BOOKS_TEMPLATES_PATH")
                _waitDummy = shutil.copy(pathToTemplates + "/TOC_template.tex",
                                        cls._getTOCFilePath(topSectionName))
            
            cls._getTOCLines(sectionData, sectionsTOCLines, 0)

            
            _u.replaceMarkerInFile(cls._getTOCFilePath(topSectionName), 
                                cls.PubPro.NAME_MARKER, 
                                topSectionName)
            _u.replaceMarkerInFile(cls._getTOCFilePath(topSectionName), 
                                cls.PubPro.CONTENT_MARKER, 
                                sectionsTOCLines[0])

    
    def _getTOCSectionNameFromSectionPath(sectionPath):
        prefix = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix)
        separator = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator)
        return prefix + "_" + sectionPath.split(separator)[0]

    @classmethod
    def updateTOCfiles(cls, sectionPath, propertyName, newValue):
        oldPropertyValue = sfs.SectionInfoStructure.readProperty(sectionPath, propertyName)

        # update the TOC files
        sectionName = cls._getTOCSectionNameFromSectionPath(sectionPath)
        if oldPropertyValue != "":
            _u.replaceMarkerInFile(cls._getTOCFilePath(sectionName), 
                                "[" + oldPropertyValue + "]", 
                                "[" + newValue + "]", 
                                "[" + sectionPath + "]")
        else:
            marker = cls.PubPro.propertyToMarker[propertyName]
            _u.replaceMarkerInFile(cls._getTOCFilePath(sectionName), 
                                "[" + marker  + "]", 
                                "[" + newValue + "]", 
                                "[" + sectionPath + "]")

    @classmethod
    def _getTOCLines(cls, sectionsData, outLines, level):
        INTEMEDIATE_LINE = cls.PubPro.NAME_MARKER + ":\\\\\n"
        BOTTOM_LINE = "\TOCline{[" + cls.PubPro.TEXT_MARKER + \
            "] [" + cls.PubPro.NAME_MARKER + "]// [" + \
            cls.PubPro.START_MARKER + \
            "] - [" + cls.PubPro.FINISH_MARKER + "]}{[" + \
            cls.PubPro.START_MARKER + "]}" + \
            "\\\\\n"

        DEFAULT_PREFIX_SPACES = " " * 4 + level * " " * 4
    
        for name, section in sectionsData["sections"].items():
            if type(section) == dict:
                if section["sections"] == {}:
                    # add line
                    lineToAdd = DEFAULT_PREFIX_SPACES \
                                + BOTTOM_LINE.replace(cls.PubPro.NAME_MARKER, name)
                    outLines[0] = outLines[0] + lineToAdd
                else:
                    lineToAdd = DEFAULT_PREFIX_SPACES \
                                + INTEMEDIATE_LINE.replace(cls.PubPro.NAME_MARKER, name)
                    outLines[0] = outLines[0] + lineToAdd
                    cls._getTOCLines(section, outLines, level +1)
    
    def _getTOCDirPath():
        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        return os.path.join(bookPath, bfs.BookInfoStructure.TOCbaseRelPath)

    @classmethod
    def _getTOCFilePath(cls, topSectionName):
        secprefix = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix)
        tocFolderPath = cls._getTOCDirPath()
        if (os.path.isdir(tocFolderPath)):
            return os.path.join(tocFolderPath, "TOC_" + secprefix + "_" + topSectionName + ".tex")
        else:
            log.autolog("The TOC dir is not present. Will create: {0}".format(tocFolderPath))
            ocf.Wr.FsAppCalls.createDir(tocFolderPath)
            return os.path.join(tocFolderPath, "TOC_" + secprefix + "_" + topSectionName + ".tex")
