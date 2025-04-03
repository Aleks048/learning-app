from PIL import Image, ImageOps
import subprocess
import time
import re
from threading import Thread
import os
import copy

import UI.widgets_wrappers as ww
import UI.widgets_data as wd
import UI.widgets_facade as wf

import file_system.file_system_facade as fsf
import data.constants as dc
import data.temp as dt
import _utils.pathsAndNames as _upan
import settings.facade as sf
import _utils._utils_main as _u
import outside_calls.outside_calls_facade as ocf
import generalManger.generalManger as gm
import tex_file.tex_file_facade as tff


def bindWidgetTextUpdatable(event, getTextFunc, setTextFunc, 
                                   updateImageFunc = lambda *args: None,
                                   changeOnEtrFunc = lambda *args: None,
                                   changeOnLabelBackFunc = lambda *args: None,):
    widget = event.widget

    def __bringImageWidgetBack(event, imageWidget, setTextFunc, updateImageFunc, changeOnLabelBackFunc):
        newText = event.widget.getData()

        setTextFunc(newText, imageWidget)
        updateImageFunc(imageWidget)
        
        event.widget.hide()
        imageWidget.updateLabel()
        imageWidget.render()

        changeOnLabelBackFunc(widget)

    subsectionLabel = MultilineText_ETR(widget.rootWidget, 
                                        "subsectionETR_" + widget.name, 
                                        widget.row, widget.column, 
                                        "", # NOTE: not used anywhere  
                                        getTextFunc(widget))
    subsectionLabel.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                            [lambda e, w = widget, sf = setTextFunc,  uf = updateImageFunc, bf = changeOnLabelBackFunc,
                             *args: __bringImageWidgetBack(e, w, sf, uf, bf)])
    subsectionLabel.forceFocus()
    subsectionLabel.render()
    widget.hide()
    changeOnEtrFunc(widget)



def bindChangeColorOnInAndOut(widget, shouldBeRed = False, shouldBeBrown = False):
    def __changeTextColorBlue(event = None, *args):
        event.widget.changeColor("blue")

    def __changeTextColorBrown(event = None, *args):
        event.widget.changeColor("brown")

    def __changeTextColorRed(event = None, *args):
        event.widget.changeColor("red")

    def __changeTextColorWhite(event = None, *args):
        event.widget.changeColor("white")
    
    widget.rebind([ww.currUIImpl.Data.BindID.enterWidget], [__changeTextColorBlue])
    if not shouldBeRed:
        widget.rebind([ww.currUIImpl.Data.BindID.leaveWidget], [__changeTextColorWhite])
    else:
        widget.rebind([ww.currUIImpl.Data.BindID.leaveWidget], [__changeTextColorRed])
    
    if shouldBeBrown:
        widget.rebind([ww.currUIImpl.Data.BindID.leaveWidget], [__changeTextColorBrown])


def getGroupImg(subsection, currImGroupName):
    gi = str(list(fsf.Data.Sec.imagesGroupsList(subsection).keys()).index(currImGroupName))
    groupImgPath = _upan.Paths.Screenshot.Images.getGroupImageAbs(sf.Wr.Manager.Book.getCurrBookName(), 
                                            subsection,
                                            gi)

    if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(groupImgPath):
        result = Image.open(groupImgPath)
    else:
        result = \
            fsf.Wr.SectionInfoStructure.rebuildGroupOnlyImOnlyLatex(subsection,
                                                                    currImGroupName)

    shrink = 0.8
    result.thumbnail([int(result.size[0] * shrink),int(result.size[1] * shrink)], Image.LANCZOS)
    result = ww.currUIImpl.UIImage(result)

    return result


def getEntryImg(tex, subsection, imIdx):
    currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
    entryImgPath = _upan.Paths.Screenshot.Images.getMainEntryTexImageAbs(currBookPath, 
                                                                        subsection, 
                                                                        imIdx)

    if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryImgPath):
        result = Image.open(entryImgPath)
    else:
        result = tff.Wr.TexFileUtils.fromTexToImage(tex, 
                                                    entryImgPath,
                                                    fixedWidth = 700)

    return result


class ImageGroupOM(ww.currUIImpl.OptionMenu):
    def __init__(self,
                 listOfOptions, 
                 rootWidget, 
                 subsection,
                 imIdx,
                 tocBox,
                 column,
                 currImGroupName = None):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : column, 
                                            "row" : 0,
                                            "columnspan" : 3},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, 
                                     "sticky" : ww.currUIImpl.Orientation.NW}
        }

        name = "GroupOM_"

        self.imIdx = imIdx
        self.subsection = subsection
        self.tocBox = tocBox

        prefix = "_Group_" + subsection.replace(".", "_") + "_" + imIdx

        super().__init__(prefix, 
                         name,
                         listOfOptions,
                         rootWidget,
                         data,
                         defaultOption = currImGroupName,
                         cmd = self.chooseGroupCmd)
                        
    def chooseGroupCmd(self):
        imagesGroupList:list = list(fsf.Data.Sec.imagesGroupsList(self.subsection).keys())
        imagesGroupDict = fsf.Data.Sec.imagesGroupDict(self.subsection)
        imagesGroupDict[self.imIdx] =  imagesGroupList.index(self.getData())
        fsf.Data.Sec.imagesGroupDict(self.subsection, imagesGroupDict)

        
        for w in wd.Data.Reactors.entryChangeReactors.values():
            if "onGroupChange" in dir(w):
                w.onGroupChange(self.subsection, self.imIdx)


class EntryShowPermamentlyCheckbox(ww.currUIImpl.Checkbox):
    def __init__(self, parent, subsection, imIdx, prefix, row, column):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        name = "_EntryShowPermamentlyCheckbox_"

        self.subsection = subsection
        self.imIdx = str(imIdx)

        tocWImageDict = fsf.Data.Sec.tocWImageDict(self.subsection)
        if tocWImageDict == _u.Token.NotDef.dict_t:
            alwaysShow = "0"
        else:
            alwaysShow = tocWImageDict[self.imIdx]

        super().__init__(prefix,
                         name,
                         parent, 
                         renderData,
                         command = lambda *args: self.__cmd())
        self.setData(int(alwaysShow))

    def __cmd(self):
        tocWImageDict = fsf.Data.Sec.tocWImageDict(self.subsection)
        tocWImageDict[self.imIdx] = str(self.getData())
        fsf.Data.Sec.tocWImageDict(self.subsection, tocWImageDict)


        for w in wd.Data.Reactors.entryChangeReactors.values():
            if "onAlwaysShowChange" in dir(w):
                w.onAlwaysShowChange(self.subsection, self.imIdx)
    
    def render(self):
        tocWImageDict = fsf.Data.Sec.tocWImageDict(self.subsection)
        newData = _u.Token.NotDef.str_t

        if tocWImageDict.get(self.imIdx) != None:
            newData = tocWImageDict[self.imIdx]

        self.setData(newData)
        return super().render(self.renderData)


class MultilineText_ETR(ww.currUIImpl.MultilineText):
    def __init__(self, parentWidget, prefix, row, column, imLineIdx, text:str, width = 70, *args, **kwargs):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0}
        }

        name = "_MultilineText_ETR_"

        self.imIdx = None
        self.eImIdx = None
        self.subsection = None
        self.etrWidget = None
        self.lineImIdx = None

        self.root = parentWidget

        self.defaultText = text

        while text[-2:] == "\n":
            text = text[:-2]

        text = text.rstrip()

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
     
        super().__init__(prefix,
                         name,
                         parentWidget, 
                         renderData,
                         text = text,
                         wrap = None, 
                         width = width, 
                         height = newHeight, 
                         *args, 
                         **kwargs)

        self.rebind([ww.currUIImpl.Data.BindID.Keys.ctrlv],
                    [lambda *args: self.pasteTextFromClipboard(*args)])
        self.rebind_()

    def rebind_(self, keys = [], funcs = []):
        self.rebind(keys, funcs)
        
        def __boldenText(*args):
            self.wrapSelectedText("\\textbf{", "}")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdb],
                    [lambda *args: __boldenText(*args)])
        

        def __underlineText(*args):
             self.wrapSelectedText("\\underline{", "}")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdu],
                  [lambda *args: __underlineText(*args)])

        def __addNote(*args):
            self.addTextAtStart("\\textbf{NOTE:} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdn],
                  [lambda *args: __addNote(*args)])

        def __addNoteInPlace(*args):
            self.addTextAtCurrent("\\textbf{NOTE:} ")\

        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdshn],
                  [lambda *args: __addNoteInPlace(*args)])

        def __addDef(*args):
            self.addTextAtCurrent("\\textbf{DEF:} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdd],
                  [lambda *args: __addDef(*args)])

        def __addProposion(*args):
            self.addTextAtCurrent("\\textbf{Proposition:} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdshp],
                  [lambda *args: __addProposion(*args)])

        def __addExample(*args):
            self.addTextAtStart("\\textbf{EX:} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmde],
                  [lambda *args: __addExample(*args)])

        def __addLemma(*args):
            self.addTextAtStart("\\textbf{Lemma:} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdl],
                  [lambda *args: __addLemma(*args)])

        def __addCorollary(*args):
            self.addTextAtStart("\\textbf{Corollary:} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdshc],
                  [lambda *args: __addCorollary(*args)])

        def __addCode(*args):
            self.addTextAtStart("\\textbf{Code:} ")

        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmddc],
                    [lambda *args: __addCode(*args)])

        def __addExcercise(*args):
            self.addTextAtStart("\\textbf{\\underline{EXCERCISE:}} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdshe],
                    [lambda *args: __addExcercise(*args)])

        def __addTheorem(*args):
            self.addTextAtStart("\\textbf{Theorem:} ")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdt],
                    [lambda *args: __addTheorem(*args)])

        def __addProof(*args):
            self.addTextAtStart("proof")
        
        self.rebind([ww.currUIImpl.Data.BindID.Keys.cmdp],
                  [lambda *args: __addProof(*args)])


class ImageSize_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix, row, column, imIdx, text, width = 3):
        self.subsection = None
        self.imIdx = None
        self.eImIdx = None
        self.textETR = None

        name = "_imageSizeTOC_ETR" + str(imIdx) + "_" + str(self.eImIdx)
        self.defaultText = text

        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
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


class TOCFrame(ww.currUIImpl.Frame):
    def __init__(self, root, prefix, row, column, columnspan = 1, padding = [0, 0, 0, 0]) -> None:
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : column, "row" : row, "columnspan": columnspan},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        name = "_TOCFrame"

        self.subsection = None
        self.imIdx = None

        self.row = row
        self.column = column
        self.columnspan = columnspan

        super().__init__(prefix, name, root, renderData, padding = padding)


class TOCTextWithClick(ww.currUIImpl.Label):
    '''
    this is used to run different commands on whether the label was clicked even or odd times
    '''

    def __init__(self, root, prefix, row, column, columnspan = 1, sticky = ww.currUIImpl.Orientation.NW, text = ""):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : column, "row" : row, "columnspan": columnspan},
            ww.TkWidgets.__name__ : {"padx" : 10, "pady" : 10, "sticky" : sticky}
        }

        name = "_TOCTextWithClick_"

        self.clicked = False
        self.text = text
        
        self.row = row
        self.column = column
        self.columnspan = columnspan
        self.sticky = sticky

        super().__init__(prefix, name, root, renderData, text = self.text)

        self.setStyle(ww.currUIImpl.Data.Styles.entryText)

    def hide(self, **kwargs):
        return super().hide(**kwargs)

    # def __getattr__(self, name: str):
    #     return self.__dict__[f"_{name}"]

    # def __setattr__(self, name, value):
    #     self.__dict__[f"_{name}"] = value


class TOCTextWithClickTextOnlyEntry(TOCTextWithClick):
    width = 60

    def __init__(self, root, prefix, row, column, columnspan=1, sticky=ww.currUIImpl.Orientation.NW, text=""):
        super().__init__(root, prefix, row, column, columnspan, sticky, text)
        self.setWrapLength(self.width * 9)
        self.setWidth(self.width)

    def updateLabel(self):
        self.changeText(fsf.Data.Sec.imageText(self.subsection)[self.imIdx])
        self.setWidth(self.width)


class TOCCanvasWithclick(ww.currUIImpl.Canvas):
    class Label:
        def __init__(self, subsection, imIdx, canvas, 
                     startX, startY, endX, endY,
                     omPage, 
                     labelStartX = None, labelStartY = None):
            self.canvas = canvas
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

            subsecId = self.subsection.replace(".", "_")
            prefix = f"{subsecId}_{self.imIdx}"

            if self.eImIdx != None:
                prefix += f"_{self.eImIdx}"

            name = "_CanvasButton_"
            renderData = {
                ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 0},
                ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.W}
            }
            self.label = ww.currUIImpl.Button(prefix = prefix,
                                 name = name,
                                 text = text,
                                 rootWidget = self.canvas,
                                 renderData = renderData,
                                 cmd = self.__labelCmd
                                 )

            self.label.setStyle("Canvas.TMenubutton")
            self.id = self.canvas.createButton(self.labelStartX, 
                                               self.labelStartY, 
                                               anchor = ww.currUIImpl.Orientation.NW, 
                                               buttonWidget = self.label,
                                               tags = f"button:{self.subsection}:{self.imIdx}")
            self.handleId = self.canvas.createRectangle(self.labelStartX, 
                                        self.labelStartY,
                                        self.labelStartX + 10,
                                        self.labelStartY + 40,
                                        fill = "green",
                                        tags = f"buttonRect:{self.subsection}:{self.imIdx}")
            self.handleId2 = self.canvas.createRectangle(self.labelStartX + 70, 
                                        self.labelStartY,
                                        self.labelStartX + 80,
                                        self.labelStartY - 10,
                                        fill = "green",
                                        tags = f"buttonRect:{self.subsection}:{self.imIdx}")

            def __drawLine(self):
                self.line = self.canvas.createRectangle(self.startX - 5, self.startY,
                                                    self.startX + 1, self.endY,
                                                    fill = "red",
                                                    tags = f"entryLineRect:{self.subsection}:{self.imIdx}")

            def __deleteLine(self):
                if self.line != None:
                    self.canvas.deleteByTag(self.line)
                    self.line = None              

            self.label.rebind(["<Enter>", "<Leave>"], 
                              [lambda *args: __drawLine(self), lambda *args: __deleteLine(self)])

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
            self.canvas.deleteByTag(self.handleId)
            self.canvas.deleteByTag(self.handleId2)
            if self.label != None:
                self.handleId = self.canvas.createRectangle(self.labelStartX, 
                                        self.labelStartY,
                                        self.labelStartX + 10,
                                        self.labelStartY + 40,
                                        fill = "yellow",
                                        tags = f"buttonRect:{self.subsection}:{self.imIdx}")
                self.handleId2 = self.canvas.createRectangle(self.labelStartX + 70, 
                                        self.labelStartY,
                                        self.labelStartX + 80,
                                        self.labelStartY - 10,
                                        fill = "yellow",
                                        tags = f"buttonRect:{self.subsection}:{self.imIdx}")

        def unselect(self):
            self.canvas.deleteByTag(self.handleId) 
            self.canvas.deleteByTag(self.handleId2) 
            if self.label != None:
                self.handleId = self.canvas.createRectangle(self.labelStartX, 
                                        self.labelStartY,
                                        self.labelStartX + 10,
                                        self.labelStartY + 40,
                                        fill = "green",
                                        tags = f"buttonRect:{self.subsection}:{self.imIdx}")
                self.handleId2 = self.canvas.createRectangle(self.labelStartX + 70,
                                            self.labelStartY,
                                            self.labelStartX + 80,
                                            self.labelStartY - 10,
                                            fill = "green",
                                            tags = f"buttonRect:{self.subsection}:{self.imIdx}")

        def deleteLabel(self):
            if self.id != None:
                self.canvas.deleteByTag(self.id)
                self.canvas.labels = [i for i in self.canvas.labels if i.id != self.id]
                self.label.hide()
                self.id = None
            if self.handleId != None:
                self.canvas.deleteByTag(self.handleId)
                self.canvas.deleteByTag(self.handleId2)
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

            self.canvas = canvas
            
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

            self.cornerWidgetsIds[0] = self.canvas.createOval(self.startX - radius, 
                                                            self.startY - radius,
                                                            self.startX + radius, 
                                                            self.startY + radius,
                                                            fill = self.cornerWidgetsColor, 
                                                            outline = self.cornerWidgetsOutline,
                                                            tags = "cornerWidget")
            self.cornerWidgetsIds[1] = self.canvas.createOval(self.endX - radius, 
                                                            self.startY - radius,
                                                            self.endX + radius, 
                                                            self.startY + radius, 
                                                            fill = self.cornerWidgetsColor, 
                                                            outline = self.cornerWidgetsOutline,
                                                            tags = "cornerWidget")
            self.cornerWidgetsIds[2] = self.canvas.createOval(self.startX - radius, 
                                                            self.endY - radius,
                                                            self.startX + radius, 
                                                            self.endY + radius, 
                                                            fill = self.cornerWidgetsColor, 
                                                            outline = self.cornerWidgetsOutline,
                                                            tags = "cornerWidget")
            self.cornerWidgetsIds[3] = self.canvas.createOval(self.endX - radius, 
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
            self.imageContainer = ww.currUIImpl.UIImage(image)

            if not self.canvas.selectingZone:
                self.id =  self.canvas.createImage(x1, y1, 
                                                   image = self.imageContainer, 
                                                   anchor=ww.currUIImpl.Orientation.NW, 
                                                   tag = self.tag)
            else:
                self.id =  self.canvas.createPolygon([x1, y1, x2, y1, x2, y2, x1, y2], 
                                                    fill = '',
                                                    outline = "black",
                                                    tags = self.tag)

        def deleteCornerWidgets(self):      
            for w in self.cornerWidgetsIds:
                if w != None:
                    self.canvas.deleteByTag(w)
            
            self.cornerWidgetsIds = [None, None, None, None]

        def deleteRectangle(self):
            if self.id != None:
                self.deleteCornerWidgets()
                self.canvas.deleteByTag(self.id)

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

        keys = ["<Mod1-s>", "<Delete>"]
        cmds = [lambda *args: self.saveFigures(stampChanges = True),
                lambda *args: self.deleteSelectedRectangle()]
        self.rebind(keys, cmds)

        if self.selectingZone \
            and self.lastRecrangle != None:
            x = self.lastRecrangle.startX
            y =  self.lastRecrangle.startY
            x1 = self.lastRecrangle.endX
            y1 = self.lastRecrangle.endY
            self.lastRecrangle.deleteRectangle()

            if "image" in dir(self.image):
                im = self.image.image
            else:
                im = self.image
            im = im.crop([x - 1, y - 1, x1 + 1, y1 + 1])

            if self.getTextOfSelector:
                text = _u.getTextFromImage(None, im)

                subprocess.run("pbcopy", text=True, input=text)
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
                imLinkOMPageDict[self.imIdx] = str(self.omPage)
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
            self.saveFigures()

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

        overlapIds = self.findOverlapping(x1, y1, x1, y1)
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
            overlapIds = self.findOverlapping(x1, y1, x1, y1)

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

        cws = self.findByTag("cornerWidget")
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
                figuresList = copy.copy(figuresList)

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
            if type(f) != str:
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

            proofsManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.ProofsManager)
            proofsManager.refresh(self.subsection, self.imIdx)


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
                 columnspan = 1, sticky = ww.currUIImpl.Orientation.NW, 
                 image = None, extraImIdx = None,
                 makeDrawable = True, 
                 isPdfPage = False, page = None,
                 resizeFactor = 1.0,
                 imagePath = "",
                 *args, **kwargs) -> None:
        self.root = root

        self.row = row
        self.column = column
        self.columnspan = columnspan
        self.sticky = sticky
        self.image = image
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

        if "width" in dir(self.image):
            self.width = self.image.width()
            self.height = self.image.height()
        else:
            self.width = self.image.getWidth()
            self.height = self.image.getHeight()

        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        name = "_Canvas_"

        super().__init__(prefix, name, root, renderData, image, self.width, self.height)
        self.readFigures()

        if makeDrawable:
            if not self.isPdfPage:
                keys, cmds = self.__bindCmd()
                self.rebind(keys, cmds)
            else:
                keys = ["<Enter>", "<Leave>"]

                def __b(*args):
                    keys, cmds = self.__bindCmd()
                    self.rebind(keys, cmds)
                def __ub(*args):
                    keys = self.__unbindCmd()
                    self.unbind(keys)

                cmds = [__b, __ub]
                self.rebind(keys, cmds)

    def refreshImage(self, addBrownBorder = True):
        self.pilIm = Image.open(self.imagePath)
        pilIm = self.pilIm

        newWidth = self.image.getWidth()
        newHeight = self.image.getHeight()
        
        pilIm = pilIm.resize([int(newWidth), int(newHeight)], Image.LANCZOS)

        if addBrownBorder:
            pilIm = ImageOps.expand(pilIm, border = 2, fill = "brown")

        self.image = ww.currUIImpl.UIImage(pilIm)

        super().refreshImage(self.backgroundImage, self.image)

        self.readFigures()

        if self.makeDrawable:
            if not self.isPdfPage:
                keys, cmds = self.__bindCmd()
                self.rebind(keys, cmds)
            else:
                keys = ["<Enter>", "<Leave>"]

                def __b(*args):
                    keys, cmds = self.__bindCmd()
                    self.rebind(keys, cmds)
                def __ub(*args):
                    keys = self.__unbindCmd()
                    self.unbind(keys)

                cmds = [__b, __ub]
                self.rebind(keys, cmds)

    def getEntryWidget(self, subsection, imIdx , eImIdx = None):
        for l in self.labels:
            if (l.subsection == subsection) and (str(l.imIdx) == str(imIdx)):
                if eImIdx == None:
                    return l
                else:
                    if str(l.eImIdx) == str(eImIdx):
                        return l

        return None

    def __bindCmd(self, *args):
        return ["<Shift-B1-Motion>", "<B1-Motion>", "<Button-1>", "<ButtonRelease-1>"],\
               [self.draw, self.draw, self.clickOnFigure, self.release]

    def __unbindCmd(self, *args):
        return ["<Shift-B1-Motion>", "<B1-Motion>", "<Button-1>", 
                "<ButtonRelease-1>", "<Mod1-s>", "<Delete>"]


