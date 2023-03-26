import os
import shutil

import file_system.book_fs as bfs
import file_system.toc_fs as tocfs
import file_system._utils as _ufs
import file_system.links as l
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import _utils.logging as log
import outside_calls.outside_calls_facade as ocf

import file_system.file_system_manager as fsm

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
        startPage = "_startPage"
        latestSubchapter = "_latestSubchapter"
        subSections = "_subSections"

        #imagesProperties
        imageProp = "_imageProp"
        imageContentFileMoveLinesNumber = "_imageContentFileMoveLinesNumber"
        imageTOCFileMoveLinesNumber = "_imageContentFileMoveLinesNumber"
        imLinkDict = "imLinkDict"

    class PrivProp:
        tocData = "_tocData"

        level = "_level"

        levelData = "_levelData"
        levelData_depth = "_depth"
        levelData_level = "_level"

    sectionPrefixForTemplate = ""
    sectionPathForTemplate = ""

    @classmethod
    def _getTemplate(cls, depth, level):
        sectionInfoEntryPrefix = cls.sectionPathForTemplate
        sectionInfo_template = {
                sectionInfoEntryPrefix + cls.PubProp.name: _u.Token.NotDef.str_t,
                sectionInfoEntryPrefix + cls.PubProp.startPage: _u.Token.NotDef.str_t,
                sectionInfoEntryPrefix + cls.PubProp.latestSubchapter: _u.Token.NotDef.str_t,
                # sectionInfoEntryPrefix + cls.PubProp.subSections: [],
                sectionInfoEntryPrefix + cls.PrivProp.levelData:{
                    sectionInfoEntryPrefix + cls.PrivProp.levelData_depth: str(depth),
                    sectionInfoEntryPrefix + cls.PrivProp.levelData_level: str(level),
                },
                sectionInfoEntryPrefix + cls.PrivProp.tocData:{
                    sectionInfoEntryPrefix + tocfs.TOCStructure.PubPro.text: _u.Token.NotDef.str_t,
                    sectionInfoEntryPrefix + tocfs.TOCStructure.PubPro.start: _u.Token.NotDef.str_t,
                    sectionInfoEntryPrefix + tocfs.TOCStructure.PubPro.finish: _u.Token.NotDef.str_t
                },
                sectionInfoEntryPrefix + cls.PubProp.imageProp: {
                    sectionInfoEntryPrefix + cls.PubProp.imageContentFileMoveLinesNumber: _u.Token.NotDef.str_t,
                    sectionInfoEntryPrefix + cls.PubProp.imageTOCFileMoveLinesNumber: _u.Token.NotDef.str_t,
                    sectionInfoEntryPrefix + cls.PubProp.imLinkDict: _u.Token.NotDef.dict_t
                }
                
        }
        return sectionInfo_template

    def getSectionJSONKeyPrefixFormPath(path):
        sectionPathSeparator = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator) 
        secPrefix = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix)
        return secPrefix + "_" + path.replace(sectionPathSeparator, "_")   

    def createStructure():
        os.makedirs(_ufs._getPathToSectionsFolder())
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.currSection,
                                            _u.Token.NotDef.str_t)
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.currTopSection, 
                                            _u.Token.NotDef.str_t)
        return

    @classmethod
    def addSection(cls, sectionPath):
        # set the curr section to new section
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.currSection, sectionPath)

        sectionPathSeparator = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator) 

        numLevels = len(sectionPath.split(sectionPathSeparator))

        dirPathToSection = _upan.Current.Paths.Section.abs()

        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(dirPathToSection):
            msg = "The sections structure was not present will create it.\n" + \
                    "Creating path: '{0}'".format(dirPathToSection)
            log.autolog(msg)
            
            # create folders
            sectionFolderName = dirPathToSection.split("/")[-1]
            _waitDummy = os.makedirs(dirPathToSection)

            # create images folder
            imagesFolderFSPath = os.path.join(dirPathToSection, sectionFolderName + "_images")
            _waitDummy = os.makedirs(imagesFolderFSPath)
            
            # create _con and _toc .tex files
            _waitDummy = \
                open(os.path.join(dirPathToSection, sectionFolderName + "_toc.tex"), "w").close()
            _waitDummy = \
                open(os.path.join(dirPathToSection, sectionFolderName + "_con.tex"), "w").close()
        
        # create the json file file, _out folder, main.tex
        relSectionPath = _u.Token.NotDef.str_t
        sectionPathList = sectionPath.split(sectionPathSeparator)
        for i,path in enumerate(sectionPathList):
            relSectionPath = path if relSectionPath == _u.Token.NotDef.str_t else relSectionPath + "." + path
            
            cls.sectionPathForTemplate = cls.getSectionJSONKeyPrefixFormPath(relSectionPath)
            
            pathToTopSection = _ufs._getSectionFilepath(relSectionPath)
            sectionFilepath = os.path.join(pathToTopSection, bfs.BookInfoStructure.sectionsInfoFilename)
            
            with open(sectionFilepath, "w+") as f:
                jsonObj = _u.json.dumps(cls._getTemplate(numLevels, i + 1), indent = 4)
                f.write(jsonObj)
            
            sectionFolderName = pathToTopSection.split("/")[-1]
            mainTemplateFile = os.path.join(os.getenv("BOOKS_TEMPLATES_PATH"),"main_template.tex")
            if not os.path.exists(os.path.join(pathToTopSection,"_out")):
                _waitDummy = os.makedirs(os.path.join(pathToTopSection,"_out"))
                _waitDummy = shutil.copy(mainTemplateFile, 
                                        os.path.join(pathToTopSection, 
                                        sectionFolderName + "_main.tex"))
        
        # copy the settings 
        vscodeSettings =os.path.join(os.getenv("BOOKS_TEMPLATES_PATH"), "settings.json")
        vscodeSettingsDirPath = os.path.join(dirPathToSection, ".vscode")
        os.makedirs(vscodeSettingsDirPath)
        shutil.copy(vscodeSettings, os.path.join(vscodeSettingsDirPath, "settings.json"))
    
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
    def readProperty(cls, sectionPath, propertyName):
        fullPathToSection = _ufs._getSectionFilepath(sectionPath)
        fullPathToSection = os.path.join(fullPathToSection, bfs.BookInfoStructure.sectionsInfoFilename)

        sectionPathSeparator = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator)
        
        sectionPrefixForTemplate = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix)
        sectionPathForTemplate = sectionPath.replace(sectionPathSeparator, "_")
        if sectionPathForTemplate == _u.Token.NotDef.str_t:
            return _u.Token.NotDef.str_t
        else:
            return _u.JSON.readProperty(fullPathToSection, 
                                        sectionPrefixForTemplate 
                                            + "_" + sectionPathForTemplate 
                                            + propertyName)

    @classmethod
    def updateProperty(cls, sectionPath, propertyName, newValue):        
        fullPathToSection = _ufs._getSectionFilepath(sectionPath)
        fullPathToSection = os.path.join(fullPathToSection, bfs.BookInfoStructure.sectionsInfoFilename)

        sectionPathSeparator = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator)
        sectionPrefixForTemplate = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix)
        sectionPathForTemplate = sectionPath.replace(sectionPathSeparator, "_")
        _u.JSON.updateProperty(fullPathToSection, 
                            sectionPrefixForTemplate + "_" + sectionPathForTemplate  + propertyName,
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