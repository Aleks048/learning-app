import file_system.file_system_facade as fsf
import settings.facade as sf
import _utils.logging as log


class GeneralManger:
    def AddNewBook(bookName, bookPath, originalMaterialLocation, originalMaterialRelPath):
        # create filesystem
        addedNewbook = fsf.Wr.FileSystemManager.addNewBook(bookName, bookPath)
        if not addedNewbook:
            message = "Could not create book at filepath" + bookPath
            log.autolog(message)
            return 

        # add original material
        fsf.Wr.FileSystemManager.addOriginalMaterial(originalMaterialLocation, 
                                                    originalMaterialRelPath)

        # update settings
        sf.Wr.Manager.Book.addNewBook(bookName, bookPath)