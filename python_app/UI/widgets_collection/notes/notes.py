import tkinter as tk
from tkinter import ttk
import Pmw
from PIL import Image, ImageTk
from threading import Thread

from tkinter import scrolledtext

import UI.widgets_wrappers as ww
import UI.widgets_facade as wf
import UI.widgets_collection.utils as _ucomw
import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import data.constants as dc
import file_system.file_system_facade as fsf
import settings.facade as sf
import outside_calls.outside_calls_facade as ocf
import scripts.osascripts as osascr
import UI.widgets_data as wd
import data.temp as dt
import generalManger.generalManger as gm
import wordDict.wordDict as wordd

exImages = []

class ImageText_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix, row, column, imNoteIdx, text):
        name = "_textImage_ETR" + str(imNoteIdx)
        self.defaultText = text
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row, "columnspan": 6},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }


        extraBuildOptions = {
            ww.Data.GeneralProperties_ID : {ww.Data.CommonTextColor_ID: wd.Data.ENT.defaultTextColor,
                                            "font": ('Georgia 14')},
            ww.TkWidgets.__name__ : {"width": 60, "fg": "white"}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraBuildOptions,
                        defaultText = self.defaultText)
        super().setData(self.defaultText)
        self.setTextColor("white")
    
    def receiveNotification(self, _):
        return self.getData()
    
    def defaultTextCMD(self):
        pass


class NotesImageLabel(ttk.Label):
    noteImIdx = None

    def __init__(self, root, name, subsection, imIdx, 
                 noteIdx, text = _u.Token.NotDef.str_t, padding = [0, 0, 0, 0]):
        self.noteImIdx = str(noteIdx)

        if text ==  _u.Token.NotDef.str_t:
            bookName = sf.Wr.Manager.Book.getCurrBookName()

            imagePath = _upan.Paths.Entry.NoteImage.getAbs(bookName, subsection, imIdx, noteIdx)

            if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(imagePath):
                currBookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                fsf.Wr.EntryInfoStructure.rebuildNote(subsection, 
                                                      imIdx, 
                                                      noteIdx, 
                                                      text,
                                                      currBookPath)

            pilIm = Image.open(imagePath)
            pilIm.thumbnail([530, 1000], Image.LANCZOS)
            img = ImageTk.PhotoImage(pilIm)
            exImages.append(img)
            return super().__init__(root, name = name, image = img, padding = padding)
        else:
            return super().__init__(root, name = name, text = text, padding = padding)


class NotesImage(ww.currUIImpl.Frame):
    displayedImages = []
    subsection = None
    entryIdx = None

    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0, "columnspan": 6},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.NW}
        }
        name = "_notesImage_LBL"

        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data)
    
    def render(self, **kwargs):
                
        # get an image from the
        widget = self.widgetObj

        for child in widget.winfo_children():
            child.destroy()

        balloon = Pmw.Balloon(widget)
        self.imLabel = _ucomw.addMainEntryImageWidget(widget, 
                                                      self.subsection, self.entryIdx,
                                                      120, self.displayedImages, balloon)
        self.imLabel.render()
        self.imLabel.focus_force()

        def skipProofs(subsection, imIdx, i):
           return "proof" in fsf.Data.Sec.extraImagesDict(subsection)[imIdx][i].lower()

        exImLabels = _ucomw.addExtraEntryImagesWidgets(widget, 
                                                       self.subsection, self.entryIdx,
                                                       120, self.displayedImages, balloon,
                                                       skippConditionFn = skipProofs)
        for l in exImLabels:
            l.render()

        return super().render(**kwargs)

class MoveTOCtoNotesEntry_BTN(ww.currUIImpl.Button,
                                  dc.AppCurrDataAccessToken):
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 4, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Move TOC"
        name = "_MoveTOCToEntry_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        notesManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.MathMenuManager)
        notesManager.moveTocToEntry(self.subsection, self.imIdx)

