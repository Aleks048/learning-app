import os
import subprocess

import _utils._utils_main as _u
import _utils.pathsAndNames as _upan

import file_system.file_system_facade as fsm
import outside_calls.outside_calls_facade as ocf
import _utils.logging as log
import settings.facade as sf

class TexFilePopulate:
    def populateMainFile(subsectionName_full_WPrefix, bookPath):
        contentFile = []
        tocFile = []

        localLinksLine = ""
        conFilepath = _upan.Paths.TexFiles.Content.getAbs(bookPath, subsectionName_full_WPrefix)
        tocFilepath = _upan.Paths.TexFiles.TOC.getAbs(bookPath, subsectionName_full_WPrefix)
        mainFilepath = _upan.Paths.TexFiles.Main.getAbs(bookPath, subsectionName_full_WPrefix)

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
                if "myTarget" in line:
                    log.autolog(line)
                    lineArr = line.split("{")
                    imageName = lineArr[1][:-1]
                    imagePath = os.path.join(_upan.Paths.Screenshot.getAbs(bookPath, subsectionName_full_WPrefix),
                                             imageName)
                    contentFile[i] = line.replace(imageName, imagePath)

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

    @classmethod
    def populateCurrMainFile(cls):
        currName = _upan.Current.Names.Section.name_wPrefix()
        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        cls.populateMainFile(currName, bookPath)