import UI.widgets_manager as wm
import UI.widgets_wrappers as ww

import UI.widgets_collection.main.math.UI_layouts.common as commw
import UI.widgets_collection.main.math.UI_layouts.mainLayout as ml
import UI.widgets_collection.main.math.UI_layouts.sectionLayout as sl
import UI.widgets_collection.main.math.UI_layouts.addModifySections as amsl
import UI.widgets_collection.main.math.UI_layouts.addModifyOrigMat as amom
import UI.widgets_collection.common as comw
import data.constants as dc
import file_system.file_system_facade as fsf

class LayoutManagers:
    class _Main(wm.MenuLayout_Interface):
        prefix = "_mainLayout"
        tocBox = None

        addEntryETR = None

        def __init__(self, winRoot : ww.currUIImpl.RootWidget):
            #
            # pre init
            #


            #
            # init
            #
            monitorSize = dc.MonitorSize.getData()
            monHalfWidth = int(monitorSize[0] / 2)
            appDimensions = [monHalfWidth, 830, monHalfWidth, 0]

            super().__init__(winRoot, appDimensions)

            tocBox_BOX = comw.TOC_BOX(winRoot, self.prefix)
            tocBox_BOX.populateTOC()
            self.addWidget(tocBox_BOX)
            self.tocBox = tocBox_BOX
            
            addToTOCwImage_CHB = ml.addToTOCwImage_CHB(winRoot, self.prefix)
            self.addWidget(addToTOCwImage_CHB)
            textOnly_CHB = ml.TextOnly_CHB(winRoot, self.prefix)
            self.addWidget(textOnly_CHB)

            imageGenration_ERT = ml.ImageGeneration_ETR(winRoot, self.prefix)
            self.addEntryETR = imageGenration_ERT
            self.addWidget(imageGenration_ERT)
            
            imageGeneration_BTN = ml.ImageGeneration_BTN(winRoot, self.prefix)
            imageGeneration_BTN.addListenerWidget(imageGenration_ERT)
            imageGeneration_BTN.addListenerWidget(addToTOCwImage_CHB)
            imageGeneration_BTN.addListenerWidget(textOnly_CHB)
            imageGeneration_BTN.addListenerWidget(tocBox_BOX)
            self.addWidget(imageGeneration_BTN)

            imageGenerationRestart_BTN =ml.ImageGenerationRestart_BTN(winRoot, self.prefix)
            imageGenerationRestart_BTN.addListenerWidget(imageGenration_ERT)
            imageGenerationRestart_BTN.addListenerWidget(imageGeneration_BTN)
            self.addWidget(imageGenerationRestart_BTN)

            screenshotLocation_LBL = ml.ScreenshotLocation_LBL(winRoot, self.prefix)
            self.addWidget(screenshotLocation_LBL)
            
            imageGenration_ERT.addListenerWidget(imageGeneration_BTN)
            imageGenration_ERT.addListenerWidget(imageGenerationRestart_BTN)
            imageGenration_ERT.addListenerWidget(addToTOCwImage_CHB)
            imageGenration_ERT.addListenerWidget(textOnly_CHB)

            switchLayout_BTN = commw.SwitchLayoutSectionVSMain_BTN(winRoot, self.prefix)
            self.addWidget(switchLayout_BTN)

            # switchToCurrSectionLayout_BTN = ml.SwitchToCurrSectionLayout_BTN(winRoot, self.prefix)
            # self.addWidget(switchToCurrSectionLayout_BTN)

            chooseOriginalMaterial_OM = ml.ChooseOriginalMaterial_OM(winRoot, self.prefix)
            self.addWidget(chooseOriginalMaterial_OM)

            layoutsSwitchOrigMatVSMain_BTN = commw.LayoutsSwitchOrigMatVSMain_BTN(winRoot, self.prefix)
            self.addWidget(layoutsSwitchOrigMatVSMain_BTN)

            exitApp_BTN = ml.ExitApp_BTN(winRoot, self.prefix)
            self.addWidget(exitApp_BTN)
            exitApp_BTN.addListenerWidget(tocBox_BOX)
 
            showTocWindow_BTN = commw.ShowTocWindow_BTN(winRoot, self.prefix)
            self.addWidget(showTocWindow_BTN)
            
            # reAddAllNotesFromTheOMPage_BTN = ml.ReAddAllNotesFromTheOMPage_BTN(winRoot, self.prefix)
            # self.addWidget(reAddAllNotesFromTheOMPage_BTN)

            showAllSubsections_BTN = ml.ShowAllSubsections_BTN(winRoot, self.prefix)
            self.addWidget(showAllSubsections_BTN)

            # showFirstEntryOfTheCurrPage = ml.ShowFirstEntryOfTheCurrPage(winRoot, self.prefix)
            # self.addWidget(showFirstEntryOfTheCurrPage)

            addGlobalLink_ETR = commw.AddGlobalLink_ETR(winRoot, self.prefix, column = 0, row = 14)
            self.addWidget(addGlobalLink_ETR)

            addWebLink_BTN = commw.AddWebLink_BTN(winRoot, self.prefix, column = 3, row = 14)
            self.addWidget(addWebLink_BTN)

            showProof_BTN = commw.ShowProofs_BTN(winRoot, self.prefix, column = 5, row = 14)
            self.addWidget(showProof_BTN)
            showProof_BTN.addListenerWidget(tocBox_BOX)

            imageGroupAdd_BTN = ml.ImageGroupAdd_BTN(winRoot, self.prefix)
            self.addWidget(imageGroupAdd_BTN)

            showHideLinks_BTN = ml.ShowHideLinks_BTN(winRoot, self.prefix)
            self.addWidget(showHideLinks_BTN)

            tocBox_BOX.addListenerWidget(screenshotLocation_LBL)

            imageGroupAdd_BTN.addListenerWidget(imageGenration_ERT)
            imageGroupAdd_BTN.addListenerWidget(imageGenerationRestart_BTN)
            imageGroupAdd_BTN.addListenerWidget(tocBox_BOX)

            showHideLinks_BTN.addListenerWidget(tocBox_BOX)
            showAllSubsections_BTN.addListenerWidget(tocBox_BOX)
            # showFirstEntryOfTheCurrPage.addListenerWidget(tocBox_BOX)

            addWebLink_BTN.addListenerWidget(addGlobalLink_ETR)
            addWebLink_BTN.addListenerWidget(imageGenration_ERT)
            addWebLink_BTN.addListenerWidget(tocBox_BOX)

            #
            # post init
            #

        def show(self):
            self.winRoot.configureColumn(0, weight = 1)
            self.winRoot.configureColumn(1, weight = 1)
            self.winRoot.configureColumn(2, weight = 3)
            self.winRoot.configureColumn(3, weight = 1)
            self.winRoot.configureColumn(4, weight = 1)
            return super().show()


    class _Section(wm.MenuLayout_Interface):
        prefix = "_sectionLayout"

        def __init__(self, winRoot : ww.currUIImpl.RootWidget):
            #
            # pre init
            #


            #
            # init
            #
            monitorSize = dc.MonitorSize.getData()
            monHalfWidth = int(monitorSize[0] / 2)
            appDimensions = [monHalfWidth, 90, monHalfWidth, 0]

            super().__init__(winRoot, appDimensions)

            addGlobalLink_ETR = commw.AddGlobalLink_ETR(winRoot, self.prefix)
            self.addWidget(addGlobalLink_ETR)

            showProof_BTN = commw.ShowProofs_BTN(winRoot, self.prefix)
            self.addWidget(showProof_BTN)

            rebuildCurrSection_BTN = sl.RebuildCurrSection_BTN(winRoot, self.prefix)
            self.addWidget(rebuildCurrSection_BTN)

            switchToCurrMainLayout_BTN = sl.SwitchToCurrMainLayout_BTN(winRoot, self.prefix)
            self.addWidget(switchToCurrMainLayout_BTN)

            showTocWindow_BTN = commw.ShowTocWindow_BTN(winRoot, self.prefix, row=0)
            self.addWidget(showTocWindow_BTN)
            #
            # post init
            #
        
        def show(self):
            self.winRoot.configureColumn(0, weight = 1)
            self.winRoot.configureColumn(1, weight = 1)
            self.winRoot.configureColumn(2, weight = 1)
            self.winRoot.configureColumn(3, weight = 1)
            self.winRoot.configureColumn(4, weight = 1)
            return super().show()
    

    class _AddModifySection(wm.MenuLayout_Interface):
        prefix = "_AddModifySectionLayout"

        def __init__(self, winRoot : ww.currUIImpl.RootWidget):
            #
            # pre init
            #
            monitorSize = dc.MonitorSize.getData()
            monHalfWidth = int(monitorSize[0] / 2)
            appDimensions = [monHalfWidth, 120, monHalfWidth, 0]

            #
            # init
            #

            super().__init__(winRoot, appDimensions)

            switchLayout_BTN = amsl.SwitchLayoutSectionVSMain_amsl_BTN(winRoot, self.prefix)
            self.addWidget(switchLayout_BTN)

            setSectionStartPage_ETR = amsl.SetSectionStartPage_ETR(winRoot, self.prefix)
            self.addWidget(setSectionStartPage_ETR)

            setSectionName_ETR = amsl.SetSectionName_ETR(winRoot, self.prefix)
            self.addWidget(setSectionName_ETR)

            currSectionPath_LBL = amsl.CurrSectionPath_LBL(winRoot, self.prefix)
            self.addWidget(currSectionPath_LBL)
            
            newSectionPath_ETR = amsl.NewSectionPath_ETR(winRoot, self.prefix)
            self.addWidget(newSectionPath_ETR)
            
            createNewSubsection_BTN = amsl.CreateNewSubsection_BTN(winRoot, self.prefix)
            self.addWidget(createNewSubsection_BTN)
            
            createNewSubsection_BTN.addListenerWidget(newSectionPath_ETR)
            createNewSubsection_BTN.addListenerWidget(setSectionStartPage_ETR)
            createNewSubsection_BTN.addListenerWidget(setSectionName_ETR)


            modifySubsection_BTN = amsl.ModifySubsection_BTN(winRoot, self.prefix)
            self.addWidget(modifySubsection_BTN)

            modifySubsection_BTN.addListenerWidget(currSectionPath_LBL)
            modifySubsection_BTN.addListenerWidget(setSectionStartPage_ETR)
            modifySubsection_BTN.addListenerWidget(setSectionName_ETR)

            setSectionNoteAppLink_ETR = amsl.SetSectionNoteAppLink_ETR(winRoot, self.prefix)
            self.addWidget(setSectionNoteAppLink_ETR)
            modifySubsection_BTN.addListenerWidget(setSectionNoteAppLink_ETR)

            modifyNotesAppLink_BTN = amsl.ModifyNotesAppLink_BTN(winRoot, self.prefix)
            self.addWidget(modifyNotesAppLink_BTN)
            modifyNotesAppLink_BTN.addListenerWidget(setSectionNoteAppLink_ETR)

            moveToTOC_BTN = amsl.MoveToTOC_BTN(winRoot, self.prefix)
            self.addWidget(moveToTOC_BTN)


        def show(self):
            self.winRoot.configureColumn(0, weight = 1)
            self.winRoot.configureColumn(1, weight = 1)
            self.winRoot.configureColumn(2, weight = 1)
            self.winRoot.configureColumn(3, weight = 1)
            self.winRoot.configureColumn(4, weight = 1)
            return super().show()
    

    class _AddModifyOrigMat(wm.MenuLayout_Interface):
        prefix = "_AddModifyOrigMatLayout"

        def __init__(self, winRoot : ww.currUIImpl.RootWidget):
            #
            # pre init
            #
            monitorSize = dc.MonitorSize.getData()
            monHalfWidth = int(monitorSize[0] / 2)
            appDimensions = [monHalfWidth, 90, monHalfWidth, 0]

            #
            # init
            #

            super().__init__(winRoot, appDimensions)


            addOrigMaterial_BTN = amom.AddOrigMaterial_BTN(winRoot, self.prefix)
            self.addWidget(addOrigMaterial_BTN)

            fetOrigMatPath_ETR = amom.GetOrigMatPath_ETR(winRoot, self.prefix)
            self.addWidget(fetOrigMatPath_ETR)

            getOrigMatDestRelPath_ETR = amom.GetOrigMatDestRelPath_ETR(winRoot, self.prefix)
            self.addWidget(getOrigMatDestRelPath_ETR)

            getOrigMatName_ETR = amom.GetOrigMatName_ETR(winRoot, self.prefix)
            self.addWidget(getOrigMatName_ETR)

            addOrigMaterial_BTN.addListenerWidget(fetOrigMatPath_ETR)
            addOrigMaterial_BTN.addListenerWidget(getOrigMatDestRelPath_ETR)
            addOrigMaterial_BTN.addListenerWidget(getOrigMatName_ETR)

            layoutsSwitchOrigMatVSMain_BTN = amom.LayoutsSwitchOrigMatVSMain_BTN(winRoot, self.prefix)
            self.addWidget(layoutsSwitchOrigMatVSMain_BTN)
            


        def show(self):
            self.winRoot.configureColumn(0, weight = 1)
            self.winRoot.configureColumn(1, weight = 1)
            self.winRoot.configureColumn(2, weight = 1)
            return super().show()
    

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class MathMenuManager(wm.MenuManager_Interface):
    layouts = []
    isShown = False

    def __init__(self):
        winRoot = commw.MainMenuRoot(0, 0)
        layouts = self.layouts

        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(winRoot))
        
        currLayout = None
        for layout in layouts:
            if type(layout) == LayoutManagers._Main:
                currLayout = layout
                break
        
        super().__init__(winRoot,
                        layouts,
                        currLayout)

    def show(self):
        self.isShown = True
        return super().show()
    
    def hide(self):
        self.isShown = False
        return super().hide()

    def getShownStatus(self):
        return self.isShown    

    def switchToMainLayout(self):
        self.switchUILayout(LayoutManagers._Main)

    # def renderTocWidget(self):
    #     for layout in self.layouts:
    #         if type(layout) == LayoutManagers._Main:
    #             layout.tocBox.render()
    #             return

    def startAddingTheEntry(self):
        for layout in self.layouts:
            if type(layout) == LayoutManagers._Main:
                layout.addEntryETR.notify(ml.ImageGeneration_BTN)
                break

    def moveTocToEntry(self, subsection, imIdx, fromTOCWindow = False):
        for layout in self.layouts:
            if type(layout) == LayoutManagers._Main:
                fsf.Data.Book.currTopSection = subsection.split(".")[0]
                fsf.Data.Book.subsectionOpenInTOC_UI = subsection

                layout.tocBox.renderFromTOCWindow = fromTOCWindow
                layout.tocBox.scrollToEntry(subsection, imIdx)
                layout.tocBox.renderFromTOCWindow = False
                return

    def moveTocToCurrEntry(self):
        for layout in self.layouts:
            if type(layout) == LayoutManagers._Main:
                layout.tocBox.render(shouldScroll = True)
                return

    def scrollTocToEntry(self, subsection, imIdx):
        for layout in self.layouts:
            if type(layout) == LayoutManagers._Main:
                layout.tocBox.scrollToEntry(subsection, imIdx)
                return

    def renderWithoutScroll(self):
        for layout in self.layouts:
            if type(layout) == LayoutManagers._Main:
                layout.tocBox.render(shouldScroll = False)
                return

    def showLinksForEntry(self, subsection, imIdx):
        for layout in self.layouts:
            if type(layout) == LayoutManagers._Main:
                layout.tocBox.showLinksForSubsections = []
                layout.tocBox.showLinksForEntryCmd(None, subsection, imIdx)
                return
        

    def switchToSectionLayout(self):
        self.switchUILayout(LayoutManagers._Section)