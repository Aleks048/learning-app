import UI.widgets_collection.image.image as imw

import UI.widgets_manager as wm
import file_system.file_system_facade as fsf
import settings.facade as sf
import _utils._utils_main as _u


class LayoutManagers:
    class ImagesLayout(wm.MenuLayout_Interface):
        def __init__(self, winRoot):
            self.prefix = "_ImagesLayout_"
            self.subsection = _u.Token.NotDef.str_t
            self.imIdx = _u.Token.NotDef.str_t
            self.extraImIdx = _u.Token.NotDef.int_t

            appDimensions = [720, 800, 0, 0]
            super().__init__(winRoot, appDimensions)
            self.imageMainImage = imw.ImageMainImage(winRoot, self.prefix)
            self.addWidget(self.imageMainImage)
            self.hideImagesWindow_BTN = imw.HideImagesWindow_BTN(winRoot, self.prefix)
            self.addWidget(self.hideImagesWindow_BTN)
            self.moveTOCtoImageEntry_BTN = imw.MoveTOCtoImageEntry_BTN(winRoot, self.prefix)
            self.addWidget(self.moveTOCtoImageEntry_BTN)
            self.notesLabel = imw.NotesLabel(winRoot, self.prefix)
            self.addWidget(self.notesLabel)

            winRoot.setGeometry(*self.appDimensions)

        def show(self):
            self.imageMainImage.subsection = self.subsection
            self.imageMainImage.entryIdx = self.imIdx
            self.imageMainImage.extraWidgetIdx = self.extraImIdx

            self.hideImagesWindow_BTN.subsection = self.subsection
            self.hideImagesWindow_BTN.imIdx = self.imIdx

            self.moveTOCtoImageEntry_BTN.subsection = self.subsection
            self.moveTOCtoImageEntry_BTN.imIdx = self.imIdx

            self.notesLabel.subsection = self.subsection
            self.notesLabel.imIdx = self.imIdx
            self.notesLabel.eImIdx = self.extraImIdx

            super().show()

            # resize the solution box in respect to the size of the main image
            self.imageMainImage.widgetObj.update()

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class ImagesManager(wm.MenuManager_Interface):
    imIdx = 0
    appDimensions = None
    notesImDimensions = None

    def __init__(self):
        winRoot = imw.ImagesRoot(50, 50)
        layouts = []
        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))
            
        self.subsection = fsf.Data.Book.currSection
        currLayout = layouts[0]
        currLayout.subsection = self.subsection
        
        super().__init__(winRoot,
                        layouts,
                        currLayout)
    def show(self, appDimensions, extraImIdx, notesImDimensions = 0):
        self.winRoot.hideWidget = self.layouts[0].hideImagesWindow_BTN

        self.layouts[0].subsection = self.subsection
        self.layouts[0].imIdx = self.imIdx
        self.layouts[0].appDimensions = appDimensions
        self.appDimensions = appDimensions
        self.notesImDimensions = notesImDimensions
        self.layouts[0].extraImIdx = extraImIdx
        return super().show()
