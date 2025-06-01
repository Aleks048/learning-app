import _utils._utils_main as _u
import _utils.logging as log

class ClassAttNotAccessibleType(type):
    data = None
    dataAccessCounter = 0

    def __getattribute__(self, __name):
        if __name == "dataAccessCounter":
            return object.__getattribute__(self, __name)
        elif __name in ["getData", "setData", "__name__"]:
            self.dataAccessCounter = 1
            return object.__getattribute__(self, __name)
        elif __name == "data" and self.dataAccessCounter == 1:
            self.dataAccessCounter = 0
            return object.__getattribute__(self, __name)
        else: 
            raise TypeError("The objects of this calss are not acessible directly. Please use getData(dataAccessToken)")
    
    def getData(self, token, dpType = None):
        if dpType == None:
            return self.data
        else:
            data = self.data
            dpType = str(dpType).split(".")[-1]
            for dp in data:
                dpTypeNameFormatted = str(dp.__class__).split(".")[-1]

                if dpType == dpTypeNameFormatted:
                    return dp

                baseClasses = dp.__class__.__bases__
                for bc in baseClasses:
                    dpTypeNameFormatted = str(bc).split(".")[-1]
                    if dpType == dpTypeNameFormatted:
                        return dp

            raise KeyError

    def setData(self, token, newValue):
        self.data = newValue

class NonInstantiable_Interface:
    def __new__(cls, *args, **kwargs):
        raise TypeError(f"'{cls.__name__}' may not be instantiated")



class AppState:
    class CurrLayout(NonInstantiable_Interface, metaclass = ClassAttNotAccessibleType):
        pass
    
    class UIManagers(NonInstantiable_Interface, metaclass = ClassAttNotAccessibleType):
        data = []
    
    class Wait(NonInstantiable_Interface, metaclass = ClassAttNotAccessibleType):
        data = False

    class ShowProofs(NonInstantiable_Interface, metaclass = ClassAttNotAccessibleType):
        data = False

    class UseLatestGroup(NonInstantiable_Interface, metaclass = ClassAttNotAccessibleType):
        data = False

class OtherAppsInfo:
    class GoodNotes:
        section_pid = _u.Token.NotDef.str_t
    
    class VsCode:
        section_pid = _u.Token.NotDef.str_t

    class Skim:
        section_pid = _u.Token.NotDef.str_t
        main_pid = _u.Token.NotDef.str_t
        main_winName = _u.Token.NotDef.str_t

    class Finder:
        main_pid = _u.Token.NotDef.str_t

class UITemp:
    class Copy:
        subsection = _u.Token.NotDef.str_t
        imIdx = _u.Token.NotDef.str_t
        cut = _u.Token.NotDef.no_t
    class Link:
        subsection = _u.Token.NotDef.str_t
        imIdx = _u.Token.NotDef.str_t
    
    class Layout:
        noMainEntryShown = False
    
    class Groups:
        copyGroupIdx = None
    
class CodeTemp:
    currCodeFullLink = _u.Token.NotDef.str_t