def boldenTheText(text):
    return "\\begin{bfseries}" + text + "\\end{bfseries}"

def addNormalText(text):
    return "\\textrm{{{0}}}".format(text)

def getUrl(bookName, topSection, subsection, imIDX, linkType: str, notLatex = False):
    if notLatex:
        return "KIK://{0}/{1}/{2}/{3}/{4}".format(bookName, topSection, subsection, imIDX, linkType)
    else:
        return "KIK:/{0}/{1}/{2}/{3}/{4}".format(bookName, topSection, subsection, imIDX, linkType)

def getLinkLine(bookName, topSection, subsection, imIDX, linkName: str, linkType: str):
    url = getUrl(bookName, topSection, subsection, imIDX, linkType)
    return "\href{" + url + "}{" + linkName + "}\n"