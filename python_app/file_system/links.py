import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import file_system.section_fs as sfs

class ImIDX:
    @classmethod
    def get_curr(cls):
        currSec = _upan.Current.Names.Section.name()
        return cls.get(currSec)
    
    def get(secPath, linkValue = None):
        d = LinkDict.get(secPath)

        if d == _u.Token.NotDef.dict_t or d == None:
            return 0

        if linkValue == None:
            keysList = list(d.keys())
            if len(keysList) > 0:
                return keysList[-1]
            else:
                return 0
        else:
            for k,v in d.items():
                if str(v) == str(linkValue):
                    return k
    
    def getIndiciesInSameFile(imIdx):
        imIdx = int(imIdx)
        startIdx = imIdx - (imIdx % 5)
        endIdx = startIdx + 5
        return range(startIdx, endIdx)


class ImLink:
    def get(secPath, idx = None):
        d = LinkDict.get(secPath)

        if d == _u.Token.NotDef.dict_t or d == None:
            return _u.Token.NotDef.str_t

        if idx == None:
            valList =  list(d.values())[-1]
            if len(valList) > 0:
                return valList[-1]
            else:
                return _u.Token.NotDef.str_t
        else:
            for k,v in d.items():
                if str(k) == str(idx):
                    return v

 
class LinkDict:
    def get(sectionPath):
        if sectionPath == _u.Token.NotDef.str_t:
            return _u.Token.NotDef.dict_t
        else:
            return sfs.SectionInfoStructure.readProperty(sectionPath, 
                                                    sfs.SectionInfoStructure.PubProp.imLinkDict)

    @classmethod
    def set(cls, sectionPath, linkName, imIDX):
        d = cls.get(sectionPath)
        # check if the dict is notDefined
        if d == _u.Token.NotDef.dict_t:
            d = {}
        d[imIDX] = linkName
        sfs.SectionInfoStructure.updateProperty(sectionPath, 
                                                sfs.SectionInfoStructure.PubProp.imLinkDict, d)

    def getCurrImLinksSorted(secPath):
        currChImageLinksDict = LinkDict.get(secPath)
        if currChImageLinksDict == _u.Token.NotDef.dict_t or currChImageLinksDict == None:
            return _u.Token.NotDef.list_t
        elif currChImageLinksDict != _u.Token.NotDef.dict_t:
            currSubsecImIDX = list(currChImageLinksDict.keys())
            currSubsecImIDX.sort(key = int)

            linksSorted = [list(currChImageLinksDict.values())[list(currChImageLinksDict.keys()).index(i)] for i in currSubsecImIDX]

            if linksSorted == []:
                return _u.Token.NotDef.list_t
            else:
                return linksSorted
        else:
            return _u.Token.NotDef.list_t

