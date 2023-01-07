import os
import subprocess
import tkinter as tk

# from pathlib import Path
# from tkinter import 


defaultScrPrefix = "scrShot"

master = tk.Tk()
e = tk.Entry(master)
e.pack()

e.focus_set()
counter = 0
prefix = ""
buttonText = tk.StringVar()
buttonText.set("set Prefix")
buttonTextE = tk.StringVar()
buttonTextE.set("Exit")
buttonTextSC = tk.StringVar()
buttonTextSC.set("SetCounter:" + str(counter))


def callbackE():
    global master
    os.system("defaults write com.apple.screencapture name " + defaultScrPrefix + "; killall SystemUIServer")
    master.destroy()
def callbackSC():
    global counter
    counter = int(e.get())
    buttonTextSC.set("SetCounter:" + str(counter))
def callback():
    global counter
    global master
    global prefix
    if (counter == 0):
        prefix = e.get() + "_"
        if prefix!="":
            buttonText.set("Prefix is :" + prefix)
            counter += 1
            buttonTextSC.set("SetCounter:" + str(counter))
    else:
        os.system("defaults write com.apple.screencapture name " + prefix + str(counter) + "; killall SystemUIServer")
        os.system("screencapture -ip")
        counter += 1
        buttonTextSC.set("SetCounter:" + str(counter))

def funcEnter(event):
    global counter
    global e
    callback()
    # e.delete(0, 'end')
def funcEscape(event):
    callbackE()
def funcSC(event):
    callbackSC()


master.bind('<Return>', funcEnter)
master.bind('<Escape>', funcEscape)
master.bind('{', funcSC)

b = tk.Button(master, 
            textvariable = buttonText, 
            width = 10, 
            command = lambda: callback())
b.pack()
eb = tk.Button(master, 
            textvariable = buttonTextE, 
            width = 10, 
            command = lambda: callbackE())
eb.pack()
setCounterB = tk.Button(master, 
                        textvariable = buttonTextSC, 
                        width = 10, 
                        command = lambda: callbackSC())
setCounterB.pack()
master.configure(bg='red')


master.after(1000, )
tk.mainloop()