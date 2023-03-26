from time import sleep

import scripts.osascripts as oscr
import data.temp as dt
import _utils._utils_main as _u
import _utils.logging as log
import settings.facade as sf


class LayoutsManager:
    def closeIDEWindow(idToken, ownerPID = None):
        log.autolog("Closing IDE window with token '{0}'.".format(idToken))

        if ownerPID == None:
            _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.vsCode_ID, idToken)
            
            while ownerPID == None:
                sleep(0.1)
                _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.vsCode_ID, idToken)

        cmd = oscr.closeVscodeWindow(ownerPID, idToken)
        _u.runCmdAndWait(cmd)
    

    def closeFSWindow(idToken, ownerPID = None):
        log.autolog("Closing File System window with token '{0}'.".format(idToken))

        if ownerPID == None:
            _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.finder_ID, idToken)
            
            while ownerPID == None:
                sleep(0.1)
                _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.finder_ID, idToken)

        cmd = oscr.closeFinderWindow(ownerPID, idToken)
        _u.runCmdAndWait(cmd)
    
    def closePDFwindow(idToken, ownerPID = None):  
        
        if ownerPID == None:
            _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, idToken)
            
            while ownerPID == None:
                sleep(0.1)
                _, _, ownerPID = _u.getOwnersName_windowID_ofApp(sf.Wr.Data.TokenIDs.AppIds.skim_ID, idToken)
        
        cmd = oscr.closeSkimDocument(ownerPID, idToken)
        _u.runCmdAndWait(cmd)

