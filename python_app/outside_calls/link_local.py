import os
import _utils._utils_main as _u
import _utils.logging as log
import file_system.file_system_manager as fsm

def processLinkSecLinkCall(popsitionIDX):
    currConFile = fsm.Wr.Paths.TexFiles.Content.getAbs_curr()
    currTocFile = fsm.Wr.Paths.TexFiles.TOC.getAbs_curr()
    currTocFile = fsm.Wr.Paths.PDF.getAbs_curr()

    processLinkCall(popsitionIDX, currConFile, currTocFile, currTocFile)

def processLinkCall(popsitionIDX, secName, bookName):
    '''
    this one is used by the image scripts to get the 
    '''

    secNameWPrefix = fsm.Wr.Utils.getSectionNameWPrefix(secName)
    log.autolog(secName)
    bookPath = _u.getBookPath(bookName)
    if bookPath == _u.Token.NotDef.str_t:
        log.autolog("Could not find the path for the book with name '" 
                    + bookName + "'. Abropt link '" + secName + "'processing.")
        return

    conTexFilepath = fsm.Wr.Paths.TexFiles.Content.getAbs(bookPath, secNameWPrefix)
    tocTexFilepath = fsm.Wr.Paths.TexFiles.TOC.getAbs(bookPath, secNameWPrefix)
    secPdfFilepath = fsm.Wr.Paths.PDF.getAbs(bookPath, secNameWPrefix)

    # enforce the position index to be a string
    if type(popsitionIDX) != str:
        popsitionIDX = str(popsitionIDX)
    
    idxMarker = popsitionIDX

    # get position of index in content file
    conLine,_ = _u.findPositionsOfMarkerInFile(conTexFilepath, idxMarker)
    conLine = conLine[0]

    # get position of index in toc file
    tocLine, _ = _u.findPositionsOfMarkerInFile(tocTexFilepath, idxMarker)
    tocLine = tocLine[0]

    currSection = fsm.Wr.SectionCurrent.readCurrSection()
    
    #check if section infostructure has file move numbers defined
    conFileMoveNumber = \
        int(fsm.Wr.SectionInfoStructure.readProperty(currSection, 
                                fsm.PropIDs.Sec.imageContentFileMoveLinesNumber_ID))
    tocFileMoveNumber = \
        int(fsm.Wr.SectionInfoStructure.readProperty(currSection, 
                                fsm.PropIDs.Sec.imageTOCFileMoveLinesNumber_ID))

    tocLineNumber = str(tocLine + tocFileMoveNumber)
    conLineNumber = str(conLine + conFileMoveNumber)
    pdfPage = popsitionIDX

    if conFileMoveNumber == _u.Token.NotDef.str_t and tocFileMoveNumber == _u.Token.NotDef.str_t:
        #get the move numbers from bookinfostructure
        conFileMoveNumber = \
            fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.imageContentFileMoveLinesNumber_ID)
        tocFileMoveNumber = \
            fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.imageTOCFileMoveLinesNumber_ID)
        
        tocLineNumber = str(tocLine + tocFileMoveNumber)
        conLineNumber = str(conLine + conFileMoveNumber)    

    cmd ="""\
# move tex TOC file to desired
code -g {0}:{1}:0
code -g {2}:{3}:0
open \"skim://{4}#page={5}\"
""".format(tocTexFilepath, 
        tocLineNumber, 
        conTexFilepath, 
        conLineNumber, 
        secPdfFilepath,
        pdfPage)
    os.system(cmd)
    