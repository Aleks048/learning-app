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

        def fromTexToImage(tex, savePath):
            buf = io.BytesIO()
            plt.rcParams.update({
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
            plt.text(0.05, 0.05, f'${tex}$', size = 14, wrap = True)
            plt.savefig(buf, format='png')
            plt.clf()

            im = Image.open(buf)
            white = (255, 255, 255, 255)
            bg = Image.new(im.mode, im.size, white)
            bg = bg.convert('RGB')
            im = im.convert('RGB')
            diff = ImageChops.difference(im, bg)
            # diff = ImageChops.add(diff, diff, 2.0, -100)
            bbox = diff.getbbox()
            im = im.crop(bbox)
            
            right = 10
            left = 10
            top = 10
            bottom = 10
            
            width, height = im.size
            
            new_width = width + right + left
            new_height = height + top + bottom
            
            result = Image.new(im.mode, (new_width, new_height), (255, 255, 255))
            result.paste(im, (left, top))

            result.save(savePath)

            return result

        @classmethod
        def fromEntryToLatexTxt(cls, idx, text):
            latexTxt = "\\textbf{" + idx + ":} " + text
            return cls.formatEntrytext(latexTxt)

        def getUrl(bookName, topSection, subsection, imIDX, linkType: str, notLatex = True):
            return tfu.getUrl(bookName, topSection, subsection, imIDX, linkType , notLatex)