class AddDictHitToEntry_BTN(ww.currUIImpl.Button,
                              dc.AppCurrDataAccessToken):
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Add Word"
        name = "_AddWordWindow_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        currBookpath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        entryFSpath = _upan.Paths.Entry.getAbs(currBookpath, self.subsection, self.imIdx)

        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryFSpath):
            fsf.Wr.EntryInfoStructure.createStructure(currBookpath, 
                                                      self.subsection,
                                                      self.imIdx)

        entryWordDictDict = fsf.Wr.EntryInfoStructure.readProperty(self.subsection,
                                                                       self.imIdx,
                                                                       fsf.Wr.EntryInfoStructure.PubProp.entryWordDictDict,
                                                                       currBookpath)
        if entryWordDictDict == _u.Token.NotDef.dict_t:
            entryWordDictDict = {}
        
        key = self.notify(SearchDict_ETR)

        if key == _u.Token.NotDef.str_t:
            return

        value = wordd.readFromDict(key)
        entryWordDictDict[key] = value

        fsf.Wr.EntryInfoStructure.updateProperty(self.subsection,
                                                self.imIdx,
                                                fsf.Wr.EntryInfoStructure.PubProp.entryWordDictDict,
                                                entryWordDictDict,
                                                currBookpath)

        msg = f"After adding '{key}' to entry '{self.subsection}:{self.imIdx}'"
        ocf.Wr.TrackerAppCalls.stampChanges(currBookpath, msg)

        self.notify(DictText_LBL)

class HideNotesWindow_BTN(ww.currUIImpl.Button,
                              dc.AppCurrDataAccessToken):
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 2, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        text = "Hide"
        name = "_HideNotesWindow_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        notesManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.NotesManager)
        notesManager.hide()

        msg = "\
After updating the notes for \n\
'{0}':'{1}'.".format(self.subsection, self.imIdx)
        _u.log.autolog(msg)
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)


class SearchDict_ETR(ww.currUIImpl.TextEntry):
    def __init__(self, patentWidget, prefix):
        name = "_SearchDict_ETR"
        defaultText = "Search for definition in the in dictionary"
        renderData = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 3, "columnspan": 6},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.N}
        }
        extraOptions = {
            ww.Data.GeneralProperties_ID : {"width" : 70},
            ww.TkWidgets.__name__ : {}
        }

        super().__init__(prefix, 
                        name, 
                        patentWidget, 
                        renderData,
                        extraOptions = extraOptions,
                        defaultText = defaultText,
                        bindCmd = self.bindCmd)
    
    def receiveNotification(self, broadcasterType):
        text = self.getData()

        if (text != self.defaultText) and (text != ""):
            return text
        else:
            return _u.Token.NotDef.str_t
      
    def getData(self, **kwargs):
        text = super().getData(**kwargs)
        return text
      
    def bindCmd(self):
        def __searchCmd(*args):
            key = self.getData()
            hits = [wordd.readFromDict(key)]
            hits = [[i, False, key] for i in hits]
            self.notify(Dict_BOX, [hits])

        return [ww.currUIImpl.Data.BindID.Keys.shenter], \
                [__searchCmd]


class DictText(tk.Text):
    '''
    This used to show the text retrieved from the dict
    '''
    
    tocFrame = None
    text = None

    def rebind(self, keys, cmds):
        for i in range(len(keys)):
            key = keys[i]
            cmd = cmds[i]

            self.bind(key, cmd)

    def __showAsETR(self, *args):
        dictHits = self.tocFrame.dictHits

        for i in range(len(dictHits)):
            if dictHits[i][0] == self.text:
                dictHits[i][1] = True
        
        self.tocFrame.render()

    def __init__(self, root, prefix, row = 0, column = 0, columnspan = 1, sticky = tk.NW, 
                 text = "", localWord = False, *args, **kwargs) -> None:
        self.text = text
       
        self.row = row
        self.column = column
        self.columnspan = columnspan
        self.sticky = sticky

        super().__init__(root, name = prefix, *args, **kwargs)
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

        if not localWord:
            self.config(background = "#394d43")
        else:
            self.config(background = "#7c3b3b")

        self.config(state=tk.DISABLED)
        self.place(x = 0, y = 0)

        self.rebind([ww.currUIImpl.Data.BindID.mouse2],[self.__showAsETR])
    
    def render(self):
        self.grid(row = self.row, column = self.column,
                  columnspan = self.columnspan, sticky = self.sticky)

    def generateEvent(self, event, *args, **kwargs):
        self.event_generate(event, *args, **kwargs)

    def getChildren(self):
        return self.winfo_children()

