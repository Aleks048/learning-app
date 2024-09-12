import UI.widgets_collection.entryNotes.entryNotes as enow

import UI.widgets_manager as wm
import file_system.file_system_facade as fsf
import settings.facade as sf
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import outside_calls.outside_calls_facade as ocf


class LayoutManagers:

    class EntryNotesLayout(wm.MenuLayout_Interface):
        prefix = "_EntryNotesLayout_"
        subsection = _u.Token.NotDef.str_t
        imIdx = _u.Token.NotDef.str_t

        def __init__(self, winRoot):
            appDimensions = [750, 800, 300, 0]
            super().__init__(winRoot, appDimensions)
            self.entryNotes_BOX = enow.Notes_BOX(winRoot, self.prefix)
            self.addWidget(self.entryNotes_BOX)
            self.hideNotesWindow_BTN = enow.HideEntryNotesWindow_BTN(winRoot, self.prefix)
            self.addWidget(self.hideNotesWindow_BTN)

            winRoot.setGeometry(*self.appDimensions)
        def show(self):
            self.hideNotesWindow_BTN.subsection = self.subsection
            self.hideNotesWindow_BTN.imIdx = self.imIdx

            self.entryNotes_BOX.subsection = self.subsection
            self.entryNotes_BOX.imIdx = self.imIdx

            super().show()

            self.entryNotes_BOX.scrollable_frame.focus_force()

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class EntryNotesManager(wm.MenuManager_Interface):
    imIdx = 0
    shown = False
    def __init__(self):

        winRoot = enow.EntryNotesRoot(50, 50)
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