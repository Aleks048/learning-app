import file_system.file_system_manager as fsm
import tex_file.tex_file_create as tc

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