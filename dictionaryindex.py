import cv2 as cv
import numpy as np
import sys, time, os
from PyPDF2 import PdfFileReader, PdfFileWriter
from pdf2image import convert_from_path
from pdf2image.exceptions import (PDFInfoNotInstalledError,PDFPageCountError,PDFSyntaxError)
from PIL import Image

def CutAndLoadPdf(start,end):
    global pages
    pdf_writer = PdfFileWriter()
    start_page = start
    end_page = end
    for page_num in range(start_page, end_page):
        pdf_writer.addPage(pdf_reader.getPage(page_num))
    
    cut_filename = f'cut.pdf'
    with open(cut_filename,'wb') as out:
            pdf_writer.write(out)
    
    pages = convert_from_path(cut_filename)

def resizeCvImage(cvimage,newsizex=300):
    iw = cvimage.shape[1]
    height = int(cvimage.shape[0] * (newsizex/iw))
    dim = (newsizex, height)
    img = cv.resize(cvimage, dim, interpolation = cv.INTER_AREA)
    return img

def FindMatches(pages):
    global pot, kernel, curr_sequence
    for k,p in enumerate(pages):
        #converting PIL to np array
        nparray = np.array(p)
        #inverting RGB to BGR for opencv compatibility
        nparray = nparray[:, :, ::-1].copy()
        #BGR to Grayscale
        open_cv_image = cv.cvtColor(nparray, cv.COLOR_BGR2GRAY)
        #applying threshold, making the image 1bit in color, and inverting the image
        open_cv_image = cv.adaptiveThreshold(open_cv_image, 255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV,9,11)
        #dilating, to smudge visible elements, essentially normalizing the image
        open_cv_image = cv.dilate(open_cv_image,kernel,iterations = it)
        #resizing image to a lesser size for time efficiency
        open_cv_image = resizeCvImage(open_cv_image)
        
        #determining how many times the template image can fit in the base image
        height, width = open_cv_image.shape
        ratio = height//indextemp.shape[0]
        base_r_y = height//ratio
        for i in range(0,ratio):
            #for each occurence cut out a rectangle that is the size of the template image 
            cropped_img = open_cv_image[(base_r_y)*i:(base_r_y)*(i+1)]
            #on the scale of 0 (white) to 255 (black) (this is because we inverted the picture a few lines back) determine the average by row
            #then determine the average from all of the rows
            avg = np.average(np.average(cropped_img, axis=0),axis=0)
            #if the average (that we got from this slice of the image) corresponds to the average of our template
            if int(avg) <= int(avg_ind)+difference:
                #add to the result array, and quit
                pot.append([open_cv_image,(curr_sequence*maxpagecount)+k])
                break

t = time.time()

pages = [] #where each the PIL images of each sequence is stored
pdf_reader = PdfFileReader(open(str(sys.argv[1]), 'rb'))

indextemp = cv.imread(str(sys.argv[2]))
indextemp = cv.cvtColor(indextemp, cv.COLOR_BGR2GRAY)
indextemp = cv.adaptiveThreshold(indextemp, 255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV,9,11)
kernel = cv.getStructuringElement(cv.MORPH_CROSS,(3,3))

# number of iterations when dilating image
try:
    it = sys.argv[4] 
except:
    it = 2

try:
    difference = sys.argv[3]
except:
    difference = 30


indextemp = cv.dilate(indextemp,kernel,iterations = it)
indextemp = resizeCvImage(indextemp)
avg_ind = np.average(np.average(indextemp, axis=0),axis=0)

pot = [] #where match results are stored

pdf_pagecount = pdf_reader.getNumPages()
#max number of pages in a batch
maxpagecount = 100
sequence = pdf_pagecount // maxpagecount
curr_sequence = 0
for i in range((sequence)):
            curr_sequence = i      
            CutAndLoadPdf((i*maxpagecount)+1,(i+1)*maxpagecount) #fills pages[] with PIL images from the pdf
            FindMatches(pages) #adds matches to pot[]
            print(i,"runtime:",1000*(time.time()-t),"ms")
            t = time.time()

remainder = pdf_pagecount - (sequence)*maxpagecount
if remainder != 0:
    curr_sequence += 1
    CutAndLoadPdf((sequence*maxpagecount)+1,(sequence*maxpagecount)+remainder)
    FindMatches(pages)
    print("runtime:",1000*(time.time()-t),"ms")

os.remove("cut.pdf")

images = []
for i,j in enumerate(pot):
    img = cv.cvtColor(j[0], cv.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    images.append(img)
images[0].save("out.pdf", save_all=True, append_images=images[1:])

pdf_out = PdfFileWriter()
pdf_reader = PdfFileReader(open("out.pdf", 'rb'))
for i,k in enumerate(pot):
    pdf_out.addPage(pdf_reader.getPage(i))
    pdf_out.addBookmark(str(k[1]+2),i)

os.remove("out.pdf")
output_f = f'output.pdf'
with open(output_f,'wb') as out:
    pdf_out.write(out)
