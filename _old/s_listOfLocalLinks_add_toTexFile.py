import sys
import os
sys.path.append(os.getenv("BOOKS_PY_APP_PATH"))

from _utils import _utils


def createLocalLinkFromImNumString(line):
    global imNumString
    line = line.replace("\def\imnum{", "")[:-1]
    line = line.replace(" ", "")
    return line
def createLocalLinkFromLinknameString(line):
    global imLinknameString
    line = line.replace(imLinknameString, "")[:-1]
    line = line.replace(" ", "")
    return line

# read the filepath from the argvalue
filepath = _utils.readPyArgs()[0]

# read the .tex file 
texFile = _utils.readFile(filepath)

# mark the line where we find the marker
localLinksMarker = "LOCAL_LINKS"
localLinksMarkerPositions = _utils.getPositionsOfMarker(texFile, localLinksMarker)

# create the list of local links
listOfLocalLinks = []

# insertMarker = "_pos"
imNumString = "\def\imnum{"
imLinknameString = "\def\linkname{"

localLinkString = "\link"

for i in range(0, len(texFile)):
    line = texFile[i]
    if imNumString in line:
        listOfLocalLinks.append(localLinkString + "[" 
                + createLocalLinkFromImNumString(line) + "]{"
                + createLocalLinkFromLinknameString(texFile[i + 2]) + "}")
        i += 2

localLinksLine = "[" + ",".join(listOfLocalLinks) + "]" + " %" + localLinksMarker


# update the file lines list
for i in localLinksMarkerPositions:
    texFile[i] = "\\\\Local links:" + localLinksLine

# update calling file
with open(filepath, "r+") as exFile:
    for line in texFile:
        exFile.write(line + "\n")


# NOTE: we should add some text that would let us know that the line is generated