class TOCLabelWithClick(ww.currUIImpl.Label):
    '''
    this is used to run different commands on whether the label was clicked even or odd times
    '''
    def __init__(self, root, prefix, row, column, columnspan = 1, 
                 sticky = ww.currUIImpl.Orientation.NW, padding = [0, 0 ,0, 0], image = None, text = None) -> None:   
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row, "columnspan" : columnspan},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : sticky}
        }
        name = "_TOCLabelWithClick_"

        self.root = root
        self.clicked = False
        self.imIdx = ""
        self.eImIdx = ""
        self.subsection = ""
        self.imagePath = ""
        self.group = ""
        self.image = image
        self.text = text
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

        super().__init__(prefix, name, root, 
                            renderData, 
                            image = self.image,
                            text = self.text,
                            padding = padding)

    def updateImage(self, image):
        super().updateImage(image)

    def changePermamentColor(self, newColor):
        super().changeColor(newColor)
        if newColor == "brown":
            bindChangeColorOnInAndOut(self, shouldBeBrown = True)
        else:
            bindChangeColorOnInAndOut(self, shouldBeBrown = False)

class TOCLabelWithClickEntry(TOCLabelWithClick):
    def updateLabel(self):
        pilIm = getEntryImg("no", self.subsection, self.imIdx)

        shrink = 0.7
        pilIm.thumbnail([int(pilIm.size[0] * shrink),int(pilIm.size[1] * shrink)], Image.LANCZOS)
        self.image = ww.currUIImpl.UIImage(pilIm)
        super().updateImage(self.image)

class TOCLabelWithClickGroup(TOCLabelWithClick):
    def updateLabel(self):
        self.image = getGroupImg(self.subsection, self.group)
        super().updateImage(self.image)

class TOCLabeWithClickSubsection(TOCLabelWithClick):   
    def updateLabel(self):
        if self.subsection in list(fsf.Data.Book.sections.keys()):
            topSectionImgPath = _upan.Paths.Screenshot.Images.getTopSectionEntryImageAbs(
                                                            sf.Wr.Manager.Book.getCurrBookName(),
                                                            self.subsection)

            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(topSectionImgPath):
                self.result = Image.open(topSectionImgPath)
            else:
                self.result = fsf.Wr.SectionInfoStructure.rebuildTopSectionLatex(self.subsection,
                                                                            _upan.Names.Subsection.getTopSectionPretty)
            result = self.result
            shrink = 0.8
            result.thumbnail([int(result.size[0] * shrink),int(result.size[1] * shrink)], Image.LANCZOS)
            self.image = ww.currUIImpl.UIImage(result)
            super().updateImage(self.image)
        else:
            subsectionImgPath = _upan.Paths.Screenshot.Images.getSubsectionEntryImageAbs(
                                                            sf.Wr.Manager.Book.getCurrBookName(), 
                                                            self.subsection)

            if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(subsectionImgPath):
                self.result = Image.open(subsectionImgPath)
            else:
                self.result = \
                    fsf.Wr.SectionInfoStructure.rebuildSubsectionImOnlyLatex(self.subsection, 
                                                                            _upan.Names.Subsection.getSubsectionPretty)
            result = self.result
            shrink = 0.8
            result.thumbnail([int(result.size[0] * shrink),int(result.size[1] * shrink)], Image.LANCZOS)
            self.image = ww.currUIImpl.UIImage(result)
            super().updateImage(self.image)


class SubsectionFrameManager:
    def __init__(self, subsection, subsectionFrame, topFrame, entriesFrame, subsectionChildrenSectionsFrame, widgetFactory):
        self.factory = widgetFactory
        self.subsection = subsection

        self.subsectionFrame = subsectionFrame
        self.topFrame = topFrame
        self.entriesFrame = entriesFrame
        self.subsectionChildrenSectionsFrame = subsectionChildrenSectionsFrame

        self.openContentWidget = None
        self.entriesWidgetManagers = {}

    def removeAllSubsections(self):
        self.subsectionChildrenSectionsFrame.destroy()

        self.subsectionChildrenSectionsFrame = \
            self.factory.produceSectionChildrenSectionsFrame(self.subsectionFrame)

    def addEntryWidgetsForSubsection(self, filter = ""):
        entries = fsf.Data.Sec.imLinkDict(self.subsection)

        row = 0

        for imIdx, imText in entries.items():
            if imIdx == _u.Token.NotDef.str_t:
                continue
            if filter in imText:
                self.addEntryWidget(imIdx)

            row += 1

    def openSubsection(self):
        if self.openContentWidget != None:
            self.openContentWidget.clicked = True
            self.openContentWidget.changeColor("brown")
            bindChangeColorOnInAndOut(self.openContentWidget, True)

    def closeSubsection(self):
        for ch in self.entriesFrame.getChildren().copy():
            ch.destroy()
        
        if self.openContentWidget != None:
            self.openContentWidget.clicked = False
            self.openContentWidget.changeColor("white")
            bindChangeColorOnInAndOut(self.openContentWidget, False)

        self.entriesFrame.hide()


class SubsectionFrameManagerMainTOC(SubsectionFrameManager):
    def addEntryWidget(self, imIdx):                
        entryWidgetFactory = EntryWidgetFactoryTOC(self.subsection, imIdx, 0, 0)
        row = len(list(self.entriesWidgetManagers.keys()))
        entryWidgetFactory.produceEntryWidgetsForFrame(self.entriesFrame, row)

        self.entriesWidgetManagers[imIdx] = entryWidgetFactory.entryFrameManager

class SubsectionFrameManagerSearchTOC(SubsectionFrameManager):
    def addEntryWidget(self, imIdx):                
        entryWidgetFactory = EntryWidgetFactorySearchTOC(self.subsection, imIdx, 0, 0)
        row = len(list(self.entriesWidgetManagers.keys()))
        entryWidgetFactory.produceEntryWidgetsForFrame(self.entriesFrame, row)
        self.entriesWidgetManagers[imIdx] = entryWidgetFactory.entryFrameManager


class EntryFrameManager:
    def __init__(self, entryFrame, subsection, imIdx, widgetFactory):
        self.factory = widgetFactory

        self.subsection = subsection
        self.imIdx = imIdx

        self.entryFrame = entryFrame
        self.groupFrame = None
        self.rowFrame1 = None

        self.fullMoveWidget = None
        self.uiResizeEtr = None
        self.latexEntryImage = None

        self.rowFrame2 = None
        self.linksFrameManager = None
        self.imagesFrame = None

        self.imagesShown = False

        self.mainImLabel = None
        self.extraImLabels = None

    def changeFullMoveColor(self, default):
        if self.fullMoveWidget == None:
            return
        if default:
            self.fullMoveWidget.changeColor("white")
            bindChangeColorOnInAndOut(self.fullMoveWidget, False)
        else:
            self.fullMoveWidget.changeColor("brown")
            bindChangeColorOnInAndOut(self.fullMoveWidget, True)

    def alwaysShow(self):
        tocWImageDict = fsf.Data.Sec.tocWImageDict(self.subsection)
        if tocWImageDict == _u.Token.NotDef.dict_t:
            alwaysShow = False
        else:
            alwaysShow = True if tocWImageDict[self.imIdx] != "0" else False
        return alwaysShow

    def updateMainImage(self):
        if self.mainImLabel != None:
            self.mainImLabel.destroy()
            self.__setMainImage()
    
    def updateEntryImage(self):
        if self.latexEntryImage != None:
            self.latexEntryImage.updateLabel()

    def __getExtraImageFrame(self, eImIdx):
        entryImagesFactory = EntryImagesFactory(self.subsection, self.imIdx)
        extraImFrame = entryImagesFactory.produceEntryExtraImageFrame(rootLabel = self.imagesFrame,
                                                                      eImIdx = int(eImIdx),
                                                                      imPadLeft = 0,
                                                                      leftMove = 0,
                                                                      createExtraWidgets = True,
                                                                      resizeFactor = 1.0,
                                                                      bindOpenWindow = True)
        return extraImFrame

    def updateExtraImage(self, eImIdx):
        eImFrameIdx = self.__findFrameIdxByEImIdx(eImIdx)
        self.replaceExtraImage(eImFrameIdx, eImFrameIdx)
    
    def replaceExtraImage(self, origEImFrameIdx, newEImFrameIdx):
        extraImFrame = self.__getExtraImageFrame(self.extraImLabels[int(newEImFrameIdx)].eImIdx)
        
        self.extraImLabels[int(origEImFrameIdx)].hide()
        self.extraImLabels[int(origEImFrameIdx)] = extraImFrame
        self.extraImLabels[int(origEImFrameIdx)].render()
    
    def __updateEImFrameEImIdx(self, frameIdx, newEImIdx):
        self.extraImLabels[frameIdx].eImIdx = newEImIdx
        for ch in self.extraImLabels[frameIdx].getChildren():
            ch.eImIdx = newEImIdx
            for gch in ch.getChildren():
                gch.eImIdx = newEImIdx

    def deleteExtraImage(self, eImIdx):
        for i in range(len(self.extraImLabels)):
            if self.extraImLabels[i].eImIdx == int(eImIdx):
                frameIdx = i
                self.extraImLabels[i].destroy()
            elif self.extraImLabels[i].eImIdx > int(eImIdx):
                newEImIdx = str(int(self.extraImLabels[i].eImIdx) - 1)
                self.__updateEImFrameEImIdx(i, newEImIdx)

        self.extraImLabels.pop(frameIdx)

    def addExtraImIdx(self, eImIdx):
        if self.extraImLabels != None:
            extraImFrame = self.__getExtraImageFrame(eImIdx)
            extraImFrame.render()
            self.extraImLabels.append(extraImFrame)
            return extraImFrame

    def __findFrameIdxByEImIdx(self, eImIdx):
        for i in range(len(self.extraImLabels)):
            if int(self.extraImLabels[i].eImIdx) == int(eImIdx):
                return i
        return _u.Token.NotDef.int_t

    def moveExtraIm(self, eImIdx, moveUp:bool):
        if moveUp:
            delta = -1
        else:
            delta = 1

        origFrameIdx = self.__findFrameIdxByEImIdx(eImIdx)

        newExtraImFrameIdx = origFrameIdx + delta

        if newExtraImFrameIdx < 0:
            return
        if newExtraImFrameIdx >= len(self.extraImLabels):
            return

        origEImIdx = int(self.extraImLabels[int(origFrameIdx)].eImIdx)
        newEImIdx = int(self.extraImLabels[int(newExtraImFrameIdx)].eImIdx)

        if origEImIdx == _u.Token.NotDef.int_t\
            or newEImIdx == _u.Token.NotDef.str_t:
            _u.log.autolog(f"Wrong extra image index from frame {origEImIdx} {newEImIdx}.")
            return

        fsf.Wr.SectionInfoStructure.moveExtraIm(self.subsection,
                                                self.imIdx,
                                                eImIdx = origEImIdx,
                                                destEimIdx = newEImIdx)

        self.updateExtraImage(origEImIdx)
        self.updateExtraImage(newEImIdx)

        return self.extraImLabels[int(newExtraImFrameIdx)]

    def __getImageResizeFactor(self, eImIdx = None):
        uiResizeEntryIdx = fsf.Data.Sec.imageUIResize(self.subsection)

        uiResizeEntryIdx = fsf.Data.Sec.imageUIResize(self.subsection)

        if eImIdx == None:
            if uiResizeEntryIdx.get(self.imIdx) != None:
                resizeFactor = float(uiResizeEntryIdx[self.imIdx])
            else:
                resizeFactor = 1.0
        else:
            if uiResizeEntryIdx.get(self.imIdx + "_" + str(eImIdx)) != None:
                resizeFactor = float(uiResizeEntryIdx[self.imIdx + "_" + str(eImIdx)])
            else:
                resizeFactor = 1.0
        return resizeFactor


    def __setMainImage(self, imPadLeft = 120):
        entryImagesFactory = EntryImagesFactory(self.subsection, self.imIdx)  
        imLabel = entryImagesFactory.produceEntryMainImageWidget(self.imagesFrame,
                                                            imPadLeft = imPadLeft,
                                                            resizeFactor = 1.0)

        imLabel.render()
        self.mainImLabel = imLabel


    def __setExtraImages(self, createExtraWidgets, imPadLeft = 0):
        def skipProofAndExtra(subsection, imIdx, exImIdx):
            extraImages = fsf.Data.Sec.extraImagesDict(subsection)[imIdx]
            eImText = extraImages[exImIdx]
            return (("proof" in eImText.lower())\
                    or (("proof" in eImText.lower()) and self.showAll))\
                    or (("extra") in eImText.lower())

        entryImagesFactory = EntryImagesFactory(self.subsection, self.imIdx)   
        exImLabels = entryImagesFactory.produceEntryExtraImagesWidgets(rootLabel = self.imagesFrame,
                                                        skippConditionFn = skipProofAndExtra,
                                                        createExtraWidgets = createExtraWidgets,
                                                        imPadLeft = imPadLeft)
        self.extraImLabels = exImLabels

        for l in exImLabels:
            l.render()

    def updateResizeEtrText(self, eImIdx = _u.Token.NotDef.str_t):
        if eImIdx == _u.Token.NotDef.str_t:
            newResizeFactor = fsf.Data.Sec.imageUIResize(self.subsection)[self.imIdx]
            self.uiResizeEtr.setData(newResizeFactor)
        else:
            newResizeFactor = fsf.Data.Sec.imageUIResize(self.subsection)[self.imIdx + "_" + str(eImIdx)]
            if self.extraImLabels[eImIdx].resizeEtr != None:
                self.extraImLabels[eImIdx].resizeEtr.setData(newResizeFactor)

    def showRow2(self):   
        self.rowFrame2.render()
        self.imagesShown = True   

    def hideRow2(self):
        self.rowFrame2.hide()
        self.imagesShown = False   

    def showImages(self, mainImPadLeft = 120, eImPadLeft = 0, createExtraImagesExtraWidgets = True):
        self.imagesShown = True   

        # if self.fullMoveWidget != None:
        #     self.fullMoveWidget.clicked = True 

        self.__setMainImage(imPadLeft = mainImPadLeft)
        self.__setExtraImages(createExtraWidgets = createExtraImagesExtraWidgets,
                              imPadLeft = eImPadLeft)
        self.imagesFrame.render()

    def setFullImageLabelNotClicked(self):
        if self.fullMoveWidget != None:
            self.fullMoveWidget.clicked = False 

    def remove(self):
        self.entryFrame.destroy()

    def hideImages(self):
        self.imagesShown = False
        for ch in self.imagesFrame.getChildren().copy():
            ch.destroy()
        self.imagesFrame.hide()
        self.setFullImageLabelNotClicked()

