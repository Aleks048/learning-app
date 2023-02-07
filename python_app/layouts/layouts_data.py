import layouts.layouts_collection.layout_main as lm
import layouts.layouts_collection.layout_section as ls


import _utils._utils_main as _u


# listOfLayoutClasses = [getattr(lm, layoutName + _u.Settings.layoutClassToken) for layoutName in _u.Settings.layoutsList]
listOfLayoutClasses = [lm.MainLayout, ls.SectionLayout]
