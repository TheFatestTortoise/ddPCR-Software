# -*- coding: utf-8 -*-
"""
Splits files from a full sized file (upwards of 10000x470) into smaller chunks
The chunks don't have bounding boxes on the edges and are autosized

This file could do with some cleaning up
Tying all math into chunk rate would be good too


Created on Mon Jun 12 13:56:00 2023

@author: Mason
"""
import os
import cv2
import random

DEBUG = False
GENERATE_BACKGROUNDS = True

END_FILE_CUTOFF = 0.35

numRemoved = 0

#Large PNG files of waveforms
IMAGE_DIR     = r"C:\Users\Mason\Desktop\flowCytometerCounter\IMAGES"
#TXT data files of bounding boxes
BOX_DIR       = r"C:\Users\Mason\Desktop\flowCytometerCounter\DATA"
#Save images out after splitting
IMAGE_OUT_DIR = r"C:\Users\Mason\Desktop\flowCytometerCounter\SPLIT_IMAGES"

BOX_OUT_DIR   = r"C:\Users\Mason\Desktop\flowCytometerCounter\SPLIT_BOXES"

#CONSTANT SINGLE CUT IMAGE SIZE (W, H)
IMG_SIZE = (930, 467)

#Number of chunks per single cut image
CHUNK_RATE = 4

RANDOM_SPREAD_FACTOR = 1/3

def on_trackbar(value):
    global roi, dst
    #Sets the region of interest, the y will always be 0 since we don't want it to change
    roi = (value, 0, windowW, windowH)  # Update ROI for display
    #Crops the image to be from 0 - window height and from the passed value to the windowW
    dst = img[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]
    cv2.imshow("RAW DATA", dst)

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

global windowW, windowH
for txt in os.listdir(BOX_DIR):
    cleanBoxesR = []
    cleanBoxesP = []
    chunks = []
    searchStart = 0
    
    boxInDir = os.path.join(BOX_DIR, txt)
    
    imgInDir = os.path.join(IMAGE_DIR, txt)
    imgInDir = imgInDir.replace("txt", "png")

    img = cv2.imread(imgInDir)
    h, w , l = img.shape

    numChunks = int(w/IMG_SIZE[0]) * CHUNK_RATE
    
    cv2.namedWindow("RAW DATA")
    cv2.resizeWindow("RAW DATA", (1500, 800))
    x, y, windowW, windowH = cv2.getWindowImageRect('RAW DATA')
    
    cv2.createTrackbar('x', 'RAW DATA', 1, w-windowW, on_trackbar)
    
    with open(boxInDir, "r") as file:
       boxes = file.readlines()
    for box in boxes:
        scBoxR = box.replace('\n', '').split(' ')
        #ClassID, XCENTER, YCENTER, WIDTH, HEIGHT
        scBoxP = [int(scBoxR[0]), float(scBoxR[1])*w, float(scBoxR[2])*h, float(scBoxR[3])*w, float(scBoxR[4])*h]

        cleanBoxesR.append([int(scBoxR[0]), float(scBoxR[1]), float(scBoxR[2]), float(scBoxR[3]), float(scBoxR[4])])
        #CLASSID, X1, Y1, X2, Y2
        cleanBoxesP.append([scBoxP[0], int(scBoxP[1]-scBoxP[3]/2), int(scBoxP[2]-scBoxP[4]/2), int(scBoxP[1]+scBoxP[3]/2), int(scBoxP[2]+scBoxP[4]/2)])
        if scBoxR[0] == 0:
            color = (0, 255, 0)
        else:
            color = (255, 0, 0)
            
        point1 = (cleanBoxesP[-1][1], cleanBoxesP[-1][2])
        point2 = (cleanBoxesP[-1][3], cleanBoxesP[-1][4])
        if DEBUG:
            cv2.rectangle(img, point1, point2, color, 2)
    
            cv2.imshow("RAW DATA", dst)
    
    #Creawting chunked images
    for i in range(numChunks):
        image_generated = False
        exportBoxes = []
        
        xSlide = random.gauss(0, .25) * IMG_SIZE[0]/(CHUNK_RATE) * RANDOM_SPREAD_FACTOR
        #       STARTING POINT           AMMOUNT TO SLIDE EACH BOX   RANDOM SLIDE ADJUSTMENT   Y = 0 -> Height
        pointAX = int((i * (IMG_SIZE[0] / 4)) + xSlide)
        if pointAX < 0:
            pointAX = 0
        pointA = [pointAX, 0]
        pointB = [int( (IMG_SIZE[0] / 2) + (i * (IMG_SIZE[0] / 4)) + xSlide), IMG_SIZE[1]]

        for j in range(len(cleanBoxesP) - searchStart):
            #Check for a box on the edge
            currentBox = cleanBoxesP[j+searchStart]
            if currentBox[1] < pointA[0] and currentBox[3] > pointA[0]:
                #Box overlaps left side 
                pointA[0] = currentBox[1]

                exportBoxes.append([currentBox[0], (0, currentBox[2]), (currentBox[3] - pointA[0], currentBox[4])])
            elif currentBox[1] < pointB[0] and currentBox[3] > pointB[0]:
                #Box overlaps left side
                pointB[0] = currentBox[1]
                
                exportBoxes.append([currentBox[0], (currentBox[1] - pointA[0], currentBox[2]), (currentBox[3] - pointA[0], currentBox[4])])
            elif currentBox[1] < pointB[0] and currentBox[3] > pointA[0]:
                exportBoxes.append([currentBox[0], (currentBox[1] - pointA[0], currentBox[2]), (currentBox[3] - pointA[0], currentBox[4])])

        for box in exportBoxes:
            exportRelativeData(box[0], box[1], box[2], pointB[0]-pointA[0], pointB[1], os.path.join(BOX_OUT_DIR, txt.replace(".txt", str(i) + ".txt")))
            if not image_generated:
                cv2.imwrite(os.path.join(IMAGE_OUT_DIR, txt.replace(".txt", str(i) + ".png")), img[0:pointB[1], pointA[0]:pointB[0]])
                image_generated = True
        if GENERATE_BACKGROUNDS and not image_generated and pointB[0] < w * (1-END_FILE_CUTOFF):
            with open( os.path.join(BOX_OUT_DIR, txt.replace(".txt", str(i) + ".txt")), 'w') as fp:
                pass
            cv2.imwrite(os.path.join(IMAGE_OUT_DIR, txt.replace(".txt", str(i) + ".png")), img[0:pointB[1], pointA[0]:pointB[0]])
        elif GENERATE_BACKGROUNDS and not image_generated and not pointB[0] < w * (1-END_FILE_CUTOFF):
            numRemoved += 1
            print('Excess background removed', numRemoved)
        if i % 3 == 0:
            boxColor = (0, 0, 0)
        elif i % 3 == 1:
            boxColor = (100, 100, 100)
        else:
            boxColor = (0, 0, 255)
            
        if DEBUG:
            chunks.append([pointA, pointB])
            cv2.rectangle(img, pointA, pointB, boxColor, 2)
            cv2.imshow("RAW DATA", dst)
        cv2.destroyAllWindows()