import UI.widgets_collection.notes.notes as now

import UI.widgets_manager as wm
import file_system.file_system_facade as fsf
import settings.facade as sf
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import outside_calls.outside_calls_facade as ocf


class LayoutManagers:

    class NotesLayout(wm.MenuLayout_Interface):
        prefix = "_NotesLayout_"
        subsection = _u.Token.NotDef.str_t
        imIdx = _u.Token.NotDef.str_t

        def __init__(self, winRoot):
            appDimensions = [750, 800, 300, 0]
            super().__init__(winRoot, appDimensions)
            self.dict_BOX = now.Dict_BOX(winRoot, self.prefix)
            self.addWidget(self.dict_BOX)
            self.hideNotesWindow_BTN = now.HideNotesWindow_BTN(winRoot, self.prefix)
            self.addWidget(self.hideNotesWindow_BTN)
            self.addDictHitToEntry_BTN = now.AddDictHitToEntry_BTN(winRoot, self.prefix)
            self.addWidget(self.addDictHitToEntry_BTN)
            searchDict_ETR = now.SearchDict_ETR(winRoot, self.prefix)
            self.addWidget(searchDict_ETR)
            self.dictText_LBL = now.DictText_LBL(winRoot, self.prefix)
            self.addWidget(self.dictText_LBL)

            searchDict_ETR.addListenerWidget(self.dict_BOX)
            self.addDictHitToEntry_BTN.addListenerWidget(searchDict_ETR)
            self.addDictHitToEntry_BTN.addListenerWidget(self.dictText_LBL)
            self.dictText_LBL.addListenerWidget(self.dict_BOX)

            self.moveTOCtoNotesEntry_BTN = now.MoveTOCtoNotesEntry_BTN(winRoot, self.prefix)
            self.addWidget(self.moveTOCtoNotesEntry_BTN)

            winRoot.setGeometry(*self.appDimensions)
        def show(self):
            self.hideNotesWindow_BTN.subsection = self.subsection
            self.hideNotesWindow_BTN.imIdx = self.imIdx

            self.addDictHitToEntry_BTN.subsection = self.subsection
            self.addDictHitToEntry_BTN.imIdx = self.imIdx

            self.dictText_LBL.subsection = self.subsection
            self.dictText_LBL.imIdx = self.imIdx

            self.moveTOCtoNotesEntry_BTN.subsection = self.subsection
            self.moveTOCtoNotesEntry_BTN.imIdx = self.imIdx


            self.dict_BOX.subsection = self.subsection
            self.dict_BOX.imIdx = self.imIdx

            super().show()

            self.dict_BOX.forceFocus()

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class NotesManager(wm.MenuManager_Interface):
    imIdx = 0
    shown = False
    def __init__(self):

        winRoot = now.NotesRoot(50, 50)
        layouts = []
        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))
            
        self.subsection = fsf.Data.Book.currSection
        currLayout = layouts[0]
        currLayout.subsection = self.subsection
        
        super().__init__(winRoot,
                        layouts,
                        currLayout)
    def show(self):
        self.layouts[0].subsection = self.subsection
        self.layouts[0].imIdx = self.imIdx
        self.shown = True

        return super().show()
    
    def hide(self):
        self.shown = False

        return super().hide()