import outside_calls.latex_calls as lc
import outside_calls.pdfApp_calls as sc
import outside_calls.fsApp_calls as fc
import outside_calls.ide_calls as idec
import outside_calls.screenshot_app as scrc

class Wr:
    class PdfApp(sc.currPdfApp):
        pass
    
    class LatexCalls(lc.currLatecDistro):
        pass
   
    class fsAppCalls(fc.currFilesystemApp):
        pass

    class IdeCalls(idec.currIdeApp):
        pass
    
    class ScreenshotCalls(scrc.currScreenshotApp):
        pass
