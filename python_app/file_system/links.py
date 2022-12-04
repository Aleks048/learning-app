import _utils._utils_main as _u
import file_system.section_fs as sfs

class ImIDX:
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
            return _u.Token.NotDef.str_t
        else:
            return sfs.SectionInfoStructure.readProperty(sectionPath, 
                                                    sfs.SectionInfoStructure.PubProp.imLinkDict_ID)

    @classmethod
    def set(cls, sectionPath, linkName, imIDX):
        d = cls.get(sectionPath)
        # check if the dict is notDefined
        if d == _u.Token.NotDef.dict_t:
            d = {}
        d[linkName] = imIDX
        sfs.SectionInfoStructure.updateProperty(sectionPath, 
                                                sfs.SectionInfoStructure.PubProp.imLinkDict_ID, d)

    def getCurrImLinksSorted(secPath):
        currChImageLinksDict = LinkDict.get(secPath)
        if currChImageLinksDict != _u.Token.NotDef.dict_t:
            currChImageIDX = list(currChImageLinksDict.values())
            currChImageIDX.sort(key = int)
            return [list(currChImageLinksDict.keys())[list(currChImageLinksDict.values()).index(i)] for i in currChImageIDX]
        else:
            return _u.Token.NotDef.list_t

    def createLinkScript(imIDX, contentFilePath, tocFilepath, pdfName):
        scriptFile = ""
        scriptFile += "#!/bin/bash\n"
        scriptFile += "\
conIDX=`grep -n \"% THIS IS CONTENT id: " + imIDX +"\" \"" + contentFilePath + "\" | cut -d: -f1`\n"
        scriptFile += "\
tocIDX=`grep -n \"% THIS IS CONTENT id: " + imIDX +"\" \"" + tocFilepath + "\" | cut -d: -f1`\n"
        # get image move numbers
        scriptFile += "\n\
pushd ${BOOKS_PY_APP_PATH}\n\
    cmd=\"from _utils import _utils_main as _u; _u.getCurrSectionMoveNumber();\"\n\
    movenumbersarray=(`python3 -c \"${cmd}\"`)\n\
popd\n"
        scriptFile += "\
if [ \"$conIDX\" != \"\" ]\n\
then\n\
osascript -  $conIDX <<EOF\n\
    on run argv\n\
        tell application \"code\"\n\
            activate\n\
            tell application \"System Events\"\n\
                keystroke \"1\" using {command down}\n\
                delay 0.1\n\
                keystroke \"g\" using {control down}\n\
                keystroke item 1 of argv + ${movenumbersarray[0]}\n\
                keystroke return\n\
            end tell\n\
        end tell\n\
    end run\n\
EOF\n\
fi\n"
        scriptFile += "\
if [ \"$tocIDX\" != \"\" ]\n\
then\n\
osascript - $tocIDX <<EOF\n\
    on run argv\n\
        tell application \"code\"\n\
            activate\n\
            tell application \"System Events\"\n\
                keystroke \"2\" using {command down}\n\
                delay 0.1\n\
                keystroke \"g\" using {control down}\n\
                keystroke item 1 of argv + ${movenumbersarray[1]}\n\
                keystroke return\n\
            end tell\n\
        end tell\n\
    end run\n\
EOF\n\
fi\n"
        scriptFile += "osascript -e '\
tell application \"" + _u.Settings._appsIDs.skim_ID + "\"\n\
    tell document \"" + pdfName + "\"\n\
        delay 0.1\n\
        go to page " + str(imIDX) + "\n\
        end tell\n\
end tell'"
        
        return scriptFile
