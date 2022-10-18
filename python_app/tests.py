import tkinter as tk

from UI.widgets import *
from file_system.file_system_main import BookInfoStructure, SectionInfoStructure, TOCStructure
from layouts.layouts_main import *
from _utils._utils_main import *
from layouts import *
from file_system import *

import unittest


# filesystem

'''
bookInfo structure
'''


testBookPath = os.getenv("BOOKS_ROOT_PATH") + "/b_analysis_test/"


class Test_BookInfoStructure(unittest.TestCase):

    def test_createStructure(self):
        """
        createBookInfoStrunture
        """
        expectedFilePath = testBookPath + BookInfoStructure._getRelFilepath()
        
        expectedFileDir = "/".join(expectedFilePath.split("/")[:-1])
        os.system("rm -rf " + expectedFileDir)
        
        BookInfoStructure.createStructure(expectedFilePath)

        # we created file at the expected path
        self.assertTrue(os.path.isfile(expectedFilePath))
    
    def test_updateProperties(self):
        BookInfoStructure.updateProperty(BookInfoStructure.sections_prefix_ID, "te")
        prefix = BookInfoStructure.readProperty(BookInfoStructure.sections_prefix_ID)
        self.assertEqual(prefix, "te")
        


class Test_SectionsInfoStructure(unittest.TestCase):

    def test_createStructure(self):    
        """
        createSectionsInfoStructure
        """
        BookInfoStructure.updateProperty(BookInfoStructure.sections_prefix_ID, "te")
        
        
        os.system("rm -rf " + testBookPath + BookInfoStructure.sectionsInfoBaseRelPath)
        
        SectionInfoStructure.createStructure("2.intro.pass")
        SectionInfoStructure.createStructure("2.intro.pass2")
        SectionInfoStructure.createStructure("2.intro2.pass.ando")
        SectionInfoStructure.createStructure("3.intro.pass")
        SectionInfoStructure.createStructure("3.intro.3pass")
        SectionInfoStructure.createStructure("4.intro.pass")
        SectionInfoStructure.createStructure("4.intro.2pass")
    
    def test_updateProperties(self):
        SectionInfoStructure.updateProperty("2.intro", "_imIndex", "1")
        imId = SectionInfoStructure.readProperty("2.intro", "_imIndex")
        self.assertEqual(imId, "1")
        SectionInfoStructure.updateProperty("2.intro.pass", "_imIndex", "1")
        imId = SectionInfoStructure.readProperty("2.intro.pass", "_imIndex")
        self.assertEqual(imId, "1")
        


class Test_TOCStructure(unittest.TestCase):

    def test_createTOCStructure(self):

        os.system("rm -rf " + testBookPath + BookInfoStructure.TOCbaseRelPath + "/*.tex")

        TOCStructure.createTOCStructure()


# Different kinds of asserts we can have: 
#     self.assertEqual('foo'.upper(), 'FOO')
#     self.assertTrue('FOO'.isupper())
#     self.assertFalse('Foo'.isupper())
#     with self.assertRaises(TypeError):
#         s.split(2)

if __name__ == '__main__':
    unittest.main()