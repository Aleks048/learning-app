import tkinter as tk

import UI.widgets_manager as wm
import UI.widgets_utils as wu
import UI.widgets_collection.main.math.manager as mathm

class MainMenuManager(wm.MenuManager_Interface):
    currSubmanager = mathm.MathMenuManager
    @classmethod
    def createMenu(cls):
        cls.currSubmanager.createMenu()

    @classmethod
    def _bindKeys(cls):
        cls.currSubmanager.createMenu()