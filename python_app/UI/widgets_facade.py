import UI.widgets_collection.startup.manager as sm
import UI.widgets_collection.main.math.manager as mm
import UI.widgets_collection.message.manager as mesm
import UI.widgets_collection.toc.manager as tocm
import UI.widgets_collection.excercise.manager as exm
import UI.widgets_collection.proofs.manager as prm
import UI.widgets_wrappers as ww
import UI.widgets_manager as wm


class Wr:
    class MenuManagers:
        class UI_GeneralManager(wm.UI_generalManager):
            pass

        class MathMenuManager(mm.MathMenuManager):
            pass
        
        class StartupMenuManager(sm.StartupMenuManager):
            pass

        class MessageMenuManager(mesm.MessageMenuManager):
            pass
        class TOCManager(tocm.TOCManager):
            pass

        class ExcerciseManager(exm.ExcerciseManager):
            pass

        class ProofsManager(prm.ProofsManager):
            pass
    
    class UI_generalManager(wm.UI_generalManager):
        pass

    class WidgetWrappers(ww.currUIImpl):
        pass