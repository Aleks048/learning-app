import UI.widgets_collection.excerciseExtra.excerciseExtra as esln

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

            appDimensions = [720, 800, 720, 0]
            super().__init__(winRoot, appDimensions)
            self.hideExcerciseExtraWindow_BTN = \
                esln.HideExcerciseExtraWindow_BTN(winRoot, self.prefix)
            self.addWidget(self.hideExcerciseExtraWindow_BTN)
            self.excerciseExtraLabel = \
                esln.ExcerciseExtraLabel(winRoot, self.prefix)
            self.addWidget(self.excerciseExtraLabel)

            self.addFromClipbordExcerciseExtraWindow_BTN = \
                esln.AddFromClipbordExcerciseExtraWindow_BTN(winRoot, self.prefix)
            self.addWidget(self.addFromClipbordExcerciseExtraWindow_BTN)
            self.addFromClipbordExcerciseExtraWindow_BTN.addListenerWidget(self.excerciseExtraLabel)

            self.addScreenshotExcerciseExtraWindow_BTN = \
                esln.AddScreenshotExcerciseExtraWindow_BTN(winRoot, self.prefix)
            self.addWidget(self.addScreenshotExcerciseExtraWindow_BTN)
            self.addScreenshotExcerciseExtraWindow_BTN.addListenerWidget(self.excerciseExtraLabel)

            winRoot.setGeometry(*self.appDimensions)

        def show(self):
            self.excerciseExtraLabel.subsection = self.subsection
            self.excerciseExtraLabel.imIdx = self.imIdx
            self.addFromClipbordExcerciseExtraWindow_BTN.subsection = self.subsection
            self.addFromClipbordExcerciseExtraWindow_BTN.imIdx = self.imIdx
            self.addScreenshotExcerciseExtraWindow_BTN.subsection = self.subsection
            self.addScreenshotExcerciseExtraWindow_BTN.imIdx = self.imIdx

            super().show()

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class ExcerciseExtraManager(wm.MenuManager_Interface):
    imIdx = 0
    def __init__(self):
        winRoot = esln.ExcerciseExtraRoot(50, 50)
        layouts = []
        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))
            
        self.subsection = fsf.Data.Book.currSection
        currLayout = layouts[0]
        currLayout.subsection = self.subsection
        
        super().__init__(winRoot,
                        layouts,
                        currLayout)
    def show(self, subsection, imIdx):
        self.layouts[0].subsection = subsection
        self.layouts[0].imIdx = imIdx
        return super().show()