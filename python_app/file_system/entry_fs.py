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
    lineImagePadding = 10
    lineImageTextSize = 10
    numSymbolsPerLine = 75

    class PubProp:
        name = "_name"

        entryLinesList = "_entryLinesArr"
        entryLinesNotesList = "_entryLinesNotesArr"
        entryNotesList = "_entryNotesArr"
        entryWordDictDict = "_entryWordDictArr"

    class PrivProp:
        pass

    @classmethod
    def _getTemplate(cls):   
        sectionInfo_template = {
            cls.PubProp.name: _u.Token.NotDef.str_t,
            cls.PubProp.entryLinesList: _u.Token.NotDef.list_t.copy(),
            cls.PubProp.entryLinesNotesList: _u.Token.NotDef.dict_t.copy(),
            cls.PubProp.entryNotesList: _u.Token.NotDef.dict_t.copy(),
            cls.PubProp.entryWordDictDict: _u.Token.NotDef.dict_t.copy()
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
    def addNote(cls, subsection, imIdx, text, 
                bookPath, position):
        log.autolog(f"Add note '{text}' at position '{position}' for '{subsection}' '{imIdx}'")
        structureCreated = False
        entryPath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)

        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryPath):
            cls.createStructure(bookPath, subsection, imIdx)
            structureCreated = True

        entryNotesList = cls.readProperty(subsection, imIdx, cls.PubProp.entryNotesList, bookPath)

        savePath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)
        filename = _upan.Names.Entry.Note.name(imIdx, position)

        savePath = os.path.join(savePath, filename)

        if (entryNotesList == _u.Token.NotDef.dict_t) :
            cls.updateProperty(subsection, imIdx, cls.PubProp.entryNotesList, {position: text}, bookPath)
        else:
            entryNotesList[position] = text
            cls.updateProperty(subsection, imIdx, cls.PubProp.entryNotesList, entryNotesList, bookPath)

        text = tff.Wr.TexFileUtils.formatEntrytext(text)
        tff.Wr.TexFileUtils.fromTexToImage(text,
                                           savePath,
                                           fixedWidth = cls.fixedWidth,
                                           fontSize = cls.lineImageFontSize,
                                           textSize = cls.lineImageTextSize,
                                           padding = cls.lineImagePadding,
                                           numSymPerLine = cls.numSymbolsPerLine,
                                           imSize = 500)

        msg = "\
After adding the note for  \n\
'{0}':'{1}'\n\
at position '{2}'.".format(subsection, imIdx, position)
        log.autolog(msg)
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

        return structureCreated

    @classmethod
    def addLine(cls, subsection, imIdx, text, bookPath, position = -1):
        log.autolog(f"Add line '{text}' at position '{position}' for '{subsection}' '{imIdx}'")
        structureCreated = False
        entryPath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)

        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryPath):
            cls.createStructure(bookPath, subsection, imIdx)
            structureCreated = True

        entryLinesList = cls.readProperty(subsection, imIdx, cls.PubProp.entryLinesList, bookPath)

        savePath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)
        filename = _upan.Names.Entry.Line.name(imIdx, str(len(entryLinesList)))

        savePath = os.path.join(savePath, filename)

        if entryLinesList == _u.Token.NotDef.list_t:
            entryLinesList = [text]
            cls.updateProperty(subsection, imIdx, cls.PubProp.entryLinesList, entryLinesList, bookPath)
        else:
            if position != -1:
                entryLinesList.insert(position, text)
                cls.updateProperty(subsection, imIdx, cls.PubProp.entryLinesList, entryLinesList, bookPath)
                for j in range(position, len(entryLinesList)):
                    cls.rebuildLine(subsection, imIdx, j, entryLinesList[j], bookPath)

                entryLinesNotesList = cls.readProperty(subsection, imIdx, 
                                                  cls.PubProp.entryLinesNotesList, bookPath)

                for j in range(len(entryLinesList) - 1, position, -1):
                    if entryLinesNotesList.get(str(j - 1)) != None:
                        cls.addLineNote(subsection, imIdx, 
                                        entryLinesNotesList[str(j - 1)], bookPath, j,
                                        stampChanges = False)
                        cls.rebuildLineNote(subsection, imIdx, j, 
                                            entryLinesNotesList[str(j - 1)], bookPath)
                return
            else:
                entryLinesList.append(text)

        text = tff.Wr.TexFileUtils.formatEntrytext(text)
        tff.Wr.TexFileUtils.fromTexToImage(text, 
                                           savePath, 
                                           fixedWidth = cls.fixedWidth,
                                           fontSize = cls.lineImageFontSize,
                                           textSize = cls.lineImageTextSize,
                                           padding = cls.lineImagePadding,
                                           numSymPerLine = cls.numSymbolsPerLine,
                                           imSize = 500)

        cls.updateProperty(subsection, imIdx, cls.PubProp.entryLinesList, entryLinesList, bookPath)

        msg = "\
After adding the line for  \n\
'{0}':'{1}'\n\
at position '{2}'.".format(subsection, imIdx, position)
        log.autolog(msg)
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

        return structureCreated

    @classmethod
    def addLineNote(cls, subsection, imIdx, text, bookPath, position = -1, stampChanges = True):
        log.autolog(f"Add lineNote '{text}' at position '{position}' for '{subsection}' '{imIdx}'")

        entryLinesNotesList = cls.readProperty(subsection, imIdx, cls.PubProp.entryLinesNotesList, bookPath)

        savePath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)
        filename = _upan.Names.Entry.LineNote.name(imIdx, str(len(entryLinesNotesList)))

        savePath = os.path.join(savePath, filename)

        if entryLinesNotesList == _u.Token.NotDef.dict_t:
            entryLinesNotesList = {position: text}
            cls.updateProperty(subsection, imIdx, cls.PubProp.entryLinesNotesList, entryLinesNotesList, bookPath)
        else:
            entryLinesNotesList[position] = text

        text = tff.Wr.TexFileUtils.formatEntrytext(text)
        tff.Wr.TexFileUtils.fromTexToImage(text, 
                                           savePath, 
                                           fixedWidth = cls.fixedWidth,
                                           fontSize = cls.lineImageFontSize,
                                           textSize = cls.lineImageTextSize,
                                           padding = cls.lineImagePadding,
                                           numSymPerLine = cls.numSymbolsPerLine,
                                           imSize = 500)

        cls.updateProperty(subsection, imIdx, cls.PubProp.entryLinesNotesList, entryLinesNotesList, bookPath)

        if stampChanges:
            msg = "\
    After adding note to the line for  \n\
    '{0}':'{1}'\n\
    at position '{2}'.".format(subsection, imIdx, position)
            log.autolog(msg)
            ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

    @classmethod
    def rebuildNote(cls, subsection, imIdx, noteIdx, text, bookPath):
        log.autolog(f"Rebuild note '{noteIdx}' for '{subsection}' '{imIdx}'")

        entryNotesList = cls.readProperty(subsection, imIdx, cls.PubProp.entryNotesList, bookPath)
        entryNotesList[str(noteIdx)] = text

        text = tff.Wr.TexFileUtils.formatEntrytext(text)
        savePath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)
        filename = _upan.Names.Entry.Note.name(imIdx, noteIdx)
        savePath = os.path.join(savePath, filename)
        tff.Wr.TexFileUtils.fromTexToImage(text,
                                           savePath,
                                           fixedWidth = cls.fixedWidth,
                                           fontSize = cls.lineImageFontSize,
                                           textSize = cls.lineImageTextSize,
                                           padding = cls.lineImagePadding,
                                           numSymPerLine = cls.numSymbolsPerLine,
                                           imSize = 500)

        cls.updateProperty(subsection, imIdx, cls.PubProp.entryNotesList, entryNotesList, bookPath)

    @classmethod
    def updateExerciseImage(cls, subsection, imIdx, lineIdx, bookPath):
        entryLinesList = cls.readProperty(subsection, imIdx, cls.PubProp.entryLinesList, bookPath)
        text = entryLinesList[int(lineIdx)]

        text = tff.Wr.TexFileUtils.formatEntrytext(text)
        savePath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)
        filename = _upan.Names.Entry.Line.name(imIdx, lineIdx)
        savePath = os.path.join(savePath, filename)

        ocf.Wr.FsAppCalls.deleteFile(savePath)

        tff.Wr.TexFileUtils.fromTexToImage(text,
                                           savePath,
                                           fixedWidth = cls.fixedWidth,
                                           fontSize = cls.lineImageFontSize,
                                           textSize = cls.lineImageTextSize,
                                           padding = cls.lineImagePadding,
                                           numSymPerLine = cls.numSymbolsPerLine,
                                           imSize = 500)

    @classmethod
    def updateExerciseLine(cls, subsection, imIdx, lineIdx, text, bookPath):
        log.autolog(f"Update Exercise line '{lineIdx}' for '{subsection}' '{imIdx}'")
        entryLinesList = cls.readProperty(subsection, imIdx, cls.PubProp.entryLinesList, bookPath)
        entryLinesList[int(lineIdx)] = text
        cls.updateProperty(subsection, imIdx, cls.PubProp.entryLinesList, entryLinesList, bookPath)

    @classmethod
    def rebuildLine(cls, subsection, imIdx, lineIdx, text, bookPath):
        log.autolog(f"Rebuild line '{lineIdx}' for '{subsection}' '{imIdx}'")

        cls.updateExerciseLine(subsection, imIdx, lineIdx, text, bookPath)
        cls.updateExerciseImage(subsection, imIdx, lineIdx, bookPath)

    @classmethod
    def rebuildLineNote(cls, subsection, imIdx, lineIdx, text, bookPath):
        log.autolog(f"Rebuild note for line '{lineIdx}' for '{subsection}' '{imIdx}'")

        entryLinesNotesList = cls.readProperty(subsection, imIdx, cls.PubProp.entryLinesNotesList, bookPath)
        entryLinesNotesList[str(lineIdx)] = text

        text = tff.Wr.TexFileUtils.formatEntrytext(text)
        savePath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)
        filename = _upan.Names.Entry.LineNote.name(imIdx, lineIdx)
        savePath = os.path.join(savePath, filename)
        tff.Wr.TexFileUtils.fromTexToImage(text,
                                           savePath,
                                           fixedWidth = cls.fixedWidth,
                                           fontSize = cls.lineImageFontSize,
                                           textSize = cls.lineImageTextSize,
                                           padding = cls.lineImagePadding,
                                           numSymPerLine = cls.numSymbolsPerLine,
                                           imSize = 500)

        cls.updateProperty(subsection, imIdx, cls.PubProp.entryLinesNotesList, entryLinesNotesList, bookPath)

    @classmethod
    def deleteNote(cls, bookPath, subsection, imIdx, noteIdx):
        log.autolog(f"Remove note '{noteIdx}' for '{subsection}' '{imIdx}'")

        entryNotesList = cls.readProperty(subsection, imIdx, cls.PubProp.entryNotesList, bookPath)
        entryNotesList.pop(noteIdx)

        if entryNotesList == {}:
            entryNotesList = _u.Token.NotDef.dict_t.copy()

        cls.updateProperty(subsection, imIdx, cls.PubProp.entryNotesList, entryNotesList, bookPath)

        for k in entryNotesList.keys():
            cls.rebuildNote(subsection, imIdx, k, entryNotesList[k], bookPath)

        imageToRemovePath = \
            _upan.Paths.Entry.NoteImage.getAbs(bookPath,
                                               subsection,
                                               imIdx, 
                                               noteIdx)
        ocf.Wr.FsAppCalls.deleteFile(imageToRemovePath)

    @classmethod
    def deleteLine(cls, bookPath, subsection, imIdx, lineIdx):
        log.autolog(f"Remove line '{lineIdx}' for '{subsection}' '{imIdx}'")

        entryLinesList = cls.readProperty(subsection, imIdx, cls.PubProp.entryLinesList, bookPath)

        # update 
        entryLinesNotesList = cls.readProperty(subsection, imIdx, 
                                               cls.PubProp.entryLinesNotesList, bookPath)

        for j in range(lineIdx + 1, len(entryLinesList)):
            if entryLinesNotesList.get(j) != None:
                cls.addLineNote(subsection, imIdx,
                                entryLinesNotesList[str(j)], bookPath, j - 1,
                                stampChanges = False)

        entryLinesList.pop(lineIdx)
        cls.updateProperty(subsection, imIdx, cls.PubProp.entryLinesList, entryLinesList, bookPath)

        cls.deleteLineNote(bookPath, subsection, imIdx, lineIdx)


        for j in range(lineIdx, len(entryLinesList)):
            cls.rebuildLine(subsection, imIdx, j, entryLinesList[j], bookPath)
            if entryLinesNotesList.get(str(j)) != None:
                cls.rebuildLineNote(subsection, imIdx, j, entryLinesNotesList[str(j)], bookPath)

        imageToRemovePath = \
            _upan.Paths.Entry.LineImage.getAbs(bookPath, subsection, imIdx, len(entryLinesList))
        ocf.Wr.FsAppCalls.deleteFile(imageToRemovePath)

        if entryLinesList == []:
            cls.removeEntry(subsection, imIdx, bookPath)
            return True

    @classmethod
    def deleteLineNote(cls, bookPath, subsection, imIdx, lineIdx):
        log.autolog(f"Remove note for line '{lineIdx}' for '{subsection}' '{imIdx}'")

        entryLinesNotesList = cls.readProperty(subsection, imIdx, 
                                               cls.PubProp.entryLinesNotesList, bookPath)

        if entryLinesNotesList.get(str(lineIdx)) == None:
            return

        entryLinesNotesList.pop(str(lineIdx))
        cls.updateProperty(subsection, imIdx, 
                           cls.PubProp.entryLinesNotesList, entryLinesNotesList, bookPath)

        imageToRemovePath = \
            _upan.Paths.Entry.LineNoteImage.getAbs(bookPath, subsection, imIdx, lineIdx)
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

        try:
            prop =  _u.JSON.readProperty(fullPathToEntryJSON, 
                                        propertyName)
        except:
            prop = cls._getTemplate()[propertyName]

        return prop

    @classmethod
    def updateProperty(cls, subsection, imIdx, propertyName, newValue, bookPath = None):      
        if bookPath == None:
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        
        fullPathToEntry = _upan.Paths.Entry.JSON.getAbs(bookPath, subsection, imIdx)

        entryFSFile:dict = _u.JSON.readFile(fullPathToEntry)

        if propertyName not in list(entryFSFile.keys()):
            entryFSFile[propertyName] = newValue
            _u.JSON.writeFile(fullPathToEntry, entryFSFile)
        else:
            _u.JSON.updateProperty(fullPathToEntry, 
                                propertyName,
                                newValue)