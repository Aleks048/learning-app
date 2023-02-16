import os
import tkinter as tk
import threading

import UI.widgets_collection_old as wc
import UI.widgets_utils as wu
import UI.widgets_vars as wv
import UI.widgets_messages as wmes

import layouts.layouts_manager as lm

import file_system.file_system_manager as fsm

import _utils.logging as log
import _utils._utils_main as _u

import UI.widgets_collection.startup.manager as sm
# import UI.widgets_collection.layouts.mathLayouts.manager as wm

class Data:
    UItkVariables = wv.UItkVariables


class Wr:
    class ConfirmationMenu(wmes.ConfirmationMenu):
        pass
    
    class MessageMenu(wmes.MessageMenu):
        pass
    class MenuManagers:
        # class MainMenuManager(wm.MainMenuManager):
        #     pass
        
        class StartupMenuManager(sm.StartupMenuManager):
            pass

        