import os

import file_system.file_system_facade as fsm
import tex_file.tex_file_populate as tfp
import data.constants as dc
import re

import _utils.logging as log
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import settings.facade as sf


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
    
    @classmethod
    def addProcessedImage(cls, imIdx, linkName):     
        imIdx = str(imIdx)
        linkName = str(linkName)
        
        currSubsection = fsm.Wr.SectionCurrent.getSectionNameNoPrefix()
        currSubsectionNum = currSubsection.split("_")[0]
        extraImagePath = imIdx + "__" + currSubsectionNum + "__" + linkName
        
        pageToAdd = dc.Links.Local.getIdxLineMarkerLine(imIdx) + "\n"
        pageToAdd += "\
    % TEXT BEFORE MAIN IMAGE\n\
    \n\
    \n\
    % TEXT BEFORE MAIN IMAGE\n\
    \\def\\imnum{" + imIdx + "}\n\
    \\def\\linkname{" + linkName.replace("_", " ") + "}\n\
    \\hyperdef{TOC}{\\linkname}{}\n\
    \myTarget{" + extraImagePath + "}{\\imnum}\n\
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
    }\n\
    \\\\Local links: \n\
    \\TOC\\newpage"
        pageToAdd = [i + "\n" for i in pageToAdd.split("\n")]
        pageToAdd += "\n\n\n"

        cls.__updateTexFile(_upan.Paths.TexFiles.Content.getAbs(),
                            pageToAdd, 
                            dc.Links.Local.getIdxLineMarkerLine(int(imIdx)), 
                            dc.Links.Local.getIdxLineMarkerLine(int(imIdx) + 1))

    def __formatLinkName(linkName:str, formatBold:bool = True):
        # make the start bold text
        linkName = linkName.replace(" ", "\\ ")
        
        linkName = linkName.replace(":", "_")
        
        if linkName.count("__") == 1 and formatBold:
            linkName = linkName.split("__")
            linkName = "\\textbf{" + linkName[0] + ":}\ " + "".join(linkName[1:])
            #replace all '_' but the special ones with ' '
        
        linkName = re.sub("([^@])_", r"\1\\ ", linkName)
        
        # work with special "_" that are used in underscore
        linkName = linkName.replace("@_", "_")

        return linkName
    
    @classmethod
    def __getLinkText(cls, imIdx, linkName:str):
        linkName = cls.__formatLinkName(linkName)
        
        # add a start
        linktext = "[{0}]:\ {1}".format(imIdx, linkName)
        
        return linktext

    @classmethod
    def addImageLinkToTOC_wImage(cls, imIdx, linkName):
        currSubsection = _upan.Current.Names.Section.name()
        imIdxStr = str(imIdx)
        linktext = cls.__getLinkText(imIdxStr, linkName)
        linkNameFormatted = cls.__formatLinkName(linkName, False)
        
        pageToAdd = dc.Links.Local.getIdxLineMarkerLine(imIdx) + " \n"
        pageToAdd += "\
    \\mybox{\n\
        \\link[" + imIdxStr + "]{" + linktext + "} \\image[0.5]{" + \
        imIdxStr + "__" + currSubsection + "__" + linkNameFormatted + "}\n\
    }"
        pageToAdd = [i + "\n" for i in pageToAdd.split("\n")]
        pageToAdd += "\n\n\n"
        
        cls.__updateTexFile(_upan.Paths.TexFiles.TOC.getAbs(),
                            pageToAdd, 
                            dc.Links.Local.getIdxLineMarkerLine(int(imIdx)), 
                            dc.Links.Local.getIdxLineMarkerLine(int(imIdx) + 1))
        
    @classmethod
    def addImageLinkToTOC_woImage(cls, imIdx, linkName):
        imIdxStr = str(imIdx)
        linktext = cls.__getLinkText(imIdxStr, linkName)
        
        pageToAdd = dc.Links.Local.getIdxLineMarkerLine(imIdx) + " \n"
        pageToAdd += "\
    \\mybox{\n\
        \\link[" + imIdxStr + "]{" + linktext + "}\n\
    }"
        pageToAdd = [i + "\n" for i in pageToAdd.split("\n")]
        pageToAdd += "\n\n\n"
        
        cls.__updateTexFile(_upan.Paths.TexFiles.TOC.getAbs(),
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
    def addLinkToTexFile(cls, imIDX, linkName, contenfFilepath, 
                        bookName, topSection, subsection):
        #
        # add link to the current section file
        #
        # read content file
        log.autolog("Updating file: " + contenfFilepath)
        lines = _u.readFile(contenfFilepath)
        positionToAdd = 0
        while positionToAdd < len(lines):
            line = lines[positionToAdd]
            # find the line with id
            if dc.Links.Local.getIdxLineMarkerLine(imIDX) in line:
                # find the line with global links start
                while dc.TexFileTokens.Links.Global.linksToken not in line:
                    positionToAdd +=1
                    line = lines[positionToAdd]
                # find the line with global links end
                while dc.TexFileTokens.Links.Global.linkToken in line:
                    positionToAdd += 1   
                    line = lines[positionToAdd]
                break
            positionToAdd += 1
        
        lineToAddFull = "        " + cls.getLinkLine(bookName, topSection, subsection, imIDX, linkName, "full")
        lineToAddPdfOnly = "        " + cls.getLinkLine(bookName, topSection, subsection, imIDX, linkName, "pdf")
        outlines = lines[:positionToAdd]
        outlines.append(lineToAddFull)
        outlines.append(lineToAddPdfOnly)
        outlines.extend(lines[positionToAdd:])
        
        with open(contenfFilepath, "+w") as f:
            for line in outlines:
                f.write(line + "\n")
    
    def getLinkLine(bookName, topSection, subsection, imIDX, linkName: str, linkType: str):
        url = "KIK:/{0}/{1}/{2}/{3}".format(bookName, topSection, subsection, imIDX)
        return "\href{" + url + "/" + linkType + "}{" + linkName + "}\n"