class EntryImagesFactory:
    class __ImageFrame(ww.currUIImpl.Frame):
        def __init__(self, imagePath, subsection, imIdx, 
                    row, column, columnspan,
                    prefix: str,
                    rootWidget,
                    extraOptions = {},
                    bindCmd = lambda *args: (None, None),
                    padding = [0, 0, 0, 0]): 
            renderData = {
                ww.Data.GeneralProperties_ID :{"column" : column, "row" : row, "columnspan" : columnspan},
                ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
            }
            self.subsection = subsection
            self.imIdx = imIdx
            self.imagePath = imagePath
            self.name = "_EntryImageFrame_"
            super().__init__(prefix, 
                            self.name,
                            rootWidget, 
                            renderData,
                            extraOptions,
                            bindCmd,
                            padding)


    class __MainImageFrame(__ImageFrame):
        def __init__(self, imagePath, subsection, imIdx, 
                    row, column, columnspan,
                    prefix: str,
                    rootWidget,
                    extraOptions = {},
                    bindCmd = lambda *args: (None, None),
                    padding = [0, 0, 0, 0]):
            self.subsection = subsection
            self.imIdx = imIdx
            self.imagePath = imagePath
            super().__init__(imagePath, subsection, imIdx, 
                            row, column, columnspan,
                            prefix,
                            rootWidget,
                            extraOptions,
                            bindCmd,
                            padding)

    class __ExtraImageFrame(__MainImageFrame):
        def __init__(self, imagePath, subsection, imIdx, eImIdx,
                    row, column, columnspan,
                    prefix: str,
                    rootWidget,
                    extraOptions = {},
                    bindCmd = lambda *args: (None, None),
                    padding = [0, 0, 0, 0]):
            self.eImIdx = eImIdx
            self.resizeEtr = None
            super().__init__(imagePath, subsection, imIdx, 
                            row, column, columnspan,
                            prefix,
                            rootWidget,
                            extraOptions,
                            bindCmd,
                            padding)

        # def changePosition(self, newImIdx):
        #     for ch in self.getChildren():
        #         print(ch.name)
        #         if "eImIdx" in dir(ch):
        #             ch.eImIdx = str(newImIdx)
        #     self.eImIdx = str(newImIdx)
        #     self.renderData["row"] = int(newImIdx) + 1


    def __getImageResizeFactor(self, eImIdx = None):
        uiResizeEntryIdx = fsf.Data.Sec.imageUIResize(self.subsection)

        uiResizeEntryIdx = fsf.Data.Sec.imageUIResize(self.subsection)

        if eImIdx == None:
            if uiResizeEntryIdx.get(self.imIdx) != None:
                resizeFactor = float(uiResizeEntryIdx[self.imIdx])
            else:
                resizeFactor = 1.0
        else:
            if uiResizeEntryIdx.get(self.imIdx + "_" + str(eImIdx)) != None:
                resizeFactor = float(uiResizeEntryIdx[self.imIdx + "_" + str(eImIdx)])
            else:
                resizeFactor = 1.0
        return resizeFactor

    def __init__(self, subsection, imIdx):
        self.imIdx = imIdx
        self.subsection = subsection

    def __getImageWidget(self, root, imagePath, widgetName, imIdx, subsection,
                    imPad = 0, imageSize = [450, 1000], 
                    row = 0, column = 0, columnspan = 1,
                    resizeFactor = 1.0,
                    bindOpenWindow = True,
                    extraImIdx = _u.Token.NotDef.int_t,
                    leftMove = 0):
        def openImageManager(event, tocBox = None, leftMove = 0, *args):
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

            imMenuManger.show([width, height, leftMove, 0], eImIdx, imHeight)

            if tocBox != None:
                tocBox.widgetToScrollTo = event.widget

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

            img = ww.currUIImpl.UIImage(pilIm)

            if bindOpenWindow:
                imLabel = TOCCanvasWithclick(root, imIdx = imIdx, subsection = subsection,
                                            prefix = widgetName, image = img, padding = [imPad, 0, 0, 0],
                                            row = row, column = column, columnspan = columnspan,
                                            extraImIdx = extraImIdx, 
                                            resizeFactor = 1 / resizeFactor,
                                            imagePath = imagePath,
                                            makeDrawable = False)
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

        if bindOpenWindow:
            imLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [lambda e, *args: openImageManager(e, leftMove = leftMove)])

        return imLabel
    
    def produceEntryMainImageWidget(self,
                                rootLabel,
                                imPadLeft,
                                mainImgBindData = None,
                                resizeFactor = 1.0,
                                row = 0,
                                columnspan = 100,
                                column = 0,
                                bindOpenWindow = True,
                                leftMove = 0):
        # mainImage
        resizeFactor *= self.__getImageResizeFactor()

        currBookName = sf.Wr.Manager.Book.getCurrBookName()
        imagePath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBookName,
                                                                       self.subsection,
                                                                       self.imIdx)

        mainWidgetName = _upan.Names.UI.getMainEntryWidgetName(self.subsection, self.imIdx)

        tempLabel = EntryImagesFactory.__MainImageFrame(subsection = self.subsection,
                                                  imIdx = self.imIdx,
                                                  imagePath = imagePath,
                                                  row = row, column = column, columnspan = columnspan,
                                                  prefix = mainWidgetName,
                                                  rootWidget = rootLabel,
                                                  padding = [imPadLeft, 0, 0, 0])

        if mainImgBindData != None:
            tempLabel.rebind(*mainImgBindData)
        
        if fsf.Data.Sec.textOnly(self.subsection).get(self.imIdx) != None:
            textOnly = fsf.Data.Sec.textOnly(self.subsection)[self.imIdx]

            if not textOnly:
                imLabel = self.__getImageWidget(tempLabel, imagePath, mainWidgetName, 
                                            self.imIdx, self.subsection, imPad = 0,
                                            row = 0, column = 1, columnspan = 1,
                                            resizeFactor = resizeFactor, bindOpenWindow = bindOpenWindow,
                                            leftMove = leftMove)
                imLabel.render()
            else:
                text = fsf.Data.Sec.imageText(self.subsection)[self.imIdx]
                imLabel = TOCTextWithClickTextOnlyEntry(tempLabel, 
                                            mainWidgetName,
                                            row = 0, column = 1, columnspan = 1,
                                            text = text,
                                            )
                imLabel.subsection = self.subsection
                imLabel.imIdx = self.imIdx
                imLabel.render()

                def __getText(widget):
                    return fsf.Data.Sec.imageText(widget.subsection)[widget.imIdx]

                def __setText(newText, widget):
                    imageText = fsf.Data.Sec.imageText(widget.subsection)
                    imageText[widget.imIdx] = newText
                    fsf.Data.Sec.imageText(widget.subsection, imageText)
                
                def __changeOnEtrFunc(widget):
                    for w in wd.Data.Reactors.entryChangeReactors.values():
                        if "onTextOnlyTextUpdate" in dir(w):
                            w.onTextOnlyTextUpdate()
                
                def __changeOnLabelBackFunc(widget):
                    for w in wd.Data.Reactors.entryChangeReactors.values():
                        if "onTextOnlyTextUpdate" in dir(w):
                            w.onTextOnlyTextUpdate()

                imLabel.rebind([ww.currUIImpl.Data.BindID.mouse2],
                               [lambda e, g = __getText, 
                                          s = __setText, 
                                          c = __changeOnEtrFunc, 
                                          b = __changeOnLabelBackFunc, *args:
                                                            bindWidgetTextUpdatable(e, g, s, 
                                                                changeOnEtrFunc = c,
                                                                changeOnLabelBackFunc = b)])

            if not fsf.Data.Sec.isVideo(self.subsection):
                bindOpenOMOnThePageOfTheImage(imLabel, self.subsection, self.imIdx)
            else:
                openVideoOnThePlaceOfTheImage(imLabel, self.subsection, self.imIdx)
        return tempLabel

    def __produceEntryExtraImageExtraLabels(self, eImIdx, parentLabel, resizeFactor):
        eImWidgetName = _upan.Names.UI.getExtraEntryWidgetName(self.subsection,
                                                            self.imIdx,
                                                            eImIdx)

        tempEImLabel = TOCLabelWithClick(parentLabel, 
                                                text = "",
                                                prefix = "tempLabel_" + eImWidgetName,
                                                row = 0,
                                                column = 0)

        removeEntry = TOCLabelWithClick(tempEImLabel,
                                        text = "[d]",
                                        prefix = "delete_" + eImWidgetName,
                                        row =  eImIdx + 5, 
                                        column = 0,
                                        sticky = ww.currUIImpl.Orientation.NW)
        removeEntry.imIdx = self.imIdx
        removeEntry.subsection = self.subsection
        removeEntry.eImIdx = eImIdx

        def delEIm(event, *args):
            widget:TOCLabelWithClick = event.widget
            fsf.Wr.SectionInfoStructure.removeExtraIm(widget.subsection,
                                                    widget.imIdx,
                                                    eImIdx = widget.eImIdx)
            
            currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            entryFsPath = _upan.Paths.Entry.ExtraImage.getAbs(currBookPath, 
                                                              widget.subsection,
                                                              widget.imIdx,
                                                              widget.eImIdx)

            counter = 0
            while ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryFsPath):
                time.sleep(0.3)
                counter += 1
                if counter > 50:
                    return

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onExtraImDelete" in dir(w):
                    w.onExtraImDelete(widget.subsection, widget.imIdx, widget.eImIdx)
                  

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
                                        row =  eImIdx + 5, 
                                        column = 1,
                                        sticky = ww.currUIImpl.Orientation.NW)
        moveEntryDown.imIdx = self.imIdx
        moveEntryDown.subsection = self.subsection
        moveEntryDown.eImIdx = eImIdx

        def moveDown(event, *args):
            widget:TOCLabelWithClick = event.widget
            
            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onExtraImMove" in dir(w):
                    w.onExtraImMove(widget.subsection, widget.imIdx, widget.eImIdx, False)

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
                                        row =  eImIdx + 5, 
                                        column = 2,
                                        sticky = ww.currUIImpl.Orientation.NW)
        moveEntryUp.imIdx = self.imIdx
        moveEntryUp.subsection = self.subsection
        moveEntryUp.eImIdx = eImIdx

        def moveUp(event, *args):
            widget:TOCLabelWithClick = event.widget
            
            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onExtraImMove" in dir(w):
                    w.onExtraImMove(widget.subsection, widget.imIdx, widget.eImIdx, True)

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
                                        row =  eImIdx + 5, 
                                        column = 3,
                                        sticky = ww.currUIImpl.Orientation.NW)
        retake.imIdx = self.imIdx
        retake.subsection = self.subsection
        retake.eImIdx = eImIdx

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
            figuresData = fsf.Data.Sec.figuresData(subsection)

            if figuresLabelsData.get(f"{imIdx}_{eImIdx}") != None:
                figuresLabelsData.pop(f"{imIdx}_{eImIdx}")
                fsf.Data.Sec.figuresLabelsData(subsection, figuresLabelsData)

            if figuresData.get(f"{imIdx}_{eImIdx}") != None:
                figuresData.pop(f"{imIdx}_{eImIdx}")
                fsf.Data.Sec.figuresData(subsection, figuresData)
            
            pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                wf.Wr.MenuManagers.PdfReadersManager)
            pdfReadersManager.show(subsection = subsection,
                                    imIdx = imIdx,
                                    selector = True,
                                    removePrevLabel = True,
                                    extraImIdx = eImIdx,
                                    withoutRender = True)
            def __cmdAfterImageCreated(imagePath, subsection, imIdx, eImIdx):
                timer = 0

                while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                    time.sleep(0.3)
                    timer += 1

                    if timer > 50:
                        break

                for w in wd.Data.Reactors.entryChangeReactors.values():
                    if "onRetakeAfter" in dir(w):
                        w.onRetakeAfter(subsection, imIdx, eImIdx)
                
            
            t = Thread(target = __cmdAfterImageCreated, args = [imagePath, subsection, imIdx, eImIdx])
            t.start()
            return

        retake.rebind([ww.currUIImpl.Data.BindID.mouse1],
                        [lambda e, *args: retakeCmd(e)])

        bindChangeColorOnInAndOut(retake)
        retake.render()

        def resizeEntryImgCMD(event, *args):
            resizeFactor = event.widget.getData()

            # check if the format is right
            if not re.match("^[0-9]\.[0-9]$", resizeFactor):
                _u.log.autolog(\
                    f"The format of the resize factor '{resizeFactor}'is not correct")
                return
            
            subsection = event.widget.subsection
            imIdx = event.widget.imIdx
            eImIdx = event.widget.eImIdx
            
            uiResizeEntryIdx = fsf.Data.Sec.imageUIResize(subsection)

            if (uiResizeEntryIdx == None) \
                or (uiResizeEntryIdx == _u.Token.NotDef.dict_t):
                uiResizeEntryIdx = {}

            uiResizeEntryIdx[str(imIdx) + "_" + str(eImIdx)] = resizeFactor

            fsf.Data.Sec.imageUIResize(subsection, uiResizeEntryIdx)

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onImageResize" in dir(w):
                    w.onImageResize(subsection, imIdx, event.widget.eImIdx)

            excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                            wf.Wr.MenuManagers.ExcerciseManager)
            if excerciseManager.shown:
                excerciseManager.show()

        changeImSize = ImageSize_ETR(tempEImLabel,
                                    prefix =  "imSize_" + eImWidgetName,
                                    row = eImIdx + 5, 
                                    column = 4,
                                    imIdx = self.imIdx,
                                    text = resizeFactor)
        changeImSize.imIdx = self.imIdx
        changeImSize.eImIdx = eImIdx
        changeImSize.subsection = self.subsection
        changeImSize.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                [lambda e, *args: resizeEntryImgCMD(e)])
        changeImSize.render()
        parentLabel.resizeEtr = changeImSize

        bookCodeProj = TOCLabelWithClick(tempEImLabel,
                                        text = "code: [b",
                                        prefix = "bookCodeProj_" + eImWidgetName,
                                        row =  eImIdx + 6, 
                                        column = 0,
                                        sticky = ww.currUIImpl.Orientation.NE,
                                        columnspan = 3)
        bookCodeProj.imIdx = self.imIdx
        bookCodeProj.subsection = self.subsection
        bookCodeProj.eImIdx = eImIdx

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
                                        row =  eImIdx + 6, 
                                        column = 3,
                                        sticky = ww.currUIImpl.Orientation.NW,
                                        columnspan = 1)
        subsectionCodeProj.imIdx = self.imIdx
        subsectionCodeProj.subsection = self.subsection
        subsectionCodeProj.eImIdx = eImIdx

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
                                        row =  eImIdx + 6, 
                                        column = 4,
                                        sticky = ww.currUIImpl.Orientation.NW,
                                        columnspan = 1)
        entryCodeProj.imIdx = self.imIdx
        entryCodeProj.subsection = self.subsection
        entryCodeProj.eImIdx = eImIdx

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
                                        row =  eImIdx + 7, 
                                        column = 0,
                                        sticky = ww.currUIImpl.Orientation.NW,
                                        columnspan = 2)
        addProof.imIdx = self.imIdx
        addProof.subsection = self.subsection
        addProof.eImIdx = eImIdx

        def addExtraImProofCmd(event, *args):
            widget = event.widget
            addExtraIm(widget.subsection, widget.imIdx, 
                        True, event = event)

        addProof.rebind([ww.currUIImpl.Data.BindID.mouse1],
                        [lambda e, *args: addExtraImProofCmd(e)])
        bindChangeColorOnInAndOut(addProof)
        addProof.render()

        addEIm = TOCLabelWithClick(tempEImLabel,
                                        text = ", AddImage]",
                                        prefix = "addEIm_" + eImWidgetName,
                                        row =  eImIdx + 7, 
                                        column = 2,
                                        sticky = ww.currUIImpl.Orientation.NW,
                                        columnspan = 3)
        addEIm.imIdx = self.imIdx
        addEIm.subsection = self.subsection
        addEIm.eImIdx = eImIdx

        def addExtraImCmd(event, *args):
            widget = event.widget
            addExtraIm(widget.subsection, widget.imIdx, 
                        False, event = event)

        addEIm.rebind([ww.currUIImpl.Data.BindID.mouse1],
                        [lambda e, *args: addExtraImCmd(e)])
        bindChangeColorOnInAndOut(addEIm)
        addEIm.render()

        return tempEImLabel

    def produceEntryExtraImageFrame(self,
                                    rootLabel,
                                    eImIdx,
                                    createExtraWidgets,
                                    bindOpenWindow,
                                    resizeFactor,
                                    imPadLeft,
                                    leftMove):
        currBookName = sf.Wr.Manager.Book.getCurrBookName()

        uiResizeEntryIdx = fsf.Data.Sec.imageUIResize(self.subsection)
        shouldResetResizeFactor = False

        if (str(self.imIdx) + "_" + str(eImIdx)) in list(uiResizeEntryIdx.keys()):
            resizeFactor *= float(uiResizeEntryIdx[self.imIdx + "_" + str(eImIdx)])
        else:
            resizeFactor *= 1.0

        extraImFilepath = _upan.Paths.Screenshot.Images.getExtraEntryImageAbs(currBookName,
                                                                            self.subsection,
                                                                            self.imIdx,
                                                                            eImIdx)

        eImWidgetName = _upan.Names.UI.getExtraEntryWidgetName(self.subsection,
                                                            self.imIdx,
                                                            eImIdx)

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
            event.widget.hide()

            def __getBack(eimLabel, widget):
                newText = eimLabel.getData()
                eImTextDict = fsf.Data.Sec.extraImagesDict(eimLabel.subsection)
                eImTextList = eImTextDict[eimLabel.imIdx]
                eImTextList[eimLabel.eImIdx] = newText
                fsf.Data.Sec.extraImagesDict(eimLabel.subsection, eImTextDict)
                
                eimLabel.hide()
                widget.render()

            eimLabel.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                                                        [lambda *args: __getBack(eimLabel, event.widget)])
            eimLabel.render()

        #NOTE: we add one since we have main image already
        mainRow = int(eImIdx) + 1

        extraImFrame = EntryImagesFactory.__ExtraImageFrame(extraImFilepath,
                                                            self.subsection,
                                                            self.imIdx,
                                                            eImIdx,
                                                            row = mainRow, column = 0, columnspan = 1,
                                                            rootWidget = rootLabel, 
                                                            prefix = eImWidgetName,
                                                            padding = [imPadLeft, 0, 0, 0])

        eImLabel = self.__getImageWidget(extraImFrame, extraImFilepath, eImWidgetName, 
                                    self.imIdx, self.subsection, imPad = 0,
                                    row = 0, column = 1, columnspan = 1,
                                    resizeFactor = resizeFactor,
                                    extraImIdx = eImIdx,
                                    bindOpenWindow = bindOpenWindow,
                                    leftMove = leftMove)
        eImLabel.subsection = self.subsection
        eImLabel.imIdx = self.imIdx
        eImLabel.eImIdx = eImIdx

        bindOpenOMOnThePageOfTheImage(eImLabel, self.subsection, self.imIdx, str(eImIdx))
        eImLabel.rebind([ww.currUIImpl.Data.BindID.mouse2],
                        [extraImtextUpdate])
        eImLabel.render()
        

        if createExtraWidgets:
            extraImExtraWidgets = self.__produceEntryExtraImageExtraLabels(eImIdx = eImIdx, 
                                                                    parentLabel = extraImFrame,
                                                                    resizeFactor = resizeFactor)
            extraImExtraWidgets.render()

        if shouldResetResizeFactor:
            resizeFactor = None
            shouldResetResizeFactor = False

        return extraImFrame

    def produceEntryExtraImagesWidgets(self,
                                rootLabel,
                                skippConditionFn = lambda *args: False,
                                createExtraWidgets = True,
                                bindOpenWindow = True,
                                resizeFactor = 1.0,
                                imPadLeft = 0,
                                leftMove = 0):
        outLabels = []

        # extraImages
        if self.imIdx in list(fsf.Data.Sec.extraImagesDict(self.subsection).keys()):
            extraImages = fsf.Data.Sec.extraImagesDict(self.subsection)[self.imIdx]

            for eImIdx in range(0, len(extraImages)):
                if skippConditionFn(self.subsection, self.imIdx, eImIdx):
                    continue
                else:
                    #NOTE: this allows to have extra images to have separate roots
                    rl = rootLabel[eImIdx] if type(rootLabel) == list else rootLabel

                    extraImFrame = self.produceEntryExtraImageFrame(rl,
                                                                    eImIdx,
                                                                    createExtraWidgets,
                                                                    bindOpenWindow,
                                                                    resizeFactor,
                                                                    imPadLeft = imPadLeft,
                                                                    leftMove = leftMove)
                    extraImFrame.render()
                    outLabels.append(extraImFrame)

        return outLabels


