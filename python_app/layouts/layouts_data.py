import os
import layouts.layouts_main as lm
import _utils._utils_main as _u


listOfLayoutClasses = [getattr(lm, layoutName + _u.Settings.layoutClassToken) for layoutName in _u.Settings.layoutsList]
