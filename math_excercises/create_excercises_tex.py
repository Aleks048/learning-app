'''
    1 DONE get path to the file from the arguments 
    2 DONE run throught the images and of excercises and 
            add links to the ImagesAndLinks files with tags
    3 DONE add the includes with tags into the excercisesImagesAndLinks.tex  
'''
from asyncore import write
from math import floor
import sys
import os

exercisesImagesRelPath = "./images/excercises/original/"
exercisesSolutionsRelPath = "./images/excercises/solutions/"
imagesExtension = ".png"
imagesMultipleImagesSeparator = " "
linksTexIndicator = "% LINKS START HERE"


def filePathToParentDir(fp):
    return "/".join(fp.split("/")[:-1])

def traverseOverFolderAndGetImagesPaths(imagesRelPaths, imagesDir, imagesRelDir):
    for filename in os.listdir(imagesDir):
        f = os.path.join(imagesDir, filename)
        # checking if it is a file of type .png
        if imagesExtension in filename:
            if os.path.isfile(f):
                imagesRelPaths.append(imagesRelDir + filename)

def groupImagesPaths(imagesRelPathsGrouped):
    imagesRelPathsGroup = []
    for imP in imagesRelPaths:
        imagesRelPathsGroup.append(imP)
        if " " not in imP:
            if imagesRelPathsGroup != []:
                imagesRelPathsGrouped.append(imagesRelPathsGroup)
            imagesRelPathsGroup = []

'''
get the path and parent directory of the file that called from the arguments
'''
args = []
for i in range(1, len(sys.argv)):
    args.append(sys.argv[i])

callerFilepath = args[0]
callerExcerciseImagesDirectory  = filePathToParentDir(args[0]) + exercisesImagesRelPath[1:]

'''
get relative paths of the excercises images
'''
imagesRelPaths = []
traverseOverFolderAndGetImagesPaths(imagesRelPaths, callerExcerciseImagesDirectory, exercisesImagesRelPath)

'''
sort the images paths and group them by excercise
'''
imagesRelPaths.sort()
imagesRelPathsGrouped = []
groupImagesPaths(imagesRelPathsGrouped)


'''
create the images links in the tex file
'''
names = []
texStringsArr = []
for i in range(0, len(imagesRelPathsGrouped)):
    name = ""
    nameFull = ""
    strSplit = ""
    sortedArr = []
    if len(imagesRelPathsGrouped[i]) > 1: 
        sortedArr =  sorted(imagesRelPathsGrouped[i], key = lambda x: len(x))
        strSplit = sortedArr[0].split("/")
        name = strSplit[-1][:-4].replace("_","")
        nameFull = strSplit[-1]
    else:
        strSplit = imagesRelPathsGrouped[i][0].split("/")
        name = strSplit[-1][:-4].replace("_","")
        nameFull = strSplit[-1]
    names.append(name)

    # add the opening tag
    tagStr = "\n\
%<*" + name + ">\n"
    # add the main excercises images
    tagStr += "\
    \\def\\imnum{3}\n\
    \\def\\imname{" + name + "}\n\
    \\def\\linkname{" + name + "}\n\
    \hyperdef{TOC}{" + name + "}{}\n\
    \\target{" + name + "}\n\
    \\href{run:." + exercisesImagesRelPath + nameFull + "}{\n\
        \\includegraphics[scale = 0.6]{." + exercisesImagesRelPath + nameFull + "}\n\
    }\n\
"

    # add the extra excercise images
    if (len(imagesRelPathsGrouped[i]) > 1):
        for i in range(2,len(imagesRelPathsGrouped[i]) + 1):
            tagStr += "\
    \\\\\n\
    \\href{run:." + exercisesImagesRelPath + nameFull[:-4] + imagesMultipleImagesSeparator + str(i) + ".png}{\n\
        \\includegraphics[scale = 0.6]{." + exercisesImagesRelPath + nameFull[:-4] + imagesMultipleImagesSeparator + str(i) + ".png}\n\
    }\n\
"

    #add the ending tag
    tagStr += "\
%</" + name + ">\n"
    texStringsArr.append(tagStr)


'''
write to excercisesImagesAndlinks.tex file
'''
tagStrAll = "\n".join(texStringsArr)
with open(callerFilepath, "w") as f:
    f.write(tagStrAll)

'''
update the excercises.tex file
'''
excercisesMainFilePath = callerFilepath.replace("ImagesAndLinks","")
excercisesIandLFileName = callerFilepath.split("/")[-1]

