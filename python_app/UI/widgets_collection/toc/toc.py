import UI.widgets_wrappers as ww

import data.constants as dc
import data.temp as dt
import UI.widgets_collection.toc.manager as tocm
import UI.widgets_collection.common as comw


class Hide_BTN(ww.currUIImpl.Button,
                         dc.AppCurrDataAccessToken):
    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 5, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0,  "sticky": ww.currUIImpl.Orientation.W}
        }
        text = "Hide"
        name = "_decline_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        tocManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                            tocm.TOCManager)
        tocManager.hide()

class SearchInSubsectionsText_CHB(ww.currUIImpl.Checkbox):
    etenriesTextOnlyDefault = 0

    def __init__(self, parentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 5, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.E}
        }
        name = "_SearchInSubsectionsText_CHB"
        text = "Search Subsections Text"
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = renderData, 
                        text = text)
        self.setData(self.etenriesTextOnlyDefault)

    def receiveNotification(self, broadcasterName):
        outData =  True if self.getData() == 1 else False
        return outData


class Filter_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "columnspan": 5}
        }
        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {},
            ww.TkWidgets.__name__ : {"width": 54}
        }
        name = "_filter_ETR"
        defaultText = "Filter token"

        super().__init__(prefix, 
                        name,
                        patentWidget, 
                        data,
                        extraBuildOptions,
                        bindCmd=self.bindCmd,
                        defaultText = defaultText)        

    def bindCmd(self):
        return [ww.currUIImpl.Data.BindID.Keys.shenter], \
               [lambda *args: self.notify(comw.TOC_BOX, 
                                          [self.getData(), 
                                           self.notify(SearchInSubsectionsText_CHB)])]


class TOCRoot(ww.currUIImpl.RootWidget):
    pass