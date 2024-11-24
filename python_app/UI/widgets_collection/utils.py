from tkinter import ttk
from PIL import Image, ImageTk, ImageOps
import tkinter as tk
from AppKit import NSPasteboard, NSStringPboardType
from tkinter import scrolledtext
import time
import re
from threading import Thread
import os
import copy

import UI.widgets_wrappers as ww
import UI.widgets_data as wd
import UI.widgets_facade as wf
import UI.widgets_collection.common as comw

import file_system.file_system_facade as fsf
import data.constants as dc
import data.temp as dt
import _utils.pathsAndNames as _upan
import settings.facade as sf
import _utils._utils_main as _u
import outside_calls.outside_calls_facade as ocf
import generalManger.generalManger as gm



class MultilineText_ETR(scrolledtext.ScrolledText):
    def __init__(self, parentWidget, prefix, row, column, imLineIdx, text, *args, **kwargs):
        self.imIdx = None
        self.eImIdx = None
        self.subsection = None
        self.etrWidget = None
        self.lineImIdx = None

        self.root = parentWidget

        self.defaultText = text

        txt = ""
        lineLength = 0

        txtList = text.split(" ")

        for w in txtList:
            lineLength += len(w.replace("\n", "")) + 1
            txt += w + " "

            if ("\n" in w) or (lineLength > 70):
                if not("\n" in w):
                    txt += "\n"

                lineLength = 0

        newHeight = int(len(txt.split("\n"))) + 1
        self.row = row
        self.column = column

        super().__init__(parentWidget, 
                         wrap = None, 
                         width = 70, 
                         height = newHeight, 
                         *args, 
                         **kwargs)
        self.config(spacing1 = 10)
        self.config(spacing2 = 10)
        self.config(spacing3 = 12)
        self.insert(tk.END, text)

        self.config(height = newHeight)
        self.place(x = 0, y = 0)
        self.bind(ww.currUIImpl.Data.BindID.Keys.ctrlv,
                  lambda *args: self.__pasteText(*args))

    def __pasteText(self, *args):
        pos = self.index(tk.INSERT)
        oldText = self.get("0.0", tk.END)

        pb = NSPasteboard.generalPasteboard()
        text:str = pb.stringForType_(NSStringPboardType)

        text = text.replace("\u0000", "fi")

        self.insert(tk.INSERT, text)

    def getData(self):
        try:
            binString = self.get('1.0', tk.END)
            if binString[-1] == "\n":
                return binString[:-1]
            return binString
        except:
            return _u.Token.NotDef.str_t
        bitStringIsEmpty = len([i for i in binString if i=="" or i == "\n"]) == len(binString)

        # removing the unnecessary newlines from the end
        while binString[-1] == "\n":
            binString = binString[:-1]

            if len(binString) == 0:
                binString = _u.Token.NotDef.str_t
                break

        return binString if not bitStringIsEmpty else _u.Token.NotDef.str_t

    def rebind(self, keys, funcs):
        for i in range(len(keys)):
            self.bind(keys[i], funcs[i])
        
        def __boldenText(*args):
            startSelIDX = self.index("sel.first")
            endSelIDX = self.index("sel.last")
            selText = self.get(startSelIDX, endSelIDX)
            boldSelText = f"\\textbf{{{selText}}}"
            self.replace(startSelIDX, endSelIDX, boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdb,
                  lambda *args: __boldenText(*args))

        def __underlineText(*args):
            startSelIDX = self.index("sel.first")
            endSelIDX = self.index("sel.last")
            selText = self.get(startSelIDX, endSelIDX)
            boldSelText = f"\\underline{{{selText}}}"
            self.replace(startSelIDX, endSelIDX, boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdu,
                  lambda *args: __underlineText(*args))

        def __addNote(*args):
            boldSelText = "\\textbf{NOTE:} "
            self.insert("0.0", boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdn,
                  lambda *args: __addNote(*args))

        def __addNoteInPlace(*args):
            boldSelText = "\\textbf{NOTE:} "
            self.insert(tk.INSERT, boldSelText)

        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdshn,
                  lambda *args: __addNoteInPlace(*args))

        def __addDef(*args):
            boldSelText = "\\textbf{DEF:} "
            self.insert(tk.INSERT, boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdd,
                  lambda *args: __addDef(*args))

        def __addProposion(*args):
            boldSelText = "\\textbf{Proposition:} "
            self.insert(tk.INSERT, boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdshp,
                  lambda *args: __addProposion(*args))

        def __addExample(*args):
            boldSelText = "\\textbf{EX:} "
            self.insert("0.0", boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmde,
                  lambda *args: __addExample(*args))

        def __addLemma(*args):
            boldSelText = "\\textbf{Lemma:} "
            self.insert("0.0", boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdl,
                  lambda *args: __addLemma(*args))

        def __addCorollary(*args):
            boldSelText = "\\textbf{Corollary:} "
            self.insert("0.0", boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdshc,
                  lambda *args: __addCorollary(*args))

        def __addCode(*args):
            boldSelText = "\\textbf{Code:} "
            self.insert("0.0", boldSelText)

        self.bind(ww.currUIImpl.Data.BindID.Keys.cmddc,
                  lambda *args: __addCode(*args))

        def __addExcercise(*args):
            boldSelText = "\\textbf{\\underline{EXCERCISE:}} "
            self.insert("0.0", boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdshe,
                  lambda *args: __addExcercise(*args))

        def __addTheorem(*args):
            boldSelText = "\\textbf{Theorem:} "
            self.insert("0", boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdt,
                  lambda *args: __addTheorem(*args))

        def __addProof(*args):
            boldSelText = "proof"
            self.insert("0", boldSelText)
        
        self.bind(ww.currUIImpl.Data.BindID.Keys.cmdp,
                  lambda *args: __addProof(*args))

    def render(self):
        self.grid(row = self.row, column = self.column)
    
    def generateEvent(self, event):
        self.event_generate(event)


class ImageSize_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix, row, column, imIdx, text, width = 3):
        self.subsection = None
        self.imIdx = None
        self.textETR = None

        name = "_imageSizeTOC_ETR" + str(imIdx)
        self.defaultText = text

        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }


        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wd.Data.ENT.defaultTextColor,
                                            "font": ('Georgia 14')},
            ww.TkWidgets.__name__ : {"width": width}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraBuildOptions,
                        defaultText = self.defaultText)
        super().setData(self.defaultText)

    def receiveNotification(self, _):
        return self.getData()

    def defaultTextCMD(self):
        pass


class TOCFrame(ttk.Frame):
    def __init__(self, root, prefix, row, column, columnspan = 1, *args, **kwargs) -> None:
        self.subsection = None
        self.imIdx = None

        self.row = row
        self.column = column
        self.columnspan = columnspan

        super().__init__(root, name = prefix, *args, **kwargs)

    def render(self):
        self.grid(row = self.row, column = self.column, 
                  columnspan = self.columnspan, sticky=tk.NW)

    def getChildren(self):
        return self.winfo_children()

class TOCTextWithClick(tk.Text):
    '''
    this is used to run different commands on whether the label was clicked even or odd times
    '''

    def rebind(self, keys, cmds):
        for i in range(len(keys)):
            key = keys[i]
            cmd = cmds[i]

            if key == ww.TkWidgets.Data.BindID.allKeys:
                self.bind_all(key, lambda event: cmd(event))
            else:
                self.bind(key, cmd)

    def __init__(self, root, prefix, row, column, columnspan = 1, sticky = tk.NW, text = "", *args, **kwargs) -> None:
        self.clicked = False
        self.imIdx = ""
        self.subsection = ""
        self.imagePath = ""
        self.group = ""
        self.image = None
        self.alwaysShow = None
        self.shouldShowExMenu = False
        self.lineImIdx = _u.Token.NotDef.str_t
        self.etrWidget = _u.Token.NotDef.str_t
        self.sticky = None
        self.tocFrame = None
        self.eImIdx = None
        self.targetSubssection = None
        self.targetImIdx = None
        self.sourceSubssection = None
        self.sourceImIdx= None
        self.sourceWebLinkName = None

        self.root = root
        self.text = text
        
        self.row = row
        self.column = column
        self.columnspan = columnspan
        self.sticky = sticky

        super().__init__(root, name = prefix)
        self.setText()

    def setText(self):
        text = self.text
        
        self.config(spacing1 = 10)
        self.config(spacing2 = 10)
        self.config(spacing3 = 12)
        self.config(wrap = tk.WORD)

        self.insert(tk.END, text)

        txtList = text.split(" ")
        txt = ""
        lineLength = 0

        for w in txtList:
            lineLength += len(w.replace("\n", "")) + 1
            txt += w + " "

            if ("\n" in w) or (lineLength > 113):
                if not("\n" in w):
                    txt += "\n"

                lineLength = 0

        Font_tuple = ("TkFixedFont", 12)
        self.config(font = Font_tuple)
        self.config(width = 85)
        self.config(height = int(len(txt.split("\n"))))
        self.config(background = "#394d43")
        self.config(state=tk.DISABLED)
        self.place(x = 0, y = 0)
    
    def render(self):
        self.grid(row = self.row, column = self.column,
                  columnspan = self.columnspan, sticky = self.sticky)

    def generateEvent(self, event, *args, **kwargs):
        self.event_generate(event, *args, **kwargs)

    def getChildren(self):
        return self.winfo_children()

