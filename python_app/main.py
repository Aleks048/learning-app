from common_menus.m_main import *

#startof the application
screenHalfWidth, _ = getMonitorSize()
screenHalfWidth = str(int(screenHalfWidth / 2))
mainWin = createMainWindow([screenHalfWidth,0])
mainWin.mainloop()
