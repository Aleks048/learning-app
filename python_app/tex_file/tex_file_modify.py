import os

import file_system.file_system_facade as fsm
import tex_file.tex_file_create as tc
import data.constants as d
import _utils.logging as log
import _utils._utils_main as _u

class TexFileModify:
    # update the content file
    def addExtraImage(mainImID, extraImagePath):
        marker = "THIS IS CONTENT id: " + mainImID
        with open(fsm.Wr.Paths.TexFiles.Content.getAbs_curr(), "r+") as f:
            contentLines = f.readlines()
            lineNum = [i for i in range(len(contentLines)) if marker in contentLines[i]][0]
            extraImagesMarker = "% \\EXTRA IMAGES END"
            while extraImagesMarker not in contentLines[lineNum]:
                lineNum += 1
            outLines = contentLines[:lineNum]
            extraImageLine = "\\\\\myStIm{" + extraImagePath + "}\n"
            outLines.append(extraImageLine)
            outLines.extend(contentLines[lineNum:])

            f.seek(0)
            f.writelines(outLines)
        
        tc.TexFile._populateMainFile()
    
    def addProcessedImage(imIdx, linkName):
        imIdx = str(imIdx)
        linkName = str(linkName)
        
        currSubsection = fsm.Wr.SectionCurrent.readCurrSection()
        extraImagePath = os.path.join(fsm.Wr.Paths.Screenshot.getAbs_curr(),
                                        imIdx + "_" + currSubsection + "_" + linkName)

        with open(fsm.Wr.Paths.TexFiles.Content.getAbs_curr(), 'a') as f:
                add_page = "\n\n"
                add_page += d.Links.Local.getIdxLineMarkerLine(imIdx) + "\n"
                add_page += "\
        % TEXT BEFORE MAIN IMAGE\n\
        \n\
        \n\
        % TEXT BEFORE MAIN IMAGE\n\
        \\def\\imnum{" + imIdx + "}\n\
        \\def\\linkname{" + linkName + "}\n\
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
                    
                f.write(add_page)
    
    def addImageLinkToTOC_wImage(imIdx, linkName):
        currSubsection = fsm.Wr.SectionCurrent.readCurrSection()
        imIdx = str(imIdx)
        linkName = str(linkName)

        with open(fsm.Wr.Paths.TexFiles.TOC.getAbs_curr(), 'a') as f:
                        toc_add_image = d.Links.Local.getIdxLineMarkerLine(imIdx) + " \n"
                        toc_add_image += "\
    \\mybox{\n\
        \\link[" + imIdx + \
        "]{" + linkName + "} \\image[0.5]{" + \
        imIdx + "_" + currSubsection + "_" + imIdx + "}\n\
    }\n\n\n"
                        f.write(toc_add_image)

    def addImageLinkToTOC_woImage(imIdx, linkName):
        imIdx = str(imIdx)
        linkName = str(linkName)

        with open(fsm.Wr.Paths.TexFiles.TOC.getAbs_curr(), 'a') as f:
                        toc_add_text = d.Links.Local.getIdxLineMarkerLine(imIdx) + " \n"
                        toc_add_text += "\
    \\mybox{\n\
        \\link[" + imIdx + "]{" + linkName + "} \\textbf{!}\n\
    }\n\n\n"
                        f.write(toc_add_text)
    
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