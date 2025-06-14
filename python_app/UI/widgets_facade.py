import UI.widgets_collection.startup.manager as sm
import UI.widgets_collection.main.math.manager as mm
import UI.widgets_collection.mainTOC.manager as mtocm
import UI.widgets_collection.mainEntry.manager as mem
import UI.widgets_collection.message.manager as mesm
import UI.widgets_collection.toc.manager as tocm
import UI.widgets_collection.excercise.manager as exm
import UI.widgets_collection.notes.manager as nom
import UI.widgets_collection.entryNotes.manager as enom
import UI.widgets_collection.proofs.manager as prm
import UI.widgets_collection.image.manager as imm
import UI.widgets_collection.pdfReader.manager as pdfrm
import UI.widgets_collection.excerciseLineNote.manager as enm
import UI.widgets_collection.excerciseSolution.manager as eslnm
import UI.widgets_collection.excerciseExtra.manager as eextm
import UI.widgets_wrappers as ww
import UI.widgets_manager as wm


class Wr:
    class MenuManagers:
        class UI_GeneralManager(wm.UI_generalManager):
            pass

        class MathMenuManager(mm.MathMenuManager):
            pass

        class MainTOCManager(mtocm.MainTOCManager):
            pass

        class MainEntryManager(mem.MainEntryMenuManager):
            pass
        
        class StartupMenuManager(sm.StartupMenuManager):
            pass

        class MessageMenuManager(mesm.MessageMenuManager):
            pass
        class TOCManager(tocm.TOCManager):
            pass

        class ExcerciseManager(exm.ExcerciseManager):
            pass

        class NotesManager(nom.NotesManager):
            pass

        class EntryNotesManager(enom.EntryNotesManager):
            pass

        class ProofsManager(prm.ProofsManager):
            pass

        class ImagesManager(imm.ImagesManager):
            pass

        class PdfReadersManager(pdfrm.PdfReadersManager):
            pass

        class ExcerciseLineNoteManager(enm.ExcerciseLineNoteManager):
            pass

        class ExcerciseSolutionManager(eslnm.ExcerciseSolutionManager):
            pass

        class ExcerciseExtraManager(eextm.ExcerciseExtraManager):
            pass

    
    class UI_generalManager(wm.UI_generalManager):
        pass

    class WidgetWrappers(ww.currUIImpl):
        pass