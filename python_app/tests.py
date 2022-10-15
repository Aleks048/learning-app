import tkinter as tk

from UI.widgets import *
import file_system
from file_system.file_system_main import BookInfoStructure, SectionInfoStructure, TOCStructure
from layouts.layouts_main import *
from _utils._utils_main import *
from layouts import *
from file_system import *



# filesystem

'''
bookInfo structure
'''


testBookPath = os.getenv("BOOKS_ROOT_PATH") + "/b_analysis_test/"

import unittest

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
        SectionInfoStructure.createStructure("2.intro.pass")
    
    def test_updateProperties(self):
        SectionInfoStructure.updateProperty("2.intro", "_imIndex", "1")
        imId = SectionInfoStructure.readProperty("2.intro", "_imIndex")
        self.assertEqual(imId, "1")
        SectionInfoStructure.updateProperty("2.intro.pass", "_imIndex", "1")
        imId = SectionInfoStructure.readProperty("2.intro.pass", "_imIndex")
        self.assertEqual(imId, "1")
        


# class Test_TOCStructure(unittest.TestCase):

#     def test_createTOCStructure(self):

#         TOCStructure.createTOCStructure(str(2), testBookPath)


# Different kinds of asserts we can have: 
#     self.assertEqual('foo'.upper(), 'FOO')
#     self.assertTrue('FOO'.isupper())
#     self.assertFalse('Foo'.isupper())
#     with self.assertRaises(TypeError):
#         s.split(2)

if __name__ == '__main__':
    unittest.main()