class TOCCanvasWithclick(tk.Canvas):
    class Label:
        def __init__(self, subsection, imIdx, canvas, 
                     startX, startY, endX, endY,
                     omPage, 
                     labelStartX = None, labelStartY = None):
            self.canvas:tk.Canvas = canvas
            self.subsection = subsection

            self.id = None
            self.handleId = None
            self.handleId2 = None
            self.tag = None

            self.eImIdx = None

            self.label = None
            self.line = None

            self.movingHandle2 = False

            if len(imIdx.split("_")) == 1:
                self.imIdx = imIdx
            else:
                self.imIdx = imIdx.split("_")[0]
                self.eImIdx = imIdx.split("_")[1]

            self.startX = startX

            if labelStartX == None:
                self.labelStartX = self.startX - 85 if labelStartX == None else labelStartX
            else:
                self.labelStartX = labelStartX

            self.startY = startY

            if labelStartY == None:
                self.labelStartY = self.startY if labelStartY == None else labelStartY
            else:
                self.labelStartY = labelStartY

            self.endX = endX
            self.endY = endY

            self.omPage = omPage

            self.draw()

        def __labelCmd(self, *args):
            mainMathManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                            wf.Wr.MenuManagers.MathMenuManager)
            mainMathManager.moveTocToEntry(self.subsection, self.imIdx)


        def draw(self):
            text = f"{self.subsection}:{self.imIdx}"

            if self.eImIdx != None:
                text += f"_{self.eImIdx}"

            self.label = tk.Button(self.canvas, 
                                   text = text, 
                                   command = self.__labelCmd, 
                                   anchor = tk.W)
            self.label.configure(width = 5, bg = "#3E4742", activebackground = "#33B5E5", relief = tk.FLAT)
            self.id = self.canvas.create_window(self.labelStartX, 
                                                self.labelStartY, 
                                                anchor = tk.NW, 
                                                window = self.label,
                                                tags = f"button:{self.subsection}:{self.imIdx}")
            self.handleId = self.canvas.create_rectangle(self.labelStartX, 
                                        self.labelStartY,
                                        self.labelStartX + 10,
                                        self.labelStartY + 40,
                                        fill = "green",
                                        tags = f"buttonRect:{self.subsection}:{self.imIdx}")
            self.handleId2 = self.canvas.create_rectangle(self.labelStartX + 70, 
                                        self.labelStartY,
                                        self.labelStartX + 80,
                                        self.labelStartY - 10,
                                        fill = "green",
                                        tags = f"buttonRect:{self.subsection}:{self.imIdx}")

            def __drawLine(self):
                self.line = self.canvas.create_rectangle(self.startX - 5, self.startY,
                                                    self.startX + 1, self.endY,
                                                    fill = "red")

            def __deleteLine(self):
                if self.line != None:
                    self.canvas.delete(self.line)
                    self.line = None              

            self.label.bind("<Enter>", lambda *args: __drawLine(self))
            self.label.bind("<Leave>", lambda *args: __deleteLine(self))

        def moveCenter(self, x, y, handle2 = False):
            width = 80
            height = 40

            if self.movingHandle2:
                handle2 = True

            if not handle2:
                self.labelStartX = x 
                self.labelStartY = y - height
            else:
                self.movingHandle2 = True
                self.labelStartX = x - width
                self.labelStartY = y 

            self.redraw()

        def redraw(self):
            self.deleteLabel()
            self.draw()

        def select(self):
            self.canvas.delete(self.handleId)
            self.canvas.delete(self.handleId2)
            if self.label != None:
                self.handleId = self.canvas.create_rectangle(self.labelStartX, 
                                        self.labelStartY,
                                        self.labelStartX + 10,
                                        self.labelStartY + 40,
                                        fill = "yellow",
                                        tags = f"buttonRect:{self.subsection}:{self.imIdx}")
                self.handleId2 = self.canvas.create_rectangle(self.labelStartX + 70, 
                                        self.labelStartY,
                                        self.labelStartX + 80,
                                        self.labelStartY - 10,
                                        fill = "yellow",
                                        tags = f"buttonRect:{self.subsection}:{self.imIdx}")

        def unselect(self):
            self.canvas.delete(self.handleId) 
            self.canvas.delete(self.handleId2) 
            if self.label != None:
                self.handleId = self.canvas.create_rectangle(self.labelStartX, 
                                        self.labelStartY,
                                        self.labelStartX + 10,
                                        self.labelStartY + 40,
                                        fill = "green",
                                        tags = f"buttonRect:{self.subsection}:{self.imIdx}")
                self.handleId2 = self.canvas.create_rectangle(self.labelStartX + 70,
                                            self.labelStartY,
                                            self.labelStartX + 80,
                                            self.labelStartY - 10,
                                            fill = "green",
                                            tags = f"buttonRect:{self.subsection}:{self.imIdx}")

        def deleteLabel(self):
            if self.id != None:
                self.canvas.delete(self.id)
                self.canvas.labels = [i for i in self.canvas.labels if i.id != self.id]
                self.label.grid_forget()
                self.id = None
            if self.handleId != None:
                self.canvas.delete(self.handleId)
                self.canvas.delete(self.handleId2)
                self.handleId = None
                self.handleId2 = None


        def toDict(self):
            return {
                        "page" : self.omPage,
                        "coords" : [self.startX, self.startY,
                                    self.endX, self.endY],
                        "labelCoords" : [self.labelStartX, self.labelStartY]
                    }

    class Rectangle:
        alpha = 0.3

        cornerWidgetsColor = "black"
        cornerWidgetsOutline = "blue"

        def __init__(self, startX, startY, endX, endY, canvas, color = None) -> None:
            self.startX = startX
            self.startY = startY
            self.endX = endX
            self.endY = endY

            self.id = None
            self.tag = None
            self.color = "yellow"

            if color != None:
                self.color = color
            
            self.cornerWidgetsIds = [None, None, None, None]
            self.imageContainer = None

            self.canvas:tk.Canvas = canvas
            
            self.draw()
            
            self.tag = f"rectangle_{self.id}"

        @classmethod
        def rectangleFromDict(cls, attrDict:dict, canvas):
            rect = cls(attrDict["startX"],
                       attrDict["startY"],
                       attrDict["endX"],
                       attrDict["endY"],
                       canvas,
                       attrDict["color"]
                       )

            for k,v in attrDict.items():
                setattr(rect, k, v)

            return rect

        def toDict(self):
            propList = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
            propToFilterOut = ["id", "canvas", "imageContainer", "cornerWidgetsColor", "cornerWidgetsIds", "cornerWidgetsOutline"]
            propList = [i for i in propList if i not in propToFilterOut]
            propDict = {"type": "rectangle"}

            for k in propList:
                propDict[k] = getattr(self, k)

            return propDict

        def showCornerWidgets(self):
            self.deleteCornerWidgets()
            radius = 5

            self.cornerWidgetsIds[0] = self.canvas.create_oval(self.startX - radius, 
                                                            self.startY - radius,
                                                            self.startX + radius, 
                                                            self.startY + radius,
                                                            fill = self.cornerWidgetsColor, 
                                                            outline = self.cornerWidgetsOutline,
                                                            tags = "cornerWidget")
            self.cornerWidgetsIds[1] = self.canvas.create_oval(self.endX - radius, 
                                                            self.startY - radius,
                                                            self.endX + radius, 
                                                            self.startY + radius, 
                                                            fill = self.cornerWidgetsColor, 
                                                            outline = self.cornerWidgetsOutline,
                                                            tags = "cornerWidget")
            self.cornerWidgetsIds[2] = self.canvas.create_oval(self.startX - radius, 
                                                            self.endY - radius,
                                                            self.startX + radius, 
                                                            self.endY + radius, 
                                                            fill = self.cornerWidgetsColor, 
                                                            outline = self.cornerWidgetsOutline,
                                                            tags = "cornerWidget")
            self.cornerWidgetsIds[3] = self.canvas.create_oval(self.endX - radius, 
                                                            self.endY - radius,
                                                            self.endX + radius, 
                                                            self.endY + radius, 
                                                            fill = self.cornerWidgetsColor, 
                                                            outline = self.cornerWidgetsOutline,
                                                            tags = "cornerWidget")

        def moveCorner(self, x, y, cornerIdx):
            if cornerIdx == 0:
                self.startX = x
                self.startY = y
            elif cornerIdx == 1:
                self.endX = x
                self.startY = y
            elif cornerIdx == 2:
                self.startX = x
                self.endY = y
            elif cornerIdx == 3:
                self.endX = x
                self.endY = y

            self.redraw()
            self.showCornerWidgets()

        def moveCenter(self, x, y):
            width = abs(self.startX - self.endX)
            height = abs(self.startY - self.endY)

            leftHalfWidth = int(width / 2)
            rightHalfWidth = width - leftHalfWidth
            topHalfHight = int(height / 2)
            bottomHalfHight = height - topHalfHight

            self.startX = x - leftHalfWidth
            self.endX = x + rightHalfWidth
            self.startY = y - topHalfHight
            self.endY = y + bottomHalfHight

            self.redraw()
            self.showCornerWidgets()

        def redraw(self):
            self.deleteRectangle()
            self.draw()
        
        def draw(self):
            alpha = int(self.alpha * 255)

            if self.color == "white":
                fill = (255,255,255)
            else:
                fill = (232,255,25) + (alpha,)

            x1, y1, x2, y2 = self.startX, self.startY, self.endX, self.endY
            image = Image.new('RGBA', (abs(int(x2-x1)), abs(int(y2-y1))), fill)
            self.imageContainer = ImageTk.PhotoImage(image)

            if not self.canvas.selectingZone:
                self.id =  self.canvas.create_image(x1, y1, image = self.imageContainer, anchor='nw', 
                                                                                tag = self.tag)
            else:
                self.id =  self.canvas.create_polygon([x1, y1, x2, y1, x2, y2, x1, y2], 
                                                    fill = '',
                                                    outline = "black",
                                                    tags = self.tag)

        def deleteCornerWidgets(self):      
            for w in self.cornerWidgetsIds:
                if w != None:
                    self.canvas.delete(w)
            
            self.cornerWidgetsIds = [None, None, None, None]

        def deleteRectangle(self):
            if self.id != None:
                self.deleteCornerWidgets()
                self.canvas.delete(self.id)

                if self.canvas.drawing:
                    self.canvas.rectangles = [i for i in self.canvas.rectangles if i != None]
                    self.canvas.rectangles = [i for i in self.canvas.rectangles if i.id != self.id]

    def release(self, event):
        if self.movingFigure != None:
            if type(self.movingFigure) == TOCCanvasWithclick.Label:
                self.labels.append(self.movingFigure)
                self.movingFigure.movingHandle2 = False

        self.movingFigure = None
        self.resizingFigure = None

        self.bind_all("<Mod1-s>", lambda *args: self.saveFigures(stampChanges = True))
        self.bind_all("<Delete>", self.deleteSelectedRectangle)

        if self.selectingZone \
            and self.lastRecrangle != None:
            x = self.lastRecrangle.startX
            y =  self.lastRecrangle.startY
            x1 = self.lastRecrangle.endX
            y1 = self.lastRecrangle.endY
            self.lastRecrangle.deleteRectangle()

            im = self.pilImage
            im = im.crop([x - 1, y - 1, x1 + 1, y1 + 1])

            if self.getTextOfSelector:
                text = _u.getTextFromImage(None, im)

                r = tk.Tk()
                r.withdraw()
                r.clipboard_clear()
                r.clipboard_append(text)
                r.update()
                r.destroy()
                self.selectingZone = False
                self.getTextOfSelector = False
                self.lastRecrangle = None
                self.startCoord = []
                return

            currBookpath = sf.Wr.Manager.Book.getCurrBookFolderPath()

            imPath = ""

            if (self.eImIdx == None) or (self.eImIdx == _u.Token.NotDef.int_t):
                imPath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBookpath, 
                                                                            self.subsection, 
                                                                            self.imIdx)
            else:
                imPath = _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(currBookpath, 
                                                                             self.subsection,
                                                                             self.imIdx,
                                                                             self.eImIdx)

            if (self.eImIdx == None) or (self.eImIdx == _u.Token.NotDef.int_t):
                OMName = fsf.Data.Book.currOrigMatName
                fsf.Wr.OriginalMaterialStructure.setMaterialCurrPage(OMName, self.omPage)
                imLinkOMPageDict = fsf.Data.Sec.imLinkOMPageDict(self.subsection)
                imLinkOMPageDict[self.imIdx] = self.omPage
                fsf.Data.Sec.imLinkOMPageDict(self.subsection, imLinkOMPageDict)

                self.labels.append(TOCCanvasWithclick.Label(self.subsection,
                                                            self.imIdx,
                                                            self,
                                                            x, y, x1, y1,
                                                            self.omPage,
                                                            x - 85, y))
            else:
                self.labels.append(TOCCanvasWithclick.Label(self.subsection,
                                                            f"{self.imIdx}_{self.eImIdx}",
                                                            self,
                                                            x, y, x1, y1,
                                                            self.omPage,
                                                            x - 85, y))

            im.save(imPath)

            self.selectingZone = False
            self.getTextOfSelector = False
            self.lastRecrangle = None
            self.startCoord = []
            return

        else:
            if self.drawing:
                self.rectangles.append(self.lastRecrangle)
                self.drawing = False

            self.saveFigures()

            self.lastRecrangle = None
            self.startCoord = []

    def clickOnFigure(self, event):
        if self.drawing:
            return

        x1 = event.x
        y1 = event.y

        overlapIds = self.find_overlapping(x1, y1, x1, y1)
        if len(overlapIds) != 0:
            overlapId = overlapIds[-1]

            for l in self.labels:
                if (overlapId == l.handleId) or (overlapId == l.handleId2):
                    l.select()
                else:
                    l.unselect()

            for r in self.rectangles:
                if r != None:
                    for i in range(len(r.cornerWidgetsIds)):
                        if r.cornerWidgetsIds[i] == overlapId:
                            self.draw(event)
                            return

                    if (overlapId == r.id):
                        if (r.cornerWidgetsIds == [None, None, None, None]):
                            self.selectedRectangle = r
                            r.showCornerWidgets()
                    else:
                        r.deleteCornerWidgets()

    def draw(self, event):
        x1 = event.x
        y1 = event.y

        if self.resizingFigure != None:
            self.resizingFigure[0].moveCorner(x1, y1,
                                              self.resizingFigure[1])
            return

        if self.movingFigure != None:
            self.movingFigure.moveCenter(x1, y1)
            return

        if not self.drawing:
            overlapIds = self.find_overlapping(x1, y1, x1, y1)

            if len(overlapIds) != 0:
                overlapId = overlapIds[-1]

                for l in self.labels:
                    if (overlapId == l.handleId) or (overlapId == l.handleId2):
                        self.movingFigure = l

                        if overlapId == l.handleId:
                            l.moveCenter(x1, y1)
                        else:
                            l.moveCenter(x1, y1, True)
                        return

                for r in self.rectangles:
                    if r != None:
                        for i in range(len(r.cornerWidgetsIds)):
                            if r.cornerWidgetsIds[i] == overlapId:
                                self.resizingFigure = [r, i]
                                r.moveCorner(x1, y1, i)
                                return

                        if overlapId == r.id:
                            self.movingFigure = r
                            r.moveCenter(x1, y1)
                            return

        self.drawing = True

        if self.startCoord == []:
            self.startCoord = [x1, y1]

        startx = min(self.startCoord[0], x1)
        starty = min(self.startCoord[1], y1)
        endx = max(self.startCoord[0], x1)
        endy = max(self.startCoord[1], y1)

        cws = self.find_withtag("cornerWidget")
        for cw in cws:
            self.delete(cw)

        if self.lastRecrangle != None:
            self.lastRecrangle.deleteRectangle()

        if int(event.state) == 257:
            self.lastRecrangle = TOCCanvasWithclick.Rectangle(startx, starty, endx, endy, 
                                                            self, "white")
        else:
            self.lastRecrangle = TOCCanvasWithclick.Rectangle(startx, starty, endx, endy, 
                                                            self)

    def readFigures(self, *args):
        figuresList = []

        omBookName = fsf.Data.Book.currOrigMatName
        zoomLevel = int(fsf.Wr.OriginalMaterialStructure.getMaterialZoomLevel(omBookName))
        pageSize = fsf.Wr.OriginalMaterialStructure.getMaterialPageSize(omBookName)
        pageSize = [int(i) for i in pageSize]
        pageSizeZoomAffected = [zoomLevel, int((zoomLevel / pageSize[0]) * pageSize[1])]
        widthScale = pageSizeZoomAffected[0] / pageSize[0]
        heightScale = pageSizeZoomAffected[1] / pageSize[1]

        if not self.isPdfPage:
            figuresData = fsf.Data.Sec.figuresData(self.subsection)

            if (self.eImIdx == None) or (str(self.eImIdx) == _u.Token.NotDef.str_t):
                if figuresData.get(self.imIdx) != None:
                    figuresList = copy.deepcopy(figuresData[str(self.imIdx)])
            else:
                if figuresData.get(f"{self.imIdx}_{self.eImIdx}") != None:
                    figuresList = copy.deepcopy(figuresData[f"{self.imIdx}_{self.eImIdx}"])
                else:
                    return
        else:
            figuresList = \
                fsf.Wr.OriginalMaterialStructure.getMaterialPageFigures(omBookName, self.omPage)

            if type(figuresList) != str:
                figuresList.copy()

            # NOTE: inafficient and need to be optimised
            subsections = [i for i in fsf.Wr.BookInfoStructure.getSubsectionsList() if "." in i]

            for i in range(len(subsections) - 1, -1, -1):
                subsection = subsections[i]
                subsectionStartPage = int(fsf.Data.Sec.start(subsection))

                if subsectionStartPage > int(self.omPage) + 10:
                    continue

                figuresLabelsData = fsf.Data.Sec.figuresLabelsData(subsection).copy()

                for k, l in figuresLabelsData.items():
                    if type(l) == dict:
                        if l["page"] == self.omPage:
                            labelToAdd = TOCCanvasWithclick.Label(subsection,
                                                                k,
                                                                self,
                                                                l["coords"][0] * widthScale,
                                                                l["coords"][1] * heightScale,
                                                                l["coords"][2] * widthScale,
                                                                l["coords"][3] * heightScale,
                                                                self.omPage,
                                                                l["labelCoords"][0] * widthScale,
                                                                l["labelCoords"][1] * heightScale)
                            self.labels.append(labelToAdd)

        self.rectangles = []

        for f in figuresList:
            if f.get("type") != None:
                f.pop("type")

            if self.isPdfPage:
                f["endX"] = f["endX"] * widthScale
                f["endY"] = f["endY"] * heightScale
                f["startX"] = f["startX"] * widthScale
                f["startY"] = f["startY"] * heightScale
            elif (self.resizeFactor != 1.0):
                f["endX"] = float(f["endX"]) *  (1.0 / self.resizeFactor)
                f["endY"] = float(f["endY"]) *  (1.0 / self.resizeFactor)
                f["startX"] = float(f["startX"]) *  (1.0 / self.resizeFactor)
                f["startY"] = float(f["startY"]) *  (1.0 / self.resizeFactor)

            rect = TOCCanvasWithclick.Rectangle.rectangleFromDict(f, self)
            self.rectangles.append(rect)

    def saveFigures(self, stampChanges = False, *args):
        figuresList = []

        omBookName = fsf.Data.Book.currOrigMatName
        zoomLevel = int(fsf.Wr.OriginalMaterialStructure.getMaterialZoomLevel(omBookName))
        pageSize = fsf.Wr.OriginalMaterialStructure.getMaterialPageSize(omBookName)
        pageSize = [int(i) for i in pageSize]
        pageSizeZoomAffected = [zoomLevel, int((zoomLevel / pageSize[0]) * pageSize[1])]
        widthScale = pageSize[0] / pageSizeZoomAffected[0]
        heightScale = pageSize[1] / pageSizeZoomAffected[1]

        for i in range(len(self.rectangles)):
            if self.rectangles[i] != None:
                f= self.rectangles[i].toDict()

                if self.isPdfPage:
                    f["endX"] = f["endX"] * widthScale
                    f["endY"] = f["endY"] * heightScale
                    f["startX"] = f["startX"] * widthScale
                    f["startY"] = f["startY"] * heightScale
                elif self.resizeFactor != 1.0:
                    f["endX"] = float(f["endX"]) *  self.resizeFactor
                    f["endY"] = float(f["endY"]) *  self.resizeFactor
                    f["startX"] = float(f["startX"]) *  self.resizeFactor
                    f["startY"] = float(f["startY"]) *  self.resizeFactor

                figuresList.append(f)
            else:
                self.rectangles.pop(i)

        if not self.isPdfPage:
            figuresData = fsf.Data.Sec.figuresData(self.subsection)

            if (self.eImIdx == None) or (self.eImIdx == _u.Token.NotDef.int_t):
                figuresData[self.imIdx] = figuresList
            else:
                figuresData[f"{self.imIdx}_{self.eImIdx}"] = figuresList

            fsf.Data.Sec.figuresData(self.subsection, figuresData)
            
            mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.scrollToLatestClickedWidget()
        else:
            omBookName = fsf.Data.Book.currOrigMatName
            fsf.Wr.OriginalMaterialStructure.setMaterialPageFigures(omBookName, self.omPage, figuresList)

            for l in self.labels:
                f = l.toDict()

                coords = []
                coords.append(f["coords"][0] * widthScale)
                coords.append(f["coords"][1] * heightScale)
                coords.append(f["coords"][2] * widthScale)
                coords.append(f["coords"][3] * heightScale)
                f["coords"] = coords

                labelCoords = []
                labelCoords.append(f["labelCoords"][0] * widthScale)
                labelCoords.append(f["labelCoords"][1] * heightScale)
                f["labelCoords"] = labelCoords

                figuresLabelsData = fsf.Data.Sec.figuresLabelsData(l.subsection)

                if l.eImIdx == None:
                    figuresLabelsData[l.imIdx] = f
                else:
                    figuresLabelsData[f"{l.imIdx}_{l.eImIdx}"] = f

                fsf.Data.Sec.figuresLabelsData(l.subsection, figuresLabelsData)

        if stampChanges:
            msg = "\
        After saving the figures'."
            _u.log.autolog(msg)
            ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

    def deleteSelectedRectangle(self, *args):
        if self.selectedRectangle != None:
            for i in range(len(self.rectangles)):
                if self.rectangles[i].id == self.selectedRectangle.id:
                    r = self.rectangles.pop(i)
                    r.deleteRectangle()
                    self.selectedRectangle = None

                    self.saveFigures()

                    mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                wf.Wr.MenuManagers.MathMenuManager)
                    mainManager.scrollToLatestClickedWidget()
                    break

    def __init__(self, root, prefix, row, column, imIdx, subsection, 
                 columnspan = 1, sticky = tk.NW, 
                 image = None, extraImIdx = None,
                 makeDrawable = True, 
                 isPdfPage = False, page = None, pilIm = None,
                 resizeFactor = 1.0,
                 imagePath = "",
                 *args, **kwargs) -> None:
        self.root = root

        self.row = row
        self.column = column
        self.columnspan = columnspan
        self.sticky = sticky
        self.image = image
        self.pilImage = pilIm
        self.imIdx = imIdx
        self.subsection = subsection
        self.eImIdx = extraImIdx
        self.isPdfPage = isPdfPage
        self.omPage = page
        self.imagePath  = _u.Token.NotDef.str_t
        self.etrWidget = _u.Token.NotDef.no_t
        
        self.imagePath = imagePath
        self.makeDrawable = makeDrawable

        self.imageResize = None
        self.startCoord = []

        self.rectangles = []
        self.labels = []
        self.drawing = False
        self.lastRecrangle = None
        
        self.selectedRectangle = None

        self.selectingZone = False
        self.getTextOfSelector = False

        self.movingFigure = None
        self.resizingFigure = None

        self.__btnClickFuncId = None

        self.resizeFactor = resizeFactor

        self.width = self.image.width()
        self.height = self.image.height()

        super().__init__(root, name = prefix, 
                         width = self.width, height = self.height)
        self.backgroundImage = self.create_image(0, 0,
                                                image = self.image, 
                                                anchor='nw', 
                                                tag = prefix)

        self.readFigures()

        if makeDrawable:
            if not self.isPdfPage:
                self.bindCmd()
            else:
                self.bind("<Enter>", self.bindCmd)
                self.bind("<Leave>", self.unbindCmd)

    def refreshImage(self, addBrownBorder = True):
        pilIm = Image.open(self.imagePath)

        newWidth = self.image.width()
        newHeight = self.image.height()
        
        pilIm = pilIm.resize([int(newWidth), int(newHeight)], Image.LANCZOS)

        if addBrownBorder:
            pilIm = ImageOps.expand(pilIm, border = 2, fill = "brown")

        img = ImageTk.PhotoImage(pilIm)

        self.image = img
        self.itemconfigure(self.backgroundImage, image = img)

        self.readFigures()

        if self.makeDrawable:
            if not self.isPdfPage:
                self.bindCmd()
            else:
                self.bind("<Enter>", self.bindCmd)
                self.bind("<Leave>", self.unbindCmd)

    def getEntryWidget(self, subsection, imIdx , eImIdx = None):
        for l in self.labels:
            if (l.subsection == subsection) and (l.imIdx == imIdx):
                if eImIdx == None:
                    return l
                else:
                    if str(l.eImIdx) == str(eImIdx):
                        return l

        return None


    def bindCmd(self, *args):
        self.bind("<Shift-B1-Motion>", self.draw)
        self.bind("<B1-Motion>", self.draw)
        self.__btnClickFuncId = self.bind("<Button-1>", self.clickOnFigure)
        self.bind("<ButtonRelease-1>", self.release)

    def unbindCmd(self, *args):
        self.unbind("<Shift-B1-Motion>")
        self.unbind("<B1-Motion>")
        try:
            self.unbind("<Button-1>", self.__btnClickFuncId)
        except:
            pass
        self.unbind("<ButtonRelease-1>")

        self.unbind("<Mod1-s>")
        self.unbind("<Delete>")

    def render(self):
        self.grid(row = self.row, column = self.column,
                  columnspan = self.columnspan, sticky = self.sticky)

    def generateEvent(self, event, *args, **kwargs):
        self.event_generate(event, *args, **kwargs)

    def getChildren(self):
        return self.winfo_children()

    def rebind(self, keys, cmds):
        for i in range(len(keys)):
            key = keys[i]
            cmd = cmds[i]

            if key == ww.TkWidgets.Data.BindID.allKeys:
                self.bind_all(key, lambda event: cmd(event))
            else:
                self.bind(key, cmd)

