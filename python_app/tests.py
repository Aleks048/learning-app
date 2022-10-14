import tkinter as tk

from UI.widgets import *
import file_system
from file_system.file_system_main import BookInfoStructure, TOCStructure
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
        # create bookInfo file
        expectedFilePath = testBookPath + BookInfoStructure._getRelFilepath()
        
        expectedFileDir = "/".join(expectedFilePath.split("/")[:-1])
        os.system("rm -rf " + expectedFileDir)
        
        BookInfoStructure.createStructure(expectedFilePath)

        # we created file at the expected path
        self.assertTrue(os.path.isfile(expectedFilePath))

        


class Test_TOCStructure(unittest.TestCase):

    def test_createTOCStructure(self):

        TOCStructure.createTOCStructure(str(2), testBookPath)


# Different kinds of asserts we can have: 
#     self.assertEqual('foo'.upper(), 'FOO')
#     self.assertTrue('FOO'.isupper())
#     self.assertFalse('Foo'.isupper())
#     with self.assertRaises(TypeError):
#         s.split(2)

if __name__ == '__main__':
    unittest.main()