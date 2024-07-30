import os
import math
from functools import wraps

import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import _utils.logging as log
import data.constants as dc

import file_system.file_system_facade as fsf
import settings.facade as sf

import outside_calls.outside_calls_facade as ocf

def bookNameArg_dec(func):
    '''
    allows to provide bookname or bookpath to get the path
    '''
    @wraps(func)
    def wrapper(bookId = _u.Token.NotDef.str_t,
                subsection = _u.Token.NotDef.str_t,
                idx = _u.Token.NotDef.str_t,
                *args):
        if bookId == _u.Token.NotDef.str_t:
            bookId = sf.Wr.Manager.Book.getCurrBookFolderPath()
        
        if subsection == _u.Token.NotDef.str_t:
            subsection = fsf.Data.Book.currSection
        
        if bookId in sf.Wr.Manager.Book.getListOfBooksPaths():
            return func(bookId, subsection, idx, *args)
        else:
            bookPath = sf.Wr.Manager.Book.getPathFromName(bookId)
            return func(bookPath, subsection, idx, *args)
    
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
    
    class Book:
        class Code:
            templateFolderName = "code_templates"

            @bookNameArg_dec
            def getSubsectionTemplatePathAbs(bookPath, *args):
                return os.path.join(bookPath, 
                                    fsf.Wr.BookInfoStructure.bookInfoFoldefRelPath,
                                    Paths.Book.Code.templateFolderName,
                                    "subsection",
                                    Names.codeProjectBaseName())
            @bookNameArg_dec
            def getEntryTemplatePathAbs(bookPath, *args):
                return os.path.join(bookPath, 
                                    fsf.Wr.BookInfoStructure.bookInfoFoldefRelPath,
                                    Paths.Book.Code.templateFolderName,
                                    "entry",
                                    Names.codeProjectBaseName())
            
            @bookNameArg_dec
            def getAbs(bookPath, *args):
                return os.path.join(bookPath, 
                                    fsf.Wr.BookInfoStructure.bookInfoFoldefRelPath,
                                    Names.codeProjectBaseName())

    class Section:
        sectionFolderName = "subsections"

        @bookNameArg_dec
        def getBaseAbs(bookPath, *args):
            return os.path.join(bookPath, Paths.Section.sectionFolderName)
        
        @bookNameArg_dec
        def getAbs(bookPath, section = _u.Token.NotDef.str_t, *args):
            relFilepath = Paths.Section.getRel(bookPath, section)
            return os.path.join(bookPath, relFilepath)

        @bookNameArg_dec
        def getCodeRootAbs(bookPath, section = _u.Token.NotDef.str_t, *args):
            relFilepath = Paths.Section.getRel(bookPath, section)
            return os.path.join(bookPath, relFilepath, Names.codeProjectBaseName())

        @bookNameArg_dec
        def getRel(_, subsection, *args):
            if subsection == _u.Token.NotDef.str_t:           
                return Paths.Section.sectionFolderName

            sectionsPathSeparator = fsf.Data.Book.sections_path_separator

            pathList = subsection.split(sectionsPathSeparator)

            for i in range(len(pathList)):
                pathList[i] = _upan.Names.addSectionPrefixToName(pathList[i])

            sectionFullPath = pathList
            sectionFullPath = os.path.join(Paths.Section.sectionFolderName, *sectionFullPath)
            
            return sectionFullPath

        class JSON:
            @bookNameArg_dec
            def getAbs(bookPath, section, *args):
                sectionFilepath = Paths.Section.getAbs(bookPath, section)
                return os.path.join(sectionFilepath, "sectionInfo.json")

    class Entry:
        @bookNameArg_dec
        def getAbs(bookPath, section, imIdx, *args):
            sectionFilepath = Paths.Section.getAbs(bookPath, section)
            return os.path.join(sectionFilepath, str(imIdx))

        @bookNameArg_dec
        def getCodeProjAbs(bookPath, section, imIdx, *args):
            entrybasePath = Paths.Entry.getAbs(bookPath, section, imIdx)
            return os.path.join(entrybasePath, Names.codeProjectBaseName())

        class LineImage:
            @bookNameArg_dec
            def getAbs(bookPath, section, imIdx, *args):
                lineIdx = args[0]
                filename = Names.Entry.Line.name(imIdx, lineIdx)
                entryPath = Paths.Entry.getAbs(bookPath, section, imIdx)

                return os.path.join(entryPath, filename)

        class LineNoteImage:
            @bookNameArg_dec
            def getAbs(bookPath, section, imIdx, *args):
                lineIdx = args[0]
                filename = Names.Entry.LineNote.name(imIdx, lineIdx)
                entryPath = Paths.Entry.getAbs(bookPath, section, imIdx)

                return os.path.join(entryPath, filename)

        class NoteImage:
            @bookNameArg_dec
            def getAbs(bookPath, section, imIdx, *args):
                lineIdx = args[0]
                filename = Names.Entry.Note.name(imIdx, lineIdx)
                entryPath = Paths.Entry.getAbs(bookPath, section, imIdx)

                return os.path.join(entryPath, filename)

        class SolutionImage:
            @bookNameArg_dec
            def getAbs(bookPath, section, imIdx, *args):
                solIdx = args[0]
                filename = Names.Entry.Solution.name(solIdx)
                entryPath = Paths.Entry.getAbs(bookPath, section, imIdx)

                return os.path.join(entryPath, filename)

        class ExtraImage:
            @bookNameArg_dec
            def getAbs(bookPath, section, imIdx, *args):
                extraIdx = args[0]
                filename = Names.Entry.Extra.name(extraIdx)
                entryPath = Paths.Entry.getAbs(bookPath, section, imIdx)

                return os.path.join(entryPath, filename)

        class JSON:
            @bookNameArg_dec
            def getAbs(bookPath, section, imIdx, *args):
                entryPath = Paths.Entry.getAbs(bookPath, section, imIdx)
                return os.path.join(entryPath, "entryInfo.json")

    class Screenshot:
        @bookNameArg_dec
        def getRel(bookPath, subsection):
            return  os.path.join(Paths.Section.getRel(bookPath, subsection), "_images")

        @bookNameArg_dec
        def getAbs(bookPath,  subsection, *args):
            return  os.path.join(Paths.Section.getAbs(bookPath, subsection), "_images")
        
        @bookNameArg_dec
        def getRel_formatted(*args):
            '''
            Used in the main layout Label
            '''

            currSecName = fsf.Data.Book.currSection
            name = fsf.Data.Sec.text(currSecName)
            startPage = fsf.Data.Sec.start(currSecName)
            endPage = fsf.Data.Sec.finish(currSecName)

            text = "Sec path: '{0}'. Name: '{1}'. Start p: '{2}'. End p: '{3}'.".format(currSecName, 
                                                                                        name, 
                                                                                        startPage,
                                                                                        endPage)

            return text

        class Images:     
            @bookNameArg_dec
            def getMainEntryImageAbs(bookPath, subsection, imIdx, *args):
                screenshotFolder = Paths.Screenshot.getAbs(bookPath, subsection)
                mainImageName = Names.getImageName(str(imIdx))
                return os.path.join(screenshotFolder,  mainImageName + ".png")

            @bookNameArg_dec
            def getMainEntryTexImageAbs(bookPath, subsection, imIdx, *args):
                screenshotFolder = Paths.Screenshot.getAbs(bookPath, subsection)
                mainImageName = Names.getImageName("_" + str(imIdx))
                return os.path.join(screenshotFolder,  mainImageName + ".png")

            @bookNameArg_dec
            def getExtraEntryImageAbs(bookPath, subsection, imIdx, *args):
                extraImName = args[0]
                screenshotFolder = Paths.Screenshot.getAbs(bookPath, subsection)
                extraImFilename = Names.getExtraImageFilename(str(imIdx), subsection, extraImName)
                return os.path.join(screenshotFolder, extraImFilename + ".png")

            @bookNameArg_dec
            def getSubsectionEntryImageAbs(bookPath, subsection, *args):
                screenshotFolder = Paths.Screenshot.getAbs(bookPath, subsection)
                return os.path.join(screenshotFolder, "_sub.png")

            @bookNameArg_dec
            def getTopSectionEntryImageAbs(bookPath, topSection, *args):
                topSectionPath = Paths.Section.getAbs(sf.Wr.Manager.Book.getCurrBookName(), 
                                                topSection)
                return os.path.join(topSectionPath, "_top.png")

            @bookNameArg_dec
            def getGroupImageAbs(bookPath, subsection, filenameBase, *args):
                secreenshotPath = _upan.Paths.Screenshot.getAbs(sf.Wr.Manager.Book.getCurrBookName(), 
                                                subsection)
                filename = "_g_" + filenameBase + ".png"
                return os.path.join(secreenshotPath, filename)

            @bookNameArg_dec
            def getWebLinkImageAbs(bookPath, subsection, imIdx, ln, *args):
                linkName =  str(imIdx + "_" + ln).replace(".", "")
                linkName = linkName.replace(" ", "$")
                filename = "_" + linkName
                screenshotFolder = Paths.Screenshot.getAbs(bookPath, subsection)
                return os.path.join(screenshotFolder, f"{filename}.png")
                
  
    class TexFiles:
        def getEnding(subsection, idx):
            if idx == _u.Token.NotDef.str_t:
                idx = fsf.Wr.Links.ImIDX.get(subsection)
            
            return "_" + Names.getSubsectionFilesEnding(idx)
            
        class Output:
            @bookNameArg_dec
            def getAbs(bookPath, subsection, *args):
                return os.path.join(Paths.Section.getAbs(bookPath, subsection), "_out")
            
            class PDF:
                @bookNameArg_dec
                def getAbs(bookPath, subsection, idx, *args):
                    secNameWPrefix = _upan.Names.addSectionPrefixToName(subsection)
                    ending = Paths.TexFiles.getEnding(subsection, idx)
                    return os.path.join(Paths.TexFiles.Output.getAbs(bookPath, subsection), 
                                        secNameWPrefix + "_main" + ending + ".pdf")


        class Content:
            @bookNameArg_dec
            def getAbs(bookPath, subsection, idx, *args):
                secNameWPrefix = _upan.Names.addSectionPrefixToName(subsection)  
                ending = Paths.TexFiles.getEnding(subsection, idx)
                return os.path.join(Paths.Section.getAbs(bookPath, subsection), 
                                    secNameWPrefix + "_con" + ending + ".tex")
        
        class TOC:
            @bookNameArg_dec
            def getAbs(bookPath, subsection, idx, *args):
                secNameWPrefix = _upan.Names.addSectionPrefixToName(subsection)
                ending = Paths.TexFiles.getEnding(subsection, idx)
                return os.path.join(Paths.Section.getAbs(bookPath, subsection), 
                                    secNameWPrefix + "_toc" + ending + ".tex")
        
        class Main:
            @bookNameArg_dec
            def getAbs(bookPath, subsection, idx, *args):
                secNameWPrefix = _upan.Names.addSectionPrefixToName(subsection)
                ending = Paths.TexFiles.getEnding(subsection, idx)
                return os.path.join(Paths.Section.getAbs(bookPath, subsection), 
                                    secNameWPrefix + "_main" + ending + ".tex")

    class PDF:
        @bookNameArg_dec
        def getAbs(bookPath, subsection, idx, *args):
            secNameWPrefix = _upan.Names.addSectionPrefixToName(subsection)
            sectionDirPath = Paths.Section.getAbs(bookPath, subsection)
            ending = Paths.TexFiles.getEnding(subsection, idx)
            return os.path.join(sectionDirPath, secNameWPrefix + "_main" + ending + ".pdf")

