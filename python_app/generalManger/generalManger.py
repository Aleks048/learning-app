import os

import file_system.file_system_facade as fsf
import settings.facade as sf
import _utils.logging as log
import tex_file.tex_file_facade as tff
import _utils.pathsAndNames as _upan

import data.constants as dc
import data.temp as dt

import outside_calls.outside_calls_facade as ocf
import UI.widgets_collection.message.manager as mesm
import UI.widgets_collection.main.math.manager as mmm


class GeneralManger(dc.AppCurrDataAccessToken):
    def AddNewBook(bookName, bookPath, 
                   originalMaterialLocation, originalMaterialRelPath,
                   originalMaterialName):
        # update settings
        sf.Wr.Manager.Book.addNewBook(bookName, bookPath)
        
        # create filesystem
        addedNewbook = fsf.Wr.FileSystemManager.addNewBook(bookName, bookPath)        
        if not addedNewbook:
            message = "Could not create book at filepath" + bookPath
            log.autolog(message)
            return 

        # add original material   
        fsf.Wr.FileSystemManager.addOriginalMaterial(originalMaterialLocation, 
                                                    originalMaterialRelPath,
                                                    originalMaterialName)
    
    @classmethod
    def AddEntry(cls, subsection, imIdx:str, imText:str, addToTOC:bool, addToTOCwIm:bool):
        imagePath_curr = os.path.join(_upan.Paths.Screenshot.getAbs(),
                                    _upan.Names.getImageName(str(imIdx), subsection))
        
        imID = imIdx
        linkDict = fsf.Data.Sec.imLinkDict(subsection)
        
        if (imID in list(linkDict.values())):
            messManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
                                                        mesm.MessageMenuManager)
            mathManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
                                                        mmm.MathMenuManager)
            response = messManager.show("The index '{0}' already exists. Do you want to update?".format(imID), True)
            
            if response:
                names = []
                for name, id in linkDict.items():
                    if id == imID:
                        #remove the image
                        # prevImagePath_curr = os.path.join(_upan.Paths.Screenshot.getAbs(), str(imIdx) + "__" + currSubsection + "__" + name + ".png")
                        prevImagePath_curr = os.path.join(_upan.Paths.Screenshot.getAbs(),
                                        _upan.Names.getImageName(str(imIdx), subsection) + ".png")
                        ocf.Wr.FsAppCalls.deleteFile(prevImagePath_curr)

                        names.append(name)
                
                for name in names:
                    linkDict.pop(name, None)
                
                fsf.Data.Sec.imLinkDict(subsection, linkDict)
            
            mathManager.show()
            
            if not response:
                return False
        

        # ADD CONTENT ENTRY TO THE PROCESSED CHAPTER
        tff.Wr.TexFileModify.addProcessedImage(subsection, imIdx, imText)

        if addToTOC:
            if addToTOCwIm:
                # TOC ADD ENTRY WITH IMAGE
                tff.Wr.TexFileModify.addImageLinkToTOC_wImage(subsection, imIdx, imText)
            else:  
                # TOC ADD ENTRY WITHOUT IMAGE
                tff.Wr.TexFileModify.addImageLinkToTOC_woImage(subsection, imIdx, imText)
        

        # STOTE IMNUM, IMNAME AND LINK
        fsf.Wr.SectionCurrent.setImLinkAndIDX(imText, imIdx)
        
        # POPULATE THE MAIN FILE
        tff.Wr.TexFilePopulate.populateCurrMainFile()
        
        # take a screenshot
        if ocf.Wr.FsAppCalls.checkIfImageExists(imagePath_curr):
            mesManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken, 
                                                        mesm.MessageMenuManager)
            
            response = mesManager.show("The image with idx '{0}' already exists. Overrite", True)
            
            if response:
                ocf.Wr.ScreenshotCalls.takeScreenshot(imagePath_curr)
            else:
                return False
        else:
            ocf.Wr.ScreenshotCalls.takeScreenshot(imagePath_curr)
