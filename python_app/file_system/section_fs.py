import os

import file_system.book_fs as bfs
import file_system.links as l
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import _utils.logging as log
import outside_calls.outside_calls_facade as ocf
import settings.facade as sf

class SectionInfoStructure:
    '''
    Structure to store sections and .tex files and images
    '''

    currStucturePath = ""

    # for later: add if the section should generate the pdf.
    # currPage = "currentPage"
    # currImageID = "currImageID"
    # currImageName = "currImageName"
    # currLinkName = "currLinkName"

    class PubProp:
        name = "_name"
        latestSubchapter = "_latestSubchapter"
        subSections = "_subSections"

        #imagesProperties
        imageProp = "_imageProp"
        imageContentFileMoveLinesNumber = "_imageContentFileMoveLinesNumber"
        imageTOCFileMoveLinesNumber = "_imageContentFileMoveLinesNumber"
        imLinkDict = "imLinkDict"

        # link to note taking app
        notesAppLink = "_notesAppLink"

        # TOC properties
        text = "TOC_text"
        start = "TOC_sectionStart"
        finish = "TOC_sectionFinish"

        # original material
        origMatName = "origMatName"
        imLinkOMPageDict = "imLinkOMPageDict"

        # global links
        imGlobalLinksDict = "imGlobalLinksDict"

    class PrivProp:
        tocData = "_tocData"

        level = "_level"

        levelData = "_levelData"
        levelData_level = "_level"

    sectionPrefixForTemplate = ""
    sectionPathForTemplate = ""

    @classmethod
    def _getTemplate(cls, level):
        
        sectionInfo_template = {
                cls.PubProp.name: _u.Token.NotDef.str_t,
                cls.PubProp.latestSubchapter: _u.Token.NotDef.str_t,
                cls.PubProp.notesAppLink: _u.Token.NotDef.str_t,
                cls.PubProp.origMatName : _u.Token.NotDef.str_t,
                cls.PrivProp.levelData: {
                    cls.PrivProp.levelData_level: str(level),
                },
                cls.PrivProp.tocData: {
                    cls.PubProp.text: _u.Token.NotDef.str_t,
                    cls.PubProp.start: _u.Token.NotDef.str_t,
                    cls.PubProp.finish: _u.Token.NotDef.str_t
                },
                cls.PubProp.imageProp: {
                    cls.PubProp.imageContentFileMoveLinesNumber: _u.Token.NotDef.str_t,
                    cls.PubProp.imageTOCFileMoveLinesNumber: _u.Token.NotDef.str_t,
                    cls.PubProp.imLinkDict: _u.Token.NotDef.dict_t,
                    cls.PubProp.imLinkOMPageDict: _u.Token.NotDef.dict_t,
                    cls.PubProp.imGlobalLinksDict: _u.Token.NotDef.dict_t
                }
        }
        return sectionInfo_template

    def getSectionJSONKeyPrefixFormPath(path):
        sectionPathSeparator = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator) 
        secPrefix = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix)
        return secPrefix + "_" + path.replace(sectionPathSeparator, "_")   

    def createStructure(bookName):
        subsectionPath = _upan.Paths.Section.getAbs(bookName)
        ocf.Wr.FsAppCalls.createDir(subsectionPath)
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.currSection,
                                            _u.Token.NotDef.str_t)
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.currTopSection, 
                                            _u.Token.NotDef.str_t)
        return

    @classmethod
    def __createSubsectionFiles(cls, bookpath, sectionPath):
        dirPathToSection_curr = _upan.Paths.Section.getAbs(bookpath, sectionPath)

        sectionPathSeparator = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator) 

        depth = len(sectionPath.split(sectionPathSeparator))

        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(dirPathToSection_curr):
            msg = "The sections structure was not present will create it.\n" + \
                    "Creating path: '{0}'".format(dirPathToSection_curr)
            log.autolog(msg)
            
            # create folders
            _waitDummy = ocf.Wr.FsAppCalls.createDir(dirPathToSection_curr)
            sectionJSONfilepath = _upan.Paths.Section.JSON.getAbs(bookpath, sectionPath)

            with open(sectionJSONfilepath, "w+") as f:
                jsonObj = _u.json.dumps(cls._getTemplate(depth), indent = 4)
                f.write(jsonObj)

            # create images folder
            imagesFolderFSPath = \
                ocf.Wr.FsAppCalls.createDir(_upan.Paths.Screenshot.getAbs(bookpath, sectionPath))
            imagesFolderFSPath = \
                ocf.Wr.FsAppCalls.createDir(_upan.Paths.TexFiles.Output.getAbs(bookpath, sectionPath))
            
            # create _con and _toc .tex files
            _waitDummy = \
                ocf.Wr.FsAppCalls.createFile(_upan.Paths.TexFiles.TOC.getAbs(bookpath, sectionPath))
            _waitDummy = \
                ocf.Wr.FsAppCalls.createFile(_upan.Paths.TexFiles.Content.getAbs(bookpath, sectionPath))
            _waitDummy = \
                ocf.Wr.FsAppCalls.createFile(_upan.Paths.TexFiles.Main.getAbs(bookpath, sectionPath))
            

        # copy the settings 
        vscodeSettings = os.path.join(os.getenv("BOOKS_TEMPLATES_PATH"), "settings.json")
        vscodeSettingsDirPath = os.path.join(dirPathToSection_curr, ".vscode")
        ocf.Wr.FsAppCalls.createDir(vscodeSettingsDirPath)
        ocf.Wr.FsAppCalls.copyFile(vscodeSettings, os.path.join(vscodeSettingsDirPath, "settings.json"))

    @classmethod
    def addSection(cls, bookpath, sectionPath):

        # set the curr section to new section
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.currSection, sectionPath)

        cls.__createSubsectionFiles(bookpath, sectionPath)

        cls.updateProperty(sectionPath, cls.PubProp.name, sectionPath)
    
    @classmethod
    def removeSection(cls, sectionPath):
        # take care if the section is current section


        currSection = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.currSection, sectionPath)
        # set the curr section to not defined
        # bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.currSection, sectionPath)

        # sectionPathSeparator = \
        #     bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator) 

        
        pass

    @classmethod
    def readProperty(cls, sectionPath, propertyName, bookPath = None):
        if bookPath == None:
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        
        fullPathToSection = _upan.Paths.Section.JSON.getAbs(bookPath, sectionPath)

        sectionPathSeparator = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator)
        
        sectionPathForTemplate = sectionPath.replace(sectionPathSeparator, "_")
        
        if sectionPathForTemplate == _u.Token.NotDef.str_t:
            return _u.Token.NotDef.str_t
        else:
            return _u.JSON.readProperty(fullPathToSection, 
                                        propertyName)

    @classmethod
    def updateProperty(cls, sectionPath, propertyName, newValue, bookPath = None):      
        if bookPath == None:
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        
        fullPathToSection = _upan.Paths.Section.JSON.getAbs(bookPath, sectionPath)

        _u.JSON.updateProperty(fullPathToSection, 
                            propertyName,
                            newValue)


