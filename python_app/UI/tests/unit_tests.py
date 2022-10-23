import unittest


import unittest

import UI.widgets_manager as wm


class Test_WidgetsManager(unittest.TestCase):

    def setUp(self):
        pass

    def test_StartupMenu(self):
            wm.StartupMenu.createMenu()

# # Different kinds of asserts we can have:
# #     self.assertEqual('foo'.upper(), 'FOO')
# #     self.assertTrue('FOO'.isupper())
# #     self.assertFalse('Foo'.isupper())
# #     with self.assertRaises(TypeError):
# #         s.split(2)

if __name__ == '__main__':
    unittest.main()