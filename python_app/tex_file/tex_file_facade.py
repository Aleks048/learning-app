from PIL import Image, ImageChops
import matplotlib.pyplot as plt
import matplotlib as mpl
import io
import re
import fitz
from tex import latex2pdf

import tex_file.tex_file_populate as tfpo
import tex_file.tex_file_modify as tfm
import tex_file.tex_file_process as tfpr
import tex_file.tex_file_utils as tfu

class Data:
    pass

class Wr:
    class TexFilePopulate(tfpo.TexFilePopulate):
        pass

    class TexFileModify(tfm.TexFileModify):
        pass
    
    class TexFileProcess(tfpr.TexFileProcess):
        pass
   
    class TexFileUtils:
        def formatEntrytext(text:str):
            text = text.replace(" ", "\ ")
            text = text.replace("\n", "\\\\")

            return text

        def __fromTexToImage(tex,
                           imageColor,
                           fontSize = 12):
            # \\usepackage[pass, total={{10in, 2in}}]{{geometry}}\
            document = f"\
            \\documentclass[parskip = full]{{article}}\
            \\usepackage[legalpaper, portrait, margin=2in]{{geometry}}\
            \\usepackage{{amsfonts, amsmath, amssymb, dsfont, xcolor}}\
            \\usepackage[T1]{{fontenc}}\
            \\usepackage{{mathptmx}}\
            \\pagenumbering{{gobble}}\
            \\usepackage{{setspace}}\
            \\onehalfspacing\
            \\setlength{{\\parindent}}{{0pt}}\
            \\definecolor{{orange}}{{HTML}}{{{imageColor}}}\
            \\pagecolor{{orange}}\
            \
            \\newcommand{{\\Real}}{{\\mathbb{{R}}}}\
            \\newcommand{{\\Natural}}{{\\mathbb{{N}}}}\
            \\newcommand{{\\Sphere}}{{\\mathbb{{S}}}}\
            \\newcommand{{\\Int}}{{\\mathbb{{Z}}}}\
            \\newcommand{{\\Complex}}{{\\mathbb{{C}}}}\
            \\newcommand{{\\Ball}}{{\\mathbb{{B}}}}\
            \\newcommand{{\\Done}}{{$\\blacksquare$}}\
            \\newcommand{{\\bsl}}{{$\\textbackslash$}}\
            \
            \\begin{{document}}\
            {tex}\
            \\end{{document}}\
            "
            pdf = latex2pdf(document)
            doc = fitz.open("x.pdf", pdf)
            page = doc.load_page(0)
            pixmap = page.get_pixmap(dpi=300)
            return pixmap.tobytes()

        @classmethod
        def fromTexToImage(cls,
                           tex, 
                           savePath, 
                           padding = 10, 
                           imageColor = "#3295a8", 
                           fixedWidth = None, 
                           fixedHeight = None,
                           fontSize = 12,
                           textSize = 14,
                           numSymPerLine = 70,
                           imSize = 700):
            if "excercise" in tex.lower():
                tex = tex.replace("EXCERCISE", "{\\textbf{\\underline{\\textdagger\\ EXCERCISE\\ \\textdagger}}}")

            buf = io.BytesIO(cls.__fromTexToImage(tex, 
                                                  imageColor.replace("#", ""), 
                                                  fontSize))

            im = Image.open(buf)
            im = im.convert('RGB')
            bg = Image.new(im.mode, im.size, imageColor)
            bg = bg.convert('RGB')
            diff = ImageChops.difference(im, bg)
            diff = ImageChops.add(diff, diff, 2.0, -100)
            bbox = diff.getbbox()

            if bbox != None:
                bbox = [bbox[0] - 10,
                        bbox[1] - 10,
                        bbox[2] + 10,
                        bbox[3] + 10]

            im = im.crop(bbox)

            extra = Image.new(im.mode, (1400, im.height), imageColor)
            extra.paste(im, (0, 0))
            extra.thumbnail((imSize, 3500), Image.Resampling.LANCZOS)
            im = extra

            diff = ImageChops.difference(im, bg)
            diff = ImageChops.add(diff, diff, 2.0, -100)
            bbox = diff.getbbox()

            if bbox != None:
                bbox = [bbox[0] - 2,
                        bbox[1] - 2,
                        bbox[2] + 20,
                        bbox[3] + 2]

            if bbox[2] - bbox[0] < im.size[0]:
                im = im.crop(bbox)

            right = padding
            left = padding
            top = padding
            bottom = padding
            
            width, height = im.size
            
            # NOTE: this will allow to set the fixed width for the created image
            if fixedWidth == None:
                new_width = width + right + left
            else:
                new_width = fixedWidth
            
            if fixedHeight == None:
                new_height = height + top + bottom
            else:
                new_height = fixedHeight

            
            result = Image.new(im.mode, (new_width, new_height), imageColor)
            result.paste(im, (left, top))

            result.save(savePath)

            return result

        @classmethod
        def fromEntryToLatexTxt(cls, idx, text):
            latexTxt = "\\textbf{" + idx + ":} " + text
            return cls.formatEntrytext(latexTxt)

        def getUrl(bookName, topSection, subsection, imIDX, linkType: str, notLatex = True):
            return tfu.getUrl(bookName, topSection, subsection, imIDX, linkType , notLatex)