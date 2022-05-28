import tkinter as tk
from tkinter import Image
from tkinter import filedialog as fd
import cv2 as cv
import numpy as np
import sys, time, os
from PyPDF2 import PdfFileReader, PdfFileWriter
from pdf2image import convert_from_path
from pdf2image.exceptions import (PDFInfoNotInstalledError,PDFPageCountError,PDFSyntaxError)
from PIL import Image, ImageTk

wheight = 600
wwidth = 600
dialogmargin = 50
pages = []
current_index = 0

preproc = False

class App(tk.Frame):
    def __init__(self, parent): 
        tk.Frame.__init__(self, parent) #parent is the main canvas

        self.createCoordinates(parent)
        self.createCanvas()

        filebutton = tk.Button(parent, text="open pdf",command=self.openFileDialog) #wont appear outside of canvas probably a class problem
        filebutton.configure(width = 10, activebackground = "#33B5E5")
        filebutton_window = self.canvas.create_window((wwidth/2,wheight-45), window=filebutton)

        leftbutton = tk.Button(parent, text="<",command=self.left)
        leftbutton.configure(width = 5, activebackground = "#33B5E5")
        leftbutton_window = self.canvas.create_window(((wwidth/2)-100,wheight-45), window=leftbutton)

        rightbutton = tk.Button(parent, text=">",command=self.right)
        rightbutton.configure(width = 5, activebackground = "#33B5E5")
        rightbutton_window = self.canvas.create_window(((wwidth/2)+100,wheight-45), window=rightbutton)

        applypreproc = tk.Button(parent, text="toggle preproc",command=self)
        applypreproc.configure(width = 10, activebackground = "#33B5E5")
        applypreproc_window = self.canvas.create_window(((wwidth/2),wheight-80), window=applypreproc)

    def drawImage(self):
        global current_index
        self.canvas.delete("image")
        self.img = pages[current_index].resize((wwidth-20, wheight-20), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(self.img)
        self.canvas.create_image(wwidth/2,(wheight/2)+100,image=self.img,tags="image") #(wheight/2)+100 displacement so there is space for the selection and transformation of the rectangle 
    
    def CutAndLoadPdf(self,start,end,fn):
        global pages
        pdf_writer = PdfFileWriter()
        pdf_reader = PdfFileReader(open(fn, 'rb'))
        
        for page_num in range(start, end):
            pdf_writer.addPage(pdf_reader.getPage(page_num))
        
        cut_filename = f'cut.pdf'
        with open(cut_filename,'wb') as out:
            pdf_writer.write(out)

        pages = convert_from_path(cut_filename)
        print("pages loaded",len(pages))

    def openFileDialog(self):
        global pages
        filename = fd.askopenfilename()
        self.CutAndLoadPdf(1,20,filename)
        self.drawImage()

    def createCoordinates(self, parent):
        self.parent = parent
        self.rectx0 = 0
        self.recty0 = 0
        self.rectx1 = 0
        self.recty1 = 0
        self.rectid = None

    def createCanvas(self):
        self.canvas = tk.Canvas(self.parent, width = wwidth, height = wheight - dialogmargin, bg = "white")
        self.canvas.grid(row=0, column=0, sticky='nsew')

    def left(self):
        global current_index
        current_index -= 1
        self.drawImage()

    def right(self):
        global current_index
        current_index += 1
        self.drawImage()
        

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(str(wheight)+"x"+str(wwidth))
    app = App(root)
    root.mainloop()
