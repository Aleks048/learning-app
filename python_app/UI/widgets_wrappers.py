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

class BindableWidget_Interface:
    def bind(self, **kwargs):
        raise NotImplementedError()

class HasRelatedWidget_Interface:
    relatedWidgets = {}

    def addRelatedWidget(self, widget, **kwargs):
        self.relatedWidgets[widget.name] = widget
    
    def getRelatedWidget(self, widgetName, **kwargs):
        return self.relatedWidgets[widgetName]

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
            self.widgetObj.winfo_children()
    
    class RenderableWidget_Interface_Impl(RenderableWidget_Interface):
        def __init__(self, widgetObj = None, *args, **kwargs):
            self.widjetObj = widgetObj
        
        def render(self, widjetObj = None, **kwargs):
            if widjetObj == None:
                self.widjetObj.grid(**kwargs)
            else:
                widjetObj.grid(**kwargs)
    

    class HasRelatedWidget_Interface_Impl(HasRelatedWidget_Interface):
        def __init__(self, *args, **kwargs):
            pass

    class BindableWidget_Interface_Impl(BindableWidget_Interface):
        def __init__(self, bindCmd = lambda *args: None, *args, **kwargs):
            self.bindCmd = bindCmd
        
        def bind(self):
            self.bindCmd()
        
    class Button (HasChildren_Interface_Impl, 
                RenderableWidget_Interface_Impl,
                HasRelatedWidget_Interface_Impl,
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

            widgetObj = tk.Button(self.rootWidget, 
                                name = self.name,
                                text= self.text,
                                command = cmd,
                                **extraOptions)
            
            currUIImpl.HasChildren_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd)
            currUIImpl.RenderableWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd)
            currUIImpl.HasRelatedWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd)
            currUIImpl.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd)

            super().bind()
        
            
        def render(self, **kwargs):
            return super().render(**self.renderData)



    class OptionMenu (DataContainer_Interface_Impl,
                    HasChildren_Interface_Impl, 
                    RenderableWidget_Interface_Impl,
                    HasRelatedWidget_Interface_Impl,
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

            widgetObj = tk.Frame(self.rootWidget, name = name, background="Blue")
            optionMenu = tk.OptionMenu(widgetObj, 
                                    self.getDataObject(), 
                                    *self.listOfOptions, 
                                    command= lambda _: cmd,
                                    **extraOptions)
            self.optionMenu = optionMenu
            
            
            currUIImpl.HasChildren_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd)
            currUIImpl.RenderableWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd)
            currUIImpl.HasRelatedWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = bindCmd)
            currUIImpl.BindableWidget_Interface_Impl.__init__(self, bindCmd = bindCmd)

            super().bind()
        
            
        def render(self, **kwargs):
            super().render(self.optionMenu, column = 0, row = 0)
            return super().render(**self.renderData)
    
    class TextEntry (DataContainer_Interface_Impl,
                    HasChildren_Interface_Impl, 
                    RenderableWidget_Interface_Impl,
                    HasRelatedWidget_Interface_Impl,
                    BindableWidget_Interface_Impl):
        def __init__(self, 
                    prefix: str, 
                    name : str,
                    rootWidget, 
                    renderData : dict,
                    extraOptions = {},
                    bindCmd = lambda *args: None):
            self.renderData = currUIImpl.translateRenderOptions(renderData)
            extraOptions = currUIImpl.translateExtraBuildOptions(extraOptions)

            self.name = prefix.lower() + name
            self.rootWidget = rootWidget
            self.bindCmd = bindCmd


            currUIImpl.DataContainer_Interface_Impl.__init__(self)

            widgetObj = tk.Entry(self.rootWidget,
                        textvariable = self.getDataObject(),
                        name = self.name,
                        **extraOptions)
            
            currUIImpl.HasChildren_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = self.bindCmd)
            currUIImpl.RenderableWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = self.bindCmd)
            currUIImpl.HasRelatedWidget_Interface_Impl.__init__(self, widgetObj = widgetObj, bindCmd = self.bindCmd)
            currUIImpl.BindableWidget_Interface_Impl.__init__(self, bindCmd = self.bindCmd)

            super().bind()
        
        def render(self, **kwargs):
            return super().render(**self.renderData)
    
    class Checkbox:
        def __init__(name, rootWidget):
            pass

    
    class RootWidget:
        pass

currUIImpl = TkWidgets