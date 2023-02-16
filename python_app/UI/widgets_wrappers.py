import tkinter as tk

import _utils.logging as log

class DataContainer_Interface:
    dataVar = None

    def getDataObject(self):
        return self.dataVar

    def getData(self, **kwargs):
        raise NotImplementedError()
        
    def setData(self, data, **kwargs):
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
    listeners = []

    def addListenerWidget(self, widget, **kwargs):
        self.listeners.append(widget)
    
    def notifyAllListeners(self, **kwargs):
        for widget in self.listeners:
            widget.notify(self.name)

class Notifyable_Interface:
    def notify(self, broadcasterName):
        pass

class DataTranslatable_Interface:
    def translateExtraBuildOptions(extraOptions):
        if extraOptions != {}:
            extraOptions = {**extraOptions[Data.GeneralProperties_ID], **extraOptions[currUIImpl.__name__]}
            if Data.CommonTextColor_ID in extraOptions:
                extraOptions[currUIImpl.Data.textColor_ID] = extraOptions.pop(Data.CommonTextColor_ID)    
        return extraOptions

    def translateRenderOptions(renderOptions):
        if renderOptions != {}:
            renderOptions = {**renderOptions[Data.GeneralProperties_ID], **renderOptions[currUIImpl.__name__]}
        return renderOptions

class Data:
    CommonTextColor_ID = "textColor"
    GeneralProperties_ID = "general"

class TkWidgets (DataTranslatable_Interface):
    class Data:
        textColor_ID = "fg"
        tk = tk.Tk()
        class BindID:
            focusIn = "<FocusIn>"
            focusOut = "<FocusOut>"

    class DataContainer_Interface_Impl(DataContainer_Interface):
        def __init__(self, *args, **kwargs):
            self.dataVar = tk.Variable()

        def getData(self, **kwargs):
            return self.dataVar.get()
        
        def setData(self, data, **kwargs):
            self.dataVar.set(data)

    class HasChildren_Interface_Impl(HasChildren_Interface):
        def __init__(self, widgetObj = None, *args, **kwargs):
            self.widgetObj = widgetObj
        
        def getChildren(self):
            return self.widgetObj.winfo_children()
    
    class RenderableWidget_Interface_Impl(RenderableWidget_Interface):
        def __init__(self, widgetObj = None, *args, **kwargs):
            self.wasRendered = False
            self.widjetObj = widgetObj
        
        def render(self, widjetObj = None, **kwargs):
            if self.wasRendered:
                log.autolog("ho")
                self.widjetObj.grid()
            else:
                if widjetObj == None:
                    self.widjetObj.grid(**kwargs)
                else:
                    log.autolog("hi")
                    widjetObj.grid(**kwargs)
        
        def hide(self, **kwargs):
            self.widjetObj.grid_remove()
    

    class HasListenersWidget_Interface_Impl(HasListenersWidget_Interface):
        def __init__(self, *args, **kwargs):
            pass

    class BindableWidget_Interface_Impl(BindableWidget_Interface):
        def __init__(self, bindCmd = lambda *args: None, *args, **kwargs):
            self.bindCmd = bindCmd
        
        def bind(self):
            self.bindCmd()
        
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
                    bindCmd = lambda *args: None):
            
            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)
            
            self.name = prefix.lower() + name
            self.text = text
            self.rootWidget = rootWidget
            self.cmd = cmd

            widgetObj = tk.Button(self.rootWidget.widjetObj, 
                                name = self.name,
                                text= self.text,
                                command = lambda : cmd(),
                                **extraOptions)
            
            currUIImpl.HasChildren_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd)
            currUIImpl.RenderableWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd)
            currUIImpl.HasListenersWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd)
            currUIImpl.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd)
            Notifyable_Interface.__init__(self)

            super().bind()
        
            
        def render(self, **kwargs):
            return super().render(**self.renderData)



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
                    bindCmd = lambda *args: None):
            
            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)

            self.name = prefix.lower() + name
            self.listOfOptions = listOfOptions
            self.rootWidget = rootWidget
            self.cmd = cmd

            currUIImpl.DataContainer_Interface_Impl.__init__(self)

            widgetObj = tk.Frame(self.rootWidget.widjetObj, 
                                name = self.name, 
                                background="Blue")
            optionMenu = tk.OptionMenu(widgetObj, 
                                    self.getDataObject(), 
                                    *self.listOfOptions, 
                                    command= lambda _: cmd(),
                                    **extraOptions)
            self.optionMenu = optionMenu
            
            
            currUIImpl.HasChildren_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd)
            currUIImpl.RenderableWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd)
            currUIImpl.HasListenersWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd)
            currUIImpl.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd)
            Notifyable_Interface.__init__(self)

            super().bind()
                    
        def render(self, **kwargs):
            super().render(self.optionMenu, column = 0, row = 0)
            return super().render(**self.renderData)

        def updateOptions(self, newMenuOptions):
            def optionChoosingCallback(value):
                self.setData(value)
                self.cmd()

            if newMenuOptions == None:
                # TODO: should check what conditions lead to None newMenuOptions
                return
            
            if newMenuOptions[0].isnumeric():
                newMenuOptions.sort()  
            
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
                    bindCmd = lambda *args: None,
                    defaultText = ""):
            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)

            self.name = prefix.lower() + name
            self.rootWidget = rootWidget
            self.bindCmd = bindCmd
            self.defaultText = defaultText


            currUIImpl.DataContainer_Interface_Impl.__init__(self)

            widgetObj = tk.Entry(self.rootWidget.widjetObj,
                        textvariable = self.getDataObject(),
                        name = self.name,
                        **extraOptions)
            
            currUIImpl.HasChildren_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = self.bindCmd)
            currUIImpl.RenderableWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = self.bindCmd)
            currUIImpl.HasListenersWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = self.bindCmd)
            currUIImpl.BindableWidget_Interface_Impl.__init__(self, bindCmd = self.bindCmd)
            Notifyable_Interface.__init__(self)

            super().bind()
        
        def render(self, **kwargs):
            return super().render(**self.renderData)
        
        def hide(self, **kwargs):
            # self.widgetObj.delete(0, 'end')
            self.setData(self.defaultText)

            return super().hide(**kwargs)

        def setTextColor(self, color):
            self.widgetObj.configure(fg = color)
    
    class Checkbox:
        def __init__(name, rootWidget):
            pass

    
    class RootWidget(BindableWidget_Interface_Impl):
        def __init__(self, width, height):
            self.tk = TkWidgets.Data.tk
            self.tk.geometry(str(width) + "x" + str(height))
            self.widjetObj = tk.Toplevel(self.tk)
        
        def setGeometry(self, width = 0, height = 0, posx = 0, posy = 0):
            width = str(width)
            height = str(height)
            posx = str(posx)
            posy = str(posy)

            if width == "0" or height == "0":
                self.widjetObj.geometry("+" + posx + "+" + posy)
            elif posx == "0" or posy == "0":
                self.widjetObj.geometry(width + "x" + height)
            else:
                self.widjetObj.geometry(width + "x" + height + "+" + posx + "+" + posy)

        def startMainLoop(self):
            self.tk.mainloop()
        
        def stopMainLoop(self):
            self.widjetObj.withdraw()

currUIImpl = TkWidgets