from PIL import ImageTk,Image, ImageChops
import matplotlib.pyplot as plt
import matplotlib as mpl
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

        def fromTexToImage(tex, 
                           savePath, 
                           padding = 10, 
                           imageColor = "#3295a8", 
                           fixedWidth = None, 
                           fixedHeight = None,
                           fontSize = 12,
                           textSize = 14):
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

            buf = io.BytesIO()
            params = plt.rcParams.copy()
            params ['font.size'] = fontSize
            params ['font.family'] = "serif"
            params ['text.usetex'] = True
            params ['text.latex.preamble'] =  r'\usepackage{amsfonts}'
            params['figure.facecolor'] = imageColor

            if "excercise" in tex.lower():
                params['text.color'] = "red"
            else:
                params['text.color'] = "black"

            with mpl.rc_context(params):
                fig, ax = plt.subplots()
                fig.set_facecolor(mpl.rcParams['figure.facecolor'])
                ax.set_facecolor(mpl.rcParams['axes.facecolor'])
                plt.rcParams.update(params)
                plt.ioff()
                plt.axis('off')
                plt.tight_layout()
                plt.text(0.05, 0.05, f'\\noindent${tex}$', size = textSize)
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