import os

import _utils._utils_main as _u

import UI.widgets_facade as wm
import file_system.file_system_manager as fsm
import _utils.logging as log


class TexFile:
    def populateMainFile(subsectionName_full_WPrefix, bookName):
        contentFile = []
        tocFile = []

        localLinksLine = ""
        conFilepath = fsm.Wr.Paths.TexFiles.Content.getAbs(bookName, subsectionName_full_WPrefix)
        tocFilepath = fsm.Wr.Paths.TexFiles.TOC.getAbs(bookName, subsectionName_full_WPrefix)
        mainFilepath = fsm.Wr.Paths.TexFiles.Main.getAbs(bookName, subsectionName_full_WPrefix)

        topSection, subsection = fsm.Wr.Utils.stripFullName_Wprefix(subsectionName_full_WPrefix)
        
        listOfLocalLinks = []
        with open(conFilepath, 'r') as contentF:
            # create the local links line
            contentFile = contentF.readlines()
            
            linkToken = "KIK:"
            for i in range(0, len(contentFile)):
                line = contentFile[i]
                if linkToken in line:
                    line = line.replace(" ", "")
                    line = line.replace("\n", "")
                    listOfLocalLinks.append(line)

        localLinksLine = "      [" + "\n" + "".join(listOfLocalLinks) + "        ]"
        
        with open(tocFilepath, 'r') as tocF:
            tocFile = tocF.readlines()
        
        with open(os.path.join(os.getenv("BOOKS_TEMPLATES_PATH"),"main_template.tex"), 'r') as templateF:
            templateFile = templateF.readlines()
            templateFile= [i.replace("[_PLACEHOLDER_CHAPTER_]", subsection) for i in templateFile]
            topFilepath = fsm.Wr.TOCStructure._getTOCFilePath(topSection)
            templateFile= [i.replace("[_TOC_PATH_]", topFilepath) for i in templateFile]
        
        with open(mainFilepath, 'w') as outFile:

            outFileList = []
            # get the marker of the part BEFORE_LOCAL_LINKS_MARKER
            # 
            # replace everything before marker from template
            beforeLocalLinksMarker = "BEFORE_LOCAL_LINKS_MARKER"
            beforeLocalLinksmarkerPosTemplate = \
                next(i for i,v in enumerate(templateFile) if beforeLocalLinksMarker in v)
            outFileList = templateFile[:beforeLocalLinksmarkerPosTemplate + 1]

            # add local links
            outFileList.append("  " + localLinksLine + "\n")
            
            # add TOC from template
            beforeTOCmarker = "BEFORE_TOC_MARKER"
            beforeTOCmarkerPosTemplate = \
                next(i for i,v in enumerate(templateFile) if beforeTOCmarker in v)
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
        
        log.autolog("writing to main.tex file of section '{0}' is complete".format(subsectionName_full_WPrefix))

    def _populateMainFile():
        # os.system("echo testutu >> \"/Users/ashum048/books/test.txt\"")
        contentFile = []
        tocFile = []

        localLinksLine = ""
        with open(fsm.Wr.Paths.TexFiles.Content.getAbs_curr(), 'r') as contentF:
            # create the local links line
            contentFile = contentF.readlines()
            
            imLinkNameToken = "\def\linkname{"
            myTargetToken = "\myTarget{"
            
            listOfLocalLinks = []
            for i in range(0, len(contentFile)):
                line = contentFile[i]
                if imLinkNameToken in line:
                    # imLinkName = contentFile[i].replace(imLinkNameToken, "")[:-1]
                    # imLinkName = imLinkName.replace(" ", "")
                    # imLinkName = imLinkName.replace("}", "")

                    # imagesPath = contentFile[i + 2].replace(myTargetToken, "")[:-1]
                    # imagesPath = imagesPath.split("}")[0]
                    # imagesPath = imagesPath.replace(" ", "")
                    # imagesPath = imagesPath.split("/")
                    # sectionNameFull = imagesPath[-3]
                    # topSection, subsection = fsm.Wr.Utils.stripFullName_Wprefix(sectionNameFull)
                    
                    # localLinksLine = "        \\href{file:" + bookName + "." + topSection \
                    #                 + "." + subsection + "." + posIdx"}{" + imLinkName + "},\n"
                    listOfLocalLinks.append(line)

            localLinksLine = "      [" + "\n" + "".join(listOfLocalLinks) + "        ]"
        
        with open(fsm.Wr.Paths.TexFiles.TOC.getAbs_curr(), 'r') as tocF:
            tocFile = tocF.readlines()
                
        with open(os.path.join(os.getenv("BOOKS_TEMPLATES_PATH"),"main_template.tex"), 'r') as templateF:
            templateFile = templateF.readlines()
            currSection = fsm.Wr.SectionCurrent.readCurrSection()
            currTopSection = fsm.Wr.BookInfoStructure.readProperty(fsm.PropIDs.Book.currTopSection_ID)
            templateFile= [i.replace("[_PLACEHOLDER_CHAPTER_]", currSection) for i in templateFile]
            topFilepath = fsm.Wr.TOCStructure._getTOCFilePath(currTopSection)
            templateFile= [i.replace("[_TOC_PATH_]", topFilepath) for i in templateFile]
        
        with open(fsm.Wr.Paths.TexFiles.Main.getAbs_curr(), 'w') as outFile:

            outFileList = []
            # get the marker of the part BEFORE_LOCAL_LINKS_MARKER
            # 
            # replace everything before marker from template 
            beforeLocalLinksMarker = "BEFORE_LOCAL_LINKS_MARKER"
            beforeLocalLinksmarkerPosTemplate = \
                next(i for i,v in enumerate(templateFile) if beforeLocalLinksMarker in v)
            outFileList = templateFile[:beforeLocalLinksmarkerPosTemplate + 1]

            # add local links
            outFileList.append("  " + localLinksLine + "\n")
            
            # add TOC from template
            beforeTOCmarker = "BEFORE_TOC_MARKER"
            beforeTOCmarkerPosTemplate = \
                next(i for i,v in enumerate(templateFile) if beforeTOCmarker in v)
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
        currTexFilesFolder = fsm.Wr.Paths.Section.getAbs_curr()
        currTexMainFile = fsm.Wr.Paths.TexFiles.Content.getAbs_curr()
        currSectionNameWPrefix = fsm.Wr.SectionCurrent.getSectionNameWprefix()
        
        wm.Data.UItkVariables.needRebuild.set(False)
        return cls.buildSubsectionPdf(currTexFilesFolder, currTexMainFile, currSectionNameWPrefix)
    
    def buildSubsectionPdf(sectionFolder, mainTexFilepath, sectionNameWprefix):
        log.autolog("build: " + mainTexFilepath)
        
        # NOTE: we add "_con.tex" to comply with what is called when the file is saved
        cmd = "${BOOKS_ON_FILE_SAVE_PATH}/s_onTexFileSave.sh" \
                            " " + mainTexFilepath + \
                            " " + sectionFolder + \
                            " " + sectionNameWprefix + "_con.tex"
        _waitDummy = os.system(cmd)
        return True
