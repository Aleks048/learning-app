import tkinter as tk
import tkinter as Tk
import os
import vlc
from ctypes import c_void_p, cdll
import time

import UI.widgets_wrappers as ww
import UI.widgets_facade as wf
import data.temp as dt
import file_system.file_system_facade as fsf
import generalManger.generalManger as gm
import _utils.pathsAndNames as _upan
import _utils._utils_main as _u
import outside_calls.outside_calls_facade as osc

class VideoPlayerLabel(ww.currUIImpl.Frame):
    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0, "columnspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        self.subsection = None
        self.imIdx = None

        self.playing = False

        name = "_VideoPlayerLabel_FRM"
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data)

    def GetHandle(self):
        # Getting frame ID
        return self.canvas.winfo_id()
    
    def pause(self):
        if self.player.is_playing():
            self.playing = True
            self.play()

    def play(self, playPosition = None):
        self.rootWidget.widgetObj.title(f"Video for: {self.subsection}/{self.imIdx} at " + "{:.2f}".format(self.player.get_position()))
        if not self.playing:
            self.player.play()
            if playPosition != None:
                self.player.set_position(playPosition)
        else:
            self.player.pause()

        self.playing = not self.playing
    
    def scroll(self, numSeconds):
        secondAsPercentage = 1.0 / (float(self.player.get_length()) / 1000.0)
        self.player.set_position(self.player.get_position() + (numSeconds * secondAsPercentage))

    def getVideoPosition(self):
        return self.player.get_position()

    def render(self, **kwargs):
        if self.subsection != None:
            if self.playing:
                self.pause()

            # Creating VLC player
            self.instance = vlc.Instance()
            self.player = self.instance.media_player_new()

            #TODO: change to relevant path
            videoPath = _upan.Paths.Section.Video.getAbs(self.subsection)

            if not osc.Wr.FsAppCalls.checkIfFileOrDirExists(videoPath):
                _u.log.autolog(f"The file '{videoPath}' does not exist. Stop opening the menu.")
                return

            # Function to start player from given source
            self.media = self.instance.media_new(videoPath)
            self.media.get_mrl()
            self.player.set_media(self.media)

            # libtk = cdll.LoadLibrary(ctypes.util.find_library('tk'))
            # returns the tk library /usr/lib/libtk.dylib from macOS,
            # but we need the tkX.Y library bundled with Python 3+
            # and matching the version of tkinter, _tkinter, etc.
            libtk = 'libtk%s.dylib' % (Tk.TkVersion,)
            #NOTE: we keep the lib in the same dir as the python file
            libtk = os.path.join(os.path.dirname(os.path.realpath(__file__)), libtk)
            libtk = cdll.LoadLibrary(libtk)
            # getNSView = libtk.TkMacOSXDrawableView  # XXX not found?
            getNSView = libtk.TkMacOSXGetRootControl
            getNSView.restype = c_void_p
            getNSView.argtypes = c_void_p,
            self.player.set_nsobject(getNSView(self.widjetObj.winfo_id()))

            super().render(**kwargs)

            videoPositionDict:dict = fsf.Data.Sec.videoPosition(self.subsection)
            if videoPositionDict.get(self.imIdx) != None:
                self.play(videoPositionDict[self.imIdx])

                while not self.player.is_playing():
                    time.sleep(0.1)
                time.sleep(0.1)
                self.play()
            else:
                self.play()
                while not self.player.is_playing():
                    time.sleep(0.1)
                time.sleep(0.1)
                self.play()
                
            self.rootWidget.widjetObj.focus_force()

    def close(self):
        self.player.stop()
        self.media = None
        self.player = None
        self.widgetObj.grid_forget()
        self.widjetObj.grid_forget()

class VideoPlayerRoot(ww.currUIImpl.RootWidget):
    def __init__(self, width, height, bindCmd=...):
        self.videoFrame = None
        super().__init__(width, height, bindCmd= self.bindCmd)
        def __onClose(*args):
            self.videoFrame.close()
            self.widgetObj.destroy()

        self.widgetObj.protocol("WM_DELETE_WINDOW", lambda *args: __onClose())
        self.widgetObj.resizable(width=False, height=False)
        # self.rootWidget.widgetObj.overrideredirect(True)

    def bindCmd(self):
        def __startAddingEntry(*args):
            self.videoFrame.pause()
            mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.startAddingTheEntry()
        
        def __updatePosition(*args):
            videoPositionDict:dict = fsf.Data.Sec.videoPosition(self.videoFrame.subsection)
            videoPositionDict[self.videoFrame.imIdx] = self.videoFrame.getVideoPosition()
            fsf.Data.Sec.videoPosition(self.videoFrame.subsection, videoPositionDict)

        def __restart(*args):
            self.videoFrame.pause()
            self.videoFrame.play(0.0)

        def __bindAll(*args):
            self.widgetObj.bind_all(ww.currUIImpl.Data.BindID.Keys.shenter, lambda *args: __startAddingEntry())
            self.widgetObj.bind_all(ww.currUIImpl.Data.BindID.Keys.shspace, lambda *args: self.videoFrame.play())
            self.widgetObj.bind_all(ww.currUIImpl.Data.BindID.Keys.shleft, lambda *args: self.videoFrame.scroll(-5))
            self.widgetObj.bind_all(ww.currUIImpl.Data.BindID.Keys.shright, lambda *args: self.videoFrame.scroll(5))
            self.widgetObj.bind_all(ww.currUIImpl.Data.BindID.Keys.cmdu, lambda *args: __updatePosition(*args))
            self.widgetObj.bind_all(ww.currUIImpl.Data.BindID.Keys.cmdr, lambda *args: __restart(*args))

        def __unbindAll(*args):
            self.widgetObj.unbind_all(ww.currUIImpl.Data.BindID.Keys.shenter)
            self.widgetObj.unbind_all(ww.currUIImpl.Data.BindID.Keys.shspace)
            self.widgetObj.unbind_all(ww.currUIImpl.Data.BindID.Keys.shleft)
            self.widgetObj.unbind_all(ww.currUIImpl.Data.BindID.Keys.shright)
            self.widgetObj.unbind_all(ww.currUIImpl.Data.BindID.Keys.cmdu)
            self.widgetObj.unbind_all(ww.currUIImpl.Data.BindID.Keys.cmdr)
    

        return [ww.currUIImpl.Data.BindID.enterWidget,
                ww.currUIImpl.Data.BindID.focusIn,
                ww.currUIImpl.Data.BindID.leaveWidget,
                ww.currUIImpl.Data.BindID.focusOut],\
               [__bindAll,
                __bindAll,
                __unbindAll,
                __unbindAll]