class LinksFrameManager:
    def __init__(self, subsection, imIdx, linksFrame, linksFactory):
        self.imIdx = imIdx
        self.subsection = subsection
        self.linksFrame = linksFrame
        self.factory = linksFactory

        self.linksShown = False

        self.entriesFrame = None

    def processChangeLinksViewStatusChange(self):
        if not self.linksShown:
            self.factory.produceLinksEntryFrames()
            self.linksFrame.render()
        else:
            self.linksFrame.hide()
        
        self.linksShown = not self.linksShown

    def showLinks(self):
        self.factory.produceLinksEntryFrames()
        self.linksFrame.render()
        self.linksShown = True
        for w in wd.Data.Reactors.entryChangeReactors.values():
            if "onShowLinks" in dir(w):
                w.onShowLinks()

class LinksFrameFactory:
    def __init__(self, subsection, imIdx):
        self.imIdx = imIdx
        self.subsection = subsection
        self.manager = None
    
    def produceMainFrame(self, parentWidget, row, leftPad):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : row, "columnspan" : 100},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        name = "_LinksFrame_"
        self.prefix =  _upan.Names.Entry.getEntryNameID(self.subsection, self.imIdx)

        return ww.currUIImpl.Frame(prefix = self.prefix,
                                   name = name, 
                                   rootWidget = parentWidget,
                                   renderData = renderData,
                                   padding = [leftPad, 0, 0, 0])
    def produceLinksMainWidgets(self, haveLinks):
        linksPrefixLabel = TOCLabelWithClick(root = self.manager.linksFrame, 
                                text =  "Links: " if haveLinks else "No links", 
                                prefix = "contentLinksIntroFr_" + self.prefix,
                                padding = [60, 0, 0, 0],
                                row = 0, column = 0)
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 1, "columnspan" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        linksEntriesFrame = ww.currUIImpl.Frame(prefix = self.prefix,
                                               name = "contentLinksEntriesFr_",
                                               rootWidget = self.manager.linksFrame,
                                               renderData = renderData,
                                               padding = [60, 0, 0, 0])
        return linksPrefixLabel, linksEntriesFrame

    def __produceLinksEntryFrame(self, parentWidget, linkSubsection, linksImIdx, row):
        entryFrameFactory = EntryWidgetFactoryLink(linkSubsection, linksImIdx, 0, 0, 
                                                   sourceSubsection = self.subsection, 
                                                   sourceImIdx = self.imIdx)
        entryFrameFactory.produceEntryWidgetsForFrame(parentWidget, row)
        entryWidgetManager = entryFrameFactory.entryFrameManager
        return entryWidgetManager
    
    def __produceLinksWebLinkFrame(self, parentWidget, subsection, imIdx, webLinkName, row):
        entryFrameFactory = EntryWidgetFactoryWebLink(subsection = subsection, 
                                                      imIdx = imIdx,
                                                      topPad = 0,
                                                      leftPad = 0,
                                                      webLinkName = webLinkName)
        entryFrameFactory.produceEntryWidgetsForFrame(parentWidget, row)
        entryWidgetManager = entryFrameFactory.entryFrameManager
        return entryWidgetManager
       

    def produceLinksEntryFrames(self):
        if fsf.Data.Sec.imGlobalLinksDict(self.subsection).get(self.imIdx) == None:
            return

        glLinks:dict = fsf.Data.Sec.imGlobalLinksDict(self.subsection)[self.imIdx].copy()

        # NOTE: should put all the links into 
        # one frame. This way they will be aligned correctly
        if type(glLinks) == dict:
            row = 0
            for ln, lk in glLinks.items():
                if "KIK" in lk:
                    targetSubsection = ln.split("_")[0]
                    targetImIdx = ln.split("_")[1]
                    self.__produceLinksEntryFrame(self.manager.entriesFrame, 
                                                  targetSubsection, 
                                                  targetImIdx,
                                                  row)
                elif "http" in lk:
                    self.__produceLinksWebLinkFrame(self.manager.entriesFrame, 
                                                  self.subsection, 
                                                  self.imIdx, 
                                                  ln,
                                                  row)
                    
                row += 1

    def produceLinksFrame(self, parentWidget, row, leftPad):
        linksFrame = self.produceMainFrame(parentWidget = parentWidget,
                                           row = row, 
                                           leftPad = leftPad)
        self.manager = LinksFrameManager(self.subsection, self.imIdx, linksFrame, self)

        imGlobalLinksDict = fsf.Data.Sec.imGlobalLinksDict(self.subsection)
        haveLinks = self.imIdx in imGlobalLinksDict.keys()

        linksPrefixLabel, linksEntriesFrame = self.produceLinksMainWidgets(haveLinks)
        linksPrefixLabel.render()
        linksEntriesFrame.render()
        self.manager.entriesFrame = linksEntriesFrame


