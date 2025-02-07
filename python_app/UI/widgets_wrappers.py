import tkinter as tk
from tkinter import ttk

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
        def __init__(self, widgetObj = None, *args, **kwargs):
            self.widgetObj = widgetObj
        
        def getChildren(self):
            return self.widgetObj.winfo_children()

    class RenderableWidget_Interface_Impl(RenderableWidget_Interface):
        def __init__(self, widgetObj = None, renderData = {}, *args, **kwargs):
            self.wasRendered = False
            self.widjetObj = widgetObj
            self.renderData = renderData
        
        def render(self, widjetObj = None, renderData = {}, **kwargs):
            if self.wasRendered:
                self.widjetObj.grid()
            else:
                if widjetObj == None:
                    self.widjetObj.grid(**self.renderData)
                else:
                    widjetObj.grid(renderData)
                self.wasRendered = True
        
        def hide(self, **kwargs):
            self.widjetObj.grid_remove()

        def delete(self, **kwargs):
            self.widjetObj.grid_forget()

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
        def __init__(self, widgetObj = None, 
                    bindCmd = lambda *args: (None, None) , *args, **kwargs):
            self.bindCmd = bindCmd
            self.widgetObj = widgetObj
            super().__init__()
        
        def bind(self):
            keys, cmds = self.bindCmd()
            if keys != None and cmds != None:
                for i in range(len(keys)):
                    key = keys[i]
                    cmd = cmds[i]

                    if key == TkWidgets.Data.BindID.allKeys:
                        self.widgetObj.bind_all(key, lambda event: cmd(event))
                    else:
                        self.widgetObj.bind(key, cmd)

        def rebind(self, keys, cmds):
            for i in range(len(keys)):
                key = keys[i]
                cmd = cmds[i]

                if key == TkWidgets.Data.BindID.allKeys:
                    self.widgetObj.bind_all(key, lambda event: cmd(event))
                else:
                    self.widgetObj.bind(key, cmd)
        
        def unbind(self, keys):
            for i in range(len(keys)):
                key = keys[i]

                self.widgetObj.unbind(key)

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

            
            widgetObj = ttk.Button(self.rootWidget.widjetObj, 
                                name = self.name,
                                text= self.text,
                                style='green/black.TButton',
                                **extraOptions
                                )

            ttk.Style().configure('green/black.TButton', 
                                foreground = 'black',
                                background = '#323262',
                                borderwidth = 1,
                                focusthickness = 1)
            
            def btnCmd():
                cmd()
            
            widgetObj.configure(command = lambda : btnCmd())
            
            TkWidgets.HasChildren_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd, renderData = self.renderData)
            TkWidgets.HasListenersWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd)
            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd, widgetObj = widgetObj,)
            Notifyable_Interface.__init__(self)

            super().bind()
        
            
        def render(self, **kwargs):
            return super().render(**self.renderData)

        def updateLabel(self, newText):
            self.text = newText
            self.widgetObj.configure(text = newText)
        
        def getLabel(self):
            return self.widgetObj["text"]



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

            if "widjetObj" in dir(self.rootWidget):
                widgetObj = tk.Frame(self.rootWidget.widjetObj, 
                                    name = self.name, 
                                    background="Blue")
            else:
                widgetObj = tk.Frame(self.rootWidget, 
                                    name = self.name, 
                                    background="Blue")

            if defaultOption == None:
                defaultOption = self.listOfOptions[0]

            # print(f"d {defaultOption}")

            optionMenu = ttk.OptionMenu(widgetObj, 
                                        self.getDataObject(), 
                                        defaultOption,
                                        *self.listOfOptions, 
                                        command= lambda _: cmd(),
                                        **extraOptions)
            self.optionMenu = optionMenu
            self.optionMenu.grid(column= 0, row = 0)
            
            
            TkWidgets.HasChildren_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd, renderData = self.renderData)
            TkWidgets.HasListenersWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd)
            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd, widgetObj = widgetObj,)
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
            if hasattr(self.rootWidget, "widjetObj"):
                widgetObj = tk.Entry(self.rootWidget.widjetObj,
                            textvariable = self.getDataObject(),
                            name = self.name,
                            **extraOptions)
            else:
                widgetObj = tk.Entry(self.rootWidget,
                            textvariable = self.getDataObject(),
                            name = self.name,
                            **extraOptions)

            TkWidgets.HasChildren_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = self.bindCmd)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd, renderData = self.renderData)
            TkWidgets.HasListenersWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = self.bindCmd)
            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = self.bindCmd, widgetObj = widgetObj,)
            Notifyable_Interface.__init__(self)

            super().bind()
        
        def render(self, **kwargs):
            return super().render(**self.renderData)
        
        def hide(self, **kwargs):
            self.setData(self.defaultText)
            return super().hide(**kwargs)

        def setTextColor(self, color):
            self.widgetObj.configure(fg = color)

        def updateDafaultText(self, newText):
            self.defaultText = newText

        def defaultTextCMD(self):
            current = str(self.getData())
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

            if "widjetObj" in dir(self.rootWidget):
                widgetObj = ttk.Checkbutton(self.rootWidget.widjetObj, 
                                    name = self.name, 
                                    text = self.text,
                                    variable = self.getDataObject(), 
                                    onvalue = 1, 
                                    offvalue = 0,
                                    command = command,
                                    **extraOptions)
            else:
                widgetObj = ttk.Checkbutton(self.rootWidget, 
                                    name = self.name, 
                                    text = self.text,
                                    variable = self.getDataObject(), 
                                    onvalue = 1, 
                                    offvalue = 0,
                                    command = command,
                                    **extraOptions)

            # widgetObj = tk.Checkbutton(self.rootWidget.widjetObj, 
            #                     name = self.name, 
            #                     text = self.text,
            #                     variable = self.getDataObject(), 
            #                     onvalue = 1, 
            #                     offvalue = 0,
            #                     **extraOptions)
            
            TkWidgets.HasChildren_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = self.bindCmd)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd, renderData = self.renderData)
            TkWidgets.HasListenersWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = self.bindCmd)
            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = self.bindCmd, widgetObj = widgetObj)
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
                    text = _u.Token.NotDef.str_t,
                    data = {}):
            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)

            self.name = prefix.lower() + name
            # self.name = self.name.replace(".", "")
            # self.name = self.name.replace("_", "")
            self.rootWidget = rootWidget
            self.text = text
            self.image = image
            self.padding = padding

            TkWidgets.DataContainer_Interface_Impl.__init__(self)

            if "widjetObj" in dir(self.rootWidget):
                widjetObj = ttk.Label(self.rootWidget.widjetObj, 
                                      text = self.text, 
                                      image = self.image,
                                      padding = self.padding)
            else:
                widjetObj = ttk.Label(self.rootWidget, 
                                      text = self.text, 
                                      image = self.image,
                                      padding = self.padding)

            self.widgetObj = widjetObj

            TkWidgets.HasChildren_Interface_Impl.__init__(self, widgetObj = widjetObj, bindCmd = bindCmd)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widgetObj = widjetObj, bindCmd = bindCmd, renderData = self.renderData)
            TkWidgets.HasListenersWidget_Interface_Impl.__init__(self, widgetObj = widjetObj, bindCmd = bindCmd)
            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd, widgetObj = widjetObj)
            TkWidgets.EventGeneratable_Interface_Impl.__init__(self, widgetObj = widjetObj)
            Notifyable_Interface.__init__(self)
            Datable_Interface.__init__(self, data)

            self.bind()
        
        def changeText(self, newText):
            self.text = newText
            self.widjetObj.configure(text=newText)
        
        def changeColor(self, color:str):
            self.widjetObj.configure(foreground=color)
        
        def bind(self):
            return super().bind()

        def render(self, **kwargs):
            return super().render(self.widjetObj, self.renderData, **kwargs)


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

            self.name = prefix.lower() + name
            self.rootWidget = rootWidget
            self.padding = padding
            
            
            if (type(self.rootWidget) == ttk.Frame):
                widjetObj = ttk.Frame(self.rootWidget, padding = self.padding)
            else:
                widjetObj = ttk.Frame(self.rootWidget.widjetObj, padding = self.padding)
            
            TkWidgets.HasChildren_Interface_Impl.__init__(self, widgetObj = widjetObj, bindCmd = bindCmd)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widgetObj = widjetObj, bindCmd = bindCmd, renderData = self.renderData)
            Notifyable_Interface.__init__(self)
        
        def render(self, **kwargs):
            return super().render(self.widjetObj, self.renderData, **kwargs)

        def getChildren(self):
            return self.widgetObj.getChildren()

    class Canvas(Notifyable_Interface,
                RenderableWidget_Interface_Impl,
                HasChildren_Interface_Impl,
                BindableWidget_Interface_Impl):
        def __init__(self, 
                     prefix: str, 
                     name : str,
                     rootWidget, 
                     renderData : dict,
                     image,
                     width,
                     height,
                     extraOptions = {},
                     bindCmd = lambda *args: (None, None)):
            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)

            self.name = prefix.lower() + name
            self.rootWidget = rootWidget
            
            if ("widjetObj" not in dir(self.rootWidget)):
                widjetObj = tk.Canvas(self.rootWidget, width = width, height = height)
            else:
                widjetObj = tk.Canvas(self.rootWidget.widjetObj, width = width, height = height)

            self.backgroundImage = widjetObj.create_image(0, 0,
                                                          image = image, 
                                                          anchor='nw', 
                                                          tag = prefix)
            
            TkWidgets.HasChildren_Interface_Impl.__init__(self, widgetObj = widjetObj, bindCmd = bindCmd)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widgetObj = widjetObj, bindCmd = bindCmd, 
                                                               renderData = self.renderData)
            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd, widgetObj = widjetObj)
            Notifyable_Interface.__init__(self)
        
        def render(self, **kwargs):
            return super().render(self.widjetObj, self.renderData, **kwargs)

        def getChildren(self):
            return self.widgetObj.getChildren()
    
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
                                               image = image,
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

            container = ttk.Frame(rootWidget.widgetObj)
            canvas = tk.Canvas(container, height = height, width = width)
            self.canvas = canvas

            scrollbar = ttk.Scrollbar(container, orient="vertical", command = canvas.yview)
            scrollbar2 = ttk.Scrollbar(container, orient="horizontal", command = canvas.xview)
            self.scrollbar_top = scrollbar
            self.scrollbar_right = scrollbar2
            scrollable_frame = ttk.Frame(canvas)
            scrollable_frame2 = ttk.Frame(canvas)
            self.scrollable_frame = scrollable_frame

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion = canvas.bbox("all")
                )
            )
            scrollable_frame2.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion = canvas.bbox("all")
                )
            )

            self.canvas.create_window((0, 0), window = scrollable_frame, anchor="nw")
            self.canvas.create_window((0, 0), window = scrollable_frame2, anchor="se")

            self.canvas.configure(yscrollcommand=scrollbar.set)
            self.canvas.configure(xscrollcommand=scrollbar2.set)

            container.grid(column = 0, row = 0)
            scrollbar.pack(side="right", fill="y")
            scrollbar2.pack(side="top", fill="x")
            self.canvas.pack(side="top", fill="both", expand = True)

            def on_vertical(event):
                self.canvas.yview_scroll(-1 * event.delta, 'units')

            def on_horizontal(event):
                self.canvas.xview_scroll(-1 * event.delta, 'units')

            if makeScrollable:
                def __bindScroll(*args):
                    self.container.bind_all('<MouseWheel>', on_vertical)
                    self.container.bind_all('<Shift-MouseWheel>', on_horizontal) # scroll left-right
                def __unbindScroll(*args):
                    self.container.unbind_all('<MouseWheel>')
                    self.container.unbind_all('<Shift-MouseWheel>') # scroll left-right

                self.canvas.bind("<Enter>", __bindScroll, add = True)
                self.canvas.bind("<Leave>", __unbindScroll, add = True)

            self.container = container
            widjetObj = container

            TkWidgets.HasChildren_Interface_Impl.__init__(self, widgetObj = widjetObj, bindCmd = bindCmd)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widgetObj = widjetObj, bindCmd = bindCmd, renderData = self.renderData)
            TkWidgets.HasListenersWidget_Interface_Impl.__init__(self, widgetObj = widjetObj, bindCmd = bindCmd)
            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd, widgetObj = widjetObj)
            Notifyable_Interface.__init__(self)

            self.bind()
            return canvas

        def bind(self):
            return super().bind()
        
        def addTOCEntry(self, entry, row, column):
            if "grid" in dir(entry):
                entry.grid(row = row, column = column, sticky=TkWidgets.Orientation.W)
            else:
                entry.render()
    
    class RootWidget(BindableWidget_Interface_Impl,
                     RenderableWidget_Interface_Impl,
                     DataContainer_Interface_Impl):
        def __init__(self, 
                     width, 
                     height,
                     bindCmd = lambda *args: (None, None)):
            self.tk = TkWidgets.Data.tk
            self.tk.geometry(str(width) + "x" + str(height))
            self.widgetObj = tk.Toplevel(self.tk)
            
            TkWidgets.DataContainer_Interface_Impl.__init__(self)

            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd, widgetObj = self.widgetObj)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widgetObj = self.widgetObj, bindCmd = bindCmd, renderData = self.renderData)
        
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
        
        def render(self, widjetObj=None, renderData={}, **kwargs):
            self.widgetObj.deiconify()
            self.widgetObj.focus_force()
            self.widgetObj.lift()
        
        def wait(self):
            self.widgetObj.wait_variable(self.getDataObject())
        
        def stopWait(self, response = False):
            self.setData(response)
        
        def exitApp(self):
            self.widgetObj.destroy()
    
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