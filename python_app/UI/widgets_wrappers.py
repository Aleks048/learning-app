import tkinter as tk

class HasChildren_Interface:
    def getChildren(self):
        raise NotImplementedError()

class RenderableWidget_Interface:
    def render(self, **kwargs):
        raise NotImplementedError()


class TkWidgets:
    class HasChildren_Interface_Impl(HasChildren_Interface):
        def __init__(self, widgetObj = None, *args, **kwargs):
            self.widjetObj = widgetObj
        
        def getChildren(self):
            self.widgetObj.winfo_children()
    
    class RenderableWidget_Interface_Impl(RenderableWidget_Interface):
        def __init__(self, widgetObj = None, *args, **kwargs):
            self.widjetObj = widgetObj
        
        def render(self, **kwargs):
            self.widjetObj.grid(**kwargs)
    
    class Button (HasChildren_Interface_Impl, RenderableWidget_Interface_Impl):
        def __init__(self, name, text, rootWidget, cmd):
            self.name = name
            self.text = text
            self.rootWidget = rootWidget
            
            widgetObj = tk.Button(self.rootWidget, 
                                name = self.name,
                                text= self.text,
                                command = cmd)
            super().__init__(widgetObj = widgetObj)

        

    class Dropdown:
        def __init__(name, rootWidget):
            pass
    
    class Checkbox:
        def __init__(name, rootWidget):
            pass

    class TextField:
        def __init__(name, rootWidget):
            pass
        
        def getData():
            pass
    
    class Root:
        pass

currUIImpl = TkWidgets