class TOCLabelWithClick(ttk.Label):
    '''
    this is used to run different commands on whether the label was clicked even or odd times
    '''

    def rebind(self, keys, cmds):
        for i in range(len(keys)):
            key = keys[i]
            cmd = cmds[i]

            if key == ww.TkWidgets.Data.BindID.allKeys:
                self.bind_all(key, lambda event: cmd(event))
            else:
                self.bind(key, cmd)
    
    def __init__(self, root, prefix, row, column, columnspan = 1, sticky = tk.NW, *args, **kwargs) -> None:
        self.root = root
        self.clicked = False
        self.imIdx = ""
        self.eImIdx = ""
        self.subsection = ""
        self.imagePath = ""
        self.group = ""
        self.image = None
        self.alwaysShow = None
        self.shouldShowExMenu = False
        self.shouldShowProofMenu = False
        self.shouldShowNotesMenu = False
        self.lineImIdx = _u.Token.NotDef.str_t
        self.solImIdx = _u.Token.NotDef.str_t
        self.etrWidget = _u.Token.NotDef.str_t
        self.sticky = None
        self.tocFrame = None
        self.eImIdx = None
        self.targetSubssection = None
        self.targetImIdx = None
        self.sourceSubssection = None
        self.sourceImIdx= None
        self.sourceWebLinkName = None
        self.dictWord = None
        self.dictText = None

        self.imageLineIdx = None
        self.entryText = None

        self.imagePath = None

        self.row = row
        self.column = column
        self.columnspan = columnspan
        self.sticky = sticky

        super().__init__(root, name = prefix, *args, **kwargs)

    def render(self):
        self.grid(row = self.row, column = self.column,
                  columnspan = self.columnspan, sticky = self.sticky)

    def generateEvent(self, event, *args, **kwargs):
        self.event_generate(event, *args, **kwargs)

    def getChildren(self):
        return self.winfo_children()
    
    def updateImage(self):
        pilIm = comw.getEntryImg("no", self.subsection, self.imIdx)

        shrink = 0.7
        pilIm.thumbnail([int(pilIm.size[0] * shrink),int(pilIm.size[1] * shrink)], Image.LANCZOS)
        self.image = ImageTk.PhotoImage(pilIm)
        super().configure(image = self.image)
    
    def updateGroupImage(self):
        img = comw.getGroupImg(self.subsection, self.group)

        self.image = img
        super().configure(image = self.image)
    
    def updateSubsectionImage(self):
        if self.subsection in list(fsf.Data.Book.sections.keys()):
            topSectionImgPath = _upan.Paths.Screenshot.Images.getTopSectionEntryImageAbs(
                                                            sf.Wr.Manager.Book.getCurrBookName(),
                                                            self.subsection)

            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(topSectionImgPath):
                result = Image.open(topSectionImgPath)
            else:
                result = fsf.Wr.SectionInfoStructure.rebuildTopSectionLatex(self.subsection,
                                                                            _upan.Names.Subsection.getTopSectionPretty)

            shrink = 0.8
            result.thumbnail([int(result.size[0] * shrink),int(result.size[1] * shrink)], Image.LANCZOS)
            result = ImageTk.PhotoImage(result)

            self.image = result
            super().configure(image = self.image)
        else:
            subsectionImgPath = _upan.Paths.Screenshot.Images.getSubsectionEntryImageAbs(
                                                            sf.Wr.Manager.Book.getCurrBookName(), 
                                                            self.subsection)

            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(subsectionImgPath):
                result = Image.open(subsectionImgPath)
            else:
                result = \
                    fsf.Wr.SectionInfoStructure.rebuildSubsectionImOnlyLatex(self.subsection, 
                                                                            _upan.Names.Subsection.getSubsectionPretty)

            shrink = 0.8
            result.thumbnail([int(result.size[0] * shrink),int(result.size[1] * shrink)], Image.LANCZOS)
            result = ImageTk.PhotoImage(result)

            self.image = result
            super().configure(image = self.image)