class DictText_LBL(ww.currUIImpl.Label):
    textWidgets = [] 
    subsection = None
    imIdx = None

    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 4, "columnspan": 6},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_DictTextLabel_LBL"
        text = ""
        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data, 
                        text = text)
    
    def receiveNotification(self, broadcasterType, *args):
        self.render()

    def __showWord(self, e, *args):
        key = e.widget.dictWord
        text = e.widget.dictText
        self.notify(Dict_BOX, [[text, False, key]])

    def __delWord(self, e, *args):
        key = e.widget.dictWord
        entryWordDictDict:dict = fsf.Wr.EntryInfoStructure.readProperty(self.subsection,
                                                                       self.imIdx,
                                                                       fsf.Wr.EntryInfoStructure.PubProp.entryWordDictDict)
        entryWordDictDict.pop(key)
        fsf.Wr.EntryInfoStructure.updateProperty(self.subsection,
                                                 self.imIdx,
                                                 fsf.Wr.EntryInfoStructure.PubProp.entryWordDictDict,
                                                 entryWordDictDict)

        currBookpath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        msg = f"After deleting the dictionary word '{key}' for '{self.subsection}:{self.imIdx}'."
        ocf.Wr.TrackerAppCalls.stampChanges(currBookpath, msg)
        self.render()

    def getWords(self):
        currBookpath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        entryFSpath = _upan.Paths.Entry.getAbs(currBookpath, self.subsection, self.imIdx)

        if not ocf.Wr.FsAppCalls.checkIfFileOrDirExists(entryFSpath):
            fsf.Wr.EntryInfoStructure.createStructure(currBookpath, 
                                                      self.subsection,
                                                      self.imIdx)

        entryWordDictDict:dict = fsf.Wr.EntryInfoStructure.readProperty(self.subsection,
                                                                       self.imIdx,
                                                                       fsf.Wr.EntryInfoStructure.PubProp.entryWordDictDict,
                                                                       currBookpath)

        column = 0

        for k,v in entryWordDictDict.items():
            textWidget = _ucomw.TOCLabelWithClick(self.widgetObj, "_DictTextLabelText_" + str(column), 
                                                    row = 0, column = column, text = "[" + k)
            textWidget.dictWord = k
            textWidget.dictText = v
            textWidget.rebind([ww.currUIImpl.Data.BindID.mouse1], [self.__showWord])
            _ucomw.bindChangeColorOnInAndOut(textWidget)
            textWidget.render()
            self.textWidgets.append(textWidget)

            textDelWidget = _ucomw.TOCLabelWithClick(self.widgetObj, "_DictTextdelLabelText_" + str(column), 
                                                    row = 0, column = column + 1, text = "d]")
            textDelWidget.dictWord = k
            _ucomw.bindChangeColorOnInAndOut(textDelWidget)
            textDelWidget.rebind([ww.currUIImpl.Data.BindID.mouse1], [self.__delWord])
            textDelWidget.render()
            self.textWidgets.append(textDelWidget)

            column += 2

    def render(self):
        for w in self.textWidgets:
            w.grid_forget()
        self.textWidgets = []
        self.getWords()
        return super().render()

def _rebuildNote(*args, **kwargs):
    '''
        used for multithreaded note rebuild
    '''
    t = Thread(target= fsf.Wr.EntryInfoStructure.rebuildNote, 
            args = (args))
    t.start()
    return t