texGetBetweenTagstr = "\
    % \\solutionsfalse\n\
    \ExecuteMetaData[../" + excercisesIandLFileName + "]{name}\n\
    \\TOC\n\
    \\newpage\n"
texTOCstr = "\
        \\hyperlink{name}{name}"
texTOCglLinkStr = "\
        \\hyperref{filename.pdf}{TOC}{section}{section}"

tocStartStr = "/TOC/"
linksStartStr = "LINKS START HERE"

numExcPerFile = 15
numExcFiles = floor((len(names) + 1)/numExcPerFile)

def addTOClinks(lines, names, numItemsPerLine, i, startIdx, endIdx):
    allLines = "".join(lines)
    counter = 1
    for k in range(len(names)):
        name = names[k]
        link = ""

        if k in range(startIdx, endIdx):
            link = texTOCstr.replace("name", name)
        else:
            fn = formatMainFilePath(floor(k / numExcPerFile))
            link = texTOCglLinkStr.replace("filename", fn.split("/")[-1][:-4])
            link = link.replace("section", name)
        
        if counter % numItemsPerLine == 0:
            link += "\\\\"
        else:
            link += "\\hspace*{0.2cm}"
        
        if "{" + name + "}{" + name + "}" not in allLines:
            lines.insert(i + counter, link)
        else:
            for j in range(i, len(lines)):
                if name in lines[j]:
                    lines[j] = link
                elif linksStartStr in lines[j]:
                    break
        counter += 1

def addImageLinks(lines, names, i, startIdx, endIdx):
    allLines = "".join(lines)
    counter = 1
    for k in range(startIdx,endIdx):
        name = names[k]
        if "]{" + name not in allLines:          
            lines.insert(i + counter, texGetBetweenTagstr.replace("name", name))
        else:
            for j in range(i, len(lines)):
                if name in lines[j]:
                    lines[j] = texGetBetweenTagstr.replace("name", name).split("\n")[1]
        counter += 1

def formatMainFilePath(num):
    return excercisesMainFilePath[:-4] + "-" + str(num) + ".tex"

lines = []
for l in range(numExcFiles + 1):
    excercisesMainFilePathFormated = formatMainFilePath(l)
    # if the excercises file does not exist create it
    if not os.path.exists(excercisesMainFilePathFormated):
        f = open(excercisesMainFilePathFormated, "w+")
        f.close()
    # if the file exists but empty populate it
    if os.path.getsize(excercisesMainFilePathFormated) == 0:
        with open(os.getenv("BOOKS_PROCESS_TEX_PATH") + "/template.tex", "r") as file:
            # read the temptate file
            lines = file.readlines()
            lines = [line.rstrip() for line in lines]

        #addTOC
        for i in range(len(lines)):
            line = lines[i]
            if tocStartStr in line:
                addTOClinks(lines, names, 7, i, l * numExcPerFile, min((l +1) * numExcPerFile,len(names)))
                break
        
        #add links
        for i in range(len(lines)):
            line = lines[i]
            if linksStartStr in line:
                addImageLinks(lines, names, i, l * numExcPerFile, min((l +1) * numExcPerFile,len(names)))
                break
        
        with open(excercisesMainFilePathFormated, "w") as exFile:
            for line in lines:        
                exFile.write(line + "\n")
    # if the file exist and not empty update it
    else:
        with open(excercisesMainFilePathFormated, "r+") as exFile:
            lines = exFile.readlines()
            lines = [line.rstrip() for line in lines]
            exFile.truncate(0)
            exFile.seek(0)

            # add TOC
            idxTOCStr = 0
            for i in range(len(lines)):
                if tocStartStr in lines[i]:
                    idxTOCStr = i
                    break
            addTOClinks(lines, names, 7, idxTOCStr, l * numExcPerFile, min((l +1) * numExcPerFile,len(names)))

            # add links
            idxLinksStr = 0
            for i in range(idxTOCStr, len(lines)):
                if linksStartStr in lines[i]:
                    idxLinksStr = i
                    break
            addImageLinks(lines, names, idxLinksStr, l * numExcPerFile, min((l +1) * numExcPerFile,len(names)))

            for line in lines:
                exFile.write(line + "\n")

# os.system("echo \"" + str(numExcFiles) + "\" > " + "/Users/ashum048/books/test.txt")