def bindChangeColorOnInAndOut(widget:TOCLabelWithClick, shouldBeRed = False, shouldBeBrown = False):
    def __changeTextColorBlue(event = None, *args):
        event.widget.configure(foreground="blue")

    def __changeTextColorBrown(event = None, *args):
        event.widget.configure(foreground="brown")

    def __changeTextColorRed(event = None, *args):
        event.widget.configure(foreground="red")

    def __changeTextColorWhite(event = None, *args):
        event.widget.configure(foreground="white")
    
    widget.rebind([ww.currUIImpl.Data.BindID.enterWidget], [__changeTextColorBlue])
    if not shouldBeRed:
        widget.rebind([ww.currUIImpl.Data.BindID.leaveWidget], [__changeTextColorWhite])
    else:
        widget.rebind([ww.currUIImpl.Data.BindID.leaveWidget], [__changeTextColorRed])
    
    if shouldBeBrown:
        widget.rebind([ww.currUIImpl.Data.BindID.leaveWidget], [__changeTextColorBrown])


def getImageWidget(root, imagePath, widgetName, imIdx, subsection,
                   imPad = 0, imageSize = [450, 1000], 
                   row = 0, column = 0, columnspan = 1,
                   resizeFactor = 1.0,
                   bindOpenWindow = True,
                   extraImIdx = _u.Token.NotDef.int_t,
                   tocBox = None):
    if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
        pilIm = Image.open(imagePath)

        # NOTE: this is how it was done originally. 
        #       No idea why. Whis way added figures are messed up at resize
        # if resizeFactor <= 1.0:
        #     pilIm.thumbnail([i * resizeFactor for i in imageSize], Image.LANCZOS)
        # else:
        origWidth, origHeight = pilIm.size
        newWidth = min(imageSize[0] * resizeFactor, origWidth * resizeFactor)
        changeFactor = (imageSize[0] / origWidth) * resizeFactor
        newHeight = min(changeFactor * origHeight, origHeight * resizeFactor)
        
        pilIm = pilIm.resize([int(newWidth), int(newHeight)], Image.LANCZOS)

        noteImIdx = str(int(extraImIdx) + 1) if extraImIdx != _u.Token.NotDef.int_t else 0
        notes:dict = fsf.Wr.EntryInfoStructure.readProperty(subsection,
                                                       imIdx, 
                                                       fsf.Wr.EntryInfoStructure.PubProp.entryNotesList)
        if notes.get(str(noteImIdx)) != None:
            pilIm = ImageOps.expand(pilIm, border = 2, fill="brown")

        img = ImageTk.PhotoImage(pilIm)

        if bindOpenWindow:
            imLabel = TOCCanvasWithclick(root, imIdx = imIdx, subsection = subsection,
                                        prefix = widgetName, image = img, padding = [imPad, 0, 0, 0],
                                        row = row, column = column, columnspan = columnspan,
                                        extraImIdx = extraImIdx, makeDrawable = False, 
                                        resizeFactor = 1 / resizeFactor,
                                        imagePath = imagePath)
        else:
            imLabel = TOCCanvasWithclick(root, imIdx = imIdx, subsection = subsection,
                                        prefix = widgetName, image = img, padding = [imPad, 0, 0, 0],
                                        row = row, column = column, columnspan = columnspan,
                                        extraImIdx = extraImIdx,
                                        resizeFactor = 1 / resizeFactor,
                                        imagePath = imagePath)
    else:
        img = None
        imLabel = TOCLabelWithClick(root, prefix = widgetName, text = "-1", padding = [imPad, 0, 0, 0],
                                    row = row, column = column, columnspan = columnspan)
        imLabel.eImIdx = extraImIdx

    imLabel.imagePath = imagePath
    imLabel.etrWidget = imLabel

    def __openImageManager(event, *args):
        imMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.ImagesManager)
        imMenuManger.subsection = event.widget.subsection
        imMenuManger.imIdx = event.widget.imIdx

        width = int(event.widget.width * 1.5) if int(event.widget.width * 1.5) > 720 else 720
        currBookpath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        eImIdx = event.widget.eImIdx
        notePosidx = str(int(eImIdx) + 1) if eImIdx != _u.Token.NotDef.str_t else 0
        notesIm = _upan.Paths.Entry.NoteImage.getAbs(currBookpath,
                                           event.widget.subsection,
                                           event.widget.imIdx,
                                           notePosidx)
        
        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(notesIm):
            im = Image.open(notesIm)
            _, imHeight = im.size
        else:
            imHeight = 30

        height = int(event.widget.height * 1.5) + imHeight + 100

        imMenuManger.show([width, height, 0, 0], eImIdx, imHeight)

        if tocBox != None:
            tocBox.widgetToScrollTo = event.widget

    if bindOpenWindow:
        imLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [__openImageManager])

    return img, imLabel


