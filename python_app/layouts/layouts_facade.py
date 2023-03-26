import os
import layouts.layouts_data as ld
import layouts.layouts_manager as lm
import layouts.layouts_collection.layout_main as lma
import layouts.layouts_collection.layout_section as ls


class Data:
    listOfLayoutClasses = ld.listOfLayoutClasses

class Wr:
    class LayoutsManager(lm.LayoutsManager):
        pass

    class MainLayout(lma.MainLayout):
        pass
    
    class SectionLayout(ls.SectionLayout):
        pass
