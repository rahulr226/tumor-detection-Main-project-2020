import numpy as np
import cv2
from matplotlib import pyplot as plt
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from subprocess import call
import shutil
import os
from tkinter.ttk import *
from skimage.morphology import extrema
from skimage.morphology import watershed as skwater
interface = Tk()


def ShowImage(title,img,ctype):
  plt.figure(figsize=(10,5))
  cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
  cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
  if ctype=='bgr':

    b,g,r = cv2.split(img)
    rgb_img = cv2.merge([r,g,b])
    plt.imshow(rgb_img)
  elif ctype=='hsv':
    rgb = cv2.cvtColor(img,cv2.COLOR_HSV2RGB)
    plt.imshow(rgb)
  elif ctype=='gray':
    plt.imshow(img,cmap='gray')
  elif ctype=='rgb':
    plt.imshow(img)
  else:
    raise Exception("Unknown colour type")
  plt.axis('off')
  plt.title(title)
  plt.show()

def f1(fpa):
  img = cv2.imread(fpa)

  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  ShowImage(' noise removed clear image(click X to proceed to next step)', gray, 'gray')
  ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
  ShowImage('Thresholding image:removed normal parts of brain(click X to proceed) ', thresh, 'gray')

  ret, markers = cv2.connectedComponents(thresh)

  marker_area = [np.sum(markers == m) for m in range(np.max(markers)) if m != 0]
  largest_component = np.argmax(marker_area) + 1
  brain_mask = markers == largest_component

  brain_out = img.copy()
  brain_out[brain_mask == False] = (0, 0, 0)

  img = cv2.imread(fpa)
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
  kernel = np.ones((3, 3), np.uint8)
  opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

  sure_bg = cv2.dilate(opening, kernel, iterations=3)

  dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
  ret, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)

  sure_fg = np.uint8(sure_fg)
  unknown = cv2.subtract(sure_bg, sure_fg)

  ret, markers = cv2.connectedComponents(sure_fg)

  markers = markers + 1

  markers[unknown == 255] = 0
  markers = cv2.watershed(img, markers)
  img[markers == -1] = [255, 0, 0]

  im1 = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
  ShowImage('more enhanced image(Click X to extract only tumor part)', im1, 'gray')

  brain_mask = np.uint8(brain_mask)
  kernel = np.ones((8, 8), np.uint8)
  closing = cv2.morphologyEx(brain_mask, cv2.MORPH_CLOSE, kernel)
  ShowImage('Tumor affected area of the person', closing, 'gray')

  brain_out = img.copy()

  brain_out[closing == False] = (0, 0, 0)


def openfile():
    interface.filename=filedialog.askopenfilename()
    print(interface.filename)
    fpa=os.path.basename(interface.filename)
    shutil.copy(interface.filename,'E:/brain tumor/Brain-tumor-segmentation-master')
    f1(fpa)
photo = PhotoImage(file = "Br4.png")
w = Label(interface, image=photo)
w.grid(column=0, row=0)
style = Style()
style.configure('W.TButton', font =
               ('calibri', 15, 'bold'),
                foreground = 'green',background='black')
button = ttk.Button(interface, text="INPUT MRI IMAGE",  style = 'W.TButton', command=openfile)  # <------
button.grid(column=0, row=1)
interface.after(25000, lambda: interface.destroy())
interface.mainloop()



