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



def _rebuildNote(*args, **kwargs):
    '''
        used for multithreaded note rebuild
    '''
    t = Thread(target= fsf.Wr.EntryInfoStructure.rebuildNote, 
            args = (args))
    t.start()
    return t

class HideEntryNotesWindow_BTN(ww.currUIImpl.Button,
                              dc.AppCurrDataAccessToken):
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 2, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }
        text = "Hide"
        name = "_HideEntryNotesWindow_BTN"
        super().__init__(prefix, 
                        name, 
                        text, 
                        patentWidget, 
                        renderData, 
                        self.cmd)

    def cmd(self):
        notesManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.EntryNotesManager)
        notesManager.hide()

        msg = "\
After updating the notes for \n\
'{0}':'{1}'.".format(self.subsection, self.imIdx)
        _u.log.autolog(msg)
        ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)

class NotesImageLabel(ww.currUIImpl.Label):
    noteImIdx = None

    def __init__(self, root, prefix, subsection, imIdx, 
                 noteIdx, row, column, text = _u.Token.NotDef.str_t, padding = [0, 0, 0, 0]):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : column, "row" : row},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
        }

        name = "_NotesImageLabel_"

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
            return super().__init__(prefix, name, root, renderData, image = img, padding = padding)
        else:
            return super().__init__(prefix, name, root, renderData, text = text, padding = padding)




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

    def __init__(self, parentWidget, prefix, windth = 730, height = 730):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 1, "columnspan" : 6, "rowspan": 1},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.W}
        }
        name = "_showNotesCurr_text"

        super().__init__(prefix,
                        name,
                        parentWidget,
                        renderData = data,
                        height = height,
                        width = windth,
                        makeScrollable = False)

        def on_vertical(event):
            self.scrollY(-1 * event.delta)

        self.rebind(['<Mod1-MouseWheel>'], [on_vertical])

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
                if "tkinter." not in str(type(pwidget)):
                    posy += pwidget.getYCoord()
                    pwidget = pwidget.getParent()
                else:
                    posy += pwidget.winfo_y()
                    pwidget = pwidget.master

            posy = 0

            if widget == None:
                pwidget = event.widget
            else:
                pwidget = widget

            while pwidget != self.parent:
                if "tkinter." not in str(type(pwidget)):
                    posy += pwidget.getYCoord()
                    pwidget = pwidget.getParent()
                else:
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
        imLabel = _ucomw.addMainEntryImageWidget(mainLabels[0], 
                                                self.subsection, self.imIdx,
                                                imPadLeft = 0, 
                                                displayedImagesContainer = self.displayedImages,
                                                row = 0,
                                                columnspan = 1,
                                                column = 1)
        imageLables.append(imLabel)
        imLabel.focus_force()

        def skipProofs(*args):
           return False
        
        exImLabels = _ucomw.addExtraEntryImagesWidgets(mainLabels[1:], 
                                                       self.subsection, self.imIdx,
                                                       imPadLeft = 0, 
                                                       displayedImagesContainer = self.displayedImages,
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

            def __showTextOrImage(noteImIdx, *args):
                self.latestNoteIdxToscrollTo = noteImIdx
                bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                widgetnoteImIdx = str(noteImIdx)

                if widgetnoteImIdx in self.noteIdxShownInText:
                    self.noteIdxShownInText.remove(widgetnoteImIdx)
                    text = self.currEtr[widgetnoteImIdx].getData()

                    if text != self.currEtr[widgetnoteImIdx].defaultText:
                        _rebuildNote(self.subsection,
                                            self.imIdx,
                                            noteImIdx,
                                            text,
                                            bookPath)

                    self.currEtr.pop(widgetnoteImIdx)
                else:
                    self.noteIdxShownInText.append(str(noteImIdx))

                self.render()

            # image / text
            if str(i) not in self.noteIdxShownInText:
                label = NotesImageLabel(mainLabels[i], "notesImageIMG_" + str(i), 
                                            self.subsection, self.imIdx, i,
                                            padding = [60, 0, 0, 0], 
                                            row = 1, column = 1)
                label.render()
                label.rebind([ww.currUIImpl.Data.BindID.mouse2, ww.currUIImpl.Data.BindID.mouse1], 
                           [lambda *args: __showTextOrImage(i), self.__scrollIntoView])
                labelToScrollTo = label
            else:
                label = _ucomw.TOCFrame(mainLabels[i], 
                                "notesImageFRM_" + str(i),
                                1, 1, 1
                                )
                labIm = NotesImageLabel(label, "notesImageIMG_" + str(i), 
                                            self.subsection, self.imIdx, i,
                                            row = 0, column = 1)

                text = ""
                if str(i) in list(self.etrTexts.keys()):
                    text = self.etrTexts[str(i)][0]
                else:
                    text = notes[str(i)]

                labETR = _ucomw.MultilineText_ETR(label, "notesImageETR_", 1, 1, i, text)
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
                labIm.rebind([ww.currUIImpl.Data.BindID.mouse2, ww.currUIImpl.Data.BindID.mouse1],
                             [lambda *args: __showTextOrImage(i), self.__scrollIntoView])
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

        self.etrTexts = _u.Token.NotDef.dict_t.copy()

        if self.currEtr != _u.Token.NotDef.dict_t.copy():
            for k,v in self.currEtr.items():
                self.etrTexts[k] = [self.currEtr[k].getData(),
                                    self.currEtr[k].index(ww.currUIImpl.TextInsertPosition.CURRENT)]

        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        self.scrollable_frame.focus_force()

        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        entryNotesPath = _upan.Paths.Entry.getAbs(bookPath, self.subsection, self.imIdx)

        self.addNotesNotes()

        super().render(widjetObj, renderData, **kwargs)

        if (self.latestWidgetToscrollTo != None) and (shouldScroll):
            self.__scrollIntoView(None, self.latestWidgetToscrollTo)


class EntryNotesRoot(ww.currUIImpl.RootWidget):
    NotesBox = None
    AddNotesBTN = None

    def __init__(self, width, height, bindCmd=...):
        super().__init__(width, height)