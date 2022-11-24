import os

import _utils._utils_main as _u

import UI.widgets_manager as wm
import file_system.file_system_manager as fsm
import _utils.logging as log


class TexFile:
    sectionPrefix = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_prefix_ID) + "_"

    @classmethod
    def _getCurrContentFilepath(cls):
        currSubsection = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currSection_ID)
        return os.path.join(_u.DIR.Section.getCurrentAbs(), cls.sectionPrefix + currSubsection + "_con.tex")
    

    @classmethod
    def _getCurrTOCFilepath(cls):
        currSusection = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currSection_ID)
        return os.path.join(_u.DIR.Section.getCurrentAbs(), cls.sectionPrefix + currSusection + "_toc.tex")
    

    @classmethod      
    def _getCurrMainFilepath(cls):
        currSussection = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currSection_ID)
        return os.path.join(_u.DIR.Section.getCurrentAbs(), cls.sectionPrefix + currSussection + "_main.tex")


    def _populateMainFile():
        contentFile = []
        tocFile = []

        localLinksLine = ""
        with open(TexFile._getCurrContentFilepath(), 'r') as contentF:
            # create the local links line
            contentFile = contentF.readlines()
            
            imLinkNameToken = "\def\linkname{"
            myTargetToken = "\myTarget{"
            
            listOfLocalLinks = []
            for i in range(0, len(contentFile)):
                line = contentFile[i]
                if imLinkNameToken in line:
                    imLinkName = contentFile[i].replace(imLinkNameToken, "")[:-1]
                    imLinkName = imLinkName.replace(" ", "")
                    imLinkName = imLinkName.replace("}", "")

                    imageAndScriptPath = contentFile[i + 2].replace(myTargetToken, "")[:-1]
                    imageAndScriptPath = imageAndScriptPath.split("}")[0]
                    imageAndScriptPath = imageAndScriptPath.replace(" ", "")
                    
                    localLinksLine = "        \\href{file:" + imageAndScriptPath + ".sh" + "}{" + imLinkName + "},\n"
                    listOfLocalLinks.append(localLinksLine)
                    # i += 2

            localLinksLine = "      [" + "\n" + "".join(listOfLocalLinks) + "        ]"
        
        with open(TexFile._getCurrTOCFilepath(), 'r') as tocF:
            tocFile = tocF.readlines()
                
        with open(os.path.join(os.getenv("BOOKS_TEMPLATES_PATH"),"main_template.tex"), 'r') as templateF:
            templateFile = templateF.readlines()
            currSection = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currSection_ID)
            currTopSection = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currTopSection_ID)
            templateFile= [i.replace("[_PLACEHOLDER_CHAPTER_]", currSection) for i in templateFile]
            topFilepath = fsm.Wr.TOCStructure._getTOCFilePath(currTopSection)
            templateFile= [i.replace("[_TOC_PATH_]", topFilepath) for i in templateFile]
        
        with open(TexFile._getCurrMainFilepath(), 'w') as outFile:

            outFileList = []
            # get the marker of the part BEFORE_LOCAL_LINKS_MARKER
            # 
            # replace everything before marker from template 
            beforeLocalLinksMarker = "BEFORE_LOCAL_LINKS_MARKER"
            beforeLocalLinksmarkerPosTemplate = next(i for i,v in enumerate(templateFile) if beforeLocalLinksMarker in v)
            outFileList = templateFile[:beforeLocalLinksmarkerPosTemplate + 1]

            # add local links
            outFileList.append("  " + localLinksLine + "\n")
            
            # add TOC from template
            beforeTOCmarker = "BEFORE_TOC_MARKER"
            beforeTOCmarkerPosTemplate = next(i for i,v in enumerate(templateFile) if beforeTOCmarker in v)
            outFileList.extend(templateFile[beforeLocalLinksmarkerPosTemplate + 1:beforeTOCmarkerPosTemplate + 1])          

            # add TOC data
            outFileList.extend(["        " + i for i in tocFile])
            
            # get the marker of the part AFTER TOC and BEFORE IMAGES
            # 
            # replace everything betweeen markers
            afterTOCmarker = "AFTER_TOC_MARKER"
            # afterTOCmarkerPos = next(i for i,v in enumerate(texFile) if afterTOCmarker in v)
            afterTOCmarkerPosTem = next(i for i,v in enumerate(templateFile) if afterTOCmarker in v)
            beforePICmarker = "BEFORE_PIC_MARKER"
            beforePICmarkerPosTem = next(i for i,v in enumerate(templateFile) if beforePICmarker in v)
            outFileList.extend(templateFile[afterTOCmarkerPosTem: beforePICmarkerPosTem + 1])

            # add CONTENT
            outFileList.extend(contentFile)

            # add extra 2 lines
            outFileList.extend("\n\n")

            # get the marker of the part in the END
            # 
            # replace everything after marker from template 
            afterPICmarker = "AFTER_PIC_MARKER"
            afterPICmarkerPosTem = next(i for i,v in enumerate(templateFile) if afterPICmarker in v)
            outFileList.extend(templateFile[afterPICmarkerPosTem:])
            
            # writeToMainFile
            for line in outFileList:
                outFile.write(line)


    @classmethod 
    def buildCurrentSubsectionPdf(cls):
        currTexFilesFolder = _u.DIR.Section.getCurrentAbs()
        currTexMainFile = cls._getCurrContentFilepath()
        secPrefix = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.sections_prefix_ID)
        currSection = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currSection_ID)
        log.autolog("build: " + currTexMainFile)
        
        # NOTE: we add "_con.tex" to comply with what is called when the file is saved
        cmd = "${BOOKS_ON_FILE_SAVE_PATH}/s_onTexFileSave.sh" \
                            " " + currTexMainFile + \
                            " " + currTexFilesFolder + \
                            " " + secPrefix + "_" + currSection + "_con.tex"
        _waitDummy = os.system(cmd)
        wm.Data.UItkVariables.needRebuild.set(False)
        return True

