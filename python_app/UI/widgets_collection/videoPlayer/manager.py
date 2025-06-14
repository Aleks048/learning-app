import UI.widgets_collection.videoPlayer.videoPlayer as viplmw

import UI.widgets_manager as wm
import UI.widgets_facade as wf

import file_system.file_system_facade as fsf
import _utils._utils_main as _u
import data.temp as dt


class LayoutManagers:
    class _Main(wm.MenuLayout_Interface):
        prefix = "_Main"

        def __init__(self, winRoot):
            super().__init__(winRoot)

            # self.videoPlayerFrame = viplmw.VideoPlayerLabel(winRoot, prefix = "")
            # self.addWidget(self.videoPlayerFrame)

        def getVideoPosition(self):
            return self.videoPlayerFrame.getVideoPosition()

        def showVideo(self, subsection, imIdx):
            currSubsection  = self.winRoot.videoLabel.subsection
            currImIdx = self.winRoot.videoLabel.imIdx

            if (not self.winRoot.wasRendered) \
                or (subsection != currSubsection) or (imIdx != currImIdx):
                self.winRoot.render()
                self.winRoot.showVideo(subsection, imIdx)
                pdfMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                                    wf.Wr.MenuManagers.PdfReadersManager)
                pdfMenuManager.reduceHeight(300)
            else:
                self.winRoot.hide()
                pdfMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                                    wf.Wr.MenuManagers.PdfReadersManager)
                pdfMenuManager.reduceHeight(0)

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class VideoPLayerManager(wm.MenuManager_Interface):
    imIdx = 0
    shown = False

    def __init__(self, rootWidget):
        dimensions = _u.getMonitorsAreas()[0]
        width = dimensions[2] # 1500
        height = dimensions[3] - 50 # 850

        halfWidth = int(width / 2)

        width = halfWidth, 
        height = 300
        rootWidget.width = width
        rootWidget.height = height
        rootWidget.setGeometry(width, height)

        winRoot = viplmw.VideoPlayerRoot(rootWidget, 
                                     width = 0, 
                                     height = 0)
        layouts = []
        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))
            
        self.subsection = fsf.Data.Book.currSection
        currLayout = layouts[0]
        currLayout.subsection = self.subsection
        
        super().__init__(winRoot,
                        layouts,
                        currLayout)

    def showVideo(self, subsection, imIdx):
        return self.layouts[0].showVideo(subsection, imIdx)

    def getVideoPosition(self):
        return self.layouts[0].getVideoPosition()