def addMainEntryImageWidget(rootLabel,
                            subsection, imIdx,
                            imPadLeft, 
                            displayedImagesContainer,
                            imageBaloon,
                            mainImgBindData = None,
                            resizeFactor = 1.0,
                            row = 4,
                            columnspan = 100,
                            column = 0,
                            bindOpenWindow = True,
                            tocBox = None):
    # mainImage
    currBookName = sf.Wr.Manager.Book.getCurrBookName()
    imagePath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBookName,
                                                                   subsection,
                                                                   imIdx)

    mainWidgetName = _upan.Names.UI.getMainEntryWidgetName(subsection, imIdx)

    tempLabel = TOCLabelWithClick(rootLabel, prefix = "temp_" + mainWidgetName,
                                  padding = [0, 0, 0, 0],
                                  row = row, column = column, columnspan = columnspan)
    emptyLabel = TOCLabelWithClick(tempLabel, prefix = "empty_" + mainWidgetName,
                                  padding = [imPadLeft, 0, 0, 0],
                                  row = 0, column = 0, columnspan = 1)
    emptyLabel.render()
    tempLabel.imagePath = imagePath
    tempLabel.imIdx = imIdx
    tempLabel.subsection = subsection
    tempLabel.etrWidget = tempLabel

    if mainImgBindData != None:
        tempLabel.rebind(*mainImgBindData)
    
    textOnly = fsf.Data.Sec.textOnly(subsection)[imIdx]

    if not textOnly:
        img, imLabel = getImageWidget(tempLabel, imagePath, mainWidgetName, 
                                    imIdx, subsection, imPad = 0,
                                    row = 0, column = 1, columnspan = 1,
                                    resizeFactor = resizeFactor, bindOpenWindow = bindOpenWindow,
                                    tocBox = tocBox)
        imLabel.render()

        displayedImagesContainer.append(img)

        imLinkDict = fsf.Data.Sec.imLinkDict(subsection)

        if type(imLinkDict) == dict:
            if str(imIdx) in list(imLinkDict.keys()):
                imText = imLinkDict[str(imIdx)]
            else:
                imText = _u.Token.NotDef.str_t
        else:
            imText = _u.Token.NotDef.str_t
        imageBaloon.bind(imLabel, "{0}".format(imText))
    else:
        text = fsf.Data.Sec.imageText(subsection)[imIdx]
        imLabel = TOCTextWithClick(tempLabel, 
                                    mainWidgetName,
                                    row = 0, column = 1, columnspan = 1,
                                    text = text,
                                    padx = 10,
                                    pady = 10
                                    )
        imLabel.subsection = subsection
        imLabel.imIdx = imIdx
        imLabel.render()

    openOMOnThePageOfTheImage(imLabel, subsection, imIdx)
    return tempLabel


