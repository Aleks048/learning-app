import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
from PIL import ImageTk
import inspect

import os
from ctypes import c_void_p, cdll
import vlc

from AppKit import NSPasteboard, NSStringPboardType

import _utils.logging as log
import _utils._utils_main as _u
import UI.widgets_data as wd
import outside_calls.outside_calls_facade as ocf
import settings.facade as sf
import file_system.file_system_facade as fsf

class DataContainer_Interface: 
    def __init__(self):
        self.dataVar = None

    def getDataObject(self):
        return self.dataVar

    def getData(self, **kwargs):
        raise NotImplementedError()
        
    def setData(self, data, **kwargs):
        raise NotImplementedError()
    
    def setOnCmdONDataChange(self, cmd, **kwargs):
        raise NotImplementedError()

class HasChildren_Interface:
    def getChildren(self, **kwargs):
        raise NotImplementedError()

class RenderableWidget_Interface:
    def render(self, **kwargs):
        raise NotImplementedError()
    def hide(self, **kwargs):
        raise NotImplementedError()

class BindableWidget_Interface:
    def bind(self, **kwargs):
        raise NotImplementedError()

class HasListenersWidget_Interface:
    def __init__(self):
        self.listeners = []

    def addListenerWidget(self, widget, **kwargs):
        self.listeners.append(widget)
    
    def notifyAllListeners(self, *args, **kwargs):
        for widget in self.listeners:
            widget.receiveNotification(type(self), *args, **kwargs)
    
    def notify(self, reciverWidgetType, *args, **kwargs):
        for widget in self.listeners:
            if type(widget) == reciverWidgetType:
                return widget.receiveNotification(type(self), *args, **kwargs)

class Notifyable_Interface:
    def receiveNotification(self, broadcasterType) -> None:
        raise NotImplementedError

class Datable_Interface:
    data = {}

    def __init__(self, data) -> None:
        self.data = data

    def setData(self, key, newData) -> None:
        self.data[key] = newData

    def getData(self, key) -> None:
        if key in list(self.data.keys()):
            return self.data[key]
        else:
            return _u.Token.NotDef.no_t

class EventGeneratable_Interface:
    def generateEvent(self, event, *args, **kwars) -> None:
        raise NotImplementedError


class DataTranslatable_Interface:
    def translateExtraBuildOptions(extraOptions):
        kwargs = {}
        if extraOptions != {}:
            kwargs = {**extraOptions[Data.GeneralProperties_ID], **extraOptions[currUIImpl.__name__]}
            if Data.CommonTextColor_ID in kwargs:
                kwargs[currUIImpl.Data.textColor_ID] = kwargs.pop(Data.CommonTextColor_ID)    
        return kwargs

    def translateRenderOptions(renderOptions):
        kwargs = {}
        if renderOptions != {}:
            kwargs = {**renderOptions[Data.GeneralProperties_ID], **renderOptions[currUIImpl.__name__]}
        return kwargs

class Data:
    CommonTextColor_ID = "textColor"
    GeneralProperties_ID = "general"
    args = "args"
    widgetsWidth = "width"

