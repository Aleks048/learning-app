import tkinter as tk

# from UI.widgets_collection import *
from file_system.file_system_main import BookInfoStructure, OriginalMaterialStructure, SectionInfoStructure, TOCStructure
from file_system.file_system_manager import addSectionForCurrBook, createNewBook
from _utils._utils_main import *
from layouts import *
from file_system import *
from file_system import file_system_manager as fsm

import unittest

testBookName = "b_analysis_test"
testBookPath = os.getenv("BOOKS_ROOT_PATH") + testBookName
test2BookName = "b_newBook_test"
test2BookPath = os.getenv("BOOKS_ROOT_PATH") + "/" + test2BookName + "/"
test3BookName = "b_newBook2_test"
test3BookPath = os.getenv("BOOKS_ROOT_PATH") + "/" + test3BookName + "/"


class Test_BookInfoStructure(unittest.TestCase):

    def setUp(self):
        Settings.Book.setCurrentBook(testBookName, testBookPath)

    def test_createStructure(self):
        expectedFilePath = testBookPath + BookInfoStructure._getRelFilepath()

        expectedFileDir = "/".join(expectedFilePath.split("/")[:-1])
        os.system("rm -rf " + expectedFileDir)

        BookInfoStructure.createStructure(expectedFilePath)

        # we created file at the expected path
        self.assertTrue(os.path.isfile(expectedFilePath))

    def test_updateProperties(self):
        BookInfoStructure.updateProperty(BookInfoStructure.PubProp.sections_prefix_ID, "te")
        prefix = BookInfoStructure.readProperty(BookInfoStructure.PubProp.sections_prefix_ID)
        self.assertEqual(prefix, "te")


class Test_SectionsInfoStructure(unittest.TestCase):

    def setUp(self):
        Settings.Book.setCurrentBook(testBookName, testBookPath)
    
    def test_createStructure(self):
        BookInfoStructure.updateProperty(BookInfoStructure.PubProp.sections_prefix_ID, "te")

        os.system("rm -rf " + testBookPath + BookInfoStructure.sectionsInfoBaseRelPath)

        SectionInfoStructure.createStructure()

        SectionInfoStructure.addSection("2.intro.pass")
        BookInfoStructure.addSection("2.intro.pass")
        SectionInfoStructure.addSection("2.intro.pass2")
        BookInfoStructure.addSection("2.intro.pass2")
        SectionInfoStructure.addSection("2.intro2.pass.ando")
        BookInfoStructure.addSection("2.intro2.pass.ando")
        SectionInfoStructure.addSection("2.intro2.pass2.ando")
        BookInfoStructure.addSection("2.intro2.pass2.ando")
        SectionInfoStructure.addSection("2.intro2.pass2.anda")
        BookInfoStructure.addSection("2.intro2.pass2.anda")
        SectionInfoStructure.addSection("3.intro.pass")
        BookInfoStructure.addSection("3.intro.pass")
        SectionInfoStructure.addSection("3.intro.3pass")
        BookInfoStructure.addSection("3.intro.3pass")
        SectionInfoStructure.addSection("4.intro.pass")
        BookInfoStructure.addSection("4.intro.pass")
        SectionInfoStructure.addSection("4.intro.2pass")
        BookInfoStructure.addSection("4.intro.2pass")

    def test_updateProperties(self):
        SectionInfoStructure.updateProperty("2.intro", "_imIndex", "1")
        imId = SectionInfoStructure.readProperty("2.intro", "_imIndex")
        self.assertEqual(imId, "1")
        SectionInfoStructure.updateProperty("2.intro.pass", "_imIndex", "1")
        imId = SectionInfoStructure.readProperty("2.intro.pass", "_imIndex")
        SectionInfoStructure.addSection("4.intro.2passta")
        BookInfoStructure.addSection("4.intro.2passta")
        self.assertEqual(imId, "1")



