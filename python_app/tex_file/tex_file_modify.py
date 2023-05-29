import os

import file_system.file_system_facade as fsm
import tex_file.tex_file_populate as tfp
import data.constants as dc
import re

import _utils.logging as log
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import settings.facade as sf

import tex_file.tex_file_utils as tfu
import outside_calls.outside_calls_facade as ocf


class TexFileModify:
    @classmethod
    def removeImageFromCon(cls, bookName, subsection, imIdx):
        filepath = _upan.Paths.TexFiles.Content.getAbs(bookName, subsection)
        cls.__updateTexFile(filepath,
                            "", 
                            dc.Links.Local.getIdxLineMarkerLine(int(imIdx)), 
                            dc.Links.Local.getIdxLineMarkerLine(int(imIdx) + 1))
    
    @classmethod
    def removeImageFromToc(cls, bookName, subsection, imIdx):
        filepath = _upan.Paths.TexFiles.TOC.getAbs(bookName, subsection)
        cls.__updateTexFile(filepath,
                            "", 
                            dc.Links.Local.getIdxLineMarkerLine(int(imIdx)), 
                            dc.Links.Local.getIdxLineMarkerLine(int(imIdx) + 1))


    def changeProofsVisibility(hideProofs):
        with open(_upan.Paths.TexFiles.Content.getAbs(),"r") as conF:
            contentLines = conF.readlines()
        
        for i in range(len(contentLines)):
            if (dc.TexFileTokens.extraImagesStartToken in contentLines[i]):
                while (dc.TexFileTokens.extraImagesEndToken not in contentLines[i]):
                    i += 1
                    line = contentLines[i]
                    
                    if dc.TexFileTokens.Proof.proofToken in line.lower():
                        if hideProofs:
                            contentLines[i] = line.replace("% ", "")
                        else:
                            if "% " not in line:
                                contentLines[i] = "% " + line
        
        with open(_upan.Paths.TexFiles.Content.getAbs(),"w") as conF:
            _waitDummy = conF.writelines(contentLines)

    # update the content file
    def addExtraImage(mainImID, extraImageName):
        marker = dc.Links.Local.getIdxLineMarkerLine(mainImID)
        
        with open(_upan.Paths.TexFiles.Content.getAbs(), "r+") as f:
            contentLines = f.readlines()
            lineNum = [i for i in range(len(contentLines)) if marker in contentLines[i]][0]
            
            while dc.TexFileTokens.extraImagesEndToken not in contentLines[lineNum]:
                lineNum += 1
            
            outLines = contentLines[:lineNum]
            extraImageLine = "      \\\\\myStIm{" + extraImageName + "}\n"
            outLines.append(extraImageLine)
            outLines.extend(contentLines[lineNum:])

            f.seek(0)
            f.writelines(outLines)
        
        tfp.TexFilePopulate.populateCurrMainFile()
    
    def __getMainImageLine(subsectionNum, imIdx):
        extraImagePath = _upan.Names.getImageName(imIdx, subsectionNum)
        return "\myTarget{" + extraImagePath + "}{" + imIdx + "}"

    @classmethod
    def addProcessedImage(cls, subsection, imIdx, linkName):     
        imIdx = str(imIdx)
        linkName = str(linkName)
        
        currSubsectionNum = subsection.split("_")[0]
        
        pageToAdd = dc.Links.Local.getIdxLineMarkerLine(imIdx) + "\n"
        pageToAdd += "\
    % TEXT BEFORE MAIN IMAGE\n\
    \n\
    \n\
    % TEXT BEFORE MAIN IMAGE\n\
    " + cls.__getMainImageLine(currSubsectionNum, imIdx) + "\n\
    % TEXT AFTER MAIN IMAGE\n\
    \n\
    \n\
    % TEXT AFTER MAIN IMAGE\n\
    " + dc.TexFileTokens.extraImagesStartToken + "\n\
    " + dc.TexFileTokens.extraImagesEndToken + "\n\
    % TEXT AFTER EXTRA IMAGES\n\
    \n\
    \n\
    % TEXT AFTER EXTRA IMAGES\n\
    \\\\\\rule{\\textwidth}{0.4pt}\n\
    \\\\\\myGlLinks{\n\
        % \\myGlLink{}{}\n\
    }\\\\\n\
    \\TOC\\newpage"
        pageToAdd = [i + "\n" for i in pageToAdd.split("\n")]
        pageToAdd += "\n\n\n"

        conFilepath = _upan.Paths.TexFiles.Content.getAbs(idx = imIdx)

        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(conFilepath):
            ocf.Wr.FsAppCalls.createFile(conFilepath)

        cls.__updateTexFile(_upan.Paths.TexFiles.Content.getAbs(idx = imIdx),
                            pageToAdd, 
                            dc.Links.Local.getIdxLineMarkerLine(int(imIdx)), 
                            dc.Links.Local.getIdxLineMarkerLine(int(imIdx) + 1))

    def formatLinkName(linkName:str, formatBold:bool = True):
        # make the start bold text
        linkName = linkName.replace(" ", "\\ ")
        linkName = linkName.replace("->", "\\rightarrow")
        linkName = linkName.replace("<-", "\\leftarrow")
        
        if linkName.count(":") > 0 and formatBold:
            linkName = linkName.split(":")
            for i in range(len(linkName) - 1):
                ln = linkName[i]
                lnArr = ln.split(" ")
                
                end = tfu.boldenTheText(lnArr[-1] + ":")
                if len(lnArr) > 1:
                    end = " " + end

                lnArr[-1] = end
                linkName[i] = "".join(lnArr)
                
            linkName = "".join(linkName)
        
        linkName = re.sub("([^@])_", r"\1\\ ", linkName)
        
        # work with special "_" that are used in underscore
        linkName = linkName.replace("@_", "_")

        return linkName
    
    @classmethod
    def __getLinkText(cls, imIdx, linkName:str):
        # linkName = cls.formatLinkName(linkName)
        
        # add a start
        linktext = "[{0}]: {1}".format(imIdx, linkName)
        
        return linktext

    @classmethod
    def addImageLinkToTOC_wImage(cls, subsection, imIdx, linkName):
        imIdxStr = str(imIdx)
        linktext = cls.__getLinkText(imIdxStr, linkName)
        
        pageToAdd = dc.Links.Local.getIdxLineMarkerLine(imIdx) + " \n"
        imName = _upan.Names.getImageName(imIdxStr, subsection)
        pageToAdd += "\
    \\mybox{\n\
        " + dc.TexFileTokens.TOC.imTextToken + "{" + linktext + "}\\image[0.5]{" + imName + "}\n\
    }"
        pageToAdd = [i + "\n" for i in pageToAdd.split("\n")]
        pageToAdd += "\n\n\n"

        tocFilepath = _upan.Paths.TexFiles.TOC.getAbs(subsection = subsection, idx = imIdx)
        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(tocFilepath):
            ocf.Wr.FsAppCalls.createFile(tocFilepath)
        
        cls.__updateTexFile(tocFilepath,
                            pageToAdd, 
                            dc.Links.Local.getIdxLineMarkerLine(int(imIdx)), 
                            dc.Links.Local.getIdxLineMarkerLine(int(imIdx) + 1))
        
    @classmethod
    def addImageLinkToTOC_woImage(cls, subsection, imIdx, linkName):
        imIdxStr = str(imIdx)
        linktext = cls.__getLinkText(imIdxStr, linkName)
        
        pageToAdd = dc.Links.Local.getIdxLineMarkerLine(imIdx) + " \n"
        pageToAdd += "\
    \\mybox{\n\
        " + dc.TexFileTokens.TOC.imTextToken + "{" + linktext + "}\n\
    }"
        pageToAdd = [i + "\n" for i in pageToAdd.split("\n")]
        pageToAdd += "\n\n\n"

        tocFilepath = _upan.Paths.TexFiles.TOC.getAbs(subsection = subsection, idx = imIdx)
        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(tocFilepath):
            ocf.Wr.FsAppCalls.createFile(tocFilepath)
        
        cls.__updateTexFile(tocFilepath,
                            pageToAdd, 
                            dc.Links.Local.getIdxLineMarkerLine(int(imIdx)), 
                            dc.Links.Local.getIdxLineMarkerLine(int(imIdx) + 1))
    
    def __updateTexFile(filePath, linesToAdd, startMarker, stopMarker):
        with open(filePath, 'r') as f:
            fileLines = f.readlines()
        
        imIdxLineStartNum = -1
        imIdxLineEndNum = -1
        for i in range(len(fileLines)):
            if startMarker in fileLines[i]:
                log.autolog("The marker: '{0}' was alteady in the \n'{1}' file. Will replace it".format(startMarker, filePath))
                imIdxLineStartNum = i
                while stopMarker not in fileLines[i]:
                    i += 1
                    if i >= len(fileLines):
                        break
                
                if i < len(fileLines) - 3:
                    i += 3
                
                imIdxLineEndNum = i + 1
                break
        
        if imIdxLineStartNum != -1 and imIdxLineEndNum != -1:
            fileLinesBefore = fileLines[:imIdxLineStartNum]
            fileLinesAfter = fileLines[imIdxLineEndNum:]
            fileLines = fileLinesBefore
        
        fileLines.extend(linesToAdd)

        if imIdxLineStartNum != -1 and imIdxLineEndNum != -1:
            fileLines.extend(fileLinesAfter)
        
        with open(filePath, 'w') as f:
            f.writelines(fileLines)
    
    @classmethod
    def addLinkToTexFile(cls, sourceImIDX, contentFileLInes, link, linkName):
        #
        # add link to the current section file
        #
        # read content file

        linkName = cls.formatLinkName(linkName)

        positionToAdd = 0
        while positionToAdd < len(contentFileLInes):
            line = contentFileLInes[positionToAdd]
            # find the line with id
            if dc.Links.Local.getIdxLineMarkerLine(sourceImIDX) in line:
                # find the line with global links start
                while dc.TexFileTokens.Links.Global.linksToken not in line:
                    positionToAdd +=1
                    line = contentFileLInes[positionToAdd]
                # find the line with global links end
                while dc.TexFileTokens.Links.Global.linkToken in line or "href" in line:
                    positionToAdd += 1   
                    line = contentFileLInes[positionToAdd]
                break
            positionToAdd += 1

        outlines = contentFileLInes[:positionToAdd]
        
        lineToAddFull = "        " + tfu.urlLatexWrapper(link, linkName)
        
        lineToAddPdfOnly = ""

        if "KIK" in link:
            lineToAddFull = lineToAddFull.replace("\n", "")
            pdfLink = tfu.replaceUrlType(link, "full", "pdf")
            lineToAddPdfOnly = "        " + tfu.urlLatexWrapper(pdfLink, "[p]")
            lineToAddPdfOnly = lineToAddPdfOnly.replace("\n", "") + ", "
        else:
            lineToAddFull = lineToAddFull.replace("\n", "") + ", "
        
        outlines.append(lineToAddFull)
        
        if "KIK" in link:
            outlines.append(lineToAddPdfOnly)
        
        outlines.extend(contentFileLInes[positionToAdd:])

        return [i for i in outlines]
 