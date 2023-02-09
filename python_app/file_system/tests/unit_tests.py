import unittest
import os
import shutil

# from UI.widgets_collection import *
# import _utils._utils_main as _u
# import layouts.layouts_manager as lm
# import layouts.layouts_main as lmain
# import file_system.file_system_manager as fsm


import UI.widgets_facade as wm
import UI.widgets_messages as wmes
import file_system.file_system_manager as fsm
import file_system.origmaterial_fs as fsmain
import _utils._utils_main as _u

import _utils.logging as log

testBookName = "b_analysis_test"
testBookPath = os.getenv("BOOKS_ROOT_PATH") + testBookName
test2BookName = "b_newBook_test"
test2BookPath = os.path.join(os.getenv("BOOKS_ROOT_PATH"), "testBooks", test2BookName)
test3BookName = "b_newBook2_test"
test3BookPath = os.path.join(os.getenv("BOOKS_ROOT_PATH"), "testBooks", test3BookName)

class BookSetup:
    def addOriginalMaterialWholePDF():
        fsmain.OriginalMaterialStructure.createStructure()

        testBookFilePath = "/Users/ashum048/books/utils/tests_data/whole_book.pdf"
        fsmain.OriginalMaterialStructure.addOriginalMaterial("whole_book", 
                                                            testBookFilePath, 
                                                            "book/")


class Test_BookInfoStructure(unittest.TestCase):

    def setUp(self):
        _u.Settings.Book.setCurrentBook(testBookName, testBookPath)

    def test_createStructure(self):
        expectedFilePath = testBookPath + fsmain.BookInfoStructure._getRelFilepath()

        expectedFileDir = os.path.join(*expectedFilePath.split("/")[:-1])
        os.system("rm -rf " + expectedFileDir)

        fsmain.BookInfoStructure.createStructure(expectedFilePath)

        # we created file at the expected path
        self.assertTrue(os.path.isfile(expectedFilePath))

    def test_updateProperties(self):
        fsmain.BookInfoStructure.updateProperty(
            fsmain.BookInfoStructure.PubProp.sections_prefix_ID, 
            "te"
        )
        prefix = fsmain.BookInfoStructure.readProperty(
            fsmain.BookInfoStructure.PubProp.sections_prefix_ID
        )

        self.assertEqual(prefix, "te")


class Test_SectionsInfoStructure(unittest.TestCase):

    def setUp(self):
        _u.Settings.Book.setCurrentBook(testBookName, testBookPath)
    
    def test_createStructure(self):
        fsmain.BookInfoStructure.updateProperty(
            fsmain.BookInfoStructure.PubProp.sections_prefix_ID, 
            "te"
        )

        os.system(
            "rm -rf " 
            + os.path.join(testBookPath + fsmain.BookInfoStructure.sectionsInfoBaseRelPath)
        )

        fsmain.SectionInfoStructure.createStructure()

        fsmain.SectionInfoStructure.addSection("2.intro.pass")
        fsmain.BookInfoStructure.addSection("2.intro.pass")
        fsmain.SectionInfoStructure.addSection("2.intro.pass2")
        fsmain.BookInfoStructure.addSection("2.intro.pass2")
        fsmain.SectionInfoStructure.addSection("2.intro2.pass.ando")
        fsmain.BookInfoStructure.addSection("2.intro2.pass.ando")
        fsmain.SectionInfoStructure.addSection("2.intro2.pass2.ando")
        fsmain.BookInfoStructure.addSection("2.intro2.pass2.ando")
        fsmain.SectionInfoStructure.addSection("2.intro2.pass2.anda")
        fsmain.BookInfoStructure.addSection("2.intro2.pass2.anda")
        fsmain.SectionInfoStructure.addSection("3.intro.pass")
        fsmain.BookInfoStructure.addSection("3.intro.pass")
        fsmain.SectionInfoStructure.addSection("3.intro.3pass")
        fsmain.BookInfoStructure.addSection("3.intro.3pass")
        fsmain.SectionInfoStructure.addSection("4.intro.pass")
        fsmain.BookInfoStructure.addSection("4.intro.pass")
        fsmain.SectionInfoStructure.addSection("4.intro.2pass")
        fsmain.BookInfoStructure.addSection("4.intro.2pass")

    def test_updateProperties(self):
        fsmain.SectionInfoStructure.updateProperty("2.intro", "_imIndex", "1")
        imId = fsmain.SectionInfoStructure.readProperty("2.intro", "_imIndex")
        self.assertEqual(imId, "1")
        fsmain.SectionInfoStructure.updateProperty("2.intro.pass", "_imIndex", "1")
        imId = fsmain.SectionInfoStructure.readProperty("2.intro.pass", "_imIndex")
        fsmain.SectionInfoStructure.addSection("4.intro.2passta")
        fsmain.BookInfoStructure.addSection("4.intro.2passta")
        self.assertEqual(imId, "1")



class Test_TOCStructure(unittest.TestCase):

    def setUp(self):
        _u.Settings.Book.setCurrentBook(testBookName, testBookPath)

    def test_createStructure(self):

        os.system("rm -rf " 
            + os.path.join(testBookPath + fsmain.BookInfoStructure.TOCbaseRelPath + "/*.tex")
        )

        fsmain.TOCStructure.createStructure()

        fsmain.TOCStructure.addSection("2.intro.pass")
        fsmain.TOCStructure.addSection("2.intro.pass2")
        fsmain.TOCStructure.addSection("2.intro2.pass.ando")
        fsmain.TOCStructure.addSection("2.intro2.pass2.ando")
        fsmain.TOCStructure.addSection("2.intro2.pass2.anda")
        fsmain.TOCStructure.addSection("3.intro.pass")
        fsmain.TOCStructure.addSection("3.intro.3pass")
        fsmain.TOCStructure.addSection("4.intro.pass")
        fsmain.TOCStructure.addSection("4.intro.2pass")
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
        _u.Settings.Book.setCurrentBook(testBookName, testBookPath)
        self.originalMaterialStructurePath = os.path.join(testBookPath, 
                                            fsmain.OriginalMaterialStructure.originalMaterialBaseRelPath)
        log.autolog(self.originalMaterialStructurePath)
        if (os.path.exists(self.originalMaterialStructurePath)):
            _waitDummy = shutil.rmtree(self.originalMaterialStructurePath)


    def test_addingOriginalMaterial(self):
        fsmain.OriginalMaterialStructure.createStructure()

        testBookFilePath = "/Users/ashum048/books/utils/tests_data/whole_book.pdf"
        fsmain.OriginalMaterialStructure.addOriginalMaterial("whole_book", 
                                                            testBookFilePath, 
                                                            "book/")
        
        self.assertTrue(os.path.exists(self.originalMaterialStructurePath))

        expectedFileLocation = "\
/Users/ashum048/books/testBooks/b_analysis_test/originalMaterial/book/whole_book.pdf"
        
        self.assertTrue(os.path.exists(expectedFileLocation))


class Test_FileSystemManager(unittest.TestCase):
    sectionPath = "1.ser.per"
    sectionPath2 = "1.ser.per2"
    sectionPath3 = "1.ser2.per"
    sectionPath4 = "2.ser.per"
    middleSectionPath = "1.ser"
    endSectionPath = "1.ser.per"

    def setUp(self):
        _u.Settings.Book.setCurrentBook(test2BookName, test2BookPath)

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

        fsm.updateSectionProperty(self.sectionPath, fsm.PropIDs.Sec.name_ID, "testName")

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