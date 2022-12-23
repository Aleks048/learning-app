import _utils._utils_main as _u
import file_system.file_system_manager as fsm

def getCurrSectionMoveNumber(popsitionIDX):
    currConFile = fsm.Wr.Paths.TexFiles.Content.getAbs_curr()
    currTocFile = fsm.Wr.Paths.TexFiles.TOC.getAbs_curr()

    getSectionMoveNumber(popsitionIDX, currConFile, currTocFile)

def getSectionMoveNumber(popsitionIDX, conTexFilepath, tocTexFilepath):
    '''
    this one is used by the image scripts to get the 
    '''
    # get position of index in content file
    conLine = _u.findPositionsOfMarkerInFile(conTexFilepath, popsitionIDX)    

    # get position of index in toc file
    tocLine = _u.findPositionsOfMarkerInFile(tocTexFilepath, popsitionIDX)    

    currSection = fsm.Wr.SectionCurrent.readCurrSection()
    
    #check if section infostructure has file move numbers defined
    contentFileMoveNumber = \
        fsm.Wr.SectionInfoStructure.readProperty(currSection, 
                                fsm.PropIDs.Sec.imageContentFileMoveLinesNumber_ID)
    tocFileMoveNumber = \
        fsm.Wr.SectionInfoStructure.readProperty(currSection, 
                                fsm.PropIDs.Sec.imageTOCFileMoveLinesNumber_ID)

    if contentFileMoveNumber != _u.Token.NotDef.str_t or tocFileMoveNumber != _u.Token.NotDef.str_t:
        #print to get values in sh script
        print(str(contentFileMoveNumber) + " "+ str(tocFileMoveNumber))
        return
    
    #get the move numbers from bookinfostructure
    contentFileMoveNumber = \
        fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.imageContentFileMoveLinesNumber_ID)
    tocFileMoveNumber = \
        fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.imageTOCFileMoveLinesNumber_ID)
    
    #print to get values in sh script
    print(str(conLine + contentFileMoveNumber) + " " + str(tocLine + tocFileMoveNumber))