class EntryWidgetFactory:
    class EntryUIs:
        class __EntryUIData:
            def __init__(self, name, column, cmd, row = 0) -> None:
                self.name = name
                self.column = column
                self.row = row
                self.cmd = cmd

        def __init__(self):
            raise NotImplementedError()

    def __init__(self, subsection, imIdx, topPad, leftPad):
        self.subsection = subsection
        self.imIdx = imIdx
        self.frame = None
        self.__nameIdPrefix = _upan.Names.Entry.getEntryNameID(self.subsection, self.imIdx)
        self.EntryUIs = self.EntryUIs()

        self.topPad = topPad
        self.leftPad = leftPad

        self.entryFrameManager = None

    def getPrefixID(self):
        return self.__nameIdPrefix

    def produceShiftLabelWidget(self, parentWidget):
        def shiftEntryCmd(event, *args):
            widget = event.widget
            fsf.Wr.SectionInfoStructure.shiftEntryUp(widget.subsection,
                                                        widget.imIdx)
            
            fsf.Data.Book.subsectionOpenInTOC_UI = self.subsection
            fsf.Data.Book.entryImOpenInTOC_UI = str(int(widget.imIdx) + 1)
            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onEntryShift" in dir(w):
                    w.onEntryShift(widget.subsection, widget.imIdx)

        shiftEntry = TOCLabelWithClick(parentWidget,
                                                text = self.EntryUIs.shift.name,
                                                prefix = "contentShiftEntry" + self.__nameIdPrefix,
                                                row = self.EntryUIs.shift.row, 
                                                column = self.EntryUIs.shift.column)
        shiftEntry.imIdx = self.imIdx
        shiftEntry.subsection = self.subsection
        shiftEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [shiftEntryCmd])
        bindChangeColorOnInAndOut(shiftEntry)
        return shiftEntry

    def produceLeadingEntryEtrWidget(self, parentWidget):
        def changeLeadingEntryCmd(event, subsection, imIdx,  *args):
            widget = event.widget

            leadingEntryIdx = widget.getData()

            leadingEntry = fsf.Data.Sec.leadingEntry(subsection)

            if str(leadingEntryIdx) == _u.Token.NotDef.str_t:
                if leadingEntry.get(imIdx) != None:
                    leadingEntry.pop(imIdx)
            else:
                leadingEntry[imIdx] = leadingEntryIdx

            fsf.Data.Sec.leadingEntry(subsection, leadingEntry)
            
            imagesGroupDict = fsf.Data.Sec.imagesGroupDict(subsection)

            if str(leadingEntryIdx) == _u.Token.NotDef.str_t:
                imagesGroupDict[imIdx] = 0
            else:
                imagesGroupDict[imIdx] = imagesGroupDict[leadingEntryIdx]

            fsf.Data.Sec.imagesGroupDict(subsection, imagesGroupDict)

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onSetLeadingEntry" in dir(w):
                    w.onSetLeadingEntry(widget.subsection, widget.imIdx)

        leadingEntryText = _u.Token.NotDef.str_t

        if fsf.Data.Sec.leadingEntry(self.subsection).get(self.imIdx) != None:
            leadingEntryIdx = fsf.Data.Sec.leadingEntry(self.subsection)[self.imIdx]

            leadingEntryText = leadingEntryIdx

        leadingEntry = ImageSize_ETR(parentWidget,
                                            prefix = "leadingEntry_" + self.__nameIdPrefix,
                                            row = 0, 
                                            column = self.EntryUIs.leadingEntry.column,
                                            imIdx = self.imIdx,
                                            text = leadingEntryText)
        
        leadingEntry.imIdx = self.imIdx
        leadingEntry.subsection = self.subsection
        leadingEntry.rebind([ww.currUIImpl.Data.BindID.Keys.shenter],
                                [lambda e, *args: changeLeadingEntryCmd(e, self.subsection, self.imIdx)])
        return leadingEntry

    def produceChangeImSizeWidget(self, parentWidget):
        def resizeEntryImgCMD(event, *args):
            resizeFactor = event.widget.getData()

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
            msg = f"After resize of {subsection} {imIdx}"
            ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onImageResize" in dir(w):
                    w.onImageResize(subsection, imIdx, None)

        uiResizeEntryIdx = fsf.Data.Sec.imageUIResize(self.subsection)

        if self.imIdx in list(uiResizeEntryIdx.keys()):
            resizeFactor = float(uiResizeEntryIdx[self.imIdx])
        else:
            resizeFactor = 1.0

        changeImSize = ImageSize_ETR(parentWidget,
                                        prefix = "contentUpdateEntryText" + self.__nameIdPrefix,
                                        row = 0, 
                                        column = self.EntryUIs.changeImSize.column,
                                        imIdx = self.imIdx,
                                        text = resizeFactor)
        changeImSize.imIdx = self.imIdx
        changeImSize.subsection = self.subsection
        changeImSize.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                [resizeEntryImgCMD])
        return changeImSize

    def produceRemoveEntryWidget(self, parentWidget):
        def removeEntryCmd(event, *args):
            widget = event.widget
            fsf.Wr.SectionInfoStructure.removeEntry(widget.subsection, widget.imIdx)

            def __afterDeletion(subsection, imIdx, *args):
                timer = 0
                while fsf.Data.Sec.figuresLabelsData(subsection).get(imIdx) != None:
                    time.sleep(0.3)
                    timer += 1
                    if timer > 50:
                        break

                for w in wd.Data.Reactors.entryChangeReactors.values():
                    if "onEntryDelete" in dir(w):
                        w.onEntryDelete(subsection, imIdx)

            t = Thread(target = __afterDeletion, args = [widget.subsection, widget.imIdx])
            t.start()

        removeEntry = TOCLabelWithClick(parentWidget,
                                        text = self.EntryUIs.delete.name,
                                        prefix = "contentRemoveEntry" + self.__nameIdPrefix,
                                        row = 0, 
                                        column = self.EntryUIs.delete.column)
        removeEntry.imIdx = self.imIdx
        removeEntry.subsection = self.subsection
        removeEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [removeEntryCmd])
        bindChangeColorOnInAndOut(removeEntry)
        return removeEntry

    def produceCopyEntryWidget(self, parentWidget):
        def copyEntryCmd(event, *args):
            widget = event.widget

            dt.UITemp.Copy.subsection = widget.subsection
            dt.UITemp.Copy.imIdx = widget.imIdx
            dt.UITemp.Copy.cut = False

        def cutEntryCmd(event, *args):
            widget = event.widget

            dt.UITemp.Copy.subsection = widget.subsection
            dt.UITemp.Copy.imIdx = widget.imIdx
            dt.UITemp.Copy.cut = True

        copyEntry = TOCLabelWithClick(parentWidget,
                                                text = self.EntryUIs.copy.name,
                                                prefix = "contentCopyEntry" + self.__nameIdPrefix,
                                                row = 0, 
                                                column = self.EntryUIs.copy.column)
        copyEntry.imIdx = self.imIdx
        copyEntry.subsection = self.subsection
        copyEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [copyEntryCmd])
        copyEntry.rebind([ww.currUIImpl.Data.BindID.shmouse1],
                            [cutEntryCmd])

        bindChangeColorOnInAndOut(copyEntry)
        return copyEntry

    def producePasteEntryWidget(self, parentWidget):
        def pasteEntryCmd(event, *args):
            widget = event.widget

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onPaste" in dir(w):
                    w.onPaste(widget.subsection, widget.imIdx)

        pasteAfterEntry = TOCLabelWithClick(parentWidget,
                                                text = self.EntryUIs.pasteAfter.name,
                                                prefix = "contentPasteAfterEntry" + self.__nameIdPrefix,
                                                row = 0, 
                                                column = self.EntryUIs.pasteAfter.column)
        pasteAfterEntry.imIdx = self.imIdx
        pasteAfterEntry.subsection = self.subsection

        pasteAfterEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [pasteEntryCmd])        
        bindChangeColorOnInAndOut(pasteAfterEntry) 

        return pasteAfterEntry

    def produceShowLinksForEntry(self, parentWidget):
        def showLinksForEntryCmd(e, manager):
            linksFrmaeManger = manager.linksFrameManager
            linksFrmaeManger.processChangeLinksViewStatusChange()        

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onLinksShow" in dir(w):
                    w.onLinksShow(e.widget.subsection, e.widget.imIdx)

        showLinksForEntry = TOCLabelWithClick(parentWidget,
                                                text = self.EntryUIs.showLinks.name,
                                                prefix = "contentShowLinksForEntry" + self.__nameIdPrefix,
                                                row = 0, 
                                                column = self.EntryUIs.showLinks.column)
        showLinksForEntry.imIdx = self.imIdx
        showLinksForEntry.subsection = self.subsection

        showLinksForEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                    [lambda e, lf = self.entryFrameManager, *args: showLinksForEntryCmd(e, lf)])

        linkExist = self.imIdx in list(fsf.Data.Sec.imGlobalLinksDict(self.subsection).keys())

        if linkExist:
            showLinksForEntry.changeColor("brown")

        bindChangeColorOnInAndOut(showLinksForEntry, shouldBeBrown = linkExist)
        return showLinksForEntry

    def produceShowProof(self, parentWidget):
        def openProofsMenu(event, *args):
            prMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.ProofsManager)

            event.widget.shouldShowProofMenu = not event.widget.shouldShowProofMenu

            if (event.widget.shouldShowProofMenu):
                prMenuManger.show(subsection =  event.widget.subsection, imIdx = event.widget.imIdx)
            else:
                prMenuManger.hide(subsection =  event.widget.subsection, imIdx = event.widget.imIdx)

        tarOpenProofsUIEntry = TOCLabelWithClick(parentWidget, 
                                    text = self.EntryUIs.proof.name, 
                                    prefix = "contentGlLinksTSubsectionProof_" + self.__nameIdPrefix,
                                    row = 0, 
                                    column = 5)
        tarOpenProofsUIEntry.changeColor("brown")

        tarOpenProofsUIEntry.imIdx = self.imIdx
        tarOpenProofsUIEntry.subsection = self.subsection
        tarOpenProofsUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                    [openProofsMenu])
        bindChangeColorOnInAndOut(tarOpenProofsUIEntry)
        return tarOpenProofsUIEntry

    def produceCopyTextToMemWidget(self, parentWidget):
        def copyTextToMemCmd(event, *args):
            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onCopyTextToMem" in dir(w):
                    w.onCopyTextToMem(event.widget.subsection, event.widget.imIdx)

        copyTextToMem = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.copyText.name, 
                                        prefix = "contentCopyTextToMem" + self.__nameIdPrefix,
                                        row = self.EntryUIs.copyText.row, 
                                        column = self.EntryUIs.copyText.column,
                                        columnspan = 1)
        copyTextToMem.imIdx = self.imIdx
        copyTextToMem.subsection = self.subsection
        copyTextToMem.rebind([ww.currUIImpl.Data.BindID.mouse1],
                             [copyTextToMemCmd])
        bindChangeColorOnInAndOut(copyTextToMem)
        return copyTextToMem

    def produceRetakeImageWidget(self, parentWidget):
        def retakeImageCmd(event, *args):
            widget = event.widget
            subsection = widget.subsection
            imIdx = widget.imIdx

            currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            
            msg = "Do you want to retake entry image?"
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

            if not response:
                return

            imagePath = _upan.Paths.Screenshot.Images.getMainEntryImageAbs(currBookPath,
                                                                        subsection,
                                                                        str(imIdx))
            ocf.Wr.FsAppCalls.deleteFile(imagePath)
            figuresLabelsData = fsf.Data.Sec.figuresLabelsData(subsection)
            figuresData = fsf.Data.Sec.figuresData(subsection)

            if figuresLabelsData.get(str(imIdx)) != None:
                figuresLabelsData.pop(str(imIdx))
            
            if figuresData.get(str(imIdx)) != None:
                figuresData.pop(str(imIdx))
            

            fsf.Data.Sec.figuresLabelsData(subsection, figuresLabelsData)
            fsf.Data.Sec.figuresData(subsection, figuresData)

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onRetakeBefore" in dir(w):
                    w.onRetakeBefore(subsection, imIdx)

            def __cmdAfterImageCreated(subsection, imIdx):
                timer = 0

                while not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                    time.sleep(0.3)
                    timer += 1

                    if timer > 50:
                        break
                
                
                for w in wd.Data.Reactors.entryChangeReactors.values():
                    if "onRetakeAfter" in dir(w):
                        w.onRetakeAfter(subsection, imIdx)

            t = Thread(target = __cmdAfterImageCreated, args = [subsection, imIdx])
            t.start()

        retakeImageForEntry = TOCLabelWithClick(parentWidget,
                                                text =  self.EntryUIs.retake.name,
                                                prefix = "contentRetakeImageForEntry" + self.__nameIdPrefix,
                                                row = 0, 
                                                column =  self.EntryUIs.retake.column)
        retakeImageForEntry.imIdx = self.imIdx
        retakeImageForEntry.subsection = self.subsection
        retakeImageForEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                    [retakeImageCmd])
        bindChangeColorOnInAndOut(retakeImageForEntry)
        return retakeImageForEntry

    def produceAddExtraImageWidget(self, parentWidget):
        def addExtraImCmd(event, *args):
            widget = event.widget
            addExtraIm(widget.subsection, widget.imIdx, False)

        addExtraImage = TOCLabelWithClick(parentWidget, 
                                            text = self.EntryUIs.addExtra.name,
                                            prefix = "contentAddExtraImageEntry" + self.__nameIdPrefix,
                                            row = 0, 
                                            column = self.EntryUIs.addExtra.column)
        addExtraImage.imIdx = self.imIdx
        addExtraImage.subsection = self.subsection
        addExtraImage.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [addExtraImCmd])
        bindChangeColorOnInAndOut(addExtraImage)
        return addExtraImage

    def produceAddProofImageWidget(self, parentWidget):
        def addExtraImProofCmd(event, *args):
            widget = event.widget
            addExtraIm(widget.subsection, widget.imIdx, True)

        addProofImage = TOCLabelWithClick(parentWidget, 
                                            text = self.EntryUIs.addProof.name,
                                            prefix = "contentAddExtraProofEntry" + self.__nameIdPrefix,
                                            row = 0, 
                                            column = self.EntryUIs.addProof.column)
        addProofImage.imIdx = self.imIdx
        addProofImage.subsection = self.subsection
        addProofImage.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [addExtraImProofCmd])
        bindChangeColorOnInAndOut(addProofImage)
        return addProofImage

    def produceCopyLinkWidget(self, parentWidget):
        def copyGlLinkCmd(event, *args):
            widget = event.widget
            dt.UITemp.Link.subsection = widget.subsection
            dt.UITemp.Link.imIdx = widget.imIdx
        
        copyLinkEntry = TOCLabelWithClick(parentWidget, 
                                            text = self.EntryUIs.copyLink.name,
                                            prefix = "contentCopyGlLinkEntry" + self.__nameIdPrefix,
                                            row = 0, 
                                            column = self.EntryUIs.copyLink.column)
        copyLinkEntry.imIdx = self.imIdx
        copyLinkEntry.subsection = self.subsection
        copyLinkEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [copyGlLinkCmd])
        bindChangeColorOnInAndOut(copyLinkEntry)
        return copyLinkEntry
    
    def producePasteLinkEntryWidget(self, parentWidget):
        def pasteGlLinkCmd(event, *args):
            widget = event.widget
            sourceSubsection = widget.subsection
            sourceTopSection = sourceSubsection.split(".")[0]
            sourceImIdx = widget.imIdx
            targetSubsection = dt.UITemp.Link.subsection
            targetImIdx = dt.UITemp.Link.imIdx

            excerciseManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.ExcerciseManager)
            excerciseWidgetShown = excerciseManager.shown

            if targetSubsection != _u.Token.NotDef.str_t\
                and targetImIdx != _u.Token.NotDef.str_t:
                gm.GeneralManger.AddLink(f"{targetSubsection}.{targetImIdx}",
                                        sourceSubsection,
                                        sourceImIdx,
                                        sourceTopSection)

            if excerciseWidgetShown:
                excerciseManager.show()
            
            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onPasteLink" in dir(w):
                    w.onPasteLink()


        pasteLinkEntry = TOCLabelWithClick(parentWidget,
                                            text = self.EntryUIs.pasteLink.name,
                                            prefix = "contentPasteGlLinkEntry" + self.__nameIdPrefix,
                                            row = 0, 
                                            column = self.EntryUIs.pasteLink.column)
        pasteLinkEntry.imIdx = self.imIdx
        pasteLinkEntry.subsection = self.subsection
        pasteLinkEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [pasteGlLinkCmd])
        bindChangeColorOnInAndOut(pasteLinkEntry)
        return pasteLinkEntry

    def produceOpenExcercisesWidget(self, parentWidget):
        def openExcerciseMenu(event, *args):
            exMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.ExcerciseManager)
            exMenuManger.subsection = event.widget.subsection
            exMenuManger.imIdx = event.widget.imIdx

            event.widget.shouldShowExMenu = not event.widget.shouldShowExMenu

            if (event.widget.shouldShowExMenu):
                exMenuManger.show()
            else:
                exMenuManger.hide()

        openExUIEntry = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.excercises.name, 
                                        prefix = "contentOpenExcerciseUIEntry" + self.__nameIdPrefix,
                                        row = 0, 
                                        column = self.EntryUIs.excercises.column,
                                        columnspan = 1)
        openExUIEntry.imIdx = self.imIdx
        openExUIEntry.subsection = self.subsection
        openExUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openExcerciseMenu])
        
        fullPathToEntryJSON = _upan.Paths.Entry.JSON.getAbs(sf.Wr.Manager.Book.getCurrBookFolderPath(),
                                                            self.subsection, self.imIdx)
        entryStructureExists = ocf.Wr.FsAppCalls.checkIfFileOrDirExists(fullPathToEntryJSON)

        #TODO: should probably change to something else since the structure might exist but no excercises present.
        excerciseExists = False
        if entryStructureExists:
            entryLinesList = fsf.Wr.EntryInfoStructure.readProperty(self.subsection, self.imIdx, 
                                                   fsf.Wr.EntryInfoStructure.PubProp.entryLinesList)
            if (entryLinesList != _u.Token.NotDef.list_t) and (entryLinesList != []):
                excerciseExists = True
        if excerciseExists:
            openExUIEntry.changeColor("brown")
        bindChangeColorOnInAndOut(openExUIEntry, shouldBeBrown = excerciseExists)
        return openExUIEntry

    def produceMainImageWidget(self, parentWidget, leftPad = 60, column = 0):
        def updateEntry(event, *args):
            def __getText(widget):
                imLinkDict = fsf.Data.Sec.imLinkDict(widget.subsection)
                text = imLinkDict[widget.imIdx]
                return text

            def __setText(newText, widget):
                imLinkDict = fsf.Data.Sec.imLinkDict(widget.subsection)
                imLinkDict[widget.imIdx] = newText
                fsf.Data.Sec.imLinkDict(widget.subsection, imLinkDict)
            
            def __updateImage(widget):
                textOnly = fsf.Data.Sec.textOnly(widget.subsection)[widget.imIdx]
                imLinkDict = fsf.Data.Sec.imLinkDict(widget.subsection)
                text = imLinkDict[widget.imIdx]
                fsf.Wr.SectionInfoStructure.rebuildEntryLatex(widget.subsection,
                                                            widget.imIdx,
                                                            text,
                                                            textOnly
                                                            )

                for w in wd.Data.Reactors.entryChangeReactors.values():
                    if "onMainLatexImageUpdate" in dir(w):
                        w.onMainLatexImageUpdate(widget.subsection, widget.imIdx)

            def __changeOnEtrFunc(widget):
                for w in wd.Data.Reactors.entryChangeReactors.values():
                    if "onEntryTextUpdate" in dir(w):
                        w.onEntryTextUpdate()
            
            def __changeOnLabelBackFunc(widget):
                for w in wd.Data.Reactors.entryChangeReactors.values():
                    if "onEntryTextUpdate" in dir(w):
                        w.onEntryTextUpdate()
            
            bindWidgetTextUpdatable(event, __getText, __setText, __updateImage, 
                                                      __changeOnEtrFunc, __changeOnLabelBackFunc)


        if fsf.Data.Sec.imLinkDict(self.subsection).get(self.imIdx) != None:
            v = fsf.Data.Sec.imLinkDict(self.subsection)[self.imIdx]

            latexTxt = tff.Wr.TexFileUtils.fromEntryToLatexTxt(self.imIdx, v)
            pilIm = getEntryImg(latexTxt, self.subsection, self.imIdx)

            shrink = 0.7
            pilIm.thumbnail([int(pilIm.size[0] * shrink),int(pilIm.size[1] * shrink)], Image.LANCZOS)
            img = ww.currUIImpl.UIImage(pilIm)

            textLabelPage = TOCLabelWithClickEntry(parentWidget,
                                            image = img, 
                                            prefix = "contentP_" + self.__nameIdPrefix, 
                                            padding= [leftPad, 0, 0, 0],
                                            row = 0, 
                                            column = column)
            textLabelPage.imIdx = self.imIdx
            textLabelPage.subsection = self.subsection
            textLabelPage.etrWidget = textLabelPage
            textLabelPage.imageLineIdx = int(self.imIdx)
            textLabelPage.entryText = v
            textLabelPage.imagePath = v

            textLabelPage.rebind([ww.currUIImpl.Data.BindID.mouse2],
                                    [updateEntry])
            
            bindOpenOMOnThePageOfTheImage(textLabelPage, textLabelPage.subsection, textLabelPage.imIdx)
            textLabelPage.image = img
        else:
            textLabelPage = TOCLabelWithClickEntry(parentWidget,
                                                text = _u.Token.NotDef.str_t, 
                                                prefix = "contentP_" + self.__nameIdPrefix, 
                                                padding= [leftPad, 0, 0, 0],
                                                row = 0, 
                                                column = column)

        self.entryFrameManager.latexEntryImage = textLabelPage
        return textLabelPage

    def produceOpenSecondaryImageWidget(self, parentWidget):
        def openSecondaryImage(widget):
            def __cmd(event = None, *args):
                widget = event.widget
                imIdx = widget.imIdx
                subsection = widget.subsection

                for w in wd.Data.Reactors.entryChangeReactors.copy().values():
                    if "onSecondaryImageOpen" in dir(w):
                        w.onSecondaryImageOpen(subsection, imIdx)
            
            widget.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])

        textLabelFull = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.im.name, 
                                        prefix = "contentFull_" + self.__nameIdPrefix,
                                        row = 0, 
                                        column = self.EntryUIs.im.column)
        textLabelFull.subsection = self.subsection
        textLabelFull.imIdx = self.imIdx
        openSecondaryImage(textLabelFull)
        bindChangeColorOnInAndOut(textLabelFull)
        return textLabelFull
        

    def produceFullMoveEntriesWidget(self, parentWidget):
        def fullMove(event, entryFrameManager:EntryFrameManager,
                                *args):
            if not event.widget.clicked:
                fsf.Data.Book.subsectionOpenInTOC_UI = self.subsection
                fsf.Data.Book.entryImOpenInTOC_UI = self.imIdx
            else:
                fsf.Data.Book.entryImOpenInTOC_UI = _u.Token.NotDef.str_t

            event.widget.clicked = not event.widget.clicked

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onFullEntryMove" in dir(w):
                    w.onFullEntryMove()
            

        showImages = TOCLabelWithClick(parentWidget, 
                                    text = self.EntryUIs.full.name,
                                    prefix = "contentOfImages_" + self.__nameIdPrefix,
                                    row = 0,
                                    column = self.EntryUIs.full.column)
        showImages.imIdx = self.imIdx
        showImages.subsection = self.subsection
        showImages.clicked = False
        showImages.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [lambda e, efm = self.entryFrameManager, *args: fullMove(e, efm, *args)])
        bindChangeColorOnInAndOut(showImages)
        return showImages

    def produceAlwaysShowChbxWidget(self, parentWidget):
        chkbtnShowPermamently = EntryShowPermamentlyCheckbox(parentWidget, 
                                                             self.subsection, self.imIdx, 
                                                             "contentShowAlways_" + self.__nameIdPrefix,
                                                             row = 0, 
                                                             column = self.EntryUIs.alwaysShow.column,)
        return chkbtnShowPermamently

    def produceDictWidget(self, parentWidget):
        def openNoteMenu(event, *args):
            notesMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.NotesManager)
            notesMenuManger.subsection = event.widget.subsection
            notesMenuManger.imIdx = event.widget.imIdx

            event.widget.shouldShowNotesMenu = not event.widget.shouldShowNotesMenu
            if (event.widget.shouldShowNotesMenu):
                notesMenuManger.show()
            else:
                notesMenuManger.hide()
        openNoteUIEntry = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.dict.name, 
                                        prefix = "contentOpenDictUIEntry" + self.__nameIdPrefix,
                                        row = self.EntryUIs.dict.row, 
                                        column = self.EntryUIs.dict.column,
                                        columnspan = 1)
        openNoteUIEntry.imIdx = self.imIdx
        openNoteUIEntry.subsection = self.subsection
        openNoteUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openNoteMenu])
        bindChangeColorOnInAndOut(openNoteUIEntry)
        return openNoteUIEntry 

    def produceOpenNotesWidget(self, parentWidget):
        def openNoteMenu(event, *args):
            notesMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.EntryNotesManager)
            notesMenuManger.subsection = event.widget.subsection
            notesMenuManger.imIdx = event.widget.imIdx

            event.widget.shouldShowNotesMenu = not event.widget.shouldShowNotesMenu
            if (event.widget.shouldShowNotesMenu):
                notesMenuManger.show()
            else:
                notesMenuManger.hide()
    
        openNoteUIEntry = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.entryNote.name, 
                                        prefix = "contentOpenNoteUIEntry" + self.__nameIdPrefix,
                                        row = self.EntryUIs.entryNote.row, 
                                        column = self.EntryUIs.entryNote.column,
                                        columnspan = 1)
        openNoteUIEntry.imIdx = self.imIdx
        openNoteUIEntry.subsection = self.subsection
        openNoteUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openNoteMenu])
        notesExist = False

        fullPathToEntryJSON = _upan.Paths.Entry.JSON.getAbs(sf.Wr.Manager.Book.getCurrBookFolderPath(),
                                                        self.subsection, self.imIdx)
        entryStructureExists = ocf.Wr.FsAppCalls.checkIfFileOrDirExists(fullPathToEntryJSON)
        if entryStructureExists:
            currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            entryWordDictArr = fsf.Wr.EntryInfoStructure.readProperty(self.subsection,
                                                    self.imIdx,
                                                    fsf.Wr.EntryInfoStructure.PubProp.entryWordDictDict,
                                                    currBookPath)

            if (entryWordDictArr != _u.Token.NotDef.dict_t)\
                and (entryWordDictArr != {}):
                notesExist = True
        if notesExist:
            openNoteUIEntry.changeColor("brown")
        bindChangeColorOnInAndOut(openNoteUIEntry, shouldBeBrown = notesExist)
        return openNoteUIEntry

    def showSubrentriesWidget(self, parentWidget):
        def showSubentriesCmd(event, *args):
            widget = event.widget
            
            if self.imIdx not in fsf.Data.Sec.leadingEntry(self.subsection).values():
                return

            showSubentries = fsf.Data.Sec.showSubentries(widget.subsection)
            if showSubentries.get(widget.imIdx) != None:
                showSubentries[widget.imIdx] = not showSubentries[widget.imIdx]
            else:
                showSubentries[widget.imIdx] = True
    
            fsf.Data.Sec.showSubentries(widget.subsection, showSubentries)

            for w in wd.Data.Reactors.entryChangeReactors.copy().values():
                if "onShowSubentries" in dir(w):
                    w.onShowSubentries(widget.subsection, widget.imIdx)

        showSubentries = TOCLabelWithClick(parentWidget,
                                        text = self.EntryUIs.showSubentries.name,
                                        prefix = "contentShowSubentriesEntry" + self.__nameIdPrefix,
                                        row = 0, 
                                        column = self.EntryUIs.showSubentries.column)
        showSubentries.imIdx = self.imIdx
        showSubentries.subsection = self.subsection
        showSubentries.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [showSubentriesCmd])
        
        if str(self.imIdx) in fsf.Data.Sec.leadingEntry(self.subsection).values():
            hasSubentries = True
        else:
            hasSubentries = False
        if hasSubentries:
            showSubentries.changeColor("brown")
        bindChangeColorOnInAndOut(showSubentries, shouldBeBrown = hasSubentries)
        return showSubentries

    def __produceGroupExtraWidgets(self, parentWidget, groupName):
        hideImageGroupLabel = TOCLabelWithClick(parentWidget, 
                                                text = "[show/hide]",
                                                prefix = "contentHideImageGroupLabel_" + self.__nameIdPrefix,
                                                row = 0, column = 1)

        hideImageGroupLabel.render()

        hideImageGroupLabel.subsection = self.subsection
        hideImageGroupLabel.imIdx = self.imIdx
        hideImageGroupLabel.group = groupName

        bindChangeColorOnInAndOut(hideImageGroupLabel)

        def __cmd(e):
            imagesGroupsList = fsf.Data.Sec.imagesGroupsList(e.widget.subsection)
            imagesGroupsList[e.widget.group] = not imagesGroupsList[e.widget.group]
            fsf.Data.Sec.imagesGroupsList(e.widget.subsection, imagesGroupsList)

        hideImageGroupLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])

        newGroup = ImageSize_ETR(parentWidget,
                prefix = "contentNewGroupImageGroupLabel_" + self.__nameIdPrefix,
                row = 0, 
                column = 3,
                imIdx = self.imIdx,
                text = groupName,
                width = 10)
        newGroup.subsection = self.subsection
        newGroup.render()
        newGroup.setData(groupName)

        moveGroup = ImageSize_ETR(parentWidget,
                prefix = "contentMoveImageGroupLabel_" + self.__nameIdPrefix,
                row = 0, 
                column = 2,
                imIdx = self.imIdx,
                text = self.subsection + ":" + self.imIdx,
                width = 10)
        moveGroup.subsection = self.subsection
        moveGroup.imIdx = self.imIdx

        def __moveGroup(e, *args): 
            subsection = e.widget.subsection
            imIdx = e.widget.imIdx
            # NOTE: this is a hack but I can't find a better way atm
            newGroupNameWName = "contentNewGroupImageGroupLabel_".lower()
            newGroupNameW = [i for i in e.widget.getParent().getChildren() \
                                if newGroupNameWName.lower() in i.name][0]

            targetWholePath:str = e.widget.getData()

            if ":" not in targetWholePath:
                _u.log.autolog("Incorrect destination path")

            targetSubsection = targetWholePath.split(":")[0]
            targetEntryIdx = targetWholePath.split(":")[1]
            targetGroupName = newGroupNameW.getData() if newGroupNameW.getData() != "" else "No group"
            sourceSubsection = subsection
            sourceEntryIdx = imIdx
            sourceGroupNameIdx = fsf.Data.Sec.imagesGroupDict(sourceSubsection)[sourceEntryIdx]
            sourceGroupName = list(fsf.Data.Sec.imagesGroupsList(sourceSubsection).keys())[sourceGroupNameIdx]

            # ask the user if we wnat to proceed.
            msg = "\
Do you want to move group \n\nto subsection\n'{0}' \n\nand entry: \n'{1}'\n\n with group name \n'{2}'?".format(targetSubsection, 
                                                                            targetEntryIdx, 
                                                                            targetGroupName)
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)


            if not response:
                return

            # UI
            pdfMenuManager = dt.AppState.UIManagers.getData("fake data access token", 
                                                            wf.Wr.MenuManagers.PdfReadersManager)
            pdfMenuManager.saveFigures()

            gm.GeneralManger.moveGroupToSubsection(sourceSubsection, sourceGroupName,
                                                    targetSubsection, targetGroupName, targetEntryIdx)

            self.widgetToScrollTo = None
            self.linkFrames = None
            self.currSecondRowLabels = None

            pdfMenuManager.forceUpdate()

        moveGroup.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                [__moveGroup])
        moveGroup.render()

    def produceGroupWidget(self, parentWidget):
        imagesGroupDict:dict = fsf.Data.Sec.imagesGroupDict(self.subsection)
        imagesGroupsWShouldShow:list = fsf.Data.Sec.imagesGroupsList(self.subsection)
        imagesGroups:list = list(imagesGroupsWShouldShow.keys())

        if imagesGroupDict.get(self.imIdx) != None:
            currImGroupidx = imagesGroupDict[self.imIdx]
        else:
            currImGroupidx = 0

        if int(self.imIdx) > 0 :
            entriesList = list(fsf.Data.Sec.imLinkDict(self.subsection).keys())
            entriesList.sort(key = int)

            print(entriesList)
            counter = 0

            while str(self.imIdx) not in entriesList:
                time.sleep(0.3)
                entriesList = list(fsf.Data.Sec.imLinkDict(self.subsection).keys())
                counter += 1
                if counter > 50:
                    _u.log.autolog("Something is wrong with the group list. Return")
                    return

            entriesList.index(str(self.imIdx))
            idx = entriesList[entriesList.index(self.imIdx) - 1] #previous entry

            if imagesGroupDict.get(str(idx)) != None:
                if idx == _u.Token.NotDef.str_t:
                    prevImGroupName = _u.Token.NotDef.str_t
                else:
                    prevImGroupName = imagesGroups[imagesGroupDict[idx]]
            else:
                prevImGroupName = _u.Token.NotDef.str_t
        elif self.imIdx == _u.Token.NotDef.str_t:
            prevImGroupName = imagesGroups[0]
        else:
            if imagesGroupDict.get(self.imIdx) != None:
                prevImGroupName = imagesGroups[imagesGroupDict[self.imIdx]]
            else:
                prevImGroupName = imagesGroups[0]

        if currImGroupidx == _u.Token.NotDef.str_t:
            currImGroupidx = 0

        currImGroupName = imagesGroups[currImGroupidx]

        topPad = 0

        if currImGroupName != prevImGroupName:
            if not imagesGroupsWShouldShow[currImGroupName]:
                topPad = 0
            elif (self.imIdx != "0"):
                topPad = 5

        imageGroupFrame = TOCFrame(parentWidget,
                                    prefix = "contentImageGroupFr_" + self.__nameIdPrefix,
                                    padding=[0, topPad, 0, 0], 
                                    row = 0, column = 0, columnspan = 100)

        if (currImGroupName != prevImGroupName) or (self.imIdx == "0"):
            def __updateGroup(event, *args):
                widget = event.widget

                if widget.group == "No group":
                    return

                def __getText(widget):
                    return widget.group
                                 
                def __setText(newText, widget):
                    oldGroupName = widget.group
    
                    imagesGroupsList = \
                        fsf.Data.Sec.imagesGroupsList(widget.subsection).copy()
                    imagesGroupsList = \
                        {k if k != oldGroupName else newText: v for k,v in imagesGroupsList.items()}
                    fsf.Data.Sec.imagesGroupsList(widget.subsection,
                                                    imagesGroupsList)
                    widget.group = newText
                
                def __updateImage(widget):
                    fsf.Wr.SectionInfoStructure.rebuildGroupOnlyImOnlyLatex(widget.subsection,
                                                                            widget.group)
                    #TODO: we need to update the other widgets as well

                bindWidgetTextUpdatable(event, __getText, __setText, __updateImage)

            img = getGroupImg(self.subsection, currImGroupName)
            imageGroupLabel = TOCLabelWithClickGroup(imageGroupFrame, 
                                        image = img, 
                                        prefix = "contentGroupP_" + self.__nameIdPrefix,
                                        padding = [30, 0, 0, 0], 
                                        row = 0, column = 0)
            imageGroupLabel.image = img
            imageGroupLabel.subsection = self.subsection
            imageGroupLabel.group = currImGroupName

            # NOTE: without rebind groups sometimes not shoing up #FIXME
            imageGroupLabel.rebind([ww.currUIImpl.Data.BindID.mouse2],
                                    [__updateGroup])

            imageGroupLabel.render()

            if currImGroupName != "No group":
                self.__produceGroupExtraWidgets(imageGroupFrame, currImGroupName)

        return imageGroupFrame 

    def produceGroupOM(self, parentWidget):
        imagesGroupDict:dict = fsf.Data.Sec.imagesGroupDict(self.subsection)
        imagesGroups = fsf.Data.Sec.imagesGroupsList(self.subsection)

        currImGroupidx = 0

        if imagesGroupDict.get(self.imIdx) != None:
            currImGroupidx = imagesGroupDict[self.imIdx]
        
        currImGroupidx = 0 if currImGroupidx == _u.Token.NotDef.str_t else currImGroupidx

        currImGroupName = list(imagesGroups.keys())[currImGroupidx]

        imageGroupOM = ImageGroupOM(imagesGroups,
                                   parentWidget, 
                                   self.subsection,
                                   self.imIdx,
                                   self,
                                   column = self.EntryUIs.group.column,
                                   currImGroupName = currImGroupName)
        return imageGroupOM

    def produceBookCodeProject(self, parentWidget):
        def openBookCodeProjectCmd(event, *args):
            subsection = event.widget.subsection
            imIdx = event.widget.imIdx
            dt.CodeTemp.currCodeFullLink = imIdx

            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            projectPath = _upan.Paths.Book.Code.getAbs(bookPath)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(projectPath):
                _u.log.autolog("Please add a book code project files.")
                return

            ocf.Wr.IdeCalls.openNewWindow(projectPath)

            bookCodeFiles:dict = fsf.Data.Sec.bookCodeFile(subsection)

            if bookCodeFiles.get(imIdx) != None:
                relFilepath = bookCodeFiles.get(imIdx)
                time.sleep(0.5)
                filepath = os.path.join(projectPath, relFilepath)

                if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(filepath):
                    return

                lines = []
                with open(filepath) as f:
                    lines = f.read().splitlines()
                
                marker = _upan.Names.codeLineMarkerBook(subsection, imIdx)

                for i in range(len(lines)):
                    if marker in lines[i]:
                        ocf.Wr.IdeCalls.openNewTab(filepath, i)
                        return

                ocf.Wr.IdeCalls.openNewTab(filepath)

        openBookCodeProject = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.openBookCodeProject.name, 
                                        prefix = "openBookCodeProject" + self.__nameIdPrefix,
                                        row = 1, 
                                        column = self.EntryUIs.openBookCodeProject.column,
                                        columnspan = 1)
        openBookCodeProject.imIdx = self.imIdx
        openBookCodeProject.subsection = self.subsection
        openBookCodeProject.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openBookCodeProjectCmd])
        bindChangeColorOnInAndOut(openBookCodeProject)
        return openBookCodeProject

    def produceSubsectionCodeProject(self, parentWidget):
        def openSubsectionCodeProjectCmd(event, *args):
            subsection = event.widget.subsection
            imIdx = event.widget.imIdx
            dt.CodeTemp.currCodeFullLink = imIdx

            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
            codeTemplatePath =_upan.Paths.Book.Code.getSubsectionTemplatePathAbs(bookPath)
            codeSubsectionPath =_upan.Paths.Section.getCodeRootAbs(bookPath,
                                                                    subsection)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(codeSubsectionPath):
                ocf.Wr.FsAppCalls.copyFile(codeTemplatePath, codeSubsectionPath)

            ocf.Wr.IdeCalls.openNewWindow(codeSubsectionPath)

            subsectionCodeFiles:dict = fsf.Data.Sec.subsectionCodeFile(subsection)

            if subsectionCodeFiles.get(imIdx) != None:
                relFilepath = subsectionCodeFiles.get(imIdx)
                time.sleep(0.5)
                filepath = os.path.join(codeSubsectionPath, relFilepath)

                if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(filepath):
                    _u.log.autolog(f"Subsection '{filepath}' file not found.")
                    return

                lines = []
                with open(filepath) as f:
                    lines = f.read().splitlines()
                
                marker = _upan.Names.codeLineMarkerSubsection(subsection, imIdx)

                for i in range(len(lines)):
                    if marker in lines[i]:
                        ocf.Wr.IdeCalls.openNewTab(filepath, i)
                        return

                ocf.Wr.IdeCalls.openNewTab(filepath)

        openSubsectionCodeProject = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.openSubsectionCodeProject.name, 
                                        prefix = "openSubsectionCodeProject" + self.__nameIdPrefix,
                                        row = 1, 
                                        column = self.EntryUIs.openSubsectionCodeProject.column,
                                        columnspan = 1)
        openSubsectionCodeProject.imIdx = self.imIdx
        openSubsectionCodeProject.subsection = self.subsection
        openSubsectionCodeProject.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openSubsectionCodeProjectCmd])
        bindChangeColorOnInAndOut(openSubsectionCodeProject)
        return openSubsectionCodeProject

    def produceEntryCodeProject(self, parentWidget):
        def openEntryCodeProjectCmd(event, *args):
            subsection =  event.widget.subsection
            imIdx =  event.widget.imIdx
            bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()

            entryPath = _upan.Paths.Entry.getAbs(bookPath, subsection, imIdx)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryPath):
                fsf.Wr.EntryInfoStructure.createStructure(bookPath, subsection, imIdx)

            entryCodeProjFilepath = _upan.Paths.Entry.getCodeProjAbs(bookPath, subsection, imIdx)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryCodeProjFilepath):
                codeProjTemplatePath = \
                    _upan.Paths.Book.Code.getEntryTemplatePathAbs(bookPath)
                ocf.Wr.FsAppCalls.copyFile(codeProjTemplatePath, entryCodeProjFilepath)

            ocf.Wr.IdeCalls.openNewWindow(_upan.Paths.Entry.getCodeProjAbs(bookPath, subsection, imIdx))

        openEntryCodeProject = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.openEntryCodeProject.name, 
                                        prefix = "openEntryCodeProject" + self.__nameIdPrefix,
                                        row = 1, 
                                        column = self.EntryUIs.openEntryCodeProject.column,
                                        columnspan = 1)
        openEntryCodeProject.imIdx = self.imIdx
        openEntryCodeProject.subsection = self.subsection
        openEntryCodeProject.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openEntryCodeProjectCmd])
        bindChangeColorOnInAndOut(openEntryCodeProject)
        return openEntryCodeProject


    def produceOpenProofMenu(self, parentWidget):
        def openProofsMenu(event, *args):
            prMenuManger = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.ProofsManager)

            event.widget.shouldShowProofMenu = not event.widget.shouldShowProofMenu

            if (event.widget.shouldShowProofMenu):
                prMenuManger.show(subsection =  event.widget.subsection, imIdx = event.widget.imIdx)
            else:
                prMenuManger.hide(subsection =  event.widget.subsection, imIdx = event.widget.imIdx)

        openProofsUIEntry = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.proof.name, 
                                        prefix = "contentOpenProofsUIEntry" + self.__nameIdPrefix,
                                        row = self.EntryUIs.proof.row, 
                                        column = self.EntryUIs.proof.column)

        openProofsUIEntry.imIdx = self.imIdx
        openProofsUIEntry.subsection = self.subsection
        openProofsUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [openProofsMenu])
        bindChangeColorOnInAndOut(openProofsUIEntry)
        return openProofsUIEntry

    def produceOpenWikiNotes(self, parentWidget):
        def openWiki(event, *args):
            os.system("\
    /Users/ashum048/books/utils/c++_modules/qt_KIK_Browser/build/Qt_6_8_0_macos-Debug/browser.app/Contents/MacOS/browser \
    http://localhost/wiki/A/User:The_other_Kiwix_guy/Landing")

        openEntryWikiUIEntry = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.wikiNote.name, 
                                        prefix = "contentOpenEntryWikiUIEntry" + self.__nameIdPrefix,
                                        row = 1, 
                                        column = self.EntryUIs.wikiNote.column,
                                        columnspan = 1)
        openEntryWikiUIEntry.imIdx = self.imIdx
        openEntryWikiUIEntry.subsection = self.subsection
        openEntryWikiUIEntry.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                    [openWiki])
        bindChangeColorOnInAndOut(openEntryWikiUIEntry)
        return openEntryWikiUIEntry

    def produceEntryWidgetFrames(self, topPad, row, leftPad, rowsPad = 0):
        nameId = _upan.Names.Entry.getEntryNameID(self.subsection, self.imIdx)

        entryFrame = TOCFrame(self.frame,
                                prefix = "contentFr_" + nameId,
                                padding=[leftPad, topPad, 0, 0],
                                row = row, column = 0, columnspan = 100)
        entryFrame.render()

        entryFrameManager = EntryFrameManager(entryFrame = entryFrame, 
                                              subsection = self.subsection, 
                                              imIdx = self.imIdx,
                                              widgetFactory = self)

        entryFrameManager.groupFrame = self.produceGroupWidget(entryFrame)

        entryFrameManager.rowFrame1 = TOCFrame(entryFrame,
                            prefix = "contentRow1Fr_" + nameId,
                            padding=[rowsPad, 0, 0, 0],
                            row = 1, 
                            column = 0, columnspan = 100)
        entryFrameManager.rowFrame1.subsection = self.subsection
        entryFrameManager.rowFrame1.imIdx = self.imIdx
        entryFrameManager.rowFrame1.render()

        entryFrameManager.rowFrame2 = TOCFrame(entryFrame,
                            prefix = "contentRow2Fr_" + nameId,
                            padding=[60 + rowsPad, 0, 0, 0],
                            row = 2, 
                            column = 0, columnspan = 100)
        entryFrameManager.rowFrame2.subsection = self.subsection
        entryFrameManager.rowFrame2.imIdx = self.imIdx

        linksFrameFactory = LinksFrameFactory(self.subsection,
                                              self.imIdx)
        linksFrameFactory.produceLinksFrame(parentWidget = entryFrame,
                                            row = 3,
                                            leftPad = rowsPad)
        entryFrameManager.linksFrameManager = linksFrameFactory.manager
        
        entryFrameManager.imagesFrame = TOCFrame(entryFrame,
                            prefix = "ImagesFrame" + nameId,
                            padding=[0, 0, 0, 0],
                            row = 4, 
                            column = 0, columnspan = 100)
        entryFrameManager.imagesFrame.subsection = self.subsection
        entryFrameManager.imagesFrame.imIdx = self.imIdx
        entryFrameManager.imagesFrame.render()
        return entryFrameManager

