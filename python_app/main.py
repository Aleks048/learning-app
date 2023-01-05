import tkinter as tk

import file_system.file_system_manager as fsm
import layouts.layouts_manager as lm
import tex_file.tex_file_manager as tm
import UI.widgets_manager as wm
import data.temp as dt

winRoot = tk.Tk()
winRoot.geometry("0x0")
wm.StartupMenu.createMenu(winRoot)