import UI.widgets_collection.summary.summary as summ
import UI.widgets_manager as wm
import UI.widgets_facade as wf

import data.temp as dt
import file_system.file_system_facade as fsf
import _utils._utils_main as _u


class LayoutManagers:
    class _Main(wm.MenuLayout_Interface):
        prefix = "_Main"

        def __init__(self, winRoot):
            super().__init__(winRoot)

            self.subsectionSummary = summ.SubsectionSummaryText(winRoot)

        def show(self):
            super().show()

        def showSummary(self, subsection):
            if not self.subsectionSummary.wasRendered:
                self.subsectionSummary.subsection = subsection
                self.subsectionSummary.render()

                pdfMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                                    wf.Wr.MenuManagers.PdfReadersManager)
                pdfMenuManager.reduceHeight(300)
            else:
                self.subsectionSummary.subsection = subsection
                self.subsectionSummary.hide()
                pdfMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                                    wf.Wr.MenuManagers.PdfReadersManager)
                pdfMenuManager.reduceHeight(0)

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

class SummaryManager(wm.MenuManager_Interface):
    imIdx = 0
    shown = False

    def __init__(self, topFrame):
        dimensions = _u.getMonitorsAreas()[0]
        width = dimensions[2] # 1500
        height = dimensions[3] - 50 # 850

        halfWidth = int(width / 2)

        width = halfWidth
        height = 300
        topFrame.width = width
        topFrame.height = height
        topFrame.setGeometry(width, height)

        winRoot = summ.SummaryRoot(topFrame.contentFrame, 
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

    def showSummary(self, subsection):
        self.layouts[0].showSummary(subsection)
