import tkinter as tk
import os

import UI.widgets_vars as wv

import file_system.file_system_manager as fsm
import layouts.layouts_manager as lm

import _utils._utils_main as _u
import _utils.logging as log

class Data:
    class ENT:
        entryWidget_ID = "ETR"

        regularTextColor = "white"
        defaultTextColor = "blue"
    class BTN:
        buttonWidget_ID = "BTN"
