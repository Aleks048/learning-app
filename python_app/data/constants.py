class Links:
    class Local:
        idxLineMarker = "% THIS IS CONTENT id: "
        @classmethod
        def getIdxLineMarkerLine(cls, idx):
            return cls.idxLineMarker + idx