import os

import file_system.file_system_manager as fsm
import tex_file.tex_file_create as tc
import data.constants as d

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