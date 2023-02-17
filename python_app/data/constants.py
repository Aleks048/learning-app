import _utils._utils_main as _u


class ClassGetOnly(type):
    data = None
    dataAccessCounter = 0

    def __getattribute__(self, __name):
        if __name == "dataAccessCounter":
            return object.__getattribute__(self, __name)
        elif __name == "getData":
            self.dataAccessCounter = 1
            return object.__getattribute__(self, __name)
        elif __name == "data" and self.dataAccessCounter == 1:
            self.dataAccessCounter = 0
            return object.__getattribute__(self, __name)
        else: 
            raise TypeError("The objects of this calss are not acessible directly. Please use getData(dataAccessToken)")
    
    def getData(self):
        return self.data

class AppCurrDataAccessToken:
    appCurrDataAccessToken = "I can access the current data of the app"

class MonitorSize(metaclass = ClassGetOnly):
    data = _u.getMonitorSize()

class Links:
    class Local:
        idxLineMarker = "% THIS IS CONTENT id: "
        @classmethod
        def getIdxLineMarkerLine(cls, idx):
            return cls.idxLineMarker + idx