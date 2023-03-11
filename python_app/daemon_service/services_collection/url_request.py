import outside_calls.pdfApp_calls as sc
import outside_calls.outside_calls_facade as ocf

#
# use this if we need to move the vscode from the url
#
# def processLocalLinkCall(positionIDX, secName, bookName):
#     '''
#     this one is used by the image scripts to get the 
#     '''

#     secNameWPrefix = fsm.Wr.Utils.getSectionNameWPrefix(secName)
#     bookPath = _u.getBookPath(bookName)
#     if bookPath == _u.Token.NotDef.str_t:
#         log.autolog("Could not find the path for the book with name '" 
#                     + bookName + "'. Abropt local link '" + secName + "'processing.")
#         return

#     conTexFilepath = fsm.Wr.Paths.TexFiles.Content.getAbs(bookPath, secNameWPrefix)
#     tocTexFilepath = fsm.Wr.Paths.TexFiles.TOC.getAbs(bookPath, secNameWPrefix)
#     secPdfFilepath = fsm.Wr.Paths.PDF.getAbs(bookPath, secNameWPrefix)

#     # enforce the position index to be a string
#     if type(positionIDX) != str:
#         positionIDX = str(positionIDX)
    
#     idxMarker = positionIDX

#     # get position of index in content file
#     conLine,_ = _u.findPositionsOfMarkerInFile(conTexFilepath, idxMarker)
#     conLine = conLine[0]

#     # get position of index in toc file
#     tocLine, _ = _u.findPositionsOfMarkerInFile(tocTexFilepath, idxMarker)
#     tocLine = tocLine[0]

#     currSection = fsm.Wr.SectionCurrent.readCurrSection()
    
#     #check if section infostructure has file move numbers defined
#     conFileMoveNumber = \
#         int(fsm.Wr.SectionInfoStructure.readProperty(currSection, 
#                                 fsm.PropIDs.Sec.imageContentFileMoveLinesNumber_ID))
#     tocFileMoveNumber = \
#         int(fsm.Wr.SectionInfoStructure.readProperty(currSection, 
#                                 fsm.PropIDs.Sec.imageTOCFileMoveLinesNumber_ID))

#     tocLineNumber = str(tocLine + tocFileMoveNumber)
#     conLineNumber = str(conLine + conFileMoveNumber)
#     pdfPage = positionIDX

#     if conFileMoveNumber == _u.Token.NotDef.str_t and tocFileMoveNumber == _u.Token.NotDef.str_t:
#         #get the move numbers from bookinfostructure
#         conFileMoveNumber = fsm.Data.Book.imageContentFileMoveLinesNumber
#         tocFileMoveNumber = fsm.Data.Book.imageTOCFileMoveLinesNumber
        
#         tocLineNumber = str(tocLine + tocFileMoveNumber)
#         conLineNumber = str(conLine + conFileMoveNumber)    

#     cmd ="""\
# # move tex TOC file to desired
# code -g {0}:{1}:0
# code -g {2}:{3}:0
# open \"skim://{4}#page={5}\"
# """.format(tocTexFilepath, 
#         tocLineNumber, 
#         conTexFilepath, 
#         conLineNumber, 
#         secPdfFilepath,
#         pdfPage)
#     os.system(cmd)



def processCall(url):
    url = url.replace("KIK:/")
    url = url.split(".")
    bookName = url[0]
    topSection = url[1]
    subsecPath = url[2]
    positionIDX = url[3]
    ocf.Wr.PdfApp.openSubsectionPDF(positionIDX, topSection, subsecPath, bookName)