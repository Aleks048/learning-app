import os
import shutil

import file_system.book_fs as bfs
import file_system.toc_fs as tocfs
import file_system._utils as _ufs
import file_system.links as l
import file_system.paths as paths
import _utils._utils_main as _u
import _utils.logging as log

class SectionInfoStructure:
    '''
    Structure to store sections and .tex files and images
    '''

    currStucturePath = ""

    # for later: add if the section should generate the pdf.
    # currPage_ID = "currentPage"
    # currImageID_ID = "currImageID"
    # currImageName_ID = "currImageName"
    # currLinkName_ID = "currLinkName"

    class PubProp:
        name_ID = "_name"
        startPage_ID = "_startPage"
        latestSubchapter_ID = "_latestSubchapter"
        subSections_ID = "_subSections"

        #imagesProperties
        imageProp_ID = "_imageProp"
        imageContentFileMoveLinesNumber_ID = "_imageContentFileMoveLinesNumber"
        imageTOCFileMoveLinesNumber_ID = "_imageContentFileMoveLinesNumber"
        imLinkDict_ID = "imLinkDict"

    class PrivProp:
        tocData_ID = "_tocData"

        level_ID = "_level"

        levelData_ID = "_levelData"
        levelData_depth_ID = "_depth"
        levelData_level_ID = "_level"

    sectionPrefixForTemplate = ""
    sectionPathForTemplate = ""

    @classmethod
    def _getTemplate(cls, depth, level):
        sectionInfoEntryPrefix = cls.sectionPathForTemplate
        sectionInfo_template = {
                sectionInfoEntryPrefix + cls.PubProp.name_ID: _u.Token.NotDef.str_t,
                sectionInfoEntryPrefix + cls.PubProp.startPage_ID: _u.Token.NotDef.str_t,
                sectionInfoEntryPrefix + cls.PubProp.latestSubchapter_ID: _u.Token.NotDef.str_t,
                # sectionInfoEntryPrefix + cls.PubProp.subSections_ID: [],
                sectionInfoEntryPrefix + cls.PrivProp.levelData_ID:{
                    sectionInfoEntryPrefix + cls.PrivProp.levelData_depth_ID: str(depth),
                    sectionInfoEntryPrefix + cls.PrivProp.levelData_level_ID: str(level),
                },
                sectionInfoEntryPrefix + cls.PrivProp.tocData_ID:{
                    sectionInfoEntryPrefix + tocfs.TOCStructure.PubPro.text_ID: _u.Token.NotDef.str_t,
                    sectionInfoEntryPrefix + tocfs.TOCStructure.PubPro.start_ID: _u.Token.NotDef.str_t,
                    sectionInfoEntryPrefix + tocfs.TOCStructure.PubPro.finish_ID: _u.Token.NotDef.str_t
                },
                sectionInfoEntryPrefix + cls.PubProp.imageProp_ID: {
                    sectionInfoEntryPrefix + cls.PubProp.imageContentFileMoveLinesNumber_ID: _u.Token.NotDef.str_t,
                    sectionInfoEntryPrefix + cls.PubProp.imageTOCFileMoveLinesNumber_ID: _u.Token.NotDef.str_t,
                    sectionInfoEntryPrefix + cls.PubProp.imLinkDict_ID: _u.Token.NotDef.dict_t
                }
                
        }
        return sectionInfo_template

    def getSectionJSONKeyPrefixFormPath(path):
        sectionPathSeparator = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator_ID) 
        secPrefix = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix_ID)
        return secPrefix + "_" + path.replace(sectionPathSeparator, "_")   

    def createStructure():
        os.makedirs(_ufs._getPathToSectionsFolder())
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.currentPage_ID, 
                                            _u.Token.NotDef.str_t)
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.currSection_ID,
                                            _u.Token.NotDef.str_t)
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.currTopSection_ID, 
                                            _u.Token.NotDef.str_t)
        return

    @classmethod
    def addSection(cls, sectionPath):
        # set the curr section to new section
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.currSection_ID, sectionPath)

        sectionPathSeparator = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator_ID) 

        numLevels = len(sectionPath.split(sectionPathSeparator))

        dirPathToSection = paths.Paths.Section.getAbs()

        if not os.path.exists(dirPathToSection):
            msg = "The sections structure was not present will create it.\n" + \
                    "Creating path: " + dirPathToSection
            log.autolog(msg)
            
            # create folders
            sectionFolderName = dirPathToSection.split("/")[-1]
            _waitDummy = os.makedirs(dirPathToSection)
            _waitDummy = os.makedirs(paths.Paths.Screenshot.getAbs())
            _waitDummy = os.makedirs(paths.Paths.Scripts.Links.Local.getAbs())
            _waitDummy = os.makedirs(paths.Paths.Scripts.Links.Global.getAbs())
            _waitDummy = os.makedirs(paths.Paths.Scripts.Utils.getAbs())
            
            # create files
            _waitDummy = \
                open(os.path.join(dirPathToSection, sectionFolderName + "_toc.tex"), "w").close()
            _waitDummy = \
                open(os.path.join(dirPathToSection, sectionFolderName + "_con.tex"), "w").close()
        
        # create the json file file, _out folder, main.tex
        relSectionPath = ""
        sectionPathList = sectionPath.split(sectionPathSeparator)
        for i,p in enumerate(sectionPathList):
            relSectionPath += p if relSectionPath == "" else "." + p
            
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
    def readProperty(cls, sectionPath, propertyName):
        fullPathToSection = _ufs._getSectionFilepath(sectionPath)
        fullPathToSection = os.path.join(fullPathToSection, bfs.BookInfoStructure.sectionsInfoFilename)

        sectionPathSeparator = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator_ID)
        
        sectionPrefixForTemplate = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix_ID)
        sectionPathForTemplate = sectionPath.replace(sectionPathSeparator, "_")
        if sectionPathForTemplate == _u.Token.NotDef.str_t:
            return ""
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
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_path_separator_ID)
        sectionPrefixForTemplate = \
            bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix_ID)
        sectionPathForTemplate = sectionPath.replace(sectionPathSeparator, "_")
        _u.JSON.updateProperty(fullPathToSection, 
                            sectionPrefixForTemplate + "_" + sectionPathForTemplate  + propertyName,
                            newValue)


class SectionCurrent:
    @classmethod
    def getSectionPdfName(cls):
        return cls.getSectionNameWprefix() + "_" + "main.myPDF"

    @classmethod
    def getSectionNameWprefix(cls):
        sectionPrefix = bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.sections_prefix_ID)
        currSection = cls.getSectionNameNoPrefix()
        return sectionPrefix + "_" + currSection

    @classmethod
    def getSectionNameNoPrefix(cls):
        currSection = cls.readCurrSection()
        return currSection

    @classmethod
    def getImIDX(cls):
        currSectionPath = cls.readCurrSection()
        return l.ImIDX.get(currSectionPath)

    @classmethod
    def getCurrLinkIdxDict(cls):
        currSectionPath = cls.readCurrSection()
        return l.LinkDict.get(currSectionPath)

    @classmethod
    def setImLinkAndIDX(cls, linkName, imIDX):
        currSectionPath = cls.readCurrSection()
        l.LinkDict.set(currSectionPath, linkName, imIDX)

    def readCurrSection():
        return bfs.BookInfoStructure.readProperty(bfs.BookInfoStructure.PubProp.currSection_ID)