class SectionCurrent:
    def getSubsectionsListForCurrTopSection():
        currSectionPath = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.currTopSection)
        childrensList = bfs.BookInfoStructure.getSubsectionsList(currSectionPath)
        return childrensList

    @classmethod
    def getSectionPdfName(cls):
        return cls.getSectionNameWprefix() + "_" + "main.pdf"

    @classmethod
    def getSectionNameWprefix(cls):
        sectionPrefix = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix)
        currSection = cls.getSectionNameNoPrefix()
        if currSection == _u.Token.NotDef.str_t:
            return _u.Token.NotDef.str_t
        return sectionPrefix + "_" + currSection

    @classmethod
    def getSectionNameNoPrefix(cls):
        currSection = _upan.Current.Names.Section.name()
        return currSection

    @classmethod
    def getImIDX(cls):
        currSectionPath = _upan.Current.Names.Section.name()
        return l.ImIDX.get(currSectionPath)

    @classmethod
    def getCurrLinkIdxDict(cls):
        currSectionPath = _upan.Current.Names.Section.name()
        return l.LinkDict.get(currSectionPath)

    @classmethod
    def setImLinkAndIDX(cls, linkName, imIDX):
        currSectionPath = _upan.Current.Names.Section.name()
        l.LinkDict.set(currSectionPath, linkName, imIDX)