import UI.widgets_wrappers as ww
import UI.widgets_utils as wu
import UI.widgets_collection.main.math.manager as mmm
import layouts.layouts_manager as lm
import _utils._utils_main as _u


class MainMenuRoot(ww.currUIImpl.RootWidget):
    pass


class Layouts_OM(ww.currUIImpl.OptionMenu):
    def __init__(self, patentWidget, prefix):
        self.layoutOptions = {
            "Main" : [mmm.LayoutManagers._Main, lm.Wr.MainLayout], 
            "Section" : [mmm.LayoutManagers._Section, lm.Wr.SectionLayout], 
            "WholeVSCode": None}
        
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }
        name = "_layouts_optionMenu"
        listOfLayouts = self.layoutOptions.keys()

        super().__init__(prefix, 
                        name, 
                        listOfLayouts,
                        patentWidget, 
                        renderData, 
                        self.cmd)

        self.setData(list(listOfLayouts)[0])
    
    def cmd(self):
        layoutToSwitchTo = self.getData()
        mmm.MathMenuManager.switchUILayout(self.layoutOptions[layoutToSwitchTo][0])
        self.layoutOptions[layoutToSwitchTo][1].set()


class SwitchLayoutSectionVSMain_BTN(ww.currUIImpl.Button):
    labelOptions = ["Add/Modify", "Main"]

    def __init__(self, patentWidget, prefix, data = None, name = None, text = None):
        if data == None:
            data = {
                ww.Data.GeneralProperties_ID : {"column" : 4, "row" : 0},
                ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
            }
        if name == None:
            name = "_chooseSubsectionLayout_BTN"
        
        if text == None:
            text = self.labelOptions[0]

        super().__init__(prefix, 
                        name,
                        text, 
                        patentWidget,
                        data, 
                        self.cmd)
    
    def cmd(self):
        # wu.hideAllWidgets(self.rootWidget)
        if not _u.Settings.UI.showMainWidgetsNext:
            # show the sections UI
            mmm.MathMenuManager.switchUILayout(mmm.LayoutManagers._AddModifySection)
            
            #TODO: switch other apps layout

            self.updateLabel(self.labelOptions[0])
            _u.Settings.UI.showMainWidgetsNext = True


        else:
            mmm.MathMenuManager.switchUILayout(mmm.LayoutManagers._Main)

            self.updateLabel(self.labelOptions[1]) 
            _u.Settings.UI.showMainWidgetsNext = False