class EntryWidgetFactoryTOC(EntryWidgetFactory):
    # row 1
    class EntryUIs(EntryWidgetFactory.EntryUIs):
        def __init__(self):
            self.full = self.__EntryUIData("[f]", 1, EntryWidgetFactory.produceFullMoveEntriesWidget)
            self.im = self.__EntryUIData("[i]", 2, EntryWidgetFactory.produceOpenSecondaryImageWidget)
            self.copyLink = self.__EntryUIData("[cl]", 3, EntryWidgetFactory.produceCopyLinkWidget)
            self.pasteLink = self.__EntryUIData("[pl]", 4, EntryWidgetFactory.producePasteLinkEntryWidget)
            self.copy = self.__EntryUIData("[c]", 5, EntryWidgetFactory.produceCopyEntryWidget)
            self.pasteAfter = self.__EntryUIData("[p]", 6, EntryWidgetFactory.producePasteEntryWidget)
            self.excercises = self.__EntryUIData("[e]", 7, EntryWidgetFactory.produceOpenExcercisesWidget)
            self.group = self.__EntryUIData("", 8, EntryWidgetFactory.produceGroupOM)

            # row 2
            self.showLinks = self.__EntryUIData("[Links]", 1, EntryWidgetFactory.produceShowLinksForEntry)
            self.alwaysShow = self.__EntryUIData("", 2, EntryWidgetFactory.produceAlwaysShowChbxWidget)
            self.changeImSize = self.__EntryUIData("", 3, EntryWidgetFactory.produceChangeImSizeWidget)
            self.delete = self.__EntryUIData("[Delete]", 4, EntryWidgetFactory.produceRemoveEntryWidget)
            self.retake = self.__EntryUIData("[Retake]", 5, EntryWidgetFactory.produceRetakeImageWidget)
            self.addExtra = self.__EntryUIData("[Add extra]", 6, EntryWidgetFactory.produceAddExtraImageWidget)
            self.addProof = self.__EntryUIData("[Add proof]", 7, EntryWidgetFactory.produceAddProofImageWidget)
            self.showSubentries = self.__EntryUIData("[Show sub]", 8, EntryWidgetFactory.showSubrentriesWidget)
            self.note = self.__EntryUIData("[Dictionary]", 8, EntryWidgetFactory.produceOpenNotesWidget)
            self.leadingEntry = self.__EntryUIData("", 9, EntryWidgetFactory.produceLeadingEntryEtrWidget)
            self.shift = self.__EntryUIData("[Shift Up]", 10, EntryWidgetFactory.produceShiftLabelWidget)
            self.copyText = self.__EntryUIData("[Copy text]", 11, EntryWidgetFactory.produceCopyTextToMemWidget)

    def produceEntryWidgetsForFrame(self, parentWidget, row):
        self.frame = parentWidget

        leadingEntry = fsf.Data.Sec.leadingEntry(self.subsection)

        rowsPad = 0

        if leadingEntry.get(self.imIdx) != None:
            if str(leadingEntry[self.imIdx]) != _u.Token.NotDef.str_t:
                rowsPad += 30

                showSubentries = fsf.Data.Sec.showSubentries(self.subsection)
                if showSubentries.get(self.imIdx) != None:
                    if not showSubentries[self.imIdx]:
                        self.entryFrameManager = None
                        return

        self.entryFrameManager = self.produceEntryWidgetFrames(topPad = self.topPad, 
                                                               leftPad = self.leftPad, 
                                                               row = row,
                                                               rowsPad = rowsPad)

        if self.entryFrameManager == None:
            return
        
        self.entryFrameManager.groupFrame.render()

        mainImageWidget = self.produceMainImageWidget(parentWidget = self.entryFrameManager.rowFrame1)
        mainImageWidget.render()

        if fsf.Data.Sec.tocWImageDict(self.subsection)[self.imIdx] == "1":
            self.entryFrameManager.showImages()

        full = self.EntryUIs.full.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        self.entryFrameManager.fullMoveWidget = full
        full.render()
        im = self.EntryUIs.im.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        im.render()
        copy = self.EntryUIs.copy.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        copy.render()
        pasteAfter = self.EntryUIs.pasteAfter.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        pasteAfter.render()
        excercises = self.EntryUIs.excercises.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        excercises.render()
        copyLink = self.EntryUIs.copyLink.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        copyLink.render()
        pasteLink = self.EntryUIs.pasteLink.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        pasteLink.render()
        group = self.EntryUIs.group.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        group.render()

        leadingEntry = self.EntryUIs.leadingEntry.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        leadingEntry.render()
        showSubentries = self.EntryUIs.showSubentries.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        showSubentries.render()
        delete = self.EntryUIs.delete.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        delete.render()
        shift = self.EntryUIs.shift.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        shift.render()
        copyText = self.EntryUIs.copyText.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        copyText.render()
        retake = self.EntryUIs.retake.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        retake.render()
        addExtra = self.EntryUIs.addExtra.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        addExtra.render()
        addProof = self.EntryUIs.addProof.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        addProof.render()
        alwaysShow = self.EntryUIs.alwaysShow.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        alwaysShow.render()
        changeImSize = self.EntryUIs.changeImSize.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        changeImSize.render()
        self.entryFrameManager.uiResizeEtr = changeImSize

