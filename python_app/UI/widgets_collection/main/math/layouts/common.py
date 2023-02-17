import UI.widgets_wrappers as ww
import UI.widgets_utils as wu
import UI.widgets_collection.main.math.manager as mmm
import layouts.layouts_manager as lm


class MainMenuRoot(ww.currUIImpl.RootWidget):
    pass


class Layouts_OM(ww.currUIImpl.OptionMenu):
    def __init__(self, patentWidget, prefix):
        self.layoutOptions = {
            "Main" : [mmm.LayoutManagers._Main.name, lm.Wr.MainLayout], 
            "Section" : [mmm.LayoutManagers._Section.name, lm.Wr.SectionLayout], 
            "WholeVSCode": None}
        
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 1, "row" : 0},
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