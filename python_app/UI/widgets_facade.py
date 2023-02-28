import UI.widgets_collection.startup.manager as sm
import UI.widgets_collection.main.math.manager as mm
import UI.widgets_collection.message.manager as mesm
import UI.widgets_wrappers as ww


class Wr:
    class MenuManagers:
        class MainMenuManager(mm.MathMenuManager):
            pass
        
        class StartupMenuManager(sm.StartupMenuManager):
            pass

        class MessageMenuManager(mesm.MessageMenuManager):
            pass
    
    class WidgetWrappers(ww.currUIImpl):
        pass