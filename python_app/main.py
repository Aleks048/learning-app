import tkinter as tk

import file_system.file_system_manager as fsm
import layouts.layouts_manager as lm
import tex_file.tex_file_facade as tm
import UI.widgets_facade as wf
import data.temp as dt
import daemon_service.daemon_service as das

# start the daemon to process client calls
das.startMainServerDaemon()

# create startup menu
winRoot = tk.Tk()
winRoot.geometry("0x0")
wf.Wr.MenuManagers.StartupMenuManager.createMenu(winRoot)
