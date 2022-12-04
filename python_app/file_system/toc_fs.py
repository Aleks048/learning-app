import os
import shutil

import file_system.book_fs as bfs
import file_system.section_fs as sfs
import _utils._utils_main as _u

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
        
        text_ID = "TOC_text"
        start_ID = "TOC_sectionStart"
        finish_ID = "TOC_sectionFinish"
        
        propertyToMarker = {
            text_ID: TEXT_MARKER,
            start_ID: START_MARKER,
            finish_ID: FINISH_MARKER
        }
 
        def getPropertyFormPath(path, propertyName):
            separator = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator_ID)
            sectionPrefix = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix_ID)
            return sectionPrefix + "_" + path.replace(separator, "_") + propertyName

    @classmethod
    def createStructure(cls):
        os.system("mkdir -p " + cls._getTOCDirPath())
        
    @classmethod
    def addSection(cls, sectionPath):
        sectionPathSeparator = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator_ID)

        sectionPathList = sectionPath.split(sectionPathSeparator)
        
        for i,sectionName in enumerate(sectionPathList):
            sectionsList = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_ID)
            sectionData = bfs.BookInfoStructure.readProperty(sectionName)
            if sectionData == None:
                continue

            separator = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator_ID)
            topSectionName = sectionName.split(separator)[0]
            
            sectionsTOCLines = [""]
            
            if i == 0:
                pathToTemplates = os.getenv("BOOKS_TEMPLATES_PATH")
                _waitDummy = shutil.copy(pathToTemplates + "/TOC_template.tex",
                                        + cls._getTOCFilePath(topSectionName))
            
            cls._getTOCLines(sectionData, sectionsTOCLines, 0)

            
            _u.replaceMarkerInFile(cls._getTOCFilePath(topSectionName), 
                                cls.PubPro.NAME_MARKER, 
                                topSectionName)
            _u.replaceMarkerInFile(cls._getTOCFilePath(topSectionName), 
                                cls.PubPro.CONTENT_MARKER, 
                                sectionsTOCLines[0])

    
    def _getTOCSectionNameFromSectionPath(sectionPath):
        prefix = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix_ID)
        separator = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator_ID)
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
        bookPath = _u.Settings.readProperty(_u.Settings.PubProp.currBookPath_ID)
        return bookPath + bfs.BookInfoStructure.TOCbaseRelPath

    @classmethod
    def _getTOCFilePath(cls, topSectionName):
        secprefix = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix_ID)
        tocFolderPath = cls._getTOCDirPath()
        if (os.path.isdir(tocFolderPath)):
            return os.path.join(tocFolderPath, "TOC_" + secprefix + "_" + topSectionName + ".tex")
        else:
            print("_getTOCFilePath - " + "the TOC filepath is not present.")
            print("Will create: " + tocFolderPath)
            _waitDummy = os.system("mkdir " + tocFolderPath)
            return os.path.join(tocFolderPath, "TOC_" + secprefix + "_" + topSectionName + ".tex")
