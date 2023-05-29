import os
import time

import outside_calls.fsApp_calls as fsc
import _utils.logging as log
import _utils._utils_main as _u
import data.constants as dc

class GitTracker:
    def initBook(bookPath, remoteAddress = _u.Token.NotDef.str_t):
        gitFolder = os.path.join(bookPath, ".git")

        if fsc.currFilesystemApp.checkIfFileOrDirExists(gitFolder):
            log.autolog("Removing the git folder for book with filepath '{0}'".format(bookPath))
            fsc.currFilesystemApp.removeDir(gitFolder)
            time.sleep(0.3)
        
        log.autolog("Initializing the git folder for book with filepath '{0}'".format(bookPath))
        
        with open(os.path.join(bookPath, ".gitignore"), "w") as f:
            lines = ["*.aux", "*.log", "*.out", "*.gz", "*.DS_Store"]
            f.writelines([i + "\n" for i in lines])

        cmd = "cd \"{0}\" && git init".format(bookPath)
        _u.runCmdAndWait(cmd)
        time.sleep(0.3)
        cmd = "cd \"{0}\" && git branch -M main".format(bookPath)
        _u.runCmdAndWait(cmd)
        time.sleep(0.3)
        if remoteAddress != _u.Token.NotDef.str_t:
            cmd = "cd \"{0}\" && git remote add origin {1}".format(bookPath, remoteAddress)
            _u.runCmdAndWait(cmd)
    
    def stampChanges(bookPath, id):
        cmd = "cd \"{0}\" && git add -A && git commit -m \"{1}\"".format(bookPath, id)
        _u.runCmdAndWait(cmd)

        if dc.StartupConsts.WITH_TRACKING:
            time.sleep(0.3)
            cmd = "cd \"{0}\" && git push origin main".format(bookPath, id)
            _u.runCmdAndWait(cmd)

currrtrackerApp = GitTracker