class Test_TOCStructure(unittest.TestCase):

    def setUp(self):
        Settings.Book.setCurrentBook(testBookName, testBookPath)

    def test_createStructure(self):

        os.system("rm -rf " + testBookPath + BookInfoStructure.TOCbaseRelPath + "/*.tex")

        TOCStructure.createStructure()

        TOCStructure.addSection("2.intro.pass")
        TOCStructure.addSection("2.intro.pass2")
        TOCStructure.addSection("2.intro2.pass.ando")
        TOCStructure.addSection("2.intro2.pass2.ando")
        TOCStructure.addSection("2.intro2.pass2.anda")
        TOCStructure.addSection("3.intro.pass")
        TOCStructure.addSection("3.intro.3pass")
        TOCStructure.addSection("4.intro.pass")
        TOCStructure.addSection("4.intro.2pass")

        #TODO: need to check that files with expected names and content are created

    # TODO: turned off since update now only happens in TOC structure
    # def test_updateProperties(self):
    #     propertyName = TOCStructure.TOC_SECTION_PROPERTIES.text_ID
    #     TOCStructure.updateProperty("2.intro.pass", propertyName, "test")
    #     self.assertEqual(TOCStructure.readProperty("2.intro.pass", propertyName), "test")
    #     TOCStructure.updateProperty("2.intro.pass", propertyName, "testa")
    #     self.assertEqual(TOCStructure.readProperty("2.intro.pass", propertyName), "testa")

    #     propertyName = TOCStructure.TOC_SECTION_PROPERTIES.sectionStart_ID
    #     TOCStructure.updateProperty("2.intro.pass", propertyName, "1")
    #     self.assertEqual(TOCStructure.readProperty("2.intro.pass", propertyName), "1")

    #     propertyName = TOCStructure.TOC_SECTION_PROPERTIES.sectionFinish_ID
    #     TOCStructure.updateProperty("2.intro.pass", propertyName, "3")
    #     self.assertEqual(TOCStructure.readProperty("2.intro.pass", propertyName), "3")
    #     TOCStructure.updateProperty("2.intro.pass", propertyName, "4")
    #     self.assertEqual(TOCStructure.readProperty("2.intro.pass", propertyName), "4")

    #     #TODO: We need to check that the TOC files are updated correctly

class Test_OriginalMaterialStructure(unittest.TestCase):

    def setUp(self):
        Settings.Book.setCurrentBook(testBookName, testBookPath)

    def test_createStructure(self):

        originalMaterialStructurePath = testBookPath + BookInfoStructure.originalMaterialBaseRelPath
        os.system("rm -rf " + originalMaterialStructurePath)

        OriginalMaterialStructure.createStructure()

        self.assertTrue(os.path.exists(originalMaterialStructurePath))


class Test_FileSystemManager(unittest.TestCase):
    sectionPath = "1.ser.per"
    sectionPath2 = "1.ser.per2"
    sectionPath3 = "1.ser2.per"
    sectionPath4 = "2.ser.per"
    middleSectionPath = "1.ser"
    endSectionPath = "1.ser.per"

    def setUp(self):
        Settings.Book.setCurrentBook(test2BookName, test2BookPath)

    def test_CreateNewBook(self):
        os.system("rm -rf " +  test2BookPath)
        os.system("rm -rf " +  test3BookPath)

        fsm.createNewBook(test2BookName)
        fsm.createNewBook(test3BookName)

        self.assertTrue(os.path.exists(test2BookPath))

        children = os.listdir(test2BookPath)
        self.assertEqual(len(children), 4)

        allAncestors = [x[0] for x in os.walk(test2BookPath)]
        self.assertEqual(len(allAncestors), 5)

    def test_Section(self):
        
        fsm.addSectionForCurrBook(self.sectionPath)
        fsm.updateSectionStartPage(self.sectionPath, "2")
        fsm.updateSectionStartPage(self.sectionPath, "3")
        fsm.updateSectionFinishPage(self.sectionPath, "5")
        fsm.updateSectionTOCText(self.sectionPath, "testi")

        fsm.updateSectionProperty(self.sectionPath, fsm.PropIDs.SectionProperties_IDs.name_ID, "testName")

    def test_getSubsectionsList(self):
        
        fsm.addSectionForCurrBook(self.sectionPath2)
        fsm.addSectionForCurrBook(self.sectionPath3)
        fsm.addSectionForCurrBook(self.sectionPath4)
        # Settings.Book.setCurrentBook(testBookName, testBookPath)
        namesList = fsm.getSubsectionsList()
        self.assertEqual(namesList, ['1.ser.per', '1.ser.per2', '1.ser2.per', '2.ser.per'])

        namesList = fsm.getSubsectionsList(self.middleSectionPath)
        self.assertEqual(namesList, ["1.ser.per", "1.ser.per2"])
        
        namesList = fsm.getSubsectionsList(self.endSectionPath)
        self.assertEqual(namesList, [])

    def test_getTopSections(self):

        topSections = fsm.getTopSectionsList()
        self.assertEqual(topSections, ["1", "2"])

# # Different kinds of asserts we can have:
# #     self.assertEqual('foo'.upper(), 'FOO')
# #     self.assertTrue('FOO'.isupper())
# #     self.assertFalse('Foo'.isupper())
# #     with self.assertRaises(TypeError):
# #         s.split(2)

if __name__ == '__main__':
    unittest.main()