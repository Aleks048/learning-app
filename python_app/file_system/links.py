import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import _utils.logging as log
import file_system.section_fs as sfs

class ImIDX:
    @classmethod
    def get_curr(cls):
        currSec = _upan.Current.Names.Section.name()
        return cls.get(currSec)
    def get(secPath):
        d = LinkDict.get(secPath)
        return list(d.values())[-1]


class ImLink:
    #NOTE: not used now
    def get(secPath, newValue):
        d = LinkDict.get(secPath)
        return list(d.keys())[-1]

 
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
        d[linkName] = imIDX
        sfs.SectionInfoStructure.updateProperty(sectionPath, 
                                                sfs.SectionInfoStructure.PubProp.imLinkDict, d)

    def getCurrImLinksSorted(secPath):
        currChImageLinksDict = LinkDict.get(secPath)
        if str(currChImageLinksDict) == _u.Token.NotDef.str_t:
            return _u.Token.NotDef.list_t
        elif currChImageLinksDict != _u.Token.NotDef.dict_t:
            currChImageIDX = list(currChImageLinksDict.values())
            currChImageIDX.sort(key = int)
            return [list(currChImageLinksDict.keys())[list(currChImageLinksDict.values()).index(i)] for i in currChImageIDX]
        else:
            return _u.Token.NotDef.list_t

