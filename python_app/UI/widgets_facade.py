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

import UI.widgets_collection.imageCreation as icw
import UI.widgets_manager as wm

class Data:
    UItkVariables = wv.UItkVariables


class Wr:
    class ConfirmationMenu(wmes.ConfirmationMenu):
        pass
    
    class MessageMenu(wmes.MessageMenu):
        pass

    class ImageCreationWidgets(icw.ImageCreation):

        class AddExtraImage_BTN(icw.AddExtraImage_BTN):
            pass
        
        class ImageGenerationRestart_BTN(icw.ImageGenerationRestart_BTN):
            pass
    
    class MenuManagers:
        class MainMenuManager(wm.MainMenuManager):
            pass
        
        class StartupMenuManager(wm.StartupMenuManager):
            pass

        