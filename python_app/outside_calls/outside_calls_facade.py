import outside_calls.latex_calls as lc
import outside_calls.fsApp_calls as fc
import outside_calls.ide_calls as idec
import outside_calls.screenshot_app as scrc
import outside_calls.tracker_calls as tac

class Wr:
    class LatexCalls(lc.currLatecDistro):
        pass
   
    class FsAppCalls(fc.currFilesystemApp):
        pass

    class IdeCalls(idec.currIdeApp):
        pass
    
    class ScreenshotCalls(scrc.currScreenshotApp):
        pass
    
    class TrackerAppCalls(tac.currrtrackerApp):
        pass
