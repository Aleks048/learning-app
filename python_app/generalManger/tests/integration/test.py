import shutil
import unittest
import os
import pathlib

import UI.widgets_facade as wf
import outside_calls.outside_calls_facade as ocf

import generalManger.generalManger as gm

import _utils.logging as log

def createRootWidget(width = 100, height = 100):
    return wf.Wr.WidgetWrappers.RootWidget(width, height)

TEST_BOOK_PATH = os.path.join(pathlib.Path(__file__).parent.resolve(), 
                              "data/testBook")
TEST_ORIGINAL_MATERIAL_PATH = os.path.join(pathlib.Path(__file__).parent.resolve(), 
                                           "data/test.pdf")

class AddBookCDM(unittest.TestCase):
    def test_addBook(self):
        shutil.rmtree(TEST_BOOK_PATH, ignore_errors = True)
        gm.GeneralManger.AddNewBook("test",
                                    TEST_BOOK_PATH,
                                    TEST_ORIGINAL_MATERIAL_PATH,
                                    "main/test"
                                    )

        self.assertTrue(\
            ocf.Wr.FsAppCalls.checkIfFileOrDirExists(TEST_BOOK_PATH))
        self.assertTrue(\
            ocf.Wr.FsAppCalls.checkIfFileOrDirExists(os.path.join(TEST_BOOK_PATH, "bookInfo", "bookInfo.json")))
        self.assertTrue(\
            ocf.Wr.FsAppCalls.checkIfFileOrDirExists(os.path.join(TEST_BOOK_PATH, "originalMaterial/main/test/test.pdf")))
        self.assertTrue(\
            ocf.Wr.FsAppCalls.checkIfFileOrDirExists(os.path.join(TEST_BOOK_PATH, "subsections")))

if __name__ == '__main__':
    unittest.main()