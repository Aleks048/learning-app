import time

import UI.widgets_wrappers as ww
import UI.widgets_facade as wf
import data.temp as dt
import file_system.file_system_facade as fsf
import _utils.pathsAndNames as _upan
import _utils._utils_main as _u
import outside_calls.outside_calls_facade as osc

class VideoInfoLabel(ww.currUIImpl.Label):
    def __init__(self, rootWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 1, "columnspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.W}
        }
        name = "_VideoInfoLabel_"
        super().__init__(prefix = prefix, 
                         name = name, 
                         rootWidget = rootWidget, 
                         renderData = data, 
                         padding = [0, 0, 0, 0], 
                         text = "")
    def receiveNotification(self, broadcasterType, data):
        text = data[0]
        self.changeText(text)

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
                        renderData = data,
                        bindCmd = self.bindCmd)
    
    def __getInfoText(self):
        return f"subsection {self.subsection}:{self.imIdx} | position {round(self.getVideoPosition(), 2)}%"

    def play(self, playPosition=None):
        self.notify(VideoInfoLabel, [self.__getInfoText()])
        return super().play(playPosition)

    def pause(self):
        self.notify(VideoInfoLabel, [self.__getInfoText()])
        return super().pause()

    def bindCmd(self):
        def __startAddingEntry(*args):
            self.pause()
            mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.startAddingTheEntry()
        
        def __updatePosition(*args):
            if self.imIdx == _u.Token.NotDef.str_t:
                return

            videoPositionDict:dict = fsf.Data.Sec.videoPosition(self.subsection)
            videoPositionDict[self.imIdx] = self.getVideoPosition()
            fsf.Data.Sec.videoPosition(self.subsection, videoPositionDict)

        def __restart(*args):
            self.pause()
            self.play(0.0)
        
        def __scroll(amount):
            self.scroll(amount)
            self.notify(VideoInfoLabel, [self.__getInfoText()])
        
        def __removeImIdx():
            self.imIdx = _u.Token.NotDef.str_t
            self.notify(VideoInfoLabel, [self.__getInfoText()])

        def __bindAll(*args):
            self.rebind([ww.currUIImpl.Data.BindID.Keys.shenter], [lambda *args: __startAddingEntry()])
            self.rebind([ww.currUIImpl.Data.BindID.Keys.shspace], [lambda *args: self.play()])
            self.rebind([ww.currUIImpl.Data.BindID.Keys.left], [lambda *args: __scroll(-5)])
            self.rebind([ww.currUIImpl.Data.BindID.Keys.right], [lambda *args: __scroll(5)])
            self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdu], [lambda *args: __updatePosition(*args)])
            self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdr], [lambda *args: __restart(*args)])
            self.rebind([ww.currUIImpl.Data.BindID.Keys.escape], [lambda *args:__removeImIdx()])

        def __unbindAll(*args):
            self.unbind([ww.currUIImpl.Data.BindID.Keys.shenter,
                         ww.currUIImpl.Data.BindID.Keys.shspace,
                         ww.currUIImpl.Data.BindID.Keys.shleft,
                         ww.currUIImpl.Data.BindID.Keys.shright,
                         ww.currUIImpl.Data.BindID.Keys.cmdu,
                         ww.currUIImpl.Data.BindID.Keys.cmdr,
                         ww.currUIImpl.Data.BindID.Keys.escape])
    

        self.rebind([ww.currUIImpl.Data.BindID.focusIn,
                     ww.currUIImpl.Data.BindID.focusOut],\
                    [__bindAll,
                    __unbindAll])
        return [ww.currUIImpl.Data.BindID.enterWidget],\
               [lambda *args: self.forceFocus()]

    def render(self, **kwargs):

        videoPath = _upan.Paths.Section.Video.getAbs(self.subsection)
        audioPath = _upan.Paths.Section.Video.getAbsAudio(self.subsection)

        if self.subsection != None:
            super().render(videoPath, audioPath)
            self.setWidth(700)

            if self.playing:
                self.pause()

            #TODO: change to relevant path

            if not osc.Wr.FsAppCalls.checkIfFileOrDirExists(videoPath):
                _u.log.autolog(f"The file '{videoPath}' does not exist. Stop opening the menu.")
                return


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

class VideoPlayerRoot(ww.currUIImpl.Frame):
    def __init__(self, rootWidget, width, height):
        name = "_VideoPlayerRoot_"
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 100, "row" : 1, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NE}
        }

        extraOptions = {
            ww.Data.GeneralProperties_ID :{"width" : width, "height" : height},
            ww.TkWidgets.__name__ : {}
        }
        super().__init__("", name, rootWidget, 
                         renderData = renderData, extraOptions = extraOptions)

        self.videoLabel = VideoPlayerLabel(self, "_video_")
        self.videoInfo = VideoInfoLabel(self, "_video_")

        self.videoLabel.addListenerWidget(self.videoInfo)

    def getVideoPosition(self):
        return self.videoLabel.getVideoPosition()

    def hide(self, **kwargs):
        self.rootWidget.hide()
        return super().hide(**kwargs)

    def showVideo(self, subsection, imIdx):
        self.videoLabel.subsection = subsection
        self.videoLabel.imIdx = imIdx

        self.videoInfo.render()
        self.videoLabel.render()
