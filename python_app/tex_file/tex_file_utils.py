def boldenTheText(text):
    return "\\begin{bfseries}" + text + "\\ \\end{bfseries}"

def addNormalText(text):
    return "\\textrm{{{0}}}".format(text)

def getLinkLine(bookName, topSection, subsection, imIDX, linkName: str, linkType: str):
    url = "KIK:/{0}/{1}/{2}/{3}".format(bookName, topSection, subsection, imIDX)
    return "\href{" + url + "/" + linkType + "}{" + linkName + "}\n"