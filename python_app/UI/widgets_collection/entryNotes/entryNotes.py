from threading import Thread
from PIL import Image

import UI.widgets_wrappers as ww
import UI.widgets_facade as wf
import UI.widgets_collection.utils as _ucomw
import UI.widgets_collection.common as comw
import UI.factories.factoriesFacade as wff

import _utils._utils_main as _u
import _utils.pathsAndNames as _upan
import data.constants as dc
import file_system.file_system_facade as fsf
import settings.facade as sf
import outside_calls.outside_calls_facade as ocf
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
            self.image = ww.currUIImpl.UIImage(pilIm)
            return super().__init__(prefix, name, root, renderData, image = self.image, padding = padding)
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
            self.currEtr[noteIdx].forceFocus()

            self.currEtr[noteIdx].setPosition(position.split(".")[0],
                                              position.split(".")[1])

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


            self.scrollY(-100)
            self.update()
            pwidget.update()

            while pwidget != self.parent:
                posy += pwidget.getYCoord()
                pwidget = pwidget.getParent()

            posy = 0

            if widget == None:
                pwidget = event.widget
            else:
                pwidget = widget

            while pwidget != self.parent:
                posy += pwidget.getYCoord()
                pwidget = pwidget.getParent()

            pos = posy - self.yPosition()
            height = self.getFrameHeight()
            self.moveY((pos / height) - 0.008)
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
            mainLabels.append(comw.TOCFrame(self.scrollable_frame, 
                                            "notesMainNoteImageFRM_" + str(i),
                                            i, 0, 1)
                              )

        imageLables = []
        entryImagesFactory = wff.EntryImagesFactory(self.subsection, self.imIdx)
        imLabel = entryImagesFactory.produceEntryMainImageWidget(rootLabel = mainLabels[0],
                                                                imPadLeft = 0,
                                                                row = 0,
                                                                columnspan = 1,
                                                                column = 1)

        imageLables.append(imLabel)
        imLabel.forceFocus()

        def skipProofs(*args):
           return False
        

        exImLabels = entryImagesFactory.produceEntryExtraImagesWidgets(mainLabels[1:], 
                                                                       skippConditionFn = skipProofs,
                                                                       imPadLeft = 0,
                                                                       createExtraWidgets = False)
  
        imageLables.extend(exImLabels)

        for i in range(len(imageLables)):
            imageLables[i].render()

            '''
            add
            '''
            addLabel = comw.TOCLabelWithClick(mainLabels[i], "_addNote_" + str(i), 
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
                           [lambda e, idx = str(i), *args: __showTextOrImage(idx), self.__scrollIntoView])
                labelToScrollTo = label
            else:
                label = comw.TOCFrame(mainLabels[i], 
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

                labETR = comw.MultilineText_ETR(label, "notesImageETR_", 1, 1, i, text)
                self.currEtr[str(i)] = labETR

                labRebuild = comw.TOCLabelWithClick(label, "notesImageRebuild_" + str(i), 
                                                2, 0, text = "Rebuild")
                labRebuild.noteImIdx = str(i)

                def rebuildETRImage(event, *args):
                    widgetnoteImIdx = event.widget.noteImIdx
                    text = self.currEtr[widgetnoteImIdx].getData()

                    bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
                    self.noteIdxShownInText.remove(widgetnoteImIdx)

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
            deleteLabel = comw.TOCLabelWithClick(mainLabels[i], "_deleteNote_" + str(i), 
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

    def render(self, shouldScroll = True):
        self.etrTexts =  _u.Token.NotDef.dict_t.copy()

        self.etrTexts = _u.Token.NotDef.dict_t.copy()

        if self.currEtr != _u.Token.NotDef.dict_t.copy():
            for k,v in self.currEtr.items():
                self.etrTexts[k] = [self.currEtr[k].getData(),
                                    self.currEtr[k].getCurrCursorPosition()]

        for w in self.getChildren().copy():
            w.destroy()

        self.forceFocus()

        bookPath = sf.Wr.Manager.Book.getCurrBookFolderPath()
        entryNotesPath = _upan.Paths.Entry.getAbs(bookPath, self.subsection, self.imIdx)

        self.addNotesNotes()

        super().render(self.renderData)

class EntryNotesRoot(ww.currUIImpl.RootWidget):
    NotesBox = None
    AddNotesBTN = None

    def __init__(self, width, height, bindCmd=...):
        super().__init__(width, height)