class Notes_BOX(ww.currUIImpl.ScrollableBox,
                    dc.AppCurrDataAccessToken):
    subsection = None
    imIdx = None

    currNoteCopyIdx = _u.Token.NotDef.int_t

    noteIdxShownInText = []
    currEtr = _u.Token.NotDef.dict_t.copy()
    etrTexts = _u.Token.NotDef.dict_t.copy()

    displayedImages = []

    latestWidgetToscrollTo = None
    latestNoteIdxToscrollTo = None

    def __init__(self, parentWidget, prefix, windth = 730, height = 450):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 1, "columnspan" : 6, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_showNotesCurr_text"

        self.parent = parentWidget.widgetObj

        super().__init__(prefix,
                        name,
                        parentWidget,
                        renderData = data,
                        height = height,
                        width = windth,
                        makeScrollable = False)

        def on_vertical(event):
            self.canvas.yview_scroll(-1 * event.delta, 'units')

        self.container.bind_all('<Mod1-MouseWheel>', on_vertical)

    def __renderAfterRebuild(self, *args, **kwargs):
        def __internal(*args, **kwargs):
            noteIdx = kwargs["noteIdx"]
            t = _rebuildNote(*args, **kwargs)
            t.join()
            self.render()
            position = self.etrTexts[noteIdx][1]
            self.currEtr[noteIdx].focus_force()

            try:
                self.currEtr[noteIdx].mark_set("insert", position)
            except:
                pass
        Thread(target = __internal,
               args = args, 
               kwargs = kwargs).start()

    def __scrollIntoView(self, event, widget = None):
        try:
            posy = 0

            if widget == None:
                pwidget = event.widget
            else:
                pwidget = widget


            self.canvas.yview_scroll(-100, "units")
            self.canvas.update()
            pwidget.update()

            while pwidget != self.parent:
                posy += pwidget.winfo_y()
                pwidget = pwidget.master

            posy = 0

            if widget == None:
                pwidget = event.widget
            else:
                pwidget = widget

            while pwidget != self.parent:
                posy += pwidget.winfo_y()
                pwidget = pwidget.master

            pos = posy - self.scrollable_frame.winfo_rooty()
            height = self.scrollable_frame.winfo_height()
            self.canvas.yview_moveto((pos / height) - 0.008)
        except:
            pass

    def addNotesNotes(self):
        notes = fsf.Wr.EntryInfoStructure.readProperty(self.subsection,
                                                       self.imIdx, 
                                                       fsf.Wr.EntryInfoStructure.PubProp.entryNotesList)
        '''
        for each note add widgets:
        '''
        if self.currEtr == _u.Token.NotDef.dict_t:
            self.currEtr = {}           


        extraImagesDict = fsf.Data.Sec.extraImagesDict(self.subsection)
        if self.imIdx in list(extraImagesDict.keys()):
            extraImages = extraImagesDict[self.imIdx]
            numOrigImages = len(extraImages) + 1
        else:
            numOrigImages = 1

        mainLabels = []
        for i in range(numOrigImages):
            mainLabels.append(_ucomw.TOCFrame(self.scrollable_frame, 
                                            "notesMainNoteImageFRM_" + str(i),
                                            i, 0, 1)
                              )

        imageLables = []
        balloon = Pmw.Balloon(self.scrollable_frame)
        imLabel = _ucomw.addMainEntryImageWidget(mainLabels[0], 
                                                      self.subsection, self.imIdx,
                                                      0, self.displayedImages, balloon,
                                                      row = 0,
                                                      columnspan = 1,
                                                      column = 1)
        imageLables.append(imLabel)
        imLabel.focus_force()

        def skipProofs(*args):
           return False
        
        exImLabels = _ucomw.addExtraEntryImagesWidgets(mainLabels[1:], 
                                                       self.subsection, self.imIdx,
                                                       0, self.displayedImages, balloon,
                                                       skippConditionFn = skipProofs,
                                                       row = 0,
                                                       columnspan = 1,
                                                       column = 1,
                                                       createExtraWidgets = False)
  
        imageLables.extend(exImLabels)

        for i in range(len(imageLables)):
            imageLables[i].render()

            '''
            add
            '''
            addLabel = _ucomw.TOCLabelWithClick(mainLabels[i], "_addNote_" + str(i), 
                                                    0, 0, text = "Add")
            addLabel.noteImIdx = i

            def addLabelNoteIdx(event, *args):
                text = _u.Token.NotDef.str_t
                bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                structureCreated = fsf.Wr.EntryInfoStructure.addNote(self.subsection, self.imIdx, 
                                                                     text, bookPath, 
                                                                     position = event.widget.noteImIdx)

                # update the box UI
                self.notify(Notes_BOX)

                if structureCreated:
                    notesManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                                wf.Wr.MenuManagers.MathMenuManager)
                    notesManager.moveTocToEntry(self.subsection, self.imIdx)
                
                self.render()

            addLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [addLabelNoteIdx])
            _ucomw.bindChangeColorOnInAndOut(addLabel)
            addLabel.render()
            
            if str(i) not in list(notes.keys()):
                continue

            def __showTextOrImage(event, *args):
                self.latestNoteIdxToscrollTo = event.widget.noteImIdx
                bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                widgetnoteImIdx = str(event.widget.noteImIdx)

                if widgetnoteImIdx in self.noteIdxShownInText:
                    self.noteIdxShownInText.remove(widgetnoteImIdx)
                    text = self.currEtr[widgetnoteImIdx].getData()

                    if text != self.currEtr[widgetnoteImIdx].defaultText:
                        _rebuildNote(self.subsection,
                                            self.imIdx,
                                            event.widget.noteImIdx,
                                            text,
                                            bookPath)

                    self.currEtr.pop(widgetnoteImIdx)
                else:
                    self.noteIdxShownInText.append(str(event.widget.noteImIdx))

                self.render()

            # image / text
            if str(i) not in self.noteIdxShownInText:
                label = NotesImageLabel(mainLabels[i], "notesImageIMG_" + str(i), 
                                            self.subsection, self.imIdx, i,
                                            padding = [120, 0, 0, 0])
                label.grid(row = 1, column = 1, sticky = tk.NW)
                label.bind(ww.currUIImpl.Data.BindID.mouse2, __showTextOrImage)
                label.bind(ww.currUIImpl.Data.BindID.mouse1, self.__scrollIntoView)
                labelToScrollTo = label
            else:
                label = _ucomw.TOCFrame(mainLabels[i], 
                                "notesImageFRM_" + str(i),
                                1, 1, 1
                                )
                labIm = NotesImageLabel(label, "notesImageIMG_" + str(i), 
                                            self.subsection, self.imIdx, i)
                labIm.grid(row = 0, column = 1)

                text = ""
                if str(i) in list(self.etrTexts.keys()):
                    text = self.etrTexts[str(i)][0]
                else:
                    text = notes[str(i)]

                labETR = _ucomw.MultilineText_ETR(label, "notesImageETR_", 1, 0, i, text)
                self.currEtr[str(i)] = labETR

                labRebuild = _ucomw.TOCLabelWithClick(label, "notesImageRebuild_" + str(i), 
                                                2, 0, text = "Rebuild")
                labRebuild.noteImIdx = str(i)

                def rebuildETRImage(event, *args):
                    widgetnoteImIdx = event.widget.noteImIdx
                    text = self.currEtr[widgetnoteImIdx].getData()

                    bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                    self.__renderAfterRebuild(self.subsection,
                                self.imIdx,
                                event.widget.noteImIdx,
                                text,
                                bookPath,
                                noteIdx = widgetnoteImIdx)

                    return "break"

                labETR.noteImIdx = str(i)
                labETR.rebind([ww.currUIImpl.Data.BindID.Keys.shenter], [rebuildETRImage])
                labRebuild.rebind([ww.currUIImpl.Data.BindID.mouse1], [rebuildETRImage])
                labIm.bind(ww.currUIImpl.Data.BindID.mouse2, __showTextOrImage)
                labIm.bind(ww.currUIImpl.Data.BindID.mouse1, self.__scrollIntoView)
                _ucomw.bindChangeColorOnInAndOut(labRebuild)

                labETR.render()
                labRebuild.render()
                label.render()
                labelToScrollTo = label


            if (str(i) == self.latestNoteIdxToscrollTo) and label != None:
                self.latestWidgetToscrollTo = labelToScrollTo

            '''
            delete
            '''
            deleteLabel = _ucomw.TOCLabelWithClick(mainLabels[i], "_deleteNote_" + str(i), 
                                                    1, 0, text = "Del")
            deleteLabel.noteImIdx = i

            def deleteNoteIdx(event, *args):
                bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                fsf.Wr.EntryInfoStructure.deleteNote(bookPath,
                                                     self.subsection,
                                                     self.imIdx,
                                                     str(event.widget.noteImIdx))
                try:
                    self.currEtr.pop(str(event.widget.noteImIdx))
                except:
                    pass
                self.render()

            deleteLabel.rebind([ww.currUIImpl.Data.BindID.mouse1], [deleteNoteIdx])
            _ucomw.bindChangeColorOnInAndOut(deleteLabel)
            deleteLabel.render()

        for mainLabel in mainLabels:
            mainLabel.render()

    def render(self, widjetObj=None, renderData=..., shouldScroll = True, **kwargs):
        global exImages
        exImages = []
        self.etrTexts =  _u.Token.NotDef.dict_t.copy()

        dummyPreLabel = tk.Label(self.scrollable_frame, height = 1000)
        dummyPreLabel.grid(row = 1, column=0)

        self.etrTexts = _u.Token.NotDef.dict_t.copy()

        if self.currEtr != _u.Token.NotDef.dict_t.copy():
            for k,v in self.currEtr.items():
                self.etrTexts[k] = [self.currEtr[k].getData(),
                                    self.currEtr[k].index(tk.INSERT)]

        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        self.scrollable_frame.focus_force()

        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        entryNotesPath = _upan.Paths.Entry.getAbs(bookPath, self.subsection, self.imIdx)

        self.addNotesNotes()

        super().render(widjetObj, renderData, **kwargs)

        if (self.latestWidgetToscrollTo != None) and (shouldScroll):
            self.__scrollIntoView(None, self.latestWidgetToscrollTo)


