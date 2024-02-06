# -*- coding: utf-8 -*-
"""
This code opens every image in the IMAGES directory to place boxes

Currently this works with 4 classes:
    Rebound Peak - Right click
    Single Peak - Left click - Mode = 0
    Double Peak - Left click - Mode = 1
    And Poly Peak - Left click - Mode = 2
    
saves txt files in relative form for YoloV5

Created on Wed Jun  7 10:32:22 2023

@author: Mason
"""

import cv2
import os
global img, windowW, windowH, imagePath
FILE_DIR = "C:\\Users\\Mason\\Desktop\\flowCytometerCounter\\IMAGES"
def display_image(path):
    pass # Placeholder
#Generates the trackbar function for cropping the view
def on_trackbar(value):
    global roi, dst
    #Sets the region of interest, the y will always be 0 since we don't want it to change
    roi = (value, 0, windowW, windowH)  # Update ROI for display
    #Crops the image to be from 0 - window height and from the passed value to the windowW
    dst = img[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]
    cv2.imshow("RAW DATA", dst)
    
#Helper function to convert from pixels to relative placements using (xcenter, ycenter, width, height) as YOLO wants
def exportRelativeData(classID, point1, point2, w, h, outDir):
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

def draw_rectangle(event, x, y, flags, param):
   global ix, iy, drawing, img
   h, w, l = img.shape
   
   outPath = imagePath.replace("png", "txt")
   outPath = outPath.replace("IMAGES", "DATA")
   
   if event == cv2.EVENT_RBUTTONDOWN:
       drawing = True
       #Gets mouse position and stores it as the first point
       ix = x + roi[0]
       iy = y
   elif event == cv2.EVENT_RBUTTONUP:
       #Stores the second position then draws a rectangle from both points
       drawing = False
       point1 = (ix, iy)
       point2 = (x+roi[0], y)
       cv2.rectangle(img, point1, point2, (0, 255, 0), 2)
       #Appends the rectangle coordinates to the data file
       exportRelativeData(0, point1, point2, w, h, outPath)
       #Updates the image to show the rectangle
       cv2.imshow("RAW DATA", dst)
       
   if event == cv2.EVENT_LBUTTONDOWN:
      drawing = True
      ix = x + roi[0]
      iy = y
#Cases for switching from SINGLE, DOUBLE, and POLY Peaks allowing for only having to use the mouse when selecting the peaks
   elif event == cv2.EVENT_LBUTTONUP and mode == 0:
      drawing = False
      point1 = (ix, iy)
      point2 = (x+roi[0], y)
      cv2.rectangle(img, point1,point2,(0, 255, 255), 2)
      cv2.imshow("RAW DATA", dst)
      
      exportRelativeData(1, point1, point2, w, h, outPath)
   elif event == cv2.EVENT_LBUTTONUP and mode == 1:
      drawing = False
      point1 = (ix, iy)
      point2 = (x+roi[0], y)
      cv2.rectangle(img, point1,point2,(255, 0, 0), 2)
      cv2.imshow("RAW DATA", dst)
   
      exportRelativeData(2, point1, point2, w, h, outPath)
      
   elif event == cv2.EVENT_LBUTTONUP and mode == 2:
      drawing = False
      point1 = (ix, iy)
      point2 = (x+roi[0], y)
      cv2.rectangle(img, point1,point2,(0, 0, 255), 2)
      cv2.imshow("RAW DATA", dst)
      
      exportRelativeData(3, point1, point2, w, h, outPath)

      
for image in os.listdir(FILE_DIR):
    
    #Finds and opens the image
    imagePath = os.path.join(FILE_DIR, image)
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
        print("GREEN - RIGHT CLICK - REBOUND PEAK\n\nUSE M TO SWITCH BETWEEN THE FOLLOWING MODES:\nYELLOW - LEFT CLICK - SINGLE PEAK\nBLUE - LEFT CLICK - DOUBLE PEAK\nRed - LEFT CLICK - Poly Peaks (>2 Particles in a single peak)\n")
        print("Single Peaks on Left Click PRESS M TO CYCLE FORWARD, N TO CYCLE BACKWARD\n")
        print("PRESS Q TO QUIT")
        # Connect the mouse button to our callback function
        cv2.setMouseCallback("RAW DATA", draw_rectangle)   
        #Switches mode and handles click events
        while(1):  
            k = cv2.waitKey(1) & 0xFF  
            if k == ord('m'):  
                if mode < 2: mode += 1 
                else: mode = 0 
                print("Single Peaks" if mode == 0 else ("Double Peaks" if mode == 1 else "Poly Peaks"), "PRESS M TO CYCLE FORWARD, N TO CYCLE BACKWARD\n")
            elif k == ord('n'):  
                if mode > 0 : mode -= 1 
                else: mode = 2 
                print("Single Peaks" if mode == 0 else ("Double Peaks" if mode == 1 else "Poly Peaks"), "PRESS M TO CYCLE FORWARD, N TO CYCLE BACKWARD\n")
            elif(k == ord('q')):  
                break  
        cv2.destroyAllWindows()
    else:
        print("ANNOTATION ALREADY CREATED, SKIPPING")