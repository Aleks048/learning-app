
import UI.widgets_wrappers as ww
import UI.widgets_facade as wf
import UI.widgets_collection.common as comw
import UI.widgets_collection.utils as _ucomw
import UI.widgets_data as wd

import _utils._utils_main as _u
import data.temp as dt


class SecondaryImageFrameNameLabel(comw.TOCLabelWithClick):
    def __init__(self, root, prefix, row, column, 
                 columnspan=1, sticky=ww.currUIImpl.Orientation.NW, 
                 padding=[0, 0, 0, 0], image=None, text=None):
        self.subsection = None
        self.imIdx = None
        
        super().__init__(root, prefix, 
                         row, column, columnspan, 
                         sticky, padding, image, text)

class SecondaryImagesFrame(ww.currUIImpl.Frame):
    def __init__(self, rootWidget):
        name = "_SecondaryImagesFrame_"
        self.subsection = None
        self.imIdx = None
        self.secondWidgetFrameFrame = None
        self.mainTOCWidget = None

        self.secondImFrames = set()

        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 0, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NE}
        }
        super().__init__("", name, rootWidget, renderData = renderData)

        wd.Data.Reactors.entryChangeReactors[self.name] = self

    def addSecondaryFrame(self, subsection, imIdx):
        self.secondImFrames.add(subsection +  "_" + str(imIdx))
        self.subsection = subsection
        self.imIdx = str(imIdx)

    def receiveNotification(self, broadcasterType, data = None):
        if data != None:
            if data[0]:
                self.secondWidgetFrameFrame.destroy()
                self.secondWidgetFrameFrame = self.__addSecondaryFrameWidget(self.subsection, self.imIdx)
                self.secondWidgetFrameFrame.render()
        else:
            self.update()
            newHeight = self.getHeight()
            # self.notify(PfdReader_BOX, data = [newHeight])

    def __addSecondaryFrameSelector(self):
        seclectorFrameRenderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 1, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NE}
        }

        seclectorFrame = ww.currUIImpl.Frame("_SelectorFrame_", self.name, self, seclectorFrameRenderData)

        column = 0
        for k in self.secondImFrames:
            label = SecondaryImageFrameNameLabel(seclectorFrame, 
                                     k.replace(".", "") + "selectorLabel",
                                     0,
                                     column,
                                     text = "   " + k + "   ")
            shouldBeBrown = k == (str(self.subsection) + "_" + str(self.imIdx))
            _ucomw.bindChangeColorOnInAndOut(label, shouldBeBrown = shouldBeBrown)
            if shouldBeBrown:
                label.changeColor("brown")
            column += 1
            label.render()
            label.subsection = k.split("_")[0]
            label.imIdx = k.split("_")[1]

            def __showLabel(label):
                if (str(label.subsection) == str(self.subsection))\
                    and (str(label.imIdx) == str(self.imIdx)):
                    self.subsection = None
                    self.imIdx = None
                else:
                    self.subsection = str(label.subsection)
                    self.imIdx = str(label.imIdx)
                self.render()

            label.rebind([ww.currUIImpl.Data.BindID.mouse1],
                         [lambda e, l = label, *args: __showLabel(l)])
            
            def __deleteLabel(label):
                self.secondImFrames.remove(label.subsection + "_" + label.imIdx)
                if (self.subsection == label.subsection)\
                    and (label.imIdx == self.imIdx):
                    self.subsection = None
                    self.imIdx = None
                
                if self.secondImFrames == set():
                    pdfMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                                    wf.Wr.MenuManagers.PdfReadersManager)
                    pdfMenuManager.reduceHeight(0)
                self.render()

            label.rebind([ww.currUIImpl.Data.BindID.mouse2],
                         [lambda e, l = label, *args: __deleteLabel(l)])
        return seclectorFrame
    
    def __addSecondaryFrameWidget(self, subsection, imIdx):
        seconEntryWidgetFrameRenderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 0, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NE}
        }
        
        secondWidgetFrameFrame = ww.currUIImpl.Frame("_SecondWidgetFrame_", self.name, 
                                                     self, seconEntryWidgetFrameRenderData)

        prefix = "seconadaryFrameLabel_" + subsection.replace(".", "") +  "_" + str(imIdx)
        entryWidget = SecondaryEntryBox(secondWidgetFrameFrame, prefix)

        entryWidget.subsection = subsection
        entryWidget.imIdx = imIdx
        entryWidget.render()
        entryWidget.addListenerWidget(self)
        return secondWidgetFrameFrame
    
    def render(self):
        for ch in self.getChildren().copy():
            ch.destroy()

        frameSelector = self.__addSecondaryFrameSelector()
        frameSelector.render()

        if (self.subsection != None) and (self.imIdx != None):
            self.secondWidgetFrameFrame = self.__addSecondaryFrameWidget(self.subsection, self.imIdx)
            self.secondWidgetFrameFrame.render()
        
        super().render(self.renderData)

        newHeight = self.getHeight()
        # self.notify(PfdReader_BOX, data = [newHeight])

    def onSecondaryImageOpen(self, subsection, imIdx):
        secondaryImagesManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                            wf.Wr.MenuManagers.SecondaryImagesManager)
        secondaryImagesManager.addSecondaryFrame(subsection, imIdx)
        if not secondaryImagesManager.shown:
            secondaryImagesManager.show()
            pdfMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                                    wf.Wr.MenuManagers.PdfReadersManager)
            pdfMenuManager.reduceHeight(300)

