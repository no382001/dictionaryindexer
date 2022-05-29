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
shown_image = []
current_index = 0

preproc = False


#--------START----------- adaptive threshold
adaptiveOn = True
adaptive_options = ["cv.ADAPTIVE_THRESH_MEAN_C","cv.ADAPTIVE_THRESH_GAUSSIAN_C"]
cv_adaptive = eval(adaptive_options[0])

thresh_options = ["cv.THRESH_BINARY_INV","cv.THRESH_BINARY"]
cv_thresh =  eval(thresh_options[0])
#--------END------------- adaptive threshold


#--------START----------- dilation
dilationOn = True

dilate_no_iteration = 2

#--------END------------- dilation

openingOn = True
opening_no_iteration = 2

closingOn = False
closing_no_iteration = 2






#--------START----------- kernel
# kernel_options = ["cv.MORPH_CROSS"] #any other option wont work, bc kernel is 8bit?
kernel_options = ["cv.MORPH_CROSS","cv.MORPH_OPEN","cv.MORPH_GRADIENT","cv.MORPH_TOPHAT","cv.MORPH_BLACKHAT"]
cv_kernel = cv.getStructuringElement(eval(kernel_options[0]),np.uint8((3, 3)))
#--------END------------- kernel






allowed_difference = 30

class App(tk.Frame):
    
    def preProcess(self):
        global pages, current_index, cv_kernel, shown_image, adaptiveOn, openingOn, closingOn

        #converting PIL to np array
        nparray = np.array(pages[current_index])
        #inverting RGB to BGR for opencv compatibility
        nparray = nparray[:, :, ::-1].copy()
        #BGR to Grayscale
        open_cv_image = cv.cvtColor(nparray, cv.COLOR_BGR2GRAY)

        #applying threshold, making the image 2bits in color, and inverting the image
        #                                       src         maxVal    admeth  thmeth   blocksize    constant
        if adaptiveOn:
            open_cv_image = cv.adaptiveThreshold(open_cv_image, 255, cv_adaptive,cv_thresh,9,11)
        
        #dilating, to smudge visible elements, essentially normalizing the image
        if dilationOn:
            open_cv_image = cv.dilate(open_cv_image,cv_kernel, iterations=dilate_no_iteration)
        
        if openingOn:
            open_cv_image = cv.morphologyEx(open_cv_image, cv.MORPH_OPEN, cv_kernel, iterations=dilate_no_iteration)

        if closingOn:
            open_cv_image = cv.morphologyEx(open_cv_image, cv.MORPH_CLOSE, cv_kernel, iterations=dilate_no_iteration)

        #create a save state of transformations
        #and dropdown menu selects these morph transformations, well hidden

        return open_cv_image

        #resizing image to a lesser size for time efficiency
        #open_cv_image = resizeCvImage(open_cv_image)

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

        applypreproc = tk.Button(parent, text="toggle preproc",command=self.togglePP)
        applypreproc.configure(width = 10, activebackground = "#33B5E5")
        applypreproc = self.canvas.create_window(((wwidth/2),wheight-80), window=applypreproc)


        dilate_scale =  tk.Scale(parent,from_= 0,to = 100, orient='horizontal', command=self.dilateScaleChanged)
        dilate_scale.set(dilate_no_iteration)
        dilate_scale.configure(width = 10, activebackground = "#33B5E5")
        dilate_scale_window = self.canvas.create_window(((wwidth/2),wheight-150), window=dilate_scale)

        
        global kernel_options
        default_kernel = tk.StringVar()
        default_kernel.set(kernel_options[0])

        kernel_dropdown = tk.OptionMenu(parent, default_kernel,*kernel_options,command=self.kernelSelected)
        kernel_dropdown.configure(width = 20, activebackground = "#33B5E5")
        kernel_dropdown_window = self.canvas.create_window(((wwidth/2),wheight-180), window=kernel_dropdown)

        global adaptive_options
        default_adaptive = tk.StringVar()
        default_adaptive.set(adaptive_options[0])

        adaptiveon_button = tk.Button(parent, text="toggle_adaptive",command=self.toggleAdaptive)
        adaptiveon_button.configure(width = 10, activebackground = "#33B5E5")
        adaptiveon_button_window = self.canvas.create_window(((wwidth/2)+170,wheight-210), window=adaptiveon_button)

        adaptive_dropdown = tk.OptionMenu(parent, default_adaptive,*adaptive_options,command=self.adaptiveSelected)
        adaptive_dropdown.configure(width = 20, activebackground = "#33B5E5")
        adaptive_dropdown_window = self.canvas.create_window(((wwidth/2),wheight-210), window=adaptive_dropdown)

        global thresh_options
        default_thresh = tk.StringVar()
        default_thresh.set(thresh_options[0])

        thresh_dropdown = tk.OptionMenu(parent, default_thresh,*thresh_options,command=self.threshSelected)
        thresh_dropdown.configure(width = 20, activebackground = "#33B5E5")
        thresh_dropdown_window = self.canvas.create_window(((wwidth/2),wheight-240), window=thresh_dropdown)

        dilateon_button = tk.Button(parent, text="toggle_dilate",command=self.toggleDilate)
        dilateon_button.configure(width = 10, activebackground = "#33B5E5")
        dilateon_button_window = self.canvas.create_window(((wwidth/2)+170,wheight-240), window=dilateon_button)

        openingon_button = tk.Button(parent, text="toggle_opening",command=self.toggleOpening)
        openingon_button.configure(width = 10, activebackground = "#33B5E5")
        openingon_button_window = self.canvas.create_window(((wwidth/2)+170,wheight-280), window=openingon_button)

        closingon_button = tk.Button(parent, text="toggle_closing",command=self.toggleClosing)
        closingon_button.configure(width = 10, activebackground = "#33B5E5")
        closingon_button_window = self.canvas.create_window(((wwidth/2)+170,wheight-320), window=closingon_button)





    def drawImage(self):
        global current_index, shown_image
        self.canvas.delete("image")

        if not preproc:
            self.img = pages[current_index].resize((wwidth-20, wheight-20))
        else:
            self.img = Image.fromarray(self.preProcess()).resize((wwidth-20, wheight-20))

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
        os.remove("cut.pdf")#                       use /tmp instead
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

#----------------START--------------------- buttons
    def left(self):
        global current_index
        current_index -= 1
        self.drawImage()

    def right(self):
        global current_index
        current_index += 1
        self.drawImage()

    def togglePP(self):
        global preproc
        preproc = not preproc
        self.drawImage()

    def dilateScaleChanged(self,passed):
        global dilate_no_iteration
        dilate_no_iteration = int(passed)
        self.drawImage()

    def kernelSelected(self,passed):
        global cv_kernel
        cv_kernel = cv.getStructuringElement(eval(passed),np.uint8((3, 3)))
        self.drawImage()

    def adaptiveSelected(self,passed):
        global cv_adaptive
        cv_adaptive = eval(passed)
        self.drawImage()

    def threshSelected(self,passed):
        global cv_thresh
        cv_thresh = eval(passed)
        self.drawImage()

    def toggleAdaptive(self):
        global adaptiveOn
        adaptiveOn = not adaptiveOn
        self.drawImage()

    def toggleDilate(self):
        global dilationOn
        dilationOn = not dilationOn
        self.drawImage()

    def toggleOpening(self):
        global openingOn
        openingOn = not openingOn
        self.drawImage()

    def toggleClosing(self):
        global closingOn
        closingOn = not closingOn
        self.drawImage()

#----------------END--------------------- buttons
        

        

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(str(wheight)+"x"+str(wwidth))
    app = App(root)
    root.mainloop()
