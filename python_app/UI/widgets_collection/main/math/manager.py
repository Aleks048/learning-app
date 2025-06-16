import UI.widgets_manager as wm
import UI.widgets_wrappers as ww
import UI.widgets_data as wd

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

        def __init__(self, winRoot):
            #
            # pre init
            #


            #
            # init
            #
            # monitorSize = dc.MonitorSize.getData()
            # monHalfWidth = int(monitorSize[0] / 2)

            super().__init__(winRoot, None)

            primaryMainMenuFrame = wm.UI_generalManager.topLevelFrames["0000"].contentFrame
            secondaryMainMenuFrame = wm.UI_generalManager.topLevelFrames["0100"].contentFrame

            renderData = {
                ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 0, "columnspan" : 1},
                ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
            }

            self.secondaryMainMenuMainLayoutFrame = \
                                ww.currUIImpl.Frame(prefix = "", name = "_secoandaryManusMainLayout", 
                                rootWidget = secondaryMainMenuFrame, 
                                renderData = renderData)
            self.secondaryMainMenuMainLayoutFrame.render()

            
            addToTOCwImage_CHB = ml.addToTOCwImage_CHB(primaryMainMenuFrame, self.prefix)
            self.addWidget(addToTOCwImage_CHB)
            textOnly_CHB = ml.TextOnly_CHB(primaryMainMenuFrame, self.prefix)
            self.addWidget(textOnly_CHB)

            imageGenration_ERT = ml.ImageGeneration_ETR(primaryMainMenuFrame, self.prefix)
            self.addEntryETR = imageGenration_ERT
            self.addWidget(imageGenration_ERT)
            
            imageGeneration_BTN = ml.ImageGeneration_BTN(primaryMainMenuFrame, self.prefix)
            imageGeneration_BTN.addListenerWidget(imageGenration_ERT)
            imageGeneration_BTN.addListenerWidget(addToTOCwImage_CHB)
            imageGeneration_BTN.addListenerWidget(textOnly_CHB)
            self.addWidget(imageGeneration_BTN)

            imageGenerationRestart_BTN =ml.ImageGenerationRestart_BTN(primaryMainMenuFrame, self.prefix)
            imageGenerationRestart_BTN.addListenerWidget(imageGenration_ERT)
            imageGenerationRestart_BTN.addListenerWidget(imageGeneration_BTN)
            self.addWidget(imageGenerationRestart_BTN)

            screenshotLocation_LBL = ml.ScreenshotLocation_LBL(primaryMainMenuFrame, self.prefix)
            self.addWidget(screenshotLocation_LBL)
            
            imageGenration_ERT.addListenerWidget(imageGeneration_BTN)
            imageGenration_ERT.addListenerWidget(imageGenerationRestart_BTN)
            imageGenration_ERT.addListenerWidget(addToTOCwImage_CHB)
            imageGenration_ERT.addListenerWidget(textOnly_CHB)

            imageGroupAdd_BTN = ml.ImageGroupAdd_BTN(primaryMainMenuFrame, self.prefix)
            self.addWidget(imageGroupAdd_BTN)

            # bottom frame

            switchLayout_BTN = commw.SwitchLayoutSectionVSMain_BTN(self.secondaryMainMenuMainLayoutFrame, self.prefix)
            self.addWidget(switchLayout_BTN)

            chooseOriginalMaterial_OM = ml.ChooseOriginalMaterial_OM(self.secondaryMainMenuMainLayoutFrame, self.prefix)
            self.addWidget(chooseOriginalMaterial_OM)

            layoutsSwitchOrigMatVSMain_BTN = commw.LayoutsSwitchOrigMatVSMain_BTN(self.secondaryMainMenuMainLayoutFrame, self.prefix)
            self.addWidget(layoutsSwitchOrigMatVSMain_BTN)

            exitApp_BTN = ml.ExitApp_BTN(self.secondaryMainMenuMainLayoutFrame, self.prefix)
            self.addWidget(exitApp_BTN)
 
            showTocWindow_BTN = commw.ShowTocWindow_BTN(self.secondaryMainMenuMainLayoutFrame, self.prefix)
            self.addWidget(showTocWindow_BTN)
            
            showAllSubsections_BTN = ml.ShowAllSubsections_BTN(self.secondaryMainMenuMainLayoutFrame, self.prefix)
            self.addWidget(showAllSubsections_BTN)

            addGlobalLink_ETR = commw.AddGlobalLink_ETR(self.secondaryMainMenuMainLayoutFrame, self.prefix, column = 0, row = 14)
            self.addWidget(addGlobalLink_ETR)

            addWebLink_BTN = commw.AddWebLink_BTN(self.secondaryMainMenuMainLayoutFrame, self.prefix, column = 2, row = 14)
            self.addWidget(addWebLink_BTN)

            showProof_BTN = commw.ShowProofs_BTN(self.secondaryMainMenuMainLayoutFrame, self.prefix, column = 5, row = 14)
            self.addWidget(showProof_BTN)

            showHideLinks_BTN = ml.ShowHideLinks_BTN(self.secondaryMainMenuMainLayoutFrame, self.prefix)
            self.addWidget(showHideLinks_BTN)


            imageGroupAdd_BTN.addListenerWidget(imageGenration_ERT)
            imageGroupAdd_BTN.addListenerWidget(imageGenerationRestart_BTN)

            # showFirstEntryOfTheCurrPage.addListenerWidget(tocBox_BOX)

            addWebLink_BTN.addListenerWidget(addGlobalLink_ETR)
            addWebLink_BTN.addListenerWidget(imageGenration_ERT)

            #
            # post init
            #

        def hide(self):
            self.secondaryMainMenuMainLayoutFrame.hide()
            return

        def show(self):

            self.secondaryMainMenuMainLayoutFrame.render()
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
            appDimensions = [monHalfWidth, 90]

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
            # self.winRoot.configureColumn(0, weight = 1)
            # self.winRoot.configureColumn(1, weight = 1)
            # self.winRoot.configureColumn(2, weight = 1)
            # self.winRoot.configureColumn(3, weight = 1)
            # self.winRoot.configureColumn(4, weight = 1)
            return super().show()
    

    class _AddModifySection(wm.MenuLayout_Interface):
        prefix = "_AddModifySectionLayout"

        def __init__(self, winRoot : ww.currUIImpl.RootWidget):
            #
            # pre init
            #

            #
            # init
            #

            super().__init__(winRoot, None)

            secondaryMainMenuFrame = wm.UI_generalManager.topLevelFrames["0100"].contentFrame

            renderData = {
                ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 1, "columnspan" : 1},
                ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
            }

            self.secondaryMainMenuModifySectionLayoutFrame = \
                                ww.currUIImpl.Frame(prefix = "", name = "_secoandaryManusModifySectionLayout", 
                                rootWidget = secondaryMainMenuFrame, 
                                renderData = renderData)
            self.secondaryMainMenuModifySectionLayoutFrame.render()

            switchLayout_BTN = amsl.SwitchLayoutSectionVSMain_amsl_BTN(self.secondaryMainMenuModifySectionLayoutFrame, self.prefix)
            self.addWidget(switchLayout_BTN)

            setSectionStartPage_ETR = amsl.SetSectionStartPage_ETR(self.secondaryMainMenuModifySectionLayoutFrame, self.prefix)
            self.addWidget(setSectionStartPage_ETR)

            setSectionName_ETR = amsl.SetSectionName_ETR(self.secondaryMainMenuModifySectionLayoutFrame, self.prefix)
            self.addWidget(setSectionName_ETR)

            currSectionPath_LBL = amsl.CurrSectionPath_LBL(self.secondaryMainMenuModifySectionLayoutFrame, self.prefix)
            self.addWidget(currSectionPath_LBL)
            
            newSectionPath_ETR = amsl.NewSectionPath_ETR(self.secondaryMainMenuModifySectionLayoutFrame, self.prefix)
            self.addWidget(newSectionPath_ETR)
            
            createNewSubsection_BTN = amsl.CreateNewSubsection_BTN(self.secondaryMainMenuModifySectionLayoutFrame, self.prefix)
            self.addWidget(createNewSubsection_BTN)

            createVideoSubsection_CHBX = amsl.CreateVideoSubsection_CHBX(self.secondaryMainMenuModifySectionLayoutFrame, self.prefix)
            self.addWidget(createVideoSubsection_CHBX)
            
            createNewSubsection_BTN.addListenerWidget(newSectionPath_ETR)
            createNewSubsection_BTN.addListenerWidget(setSectionStartPage_ETR)
            createNewSubsection_BTN.addListenerWidget(setSectionName_ETR)
            createNewSubsection_BTN.addListenerWidget(createVideoSubsection_CHBX)


            modifySubsection_BTN = amsl.ModifySubsection_BTN(self.secondaryMainMenuModifySectionLayoutFrame, self.prefix)
            self.addWidget(modifySubsection_BTN)

            modifySubsection_BTN.addListenerWidget(currSectionPath_LBL)
            modifySubsection_BTN.addListenerWidget(setSectionStartPage_ETR)
            modifySubsection_BTN.addListenerWidget(setSectionName_ETR)

            setSectionNoteAppLink_ETR = amsl.SetSectionNoteAppLink_ETR(self.secondaryMainMenuModifySectionLayoutFrame, self.prefix)
            self.addWidget(setSectionNoteAppLink_ETR)
            modifySubsection_BTN.addListenerWidget(setSectionNoteAppLink_ETR)

            modifyNotesAppLink_BTN = amsl.ModifyNotesAppLink_BTN(self.secondaryMainMenuModifySectionLayoutFrame, self.prefix)
            self.addWidget(modifyNotesAppLink_BTN)
            modifyNotesAppLink_BTN.addListenerWidget(setSectionNoteAppLink_ETR)

            moveToTOC_BTN = amsl.MoveToTOC_BTN(self.secondaryMainMenuModifySectionLayoutFrame, self.prefix)
            self.addWidget(moveToTOC_BTN)


        def hide(self):
            self.secondaryMainMenuModifySectionLayoutFrame.hide()

        def show(self):
            # self.winRoot.configureColumn(0, weight = 1)
            # self.winRoot.configureColumn(1, weight = 1)
            # self.winRoot.configureColumn(2, weight = 1)
            # self.winRoot.configureColumn(3, weight = 1)
            # self.winRoot.configureColumn(4, weight = 1)
            self.secondaryMainMenuModifySectionLayoutFrame.render()
            return super().show()

    class _AddModifyOrigMat(wm.MenuLayout_Interface):
        prefix = "_AddModifyOrigMatLayout"

        def __init__(self, winRoot : ww.currUIImpl.RootWidget):
            #
            # pre init
            #

            #
            # init
            #

            super().__init__(winRoot, None)

            
            secondaryMainMenuFrame = wm.UI_generalManager.topLevelFrames["0100"].contentFrame

            renderData = {
                ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 2, "columnspan" : 1},
                ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
            }

            self.secondaryMainMenuAddOrigMaterialFrame = \
                                ww.currUIImpl.Frame(prefix = "", name = "_secoandaryManusAddOrigMaterialLayout", 
                                rootWidget = secondaryMainMenuFrame, 
                                renderData = renderData)


            addOrigMaterial_BTN = \
                amom.AddOrigMaterial_BTN(self.secondaryMainMenuAddOrigMaterialFrame, self.prefix)
            self.addWidget(addOrigMaterial_BTN)

            fetOrigMatPath_ETR = \
                amom.GetOrigMatPath_ETR(self.secondaryMainMenuAddOrigMaterialFrame, self.prefix)
            self.addWidget(fetOrigMatPath_ETR)

            getOrigMatDestRelPath_ETR = \
                amom.GetOrigMatDestRelPath_ETR(self.secondaryMainMenuAddOrigMaterialFrame, self.prefix)
            self.addWidget(getOrigMatDestRelPath_ETR)

            getOrigMatName_ETR = \
                amom.GetOrigMatName_ETR(self.secondaryMainMenuAddOrigMaterialFrame, self.prefix)
            self.addWidget(getOrigMatName_ETR)

            addOrigMaterial_BTN.addListenerWidget(fetOrigMatPath_ETR)
            addOrigMaterial_BTN.addListenerWidget(getOrigMatDestRelPath_ETR)
            addOrigMaterial_BTN.addListenerWidget(getOrigMatName_ETR)

            layoutsSwitchOrigMatVSMain_BTN = \
                amom.LayoutsSwitchOrigMatVSMain_BTN(self.secondaryMainMenuAddOrigMaterialFrame, self.prefix)
            self.addWidget(layoutsSwitchOrigMatVSMain_BTN)

        def show(self):
            self.secondaryMainMenuAddOrigMaterialFrame.render()
            # self.winRoot.configureColumn(0, weight = 1)
            # self.winRoot.configureColumn(1, weight = 1)
            # self.winRoot.configureColumn(2, weight = 1)
            return super().show()
    
        def hide(self):
            self.secondaryMainMenuAddOrigMaterialFrame.hide()
            return super().hide()
    

    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class MathMenuManager(wm.MenuManager_Interface):
    def __init__(self, rootWidget):
        self.layouts = []
        self.isShown = False
    
        self.winRoot = commw.MainMenuRoot(rootWidget)
        layouts = self.layouts

        for lm in LayoutManagers.listOfLayouts():
            layouts.append(lm(self.winRoot))
        
        currLayout = None
        for layout in layouts:
            if type(layout) == LayoutManagers._Main:
                currLayout = layout
                break
        
        super().__init__(self.winRoot,
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


    def startAddingTheEntry(self):
        for layout in self.layouts:
            if type(layout) == LayoutManagers._Main:
                layout.addEntryETR.notify(ml.ImageGeneration_BTN)
                break
        

    def switchToSectionLayout(self):
        self.switchUILayout(LayoutManagers._Section)