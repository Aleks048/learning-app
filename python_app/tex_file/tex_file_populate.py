import os

import _utils._utils_main as _u
import _utils.pathsAndNames as _upan

import file_system.file_system_facade as fsm
import outside_calls.outside_calls_facade as ocf
import _utils.logging as log
import settings.facade as sf
import tex_file.tex_file_modify as tfm
import data.constants as dc
import tex_file.tex_file_utils as  tfu

class TexFilePopulate:
    def populateMainFile(subsection, bookPath, imIdx = _u.Token.NotDef.str_t):
        contentFile = []

        if imIdx == _u.Token.NotDef.str_t:
            imIdx = fsm.Wr.Links.ImIDX.get(subsection)

        localLinksLine = ""
        bookName = sf.Wr.Manager.Book.getNameFromPath(bookPath)
        conFilepath = _upan.Paths.TexFiles.Content.getAbs(bookPath, subsection, imIdx)
        mainFilepath = _upan.Paths.TexFiles.Main.getAbs(bookPath, subsection, imIdx)

        topSection = fsm.Wr.Utils.getTopSection(subsection)
        
        listOfLocalLinks = []

        numFiles = int(int(fsm.Wr.Links.ImIDX.get(subsection)) / 5) + 1

        imTextDict = fsm.Data.Sec.imLinkDict(subsection)

        for idx,_ in imTextDict.items():
            lineToAdd = tfu.getLinkLine(bookName, topSection, subsection, idx, "{0}\_{1}".format(subsection, idx), "full")
            lineToAdd += tfu.getLinkLine(bookName, topSection, subsection, idx, "[p]", "pdf") + ", \n"
            listOfLocalLinks.append(lineToAdd)

        with open(conFilepath, 'r') as contentF:
            # create the local links line
            contentFile = contentF.readlines()

            imGlobalLinksDict = fsm.Data.Sec.imGlobalLinksDict(subsection)
            # get links for the same fileas the idx
            linksIndiciesRange = fsm.Wr.Links.ImIDX.getIndiciesInSameFile(imIdx)
            
            for id in linksIndiciesRange:
                if str(id) in list(imGlobalLinksDict.keys()):
                    # add link to the file as a list
                    linksAndNames = imGlobalLinksDict[str(id)]
                    
                    for linkName in list(linksAndNames.keys()):
                        link = linksAndNames[linkName]
                        contentFile = tfm.TexFileModify.addLinkToTexFile(id,
                                                                        contentFile,
                                                                        link,
                                                                        linkName)
            
            linkToken = "id: "
            currIdx = ""


            for i in range(0, len(contentFile)):
                line = contentFile[i]
                if linkToken in line:
                        idx = line.replace(dc.Links.Local.idxLineMarker, "")
                        idx = idx.replace(" ", "")
                        idx = idx.replace("\n", "")
                        currIdx = idx
                elif "myTarget" in line:
                    lineArr = line.split("{")
                    imageName = lineArr[1][:-1]
                    imText = imTextDict[currIdx]
                    imText =tfm.TexFileModify.formatLinkName(imText)
                    imagePath = os.path.join(_upan.Paths.Screenshot.getAbs(bookPath, subsection),
                                             imageName)
                    textToAdd = "\\mybox{{\\Large[" + subsection + "-" + currIdx + "]" + imText + ":\\par}}\\normalsize"
                    linkToOriginal = tfu.getLinkLine(bookName, topSection, subsection, 
                                                currIdx, "[Original Material]", "OM")
                    line = line.replace("\n", "")
                    contentFile[i] = textToAdd + linkToOriginal + line.replace(imageName, imagePath) + "\n"
                elif "myStIm" in line:
                    lineArr = line.split("{")
                    imageName = lineArr[-1][:-1]
                    imageNameOriginal = imageName

                    if "__EXTRA__" in line:
                        imageName = _upan.Names.getExtraImageName(currIdx, subsection, imageName)

                    imagePath = os.path.join(_upan.Paths.Screenshot.getAbs(bookPath, subsection), imageName)
                    contentFile[i] = line.replace(imageNameOriginal, imagePath)
                elif "Local links" in line:
                    #NOTE: not used TODO: remove
                    contentFile[i] = ""

        localLinksLine = "\href" + \
            "{{KIK:/{0}/{1}/{2}/-1/notes}}{{notes}}".format(bookName, topSection, subsection) + \
            "\n      [" + "\n" + "".join(listOfLocalLinks) + "        ]"

        tocFile = [tfu.getLinkLine(bookName, topSection, subsection, 
                                   imIdx, "[Bring To front]", "full")]
        
        bookName = sf.Wr.Manager.Book.getNameFromPath(bookPath)

        for i in range(numFiles):
            tocFilepath = _upan.Paths.TexFiles.TOC.getAbs(bookPath, subsection, str(i * 5))
            with open(tocFilepath, 'r') as tocF:
                tocFile_links = tocF.readlines()
                currIdx = 0

                for i in range(0, len(tocFile_links)):
                    line = tocFile_links[i]

                    if linkToken in line:
                        idx = line.replace(dc.Links.Local.idxLineMarker, "")
                        idx = idx.replace(" ", "")
                        idx = idx.replace("\n", "")
                        currIdx = idx
                    
                    if dc.TexFileTokens.TOC.imTextToken in line:
                        line = line.split(dc.TexFileTokens.TOC.imTextToken)[-1]
                        lineArr = line.split("}")
                        linkName = lineArr[0].replace("{","")
                        linkName =tfm.TexFileModify.formatLinkName(linkName)
                        lineToAdd = tfu.getLinkLine(bookName, topSection, subsection, currIdx, linkName, "full")
                        lineToAdd = lineToAdd.replace("\n", lineArr[1])

                        if dc.TexFileTokens.TOC.imageToken in line:
                            lineArr = lineToAdd.split("{")
                            imageName = lineArr[-1][:-1]
                            imagePath = os.path.join(_upan.Paths.Screenshot.getAbs(bookPath, subsection),
                                                imageName)
                            lineToAdd = lineToAdd.replace(imageName, imagePath)
                        
                        if len(lineArr) > 2:
                            lineToAdd += "}\n"

                        tocFile_links[i] = lineToAdd
            
            tocFile.extend(tocFile_links)
        
        with open(os.path.join(os.getenv("BOOKS_TEMPLATES_PATH"),"main_template.tex"), 'r') as templateF:
            templateFile = templateF.readlines()
            templateFile= [i.replace("[_PLACEHOLDER_CHAPTER_]", subsection) for i in templateFile]
        
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
            outFileList.append("Local links: " + localLinksLine + "\n")
            
            # add TOC from template
            beforeTOCmarker = "BEFORE_TOC_MARKER"
            beforeTOCmarkerPosTemplate = \
                next(i for i,v in enumerate(templateFile) if beforeTOCmarker in v)
            outFileList.extend(templateFile[beforeLocalLinksmarkerPosTemplate + 1:beforeTOCmarkerPosTemplate + 1])          

            # add TOC data
            outFileList.append("\\mybox{")
            outFileList.extend(["        " + i for i in tocFile])
            outFileList.append("}")
            
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
        
        log.autolog("writing to main.tex file of section '{0}' is complete".format(subsection))

    @classmethod
    def populateCurrMainFile(cls):
        currName = _upan.Current.Names.Section.name()
        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        cls.populateMainFile(currName, bookPath)