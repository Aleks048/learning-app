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
import wordDict.wordDict as wordd



class DictLabel(comw.TOCLabelWithClick):
    def __init__(self, root, prefix, row, column, 
                 columnspan=1, sticky=ww.currUIImpl.Orientation.NW, 
                 padding=[0, 0, 0, 0], image=None, text=None):
        self.dictWord = None
        self.dictText = None
        
        super().__init__(root, prefix, 
                         row, column, columnspan, 
                         sticky, padding, image, text)

class NotesImage(ww.currUIImpl.Frame):
    displayedImages = []
    subsection = None
    entryIdx = None

    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 0, "columnspan": 6},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.NW}
        }
        name = "_notesImage_LBL"

        super().__init__(prefix, 
                        name,
                        parentWidget, 
                        renderData = data)
    
    def render(self, **kwargs):
        for child in self.getChildren().copy():
            child.destroy()

        entryImagesFactory = wff.EntryImagesFactory(self.subsection, self.entryIdx)
        self.imLabel = entryImagesFactory.produceEntryMainImageWidget(rootLabel = self,
                                                                        imPadLeft = 120)

        self.imLabel.render()
        self.imLabel.forceFocus()

        def skipProofs(subsection, imIdx, i):
           return "proof" in fsf.Data.Sec.extraImagesDict(subsection)[imIdx][i].lower()

        exImLabels = entryImagesFactory.produceEntryExtraImagesWidgets(rootLabel = self,
                                                                        imPadLeft = 120,
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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
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
        mainTOCManager = dt.AppState.UIManagers.getData(self.appCurrDataAccessToken,
                                                          wf.Wr.MenuManagers.MainTOCManager)
        mainTOCManager.moveTocToEntry(self.subsection, self.imIdx)

class AddDictHitToEntry_BTN(ww.currUIImpl.Button,
                              dc.AppCurrDataAccessToken):
    subsection = None
    imIdx = None

    def __init__(self, patentWidget, prefix):
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : 0, "row" : 2},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.N}
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

class DictText(ww.currUIImpl.Label):
    '''
    This used to show the text retrieved from the dict
    '''
    
    tocFrame = None
    text = None

    def __showAsETR(self, *args):
        dictHits = self.tocFrame.dictHits

        for i in range(len(dictHits)):
            if dictHits[i][0] == self.text:
                dictHits[i][1] = True
        
        self.tocFrame.render()

    def __init__(self, root, prefix, row = 0, column = 0, columnspan = 1, sticky = ww.currUIImpl.Orientation.NW, 
                 text = "", localWord = False, *args, **kwargs) -> None:
        data = {
            ww.Data.GeneralProperties_ID : {"column" : column, "row" : row, "columnspan": columnspan},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : sticky}
        }

        name = "DictHit_"

        self.text = text

        super().__init__(prefix, 
                        name,
                        root, 
                        renderData = data, 
                        text = text,
                        bindCmd = self.__bindCmd)

        self.setWrapLength(730)
        if not localWord:
            self.setStyle("Dict.TLabel")
        else:
            self.setStyle("DictLoc.TLabel")
    
    def __bindCmd(self):
        return [ww.currUIImpl.Data.BindID.mouse2],[self.__showAsETR]

class DictText_LBL(ww.currUIImpl.Label):
    textWidgets = [] 
    subsection = None
    imIdx = None

    def __init__(self, parentWidget, prefix):
        data = {
            ww.Data.GeneralProperties_ID : {"column" : 0, "row" : 4, "columnspan": 6},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.W}
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
            textWidget = DictLabel(self, "_DictTextLabelText_" + str(column), 
                                    row = 0, column = column, text = "[" + k)
            textWidget.dictWord = k
            textWidget.dictText = v
            textWidget.rebind([ww.currUIImpl.Data.BindID.mouse1], [self.__showWord])
            _ucomw.bindChangeColorOnInAndOut(textWidget)
            textWidget.render()
            self.textWidgets.append(textWidget)

            textDelWidget = DictLabel(self, "_DictTextdelLabelText_" + str(column), 
                                        row = 0, column = column + 1, text = "d]")
            textDelWidget.dictWord = k
            _ucomw.bindChangeColorOnInAndOut(textDelWidget)
            textDelWidget.rebind([ww.currUIImpl.Data.BindID.mouse1], [self.__delWord])
            textDelWidget.render()
            self.textWidgets.append(textDelWidget)

            column += 2

    def render(self):
        for w in self.textWidgets:
            w.hide()
        self.textWidgets = []
        self.getWords()
        return super().render()

class MultilineDictHit_ETR(ww.currUIImpl.MultilineText):
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
        renderData = {
            ww.Data.GeneralProperties_ID :{"column" : row, "row" : column},
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.W}
        }

        name = "_MultilineDictHit_ETR_"

        prefix = str(row) + str(column)

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

        super().__init__(prefix,
                         name,
                         patentWidget, 
                         renderData,
                         text = text,
                         wrap = None, 
                         width = self.width, 
                         height = newHeight, 
                         *args, 
                         **kwargs)

        self.rebind([ww.currUIImpl.Data.BindID.Keys.shenter], [self.__wtireToWordDict])

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
            ww.TkWidgets.__name__ : {"padx" : 0, "pady" : 0, "sticky" : ww.currUIImpl.Orientation.W}
        }
        name = "_showNotesCurr_text"

        self.parent = parentWidget

        super().__init__(prefix,
                        name,
                        parentWidget,
                        renderData = data,
                        height = height,
                        width = windth,
                        makeScrollable = False)

        def on_vertical(event):
            self.scrollY(-1 * event.delta)

        self.rebind([ww.currUIImpl.Data.BindID.cmdModwheel], [on_vertical])

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

    def render(self, shouldScroll = True):
        self.etrTexts =  _u.Token.NotDef.dict_t.copy()

        self.etrTexts = _u.Token.NotDef.dict_t.copy()

        if self.currEtr != _u.Token.NotDef.dict_t.copy():
            for k,v in self.currEtr.items():
                self.etrTexts[k] = [self.currEtr[k].getData(),
                                    self.currEtr[k].index(ww.currUIImpl.TextInsertPosition.CURRENT)]

        for w in self.getChildren().copy():
            w.destroy()

        self.forceFocus()

        if not self.showLocalWord:
            self.addDictResults()
        else:
            self.addLocalDictResults()

        super().render(self.renderData)

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