def addExtraIm(subsection, mainImIdx, isProof, tocFrame, widgetToScrollTo = None):     
    def ___addExtraIm(subsection, mainImIdx, 
                        extraImageIdx, extraImText):
        gm.GeneralManger.AddExtraImageForEntry(mainImIdx, subsection, extraImageIdx, extraImText)

        def __afterEImagecreated(mainImIdx, subsection, extraImageIdx, extraImText):
            
            extraImagesDict = fsf.Data.Sec.extraImagesDict(subsection)
            extraImagesList = []

            if extraImagesDict == _u.Token.NotDef.dict_t:
                extraImagesDict = {}

            if mainImIdx in list(extraImagesDict.keys()):
                extraImagesList = extraImagesDict[mainImIdx]

            if extraImageIdx == _u.Token.NotDef.str_t:
                extraImageIdx = len(extraImagesList) - 1

            currBokkPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            extraImagePath_curr = _upan.Paths.Screenshot.getAbs(currBokkPath, subsection)

            extraImageName = _upan.Names.getExtraImageFilename(mainImIdx, subsection, extraImageIdx)
            extraImagePathFull = os.path.join(extraImagePath_curr, extraImageName + ".png")
            timer = 0

            while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(extraImagePathFull):
                time.sleep(0.3)
                timer += 1

                if timer > 50:
                    _u.log.autolog(f"\
    The correct extra image was not created for \n\
    '{subsection}':'{mainImIdx}' with id '{extraImageIdx}' and text '{extraImText}'")
                    return False
            
            tocFrame.renderWithScrollAfter()

            if widgetToScrollTo != None:
                # NOTE: this is a hack and we shouold implement correct scrolling to the newly created
                # image later
                tocFrame.scrollIntoView(None, widgetToScrollTo)

        t = Thread(target = __afterEImagecreated, 
                args = [mainImIdx, subsection, extraImageIdx, extraImText])
        t.start()

    extraImIdx = _u.Token.NotDef.str_t
    extraImagesDict = fsf.Data.Sec.extraImagesDict(subsection)

    if not isProof:
        if mainImIdx in list(extraImagesDict.keys()):
            extraImText = "con" + str(len(extraImagesDict[mainImIdx]))
        else:
            extraImText = "con0"
    else:
        extraImText = "proof"

    ___addExtraIm(subsection, mainImIdx, extraImIdx, extraImText)

def openOMOnThePageOfTheImage(widget:TOCLabelWithClick, targetSubsection, targetImIdx, eImidx = None):
    def __cmd(event = None, *args): 
        pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.PdfReadersManager)
        
        pdfReadersManager.moveToEntry(targetSubsection, targetImIdx, eImidx)

    widget.rebind([ww.currUIImpl.Data.BindID.cmdMouse1], [__cmd])

