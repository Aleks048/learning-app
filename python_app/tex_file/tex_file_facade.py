from PIL import ImageTk,Image, ImageChops
import matplotlib.pyplot as plt
import io

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
            return text

        def fromTexToImage(tex, savePath, padding = 10):
            texList = tex.split("\\ ")
            chCounter = 0
            tex = ""

            for w in texList:
                wordLen = len(w + "\\ ")
                chCounter += wordLen
                tex += w + "\\ " 
    
                if chCounter > 55:
                    tex += "\\\\"
                    chCounter = 0

            imageColor = "#3295a8"

            buf = io.BytesIO()
            plt.rcParams.update({
                'figure.facecolor': imageColor,
                'font.size': 12,
                'font.family': "serif",
                'text.usetex': True,
                'text.latex.preamble': r'\usepackage{amsfonts}'
            })

            if "excercise" in tex.lower():
                plt.rcParams.update({
                    'text.color': "red",
                })
            else:
                plt.rcParams.update({
                    'text.color': "black",
                })

            plt.ioff()
            plt.axis('off')
            plt.tight_layout()
            plt.text(0.05, 0.05, f'\\noindent${tex}$', size = 14)
            plt.savefig(buf, format='png')
            plt.clf()

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
            
            new_width = width + right + left
            new_height = height + top + bottom
            
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