class MultilineDictHit_ETR(scrolledtext.ScrolledText):
    imIdx = None
    subsection = None
    etrWidget = None
    lineImIdx = None

    tocFrame = None

    row = None

    key = None

    width = 90

    localWord = False

    def __init__(self, patentWidget, row, column, text, key, tocFrame, *args, **kwargs):
        self.defaultText = text
        self.key = key
        self.tocFrame = tocFrame

        txt = ""
        lineLength = 0

        self.row = row

        txtList = text.split(" ")

        for w in txtList:
            lineLength += len(w.replace("\n", "")) + 1
            txt += w + " "

            if ("\n" in w) or (lineLength > self.width):
                if not("\n" in w):
                    txt += "\n"

                lineLength = 0

        newHeight = int(len(txt.split("\n"))) + 1
        self.column = column

        super().__init__(patentWidget, 
                         wrap = None, 
                         width = self.width, 
                         height = newHeight, 
                         *args, 
                         **kwargs)
        self.config(spacing1 = 10)
        self.config(spacing2 = 10)
        self.config(spacing3 = 12)
        self.insert(tk.END, text)

        self.config(height = newHeight)
        self.place(x = 0, y = 0)

        self.bind(ww.currUIImpl.Data.BindID.Keys.shenter, self.__wtireToWordDict)

    def __wtireToWordDict(self, *args):
        newText = self.getData()

        if not self.localWord:
            if wordd.readFromDict(self.key) == None:
                msg = f"Do you want to add to dictionary a word:\n\n'{self.key}'\n\nwith text:\n\n'{newText}'?"
                response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

                mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                            wf.Wr.MenuManagers.MathMenuManager)
                mainManager.show()

                notesManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                            wf.Wr.MenuManagers.NotesManager)
                notesManager.show()

                if not response:
                    return

            if newText == _u.Token.NotDef.str_t:
                msg = f"Do you want to delete from dictionary a word:\n\n'{self.key}'\n\nwith text:\n\n'{newText}'?"
                response = wf.Wr.MenuManagers.UI_GeneralManager.showNotification(msg, True)

                mainManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                            wf.Wr.MenuManagers.MathMenuManager)
                mainManager.show()

                notesManager = dt.AppState.UIManagers.getData("appCurrDataAccessToken",
                                                            wf.Wr.MenuManagers.NotesManager)
                notesManager.show()

                if not response:
                    return
                else:
                    wordd.deleteFromDict(self.key)
                    return


            wordd.writeToDict(self.key, newText)

            for i in range(len(self.tocFrame.dictHits)):
                self.tocFrame.dictHits[i][1] = False
                self.tocFrame.dictHits[i][0] = wordd.readFromDict(self.tocFrame.dictHits[i][2])
        else:
            entryWordDictDict:dict = fsf.Wr.EntryInfoStructure.readProperty(self.subsection,
                                                                       self.imIdx,
                                                                       fsf.Wr.EntryInfoStructure.PubProp.entryWordDictDict)
            entryWordDictDict[self.key] = newText
            fsf.Wr.EntryInfoStructure.updateProperty(self.subsection,
                                                    self.imIdx,
                                                    fsf.Wr.EntryInfoStructure.PubProp.entryWordDictDict,
                                                    entryWordDictDict)   
 
            self.tocFrame.dictHits = []
            self.tocFrame.dictHits.append([newText, False, self.key])
        
        self.tocFrame.render()

    def getData(self):
        try:
            binString = self.get('1.0', tk.END)
            if binString[-1] == "\n":
                return binString[:-1]
            return binString
        except:
            return _u.Token.NotDef.str_t

    def rebind(self, keys, funcs):
        for i in range(len(keys)):
            self.bind(keys[i], funcs[i])

    def render(self):
        self.grid(row = self.row, column = self.column)