def addExtraEntryImagesWidgets(rootLabel, 
                               subsection, imIdx,
                               imPadLeft, 
                               displayedImagesContainer,
                               imageBaloon, 
                               skippConditionFn = lambda *args: False,
                               tocFrame = None,
                               row = None,
                               column = 0,
                               columnspan = 1000,
                               createExtraWidgets = True,
                               bindOpenWindow = True,
                               resizeFactor = None):
    import UI.widgets_collection.common as comw
    outLabels = []

    uiResizeEntryIdx = fsf.Data.Sec.imageUIResize(subsection)

    # extraImages
    if imIdx in list(fsf.Data.Sec.extraImagesDict(subsection).keys()):
        currBookName = sf.Wr.Manager.Book.getCurrBookName()
        extraImages = fsf.Data.Sec.extraImagesDict(subsection)[imIdx]

        eImWidgetsList = []

        for i in range(0, len(extraImages)):
            if skippConditionFn(subsection, imIdx, i):
                continue

            shouldResetResizeFactor = False

            if resizeFactor == None:
                shouldResetResizeFactor = True

                if (imIdx + "_" + str(i)) in list(uiResizeEntryIdx.keys()):
                    resizeFactor = float(uiResizeEntryIdx[imIdx + "_" + str(i)])
                else:
                    resizeFactor = 1.0

            eImText = extraImages[i]

            extraImFilepath = _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(currBookName,
                                                                                  subsection,
                                                                                  imIdx,
                                                                                  i)

            eImWidgetName = _upan.Names.UI.getExtraEntryWidgetName(subsection,
                                                                   imIdx,
                                                                   i)

            def extraImtextUpdate(event, *args):
                eImTextDict = fsf.Data.Sec.extraImagesDict(event.widget.subsection)
                eImTextList = eImTextDict[event.widget.imIdx]
                text = eImTextList[event.widget.eImIdx]

                eimLabel = MultilineText_ETR(event.widget.root, 
                                                eImWidgetName, 
                                                row = event.widget.row,
                                                column = event.widget.column,
                                                imLineIdx = None, 
                                                text = text)
                eimLabel.subsection = event.widget.subsection
                eimLabel.imIdx = event.widget.imIdx
                eimLabel.eImIdx = event.widget.eImIdx
                event.widget.grid_forget()

                def __getBack(eimLabel, widget):
                    newText = eimLabel.getData()
                    eImTextDict = fsf.Data.Sec.extraImagesDict(eimLabel.subsection)
                    eImTextList = eImTextDict[eimLabel.imIdx]
                    eImTextList[eimLabel.eImIdx] = newText
                    fsf.Data.Sec.extraImagesDict(eimLabel.subsection, eImTextDict)
                    
                    eimLabel.grid_forget()
                    widget.render()

                eimLabel.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                                                            [lambda *args: __getBack(eimLabel, event.widget)])
                eimLabel.render()

            mainRow = i + 5 if row == None else row

            if (tocFrame != None)\
                and (subsection == tocFrame.extraImAsETR.subsection)\
                and (imIdx == tocFrame.extraImAsETR.imIdx) \
                and (i == tocFrame.extraImAsETR.eImIdx):

                if type(rootLabel) == list:
                    eimLabel = MultilineText_ETR(rootLabel[i], 
                                                eImWidgetName, 
                                                row = mainRow,
                                                column = column,
                                                imLineIdx = None, 
                                                text = eImText)
                else:
                    eimLabel = MultilineText_ETR(rootLabel, 
                                                eImWidgetName, 
                                                row = mainRow,
                                                column = column,
                                                imLineIdx = None, 
                                                text = eImText)
                eimLabel.config(width=90)
                eimLabel.config(padx=10)
                eimLabel.config(pady=10)
                eimLabel.imIdx = imIdx
                eimLabel.subsection = subsection
                eimLabel.etrWidget = eimLabel
                eimLabel.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                                        [extraImtextUpdate])
                tocFrame.extraImAsETR.widget = eimLabel
                eimLabel.render()
                eimLabel.focus_force()

                eImWidgetsList.append(eimLabel)
                tempLabel = eimLabel
            else:
                if type(rootLabel) == list:
                    tempLabel = TOCLabelWithClick(rootLabel[i], prefix = "temp_" + eImWidgetName,
                                    padding = [0, 0, 0, 0],
                                    row = mainRow, column = column, columnspan = columnspan)
                else:
                    tempLabel = TOCLabelWithClick(rootLabel, prefix = "temp_" + eImWidgetName,
                                    padding = [0, 0, 0, 0],
                                    row = mainRow, column = column, columnspan = columnspan)

                emptyLabel = TOCLabelWithClick(tempLabel, prefix = "empty_" + eImWidgetName,
                                            padding = [imPadLeft, 0, 0, 0],
                                            row = 0, column = 0, columnspan = 1)
                emptyLabel.render()
                tempLabel.imagePath = extraImFilepath
                tempLabel.subsection = subsection
                tempLabel.imIdx = imIdx
                tempLabel.eImIdx = i

                eImg, eimLabel = getImageWidget(tempLabel, extraImFilepath, eImWidgetName, 
                                            imIdx, subsection, imPad = 0,
                                            row = 0, column = 1, columnspan = 1,
                                            resizeFactor = resizeFactor,
                                            extraImIdx = i,
                                            bindOpenWindow = bindOpenWindow,
                                            tocBox = tocFrame)
                eimLabel.subsection = subsection
                eimLabel.imIdx = imIdx
                eimLabel.eImIdx = i

                openOMOnThePageOfTheImage(eimLabel, subsection, imIdx, str(i))

                eimLabel.rebind([ww.currUIImpl.Data.BindID.mouse2],
                                [extraImtextUpdate])

                eImWidgetsList.append(tempLabel)
                tempEImLabel = TOCLabelWithClick(tempLabel, 
                                              text = "",
                                              prefix = "tempLabel_" + eImWidgetName,
                                              row = 0,
                                              column = 0)

                removeEntry = TOCLabelWithClick(tempEImLabel,
                                                text = "[d]",
                                                prefix = "delete_" + eImWidgetName,
                                                row =  i + 5, 
                                                column = 0,
                                                sticky = tk.NW)
                removeEntry.imIdx = imIdx
                removeEntry.subsection = subsection
                removeEntry.eImIdx = i
                removeEntry.tocFrame = tocFrame

                def delEIm(event, *args):
                    widget:TOCLabelWithClick = event.widget
                    fsf.Wr.SectionInfoStructure.removeExtraIm(widget.subsection,
                                                            widget.imIdx,
                                                            eImIdx = widget.eImIdx)
                    
                    if widget.tocFrame != None:
                        tocFrame.render()
                    else:
                        mathMenuManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                        wf.Wr.MenuManagers.MathMenuManager)
                        mathMenuManager.renderWithoutScroll()
                        mathMenuManager.scrollTocToEntry(widget.subsection, widget.imIdx)

                    pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                    wf.Wr.MenuManagers.PdfReadersManager)
                    pdfReadersManager.show(changePrevPos = False, removePrevLabel = True, 
                                           subsection = subsection, imIdx = imIdx,
                                           extraImIdx = str(widget.eImIdx))                    

                    excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                    wf.Wr.MenuManagers.ExcerciseManager)
                    if excerciseManager.shown:
                        excerciseManager.show()

                removeEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],[delEIm])

                bindChangeColorOnInAndOut(removeEntry)
                removeEntry.render()

                moveEntryDown = TOCLabelWithClick(tempEImLabel,
                                                text = "[\u2193",
                                                prefix = "up_" + eImWidgetName,
                                                row =  i + 5, 
                                                column = 1,
                                                sticky = tk.NW)
                moveEntryDown.imIdx = imIdx
                moveEntryDown.subsection = subsection
                moveEntryDown.eImIdx = i
                moveEntryDown.tocFrame = tocFrame

                def moveDown(event, *args):
                    widget:TOCLabelWithClick = event.widget
                    fsf.Wr.SectionInfoStructure.moveExtraIm(widget.subsection,
                                                            widget.imIdx,
                                                            eImIdx = widget.eImIdx,
                                                            down = True)
                    
                    if widget.tocFrame != None:
                        widget.tocFrame.render()
                        widget.tocFrame.shouldScroll = True
                        if (widget.eImIdx + 1) in range(len(eImWidgetsList)):
                            widget.tocFrame.scrollIntoView(None, 
                                                    eImWidgetsList[widget.eImIdx + 1])
                    else:
                        mathMenuManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                        wf.Wr.MenuManagers.MathMenuManager)
                        mathMenuManager.renderWithoutScroll()
                        mathMenuManager.scrollTocToEntry(widget.subsection, widget.imIdx)

                    excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                    wf.Wr.MenuManagers.ExcerciseManager)
                    if excerciseManager.shown:
                        excerciseManager.show()

                moveEntryDown.rebind([ww.currUIImpl.Data.BindID.mouse1],[moveDown])
                bindChangeColorOnInAndOut(moveEntryDown)
                moveEntryDown.render()

                moveEntryUp = TOCLabelWithClick(tempEImLabel,
                                                text = "\u2191]",
                                                prefix = "down_" + eImWidgetName,
                                                row =  i + 5, 
                                                column = 2,
                                                sticky = tk.NW)
                moveEntryUp.imIdx = imIdx
                moveEntryUp.subsection = subsection
                moveEntryUp.eImIdx = i
                moveEntryUp.tocFrame = tocFrame

                def moveUp(event, *args):
                    widget:TOCLabelWithClick = event.widget
                    fsf.Wr.SectionInfoStructure.moveExtraIm(widget.subsection,
                                                            widget.imIdx,
                                                            eImIdx = widget.eImIdx,
                                                            down = False)
                    
                    if widget.tocFrame != None:
                        widget.tocFrame.render()
                        widget.tocFrame.shouldScroll = True
                        if (widget.eImIdx - 1) in range(len(eImWidgetsList)):
                            widget.tocFrame.scrollIntoView(None, 
                                                    eImWidgetsList[widget.eImIdx - 1])
                    else:
                        mathMenuManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                        wf.Wr.MenuManagers.MathMenuManager)
                        mathMenuManager.renderWithoutScroll()
                        mathMenuManager.scrollTocToEntry(widget.subsection, widget.imIdx)

                    excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                    wf.Wr.MenuManagers.ExcerciseManager)
                    if excerciseManager.shown:
                        excerciseManager.show()

                moveEntryUp.rebind([ww.currUIImpl.Data.BindID.mouse1],[moveUp])

                bindChangeColorOnInAndOut(moveEntryUp)
                moveEntryUp.render()

                retake = TOCLabelWithClick(tempEImLabel,
                                                text = "[r]",
                                                prefix = "retake_" + eImWidgetName,
                                                row =  i + 5, 
                                                column = 3,
                                                sticky = tk.NW)
                retake.imIdx = imIdx
                retake.subsection = subsection
                retake.eImIdx = i
                retake.tocFrame = tocFrame

                def retakeCmd(event, *args):
                    widget = event.widget
                    subsection = widget.subsection
                    imIdx = widget.imIdx
                    eImIdx = widget.eImIdx

                    currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                    imagePath = _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(currBookPath,
                                                                                subsection,
                                                                                str(imIdx),
                                                                                str(eImIdx))

                    msg = "Do you want to retake extra image?"
                    response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

                    if not response:
                        return

                    ocf.Wr.FsAppCalls.deleteFile(imagePath)

                    figuresLabelsData = fsf.Data.Sec.figuresLabelsData(subsection)

                    if figuresLabelsData.get(f"{imIdx}_{eImIdx}") != None:
                        figuresLabelsData.pop(f"{imIdx}_{eImIdx}")
                        fsf.Data.Sec.figuresLabelsData(subsection, figuresLabelsData)
                    
                    dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                        wf.Wr.MenuManagers.PdfReadersManager).show(subsection = subsection,
                                                                                    imIdx = imIdx,
                                                                                    selector = True,
                                                                                    removePrevLabel = True,
                                                                                    extraImIdx = eImIdx)
                    def __cmdAfterImageCreated():
                        timer = 0

                        while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                            time.sleep(0.3)
                            timer += 1

                            if timer > 50:
                                break
                        
                        mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                    wf.Wr.MenuManagers.MathMenuManager)
                        mainManager.show()
                        # NOTE: should move to extra image but this should work for now
                        mainManager.moveTocToCurrEntry()
                    
                    t = Thread(target = __cmdAfterImageCreated)
                    t.start()

                retake.rebind([ww.currUIImpl.Data.BindID.mouse1],[retakeCmd])

                bindChangeColorOnInAndOut(retake)
                retake.render()

                def resizeEntryImgCMD(event, tocFrame, *args):
                    resizeFactor = event.widget.get()

                    # check if the format is right
                    if not re.match("^[0-9]\.[0-9]$", resizeFactor):
                        _u.log.autolog(\
                            f"The format of the resize factor '{resizeFactor}'is not correct")
                        return
                    
                    subsection = event.widget.subsection
                    imIdx = event.widget.imIdx
                    
                    uiResizeEntryIdx = fsf.Data.Sec.imageUIResize(subsection)

                    if (uiResizeEntryIdx == None) \
                        or (uiResizeEntryIdx == _u.Token.NotDef.dict_t):
                        uiResizeEntryIdx = {}

                    uiResizeEntryIdx[imIdx] = resizeFactor

                    fsf.Data.Sec.imageUIResize(subsection, uiResizeEntryIdx)

                    if tocFrame != None:
                        tocFrame.renderWithoutScroll()
                    else:
                        mathMenuManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                        wf.Wr.MenuManagers.MathMenuManager)
                        mathMenuManager.renderWithoutScroll()
                        mathMenuManager.scrollTocToEntry(event.widget.subsection, 
                                                         event.widget.imIdx)

                    excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                    wf.Wr.MenuManagers.ExcerciseManager)
                    if excerciseManager.shown:
                        excerciseManager.show()

                changeImSize = ImageSize_ETR(tempEImLabel,
                                            prefix =  "imSize_" + eImWidgetName,
                                            row = i + 5, 
                                            column = 4,
                                            imIdx = imIdx + "_" + str(i),
                                            text = resizeFactor)
                changeImSize.imIdx = imIdx + "_" + str(i)
                changeImSize.widgetObj.imIdx = imIdx + "_" + str(i)
                changeImSize.subsection = subsection
                changeImSize.widgetObj.subsection = subsection
                changeImSize.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                        [lambda e, *args: resizeEntryImgCMD(e, tocFrame)])
                changeImSize.render()

                if createExtraWidgets:
                    tempEImLabel.render()

                eimLabel.render()

                displayedImagesContainer.append(eImg)

                if shouldResetResizeFactor:
                    resizeFactor = None
                    shouldResetResizeFactor = False

                bookCodeProj = TOCLabelWithClick(tempEImLabel,
                                                text = "code: [b",
                                                prefix = "bookCodeProj_" + eImWidgetName,
                                                row =  i + 6, 
                                                column = 0,
                                                sticky = tk.NE,
                                                columnspan = 3)
                bookCodeProj.imIdx = imIdx
                bookCodeProj.subsection = subsection
                bookCodeProj.eImIdx = i
                bookCodeProj.tocFrame = tocFrame

                def openBookCodeProjectCmd(event, *args):
                    subsection = event.widget.subsection
                    imIdx = event.widget.imIdx
                    eImIdx = event.widget.eImIdx

                    fullLink = imIdx + "_" + str(eImIdx)
                    dt.CodeTemp.currCodeFullLink = fullLink

                    bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                    projectPath = _upan.Paths.Book.Code.getAbs(bookPath)

                    if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(projectPath):
                        _u.log.autolog("Please add a book code project files.")
                        return

                    ocf.Wr.IdeCalls.openNewWindow(projectPath)

                    bookCodeFiles:dict = fsf.Data.Sec.bookCodeFile(subsection)

                    if bookCodeFiles.get(fullLink) != None:
                        relFilepath = bookCodeFiles.get(fullLink)
                        time.sleep(0.5)
                        filepath = os.path.join(projectPath, relFilepath)

                        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(filepath):
                            return

                        lines = []
                        with open(filepath) as f:
                            lines = f.read().splitlines()
                        
                        marker = _upan.Names.codeLineMarkerBook(subsection, fullLink)

                        for i in range(len(lines)):
                            if marker in lines[i]:
                                ocf.Wr.IdeCalls.openNewTab(filepath, i)
                                return

                        ocf.Wr.IdeCalls.openNewTab(filepath)

                bookCodeProj.rebind([ww.currUIImpl.Data.BindID.mouse1],[openBookCodeProjectCmd])
                bindChangeColorOnInAndOut(bookCodeProj)
                bookCodeProj.render()

                subsectionCodeProj = TOCLabelWithClick(tempEImLabel,
                                                text = ", s",
                                                prefix = "subCodeProj_" + eImWidgetName,
                                                row =  i + 6, 
                                                column = 3,
                                                sticky = tk.NW,
                                                columnspan = 1)
                subsectionCodeProj.imIdx = imIdx
                subsectionCodeProj.subsection = subsection
                subsectionCodeProj.eImIdx = i
                subsectionCodeProj.tocFrame = tocFrame

                def openSubsectionCodeProjectCmd(event, *args):
                    subsection = event.widget.subsection
                    imIdx = event.widget.imIdx
                    eImIdx = event.widget.eImIdx
                    fullLink = imIdx + "_" + str(eImIdx)

                    dt.CodeTemp.currCodeFullLink = fullLink

                    bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                    codeTemplatePath =_upan.Paths.Book.Code.getSubsectionTemplatePathAbs(bookPath)
                    codeSubsectionPath =_upan.Paths.Section.getCodeRootAbs(bookPath,
                                                                           subsection)

                    if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(codeSubsectionPath):
                        ocf.Wr.FsAppCalls.copyFile(codeTemplatePath, codeSubsectionPath)

                    ocf.Wr.IdeCalls.openNewWindow(codeSubsectionPath)

                    subsectionCodeFiles:dict = fsf.Data.Sec.subsectionCodeFile(subsection)

                    if subsectionCodeFiles.get(fullLink) != None:
                        relFilepath = subsectionCodeFiles.get(fullLink)
                        time.sleep(0.5)
                        filepath = os.path.join(codeSubsectionPath, relFilepath)

                        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(filepath):
                            _u.log.autolog(f"Subsection '{filepath}' file not found.")
                            return

                        lines = []
                        with open(filepath) as f:
                            lines = f.read().splitlines()
                        
                        marker = _upan.Names.codeLineMarkerSubsection(subsection, fullLink)

                        for i in range(len(lines)):
                            if marker in lines[i]:
                                ocf.Wr.IdeCalls.openNewTab(filepath, i)
                                return

                        ocf.Wr.IdeCalls.openNewTab(filepath)

                subsectionCodeProj.rebind([ww.currUIImpl.Data.BindID.mouse1],[openSubsectionCodeProjectCmd])
                bindChangeColorOnInAndOut(subsectionCodeProj)
                subsectionCodeProj.render()

                entryCodeProj = TOCLabelWithClick(tempEImLabel,
                                                text = ", e]",
                                                prefix = "entryCodeProj_" + eImWidgetName,
                                                row =  i + 6, 
                                                column = 4,
                                                sticky = tk.NW,
                                                columnspan = 1)
                entryCodeProj.imIdx = imIdx
                entryCodeProj.subsection = subsection
                entryCodeProj.eImIdx = i
                entryCodeProj.tocFrame = tocFrame

                def openEntryCodeProjectCmd(event, *args):
                    subsection =  event.widget.subsection
                    imIdx =  event.widget.imIdx
                    eImIdx =  event.widget.eImIdx

                    bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

                    entryPath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)

                    if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryPath):
                        fsf.Wr.EntryInfoStructure.createStructure(bookPath, subsection, imIdx)

                    entryCodeProjFilepath = _upan.Paths.Entry.getCodeProjAbs(bookPath, subsection, imIdx)
                    codeFolderbaseName = _upan.Names.codeProjectBaseName()
                    entryCodeProjFilepath = entryCodeProjFilepath.replace(codeFolderbaseName, 
                                                                          codeFolderbaseName + "_" + str(eImIdx))

                    if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryCodeProjFilepath):
                        codeProjTemplatePath = \
                            _upan.Paths.Book.Code.getEntryTemplatePathAbs(bookPath)
                        ocf.Wr.FsAppCalls.copyFile(codeProjTemplatePath, entryCodeProjFilepath)

                    ocf.Wr.IdeCalls.openNewWindow(entryCodeProjFilepath)

                entryCodeProj.rebind([ww.currUIImpl.Data.BindID.mouse1],[openEntryCodeProjectCmd])
                bindChangeColorOnInAndOut(entryCodeProj)
                entryCodeProj.render()

                addProof = TOCLabelWithClick(tempEImLabel,
                                                text = "[AddPr",
                                                prefix = "addProof_" + eImWidgetName,
                                                row =  i + 7, 
                                                column = 0,
                                                sticky = tk.NW,
                                                columnspan = 2)
                addProof.imIdx = imIdx
                addProof.subsection = subsection
                addProof.eImIdx = i
                addProof.tocFrame = tocFrame

                def addExtraImProofCmd(event, *args):
                    widget = event.widget
                    addExtraIm(widget.subsection, widget.imIdx, 
                               True, widget.tocFrame, widget)

                addProof.rebind([ww.currUIImpl.Data.BindID.mouse1],[addExtraImProofCmd])
                bindChangeColorOnInAndOut(addProof)
                addProof.render()

                addEIm = TOCLabelWithClick(tempEImLabel,
                                                text = ", AddImage]",
                                                prefix = "addEIm_" + eImWidgetName,
                                                row =  i + 7, 
                                                column = 2,
                                                sticky = tk.NW,
                                                columnspan = 3)
                addEIm.imIdx = imIdx
                addEIm.subsection = subsection
                addEIm.eImIdx = i
                addEIm.tocFrame = tocFrame

                def addExtraImCmd(event, *args):
                    widget = event.widget
                    addExtraIm(widget.subsection, widget.imIdx, 
                               False, widget.tocFrame, widget)

                addEIm.rebind([ww.currUIImpl.Data.BindID.mouse1],[addExtraImCmd])
                bindChangeColorOnInAndOut(addEIm)
                addEIm.render()

            outLabels.append(tempLabel)

            imageBaloon.bind(eimLabel, "{0}".format(eImText))

    return outLabels


