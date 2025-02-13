import time

import UI.widgets_wrappers as ww
import UI.widgets_facade as wf
import data.temp as dt
import file_system.file_system_facade as fsf
import generalManger.generalManger as gm
import _utils.pathsAndNames as _upan
import _utils._utils_main as _u
import outside_calls.outside_calls_facade as osc

class VideoPlayerLabel(ww.currUIImpl.VideoPayer):
    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0, "columnspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.W}
        }
        self.subsection = None
        self.imIdx = None

        self.playing = False

        name = "_VideoPlayerLabel_FRM"
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data)
    
    def play(self, playPosition=None):
        return super().play(playPosition, f"{self.subsection}:{self.imIdx}")

    def render(self, **kwargs):
        if self.subsection != None:
            if self.playing:
                self.pause()

            #TODO: change to relevant path
            videoPath = _upan.Paths.Section.Video.getAbs(self.subsection)

            if not osc.Wr.FsAppCalls.checkIfFileOrDirExists(videoPath):
                _u.log.autolog(f"The file '{videoPath}' does not exist. Stop opening the menu.")
                return

            super().render(videoPath, **kwargs)

            videoPositionDict:dict = fsf.Data.Sec.videoPosition(self.subsection)
            if videoPositionDict.get(self.imIdx) != None:
                self.play(videoPositionDict[self.imIdx])

                while not self.isPlaying():
                    time.sleep(0.1)
                time.sleep(0.1)
                self.play()
            else:
                self.play()
                while not self.isPlaying():
                    time.sleep(0.1)
                time.sleep(0.1)
                self.play()
                
            self.forceFocus()

class VideoPlayerRoot(ww.currUIImpl.RootWidget):
    def __init__(self, width, height, bindCmd=...):
        self.videoFrame = None
        super().__init__(width, height, bindCmd= self.bindCmd)
        def __onClose(*args):
            self.videoFrame.close()
            self.destroy()

        self.bindToClose(__onClose)
        self.makeUnmovable()

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
            self.rebind([ww.currUIImpl.Data.BindID.Keys.shenter], [lambda *args: __startAddingEntry()])
            self.rebind([ww.currUIImpl.Data.BindID.Keys.shspace], [lambda *args: self.videoFrame.play()])
            self.rebind([ww.currUIImpl.Data.BindID.Keys.shleft], [lambda *args: self.videoFrame.scroll(-5)])
            self.rebind([ww.currUIImpl.Data.BindID.Keys.shright], [lambda *args: self.videoFrame.scroll(5)])
            self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdu], [lambda *args: __updatePosition(*args)])
            self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdr], [lambda *args: __restart(*args)])

        def __unbindAll(*args):
            self.unbind([ww.currUIImpl.Data.BindID.Keys.shenter,
                         ww.currUIImpl.Data.BindID.Keys.shspace,
                         ww.currUIImpl.Data.BindID.Keys.shleft,
                         ww.currUIImpl.Data.BindID.Keys.shright,
                         ww.currUIImpl.Data.BindID.Keys.cmdu,
                         ww.currUIImpl.Data.BindID.Keys.cmdr])
    

        return [ww.currUIImpl.Data.BindID.enterWidget,
                ww.currUIImpl.Data.BindID.focusIn,
                ww.currUIImpl.Data.BindID.leaveWidget,
                ww.currUIImpl.Data.BindID.focusOut],\
               [__bindAll,
                __bindAll,
                __unbindAll,
                __unbindAll]