class TkWidgets (DataTranslatable_Interface):
    tkinterVersion = tk.TkVersion

    s = ttk.Style()
    s.theme_use("default")
    # Create style used by default for all Frames
    s.configure('Dict.TLabel', background = "#394d43")
    s.configure('DictLoc.TLabel', background = "#7c3b3b")
    s.configure('EntryText.TLabel', background = "#394d43")
    s.configure('TLabel', foreground = "#ffffff", background = "#323232")
    s.configure('TFrame', background = "#323232")
    s.configure("TMenubutton", background="#323232")
    s.configure("Canvas.TMenubutton", width = 5, 
                                      background = "#3E4742", 
                                      activebackground = "#33B5E5", 
                                      relief = tk.FLAT)
    s.configure('TCheckbutton', background = '#323232')
    s.configure("Horizontal.TScrollbar", gripcount=0, borderwidth = 0.1, arrowsize = 0.1,
                    background="#323262", darkcolor="#323232", lightcolor="#323232",
                    troughcolor="#323232", bordercolor="#323232", arrowcolor="#323232")

    s.configure("Vertical.TScrollbar", gripcount=0, borderwidth = 0.1, arrowsize = 0.1,
                    background="#323262", darkcolor="#323232", lightcolor="#323232",
                    troughcolor="#323232", bordercolor="#323232", arrowcolor="#323232")

    # Create style for the first frame
    s.configure('Frame1.TFrame', background='red')

    s.configure('green/black.TButton', 
                foreground = 'black',
                background = '#323262',
                borderwidth = 1,
                focusthickness = 1)


    class Data:
        textColor_ID = "fg"
        tk = tk.Toplevel()
        class BindID:
            focusIn = "<FocusIn>"
            focusOut = "<FocusOut>"
            allKeys = "<Key>"
            mouse1 = "<Button-1>"
            cmdMouse1 = "<Mod1-Button-1>"
            shmouse1 = "<Shift-Button-1>"
            mouse2 = "<Button-2>"
            mouse3 = "<Button-3>"

            enterWidget = "<Enter>"
            leaveWidget = "<Leave>"

            render = "<Map>"

            customTOCMove = "<<TOCMove>>"

            class Keys:
                shspace = "<Shift-space>"
                enter = "<Return>"
                shenter = "<Shift-Return>"
                cmdenter = "<Mod1-Return>"
                cmdshs = "<Mod1-S>"
                cmdb = "<Mod1-b>"
                cmdl = "<Mod1-l>"
                cmdshc = "<Mod1-C>"
                cmddc = "<Mod1-c><Mod1-c>"
                cmdshi = "<Mod1-I>"
                cmdsht = "<Mod1-T>"
                cmdt = "<Mod1-t>"
                cmdn = "<Mod1-n>"
                cmdshn = "<Mod1-N>"
                cmdd = "<Mod1-d>"
                cmde = "<Mod1-e>"
                cmdshe = "<Mod1-E>"
                cmdp = "<Mod1-p>"
                cmdr = "<Mod1-r>"
                cmdshp = "<Mod1-P>"
                cmdu = "<Mod1-u>"
                ctrlv = "<Control-v>"
                escape = "<Escape>"
                shup = "<Shift-Up>"
                up = "<Up>"
                shright = "<Shift-Right>"
                right = "<Right>"
                shleft = "<Shift-Left>"
                left = "<Left>"
                shdown = "<Shift-Down>"
                down = "<Down>"
                focusIn = "<FocusIn>"
                focusOut = "<FocusOut>"

        class Styles:
            entryText = "EntryText.TLabel"
    class Orientation:
        N = tk.N
        NW = tk.NW
        NE = tk.NE
        E = tk.E
        W = tk.W

    class TextInsertPosition:
        END = tk.END
        CURRENT = tk.INSERT
        WRAPPER_WORD=tk.WORD

    class DataContainer_Interface_Impl(DataContainer_Interface):
        def __init__(self, *args, **kwargs):
            super().__init__()
            self.dataVar = tk.Variable()

        def getData(self, **kwargs):
            return self.dataVar.get()
        
        def setData(self, newData, **kwargs):
            self.dataVar.set(newData)

        def setOnCmdONDataChange(self, cmd, **kwargs):
            self.dataVar.trace_variable('w', cmd)

    class HasChildren_Interface_Impl(HasChildren_Interface):
        def __init__(self, widget = None):
            self.widget = widget

            self.children = set()
        
        def getChildren(self):
            return self.widget.children
        
        def addChild(self, child):
            if child not in self.children:
                self.children.add(child)
        
        def removeChild(self, child):
            gChildren = child.children.copy()
            for gChild in gChildren:
                child.removeChild(gChild)
            
            self.children.discard(child)                

        def getParent(self):
            return self.widget.rootWidget

        def getGrandParent(self):
            return self.widget.rootWidget.rootWidget


    class RenderableWidget_Interface_Impl(RenderableWidget_Interface):
        def __init__(self, widget, renderData = {}):
            self.wasRendered = False
            self.widget = widget
            self.renderData = renderData

            if not issubclass(type(self.widget), TkWidgets.RootWidget):
                self.widget.rootWidget.addChild(self.widget)

        def render(self, renderData = {}):
            if self.wasRendered:
                self.__render(**self.renderData)
                self.wasRendered = True
            else:
                if (self.renderData == {}) or (renderData != {}):
                    self.__render(**renderData)
                else:
                    self.__render(**self.renderData)
                
                self.wasRendered = True

            if not issubclass(TkWidgets.RootWidget, type(self.widget)):
                self.widget.rootWidget.addChild(self.widget)

        def __render(self, **kwargs):
            self.widget.widgetObj.grid(**kwargs)
        
        def hide(self, **kwargs):
            if not issubclass(TkWidgets.RootWidget, type(self.widget)):
                self.widget.rootWidget.removeChild(self.widget)

            self.widget.widgetObj.grid_remove()
            self.wasRendered = False


        def delete(self, **kwargs):
            self.widget.widgetObj.grid_forget()
            self.wasRendered = False

            if not issubclass(TkWidgets.RootWidget, type(self.widget)):
                self.widget.rootWidget.removeChild(self.widget)
        
        def destroy(self):
            self.widget.widgetObj.destroy()

            if not issubclass(TkWidgets.RootWidget, type(self.widget)):
                self.widget.rootWidget.removeChild(self.widget)

        def update(self):
            self.widget.widgetObj.update()

        def getYCoord(self):
            return self.widget.widgetObj.winfo_y()

        def forceFocus(self):
            self.widget.widgetObj.focus_force()
        
        def setStyle(self, style):
            self.widget.widgetObj.configure(style = style)


    class EventGeneratable_Interface_Impl(EventGeneratable_Interface):
        def __init__(self, widgetObj = None,  *args, **kwargs):
            self.widgetObj = widgetObj
            super().__init__()

        def generateEvent(self, event, *args, **kwargs) -> None:
            self.widgetObj.event_generate(event, *args, **kwargs)


    class HasListenersWidget_Interface_Impl(HasListenersWidget_Interface):
        def __init__(self, *args, **kwargs):
            super().__init__()

    class BindableWidget_Interface_Impl(BindableWidget_Interface):
        class Data:
            def __init__(self, event, callerObject):
                self.widget = callerObject
                self.event = event
                self.type = event.type
                self.keysym = event.keysym

        def __init__(self, callingObject = None, 
                    bindCmd = lambda *args: (None, None) , *args, **kwargs):
            self.bindCmd = bindCmd
            self.callingObject = callingObject
            self.bind_all_keys = ["<Delete>", 
                                  "<Mod1-s>",
                                  '<Mod1-MouseWheel>',
                                  ]

            self.root_bind_all_keys = [TkWidgets.Data.BindID.Keys.left,
                                       TkWidgets.Data.BindID.Keys.shleft,
                                       TkWidgets.Data.BindID.Keys.up,
                                       TkWidgets.Data.BindID.Keys.down,
                                       TkWidgets.Data.BindID.Keys.right,
                                       TkWidgets.Data.BindID.Keys.shright,
                                       TkWidgets.Data.BindID.Keys.shenter,
                                       TkWidgets.Data.BindID.Keys.escape,
                                       TkWidgets.Data.BindID.Keys.shenter, 
                                       TkWidgets.Data.BindID.Keys.shspace,
                                       TkWidgets.Data.BindID.Keys.shleft,
                                       TkWidgets.Data.BindID.Keys.shright, 
                                       TkWidgets.Data.BindID.Keys.cmdu, 
                                       TkWidgets.Data.BindID.Keys.cmdr]
        
        def bind(self):
            keys, cmds = self.bindCmd()
            if keys != None:
                self.rebind(keys, cmds)

        def rebind(self, keys, cmds):
            for i in range(len(keys)):
                key = keys[i]
                cmd = cmds[i]
                
                if "widgetObj" in dir(self.callingObject):
                    shouldUseBindAll = (type(self.callingObject.widgetObj) == tk.Canvas) and (key in self.bind_all_keys)
                else:
                    shouldUseBindAll = (type(self.callingObject) == tk.Canvas) and (key in self.bind_all_keys)

                shouldRootUseBindAll = ("root" in str(type(self.callingObject)).lower()) and (key in self.root_bind_all_keys)

                shouldUseBindAll = (key == TkWidgets.Data.BindID.allKeys)\
                                   or shouldUseBindAll or shouldRootUseBindAll

                if "widgetObj" in dir(self.callingObject):
                    if cmd.__name__ in dir(self.callingObject):
                        #if we are binding a call to the function class
                        name:str = cmd.__name__
                        l = lambda event, name = name : getattr(self.callingObject, name)(event)
                        if shouldUseBindAll:
                            self.callingObject.widgetObj.bind_all(keys[i], l)
                        else:
                            self.callingObject.widgetObj.bind(keys[i], l)
                    else:
                        if shouldUseBindAll:
                            self.callingObject.widgetObj.bind_all(key, 
                                lambda event, cmd = cmd: cmd(TkWidgets.BindableWidget_Interface_Impl.Data(event, self.callingObject)))
                        else:
                            self.callingObject.widgetObj.bind(key, 
                                lambda event, cmd = cmd: cmd(TkWidgets.BindableWidget_Interface_Impl.Data(event, self.callingObject)))
                else:
                    if shouldUseBindAll:
                        self.callingObject.bind_all(key, 
                            lambda event, cmd = cmd: cmd(TkWidgets.BindableWidget_Interface_Impl.Data(event, self.callingObject)))
                    else:
                        self.callingObject.bind(key, 
                            lambda event, cmd = cmd: cmd(TkWidgets.BindableWidget_Interface_Impl.Data(event, self.callingObject)))

        def unbind(self, keys):
            for i in range(len(keys)):
                key = keys[i]

                self.widgetObj.unbind(key)
                self.widgetObj.unbind_all(key)

    class Button (Notifyable_Interface,
                HasChildren_Interface_Impl, 
                RenderableWidget_Interface_Impl,
                HasListenersWidget_Interface_Impl,
                BindableWidget_Interface_Impl):
        def __init__(self, 
                    prefix, name, 
                    text, 
                    rootWidget, 
                    renderData, 
                    cmd, 
                    extraOptions = {},
                    bindCmd = lambda *args: (None, None)):
            
            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)
            
            self.name = prefix.lower() + name
            self.text = text
            self.rootWidget = rootWidget
            self.cmd = cmd

            if "_CanvasButton_".lower() in name.lower():
                # this is needed since ttk button does not provide the y coordinates correctly
                self.widgetObj = tk.Button(self.rootWidget.widgetObj, 
                                    name = self.name,
                                    text= self.text,
                                    **extraOptions
                                    )
            else:
                self.widgetObj = ttk.Button(self.rootWidget.widgetObj, 
                                    name = self.name,
                                    text= self.text,
                                    style='green/black.TButton',
                                    **extraOptions
                                    )

            def btnCmd():
                self.cmd()
            
            self.widgetObj.configure(command = lambda : btnCmd())     
                        
            caller = inspect.stack()[1].frame
            localvars = caller.f_locals
            child = localvars['self']
            
            TkWidgets.HasChildren_Interface_Impl.__init__(self, widget = self)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widget = self, renderData = self.renderData)
            TkWidgets.HasListenersWidget_Interface_Impl.__init__(self, widgetObj = self.widgetObj, bindCmd = bindCmd)
            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd, callingObject = self.widgetObj)
            Notifyable_Interface.__init__(self)

            super().bind()

        def updateLabel(self, newText):
            self.text = newText
            self.widgetObj.configure(text = newText)
        
        def getLabel(self):
            return self.widgetObj["text"]

        def setStyle(self, style):
            if "_CanvasButton_".lower() in self.name.lower():
                pass
            else:
                super().setStyle(style)


    class OptionMenu (Notifyable_Interface,
                    DataContainer_Interface_Impl,
                    HasChildren_Interface_Impl, 
                    RenderableWidget_Interface_Impl,
                    HasListenersWidget_Interface_Impl,
                    BindableWidget_Interface_Impl):
        def __init__(self, prefix, name, 
                    listOfOptions, 
                    rootWidget, 
                    renderData, 
                    cmd, 
                    extraOptions = {},
                    defaultOption = None,
                    bindCmd = lambda *args: (None, None)):
            
            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)

            self.name = prefix.lower() + name
            self.listOfOptions = list(listOfOptions)
            self.rootWidget = rootWidget
            self.cmd = cmd

            TkWidgets.DataContainer_Interface_Impl.__init__(self)

            if "widgetObj" in dir(self.rootWidget):
                self.widgetObj = ttk.Frame(self.rootWidget.widgetObj, 
                                      name = self.name)
            else:
                self.widgetObj = ttk.Frame(self.rootWidget, 
                                      name = self.name)

            if defaultOption == None:
                defaultOption = self.listOfOptions[0]

            optionMenu = ttk.OptionMenu(self.widgetObj, 
                                        self.getDataObject(), 
                                        defaultOption,
                                        *self.listOfOptions, 
                                        command= lambda _: cmd(),
                                        **extraOptions)
            self.optionMenu = optionMenu
            self.optionMenu.grid(column= 0, row = 0)
                        
            caller = inspect.stack()[1].frame
            localvars = caller.f_locals
            child = localvars['self']
            
            TkWidgets.HasChildren_Interface_Impl.__init__(self, widget = self)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widget = self, renderData = self.renderData)
            TkWidgets.HasListenersWidget_Interface_Impl.__init__(self, widgetObj = self.widgetObj, bindCmd = bindCmd)
            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd, callingObject = child)
            Notifyable_Interface.__init__(self)

            self.setData(defaultOption)
            super().bind()
                    
        # def render(self, **kwargs):
        #     super().render(self.optionMenu, column = 0, row = 0)
        #     return super().render()

        def updateOptions(self, newMenuOptions):
            def optionChoosingCallback(value):
                self.setData(value)
                self.cmd()

            if newMenuOptions == None:
                # TODO: should check what conditions lead to None newMenuOptions
                return
            
            if newMenuOptions[0].isnumeric():
                newMenuOptions.sort(key = int)  
            
            for om in self.getChildren():
                om['menu'].delete(0, 'end')
                for choice in newMenuOptions:
                    om['menu'].add_command(label=choice, 
                                        command= lambda value = choice: optionChoosingCallback(value))
            self.setData(newMenuOptions[0])
    
    class TextEntry (Notifyable_Interface,
                    DataContainer_Interface_Impl,
                    HasChildren_Interface_Impl, 
                    RenderableWidget_Interface_Impl,
                    HasListenersWidget_Interface_Impl,
                    BindableWidget_Interface_Impl):
        def __init__(self, 
                    prefix: str, 
                    name : str,
                    rootWidget, 
                    renderData : dict,
                    extraOptions = {},
                    bindCmd = lambda *args: (None, None),
                    defaultText = ""):
            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)
            
            if "fg" not in extraOptions.keys():
                extraOptions["fg"] = wd.Data.ENT.defaultTextColor

            self.name = prefix.lower() + name
            self.rootWidget = rootWidget

            def bindCmdWrapper(*args):
                keys, cmds = bindCmd(*args)
                dtKeys, dtCmds = self.__bindCMD()

                if type(keys) == list and type(cmds) == list:
                    dtKeys.extend(keys)
                    dtCmds.extend(cmds)

                return dtKeys, dtCmds
            
            self.bindCmd = bindCmdWrapper
            self.defaultText = defaultText

            TkWidgets.DataContainer_Interface_Impl.__init__(self)

            # NOTE: this is to alow 
            if hasattr(self.rootWidget, "widgetObj"):
                self.widgetObj = tk.Entry(self.rootWidget.widgetObj,
                            textvariable = self.getDataObject(),
                            name = self.name,
                            **extraOptions)
            else:
                self.widgetObj = tk.Entry(self.rootWidget,
                            textvariable = self.getDataObject(),
                            name = self.name,
                            **extraOptions)
            
            
            
            caller = inspect.stack()[1].frame
            localvars = caller.f_locals
            child = localvars['self']

            TkWidgets.HasChildren_Interface_Impl.__init__(self, widget = self)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widget = self, renderData = self.renderData)
            TkWidgets.HasListenersWidget_Interface_Impl.__init__(self, widgetObj = self.widgetObj, bindCmd = self.bindCmd)
            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = self.bindCmd, callingObject = child,)
            Notifyable_Interface.__init__(self)

            super().bind()
        
        def hide(self):
            self.setData(self.defaultText)
            return super().hide()

        def setTextColor(self, color):
            self.widgetObj.configure(fg = color)

        def updateDafaultText(self, newText):
            self.defaultText = newText

        def defaultTextCMD(self):
            current = str(self.getData()).rstrip()
            # [KIK-63] since " " in text data cause errors so we store "_" instead
            current = current.replace("_", " ")
            if current == self.defaultText:
                self.setTextColor(wd.Data.ENT.regularTextColor)
                self.setData("")
            elif current == "":
                self.setTextColor(wd.Data.ENT.defaultTextColor)
                self.setData(self.defaultText)

        def __bindCMD(self):
            keys = [TkWidgets.Data.BindID.focusIn, TkWidgets.Data.BindID.focusOut]
            cmds = [lambda *args: self.defaultTextCMD(), 
                    lambda *args: self.defaultTextCMD()]
            return keys, cmds

        def wrapSelectedText(self, txtBefore, txtAfter):
            startSelIDX = self.widgetObj.index("sel.first")
            endSelIDX = self.widgetObj.index("sel.last")
            selText = self.widgetObj.selection_get()
            allText = self.widgetObj.get()
            boldSelText = f"{txtBefore}{selText}{txtAfter}"
            finalText = allText.replace(selText, boldSelText)
            self.widgetObj.delete("0", tk.END)
            self.widgetObj.insert("0", finalText)
        
        def addTextAtStart(self, text):
            self.widgetObj.insert("0", text)
        
        def addTextAtCurrent(self, text):
            self.widgetObj.insert(TkWidgets.TextInsertPosition.CURRENT, text)
    
    class Checkbox (Notifyable_Interface,
                    DataContainer_Interface_Impl,
                    HasChildren_Interface_Impl, 
                    RenderableWidget_Interface_Impl,
                    HasListenersWidget_Interface_Impl,
                    BindableWidget_Interface_Impl):
        def __init__(self, 
                    prefix: str, 
                    name : str,
                    rootWidget, 
                    renderData : dict,
                    extraOptions = {},
                    bindCmd = lambda *args: (None, None),
                    command = lambda *args: None,
                    text = ""):
            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)

            self.name = prefix.lower() + name
            self.rootWidget = rootWidget
            self.bindCmd = bindCmd
            self.text = text

            TkWidgets.DataContainer_Interface_Impl.__init__(self)

            if "widgetObj" in dir(self.rootWidget):
                self.widgetObj = ttk.Checkbutton(self.rootWidget.widgetObj, 
                                    name = self.name, 
                                    text = self.text,
                                    variable = self.getDataObject(), 
                                    onvalue = 1, 
                                    offvalue = 0,
                                    command = command,
                                    **extraOptions)
            else:
                self.widgetObj = ttk.Checkbutton(self.rootWidget, 
                                    name = self.name, 
                                    text = self.text,
                                    variable = self.getDataObject(), 
                                    onvalue = 1, 
                                    offvalue = 0,
                                    command = command,
                                    **extraOptions)

            caller = inspect.stack()[1].frame
            localvars = caller.f_locals
            child = localvars['self']
            
            TkWidgets.HasChildren_Interface_Impl.__init__(self, widget = self)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widget = self, renderData = self.renderData)
            TkWidgets.HasListenersWidget_Interface_Impl.__init__(self, widgetObj = self.widgetObj, bindCmd = self.bindCmd)
            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = self.bindCmd, callingObject = child)
            Notifyable_Interface.__init__(self)

            super().bind()
    
    class Label (Notifyable_Interface,
                 Datable_Interface,
                 DataContainer_Interface_Impl,
                 HasChildren_Interface_Impl, 
                 RenderableWidget_Interface_Impl,
                 HasListenersWidget_Interface_Impl,
                 BindableWidget_Interface_Impl,
                 EventGeneratable_Interface_Impl):
        def __init__(self, 
                    prefix: str, 
                    name : str,
                    rootWidget, 
                    renderData : dict,
                    extraOptions = {},
                    bindCmd = lambda *args: (None, None),
                    padding = [0, 0, 0, 0],
                    image = None,
                    text = None,
                    data = {}):
            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)

            self.name = prefix.lower() + name
            self.name = self.name.replace(".", "_")
            # self.name = self.name.replace("_", "")
            self.rootWidget = rootWidget
            self.text = text
            self.image = image
            self.padding = padding

            TkWidgets.DataContainer_Interface_Impl.__init__(self)

            if type(image) == TkWidgets.UIImage:
                tkImage = image.data
            else:
                tkImage = image

            if "widgetObj" in dir(self.rootWidget):
                if text != None:
                    self.widgetObj = ttk.Label(self.rootWidget.widgetObj, 
                                        text = self.text,
                                        padding = self.padding,
                                        name = self.name)
                else:
                    self.widgetObj = ttk.Label(self.rootWidget.widgetObj,
                                        image = tkImage,
                                        padding = self.padding,
                                        name = self.name)
            else:
                if text != None:
                    self.widgetObj = ttk.Label(self.rootWidget, 
                                        text = self.text,
                                        padding = self.padding,
                                        name = self.name)
                else:
                    self.widgetObj = ttk.Label(self.rootWidget,
                                        image = tkImage,
                                        padding = self.padding,
                                        name = self.name)
                        
            caller = inspect.stack()[1].frame
            localvars = caller.f_locals
            child = localvars['self']

            TkWidgets.HasChildren_Interface_Impl.__init__(self, widget = self)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widget = self, renderData = self.renderData)
            TkWidgets.HasListenersWidget_Interface_Impl.__init__(self, widgetObj = self.widgetObj, bindCmd = bindCmd)
            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd, callingObject = child)
            TkWidgets.EventGeneratable_Interface_Impl.__init__(self, widgetObj = self.widgetObj)
            Notifyable_Interface.__init__(self)
            Datable_Interface.__init__(self, data)

            self.bind()
        
        def changeText(self, newText):
            self.text = newText
            self.widgetObj.configure(text=newText)
        
        def changeColor(self, color:str):
            self.widgetObj.configure(foreground=color)
        
        def bind(self):
            return super().bind()

        def updateImage(self, image):
            self.widgetObj.configure(image = image.data)
            return image
        
        def changeColor(self, newColor):
            try:
                self.widgetObj.configure(foreground=newColor)
            except:
                pass
        
        def getHeight(self):
            return self.widgetObj.winfo_height()
        
        def setWrapLength(self, wraplength):
            self.widgetObj.configure(wraplength = wraplength)

    class Frame(Notifyable_Interface,
                RenderableWidget_Interface_Impl,
                HasChildren_Interface_Impl):
        def __init__(self, 
                    prefix: str, 
                    name : str,
                    rootWidget, 
                    renderData : dict,
                    extraOptions = {},
                    bindCmd = lambda *args: (None, None),
                    padding = [0, 0, 0, 0]):
            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)

            self.name:str = prefix.lower() + name
            self.name = "_Frame_" + self.name.replace(".", "_")
            self.rootWidget = rootWidget
            self.padding = padding
            
            if (type(self.rootWidget) == ttk.Frame):
                self.widgetObj = ttk.Frame(self.rootWidget, 
                                           padding = self.padding,
                                           name = self.name)
            else:
                if "widgetObj" in dir(self.rootWidget):
                    self.widgetObj = ttk.Frame(self.rootWidget.widgetObj, 
                                        padding = self.padding,
                                        name = self.name)
                else:
                    self.widgetObj = ttk.Frame(self.rootWidget, 
                                        padding = self.padding,
                                        name = self.name)

            TkWidgets.HasChildren_Interface_Impl.__init__(self, widget = self)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widget = self, renderData = self.renderData)
            Notifyable_Interface.__init__(self)
        
        def getHeight(self):
            return self.widgetObj.winfo_height()

    class VideoPayer(Frame):
        def render(self, videoPath, **kwargs):
            # Creating VLC player
            self.instance = vlc.Instance()
            self.player = self.instance.media_player_new()

             # Function to start player from given source
            self.media = self.instance.media_new(videoPath)
            self.media.get_mrl()
            self.player.set_media(self.media)

            # libtk = cdll.LoadLibrary(ctypes.util.find_library('tk'))
            # returns the tk library /usr/lib/libtk.dylib from macOS,
            # but we need the tkX.Y library bundled with Python 3+
            # and matching the version of tkinter, _tkinter, etc.
            libtk = 'libtk%s.dylib' % (TkWidgets.tkinterVersion)
            #NOTE: we keep the lib in the same dir as the python file
            libtk = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tk_specific", libtk)
            libtk = cdll.LoadLibrary(libtk)
            # getNSView = libtk.TkMacOSXDrawableView  # XXX not found?
            getNSView = libtk.TkMacOSXGetRootControl
            getNSView.restype = c_void_p
            getNSView.argtypes = c_void_p,
            self.player.set_nsobject(getNSView(self.widgetObj.winfo_id()))

            super().render(**kwargs)
        
        def GetHandle(self):
            # Getting frame ID
            return self.canvas.winfo_id()
        
        def pause(self):
            if self.player.is_playing():
                self.playing = True
                self.play()

        def play(self, playPosition = None, videoName = ""):
            self.rootWidget.widgetObj.title(f"Video for: {videoName} at " + "{:.2f}".format(self.player.get_position()))
            if not self.playing:
                self.player.play()
                if playPosition != None:
                    self.player.set_position(playPosition)
            else:
                self.player.pause()

            self.playing = not self.playing
        
        def scroll(self, numSeconds):
            secondAsPercentage = 1.0 / (float(self.player.get_length()) / 1000.0)
            self.player.set_position(self.player.get_position() + (numSeconds * secondAsPercentage))

        def getVideoPosition(self):
            return self.player.get_position()
        
        def isPlaying(self):
            return self.player.is_playing()

        def close(self):
            self.player.stop()
            self.media = None
            self.player = None
            self.widgetObj.grid_forget()
            self.widgetObj.grid_forget()

        def forceFocus(self):
            self.rootWidget.widgetObj.focus_force()
        

    class MultilineText(Notifyable_Interface,
                RenderableWidget_Interface_Impl,
                HasChildren_Interface_Impl,
                BindableWidget_Interface_Impl,
                DataContainer_Interface_Impl):
        def __init__(self, 
                    prefix: str, 
                    name : str,
                    rootWidget, 
                    renderData : dict,
                    text = "",
                    wrap = None, 
                    width = 70, 
                    height = 10, 
                    extraOptions = {},
                    bindCmd = lambda *args: (None, None),
                    padding = [0, 0, 0, 0],
                    data = {}):
            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)

            self.name = prefix.lower() + name
            self.rootWidget = rootWidget
            self.padding = padding
            
            
            if (type(self.rootWidget) == ttk.Frame):
                self.widgetObj = scrolledtext.ScrolledText(self.rootWidget,
                                                      wrap = wrap, 
                                                      width = width, 
                                                      height = height,
                                                      name = name)
            else:
                self.widgetObj = scrolledtext.ScrolledText(self.rootWidget.widgetObj, 
                                                      wrap = wrap, 
                                                      width = width, 
                                                      height = height,
                                                      name = name)
            self.widgetObj.config(spacing1 = 10)
            self.widgetObj.config(spacing2 = 10)
            self.widgetObj.config(spacing3 = 12)
            
            self.widgetObj.insert(TkWidgets.TextInsertPosition.END, text)
            self.widgetObj.config(height = height)

            caller = inspect.stack()[1].frame
            localvars = caller.f_locals
            child = localvars['self']

            TkWidgets.DataContainer_Interface_Impl.__init__(self)
            TkWidgets.HasChildren_Interface_Impl.__init__(self, widget = self)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widget = self, renderData = self.renderData)
            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd, callingObject = child)
            Notifyable_Interface.__init__(self)

            self.setData(text)

        def getData(self):
            newData = self.widgetObj.get('1.0', TkWidgets.TextInsertPosition.END).rstrip()
            self.setData(newData)
            return newData
    
        def getCurrCursorPosition(self):
            return self.widgetObj.index(TkWidgets.TextInsertPosition.CURRENT)
        
        def pasteTextFromClipboard(self, *args):
            pb = NSPasteboard.generalPasteboard()
            text:str = pb.stringForType_(NSStringPboardType)

            text = text.replace("\u0000", "fi")

            self.insert(TkWidgets.TextInsertPosition.CURRENT, text)

        def wrapSelectedText(self, txtBefore, txtAfter):
            startSelIDX = self.widgetObj.index("sel.first")
            endSelIDX = self.widgetObj.index("sel.last")
            selText = self.widgetObj.get(startSelIDX, endSelIDX)
            boldSelText = f"{txtBefore}{selText}{txtAfter}"
            self.widgetObj.replace(startSelIDX, endSelIDX, boldSelText)
        
        def addTextAtStart(self, text):
            self.widgetObj.insert("0.0", text)
        
        def addTextAtCurrent(self, text):
            self.widgetObj.insert(TkWidgets.TextInsertPosition.CURRENT, text)

        def setPads(self, padx, pady):
            self.widgetObj.config(padx = padx, pady = pady)
        
        def getPosition(self):
            return self.widgetObj.index("insert")

        def setPosition(self, line, column):
            self.widgetObj.mark_set("insert", "%d.%d" % (int(line), int(column)))


    class Canvas(Notifyable_Interface,
                RenderableWidget_Interface_Impl,
                HasChildren_Interface_Impl,
                BindableWidget_Interface_Impl):
        def __init__(self, 
                     prefix: str, 
                     name : str,
                     rootWidget, 
                     renderData : dict,
                     image = None,
                     width = 100,
                     height = 100,
                     extraOptions = {},
                     bindCmd = lambda *args: (None, None)):
            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)

            self.name = prefix.lower() + name
            self.rootWidget = rootWidget

            self.widgetObj = tk.Canvas(self.rootWidget.widgetObj, 
                                       width = width, 
                                       height = height,
                                       name = self.name)

            self.image = image

            if image != None:
                if type(self.image) != TkWidgets.UIImage:
                    self.backgroundImage = self.widgetObj.create_image(0, 0,
                                                                image = self.image, 
                                                                anchor='nw', 
                                                                tag = prefix)
                else:
                    self.backgroundImage = self.widgetObj.create_image(0, 0,
                                                                image = self.image.data, 
                                                                anchor='nw', 
                                                                tag = prefix)
            else:
                self.backgroundImage = None

            caller = inspect.stack()[1].frame
            localvars = caller.f_locals
            child = localvars['self']
            
            TkWidgets.HasChildren_Interface_Impl.__init__(self, widget = self)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widget = self, 
                                                               renderData = self.renderData)
            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd, callingObject = child)
            Notifyable_Interface.__init__(self)
    
        def findOverlapping(self, x1, y1, x2, y2):
            return self.widgetObj.find_overlapping(x1, y1, x2, y2)
        
        def createButton(self,
                         labelStartX, 
                         labelStartY, 
                         anchor, 
                         buttonWidget,
                         tags):
            # return the id of the created widget
            return self.widgetObj.create_window(labelStartX, 
                                                labelStartY, 
                                                anchor = anchor, 
                                                window = buttonWidget.widgetObj,
                                                tags = tags)
        def createRectangle(self,
                            labelStartX, 
                            labelStartY,
                            labelEndX,
                            labelEndY,
                            fill,
                            tags):
            return self.widgetObj.create_rectangle(labelStartX, 
                                                   labelStartY,
                                                   labelEndX,
                                                   labelEndY,
                                                   fill = fill,
                                                   tags = tags)

        def createOval(self,
                       startX, 
                       startY,
                       endX,
                       endY,
                       fill,
                       outline,
                       tags):
            return self.widgetObj.create_oval(startX, 
                                              startY,
                                              endX, 
                                              endY,
                                              fill = fill, 
                                              outline = outline,
                                              tags = tags)

        def createImage(self,
                        x1, 
                        y1, 
                        image,
                        anchor, 
                        tag):
            return self.widgetObj.create_image(x1, 
                                               y1, 
                                               image = image.data,
                                               anchor = anchor, 
                                               tag = tag)
     
        def createPolygon(self,
                          coordinates, 
                          fill,
                          outline,
                          tags):
            return self.widgetObj.create_polygon(coordinates, 
                                                 fill = fill,
                                                 outline = outline,
                                                 tags = tags)
        
        def findByTag(self, tag):
            return self.widgetObj.find_withtag(tag)
        
        def deleteByTag(self, tag):
            return self.widgetObj.delete(tag)

    class ScrollableBox (Notifyable_Interface,
                DataContainer_Interface_Impl,
                HasChildren_Interface_Impl, 
                RenderableWidget_Interface_Impl,
                HasListenersWidget_Interface_Impl,
                BindableWidget_Interface_Impl):

        def __init__(self, 
                    prefix: str, 
                    name : str,
                    rootWidget, 
                    renderData : dict,
                    width = 700,
                    height = 150,
                    extraOptions = {},
                    bindCmd = lambda *args: (None, None),
                    makeScrollable = True):
            self.canvas = None
            self.container = None
            self.scrollbar_top = None
            self.scrollbar_right = None

            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)

            self.name = prefix.lower() + name
            self.rootWidget = rootWidget

            TkWidgets.DataContainer_Interface_Impl.__init__(self)

            self.container = TkWidgets.Frame(self.name, "_container", rootWidget, {})
            self.canvas = TkWidgets.Canvas(self.name, "_canvas", self.container, 
                                      height = height, width = width, renderData = {})

            scrollbar = ttk.Scrollbar(self.container.widgetObj, orient="vertical", command = self.canvas.widgetObj.yview)
            scrollbar2 = ttk.Scrollbar(self.container.widgetObj, orient="horizontal", command = self.canvas.widgetObj.xview)
            self.scrollbar_top = scrollbar
            self.scrollbar_right = scrollbar2
            scrollable_frame = TkWidgets.Frame(self.name, "_scrollableFrame", self.canvas, {})
            scrollable_frame2 = TkWidgets.Frame(self.name, "_scrollableFrame2", self.canvas, {})
            self.scrollable_frame = scrollable_frame

            scrollable_frame.widgetObj.bind(
                "<Configure>",
                lambda e: self.canvas.widgetObj.configure(
                    scrollregion = self.canvas.widgetObj.bbox("all")
                )
            )
            scrollable_frame2.widgetObj.bind(
                "<Configure>",
                lambda e: self.canvas.widgetObj.configure(
                    scrollregion = self.canvas.widgetObj.bbox("all")
                )
            )

            self.canvas.widgetObj.create_window((0, 0), window = scrollable_frame.widgetObj, anchor="nw")
            self.canvas.widgetObj.create_window((0, 0), window = scrollable_frame2.widgetObj, anchor="se")

            self.canvas.widgetObj.configure(yscrollcommand=scrollbar.set)
            self.canvas.widgetObj.configure(xscrollcommand=scrollbar2.set)

            self.container.render()
            scrollbar.pack(side="right", fill="y")
            scrollbar2.pack(side="top", fill="x")
            self.canvas.widgetObj.pack(side="top", fill="both", expand = True)

            def on_vertical(event):
                self.canvas.widgetObj.yview_scroll(-1 * event.delta, 'units')

            def on_horizontal(event):
                self.canvas.widgetObj.xview_scroll(-1 * event.delta, 'units')

            if makeScrollable:
                def __bindScroll(*args):
                    self.container.widgetObj.bind_all('<MouseWheel>', on_vertical)
                    self.container.widgetObj.bind_all('<Shift-MouseWheel>', on_horizontal) # scroll left-right
                def __unbindScroll(*args):
                    self.container.widgetObj.unbind_all('<MouseWheel>')
                    self.container.widgetObj.unbind_all('<Shift-MouseWheel>') # scroll left-right

                self.canvas.widgetObj.bind("<Enter>", __bindScroll, add = True)
                self.canvas.widgetObj.bind("<Leave>", __unbindScroll, add = True)

            self.widgetObj = self.container.widgetObj
                        
            caller = inspect.stack()[1].frame
            localvars = caller.f_locals
            child = localvars['self']

            TkWidgets.HasChildren_Interface_Impl.__init__(self, widget = self)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widget = self, renderData = self.renderData)
            TkWidgets.HasListenersWidget_Interface_Impl.__init__(self, widgetObj = self.widgetObj, bindCmd = bindCmd)
            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd, callingObject = child)
            Notifyable_Interface.__init__(self)

            self.bind()

        def bind(self):
            return super().bind()
        
        def addTOCEntry(self, entry, row, column):
            if "grid" in dir(entry):
                entry.grid(row = row, column = column, sticky=TkWidgets.Orientation.W)
            else:
                entry.render()

        def scrollY(self, value):
            self.canvas.widgetObj.yview_scroll(value,'units')

        def moveY(self, value):
            self.canvas.widgetObj.yview_moveto(value)

        def moveX(self, value):
            self.canvas.widgetObj.xview_moveto(value)

        def getY(self):
            y, _ = self.canvas.widgetObj.yview()
            return y

        def getHeight(self):
            return self.canvas.widgetObj.winfo_height()
    
        def setCanvasHeight(self, newHeight):
            self.canvas.widgetObj.configure(height = newHeight)

        def getChildren(self):
            return self.scrollable_frame.getChildren()
            
        def forceFocus(self):
            self.scrollable_frame.widgetObj.focus_force()
            
        def yPosition(self):
            return self.scrollable_frame.widgetObj.winfo_rooty()
        
        def getFrameHeight(self):
            return self.scrollable_frame.widgetObj.winfo_height()
        
        def updateFrameIdleTasks(self):
            return self.scrollable_frame.widgetObj.update_idletasks()

    class RootWidget(BindableWidget_Interface_Impl,
                     RenderableWidget_Interface_Impl,
                     DataContainer_Interface_Impl,
                     HasChildren_Interface_Impl):
        def __init__(self, 
                     width, 
                     height,
                     bindCmd = lambda *args: (None, None)):
            self.tk = TkWidgets.Data.tk
            self.tk.geometry(str(width) + "x" + str(height))
            self.widgetObj = tk.Toplevel(self.tk)
            self.widgetObj = self.widgetObj
            
            TkWidgets.DataContainer_Interface_Impl.__init__(self)

            caller = inspect.stack()[1].frame
            localvars = caller.f_locals
            child = localvars['self']

            if "widgetObj" in dir(child):
                TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd, callingObject = child)
            else:
                TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd, callingObject = self.widgetObj)

            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widget = self)
            TkWidgets.HasChildren_Interface_Impl.__init__(self, widget = self)
        
            super().bind()

        def setGeometry(self, width = -1, height = -1, posx = -1, posy = -1):
            width = str(width)
            height = str(height)
            posx = str(posx)
            posy = str(posy)

            if width == "-1" or height == "-1":
                self.widgetObj.geometry("+" + posx + "+" + posy)
            elif posx == "-1" or posy == "-1":
                self.widgetObj.geometry(width + "x" + height)
            else:
                self.widgetObj.geometry(width + "x" + height + "+" + posx + "+" + posy)

        
        def getHeight(self):
            return self.tk.winfo_height()

        def startMainLoop(self):
            self.tk.mainloop()
        
        def getId(self):
            return self.widgetObj.winfo_id()
        
        def stopMainLoop(self):
            self.widgetObj.withdraw()

        def configureColumn(self, conNum, weight):
            self.widgetObj.columnconfigure(conNum, weight = weight)
        
        def hide(self, **kwargs):
            self.widgetObj.withdraw()
        
        def render(self):
            self.widgetObj.deiconify()
            self.widgetObj.focus_force()
            self.widgetObj.lift()
        
        def wait(self):
            self.widgetObj.wait_variable(self.getDataObject())
        
        def stopWait(self, response = False):
            self.setData(response)
        
        def exitApp(self):
            self.widgetObj.destroy()
        
        def changeTitle(self, newTitle):
            self.widgetObj.title(newTitle)
        
        def bindToClose(self, bindCmd):
            self.widgetObj.protocol("WM_DELETE_WINDOW", lambda *args: bindCmd())

        def makeUnmovable(self):
            self.widgetObj.resizable(width=False, height=False)

    class UIImage():
        def __init__(self, image):
            self.image = image
            self.data = ImageTk.PhotoImage(self.image)
        
        def getWidth(self):
            return self.data.width()

        def getHeight(self):
            return self.data.height()

    def startLoop():
        def tick():
            # this function stamps the changes every 180 seconds
            msg = "After time has passed'."
            log.autolog(msg)
            ocf.Wr.TrackerAppCalls.stampChanges(sf.Wr.Manager.Book.getCurrBookFolderPath(), msg)
            TkWidgets.Data.tk.after(180000, tick)
            return None

        tick()
        TkWidgets.Data.tk.mainloop()

currUIImpl = TkWidgets