class EntryWidgetFactoryEntryWindow(EntryWidgetFactory):
    class EntryUIs(EntryWidgetFactory.EntryUIs):
        def __init__(self):
            self.full = self.__EntryUIData("[f]", 1, EntryWidgetFactory.produceFullMoveEntriesWidget)
            self.copyLink = self.__EntryUIData("[cl]", 3, EntryWidgetFactory.produceCopyLinkWidget)
            self.pasteLink = self.__EntryUIData("[pl]", 4, EntryWidgetFactory.producePasteLinkEntryWidget)
            self.copy = self.__EntryUIData("[c]", 5, EntryWidgetFactory.produceCopyEntryWidget)
            self.pasteAfter = self.__EntryUIData("[p]", 6, EntryWidgetFactory.producePasteEntryWidget)
            self.excercises = self.__EntryUIData("[e]", 7, EntryWidgetFactory.produceOpenExcercisesWidget)

            self.showLinks = self.__EntryUIData("[Links]", 1, EntryWidgetFactory.produceShowLinksForEntry)
            self.alwaysShow = self.__EntryUIData("", 2, EntryWidgetFactory.produceAlwaysShowChbxWidget)
            self.changeImSize = self.__EntryUIData("", 3, EntryWidgetFactory.produceChangeImSizeWidget)
            self.retake = self.__EntryUIData("[Retake]", 4, EntryWidgetFactory.produceRetakeImageWidget)
            self.addExtra = self.__EntryUIData("[Add exta]", 5, EntryWidgetFactory.produceAddExtraImageWidget)
            self.addProof = self.__EntryUIData("[Add proof]", 6, EntryWidgetFactory.produceAddProofImageWidget)
            self.dict = self.__EntryUIData("[Dictionary]", 7, EntryWidgetFactory.produceDictWidget)
            self.group = self.__EntryUIData("", 8, EntryWidgetFactory.produceGroupOM)
            
            self.openBookCodeProject = self.__EntryUIData("[code:b", 1, EntryWidgetFactory.produceBookCodeProject)
            self.openSubsectionCodeProject = self.__EntryUIData(",s", 2, EntryWidgetFactory.produceSubsectionCodeProject)
            self.openEntryCodeProject = self.__EntryUIData(",e]", 3, EntryWidgetFactory.produceEntryCodeProject)
            self.entryNote = self.__EntryUIData("[Note]", 4, EntryWidgetFactory.produceOpenNotesWidget, row = 1)
            self.wikiNote = self.__EntryUIData("[Wiki]", 5, EntryWidgetFactory.produceOpenWikiNotes)
            self.copyText = self.__EntryUIData("[Copy text]", 6, EntryWidgetFactory.produceCopyTextToMemWidget, row = 1)
            self.proof = self.__EntryUIData("[Show proof]", 7, EntryWidgetFactory.produceOpenProofMenu, row = 1)

    def produceEntryWidgetsForFrame(self, parentWidget, row):
        self.frame = parentWidget

        self.entryFrameManager = self.produceEntryWidgetFrames(topPad = self.topPad, 
                                                               leftPad = self.leftPad,
                                                               row = row)

        mainImageWidget = self.produceMainImageWidget(parentWidget = self.entryFrameManager.rowFrame1)
        mainImageWidget.render()

        self.entryFrameManager.rowFrame2.render()
        self.entryFrameManager.showImages()

        full = self.EntryUIs.full.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        self.entryFrameManager.fullMoveWidget = full
        full.render()
        copy = self.EntryUIs.copy.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        copy.render()
        pasteAfter = self.EntryUIs.pasteAfter.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        pasteAfter.render()
        excercises = self.EntryUIs.excercises.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        excercises.render()
        copyLink = self.EntryUIs.copyLink.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        copyLink.render()
        pasteLink = self.EntryUIs.pasteLink.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        pasteLink.render()


        showLinks = self.EntryUIs.showLinks.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        showLinks.render()
        alwaysShow = self.EntryUIs.alwaysShow.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        alwaysShow.render()
        changeImSize = self.EntryUIs.changeImSize.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        changeImSize.render()
        self.entryFrameManager.uiResizeEtr = changeImSize
        retake = self.EntryUIs.retake.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        retake.render()
        addExtra = self.EntryUIs.addExtra.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        addExtra.render()
        addProof = self.EntryUIs.addProof.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        addProof.render() 
        dictionary = self.EntryUIs.dict.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        dictionary.render()
        group = self.EntryUIs.group.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        group.render()

        openBookCodeProject = self.EntryUIs.openBookCodeProject.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        openBookCodeProject.render()
        openSubsectionCodeProject = self.EntryUIs.openSubsectionCodeProject.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        openSubsectionCodeProject.render()
        openEntryCodeProject = self.EntryUIs.openEntryCodeProject.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        openEntryCodeProject.render()
        entryNote = self.EntryUIs.entryNote.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        entryNote.render()
        wikiNote = self.EntryUIs.wikiNote.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        wikiNote.render()
        copyText = self.EntryUIs.copyText.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        copyText.render()
        proof = self.EntryUIs.proof.cmd(self, parentWidget = self.entryFrameManager.rowFrame2)
        proof.render()

class EntryWidgetFactoryWebLink(EntryWidgetFactory):
    class EntryUIs(EntryWidgetFactory.EntryUIs):
        def __init__(self):
            self.delete = self.__EntryUIData("[del]", 1, EntryWidgetFactoryLink.produceDeleteLinkLabel)
    
    def __init__(self, subsection, imIdx, topPad, leftPad, webLinkName):
        self.webLinkName = webLinkName

        super().__init__(subsection, imIdx, topPad, leftPad)
    
    def produceDeleteWebLink(self, parentWidget):
        def __delWebLinkCmd(event, efm):
            widget = event.widget
            gm.GeneralManger.RemoveWebLink(widget.subsection,
                                            widget.imIdx,
                                            widget.sourceWebLinkName)

            efm.remove()

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onRemoveLink" in dir(w):
                    w.onRemoveLink()
            
        linkLabelDelete = TOCLabelWithClick(parentWidget, 
                                            text = self.EntryUIs.delete.name, 
                                            prefix = "contentGlLinksTSubsectionDel_" + self.getPrefixID(),
                                            row = self.EntryUIs.delete.row, 
                                            column = 2)

        linkLabelDelete.subsection = self.subsection
        linkLabelDelete.imIdx = self.imIdx
        linkLabelDelete.sourceWebLinkName = self.webLinkName

        linkLabelDelete.rebind([ww.currUIImpl.Data.BindID.mouse1], 
                               [lambda e, m = self.entryFrameManager, *args: __delWebLinkCmd(e, m)])

        bindChangeColorOnInAndOut(linkLabelDelete)
        return linkLabelDelete

    def __produceEntryPrefixLabel(self, parentWidget):
        glLinkPrefixLbl = TOCLabelWithClick(parentWidget, 
                                                text = "web: ", 
                                                padding = [0, 0, 0, 0],
                                                prefix = "contentGlLinksTSubsection_" + self.getPrefixID(),
                                                row = 0, column = 0)
        return glLinkPrefixLbl

    def __produceMainImageLabel(self, parentWidget):
        def __openWebOfTheImageCmd(webLink):
            cmd = "open -na 'Google Chrome' --args --new-window \"" + webLink + "\""
            _u.runCmdAndWait(cmd)

        latexTxt = tff.Wr.TexFileUtils.formatEntrytext(self.webLinkName)
        currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        linkFilepath = _upan.Paths.Screenshot.Images.getWebLinkImageAbs(currBookPath,
                                                        self.subsection,
                                                        self.imIdx,
                                                        self.webLinkName)

        if ocf.Wr.FsAppCalls.checkIfFileOrDirExists(linkFilepath):
            pilIm = Image.open(linkFilepath)
        else:
            pilIm = tff.Wr.TexFileUtils.fromTexToImage(latexTxt, linkFilepath) 

        shrink = 0.7
        pilIm.thumbnail([int(pilIm.size[0] * shrink),int(pilIm.size[1] * shrink)], Image.LANCZOS)
        img = ww.currUIImpl.UIImage(pilIm)

        glLinkLablel = TOCLabelWithClick(parentWidget,
                                    image = img,
                                    text = self.webLinkName, 
                                    prefix = "contentGlLinks_" + self.getPrefixID(),
                                    row = 0, column = 1)
        glLinkLablel.subsection = self.subsection
        glLinkLablel.imIdx = self.imIdx
        glLinkLablel.image = img

        glLinks:dict = fsf.Data.Sec.imGlobalLinksDict(self.subsection)[self.imIdx]

        glLinkLablel.rebind([ww.currUIImpl.Data.BindID.mouse1], \
                            [lambda e, wl = glLinks[self.webLinkName], *args: __openWebOfTheImageCmd(wl)])
        return glLinkLablel

    def produceEntryMainFrame(self, parentWidget):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 0, "columnspan" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        name = "_LinksMainImageFrame_"

        mainImageFrame = ww.currUIImpl.Frame(prefix = self.getPrefixID(),
                                             name = name, 
                                             rootWidget = parentWidget,
                                             renderData = renderData,
                                             padding = [0, 0, 0, 0])

        glLinkPrefixLbl = self.__produceEntryPrefixLabel(mainImageFrame)
        glLinkPrefixLbl.render()

        glLinkMainImLbl = self.__produceMainImageLabel(mainImageFrame)
        glLinkMainImLbl.render()

        return mainImageFrame

    def produceEntryWidgetsForFrame(self, parentWidget, row):
        self.frame = parentWidget
        self.entryFrameManager = self.produceEntryWidgetFrames(topPad = self.topPad, 
                                                               leftPad = self.leftPad,
                                                               row = row)

        mainImageWidget = self.produceEntryMainFrame(parentWidget = self.entryFrameManager.rowFrame1)
        mainImageWidget.render()

        deleteLabelWidget = self.produceDeleteWebLink(parentWidget = self.entryFrameManager.rowFrame1)
        deleteLabelWidget.render()

class EntryWidgetFactoryLink(EntryWidgetFactory):
    class EntryUIs(EntryWidgetFactory.EntryUIs):
        def __init__(self):
            self.full = self.__EntryUIData("[f]", 1, EntryWidgetFactory.produceFullMoveEntriesWidget)
            self.im = self.__EntryUIData("[i]", 2, EntryWidgetFactoryLink.produceOpenLinkImages)
            self.delete = self.__EntryUIData("[del]", 3, EntryWidgetFactoryLink.produceDeleteLinkLabel)
            self.excercises = self.__EntryUIData("[e]", 4, EntryWidgetFactory.produceOpenExcercisesWidget)
            self.proof = self.__EntryUIData("[pr]", 5, EntryWidgetFactory.produceOpenProofMenu, row = 0)

    def __init__(self, subsection, imIdx, topPad, leftPad, sourceSubsection, sourceImIdx):
        self.sourceSubsection = sourceSubsection
        self.sourceImIdx = sourceImIdx

        super().__init__(subsection, imIdx, topPad, leftPad)

    def produceOpenLinkImages(self, parentWidget):
        def showImagesCmd(e, efm):
            if not e.widget.clicked:
                efm.showImages(mainImPadLeft = 60, eImPadLeft = 60, createExtraImagesExtraWidgets = False)
            else:
                efm.hideImages()
            
            e.widget.clicked = not e.widget.clicked

        showImages = TOCLabelWithClick(parentWidget, 
                                    text = self.EntryUIs.im.name,
                                    prefix = "showImages_" + self.getPrefixID(),
                                    row = 0,
                                    column = self.EntryUIs.im.column)
        showImages.imIdx = self.imIdx
        showImages.subsection = self.subsection
        showImages.clicked = False
        showImages.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [lambda e, efm = self.entryFrameManager, *args: showImagesCmd(e, efm, *args)])
        bindChangeColorOnInAndOut(showImages)
        return showImages

    def produceDeleteLinkLabel(self, parentWidget):
        def __delGlLinkCmd(event, efm):
            widget = event.widget

            gm.GeneralManger.RemoveGlLink(widget.targetSubssection,
                                            widget.sourceSubssection,
                                            widget.sourceImIdx,
                                            widget.targetImIdx)
            efm.remove()

            for w in wd.Data.Reactors.entryChangeReactors.values():
                if "onRemoveLink" in dir(w):
                    w.onRemoveLink()

        linkLabelDelete = TOCLabelWithClick(parentWidget, 
                                                    text = self.EntryUIs.delete.name, 
                                                    prefix = "contentGlLinksTSubsectionDel_" + self.getPrefixID(),
                                                    row = 0,
                                                    column = self.EntryUIs.delete.column)
        
        linkLabelDelete.targetSubssection = self.subsection
        linkLabelDelete.sourceSubssection = self.sourceSubsection
        linkLabelDelete.targetImIdx = self.imIdx
        linkLabelDelete.sourceImIdx = self.sourceImIdx

        linkLabelDelete.rebind([ww.currUIImpl.Data.BindID.mouse1], 
                               [lambda e, efm = self.entryFrameManager, *args: __delGlLinkCmd(e, efm)])
        bindChangeColorOnInAndOut(linkLabelDelete)
        return linkLabelDelete

    def __produceLinkPathLabel(self, parentWidget):
        glLinkSubsectioLbl = TOCLabelWithClick(parentWidget, 
                                               prefix = "contentGlLinksTSubsection_" + self.getPrefixID(),
                                               text = self.subsection + ": ", 
                                               padding = [0, 0, 0, 0],
                                               row = 0, column = 0)
        return glLinkSubsectioLbl

    def produceMainImageWidget(self, parentWidget):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 0, "columnspan" : 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        name = "_LinksMainImageFrame_"

        mainImageFrame = ww.currUIImpl.Frame(prefix = self.getPrefixID(),
                                             name = name, 
                                             rootWidget = parentWidget,
                                             renderData = renderData,
                                             padding = [0, 0, 0, 0])

        linkPathLabel = self.__produceLinkPathLabel(mainImageFrame)
        linkPathLabel.render()
        mainImageWidget = super().produceMainImageWidget(parentWidget = mainImageFrame,
                                                      leftPad = 0, column = 1)
        mainImageWidget.render()
        return mainImageFrame

    def produceEntryWidgetsForFrame(self, parentWidget, row):
        self.frame = parentWidget

        self.entryFrameManager = self.produceEntryWidgetFrames(topPad = self.topPad, 
                                                               leftPad = self.leftPad,
                                                               row = row)

        mainImageWidget = self.produceMainImageWidget(parentWidget = self.entryFrameManager.rowFrame1)
        mainImageWidget.render()

        # self.entryFrameManager.showImages(mainImPadLeft = 0, createExtraImagesExtraWidgets = False)

        full = self.EntryUIs.full.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        self.entryFrameManager.fullMoveWidget = full
        full.render()
        im = self.EntryUIs.im.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        im.render()
        delete = self.EntryUIs.delete.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        delete.render()
        excercises = self.EntryUIs.excercises.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        excercises.render()

        proof = self.EntryUIs.proof.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        proof.render()

class EntryWidgetFactorySearchTOC(EntryWidgetFactory):
    # row 1
    class EntryUIs(EntryWidgetFactory.EntryUIs):
        def __init__(self):
            self.full = self.__EntryUIData("[f]", 1, EntryWidgetFactory.produceFullMoveEntriesWidget)
            self.im = self.__EntryUIData("[i]", 2, EntryWidgetFactorySearchTOC.produceOpenImageInTocWidget)
            self.copyLink = self.__EntryUIData("[cl]", 3, EntryWidgetFactory.produceCopyLinkWidget)
            self.pasteLink = self.__EntryUIData("[pl]", 4, EntryWidgetFactory.producePasteLinkEntryWidget)
            self.copy = self.__EntryUIData("[c]", 5, EntryWidgetFactory.produceCopyEntryWidget)
            self.pasteAfter = self.__EntryUIData("[p]", 6, EntryWidgetFactory.producePasteEntryWidget)

    def produceOpenImageInTocWidget(self, parentWidget):
        def openImageInPlace(widget):
            def __cmd(event = None, *args):
                widget = event.widget
                imIdx = widget.imIdx
                subsection = widget.subsection

                widget.clicked = not widget.clicked

                if widget.clicked:
                    widget.changeColor("brown")
                else:
                    widget.changeColor("white")

                bindChangeColorOnInAndOut(textLabelFull, shouldBeBrown = widget.clicked)

                for w in wd.Data.Reactors.entryChangeReactors.copy().values():
                    if "onOpenImageInTocWidget" in dir(w):
                        w.onOpenImageInTocWidget(subsection, imIdx)
            
            widget.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])

        textLabelFull = TOCLabelWithClick(parentWidget, 
                                        text = self.EntryUIs.im.name, 
                                        prefix = "contentFull_" + super().getPrefixID(),
                                        row = 0, 
                                        column = self.EntryUIs.im.column)
        textLabelFull.subsection = self.subsection
        textLabelFull.imIdx = self.imIdx

        openImageInPlace(textLabelFull)
        bindChangeColorOnInAndOut(textLabelFull)
        return textLabelFull

    def produceEntryWidgetsForFrame(self, parentWidget, row):
        self.frame = parentWidget

        leadingEntry = fsf.Data.Sec.leadingEntry(self.subsection)

        rowsPad = 0

        if leadingEntry.get(self.imIdx) != None:
            if str(leadingEntry[self.imIdx]) != _u.Token.NotDef.str_t:
                rowsPad += 30

                showSubentries = fsf.Data.Sec.showSubentries(self.subsection)
                if showSubentries.get(self.imIdx) != None:
                    if not showSubentries[self.imIdx]:
                        self.entryFrameManager = None
                        return

        self.entryFrameManager = self.produceEntryWidgetFrames(topPad = self.topPad, 
                                                               leftPad = self.leftPad, 
                                                               row = row,
                                                               rowsPad = rowsPad)

        if self.entryFrameManager == None:
            return
        
        self.entryFrameManager.groupFrame.render()

        mainImageWidget = self.produceMainImageWidget(parentWidget = self.entryFrameManager.rowFrame1)
        mainImageWidget.render()

        if fsf.Data.Sec.tocWImageDict(self.subsection)[self.imIdx] == "1":
            self.entryFrameManager.showImages()

        full = self.EntryUIs.full.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        self.entryFrameManager.fullMoveWidget = full
        full.render()
        im = self.EntryUIs.im.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        im.render()
        copy = self.EntryUIs.copy.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        copy.render()
        pasteAfter = self.EntryUIs.pasteAfter.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        pasteAfter.render()
        copyLink = self.EntryUIs.copyLink.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        copyLink.render()
        pasteLink = self.EntryUIs.pasteLink.cmd(self, parentWidget = self.entryFrameManager.rowFrame1)
        pasteLink.render()


