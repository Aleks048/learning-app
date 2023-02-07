import os
import layouts.layouts_data as ld
import layouts.layouts_collection.layout_main as lm
import layouts.layouts_collection.layout_section as ls


class Data:
    listOfLayoutClasses = ld.listOfLayoutClasses

class Wr:
    class MainLayout(lm.MainLayout):
        pass
    
    class SectionLayout(ls.SectionLayout):
        pass
