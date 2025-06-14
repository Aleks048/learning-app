from threading import Thread

import file_system.file_system_facade as fsf

import _utils._utils_main as _u

import UI.widgets_data as wd
import UI.widgets_collection.common as comw
import UI.factories.factoriesFacade as wff


import data.temp as dt



class MainTOCBox(comw.TOC_BOX):
    def addTopSectionEntry(self, topSection, row):
        self.addSectionWidgets(topSection, row, self.scrollable_frame)


        if (topSection == fsf.Data.Book.currTopSection):
            subsections:list = fsf.Wr.BookInfoStructure.getSubsectionsList(topSection)

            for i in range(len(subsections)):
                self.addSubsectionEntry(subsections[i], i)


    def addSubsectionEntry(self, subsection, row):
        if self._isSubsectionHidden(subsection):
            return

        parentSection = ".".join(subsection.split(".")[:-1])
        
        if self.subsectionWidgetManagers.get(parentSection) == None:
            return

        parentManager = self.subsectionWidgetManagers[parentSection]

        self.addSectionWidgets(subsection, row, parentManager.subsectionChildrenSectionsFrame)

        subsections:list = fsf.Wr.BookInfoStructure.getSubsectionsList(subsection)
            
        for i in range(len(subsections)):
            self.addSubsectionEntry(subsections[i], i)


    def addSectionWidgets(self, subsection, row, parentWidget):
        subsectionFactory = wff.SubsectionWidgetFactoryMainTOC(subsection)

        if subsection == _u.Token.NotDef.str_t:
            return

        super().addSubsectionWidgetsManager(subsection, row, parentWidget, subsectionFactory)

        if subsection == fsf.Data.Book.subsectionOpenInTOC_UI:
            super().openSubsection(subsection)
            super().openEntries(subsection)
        elif subsection == fsf.Data.Book.currTopSection:
            super().openSubsection(subsection)

    def populateTOC(self):
        topSections = fsf.Wr.BookInfoStructure.getTopSectionsList()

        text_curr_filtered = topSections

        for i in range(len(text_curr_filtered)):
            subsection = text_curr_filtered[i]
            self.addTopSectionEntry(subsection, i)
        
        # self.notify(ScreenshotLocation_LBL)

    def receiveNotification(self, broadcasterType, data = None, entryClicked = None):
        import UI.widgets_collection.main.math.UI_layouts.mainLayout as mui
        if broadcasterType == mui.ExitApp_BTN:
            tsList = fsf.Wr.BookInfoStructure.getTopSectionsList()

            sections = fsf.Data.Book.sections

            for ts in tsList:
                if ts == _u.Token.NotDef.str_t:
                    return

                sections[ts]["showSubsections"] = str(int(self.showSubsectionsForTopSection[ts]))

            fsf.Data.Book.sections = sections
        elif broadcasterType == mui.ImageGeneration_BTN:
            subsection = data[0]
            imIdx = data[1]
            self.entryClicked = entryClicked

            fsf.Data.Book.subsectionOpenInTOC_UI = subsection
            fsf.Data.Book.currSection = subsection
            fsf.Data.Book.currTopSection = subsection.split(".")[0]
            fsf.Data.Book.entryImOpenInTOC_UI = imIdx

            self.AddEntryWidget(imIdx, 
                                subsection, 
                                self.subsectionWidgetManagers[subsection].entriesFrame)

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onFullEntryMove" in dir(w):
                    w.onFullEntryMove()
        elif broadcasterType == mui.ImageGroupAdd_BTN:
            self.renderWithScrollAfter()
        elif broadcasterType == mui.ShowAllSubsections_BTN:
            self.renderWithScrollAfter()
        elif broadcasterType == mui.ShowHideLinks_BTN:
            self.showLinks = not self.showLinks
            self.showLinksForSubsections = []
            self.renderWithScrollAfter()
        else:
            self.renderWithScrollAfter()

    def onSubsectionOpen(self, subsection):
        if wd.Data.General.singleSubsection:
            for subsec, m in self.subsectionWidgetManagers.items():
                if len(subsec.split(".")) != 1:
                    m.closeSubsection()

        manager = self.subsectionWidgetManagers[subsection]
        manager.entriesFrame.render()

        self.subsectionWidgetManagers[subsection].addEntryWidgetsForSubsection()
        
        self.shouldScroll = True
        self.scrollIntoView(None, manager.subsectionFrame)

    def onTopSectionOpen(self, topSection):
        self.render(withFullMove = False)

        manager = self.subsectionWidgetManagers[topSection]
        self.shouldScroll = True
        self.scrollIntoView(None, manager.subsectionFrame)

    def onFullEntryMove(self):
        currSubsection = fsf.Data.Book.subsectionOpenInTOC_UI
        currEntryIdx = fsf.Data.Book.entryImOpenInTOC_UI

        shownEntryFrame = None

        if currSubsection == _u.Token.NotDef.str_t:
            # self.notify(ScreenshotLocation_LBL)
            return

        if self.subsectionWidgetManagers.get(currSubsection) == None:
            topSection = fsf.Data.Book.currTopSection

            if self.subsectionWidgetManagers.get(topSection) != None:
                self.subsectionWidgetManagers[topSection].openSubsection()
                for w in wd.Data.Reactors.subsectionChangeReactors.values():
                    if "onTopSectionOpen" in dir(w):
                        w.onTopSectionOpen(currSubsection)
            # self.notify(ScreenshotLocation_LBL)

        if not self.subsectionWidgetManagers[currSubsection].opened:
            self.onSubsectionOpen(currSubsection)

        for imIdx, efm in self.subsectionWidgetManagers[currSubsection].entriesWidgetManagers.items():
            if imIdx != currEntryIdx:
                if (fsf.Data.Sec.tocWImageDict(currSubsection)[imIdx] == "1"):
                    efm.changeFullMoveColor(True)

                    if not efm.imagesShown:
                        efm.showImages()

                    efm.hideRow2()
                    efm.setFullImageLabelNotClicked()
                else:
                    if efm.imagesShown:
                        efm.hideImages()
                    efm.changeFullMoveColor(True)
                    efm.hideRow2()
            else:
                efm.showRow2()

                if dt.UITemp.Layout.noMainEntryShown:
                    efm.showImages()
                else:
                    if efm.imagesShown:
                        efm.hideImages()

                efm.changeFullMoveColor(False)
                shownEntryFrame = efm.entryFrame

        if shownEntryFrame != None:
            #NOTE: this seems to fix an issue when the scrolling happens before
            #      canvas update and the widget is not seen
            def th(tocWidget, frame):
                tocWidget.shouldScroll = True
                tocWidget.scrollIntoView(None, frame)
            t = Thread(target = th, args = [self, shownEntryFrame])
            t.start()

        # self.notify(ScreenshotLocation_LBL)

    def scrollToCurrSubsecrtionWidget(self):
        self.scrollIntoView(None, 
                            self.subsectionWidgetManagers[fsf.Data.Book.currSection].subsectionFrame)

    def render(self, shouldScroll=False, withFullMove = True):
        super().render(shouldScroll)

        if withFullMove:
            if fsf.Data.Book.entryImOpenInTOC_UI != _u.Token.NotDef.str_t:
                for w in wd.Data.Reactors.entryChangeReactors.values():
                    if "onFullEntryMove" in dir(w):
                        w.onFullEntryMove()

