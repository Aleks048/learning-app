import os

import _utils._utils_main as _u
import UI.widgets_manager as ui
import file_system.file_system_main as fs


class TexFile:
    def _getCurrTexFilesDir(currSubchapter):
        currChapter = fs.BookInfoStructure.readProperty(fs.BookInfoStructure.currSection_ID)
        return _u.Settings.getBookFolderPath(_u.Settings.readProperty(_u.Settings.getCurrentBookFolderName())) + \
                "/" + currChapter + "/" + \
                _u.Settings.relToSubchapters_Path + \
                "/ch_" + currSubchapter
    

    @classmethod
    def _getCurrContentFilepath(cls):
        currSubchapter = _u.BookSettings.readProperty(_u.BookSettings.CurrentStateProperties.Book.currSectionFull_ID)
        return cls._getCurrTexFilesDir(currSubchapter) + "/" + currSubchapter + "_con.tex"
    

    @classmethod
    def _getCurrTOCFilepath(cls):
        currSubchapter = _u.BookSettings.readProperty(_u.BookSettings.CurrentStateProperties.Book.currSectionFull_ID)
        return cls._getCurrTexFilesDir(currSubchapter) + "/" + currSubchapter + "_toc.tex"
    

    @classmethod      
    def _getCurrMainFilepath(cls):
        currSubchapter = _u.BookSettings.readProperty(_u.BookSettings.CurrentStateProperties.Book.currSectionFull_ID)
        return cls._getCurrTexFilesDir(currSubchapter) + "/" + currSubchapter + "_main.tex"


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
                
        with open(os.getenv("BOOKS_PROCESS_TEX_PATH") + "/template.tex", 'r') as templateF:
            templateFile = templateF.readlines()
            templateFile= [i.replace("[_PLACEHOLDER_CHAPTER_]", fs.BookInfoStructure.readProperty(fs.BookInfoStructure.currSection_ID)) for i in templateFile]

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
    def buildCurrentSubchapterPdf(cls):
        currSubchapter = _u.BookSettings.readProperty(_u.BookSettings.CurrentStateProperties.Book.currSectionFull_ID)
        currTexFilesFolder = cls._getCurrTexFilesDir(currSubchapter)
        currTexMainFile = cls._getCurrContentFilepath()
        print("ChapterLayout.set - " + currTexMainFile)
        _waitDummy = os.system("${BOOKS_ON_FILE_SAVE_PATH}/s_onTexFileSave.sh " + currTexMainFile + " " + currTexFilesFolder)
        ui.UItkVariables.needRebuild.set(False)

