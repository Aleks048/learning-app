import unittest
import os

import unittest

import UI.widgets_manager as wm
import UI.widgets_messages as wmes
import file_system.file_system_main as fs
import _utils._utils_main as _u


testBookName = "b_analysis_test"
testBookPath = os.getenv("BOOKS_ROOT_PATH") + testBookName

class Test_WidgetsManager_StartupMenu(unittest.TestCase):
    def setUp(self):
        _u.Settings.Book.setCurrentBook(testBookName, testBookPath)

    # def test_StartupMenu(self):

    #     # _waitDummy = wmes.ConfirmationMenu.createMenu("tests", lambda *args: None)

    #     # _waitDummy = wmes.ShowMessageMenu.createMenu("tetst")
        
    #     _waitDummy = wm.StartupMenu.createMenu()

    #
    # TEST WIDGETS
    #
    

    def test_MainMenu(self):

        # _waitDummy = wmes.ConfirmationMenu.createMenu("tests", lambda *args: None)

        # _waitDummy = wmes.ShowMessageMenu.createMenu("tetst")
        currentTopSectionPath = "2"
        currentSectionPath = "2.intro.pass"
        currImIdx_ID = fs.SectionInfoStructure.SecPubProp.imIndex_ID
        fs.BookInfoStructure.updateProperty(fs.BookInfoStructure.PubProp.currTopSection_ID, 
                                            currentTopSectionPath)
        sections_ID = fs.BookInfoStructure.PubProp.sections_ID
        sections = fs.BookInfoStructure.readProperty(sections_ID)
        sections["2"]["prevSubsectionPath"] = "2.intro.pass"
        sections["3"]["prevSubsectionPath"] = "3.intro.3pass"  
        sections["4"]["prevSubsectionPath"] = "4.intro.2pass"
        fs.BookInfoStructure.updateProperty(sections_ID, sections)
        fs.BookInfoStructure.updateProperty(fs.BookInfoStructure.PubProp.currSection_ID, 
                                            currentSectionPath)
        fs.SectionInfoStructure.updateProperty(currentSectionPath, currImIdx_ID, "3")
        
        _waitDummy = wm.MainMenu.createMenu()


# class Test_WidgetsManager_WarningMessage(unittest.TestCase):
    
#     def test_ShowMessagemenu(self):


# # Different kinds of asserts we can have:
# #     self.assertEqual('foo'.upper(), 'FOO')
# #     self.assertTrue('FOO'.isupper())
# #     self.assertFalse('Foo'.isupper())
# #     with self.assertRaises(TypeError):
# #         s.split(2)

if __name__ == '__main__':
    unittest.main()