def closeAllImages(gpframe, showAll, isWidgetLink, secondIm = [None, None], linkIdx = None):
    '''
    close all images of children of the widget
    '''
    for parent in gpframe.getChildren():
        # NOTE this is not an ideal hack to get the 
        if "getChildren" in dir(parent):
            for child in parent.getChildren():
                if "getChildren" in dir(child):
                    for gChild in child.getChildren():
                        if "contentOfImages_" in str(gChild):
                            subsection = str(gChild).split("_")[-2].replace("$", ".")
                            idx = str(gChild).split("_")[-1]

                            alwaysShow = False
                            if idx !=  "-1":
                                alwaysShow = fsf.Data.Sec.tocWImageDict(subsection)[idx] == "1"

                            if (not alwaysShow) or showAll: 
                                gChild.clicked = False
                            else: 
                                gChild.clicked = True

                            if "Row2" in str(child):
                                child.destroy()

                if "contentGlLinksOfImages_" in str(child):
                    child.clicked = False

                if dc.UIConsts.imageWidgetID in str(child):
                    subsection = str(child).split("_")[-2].replace("$", ".")
                    idx = str(child).split("_")[-1]

                    alwaysShow = False
                    if idx !=  "-1":
                        alwaysShow = fsf.Data.Sec.tocWImageDict(subsection)[idx] == "1"

                    if ((not alwaysShow) or showAll or isWidgetLink) and\
                        ([subsection,idx] != secondIm):

                        if isWidgetLink:
                            if idx == linkIdx:
                                child.destroy()
                            else:
                                continue
                        try:
                            child.destroy()
                        except:
                            pass