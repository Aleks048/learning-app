import UI.widgets_collection.excerciseLineNote.excerciseLineNote as enw

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
            self.lineIdx = _u.Token.NotDef.int_t

            appDimensions = [720, 400, 720, 0]
            super().__init__(winRoot, appDimensions)
            self.excerciseLineNoteLineImage = \
                enw.ExcerciseLineNoteLineImage(winRoot, self.prefix)
            self.addWidget(self.excerciseLineNoteLineImage)
            self.hideExcerciseLineNoteWindow_BTN = \
                enw.HideExcerciseLineNoteWindow_BTN(winRoot, self.prefix)
            self.addWidget(self.hideExcerciseLineNoteWindow_BTN)
            self.excerciseLineNoteLabel = \
                enw.ExcerciseLineNoteLabel(winRoot, self.prefix)
            self.addWidget(self.excerciseLineNoteLabel)

            winRoot.setGeometry(*self.appDimensions)

        def show(self):
            self.excerciseLineNoteLineImage.subsection = self.subsection
            self.excerciseLineNoteLineImage.imIdx = self.imIdx
            self.excerciseLineNoteLineImage.lineIdx = self.lineIdx

            self.excerciseLineNoteLabel.subsection = self.subsection
            self.excerciseLineNoteLabel.imIdx = self.imIdx
            self.excerciseLineNoteLabel.lineIdx = self.lineIdx

            super().show()

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class ExcerciseLineNoteManager(wm.MenuManager_Interface):
    imIdx = 0
    def __init__(self):
        winRoot = enw.ExcerciseLineNoteRoot(50, 50)
        layouts = []
        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))
            
        self.subsection = fsf.Data.Book.currSection
        currLayout = layouts[0]
        currLayout.subsection = self.subsection
        
        super().__init__(winRoot,
                        layouts,
                        currLayout)
    def show(self, subsection, imIdx, lineIdx):
        self.layouts[0].subsection = subsection
        self.layouts[0].imIdx = imIdx
        self.layouts[0].lineIdx = lineIdx
        return super().show()