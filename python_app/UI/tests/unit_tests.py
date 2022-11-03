import unittest
import os

import unittest

import UI.widgets_manager as wm
import UI.widgets_messages as wmes
import file_system.file_system_manager as fsm
import _utils._utils_main as _u


testBookName = "b_analysis_test"
testBookPath = os.getenv("BOOKS_ROOT_PATH") + testBookName

class Test_WidgetsManager_StartupMenu(unittest.TestCase):
    def setUp(self):
        _u.Settings.Book.setCurrentBook(testBookName, testBookPath)

    # def test_StartupMenu(self):

    #     # _waitDummy = wmes.ConfirmationMenu.createMenu("tests", lambda *args: None)

    #     # _waitDummy = wmes.MessageMenu.createMenu("tetst")
        
    #     _waitDummy = wm.StartupMenu.createMenu()

    #
    # TEST WIDGETS
    #
    

    def test_MainMenu(self):

        # _waitDummy = wmes.ConfirmationMenu.createMenu("tests", lambda *args: None)

        # _waitDummy = wmes.MessageMenu.createMenu("tetst")
        currentTopSectionPath = "2"
        currentSection2Path = "2.intro.pass"
        currentSection3Path = "3.intro.3pass"
        currentSection4Path = "4.intro.2pass"
        currImIdx_ID = fsm.PropIDs.SectionProperties_IDs.imIndex_ID
        fsm.Wrappers.BookInfoStructure.updateProperty(fsm.PropIDs.BookProperties_IDs.currTopSection_ID, 
                                            currentTopSectionPath)
        fsm.Wrappers.BookInfoStructure.updateProperty(fsm.PropIDs.BookProperties_IDs.currSection_ID, 
                                            currentSection2Path)
        sections_ID = fsm.PropIDs.BookProperties_IDs.sections_ID
        sections = fsm.Wrappers.BookInfoStructure.readProperty(sections_ID)
        sections["2"]["prevSubsectionPath"] = "2.intro.pass"
        sections["3"]["prevSubsectionPath"] = "3.intro.3pass"  
        sections["4"]["prevSubsectionPath"] = "4.intro.2pass"
        fsm.Wrappers.BookInfoStructure.updateProperty(sections_ID, sections)
        fsm.Wrappers.SectionInfoStructure.updateProperty(currentSection2Path, currImIdx_ID, "2")
        fsm.Wrappers.SectionInfoStructure.updateProperty(currentSection3Path, currImIdx_ID, "3")
        fsm.Wrappers.SectionInfoStructure.updateProperty(currentSection4Path, currImIdx_ID, "4")

        _u.Settings.updateProperty(_u.Settings.PubProp.currLayout_ID, "Main")
        
        _waitDummy = wm.MainMenu.createMenu()


# class Test_WidgetsManager_WarningMessage(unittest.TestCase):
    
#     def test_MessageMenu(self):


# # Different kinds of asserts we can have:
# #     self.assertEqual('foo'.upper(), 'FOO')
# #     self.assertTrue('FOO'.isupper())
# #     self.assertFalse('Foo'.isupper())
# #     with self.assertRaises(TypeError):
# #         s.split(2)

if __name__ == '__main__':
    unittest.main()