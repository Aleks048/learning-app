import UI.widgets_wrappers as ww

import data.constants as dc
import data.temp as dt

import UI.widgets_collection.toc.manager as tocm
from UI.widgets_collection.common import TOC_BOX
from UI.factories.factoriesFacade import SubsectionWidgetFactorySearchTOC

import file_system.file_system_facade as fsf


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
               [lambda *args: self.notify(TOC_BOX, 
                                          [self.getData(), 
                                           self.notify(SearchInSubsectionsText_CHB)])]

class SearchTOC_BOX(TOC_BOX):
    def onOpenImageInTocWidget(self, subsection, imIdx):
        efm = self.subsectionWidgetManagers[subsection].entriesWidgetManagers[imIdx]

        if not efm.imagesShown:
            efm.showImages()
        else:
            efm.hideImages()

    def populateTOC(self):
        text_curr = fsf.Wr.BookInfoStructure.getSubsectionsAsTOC()

        text_curr_filtered = []

        if self.filterToken != "":
            for i in range(len(text_curr)):
                subsection = text_curr[i][0]

                if "." not in subsection:
                    continue

                imLinkDict = fsf.Data.Sec.imLinkDict(subsection)
                extraImagesDict = fsf.Data.Sec.extraImagesDict(subsection)

                for k,v in imLinkDict.items():
                    entryImText = fsf.Wr.SectionInfoStructure.getEntryImText(subsection, k)

                    if k in list(extraImagesDict.keys()):
                        for t in extraImagesDict[k]:
                            entryImText += t

                    if (self.filterToken.lower() in v.lower()) \
                        or (self.filterToken.lower() in entryImText.lower()):
                        text_curr_filtered.append(text_curr[i])
                        break
        else:
            text_curr_filtered = text_curr

        if self.filterToken != "":
            for i in range(len(text_curr_filtered)):
                subsection = text_curr_filtered[i][0]

                subsectionFactory = SubsectionWidgetFactorySearchTOC(subsection)
                super().addSubsectionWidgetsManager(subsection, i,
                                                    self.scrollable_frame, subsectionFactory)
                super().openSubsection(subsection)
                super().openEntries(subsection, self.filterToken)

    def receiveNotification(self, broadcasterType, data):
        if broadcasterType == Filter_ETR:
            self.showAll = True
            self.filterToken = data[0]
            self.searchSubsectionsText = data[1]
            self.hide()
            self.showSubsectionsForTopSection = {}
            self.render()


class TOCRoot(ww.currUIImpl.RootWidget):
    pass