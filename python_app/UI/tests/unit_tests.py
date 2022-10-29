import unittest


import unittest

import UI.widgets_manager as wm
import UI.widgets_messages as wmes


class Test_WidgetsManager_StartupMenu(unittest.TestCase):

    # def test_StartupMenu(self):

    #     # _waitDummy = wmes.ConfirmationMenu.createMenu("tests", lambda *args: None)

    #     # _waitDummy = wmes.ShowMessageMenu.createMenu("tetst")
        
    #     _waitDummy = wm.StartupMenu.createMenu()

    def test_MainMenu(self):

        # _waitDummy = wmes.ConfirmationMenu.createMenu("tests", lambda *args: None)

        # _waitDummy = wmes.ShowMessageMenu.createMenu("tetst")
        
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