class SecondaryEntryBox(comw.EntryWindow_BOX):
    def onExtraImDelete(self, subsection, imIdx, eImIdx):
        if (subsection == self.subsection) and (imIdx == self.imIdx):
            if self.entryManager != None:
                etm = self.entryManager
                etm.deleteExtraImage(eImIdx)

    def onMainLatexImageUpdate(self, subsection, imIdx):
        if (subsection == self.subsection) and (imIdx == self.imIdx):
            if self.entryManager != None:
                etm = self.entryManager
                etm.updateEntryImage()

    def onExtraImMove(self, subsection, imIdx, eImIdx, moveUp:bool):
        if (subsection == self.subsection) and (imIdx == self.imIdx):
            if self.entryManager != None:
                etm = self.entryManager
                eImFrame = etm.moveExtraIm(eImIdx, moveUp)

                if eImFrame != None:
                    self.shouldScroll = True
                    self.scrollIntoView(None, eImFrame)

    def onAlwaysShowChange(self, subsection, imIdx):
        if (subsection == self.subsection) and (imIdx == self.imIdx):
            if self.entryManager != None:
                for ch in self.entryManager.rowFrame2.getChildren():
                    ch.render()

    def onAlwaysShowChange(self, subsection, imIdx):
        if (subsection == self.subsection) and (imIdx == self.imIdx):
            if self.entryManager != None:
                self.entryManager.rowFrame1.hide()
                self.entryManager.rowFrame1.render()

    def onImageResize(self, subsection, imIdx, eImIdx):
        if (subsection == self.subsection) and (imIdx == self.imIdx):
            if self.entryManager != None:
                if eImIdx == None:
                    self.entryManager.updateMainImage()
                else:
                    self.entryManager.updateExtraImage(eImIdx)
                self.entryManager.updateResizeEtrText()

    def onRetakeAfter(self, subsection, imIdx, eImidx = _u.Token.NotDef.str_t):
        if (subsection == self.subsection) and (imIdx == self.imIdx):
            if self.entryManager != None:
                self.entryManager.updateMainImage()

    def render(self, scrollTOC=True):
        wd.Data.Reactors.entryChangeReactors[self.name] = self
        super().render(scrollTOC)


class SecondaryImagesRoot(ww.currUIImpl.Frame):
    def __init__(self, rootWidget, width, height):
        name = "_SecondaryImagesRoot_"
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 0, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NE}
        }
        extraOptions = {
            ww.Data.GeneralProperties_ID :{"width" : width, "height" : height},
            ww.TkWidgets.__name__ : {}
        }
        super().__init__("", name, rootWidget, renderData = renderData, extraOptions = extraOptions)
