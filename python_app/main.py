
import file_system.file_system_facade as fsm
import layouts.layouts_manager as lm
import tex_file.tex_file_facade as tm
import UI.widgets_facade as wf
import data.temp as dt
import daemon_service.daemon_service as das

import _utils.logging as log

# start the daemon to process client calls
das.startMainServerDaemon()

# create startup menu
messageMenuManager = wf.Wr.MenuManagers.MessageMenuManager()
mainMenuManager = wf.Wr.MenuManagers.MainMenuManager()
startupMenuManager = wf.Wr.MenuManagers.StartupMenuManager()
startupMenuManager.showOnly()

wf.Wr.WidgetWrappers.startLoop()

