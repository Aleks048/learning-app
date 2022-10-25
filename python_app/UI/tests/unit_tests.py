import unittest


import unittest

import UI.widgets_manager as wm


class Test_WidgetsManager_StartupMenu(unittest.TestCase):

    def test_Menus(self):

        _waitDummy = wm.ConfirmationMenu.createMenu("tests", lambda *args: None)

        _waitDummy = wm.ShowMessageMenu.createMenu("tetst")
        
        _waitDummy = wm.StartupMenu.createMenu()


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