class Dict_BOX(ww.currUIImpl.ScrollableBox,
                    dc.AppCurrDataAccessToken):
    subsection = None
    imIdx = None

    showLocalWord = False

    dictHits = []

    currNoteCopyIdx = _u.Token.NotDef.int_t

    noteIdxShownInText = []
    currEtr = _u.Token.NotDef.dict_t.copy()
    etrTexts = _u.Token.NotDef.dict_t.copy()

    displayedImages = []

    latestWidgetToscrollTo = None
    latestNoteIdxToscrollTo = None

    def __init__(self, parentWidget, prefix, windth = 730, height = 700):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 6, "columnspan" : 6, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : tk.W}
        }
        name = "_showNotesCurr_text"

        self.parent = parentWidget.widgetObj

        super().__init__(prefix,
                        name,
                        parentWidget,
                        renderData = data,
                        height = height,
                        width = windth,
                        makeScrollable = False)

        def on_vertical(event):
            self.canvas.yview_scroll(-1 * event.delta, 'units')

        self.container.bind_all('<Mod1-MouseWheel>', on_vertical)

    def __renderAfterRebuild(self, *args, **kwargs):
        def __internal(*args, **kwargs):
            noteIdx = kwargs["noteIdx"]
            t = _rebuildNote(*args, **kwargs)
            t.join()
            self.render()
            position = self.etrTexts[noteIdx][1]
            self.currEtr[noteIdx].focus_force()

            try:
                self.currEtr[noteIdx].mark_set("insert", position)
            except:
                pass
        Thread(target = __internal,
               args = args, 
               kwargs = kwargs).start()

    def __scrollIntoView(self, event, widget = None):
        try:
            posy = 0

            if widget == None:
                pwidget = event.widget
            else:
                pwidget = widget


            self.canvas.yview_scroll(-100, "units")
            self.canvas.update()
            pwidget.update()

            while pwidget != self.parent:
                posy += pwidget.winfo_y()
                pwidget = pwidget.master

            posy = 0

            if widget == None:
                pwidget = event.widget
            else:
                pwidget = widget

            while pwidget != self.parent:
                posy += pwidget.winfo_y()
                pwidget = pwidget.master

            pos = posy - self.scrollable_frame.winfo_rooty()
            height = self.scrollable_frame.winfo_height()
            self.canvas.yview_moveto((pos / height) - 0.008)
        except:
            pass

    def addDictResults(self):
        notes = fsf.Wr.EntryInfoStructure.readProperty(self.subsection,
                                                       self.imIdx, 
                                                       fsf.Wr.EntryInfoStructure.PubProp.entryNotesList)
        '''
        for each note add widgets:
        '''
        if len(self.dictHits) == 1:
            if self.dictHits[0][0] == None:
                self.dictHits[0][0] = "No word found"

                if self.dictHits[0][1]:
                    label = MultilineDictHit_ETR(self.scrollable_frame,
                                                    row = i,
                                                    column = 0,
                                                    text = "-1",
                                                    key = self.dictHits[0][2],
                                                    tocFrame = self)
                else:
                    label = DictText(self.scrollable_frame, 
                                    "__dictResult_test_" + str(0), 
                                    text = "No word found")
                    label.tocFrame = self
                label.render()
                return
                

        for i in range(len(self.dictHits)):
            if self.dictHits[i][1]:
                label = MultilineDictHit_ETR(self.scrollable_frame,
                                                 row = i,
                                                 column = 0,
                                                 text = self.dictHits[i][0],
                                                 key = self.dictHits[i][2],
                                                 tocFrame = self)
            else:
                label = DictText(self.scrollable_frame, 
                                 "__dictResult_test_" + str(i), 
                                 text = self.dictHits[i][0])
                label.tocFrame = self
            label.render()

    def addLocalDictResults(self):
        '''
        for each note add widgets:
        '''

        if self.dictHits[0][1]:
            label = MultilineDictHit_ETR(self.scrollable_frame,
                                                row = 0,
                                                column = 0,
                                                text = self.dictHits[0][0],
                                                key = self.dictHits[0][2],
                                                tocFrame = self)
            label.subsection = self.subsection
            label.imIdx = self.imIdx
            label.localWord = True
        else:
            label = DictText(self.scrollable_frame, 
                                "__dictResult_test_" + str(0), 
                                text = self.dictHits[0][0],
                                localWord = True)
            label.tocFrame = self
        
        label.render()

    def render(self, widjetObj=None, renderData=..., shouldScroll = True, **kwargs):
        global exImages
        exImages = []
        self.etrTexts =  _u.Token.NotDef.dict_t.copy()

        dummyPreLabel = tk.Label(self.scrollable_frame, height = 1000)
        dummyPreLabel.grid(row = 1, column=0)

        self.etrTexts = _u.Token.NotDef.dict_t.copy()

        if self.currEtr != _u.Token.NotDef.dict_t.copy():
            for k,v in self.currEtr.items():
                self.etrTexts[k] = [self.currEtr[k].getData(),
                                    self.currEtr[k].index(tk.INSERT)]

        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        self.scrollable_frame.focus_force()

        if not self.showLocalWord:
            self.addDictResults()
        else:
            self.addLocalDictResults()

        super().render(widjetObj, renderData, **kwargs)

        if (self.latestWidgetToscrollTo != None) and (shouldScroll):
            self.__scrollIntoView(None, self.latestWidgetToscrollTo)

    def receiveNotification(self, broadcasterType, data, *args):
        if broadcasterType == SearchDict_ETR:
            self.showLocalWord = False
            self.dictHits = data[0]
        elif broadcasterType == DictText_LBL:
            self.showLocalWord = True
            self.dictHits = [data[0]]

        self.render()

class NotesRoot(ww.currUIImpl.RootWidget):
    NotesBox = None
    AddNotesBTN = None

    def __init__(self, width, height, bindCmd=...):
        super().__init__(width, height)