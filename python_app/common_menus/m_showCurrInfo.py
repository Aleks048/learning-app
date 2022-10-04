import tkinter as tk
from _utils._utils import _BookChoosingMenus

# create UI
master = tk.Tk()
master.title("Current information")
master.geometry("520x40")

# canvas= tk.Canvas(master, width=520, height= 75, bg="red")

# currScrshDir = "Current screenshot dir: " + str(subprocess.check_output("defaults read com.apple.screencapture location", shell=True))[2:-3]
# canvas.create_text(30, 40, anchor="nw", text=currScrshDir)
canvas = _BookChoosingMenus.createCurrentScreenshotDirText(master)
canvas.pack()

master.bind("<Escape>", lambda e:master.destroy())

opacity=1.0
def changeOpacity():
    global opacity
    if opacity < 0.94:
        master.destroy()
    else:
        opacity -= 0.001
        master.attributes('-alpha', opacity)
        master.after(100, changeOpacity)

master.attributes('-alpha', opacity)
master.after(100, changeOpacity)
tk.mainloop()