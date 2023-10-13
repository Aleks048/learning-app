import os

import file_system.book_fs as bfs
import file_system.entry_fs as efs
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
        imLinkOMPageDict = "imLinkOMPageDict"
        imGlobalLinksDict = "imGlobalLinksDict"
        origMatNameDict = "origMatNameDict"
        extraImagesDict = "extraImagesDict"
        tocWImageDict = "tocWImageDict"
        imagesGroupDict = "imagesGroupDict"

        # link to note taking app
        notesAppLink = "_notesAppLink"

        # TOC properties
        text = "TOC_text"
        start = "TOC_sectionStart"
        finish = "TOC_sectionFinish"

        #list of image groups
        imagesGroupsList = "imagesGroupsList"

        level = "_level"
        levelData = "_levelData"

    class PrivProp:
        tocData = "_tocData"

    sectionPrefixForTemplate = ""
    sectionPathForTemplate = ""

    @classmethod
    def _getTemplate(cls, level):
        
        sectionInfo_template = {
                cls.PubProp.name: _u.Token.NotDef.str_t,
                cls.PubProp.latestSubchapter: _u.Token.NotDef.str_t,
                cls.PubProp.notesAppLink: _u.Token.NotDef.str_t,
                cls.PubProp.imagesGroupsList: {"No group": True},
                cls.PubProp.levelData: {
                    cls.PubProp.level: str(level),
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
                    cls.PubProp.imGlobalLinksDict: _u.Token.NotDef.dict_t,
                    cls.PubProp.origMatNameDict : _u.Token.NotDef.dict_t,
                    cls.PubProp.extraImagesDict : _u.Token.NotDef.dict_t,
                    cls.PubProp.tocWImageDict : _u.Token.NotDef.dict_t,
                    cls.PubProp.imagesGroupDict : _u.Token.NotDef.dict_t
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
        subsectionPath = _upan.Paths.Section.getBaseAbs(bookName)
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
        # update things here for the book open subsection
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.subsectionOpenInTOC_UI, sectionPath)

        cls.__createSubsectionFiles(bookpath, sectionPath)

        cls.updateProperty(sectionPath, cls.PubProp.name, sectionPath)
    
    def __shiftTheItemsInTheDict(dict, startShiftIdx):
        # shift each item of the dict starting from the idx to the left
        outDict = {}

        for k in list(dict.keys()):
            if int(k) < int(startShiftIdx):
                outDict[k] = dict[k]
            else:
                outDict[str(int(k)-1)] = dict[k]

        return outDict

    @classmethod
    def removeEntry(cls, subsection, imIdx):
        import generalManger.generalManger as gm

        # ask the user if we wnat to proceed.
        msg = "Do you want to remove '{0}_{1}'?".format(subsection, imIdx)
        response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

        mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.MathMenuManager)
        mainManager.show()

        if not response:
            return

        # NOTE: ask twice if the user is sure.
        msg = "Still sure you want to remove '{0}_{1}'?".format(subsection, imIdx)
        response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

        mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.MathMenuManager)
        mainManager.show()

        if not response:
            return
        
        # track all the changes berore and after removal
        msg = "Before removing the subsection: '{0}_{1}'.".format(subsection, imIdx)
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

        currBookName = sf.Wr.Manager.Book.getCurrBookName()
        imagesPath = _upan.Paths.Screenshot.getAbs(currBookName, subsection)

        extraImagesDict = cls.readProperty(subsection, cls.PubProp.extraImagesDict)
        imGlobalLinksDict = cls.readProperty(subsection, cls.PubProp.imGlobalLinksDict)

        # move the extra images
        if imIdx in list(extraImagesDict.keys()):
            extraImNames = extraImagesDict[imIdx]

            if extraImNames != None:
                for extraImIdx in range(len(extraImNames)):
                    extraImFilename = _upan.Names.getExtraImageFilename(imIdx, subsection, extraImIdx)
                    ocf.Wr.FsAppCalls.deleteFile(os.path.join(imagesPath, extraImFilename + ".png"))
        

        imLinkDict = cls.readProperty(subsection, cls.PubProp.imLinkDict)
       
        if imIdx == list(imLinkDict.keys())[-1]:
            imName = _upan.Names.getImageName(imIdx, subsection)
            ocf.Wr.FsAppCalls.deleteFile(os.path.join(imagesPath, imName + ".png"))
        else:
            # take care of the rest of the images in the subsesction
            for imLinkId in list(imLinkDict.keys()):
                if int(imLinkId) > int(imIdx):
                    # move the main image files
                    imNameOld = _upan.Names.getImageName(imLinkId, subsection)
                    imNameNew = _upan.Names.getImageName(str(int(imLinkId) - 1), subsection)
                    ocf.Wr.FsAppCalls.moveFile(os.path.join(imagesPath, imNameOld + ".png"),
                                            os.path.join(imagesPath, imNameNew + ".png"))
                    
                    # move the extra images
                    if imLinkId in list(extraImagesDict.keys()):
                        extraImNames = extraImagesDict[imLinkId]

                        if extraImNames != None:
                            for extraImIdx in range(len(extraImNames)):
                                extraImOldFilename = _upan.Names.getExtraImageFilename(imLinkId, subsection, extraImIdx)
                                extraImNewFilename = _upan.Names.getExtraImageFilename(str(int(imLinkId) - 1), subsection, extraImIdx)

                                ocf.Wr.FsAppCalls.moveFile(os.path.join(imagesPath, extraImOldFilename + ".png"),
                                                            os.path.join(imagesPath, extraImNewFilename + ".png"))

        # update the tex files
        tff.Wr.TexFileModify.removeImageFromCon(currBookName, subsection, imIdx)
        
        # remove all the global links that lead to this entry
        if imIdx in list(imGlobalLinksDict.keys()):
            glLinksListImDict = imGlobalLinksDict[imIdx]
            for glLink in list(glLinksListImDict.keys()):
                linkSubsection = glLink.split("_")[0]
                linkIdx = glLink.split("_")[1]
                
                linkGlobalLinksDict = cls.readProperty(linkSubsection, cls.PubProp.imGlobalLinksDict)
                linkGlobalLinksImDict = linkGlobalLinksDict[linkIdx]
                linkGlobalLinksImDict.pop(subsection + "_" + imIdx)
                if linkGlobalLinksImDict == {}:
                    linkGlobalLinksDict.pop(linkIdx)
                else:
                    linkGlobalLinksDict[linkIdx] = linkGlobalLinksImDict
                if linkGlobalLinksDict == {}:
                    linkGlobalLinksDict = _u.Token.NotDef.dict_t

                cls.updateProperty(linkSubsection, cls.PubProp.imGlobalLinksDict, linkGlobalLinksDict)
        
        # update links to other images
        for imLinkId in list(imLinkDict.keys()):
            if int(imLinkId) > int(imIdx):
                if imLinkId in list(imGlobalLinksDict.keys()):
                    glLinksListImDict = imGlobalLinksDict[imLinkId]
                    for glLink in list(glLinksListImDict.keys()):
                        linkSubsection = glLink.split("_")[0]
                        linkIdx = glLink.split("_")[1]
                        
                        linkGlobalLinksDict = cls.readProperty(linkSubsection, cls.PubProp.imGlobalLinksDict)
                        linkGlobalLinksImDict = linkGlobalLinksDict[linkIdx]
                        linkGlobalLinksImDict.pop(subsection + "_" + imLinkId)

                        linkGlobalLinksImDict[subsection + "_" + str(int(imLinkId) - 1)] = \
                                        tff.Wr.TexFileUtils.getUrl(currBookName, 
                                                                subsection, 
                                                                subsection.split(".")[0],
                                                                str(int(imLinkId) - 1),
                                                                "full",
                                                                False)

                        linkGlobalLinksDict[linkIdx] = linkGlobalLinksImDict

                        cls.updateProperty(linkSubsection, cls.PubProp.imGlobalLinksDict, linkGlobalLinksDict)

        imLinkDict.pop(imIdx, None)
        imLinkDict = cls.__shiftTheItemsInTheDict(imLinkDict, imIdx)

        if imLinkDict == {}:
            imLinkDict = _u.Token.NotDef.dict_t

        cls.updateProperty(subsection, cls.PubProp.imLinkDict, imLinkDict)

        imLinkOMPageDict:dict = cls.readProperty(subsection, cls.PubProp.imLinkOMPageDict)
        imLinkOMPageDict.pop(imIdx, None)
        imLinkOMPageDict = cls.__shiftTheItemsInTheDict(imLinkOMPageDict, imIdx)

        if imLinkOMPageDict == {}:
            imLinkOMPageDict = _u.Token.NotDef.dict_t

        cls.updateProperty(subsection, cls.PubProp.imLinkOMPageDict, imLinkOMPageDict)

        imGlobalLinksDict.pop(imIdx, None)
        imGlobalLinksDict = cls.__shiftTheItemsInTheDict(imGlobalLinksDict, imIdx)

        if imLinkOMPageDict == {}:
            imLinkOMPageDict = _u.Token.NotDef.dict_t

        cls.updateProperty(subsection, cls.PubProp.imGlobalLinksDict, imGlobalLinksDict)

        origMatNameDict = cls.readProperty(subsection, cls.PubProp.origMatNameDict)
        origMatNameDict.pop(imIdx, None)
        origMatNameDict = cls.__shiftTheItemsInTheDict(origMatNameDict, imIdx)

        if origMatNameDict == {}:
            origMatNameDict = _u.Token.NotDef.dict_t

        cls.updateProperty(subsection, cls.PubProp.origMatNameDict, origMatNameDict)

        extraImagesDict = cls.readProperty(subsection, cls.PubProp.extraImagesDict)
        extraImNames = extraImagesDict.pop(imIdx, None)
        extraImagesDict = cls.__shiftTheItemsInTheDict(extraImagesDict, imIdx)

        tocWImageDict = cls.readProperty(subsection, cls.PubProp.tocWImageDict)
        tocWImageDict.pop(imIdx, None)

        if tocWImageDict == {}:
            tocWImageDict = _u.Token.NotDef.dict_t

        tocWImageDict = cls.__shiftTheItemsInTheDict(tocWImageDict, imIdx)
        cls.updateProperty(subsection, cls.PubProp.tocWImageDict, tocWImageDict)

        imagesGroupDict = cls.readProperty(subsection, cls.PubProp.imagesGroupDict)
        imagesGroupDict.pop(imIdx, None)

        if imagesGroupDict == {}:
            imagesGroupDict = _u.Token.NotDef.dict_t

        imagesGroupDict = cls.__shiftTheItemsInTheDict(imagesGroupDict, imIdx)
        cls.updateProperty(subsection, cls.PubProp.imagesGroupDict, imagesGroupDict)

        if extraImagesDict == {}:
            extraImagesDict = _u.Token.NotDef.dict_t

        cls.updateProperty(subsection, cls.PubProp.extraImagesDict, extraImagesDict)

        # update the links on the OM file
        for page in set(list(imLinkOMPageDict.values())):
            gm.GeneralManger.readdNotesToPage(page)


        efs.EntryInfoStructure.removeEntry(subsection, imIdx, currBookName)

        # track all the changes berore and after removal
        msg = "After removing the subsection: '{0}_{1}'.".format(subsection, imIdx)
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

        cls.rebuildSubsectionLatex(subsection, 
                                   wcom.getWidgetNameID, 
                                   wcom.formatGroupText,
                                   wcom.formatSectionText,
                                   wcom.getSubsectionPretty,
                                   wcom.getTopSectionPretty)
    
    @classmethod
    def rebuildSubsectionLatex(cls, subsection, 
                               fromSubAndEntryIdxToNameId, 
                               fromGroupNameToFilename, 
                               fromSubSectionToFileID,
                               createPrettySubSection,
                               createPrettyTopSection):
        topSection = subsection.split(".")[0]
        imLinkDict = cls.readProperty(subsection, cls.PubProp.imLinkDict)
        secreenshotPath = _upan.Paths.Screenshot.getAbs(sf.Wr.Manager.Book.getCurrBookName(), 
                                                        subsection)
        topSectionPath = _upan.Paths.Section.getAbs(sf.Wr.Manager.Book.getCurrBookName(), 
                                                topSection)

        groups = cls.readProperty(subsection, cls.PubProp.imagesGroupsList)

        for k, v in imLinkDict.items():
            filename = "_" + fromSubAndEntryIdxToNameId(subsection, k) + ".png"
            entryImgPath = os.path.join(secreenshotPath, filename)
            tex = tff.Wr.TexFileUtils.fromEntryToLatexTxt(k, v)

            tff.Wr.TexFileUtils.fromTexToImage(tex, entryImgPath)
        
        for g in groups:
            filename = "_g_" + fromGroupNameToFilename(g) + ".png"
            tex = tff.Wr.TexFileUtils.formatEntrytext(g)
            groupImgPath = os.path.join(secreenshotPath, filename)
            tff.Wr.TexFileUtils.fromTexToImage(tex, groupImgPath, padding = 10, imageColor="#109464")

        # subsection image
        filename = "_sub_" + fromSubSectionToFileID(subsection) + ".png"
        tex = tff.Wr.TexFileUtils.formatEntrytext(createPrettySubSection(subsection))
        subsectionImgPath = os.path.join(secreenshotPath, filename)
        tff.Wr.TexFileUtils.fromTexToImage(tex, subsectionImgPath, padding = 10, imageColor = "#4287f5")

        # top section image
        filename = "_top_" + fromSubSectionToFileID(topSection) + ".png"
        tex = tff.Wr.TexFileUtils.formatEntrytext(createPrettyTopSection(topSection))
        topsSctionImgPath = os.path.join(topSectionPath, filename)
        tff.Wr.TexFileUtils.fromTexToImage(tex, topsSctionImgPath, padding = 20, imageColor = "#ed8a82")

        # rebuild web links
        imGlLinkDict = cls.readProperty(subsection, cls.PubProp.imGlobalLinksDict)
        for k, ld in imGlLinkDict.items():
            if ld != _u.Token.NotDef.str_t:
                for ln, lk in ld.items():
                    if "http" in lk:
                        latexTxt = tff.Wr.TexFileUtils.formatEntrytext(ln)
                        filename = "_" + fromSubAndEntryIdxToNameId(subsection, k + "_" + ln) + ".png"
                        linkImgPath = os.path.join(secreenshotPath, filename)
                        tff.Wr.TexFileUtils.fromTexToImage(latexTxt, linkImgPath)

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