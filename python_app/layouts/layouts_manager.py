import os
import layouts.layouts_data as ld
import layouts.layouts_main as lm


class Data:
    listOfLayoutClasses = ld.listOfLayoutClasses

class Wr:
    class MainLayout(lm.MainLayout):
        pass
    
    class SectionLayout(lm.SectionLayout):
        pass
