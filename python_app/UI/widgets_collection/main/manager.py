import UI.widgets_manager as wm
import UI.widgets_collection.main.math.manager as mathm

class MathMenuManager(wm.MenuManager_Interface):
    currSubmanager = mathm.MathMenuManager
    @classmethod
    def createMenu(cls):
        cls.currSubmanager.createMenu()

    @classmethod
    def _bindKeys(cls):
        cls.currSubmanager.createMenu()