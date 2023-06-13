import UI.widgets_manager as wm
import UI.widgets_wrappers as ww

import UI.widgets_collection.main.math.UI_layouts.common as com
import UI.widgets_collection.main.math.UI_layouts.mainLayout as ml
import UI.widgets_collection.main.math.UI_layouts.sectionLayout as sl
import UI.widgets_collection.main.math.UI_layouts.addModifySections as amsl
import UI.widgets_collection.main.math.UI_layouts.addModifyOrigMat as amom
import data.constants as dc


class LayoutManagers:
    class _Main(wm.MenuLayout_Interface):
        prefix = "_mainLayout"
        def __init__(self, winRoot : ww.currUIImpl.RootWidget):
            #
            # pre init
            #


            #
            # init
            #
            monitorSize = dc.MonitorSize.getData()
            monHalfWidth = int(monitorSize[0] / 2)
            appDimensions = [monHalfWidth, 530, monHalfWidth, 0]

            super().__init__(winRoot, appDimensions)

            # winRoot.configureColumn(0, weight = 1)
            # winRoot.configureColumn(1, weight = 1)
            # winRoot.configureColumn(2, weight = 3)
            # winRoot.configureColumn(3, weight = 1)

            tocBox_BOX = ml.TOC_BOX(winRoot, self.prefix)
            tocBox_BOX.populateTOC()
            self.addWidget(tocBox_BOX)
            
            addToTOC_CHB = ml.addToTOC_CHB(winRoot, self.prefix)
            self.addWidget(addToTOC_CHB)
            addToTOCwImage_CHB = ml.addToTOCwImage_CHB(winRoot, self.prefix)
            self.addWidget(addToTOCwImage_CHB)

            layouts_OM = com.Layouts_OM(winRoot, self.prefix)
            self.addWidget(layouts_OM)
            
            imageGenration_ERT = ml.ImageGeneration_ETR(winRoot, self.prefix)
            self.addWidget(imageGenration_ERT)
            
            imageGeneration_BTN = ml.ImageGeneration_BTN(winRoot, self.prefix)
            imageGeneration_BTN.addListenerWidget(imageGenration_ERT)
            imageGeneration_BTN.addListenerWidget(addToTOC_CHB)
            imageGeneration_BTN.addListenerWidget(addToTOCwImage_CHB)
            imageGeneration_BTN.addListenerWidget(tocBox_BOX)
            self.addWidget(imageGeneration_BTN)

            addExtraImage_BTN = ml.AddExtraImage_BTN(winRoot, self.prefix)
            addExtraImage_BTN.addListenerWidget(imageGenration_ERT)
            addExtraImage_BTN.addListenerWidget(imageGeneration_BTN)
            addExtraImage_BTN.addListenerWidget(tocBox_BOX)
            self.addWidget(addExtraImage_BTN)

            imageGenerationRestart_BTN =ml.ImageGenerationRestart_BTN(winRoot, self.prefix)
            imageGenerationRestart_BTN.addListenerWidget(imageGenration_ERT)
            imageGenerationRestart_BTN.addListenerWidget(imageGeneration_BTN)
            self.addWidget(imageGenerationRestart_BTN)

            screenshotLocation_LBL = ml.ScreenshotLocation_LBL(winRoot, self.prefix)
            self.addWidget(screenshotLocation_LBL)

            chooseTopSection_OM = ml.ChooseTopSection_OM(winRoot, self.prefix)
            self.addWidget(chooseTopSection_OM)
            chooseTopSection_OM.addListenerWidget(imageGenration_ERT)
            
            chooseSubsection_OM = ml.ChooseSubsection_OM(winRoot, self.prefix)
            self.addWidget(chooseSubsection_OM)
            
            chooseSubsection_OM.addListenerWidget(imageGenration_ERT)
            
            chooseTopSection_OM.addListenerWidget(chooseSubsection_OM)
            chooseSubsection_OM.addListenerWidget(chooseTopSection_OM)
            chooseTopSection_OM.addListenerWidget(screenshotLocation_LBL)
            chooseSubsection_OM.addListenerWidget(screenshotLocation_LBL)

            switchLayout_BTN = com.SwitchLayoutSectionVSMain_BTN(winRoot, self.prefix)
            self.addWidget(switchLayout_BTN)

            switchToCurrSectionLayout_BTN = ml.SwitchToCurrSectionLayout_BTN(winRoot, self.prefix)
            self.addWidget(switchToCurrSectionLayout_BTN)

            chooseOriginalMaterial_OM = ml.ChooseOriginalMaterial_OM(winRoot, self.prefix)
            self.addWidget(chooseOriginalMaterial_OM)

            layoutsSwitchOrigMatVSMain_BTN = com.LayoutsSwitchOrigMatVSMain_BTN(winRoot, self.prefix)
            self.addWidget(layoutsSwitchOrigMatVSMain_BTN)

            exitApp_BTN = ml.ExitApp_BTN(winRoot, self.prefix)
            self.addWidget(exitApp_BTN)
            exitApp_BTN.addListenerWidget(tocBox_BOX)
 
            showTocWindow_BTN = com.ShowTocWindow_BTN(winRoot, self.prefix)
            self.addWidget(showTocWindow_BTN)
            
            reAddAllNotesFromTheOMPage_BTN = ml.ReAddAllNotesFromTheOMPage_BTN(winRoot, self.prefix)
            self.addWidget(reAddAllNotesFromTheOMPage_BTN)


            saveImage_BTN = com.ImageSave_BTN(winRoot, self.prefix, column = 5, row = 14)
            self.addWidget(saveImage_BTN)
            saveImage_BTN.addListenerWidget(tocBox_BOX)


            sourceImageLinks_OM = com.SourceImageLinks_OM(winRoot, self.prefix, column = 4, row = 13)
            self.addWidget(sourceImageLinks_OM)
            targetImageLinks_OM = com.TargetImageLinks_OM(winRoot, self.prefix, column = 2, row = 13)
            self.addWidget(targetImageLinks_OM)
            targetSubsection_OM = com.TargetSubection_OM(winRoot, self.prefix, column = 1, row = 13)
            self.addWidget(targetSubsection_OM)
            targetTopSection_OM = com.TargetTopSection_OM(winRoot, self.prefix, column = 0, row = 13)
            self.addWidget(targetTopSection_OM)
            addGlobalLink_BTN = com.AddGlobalLink_BTN(winRoot, self.prefix, column = 2, row = 14)
            self.addWidget(addGlobalLink_BTN)
            addGlobalLink_ETR = com.AddGlobalLink_ETR(winRoot, self.prefix, column = 0, row = 14)
            self.addWidget(addGlobalLink_ETR)

            latestExtraImForEntry_LBL = ml.LatestExtraImForEntry_LBL(winRoot, self.prefix)
            self.addWidget(latestExtraImForEntry_LBL)

            addGlobalLink_BTN.addListenerWidget(addGlobalLink_ETR)
            addGlobalLink_BTN.addListenerWidget(sourceImageLinks_OM)

            targetSubsection_OM.addListenerWidget(targetImageLinks_OM)
            targetImageLinks_OM.addListenerWidget(targetSubsection_OM)
            targetImageLinks_OM.addListenerWidget(addGlobalLink_ETR)
            targetSubsection_OM.addListenerWidget(addGlobalLink_ETR)

            targetTopSection_OM.addListenerWidget(targetSubsection_OM)
            targetTopSection_OM.addListenerWidget(addGlobalLink_ETR)

            imageGeneration_BTN.addListenerWidget(sourceImageLinks_OM)

            sourceImageLinks_OM.addListenerWidget(latestExtraImForEntry_LBL)
            latestExtraImForEntry_LBL.addListenerWidget(sourceImageLinks_OM)
            addExtraImage_BTN.addListenerWidget(sourceImageLinks_OM)
            imageGeneration_BTN.addListenerWidget(sourceImageLinks_OM)

            #
            # post init
            #
            targetSubsection_OM.cmd()
            targetImageLinks_OM.cmd()

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

            addGlobalLink_ETR = com.AddGlobalLink_ETR(winRoot, self.prefix)
            self.addWidget(addGlobalLink_ETR)

            layouts_OM = com.Layouts_OM(winRoot, self.prefix, 0, 0)
            self.addWidget(layouts_OM)

            showProof_BTN = sl.ShowProofs_BTN(winRoot, self.prefix)
            self.addWidget(showProof_BTN)

            saveImage_BTN = com.ImageSave_BTN(winRoot, self.prefix)
            self.addWidget(saveImage_BTN)

            rebuildCurrSection_BTN = sl.RebuildCurrSection_BTN(winRoot, self.prefix)
            self.addWidget(rebuildCurrSection_BTN)

            targetTopSection_OM = com.TargetTopSection_OM(winRoot, self.prefix)
            self.addWidget(targetTopSection_OM)
            
            targetSubsection_OM = com.TargetSubection_OM(winRoot, self.prefix)
            self.addWidget(targetSubsection_OM)

            targetTopSection_OM.addListenerWidget(targetSubsection_OM)
            targetTopSection_OM.addListenerWidget(addGlobalLink_ETR)

            targetImageLinks_OM = com.TargetImageLinks_OM(winRoot, self.prefix)
            self.addWidget(targetImageLinks_OM)

            targetSubsection_OM.addListenerWidget(targetImageLinks_OM)
            targetImageLinks_OM.addListenerWidget(targetSubsection_OM)
            targetImageLinks_OM.addListenerWidget(addGlobalLink_ETR)
            targetSubsection_OM.addListenerWidget(addGlobalLink_ETR)

            sourceImageLinks_OM = com.SourceImageLinks_OM(winRoot, self.prefix)
            self.addWidget(sourceImageLinks_OM)

            addGlobalLink_BTN = com.AddGlobalLink_BTN(winRoot, self.prefix)
            self.addWidget(addGlobalLink_BTN)

            addGlobalLink_BTN.addListenerWidget(addGlobalLink_ETR)
            addGlobalLink_BTN.addListenerWidget(sourceImageLinks_OM)

            switchToCurrMainLayout_BTN = sl.SwitchToCurrMainLayout_BTN(winRoot, self.prefix)
            self.addWidget(switchToCurrMainLayout_BTN)

            showTocWindow_BTN = com.ShowTocWindow_BTN(winRoot, self.prefix, row=0)
            self.addWidget(showTocWindow_BTN)
            #
            # post init
            #
            targetSubsection_OM.cmd()
            targetImageLinks_OM.cmd()
        
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

            chooseTopSection_OM = amsl.ChooseTopSection_OM(winRoot, self.prefix)
            self.addWidget(chooseTopSection_OM)

            chooseSubsection_OM = amsl.ChooseSubsection_OM(winRoot, self.prefix)
            self.addWidget(chooseSubsection_OM)
            
            chooseTopSection_OM.addListenerWidget(chooseSubsection_OM)
            chooseTopSection_OM.addListenerWidget(currSectionPath_LBL)
            chooseTopSection_OM.addListenerWidget(setSectionName_ETR)
            chooseTopSection_OM.addListenerWidget(setSectionStartPage_ETR)

            chooseSubsection_OM.addListenerWidget(currSectionPath_LBL)
            chooseSubsection_OM.addListenerWidget(setSectionName_ETR)
            chooseSubsection_OM.addListenerWidget(setSectionStartPage_ETR)


            modifySubsection_BTN = amsl.ModifySubsection_BTN(winRoot, self.prefix)
            self.addWidget(modifySubsection_BTN)

            modifySubsection_BTN.addListenerWidget(currSectionPath_LBL)
            modifySubsection_BTN.addListenerWidget(chooseSubsection_OM)
            modifySubsection_BTN.addListenerWidget(chooseTopSection_OM)
            modifySubsection_BTN.addListenerWidget(setSectionStartPage_ETR)
            modifySubsection_BTN.addListenerWidget(setSectionName_ETR)

            setSectionNoteAppLink_ETR = amsl.SetSectionNoteAppLink_ETR(winRoot, self.prefix)
            self.addWidget(setSectionNoteAppLink_ETR)
            modifySubsection_BTN.addListenerWidget(setSectionNoteAppLink_ETR)
            chooseSubsection_OM.addListenerWidget(setSectionNoteAppLink_ETR)

            modifyNotesAppLink_BTN = amsl.ModifyNotesAppLink_BTN(winRoot, self.prefix)
            self.addWidget(modifyNotesAppLink_BTN)
            modifyNotesAppLink_BTN.addListenerWidget(setSectionNoteAppLink_ETR)
            modifyNotesAppLink_BTN.addListenerWidget(chooseSubsection_OM)
            modifyNotesAppLink_BTN.addListenerWidget(chooseTopSection_OM)

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
    def __init__(self):
        winRoot = com.MainMenuRoot(0, 0)
        layouts = []

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
    
    def switchToMainLayout(self):
        self.switchUILayout(LayoutManagers._Main)
    
    def switchToSectionLayout(self):
        self.switchUILayout(LayoutManagers._Section)