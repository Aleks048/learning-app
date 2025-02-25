import UI.widgets_collection.videoPlayer.videoPlayer as vpw

import UI.widgets_manager as wm
import file_system.file_system_facade as fsf
import _utils._utils_main as _u


class LayoutManagers:
    class VideoPlayerLayout(wm.MenuLayout_Interface):
        prefix = "_VideoPlayerLayout_"

        def __init__(self, winRoot):

            self.winRoot = winRoot
            self.subsection = _u.Token.NotDef.str_t
            self.imIdx = _u.Token.NotDef.str_t

            appDimensions = [720, 300, 0, 0]
            super().__init__(winRoot, appDimensions)
            self.videoPlayerLabel = vpw.VideoPlayerLabel(winRoot, self.prefix)
            self.addWidget(self.videoPlayerLabel)

            winRoot.setGeometry(*self.appDimensions)
            winRoot.videoFrame = self.videoPlayerLabel
        
        def show(self):
            self.videoPlayerLabel.subsection = self.subsection
            self.videoPlayerLabel.imIdx = self.imIdx
            self.videoPlayerLabel.startPlayWithRender = True

            self.winRoot.changeTitle(f"Video for: {self.subsection}/{self.imIdx}")
            super().show()

        def getVideoPosition(self):
            return self.videoPlayerLabel.getVideoPosition()

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class VideoPlayerManager(wm.MenuManager_Interface):
    def __init__(self):
        self.imIdx = 0
        self.shown = False

        winRoot = vpw.VideoPlayerRoot(50, 50)
        layouts = []
        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))
            
        self.subsection = fsf.Data.Book.currSection
        currLayout = layouts[0]
        currLayout.subsection = self.subsection
        
        super().__init__(winRoot,
                        layouts,
                        currLayout)
        winRoot.hide()
    def show(self, subsection, imIdx):
        self.subsection = subsection
        self.imIdx = imIdx

        self.layouts[0].subsection = self.subsection
        self.layouts[0].imIdx = self.imIdx
        
        self.shown = True

        return super().show()
    
    def hide(self):
        self.shown = False

        return super().hide()
    
    def getVideoPosition(self):
        return self.layouts[0].getVideoPosition()