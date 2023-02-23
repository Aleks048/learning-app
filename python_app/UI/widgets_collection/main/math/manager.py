import tkinter as tk

import _utils._utils_main as _u
import _utils.logging as log
import layouts.layouts_manager as lm

import UI.widgets_manager as wm
import UI.widgets_utils as wu
import UI.widgets_wrappers as ww

import UI.widgets_collection.main.math.layouts.common as com
import UI.widgets_collection.main.math.layouts.mainLayout as ml
import UI.widgets_collection.main.math.layouts.sectionLayout as sl
import data.constants as dc

class LayoutManagers:
    class _Main(wm.MenuLayout_Interface):
        prefix = "_mainLayout"
        def __init__(self, winRoot : ww.currUIImpl.RootWidget):
            monitorSize = dc.MonitorSize.getData()
            monHalfWidth = int(monitorSize[0] / 2)
            appDimensions = [monHalfWidth, 90, monHalfWidth, 0]

            super().__init__(winRoot, appDimensions)

            winRoot.configureColumn(0, weight = 1)
            winRoot.configureColumn(1, weight = 1)
            winRoot.configureColumn(2, weight = 3)
            winRoot.configureColumn(3, weight = 1)

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
            self.addWidget(imageGeneration_BTN)

            addExtraImage = ml.AddExtraImage_BTN(winRoot, self.prefix)
            self.addWidget(addExtraImage)


            imageGenerationRestartBTN =ml.ImageGenerationRestart_BTN(winRoot, self.prefix)
            imageGenerationRestartBTN.addListenerWidget(imageGenration_ERT)
            imageGenerationRestartBTN.addListenerWidget(imageGeneration_BTN)
            self.addWidget(imageGenerationRestartBTN)

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
            chooseSubsection_OM.addListenerWidget(screenshotLocation_LBL)

            switchLayout_BTN = com.SwitchLayoutSectionVSMain_BTN(winRoot, self.prefix)
            self.addWidget(switchLayout_BTN)

        def show(self):
            self.winRoot.configureColumn(0, weight = 1)
            self.winRoot.configureColumn(1, weight = 1)
            self.winRoot.configureColumn(2, weight = 3)
            self.winRoot.configureColumn(3, weight = 1)
            return super().show()
    class _Section(wm.MenuLayout_Interface):
        prefix = "_sectionLayout"

        def __init__(self, winRoot : ww.currUIImpl.RootWidget):
            monitorSize = dc.MonitorSize.getData()
            monHalfWidth = int(monitorSize[0] / 2)
            appDimensions = [monHalfWidth, 90, monHalfWidth, 0]

            super().__init__(winRoot, appDimensions)

            addGlobalLink_ETR = sl.AddGlobalLink_ETR(winRoot, self.prefix)
            self.addWidget(addGlobalLink_ETR)
            
            switchLayout_BTN = com.SwitchLayoutSectionVSMain_BTN(winRoot, self.prefix)
            self.addWidget(switchLayout_BTN)

            layouts_OM = com.Layouts_OM(winRoot, self.prefix)
            self.addWidget(layouts_OM)

            showProof_BTN = sl.ShowProofs_BTN(winRoot, self.prefix)
            self.addWidget(showProof_BTN)

            saveImage_BTN = sl.ImageSave_BTN(winRoot, self.prefix)
            self.addWidget(saveImage_BTN)

            rebuildCurrSection_BTN = sl.RebuildCurrSection_BTN(winRoot, self.prefix)
            self.addWidget(rebuildCurrSection_BTN)

            targetTopSection_OM = sl.TargetTopSection_OM(winRoot, self.prefix)
            self.addWidget(targetTopSection_OM)
            
            targetSubsection_OM = sl.TargetSubection_OM(winRoot, self.prefix)
            self.addWidget(targetSubsection_OM)

            targetTopSection_OM.addListenerWidget(targetSubsection_OM)
            targetTopSection_OM.addListenerWidget(addGlobalLink_ETR)

            targetImageLinks_OM = sl.TargetImageLinks_OM(winRoot, self.prefix)
            self.addWidget(targetImageLinks_OM)

            targetSubsection_OM.addListenerWidget(targetImageLinks_OM)
            targetSubsection_OM.addListenerWidget(addGlobalLink_ETR)
            targetImageLinks_OM.addListenerWidget(targetSubsection_OM)
            targetImageLinks_OM.addListenerWidget(addGlobalLink_ETR)

            sourceImageLinks_OM = sl.SourceImageLinks_OM(winRoot, self.prefix)
            self.addWidget(sourceImageLinks_OM)

            addGlobalLink_BTN = sl.AddGlobalLink_BTN(winRoot, self.prefix)
            self.addWidget(addGlobalLink_BTN)
            
            addGlobalLink_BTN.addListenerWidget(addGlobalLink_ETR)
            addGlobalLink_BTN.addListenerWidget(sourceImageLinks_OM)

    
    @classmethod
    def listOfLayouts(cls):
        results = []
        for attrname in dir(cls):
            obj = getattr(cls, attrname)
            if isinstance(obj, type) and issubclass(obj, wm.MenuLayout_Interface):
                results.append(obj)
        return results

class MathMenuManager(wm.MenuManager_Interface):
    prefix = "_MainMathMenu_"

    @classmethod
    def createMenu(cls):
        super().createMenu()

        cls.winRoot = com.MainMenuRoot(0, 0)

        for lm in LayoutManagers.listOfLayouts():
            cls.layouts.append(lm(cls.winRoot))
        
        cls.currLayout = cls.layouts[0]