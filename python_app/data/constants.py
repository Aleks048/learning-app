class AppCurrDataAccessToken:
    appCurrDataAccessToken = "I can access the current data of the app"

class Links:
    class Local:
        idxLineMarker = "% THIS IS CONTENT id: "
        @classmethod
        def getIdxLineMarkerLine(cls, idx):
            return cls.idxLineMarker + idx