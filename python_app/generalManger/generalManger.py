import file_system.file_system_facade as fsf
import settings.facade as sf
import _utils.logging as log

import data.constants as dc
import data.temp as dt
import UI.widgets_facade as uif


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
    
    # class Layouts(dc.AppCurrDataAccessToken):
    #     appCurrDataAccessToken = super().appCurrDataAccessToken
    #     @classmethod
    #     def stopStartupStartMain(cls):
    #         # hide startup UI layout
    #         startupManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
    #                                                         uif.Wr.MenuManagers.StartupMenuManager)
    #         startupManager.hide()
            
    #         # show 3rd party main layout
    #         lm.Wr.MainLayout.set()

    #         # show UI main layout
    #         mainMathManager = dt.AppState.UIManagers.getData(cls.appCurrDataAccessToken,
    #                                                         uif.Wr.MenuManagers.MainMenuManager)
    #         mainMathManager.show()