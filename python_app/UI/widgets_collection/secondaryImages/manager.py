import UI.widgets_collection.secondaryImages.secondaryImages as sim

import UI.widgets_manager as wm
import file_system.file_system_facade as fsf
import _utils._utils_main as _u


class LayoutManagers:
    class _Main(wm.MenuLayout_Interface):
        prefix = "_Main"

        def __init__(self, winRoot):
            super().__init__(winRoot)

            self.secondaryEntry = sim.SecondaryImagesFrame(winRoot)
            self.addWidget(self.secondaryEntry)

        def show(self, dimensions = None):
            super().show()

        def hide(self):
            return super().hide()

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class SecondaryImagesManager(wm.MenuManager_Interface):
    imIdx = 0
    shown = False

    def __init__(self, topFrame):
        dimensions = _u.getMonitorsAreas()[0]
        width = dimensions[2] # 1500
        height = dimensions[3] - 50 # 850

        halfWidth = int(width / 2)

        width = halfWidth, 
        height = height - 105
        topFrame.width = width
        topFrame.height = height
        topFrame.setGeometry(width, height)

        winRoot = sim.SecondaryImagesRoot(topFrame.contentFrame, 
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

    def addSecondaryFrame(self, subsection, imIdx):
        self.layouts[0].secondaryEntry.addSecondaryFrame(subsection, imIdx)
        self.layouts[0].secondaryEntry.render()
