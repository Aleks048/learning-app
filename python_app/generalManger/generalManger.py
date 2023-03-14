import file_system.file_system_facade as fsf
import settings.facade as sf
import _utils.logging as log

import data.constants as dc
import data.temp as dt
import UI.widgets_facade as uif

import layouts.layouts_manager as lm


class GeneralManger:
    def AddNewBook(bookName, bookPath, 
                   originalMaterialLocation, originalMaterialRelPath,
                   originalMaterialName):
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

        # update settings
        sf.Wr.Manager.Book.addNewBook(bookName, bookPath)