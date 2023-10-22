import os

import file_system.book_fs as bfs
import file_system.links as l
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import _utils.logging as log
import outside_calls.outside_calls_facade as ocf
import settings.facade as sf
import UI.widgets_facade as wf
import UI.widgets_collection.common as wcom
import data.constants as dc
import data.temp as dt
import tex_file.tex_file_facade as tff

class EntryInfoStructure:
    '''
    Structure to store sections and .tex files and images
    '''

    currStucturePath = ""
    fixedWidth = 530
    lineImageFontSize = 10
    lineImagePadding = 5
    lineImageTextSize = 10
    numSymbolsPerLine = 75

    class PubProp:
        name = "_name"

        entryLinesList = "_entryLinesArr"

    class PrivProp:
        pass

    @classmethod
    def _getTemplate(cls):   
        sectionInfo_template = {
            cls.PubProp.name: _u.Token.NotDef.str_t,
            cls.PubProp.entryLinesList: _u.Token.NotDef.list_t
        }
        return sectionInfo_template

    @classmethod
    def createStructure(cls, bookName, subsection, imIdx):
        log.autolog(f"Create entry structure for '{subsection}' '{imIdx}'")
        entryPath = _upan.Paths.Entry.getAbs(bookName, subsection, imIdx)

        ocf.Wr.FsAppCalls.createDir(entryPath)

        # create JSONFILE
        sectionJSONfilepath = _upan.Paths.Entry.JSON.getAbs(bookName, subsection, imIdx)

        with open(sectionJSONfilepath, "w+") as f:
            jsonObj = _u.json.dumps(cls._getTemplate(), indent = 4)
            f.write(jsonObj)

        # set the name
        cls.updateProperty(subsection, imIdx, cls.PubProp.name, str(imIdx), bookName)

    @classmethod
    def addLine(cls, subsection, imIdx, text, bookPath, position = -1):
        log.autolog(f"Add line '{text}' at position '{position}' for '{subsection}' '{imIdx}'")
        entryPath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)

        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryPath):
            cls.createStructure(bookPath, subsection, imIdx)

        entryLinesList = cls.readProperty(subsection, imIdx, cls.PubProp.entryLinesList, bookPath)

        if entryLinesList == _u.Token.NotDef.list_t:
            entryLinesList = [text]
            cls.updateProperty(subsection, imIdx, cls.PubProp.entryLinesList, entryLinesList, bookPath)
        else:
            if position != -1:
                entryLinesList.insert(position, text)
                cls.updateProperty(subsection, imIdx, cls.PubProp.entryLinesList, entryLinesList, bookPath)
                for j in range(position, len(entryLinesList)):
                    cls.rebuildLine(subsection, imIdx, j, entryLinesList[j], bookPath)
                return
            else:
                entryLinesList.append(text)

        text = tff.Wr.TexFileUtils.formatEntrytext(text)
        savePath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)
        filename = _upan.Names.Entry.Line.name(imIdx, str(len(entryLinesList) - 1))
        savePath = os.path.join(savePath, filename)
        tff.Wr.TexFileUtils.fromTexToImage(text, 
                                           savePath, 
                                           fixedWidth = cls.fixedWidth,
                                           fontSize = cls.lineImageFontSize,
                                           textSize = cls.lineImageTextSize,
                                           padding = cls.lineImagePadding,
                                           numSymPerLine = cls.numSymbolsPerLine)

        cls.updateProperty(subsection, imIdx, cls.PubProp.entryLinesList, entryLinesList, bookPath)

    @classmethod
    def rebuildLine(cls, subsection, imIdx, lineIdx, text, bookPath):
        log.autolog(f"Rebuild line '{lineIdx}' for '{subsection}' '{imIdx}'")

        entryLinesList = cls.readProperty(subsection, imIdx, cls.PubProp.entryLinesList, bookPath)
        entryLinesList[int(lineIdx)] = text

        text = tff.Wr.TexFileUtils.formatEntrytext(text)
        savePath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)
        filename = _upan.Names.Entry.Line.name(imIdx, lineIdx)
        savePath = os.path.join(savePath, filename)
        tff.Wr.TexFileUtils.fromTexToImage(text,
                                           savePath,
                                           fixedWidth = cls.fixedWidth,
                                           fontSize = cls.lineImageFontSize,
                                           textSize = cls.lineImageTextSize,
                                           padding = cls.lineImagePadding,
                                           numSymPerLine = cls.numSymbolsPerLine)

        cls.updateProperty(subsection, imIdx, cls.PubProp.entryLinesList, entryLinesList, bookPath)

    @classmethod
    def deleteLine(cls, bookPath, subsection, imIdx, lineIdx):
        log.autolog(f"Remove line '{lineIdx}' for '{subsection}' '{imIdx}'")

        entryLinesList = cls.readProperty(subsection, imIdx, cls.PubProp.entryLinesList, bookPath)
        entryLinesList.pop(lineIdx)
        cls.updateProperty(subsection, imIdx, cls.PubProp.entryLinesList, entryLinesList, bookPath)

        for j in range(lineIdx, len(entryLinesList)):
            cls.rebuildLine(subsection, imIdx, j, entryLinesList[j], bookPath)

        imageToRemovePath = \
            _upan.Paths.Entry.LineImage.getAbs(bookPath, subsection, imIdx, len(entryLinesList))
        ocf.Wr.FsAppCalls.deleteFile(imageToRemovePath)

    @classmethod
    def removeEntry(cls, subsection, imIdx, bookName):
       log.autolog(f"Remove all lines for '{subsection}' '{imIdx}'")
       entryPath = _upan.Paths.Entry.getAbs(bookName, subsection, imIdx)
       ocf.Wr.FsAppCalls.removeDir(entryPath)

    @classmethod
    def readProperty(cls, sectionPath, imIdx, propertyName, bookPath = None):
        if bookPath == None:
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        
        fullPathToEntryJSON = _upan.Paths.Entry.JSON.getAbs(bookPath, sectionPath, imIdx)

        prop =  _u.JSON.readProperty(fullPathToEntryJSON, 
                                    propertyName)
        return prop

    @classmethod
    def updateProperty(cls, subsection, imIdx, propertyName, newValue, bookPath = None):      
        if bookPath == None:
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        
        fullPathToEntry = _upan.Paths.Entry.JSON.getAbs(bookPath, subsection, imIdx)

        _u.JSON.updateProperty(fullPathToEntry, 
                               propertyName,
                               newValue)