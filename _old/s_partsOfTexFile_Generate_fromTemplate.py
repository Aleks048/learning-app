import sys
import os
sys.path.append(os.getenv("BOOKS_PY_APP_PATH"))

from _utils import _utils

# output file
outFile = []

# read the filepath from the argvalue
filepath = _utils.readPyArgs()[0]

# read the .tex file 
texFile = _utils.readFile(filepath)

# read the template file
template = _utils.readFile(os.getenv("BOOKS_PROCESS_TEX_PATH") + "/template.tex")

# get the marker of the part BEFORE TOC
# 
# replace everything before marker from template 
beforeTOCmarker = "BEFORE_TOC_MARKER"
beforeTOCmarkerPos = next(i for i,v in enumerate(texFile) if beforeTOCmarker in v)
beforeTOCmarkerPosTem = next(i for i,v in enumerate(template) if beforeTOCmarker in v)
outFile = template[:beforeTOCmarkerPosTem]

# get the marker of the part AFTER TOC and BEFORE IMAGES
# 
# replace everything betweeen markers
afterTOCmarker = "AFTER_TOC_MARKER"
afterTOCmarkerPos = next(i for i,v in enumerate(texFile) if afterTOCmarker in v)
afterTOCmarkerPosTem = next(i for i,v in enumerate(template) if afterTOCmarker in v)
outFile.extend(texFile[beforeTOCmarkerPos: afterTOCmarkerPos])

beforePICmarker = "BEFORE_PIC_MARKER"
beforePICmarkerPos = next(i for i,v in enumerate(texFile) if beforePICmarker in v)
beforePICmarkerPosTem = next(i for i,v in enumerate(template) if beforePICmarker in v)
outFile.extend(template[afterTOCmarkerPosTem: beforePICmarkerPosTem])

# get the marker of the part in the END
# 
# replace everything after marker from template 
afterPICmarker = "AFTER_PIC_MARKER"
afterPICmarkerPos = next(i for i,v in enumerate(texFile) if afterPICmarker in v)
afterPICmarkerPosTem = next(i for i,v in enumerate(template) if afterPICmarker in v)
outFile.extend(texFile[beforePICmarkerPos:afterPICmarkerPos + 1])
outFile.extend(template[afterPICmarkerPosTem + 1:])

# update calling file
with open(filepath, "r+") as exFile:
    for line in outFile:
        exFile.write(line + "\n")