from PIL import Image, ImageChops
import matplotlib.pyplot as plt
import matplotlib as mpl
import io
import re

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

        def fromTexToImage(tex, 
                           savePath, 
                           padding = 10, 
                           imageColor = "#3295a8", 
                           fixedWidth = None, 
                           fixedHeight = None,
                           fontSize = 12,
                           textSize = 14,
                           numSymPerLine = 70):
            texList = tex.split("\\ ")
            chCounter = 0
            tex = ""

            for w in texList:
                # NOTE: we remove the newLine + latex tokens + "}"
                # to avoid incorrect calculations and newline being ignored
                # we replece it withthe token and then bring back
                w = w.replace("\\\\", "__NEWLINE__")
                splittedWord = re.split(r"\\[[a-z]+|[A-Z]+]+", w)
                w = w.replace("__NEWLINE__", "\\\\")

                for i in range(len(splittedWord)):
                    splittedWord[i] = splittedWord[i].replace("__NEWLINE__", "\\\\")
                    splittedWord[i] = re.sub(r"{[a-z]+}", "", splittedWord[i])

                # NOTE: we do use this to add one to count for the
                # symbols of the kind ex: '\subset'
                if len([i for i in splittedWord if i != ""]) == 0:
                    splittedWord = ["1"]

                for sw in splittedWord:
                    if "\\\\" in sw:
                        chCounter = 0

                filteredWord = "".join(splittedWord)\
                              .replace("\\", "")\
                              .replace("}", "")\
                              .replace("{", "")

                wordLen = len(filteredWord)

                if ((chCounter + wordLen + 1) > numSymPerLine):
                    tex += "\\\\[10pt]"
                    chCounter = 0

                chCounter += wordLen + 1
                tex += w + "\\ "

            texList = tex.split("\\\\")
            fullTex = f"\\noindent${tex}$"
            # NOTE: this is left here in case
            # I will want to split the lines into separate formulas
            # fullTex = f"\\noindent"
            # for line in texList:
            #     fullTex += f'${line}$' + "\\\\"
            # fullTex = fullTex[:-2]

            buf = io.BytesIO()
            params = plt.rcParams.copy()
            params['font.size'] = fontSize
            params['font.family'] = "serif"
            params['text.usetex'] = True
            params['text.latex.preamble'] =  r'\usepackage{amsfonts, amsmath, amssymb, dsfont}'
            params['figure.facecolor'] = imageColor

            if "excercise" in tex.lower():
                params['text.color'] = "red"
            elif "important!" in tex.lower():
                params['text.color'] = "blue"
            elif "\\square" in tex.lower():
                params['text.color'] = "#700470"
            else:
                params['text.color'] = "black"

            with mpl.rc_context(params):
                fig, ax = plt.subplots()
                fig.set_facecolor(mpl.rcParams['figure.facecolor'])
                ax.set_facecolor(mpl.rcParams['axes.facecolor'])
                plt.rcParams.update(params)
                plt.ioff()
                # NOTE: this is a hacky workaround to avoid cropping the lines
                plt.figure(figsize=(20,6))
                plt.axis('off')
                # plt.tight_layout()
                plt.text(0.15, 0.35, fullTex,
                         size = textSize)
                plt.savefig(buf, format='png')
                plt.clf()
                plt.close()

            im = Image.open(buf)
            bg = Image.new(im.mode, im.size, imageColor)
            bg = bg.convert('RGB')
            im = im.convert('RGB')
            diff = ImageChops.difference(im, bg)
            # diff = ImageChops.add(diff, diff, 2.0, -100)
            bbox = diff.getbbox()
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