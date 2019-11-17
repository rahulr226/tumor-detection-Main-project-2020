from tkinter import filedialog
from tkinter import *

root = Tk()
root.filename =  filedialog.askopenfile(initialdir ="/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
print (root.filename)