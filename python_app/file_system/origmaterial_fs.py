import os
import subprocess
import math

import _utils._utils_main as _u
import _utils.logging as log
import file_system.book_fs as bfs
import _utils.pathsAndNames as _upan

import outside_calls.outside_calls_facade as ocf
import settings.facade as sf
import scripts.osascripts as oscr

class OriginalMaterialStructure:
    '''
    Structure to store the original pdf and other required material.
    '''

    originalMaterialBaseRelPath = "originalMaterial/"

    
    class PubProp:
        materials = "materials"

        # book props
        path = "Path"
        currPage = "CurrPage"
        noteSize = "NoteSize"
        pageSize = "PageSize"
        zoomLevel = "ZoomLevel"
        pagesToBeAdded = "PagesToBeAdded"
        figures = "_figures"

        # toc page
        tocPage = "TocPage"

    bookTemplate = {
        PubProp.path : _u.Token.NotDef.str_t,
        PubProp.currPage : _u.Token.NotDef.str_t,
        PubProp.tocPage : _u.Token.NotDef.str_t,
        PubProp.noteSize : _u.Token.NotDef.list_t.copy(),
        PubProp.pageSize : _u.Token.NotDef.list_t.copy(),
        PubProp.zoomLevel : 700,
        PubProp.pagesToBeAdded : _u.Token.NotDef.str_t,
        PubProp.figures : _u.Token.NotDef.dict_t,
    }

    template = {
        PubProp.materials: {
        }
    }

    @classmethod
    def createStructure(cls):
        origMatAbsPath_curr = _upan.Paths.OriginalMaterial.getAbs()
        
        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(origMatAbsPath_curr):   
            log.autolog("The OM structure was not present. Will create it.\nCreating path: '{0}'".format(origMatAbsPath_curr))
            ocf.Wr.FsAppCalls.createDir(origMatAbsPath_curr)
        
        # create file to track original materials with names and paths
        structureFile = cls.__getJSONfilepath()
        # ocf.Wr.FsAppCalls.createDir(structureFile)
        _u.JSON.createFromTemplate(structureFile, cls.template)
    
    @classmethod
    def addOriginalMaterial(cls, filePath, structureRelPath, materialName):
        log.autolog("Adding material: '{0}' to rel path: '{1}'".format(filePath, structureRelPath))

        bookFilepath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        OM_basePath = _upan.Paths.OriginalMaterial.getAbs(bookFilepath)

        originnalMaterialDestinationPath = os.path.join(OM_basePath, structureRelPath)

        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(originnalMaterialDestinationPath):   
            log.autolog("Path '{0}' does not exist. Will create it.".format(originnalMaterialDestinationPath))
            createdFile = ocf.Wr.FsAppCalls.createDir(originnalMaterialDestinationPath)
            if not createdFile:
                return False
        
        # update curr material let path
        bfs.BookInfoStructure.updateProperty(bfs.BookInfoStructure.PubProp.currOrigMatName,
                                            materialName)
        
        # update data structure to keep the dict of books and paths to them
        origMatFilename = cls.__fromMatPathToFilename(filePath)
        cls.setMaterialPath(materialName, os.path.join(structureRelPath, origMatFilename))
        cls.setMaterialCurrPage(materialName, "1")

        # set noteSize
        cls.setNoteSize(materialName, [300, 20])
        cls.setMaterialPageSize(materialName, [-1, -1])
        cls.setTOCPage(materialName, _u.Token.NotDef.str_t)
        cls.setZoomLevel(materialName, "100")
        
        log.autolog("Copying file '{0}' to '{1}'".format(filePath, originnalMaterialDestinationPath))
        ocf.Wr.FsAppCalls.copyFile(filePath, originnalMaterialDestinationPath)

    @classmethod
    def addNoteToOriginalMaterial(cls, omName, page, noteText, idx):
        return
        idx = int(idx) - 1

        leftPad = 20

        noteSize:list = cls.getMaterialNoteSize(omName)
        nWidth = int(noteSize[0])
        nHeight = int(noteSize[1])
        pageSize = cls.getMaterialPageSize(omName)
        pWidth = int(pageSize[0])
        pHeight = int(pageSize[1])

        numCols = (pWidth - leftPad) // nWidth
        # NOTE: we hardwire 5 rows of notes per page
        numRowsBorttom = 5

        col = idx % numCols
        row = idx // numCols
        leftW = col * nWidth + leftPad
        rightW = (col + 1) * nWidth + leftPad

        if row < 2:
            bounds = [leftW,
                        pHeight - row * nHeight,
                        rightW,
                        pHeight - (row + 1) * nHeight,
                        ]
        else:
            bounds = [leftW,
                        (numRowsBorttom - row) * nHeight,
                        rightW,
                        (numRowsBorttom - row - 1) * nHeight,
                        ]

        filepath = cls.getMaterialPath(omName)
        fileName = cls.__fromMatPathToFilename(filepath)

        cmd = oscr.addNoteTheToThePage(fileName, page, noteText, bounds)
        _u.runCmdAndWait(cmd)

    @classmethod
    def getOriginalMaterialsNames(cls):
        origMatDict = cls.__getMaterailsDict()
        return list(origMatDict.keys())
    
    @classmethod
    def getOriginalMaterialsFilename(cls, matName):
        matPath = cls.getMaterialPath(matName)

        return cls.__fromMatPathToFilename(matPath).replace(".pdf", "")
    
    def __fromMatPathToFilename(matPath):
        matName = matPath.split("/")[-1]
        return matName

    @classmethod
    def getMaterialPath(cls, OMName):
        books = cls.__getMaterailsDict()
        try:
            basePath_curr =  _upan.Paths.OriginalMaterial.getAbs()
            relPath =  books[OMName][OriginalMaterialStructure.PubProp.path]
            return os.path.join(basePath_curr, relPath)
        except:
            log.autolog("No OM with name '{0}'".format(OMName))
            return None
    
    @classmethod
    def getMaterialTOCPage(cls, OMName):
        books = cls.__getMaterailsDict()
        try:
            return books[OMName][OriginalMaterialStructure.PubProp.tocPage]
        except:
            log.autolog("No OM with name '{0}'".format(OMName))
            return None

    @classmethod
    def getMaterialZoomLevel(cls, OMName):
        books = cls.__getMaterailsDict()
        try:
            return books[OMName][OriginalMaterialStructure.PubProp.zoomLevel]
        except:
            log.autolog("No OM with name '{0}'".format(OMName))
            return None
    
    @classmethod
    def getMaterialPageFigures(cls, omName, page):
        books = cls.__getMaterailsDict()

        materialData = books[omName]

        if materialData.get(OriginalMaterialStructure.PubProp.figures) == \
            _u.Token.NotDef.dict_t:
            return {}

        if materialData.get(OriginalMaterialStructure.PubProp.figures) != None:
            figures = books[omName][OriginalMaterialStructure.PubProp.figures]

            if figures.get(str(page)) != None:
                return figures[str(page)]

        return {}

    @classmethod
    def getMaterialNoteSize(cls, omName):
        books = cls.__getMaterailsDict()
        try:
            return books[omName][OriginalMaterialStructure.PubProp.noteSize]
        except:
            log.autolog("No OM with name '{0}'".format(omName))
            return None

    @classmethod
    def getMaterialPagesToBeAdded(cls, omName):
        books = cls.__getMaterailsDict()
        try:
            return books[omName][OriginalMaterialStructure.PubProp.pagesToBeAdded]
        except:
            log.autolog("No OM with name '{0}'".format(omName))
            return None

    @classmethod
    def getMaterialPageSize(cls, OMName):
        books = cls.__getMaterailsDict()
        try:
            return books[OMName][OriginalMaterialStructure.PubProp.pageSize]
        except:
            log.autolog("No OM with name '{0}'".format(OMName))
            return None
    
    @classmethod
    def getMaterialCurrPage(cls, bookName):
        books = cls.__getMaterailsDict()
        
        try:
            return books[bookName][OriginalMaterialStructure.PubProp.currPage]
        except:
            log.autolog("No OM with name '{0}'".format(bookName))
            return None
    
    @classmethod
    def updateOriginalMaterialPage(cls, matName, newPage = None):
        if newPage != None:
            cls.setMaterialCurrPage(matName, newPage)
            return

        materialFilename = cls.getOriginalMaterialsFilename(matName)
        # update the currPage for original material
        cmd = oscr.get_PageOfSkimDoc_CMD(materialFilename)
        frontSkimDocumentPage, _ = _u.runCmdAndGetResult(cmd)

        # NOTE: this is needed to not update the page when 
        # the pdf doc is still not opened.
        if len(frontSkimDocumentPage.split("page ")) < 2:
            return
        
        if frontSkimDocumentPage != None:
            page = frontSkimDocumentPage.split("page ")[1]
            page = page.split(" ")[0]
            cls.setMaterialCurrPage(matName, page)

    @classmethod
    def setMaterialPageSize(cls, materialName, pageSize = None):
        if pageSize == None:
            filepath = cls.getMaterialPath(materialName)
            origMatFilename = cls.__fromMatPathToFilename(filepath)

            # set the page size
            cmd = oscr.get_BoundsOfThePage(origMatFilename)
            firstPageSize, _ = _u.runCmdAndGetResult(cmd)
            firstPageSize = firstPageSize.replace("\n", "").split(", ")
            cls.setMaterialPageSize(materialName, [firstPageSize[2], firstPageSize[1]])
            return

        materials = cls.__getMaterailsDict() 

        if materialName not in materials.keys():
            materials[materialName] = {}

        materials[materialName][OriginalMaterialStructure.PubProp.pageSize] = pageSize
        cls.__updateMaterialDict(materials)

    @classmethod
    def setMaterialPageFigures(cls, materialName, page, pageFigures):
        materials = cls.__getMaterailsDict()

        materialData = materials[materialName]

        if materialData.get(OriginalMaterialStructure.PubProp.figures) != None:
            figures = materialData[OriginalMaterialStructure.PubProp.figures]
        else:
            materialData[OriginalMaterialStructure.PubProp.figures] = _u.Token.NotDef.dict_t.copy()
            figures = _u.Token.NotDef.dict_t.copy()

        figures[str(page)] = pageFigures
        materialData[OriginalMaterialStructure.PubProp.figures] = figures

        cls.__updateMaterialDict(materials)

    @classmethod
    def setMaterialPath(cls, materialName, materialPath):
        materials = cls.__getMaterailsDict() 

        if materialName not in materials.keys():
            materials[materialName] = {}
        
        materials[materialName][OriginalMaterialStructure.PubProp.path] = materialPath
        cls.__updateMaterialDict(materials)
    
    @classmethod
    def setTOCPage(cls, materialName, tocPage):
        materials = cls.__getMaterailsDict() 

        if materialName not in materials.keys():
            materials[materialName] = {}
        
        materials[materialName][OriginalMaterialStructure.PubProp.tocPage] = tocPage
        cls.__updateMaterialDict(materials)

    @classmethod
    def setZoomLevel(cls, materialName, zoomLevel):
        materials = cls.__getMaterailsDict() 

        if materialName not in materials.keys():
            materials[materialName] = {}
        
        materials[materialName][OriginalMaterialStructure.PubProp.zoomLevel] = zoomLevel
        cls.__updateMaterialDict(materials)
    
    @classmethod
    def setNoteSize(cls, materialName, noteSize):
        materials = cls.__getMaterailsDict() 

        if materialName not in materials.keys():
            materials[materialName] = {}
        
        materials[materialName][OriginalMaterialStructure.PubProp.noteSize] = noteSize
        cls.__updateMaterialDict(materials)
    
    @classmethod
    def setMaterialCurrPage(cls, materialName, currPage):
        materials = cls.__getMaterailsDict()

        if materialName not in materials.keys():
            materials[materialName] = {}
        
        materials[materialName][OriginalMaterialStructure.PubProp.currPage] = currPage
        cls.__updateMaterialDict(materials)
        
    @classmethod
    def __getJSONfilepath(cls) -> str:
        origMatAbsPath_curr = _upan.Paths.OriginalMaterial.getAbs()
        # create file to track original materials with names and paths
        return os.path.join(origMatAbsPath_curr, "origMat.json")
    
    @classmethod
    def __updateMaterialDict(cls, newMatDict):
        jsonFilepath = cls.__getJSONfilepath()
        _u.JSON.updateProperty(jsonFilepath, 
                               OriginalMaterialStructure.PubProp.materials,
                               newMatDict)
    
    @classmethod
    def __getMaterailsDict(cls) -> dict:
        jsonFilepath = cls.__getJSONfilepath()
        
        materialsDict = _u.JSON.readProperty(jsonFilepath,
                                    cls.PubProp.materials)
        if materialsDict == None:
            return _u.Token.NotDef.dict_t.copy()
        else:
            return materialsDict