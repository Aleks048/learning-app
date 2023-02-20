import tkinter as tk

import _utils._utils_main as _u
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
        name = __name__
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
            self.addWidget(chooseSubsection_OM)
            
            chooseTopSection_OM.addListenerWidget(chooseSubsection_OM)
            chooseSubsection_OM.addListenerWidget(chooseTopSection_OM)
            chooseTopSection_OM.addListenerWidget(screenshotLocation_LBL)
            chooseSubsection_OM.addListenerWidget(screenshotLocation_LBL)

            switchLayout_BTN = com.SwitchLayoutSectionVSMain_BTN(winRoot, self.prefix)
            self.addWidget(switchLayout_BTN)


    class _Section(wm.MenuLayout_Interface):
        prefix = "_sectionLayout"
        name = __name__
        @classmethod
        def __init__(self, winRoot):
            pass
    
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