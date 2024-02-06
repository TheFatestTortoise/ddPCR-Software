# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 15:27:48 2023

@author: Mason
""" 
import cv2
import os
global img, windowW, windowH, imagePath

from PIL import Image
FILE_DIR = "C:\\Users\\Mason\\Desktop\\flowCytometerCounter\\IMAGES"

#Generates the trackbar function for cropping the view
def on_trackbar(value):
    global roi, dst
    #Sets the region of interest, the y will always be 0 since we don't want it to change
    roi = (value, 0, windowW, windowH)  # Update ROI for display
    #Crops the image to be from 0 - window height and from the passed value to the windowW
    dst = img[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]
    cv2.imshow("RAW DATA", dst)
    
#Helper function to convert from pixels to relative placements using (xcenter, ycenter, width, height) as YOLO wants
def generateFullImage(imgDir):
    count = 0
    for image in os.listdir(FILE_DIR):
        
        #Finds and opens the image
        imagePath = os.path.join(FILE_DIR, image)
        
        if os.path.isidr(imagePath):
          print(image, "is not an image, skipping")
          continue
        else:
            count += 1
    
    outputImage = Image.new('RGB', (int(count * (axBoxT.x1-axBoxT.x0)), int(axBoxT.y1-axBoxT.y0)), (250, 250, 250))
    
    #Opens each temp image and copies it to the new image we just created
    for j in range(count):
        with Image.open(TEMP_FILE_NAMES[j]) as im:
        
            w, h = im.size

            outputImage.paste(im, (int(j*(axBoxT.x1-axBoxT.x0)), 0))

    #Saves the stitched image as a PNG
    outputImage.save(OUT_FILE, "PNG")
    
def readAndConvert(inDir):
    x1t, y1t = point1
    x2t, y2t = point2
    
    x1 = x1t / w
    x2 = x2t / w
    
    y1 = y1t / h
    y2 = y2t / h
    
    #Prevents overspill boxes
    if x1 < 0:
        x1 = 0
    elif x2 > 1:
        x2 = 1
        
    if y1 < 0:
        y1 = 0
    elif y2 > 1:
        y2 = 1
    
    #Takes the average of x1 and x2, y1 and y2 respectivley for each box to find center x and y
    xcenter = (x1 + x2)/2
    ycenter = (y1 + y2)/2
    
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    
    if xcenter < 0:
        xcenter = 0
    elif xcenter > 1:
        xcenter = 1
        
    if ycenter < 0:
        ycenter = 0
    elif ycenter > 1:
        ycenter = 1
        
    #APPENDS info in YOLO format to a txt file
    with open(outDir, "a") as w:
        w.write("{} {:.6f} {:.6f} {:.6f} {:.6f}".format(classID, xcenter, ycenter, width, height) + "\n")




end = False
      
for image in os.listdir(FILE_DIR):
    
    #Finds and opens the image
    imagePath = os.path.join(FILE_DIR, image)
    
    if os.path.isidr(imagePath):
      print(image, "is not an image, skipping")
      continue
    
    outPath = imagePath.replace("png", "txt")
    outPath = outPath.replace("IMAGES", "DATA")
    
    if not os.path.isfile(outPath):
    
        img = cv2.imread(os.path.join(FILE_DIR, image))
        
        #Gets the image size and creates the window
        h, w, l = img.shape
        cv2.namedWindow("RAW DATA")
        
        #Resizes image
        img = cv2.resize(img, (w*2, h*2))
        h, w, l = img.shape
        
        #Resizes window
        cv2.resizeWindow("RAW DATA", (1500, 800))
        
        x, y, windowW, windowH = cv2.getWindowImageRect('RAW DATA')
        
        #Links trackbar to trackbar function and adds it to the window
        cv2.createTrackbar('x', 'RAW DATA', 1, w-windowW, on_trackbar)
      
        
        mode = 0

        print("PRESS Q TO SWITCH IMAGES")
        print("PRESS ESC TO CLOSE")
        # Connect the mouse button to our callback function
        cv2.setMouseCallback("RAW DATA", draw_rectangle)   
        #Switches mode and handles click events
        while(1):  
            k = cv2.waitKey(1) & 0xFF  
            if(k == ord('q')):  
                break
            elif(k == 27):
                end = True
                break
        cv2.destroyAllWindows()
    else:
        print("ANNOTATION ALREADY CREATED, SKIPPING")

    if end:
        break