class SubsectionWidgetFactory:
    class EntryUIs:
        class __EntryUIData:
            def __init__(self, name, column, cmd, row = 0) -> None:
                self.name = name
                self.column = column
                self.row = row
                self.cmd = cmd

        def __init__(self):
            raise NotImplementedError()

    def __init__(self, subsection):
        self.subsection = subsection
        self.widgetManager = None
        self.frame = None

        self.EntryUIs = self.EntryUIs()

    def __getPrefix(self):
        nameId = "subsecLabel_" + self.subsection 
        return nameId.replace(".", "")

    def __bindOpenPdfOnStartOfTheSection(self, widget:TOCLabelWithClick):
        def __cmd(event = None, *args):
            # open orig material on page
            origMatNameDict = fsf.Data.Sec.origMatNameDict(self.subsection)
            omName = origMatNameDict[list(origMatNameDict.keys())[-1]]

            if str(omName) == _u.Token.NotDef.str_t:
                # when there is no entries yet we use the current origMaterial name
                omName = fsf.Data.Book.currOrigMatName

            subsectionStartPage = fsf.Data.Sec.start(self.subsection)
            fsf.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(omName, subsectionStartPage)

            pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.PdfReadersManager)
            pdfReadersManager.show(page = int(subsectionStartPage))

            event.widget.changeColor("white")
        
        widget.rebind([ww.currUIImpl.Data.BindID.mouse1], [__cmd])


    def __bindUpdateSubsection(self, event, *args):
        def __setTextFunc(newText, widget):
            subsection = widget.subsection
            if subsection in list(fsf.Data.Book.sections.keys()):
                sections = fsf.Data.Book.sections
                sections[subsection]["name"] = newText
                fsf.Data.Book.sections = sections
            else:
                fsf.Data.Sec.text(event.widget.subsection, newText)

        def __getTextFunc(widget):
            subsection = widget.subsection
            sectionName = ""
            if subsection in list(fsf.Data.Book.sections.keys()):
                # Top section
                sectionName = fsf.Data.Book.sections[subsection]["name"]
            else:
                sectionName = fsf.Data.Sec.text(subsection)

            return sectionName
        
        def __updateImageFunc(widget):
            subsection = widget.subsection
            if subsection in list(fsf.Data.Book.sections.keys()):
                fsf.Wr.SectionInfoStructure.rebuildTopSectionLatex(widget.subsection,
                                                                _upan.Names.Subsection.getTopSectionPretty)
            else:
                fsf.Wr.SectionInfoStructure.rebuildSubsectionImOnlyLatex(widget.subsection,
                                                                _upan.Names.Subsection.getSubsectionPretty)

        bindWidgetTextUpdatable(event, __getTextFunc, __setTextFunc, __updateImageFunc)

    def produceTopSectionLatexImage(self):
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
        result = ww.currUIImpl.UIImage(result)

        subsectionLabel = TOCLabeWithClickSubsection(root = self.widgetManager.topFrame,
                                                    image = result,
                                                    prefix = "_topSection" + self.__getPrefix(), 
                                                    padding = [0, 0, 0, 0],
                                                    row = 0, column= 0)
        subsectionLabel.image = result
        subsectionLabel.subsection = self.subsection
        subsectionLabel.rebind([ww.currUIImpl.Data.BindID.mouse2],
                                [self.__bindUpdateSubsection])
        self.__bindOpenPdfOnStartOfTheSection(subsectionLabel)
        return subsectionLabel

    def produceTopSectionExtraWidgets(self):
        openContentLabel = self.produceOpenContentWidget()
        openContentLabel.render()

    def produceOpenContentWidget(self):
        def openContentOfSubsection(e):
            widget = e.widget
            isTopSection = len(widget.subsection.split(".")) == 1

            if not widget.clicked:
                if isTopSection:
                    fsf.Data.Book.currTopSection = widget.subsection
                else:
                    fsf.Data.Book.subsectionOpenInTOC_UI = widget.subsection
                    fsf.Data.Book.currSection = widget.subsection

                for w in wd.Data.Reactors.subsectionChangeReactors.values():
                    if isTopSection:
                        if "onTopSectionOpen" in dir(w):
                            w.onTopSectionOpen(widget.subsection)
                    else:
                        if "onSubsectionOpen" in dir(w):
                            w.onSubsectionOpen(widget.subsection)
                
                widget.changeColor("brown")
                bindChangeColorOnInAndOut(widget, shouldBeBrown = True)
                widget.clicked = True
            else:
                if isTopSection:
                    fsf.Data.Book.currTopSection = _u.Token.NotDef.str_t
                else:
                    fsf.Data.Book.subsectionOpenInTOC_UI = _u.Token.NotDef.str_t
                    fsf.Data.Book.currSection = _u.Token.NotDef.str_t

                for w in wd.Data.Reactors.subsectionChangeReactors.values():
                    if isTopSection:
                        if "onTopSectionClose" in dir(w):
                            w.onTopSectionClose(widget.subsection)
                    else:
                        if "onSubsectionClose" in dir(w):
                            w.onSubsectionClose(widget.subsection)

                widget.changeColor("white")
                bindChangeColorOnInAndOut(widget, shouldBeBrown = False)
                widget.clicked = False

        openContentLabel = TOCLabelWithClick(self.widgetManager.topFrame, text = "[content]", 
                                            prefix = "subsecContent" + self.__getPrefix(),
                                            row = 0, column= 1)
        openContentLabel.subsection = self.subsection

        self.widgetManager.openContentWidget = openContentLabel

        openContentLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], 
                    [lambda e, *args: openContentOfSubsection(e)])
        bindChangeColorOnInAndOut(openContentLabel)
        return openContentLabel

    def produceSubsectionRebuildLatex(self):
        def rebuildSubsectionLatexWrapper(subsection):
            fsf.Wr.SectionInfoStructure.rebuildSubsectionLatex(subsection,
                                                            _upan.Names.Group.formatGroupText,
                                                            _upan.Names.Subsection.getSubsectionPretty,
                                                            _upan.Names.Subsection.getTopSectionPretty)

            for w in wd.Data.Reactors.subsectionChangeReactors.values():
                if "onRebuildSubsectionLatex" in dir(w):
                    w.onRebuildSubsectionLatex(subsection)

        rebuildLatex = TOCLabelWithClick(self.widgetManager.topFrame, text = "[rebuild latex]",
                                        prefix = "subsecRebuild" + self.__getPrefix(),
                                        row = 0, column = 4)
        rebuildLatex.subsection = self.subsection

        bindChangeColorOnInAndOut(rebuildLatex)
        rebuildLatex.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [lambda e, *args: rebuildSubsectionLatexWrapper(e.widget.subsection)])
        return rebuildLatex

    def produceShowVideoLabel(self):
        def showSubsectiionVideoWrapper(subsection):  
            videoPlayerManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.VideoPlayerManager)
            videoPlayerManager.show(subsection, "0")

            for w in wd.Data.Reactors.subsectionChangeReactors.values():
                if "onShowVideo" in dir(w):
                    w.onShowVideo(subsection)

        showVideo = TOCLabelWithClick(self.widgetManager.topFrame, text = "[show video]",
                                            prefix = "showVideo" + self.subsection.replace(".", ""),
                                            row = 0, column = 6)
        showVideo.subsection = self.subsection

        bindChangeColorOnInAndOut(showVideo)
        showVideo.rebind([ww.currUIImpl.Data.BindID.mouse1],
                            [lambda e, *args: showSubsectiionVideoWrapper(e.widget.subsection)])

        return showVideo

    def produceChangeStartPageETR(self):
        def __updateStartPage(e, *args):
            newStartPage = e.widget.getData()
            subsection = e.widget.subsection
            fsf.Data.Sec.start(subsection, newStartPage)
            omName = fsf.Data.Book.currOrigMatName
            
            fsf.Wr.OriginalMaterialStructure.updateOriginalMaterialPage(omName, newStartPage)

            pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.PdfReadersManager)
            pdfReadersManager.show(page = int(newStartPage))

            for w in wd.Data.Reactors.subsectionChangeReactors.values():
                if "onUpdateSubsectionStartPage" in dir(w):
                    w.onUpdateSubsectionStartPage(subsection)

        startPage = fsf.Data.Sec.start(self.subsection)
        changeStartPage = ImageSize_ETR(self.widgetManager.topFrame,
                                        prefix = "updateStartPageEntryText" + self.subsection.replace(".", ""),
                                        row = 0, 
                                        column = 3,
                                        imIdx = -1,
                                        text = startPage)
        changeStartPage.subsection = self.subsection
        changeStartPage.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                [lambda e, *args:__updateStartPage(e, changeStartPage.subsection, *args)])
        
        return changeStartPage

    def produceUpdateSubsectionPathETR(self):
        def __updateSubsectionPath(e, *args):
            targetSubsection = e.widget.getData()
            subsection = e.widget.subsection
            sourceSubsection = subsection

            # ask the user if we wnat to proceed.
            msg = "Do you want to move \n\n subsection\n'{0}' \n\nto \n'{1}'?".format(sourceSubsection, targetSubsection)
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

            mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.show()

            if not response:
                return

            gm.GeneralManger.moveSubsection(sourceSubsection,
                                            targetSubsection)
            
            for w in wd.Data.Reactors.subsectionChangeReactors.values():
                if "onUpdateSubsectionPath" in dir(w):
                    w.onUpdateSubsectionPath(subsection)

        updateSubsectionPath = ImageSize_ETR(self.widgetManager.topFrame,
                                                prefix = "updateSubsectionPosEntryText" + self.subsection.replace(".", ""),
                                                row = 0, 
                                                column = 5,
                                                imIdx = -1,
                                                text = self.subsection,
                                                width = 20)
        updateSubsectionPath.subsection = self.subsection
        updateSubsectionPath.rebind([ww.currUIImpl.Data.BindID.Keys.enter],
                                [lambda e, *args:__updateSubsectionPath(e, updateSubsectionPath.subsection, *args)])

        return updateSubsectionPath

    def produceRemoveSubsectionLabel(self):
        def __removeSubsection(e, subsection, *args):
            sourceSubsection = subsection

            # ask the user if we wnat to proceed.
            msg = "Do you want to \n\nREMOVE \n\n subsection:\n'{0}'?".format(sourceSubsection)
            response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

            mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                        wf.Wr.MenuManagers.MathMenuManager)
            mainManager.show()

            if not response:
                return

            gm.GeneralManger.deleteSubsection(sourceSubsection)

            for w in wd.Data.Reactors.subsectionChangeReactors:
                if "onSubsectionRemove" in dir(w):
                    w.onSubsectionRemove(subsection)

        removeSubsection = TOCLabelWithClick(self.widgetManager.topFrame,
                                                prefix = "removeSubsectionPosEntryText" + self.subsection.replace(".", ""),
                                                row = 0, 
                                                column = 7,
                                                text = "[delete]")
        removeSubsection.subsection = self.subsection

        bindChangeColorOnInAndOut(removeSubsection)
        removeSubsection.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [lambda e, *args:__removeSubsection(e, removeSubsection.subsection, *args)])

        return removeSubsection

    def produceShowHideSubsectionLabel(self):
        def showHideSubsectionsWrapper(subsection):
            subsectionsHidden:list = fsf.Data.Book.subsectionsHiddenInTOC_UI

            if subsection in subsectionsHidden:
                subsectionsHidden.remove(subsection)
            else:
                subsectionsHidden.append(subsection)
            
            fsf.Data.Book.subsectionsHiddenInTOC_UI =  subsectionsHidden

            for w in wd.Data.Reactors.subsectionChangeReactors.values():
                if "onSubsectionShowHide" in dir(w):
                    w.onSubsectionShowHide(subsection)

        hideSubsections = TOCLabelWithClick(self.widgetManager.topFrame, 
                                            text = "[show/hide]",
                                            prefix = "subsecShowHide" + self.subsection.replace(".", ""),
                                            row = 0, column = 2)
        subsectionsList = fsf.Wr.BookInfoStructure.getSubsectionsList(self.subsection)

        if subsectionsList != []:
            hideSubsections.changeColor("brown")

        hideSubsections.subsection = self.subsection

        if subsectionsList != []:
            bindChangeColorOnInAndOut(hideSubsections, shouldBeBrown = True)
        else:
            bindChangeColorOnInAndOut(hideSubsections)

        hideSubsections.rebind([ww.currUIImpl.Data.BindID.mouse1],
                                [lambda e, *args: showHideSubsectionsWrapper(e.widget.subsection)])
        
        return hideSubsections

    def produceSubsectionExtraWidgets(self):
        openContentLabel = self.produceOpenContentWidget()
        openContentLabel.render()

        rebuildLatexLabel = self.produceSubsectionRebuildLatex()
        rebuildLatexLabel.render()

        if fsf.Data.Sec.isVideo(self.subsection):
            showVideoLabel = self.produceShowVideoLabel()
            showVideoLabel.render()
        
        changeStartPageEtr = self.produceChangeStartPageETR()
        changeStartPageEtr.render()

        updateSubsectionPathETR = self.produceUpdateSubsectionPathETR()
        updateSubsectionPathETR.render()

        removeSubsectionLabel = self.produceRemoveSubsectionLabel()
        removeSubsectionLabel.render()

        showHideSubsectionLabel = self.produceShowHideSubsectionLabel()
        showHideSubsectionLabel.render()

    def produceSubsectionLatexImage(self):
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
        result = ww.currUIImpl.UIImage(result)

        subsectionLabel = TOCLabeWithClickSubsection(self.widgetManager.topFrame, 
                                            image = result, 
                                            prefix = "_subsecion" + self.__getPrefix(),
                                            row = 0, column= 0)
        subsectionLabel.image = result
        subsectionLabel.subsection = self.subsection
        subsectionLabel.rebind([ww.currUIImpl.Data.BindID.mouse2],
                                [self.__bindUpdateSubsection])
        self.__bindOpenPdfOnStartOfTheSection(subsectionLabel)
        return subsectionLabel

    def produceSectionChildrenSectionsFrame(self, parentWidget):
        subsectionChildrenSectionsFrame = TOCFrame(parentWidget, 
                                                   "subsectionChildrenSectionsFrame" + self.__getPrefix(), 
                                                   row = 2, 
                                                   column = 0, 
                                                   columnspan = 1, 
                                                   padding = [0, 0, 0, 0])
        subsectionChildrenSectionsFrame.render()

        return subsectionChildrenSectionsFrame

    def produceSubsectionFrame(self, row):
        topPad = 0 if (len(self.subsection.split(".")) != 1) or (row == 0) else 20

        subsectionFrame = TOCFrame(self.frame, "subsectionFrame" + self.__getPrefix(), row, 
                         column = 0, columnspan = 1, padding = [0, topPad, 0, 0])
        subsectionFrame.render()

        topFrame = TOCFrame(subsectionFrame, "subsectionTopFrame" + self.__getPrefix(), row = 0, 
                         column = 0, columnspan = 1, padding = [0, 0, 0, 0])
        topFrame.render()

        entriesFrame = TOCFrame(subsectionFrame, "subsectionEntriesFrame" + self.__getPrefix(), row = 1, 
                         column = 0, columnspan = 1, padding = [0, 0, 0, 0])
        entriesFrame.render()
        
        subsectionChildrenSectionsFrame = self.produceSectionChildrenSectionsFrame(subsectionFrame)

        return subsectionFrame, \
               topFrame, \
               entriesFrame, \
               subsectionChildrenSectionsFrame

class SubsectionWidgetFactoryMainTOC(SubsectionWidgetFactory):
    class EntryUIs(EntryWidgetFactory.EntryUIs):
        def __init__(self):
            # # row 2.5 
            # self.full = self.__EntryUIData("[f]", 1, EntryWidgetFactoryTOC.produceFullMoveEntriesWidget)
            pass

    def produceSubsectionWidgets(self, parentFrame, row):
        self.frame = parentFrame

        subsectionFrame, topFrame, entriesFrame, subsectionChildrenSectionsFrame = \
                                                         self.produceSubsectionFrame(row)

        self.widgetManager = SubsectionFrameManagerMainTOC(self.subsection, 
                                                    subsectionFrame, 
                                                    topFrame, 
                                                    entriesFrame, 
                                                    subsectionChildrenSectionsFrame,
                                                    self)
        
        if len(self.subsection.split(".")) == 1:
            subsectionImageLabel = self.produceTopSectionLatexImage()
        else:
            subsectionImageLabel = self.produceSubsectionLatexImage()
        
        subsectionImageLabel.render()

        if len(self.subsection.split(".")) == 1:
            self.produceTopSectionExtraWidgets()
        else:
            self.produceSubsectionExtraWidgets()

class SubsectionWidgetFactorySearchTOC(SubsectionWidgetFactory):
    class EntryUIs(EntryWidgetFactory.EntryUIs):
        def __init__(self):
            # # row 2.5 
            # self.full = self.__EntryUIData("[f]", 1, EntryWidgetFactoryTOC.produceFullMoveEntriesWidget)
            pass

    def produceSubsectionWidgets(self, parentFrame, row):
        self.frame = parentFrame

        subsectionFrame, topFrame, entriesFrame, subsectionChildrenSectionsFrame = \
                                                         self.produceSubsectionFrame(row)

        self.widgetManager = SubsectionFrameManagerSearchTOC(self.subsection, 
                                                    subsectionFrame, 
                                                    topFrame, 
                                                    entriesFrame, 
                                                    subsectionChildrenSectionsFrame,
                                                    self)
        
        if len(self.subsection.split(".")) == 1:
            subsectionImageLabel = self.produceTopSectionLatexImage()
        else:
            subsectionImageLabel = self.produceSubsectionLatexImage()
        
        subsectionImageLabel.render()

        if len(self.subsection.split(".")) == 1:
            self.produceTopSectionExtraWidgets()
        else:
            self.produceSubsectionExtraWidgets()

def addExtraIm(subsection, mainImIdx, isProof, entryLabel = None, event = None):
    extraImIdx = _u.Token.NotDef.str_t
    extraImagesDict = fsf.Data.Sec.extraImagesDict(subsection)

    if not isProof:
        if mainImIdx in list(extraImagesDict.keys()):
            extraImText = "con" + str(len(extraImagesDict[mainImIdx]))
        else:
            extraImText = "con0"
    else:
        extraImText = "proof"

    gm.GeneralManger.AddExtraImageForEntry(mainImIdx, subsection, extraImIdx, extraImText)

    def __afterEImagecreated(mainImIdx, subsection, 
                                extraImageIdx, extraImText, event,
                                entryLabel):            
        extraImagesDict = fsf.Data.Sec.extraImagesDict(subsection).copy()
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

        for w in wd.Data.Reactors.entryChangeReactors.values():
            if "onAddExtraImage" in dir(w):
                w.onAddExtraImage(subsection, mainImIdx, extraImageIdx)
        
        return
        if entryLabel != None:
            if entryLabel != None:
                if type(entryLabel) == TOCLabelWithClick:
                    #this comes from the main TOC menu
                    entryLabel.generateEvent(ww.currUIImpl.Data.BindID.mouse1)
                else:
                    # this comes from the Entry menu
                    entryLabel.notificationAfterImageWasCreated(entryLabel.subsection, entryLabel.imIdx)
                    updateSecondaryFrame = str(mainImIdx) != str(fsf.Data.Book.entryImOpenInTOC_UI)
                    entryLabel.updateHeight(scrollTOC = True, updateSecondaryFrame = updateSecondaryFrame)
                    entryLabel.scrollToImage(entryLabel.imIdx, extraImageIdx)

        if event != None:
            mathMenuManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                                        wf.Wr.MenuManagers.MathMenuManager)
            mathMenuManager.scrollToWidget(event, None)

    t = Thread(target = __afterEImagecreated, 
            args = [mainImIdx, subsection, extraImIdx, extraImText, event, entryLabel])
    t.start()

def bindOpenOMOnThePageOfTheImage(widget:TOCLabelWithClick, targetSubsection, targetImIdx, eImidx = None):
    def __cmd(event = None, *args): 
        pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.PdfReadersManager)
        
        pdfReadersManager.moveToEntry(targetSubsection, targetImIdx, eImidx, forcePageChange = True)

    widget.rebind([ww.currUIImpl.Data.BindID.cmdMouse1], [__cmd])

def openVideoOnThePlaceOfTheImage(widget:TOCLabelWithClick, targetSubsection, targetImIdx, eImidx = None):
    def __cmd(event = None, *args): 
        pdfReadersManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.PdfReadersManager)
        
        pdfReadersManager.changeSize([720, 517, 0, 352])
        videoManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                    wf.Wr.MenuManagers.VideoPlayerManager)
        
        videoManager.show(targetSubsection, targetImIdx)

    widget.rebind([ww.currUIImpl.Data.BindID.cmdMouse1], [__cmd])


def closeAllImages(gpframe, showAll, isWidgetLink, secondIm = [None, None], linkIdx = None):
    '''
    close all images of children of the widget
    '''
    parents = gpframe.getChildren().copy()
    for parent in parents:
        # NOTE this is not an ideal hack to get the
        children =  parent.getChildren().copy()
        for child in children:
            gChildren = child.getChildren().copy()
            for gChild in gChildren:
                if "contentOfImages_".lower() in str(gChild.name).lower():
                    subsection = str(gChild.name).split("_")[-4].replace("$", ".")
                    idx = str(gChild.name).split("_")[-3]

                    alwaysShow = False
                    if idx !=  "-1":
                        alwaysShow = fsf.Data.Sec.tocWImageDict(subsection)[idx] == "1"

                    if (not alwaysShow) or showAll: 
                        gChild.clicked = False
                    else: 
                        gChild.clicked = True

                    if "Row2" in str(child):
                        child.destroy()
            if "contentGlLinksOfImages_" in str(child.name):
                child.clicked = False

            # deal with extra images
            if dc.UIConsts.imageWidgetID.lower() in str(child.name).lower():
                subsection = str(child.name).split("_")[-4].replace("$", ".")
                idx = str(child.name).split("_")[-3].replace("-", "_").split("_")[0]

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
                    
                    child.destroy()