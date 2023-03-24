import os

import file_system.file_system_facade as fsm
import tex_file.tex_file_populate as tfp
import data.constants as d
import _utils.logging as log
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan

class TexFileModify:
    # update the content file
    def addExtraImage(mainImID, extraImageName):
        marker = d.Links.Local.getIdxLineMarkerLine(mainImID)
        with open(_upan.Current.Paths.TexFiles.Content.abs(), "r+") as f:
            contentLines = f.readlines()
            lineNum = [i for i in range(len(contentLines)) if marker in contentLines[i]][0]
            extraImagesMarker = "% \\EXTRA IMAGES END"
            while extraImagesMarker not in contentLines[lineNum]:
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
        
        pageToAdd = "\n\n"
        pageToAdd += d.Links.Local.getIdxLineMarkerLine(imIdx) + "\n"
        pageToAdd += "\
    % TEXT BEFORE MAIN IMAGE\n\
    \n\
    \n\
    % TEXT BEFORE MAIN IMAGE\n\
    \\def\\imnum{" + imIdx + "}\n\
    \\def\\linkname{" + linkName.replace("_", " ") + "}\n\
    \\hyperdef{TOC}{\\linkname}{}\n\
    \myTarget{" + extraImagePath + "}{\\linkname\\imnum}\n\
    % TEXT AFTER MAIN IMAGE\n\
    \n\
    \n\
    % TEXT AFTER MAIN IMAGE\n\
    % \EXTRA IMAGES START\n\
    % \EXTRA IMAGES END\n\
    % TEXT AFTER EXTRA IMAGES\n\
    \n\
    \n\
    % TEXT AFTER EXTRA IMAGES\n\
    \\\\\\rule{\\textwidth}{0.4pt}\n\
    \\\\\\myGlLinks{\n\
        % \\myGlLink{}{}\n\
    }\n\
    \\\\Local links: \n\
    \\TOC\\newpage\n"
        pageToAdd = [i + "\n" for i in pageToAdd.split("\n")]

        cls.__updateTexFile(_upan.Current.Paths.TexFiles.Content.abs(),
                            pageToAdd, 
                            d.Links.Local.getIdxLineMarkerLine(int(imIdx)), 
                            d.Links.Local.getIdxLineMarkerLine(int(imIdx) + 1))
        
    @classmethod
    def addImageLinkToTOC_wImage(cls, imIdx, linkName):
        currSubsection = _upan.Current.Names.Section.name()
        imIdx = str(imIdx)
        linkName = str(linkName)
        
        pageToAdd = d.Links.Local.getIdxLineMarkerLine(imIdx) + " \n"
        pageToAdd += "\
    \\mybox{\n\
        \\link[" + imIdx + \
        "]{" + linkName.replace("_", " ") + "} \\image[0.5]{" + \
        imIdx + "_" + currSubsection + "_" + imIdx + "}\n\
    }\n\n\n"
        pageToAdd = [i + "\n" for i in pageToAdd.split("\n")]
        
        cls.__updateTexFile(_upan.Current.Paths.TexFiles.TOC.abs(),
                            pageToAdd, 
                            d.Links.Local.getIdxLineMarkerLine(int(imIdx)), 
                            d.Links.Local.getIdxLineMarkerLine(int(imIdx) + 1))
        
    @classmethod
    def addImageLinkToTOC_woImage(cls, imIdx, linkName):
        imIdx = str(imIdx)
        linkName = str(linkName)
        
        pageToAdd = d.Links.Local.getIdxLineMarkerLine(imIdx) + " \n"
        pageToAdd += "\
    \\mybox{\n\
        \\link[" + imIdx + "]{" + linkName.replace("_", " ") + "} \\textbf{!}\n\
    }\n\n\n"
        pageToAdd = [i + "\n" for i in pageToAdd.split("\n")]
        
        cls.__updateTexFile(_upan.Current.Paths.TexFiles.TOC.abs(),
                            pageToAdd, 
                            d.Links.Local.getIdxLineMarkerLine(int(imIdx)), 
                            d.Links.Local.getIdxLineMarkerLine(int(imIdx) + 1))
    
    def __updateTexFile(filePath, linesToAdd, startMarker, stopMarker):
        with open(filePath, 'r') as f:
            fileLines = f.readlines()
        
        imIdxLineStartNum = -1
        imIdxLineEndNum = -1
        for i in range(len(fileLines)):
            log.autolog("The marker: '{0}' was alteady in the \n'{1}' file. Will replace it".format(startMarker, filePath))
            if startMarker in fileLines[i]:
                imIdxLineStartNum = i
                while stopMarker not in fileLines[i]:
                    i += 1
                    if i >= len(fileLines):
                        break
                imIdxLineEndNum = i + 1
        
        if imIdxLineStartNum != -1 and imIdxLineEndNum != -1:
            fileLinesBefore = fileLines[:imIdxLineStartNum]
            fileLinesAfter = fileLines[imIdxLineEndNum:]
            fileLines = fileLinesBefore
        
        fileLines.extend(linesToAdd)

        if imIdxLineStartNum != -1 and imIdxLineEndNum != -1:
            fileLines.extend(fileLinesAfter)
        
        with open(filePath, 'w') as f:
            f.writelines(fileLines)
    
    def addLinkToTexFile(imIDX, linkName, contenfFilepath, 
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
            if "id: " + imIDX in line:
                # find the line with global links start
                while "\myGlLinks{" not in line:
                    positionToAdd +=1
                    line = lines[positionToAdd]
                # find the line with global links end
                while "myGlLink" in line:
                    positionToAdd += 1   
                    line = lines[positionToAdd]
                break
            positionToAdd += 1
        
        url = "KIK:/" + bookName + "." + topSection + "." + subsection + "." + imIDX
        lineToAdd = "        \href{" + url + "}{" + linkName + "}\n"
        outlines = lines[:positionToAdd]
        outlines.append(lineToAdd)
        outlines.extend(lines[positionToAdd:])
        
        with open(contenfFilepath, "+w") as f:
            for line in outlines:
                f.write(line + "\n")