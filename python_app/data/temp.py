import _utils._utils_main as _u
import _utils.logging as log

class ClassAttNotAccessibleType(type):
    data = None
    dataAccessCounter = 0

    def __getattribute__(self, __name):
        if __name == "dataAccessCounter":
            return object.__getattribute__(self, __name)
        elif __name in ["getData", "setData"]:
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
            for dp in data:
                if dpType in dp.__class__.__bases__:
                    return dp
            raise KeyError

    def setData(self, token, newValue):
        self.data = newValue

class NonInstantiable_Interface:
    def __new__(cls, *args, **kwargs):
        raise TypeError(f"'{cls.__name__}' may not be instantiated")



class AppState:
    class CurrMenu(NonInstantiable_Interface, metaclass = ClassAttNotAccessibleType):
        pass
    
    class CurrLayout(NonInstantiable_Interface, metaclass = ClassAttNotAccessibleType):
        pass

    class CurrUILayoutName(NonInstantiable_Interface, metaclass = ClassAttNotAccessibleType):
        data = ""

    class CurrUIImplementation(NonInstantiable_Interface, metaclass = ClassAttNotAccessibleType):
        pass
    
    class UIManagers(NonInstantiable_Interface, metaclass = ClassAttNotAccessibleType):
        data = []
    
    class Wait(NonInstantiable_Interface, metaclass = ClassAttNotAccessibleType):
        data = False

class OtherAppsInfo:
    class VsCode:
        section_pid = _u.Token.NotDef.str_t

    class Skim:
        section_pid = _u.Token.NotDef.str_t
        main_pid = _u.Token.NotDef.str_t
        main_winName = _u.Token.NotDef.str_t

    class Finder:
        main_pid = _u.Token.NotDef.str_t