class Names:
    def codeProjectBaseName():
        return "code"

    def codeLineMarkerBook(subsection, imIdx):
        return f"MARKER_BOOK_{subsection}_{imIdx}"
    
    def codeLineMarkerSubsection(subsection, imIdx):
        return f"MARKER_SUBSECTION_{subsection}_{imIdx}"

    def addSectionPrefixToName(subsection):
        return fsf.Data.Book.sections_prefix + "_" + subsection.split(".")[-1]

    def getImageName(imIdx):
        return imIdx
    
    @classmethod
    def getExtraImageFilename(cls, mainImIdx, subsection, extraImName):
        return cls.getImageName(mainImIdx) + "__e__{0}".format(extraImName)
    
    def getSubsectionFilesEnding(idx):
        return str(math.floor(int(idx) / 5))
    
    def getIdxFromSubsectionFilesname(filename):
        bookNum = filename.split("_")[-1]
        bookNum = bookNum.split(".")[0]
        return str(int(bookNum) * 5)
    

    class Entry:
        class Line:
            def name(imIdx, lineIdx):
                return f"_{lineIdx}.png"

        class LineNote:
            def name(imIdx, lineIdx):
                return f"_ln_{lineIdx}.png"

        class Note:
            def name(imIdx, lineIdx):
                return f"_n_{lineIdx}.png"

        class Solution:
            solutionImgToken = "_solution_"

            @classmethod
            def name(cls, solutionIdx):
                return f"{cls.solutionImgToken}{solutionIdx}.png"
        
        class Extra:
            extraImgToken = "_Extra_"

            @classmethod
            def name(cls, extraIdx):
                return f"{cls.extraImgToken}{extraIdx}.png"

        def getEntryNameID(subsection, idx):
            subSecID = _upan.Names.UI.getWidgetSubsecId(subsection)
            nameId:str = subSecID + "_" + str(idx)
            return nameId.replace(".", "")

    class Group:
        def formatGroupText(text:str):
            text = text.replace(".", "$")
            text = text.replace(" ", "_")
            return text

    class Subsection:
        def formatSectionText(text:str):
            text = text.replace(".", "$")
            text = text.replace(" ", "_")
            return text

        def getSubsectionPretty(subsection):
            secLevel = fsf.Data.Sec.level(subsection)
            secText = fsf.Data.Sec.text(subsection)
            return "|" + int(secLevel) * "-" + " " + subsection + ": " + secText

        def getTopSectionPretty(topSsection):
            secText = fsf.Data.Book.sections[topSsection]["name"]
            return  topSsection + ": " + secText

    class UI:
        def getWidgetSubsecId(subsection):
            '''
            Entry Image ID 
            '''
            return subsection.replace(".", "$")

        def getMainEntryWidgetName(subsection, imIdx):
            mainWidgetName:str = \
                dc.UIConsts.imageWidgetID + \
                "_" + _upan.Names.UI.getWidgetSubsecId(subsection) + "_" + imIdx
            mainWidgetName = mainWidgetName.replace(".", "$")
            return mainWidgetName

        def getExtraEntryWidgetName(subsection, imIdx, eImNum):
            ename = dc.UIConsts.imageWidgetID + "_e_" \
                    + str(eImNum) + "_" +  _upan.Names.UI.getWidgetSubsecId(subsection)\
                    + "_" + imIdx
            ename = ename.replace(".", "$")
            return ename

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