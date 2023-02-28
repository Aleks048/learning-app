import UI.widgets_collection.startup.manager as sm
import UI.widgets_collection.main.manager as mm
import UI.widgets_collection.message.manager as mesm

class Wr:
    class MenuManagers:
        class MainMenuManager(mm.MainMenuManager):
            pass
        
        class StartupMenuManager(sm.StartupMenuManager):
            pass

        class MessageMenuManager(mesm.MessageMenuManager):
            pass

        