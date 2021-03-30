import tkinter as tk
from tkinter import ttk

# setup the window with a minimum size
win = tk.Tk()
win.minsize(100, 100)

# create the tabs
tabs = ttk.Notebook(win)

# first frame
fstations = ttk.Frame(tabs)
tabs.add(fstations, text='WiFi Signals')

# first frame
fethernet = ttk.Frame(tabs)
tabs.add(fethernet, text='Ethernet')

# pack the tabs into all the space
tabs.pack(expand=1, fill='both')

# start maximized
win.attributes('-zoomed', True)

# launch
win.mainloop()
