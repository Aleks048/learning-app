import tkinter as tk
from tkinter import ttk

import _utils.logging as log
import UI.widgets_data as wd

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
    class Data:
        textColor_ID = "fg"
        tk = tk.Tk()
        class BindID:
            focusIn = "<FocusIn>"
            focusOut = "<FocusOut>"
            allKeys = "<Key>"
            mouse1 = "<Button-1>"

            enterWidget = "<Enter>"
            leaveWidget = "<Leave>"

            class Keys:
                enter = "Return"
                escape = "Escape"

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

            ttk.Style().configure('green/black.TButton', 
                                foreground='white', 
                                background='black')
            
            widgetObj = ttk.Button(self.rootWidget.widjetObj, 
                                name = self.name,
                                text= self.text,
                                style='green/black.TButton',
                                **extraOptions
                                )
            
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
                    bindCmd = lambda *args: (None, None)):
            
            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)

            self.name = prefix.lower() + name
            self.listOfOptions = list(listOfOptions)
            self.rootWidget = rootWidget
            self.cmd = cmd

            TkWidgets.DataContainer_Interface_Impl.__init__(self)

            widgetObj = tk.Frame(self.rootWidget.widjetObj, 
                                name = self.name, 
                                background="Blue")
            optionMenu = tk.OptionMenu(widgetObj, 
                                    self.getDataObject(), 
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

            self.setData(self.listOfOptions[0])
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
                bindCmd(*args)
                return self.__bindCMD()
            
            self.bindCmd = bindCmdWrapper
            self.defaultText = defaultText

            TkWidgets.DataContainer_Interface_Impl.__init__(self)

            widgetObj = tk.Entry(self.rootWidget.widjetObj,
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
            current = self.getData()
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
                    text = ""):
            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)

            self.name = prefix.lower() + name
            self.rootWidget = rootWidget
            self.bindCmd = bindCmd
            self.text = text

            TkWidgets.DataContainer_Interface_Impl.__init__(self)

            widgetObj = tk.Checkbutton(self.rootWidget.widjetObj, 
                                name = self.name, 
                                text = self.text,
                                variable = self.getDataObject(), 
                                onvalue = 1, 
                                offvalue = 0,
                                **extraOptions)
            
            TkWidgets.HasChildren_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = self.bindCmd)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd, renderData = self.renderData)
            TkWidgets.HasListenersWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = self.bindCmd)
            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = self.bindCmd, widgetObj = widgetObj)
            Notifyable_Interface.__init__(self)

            super().bind()
    
    class Label (Notifyable_Interface,
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
                    text = ""):
            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)

            self.name = prefix.lower() + name
            self.rootWidget = rootWidget
            self.text = text

            TkWidgets.DataContainer_Interface_Impl.__init__(self)

            widjetObj = tk.Label(self.rootWidget.widjetObj, text = self.text)
            
            TkWidgets.HasChildren_Interface_Impl.__init__(self, widgetObj = widjetObj, bindCmd = bindCmd)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widgetObj = widjetObj, bindCmd = bindCmd, renderData = self.renderData)
            TkWidgets.HasListenersWidget_Interface_Impl.__init__(self, widgetObj = widjetObj, bindCmd = bindCmd)
            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd, widgetObj = widjetObj)
            Notifyable_Interface.__init__(self)

            self.bind()
        
        def changeText(self, newText):
            self.text = newText
            self.widjetObj.configure(text=newText)
        
        def changeColor(self, color:str):
            self.widjetObj.configure(foreground=color)
        
        def bind(self):
            return super().bind()
    
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
                    extraOptions = {},
                    bindCmd = lambda *args: (None, None)):
            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)

            self.name = prefix.lower() + name
            self.rootWidget = rootWidget

            TkWidgets.DataContainer_Interface_Impl.__init__(self)



            def on_vertical(event):
                canvas.yview_scroll(-1 * event.delta, 'units')

            def on_horizontal(event):
                canvas.xview_scroll(-1 * event.delta, 'units')

            container = ttk.Frame(rootWidget.widgetObj)
            canvas = tk.Canvas(container, height = 150, width= 700)
            scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            self.scrollable_frame = scrollable_frame

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )

            canvas.create_window((0, 0), window = scrollable_frame, anchor="nw")

            canvas.configure(yscrollcommand=scrollbar.set)

            container.grid(column = 0, row = 0)
            canvas.pack(side="left", fill="both", expand = True)
            scrollbar.pack(side="right", fill="y")

            container.bind_all('<MouseWheel>', on_vertical)
            # container.bind_all('<Shift-MouseWheel>', on_horizontal) # scroll left-right
            widjetObj = container

            
            TkWidgets.HasChildren_Interface_Impl.__init__(self, widgetObj = widjetObj, bindCmd = bindCmd)
            TkWidgets.RenderableWidget_Interface_Impl.__init__(self, widgetObj = widjetObj, bindCmd = bindCmd, renderData = self.renderData)
            TkWidgets.HasListenersWidget_Interface_Impl.__init__(self, widgetObj = widjetObj, bindCmd = bindCmd)
            TkWidgets.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd, widgetObj = widjetObj)
            Notifyable_Interface.__init__(self)

            self.bind()

        def bind(self):
            return super().bind()
        
        def addTOCEntry(self, entry):
            entry.pack(fill="both")

    
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
        
        def stopMainLoop(self):
            self.widgetObj.withdraw()

        def configureColumn(self, conNum, weight):
            self.widgetObj.columnconfigure(conNum, weight = weight)
        
        def hide(self, **kwargs):
            self.widgetObj.withdraw()
        
        def render(self, widjetObj=None, renderData={}, **kwargs):
            self.widgetObj.deiconify()
        
        def wait(self):
            self.widgetObj.wait_variable(self.getDataObject())
        
        def stopWait(self, response = False):
            self.setData(response)
        
        def exitApp(self):
            self.widgetObj.destroy()
    
    def startLoop():
        TkWidgets.Data.tk.mainloop()

currUIImpl = TkWidgets