"""
Converts csv files to graphed png files

This uses a system of plotting smaller sections and then stitching them together
These large images are useful for tagging since it can all be done in one push
which is nice

For inference save the temp images instead of the whole images

Created on Tue Jun  6 16:08:44 2023

@author: Mason
"""
import sys
import argparse
import numpy as np
import pandas as pd
import shutil
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import transforms
matplotlib.use('Agg')
import os

from PIL import Image, ImageDraw
#Setup variables
#Number of points per graph
SPLIT_NUMBER = 5000

countingResults = []
files = []
finalTimes = []
particleRates = []

global ROOT_DIR, TEMP_DIR, OUT_DIR

#Directories to pull and save data
#CSV location


r = 5

CWD_DIR = os.path.dirname(os.getcwd())
ROOT_DIR = os.path.join(CWD_DIR, "DETECTION_DATA")
#Save temporary png files generated before stitching
TEMP_DIR = os.path.join(CWD_DIR, "DETECTION_IMAGES")
#YOLOV5 Detection DIR
DETECTION_DIR = os.path.join(CWD_DIR, r"yolov5\runs\detect")
#Saves tagged images
IMG_OUT_DIR = os.path.join(CWD_DIR, "TAGGED_IMAGES")

#A list of temporary file names to save each axis to
TEMP_FILE_NAMES = []
for m in range(60):
    if m < 10:
        TEMP_FILE_NAMES.append(os.path.join(TEMP_DIR, "TEMP0" + str(m) + ".png"))
    else:
        TEMP_FILE_NAMES.append(os.path.join(TEMP_DIR, "TEMP" + str(m) + ".png"))

#The big man himself
def convert(filename):
    matplotlib.use('Agg')

    #Creates full dataframe from csv
    df = pd.read_csv(os.path.join(ROOT_DIR, filename),names = ["Time", "Amps"])
    if("--truncate" in sys.argv):
        numTruncate = int(sys.argv[sys.argv.index("--truncate") + 1])
        print("Truncating to", numTruncate)
        df = df.iloc[:numTruncate, :]
    dfSize = len(df)
    
    #Splits into chunks based on SPLIT_NUMBER
    splitDFs = []
    
    if dfSize % SPLIT_NUMBER != 0:
        numSplits = dfSize//SPLIT_NUMBER + 1
        for i in range(numSplits - 1):
            splitDFs.append(df.iloc[i*SPLIT_NUMBER:(i+1)*SPLIT_NUMBER, :])
        splitDFs.append(df.iloc[(numSplits-1)*SPLIT_NUMBER:, :])
    else:
        numSplits = dfSize//SPLIT_NUMBER
        
        for i in range(numSplits):
            splitDFs.append(df.iloc[i*SPLIT_NUMBER:(i+1)*SPLIT_NUMBER, :])


    previousTime = int(splitDFs[-1]['Time'].iloc[-1])

    populateRows = []
    for k in range(SPLIT_NUMBER - len(splitDFs[-1])):
        previousTime += splitDFs[-1]['Time'].diff().mean()
        populateRows.append({'Time' : previousTime, 'Amps' : 0})
    finalTime = (df['Time'].iloc[-1], k * splitDFs[-1]['Time'].diff().mean())
    splitDFs[-1] = pd.concat([splitDFs[-1], pd.DataFrame(populateRows)])
    #Create a figure of the appropriate size for the number of graphs
    
    for l in range(numSplits):
        figmeister, ax = plt.subplots(figsize=(12, 6))
        #removes the margins making it easier to stitch back together
        ax.margins(x=0)
        #Turns off the axis, we don't need them and it makes it impossible to stitch together, could probably keep it in but I can't be bothered
        ax.axis('off')
        
        plt.ylim([-4.5, 4.5])
        #Plots the first dataframe Time vs Amps(amplitude in volts not current) as a black line with 0.3 size
        ax.plot(splitDFs[l].Time, splitDFs[l].Amps, 'k', linewidth = 0.3)
        figmeister.canvas.draw()
        #Gets the bounding box of the plot in pixels
        axBoxT = ax.get_tightbbox(renderer = figmeister.canvas.get_renderer())
        #Converts the bounding box to inches using the defult DPI of matplotlib
        axBox = transforms.Bbox([[axBoxT.x0/100, axBoxT.y0/100],[axBoxT.x1/100, axBoxT.y1/100]])
        #Saves the bounding box to the temp name
        figmeister.savefig(TEMP_FILE_NAMES[l], bbox_inches=axBox)
        #Closes the fucking plot thank god I don't have to keep doing this manually
        plt.close('figmeister')

    return(finalTime)
#Does the loop
def detect(weights):
    for file in os.listdir(ROOT_DIR):
        files.append(file)
        #Temporarily hardcoded, can be changed later to be dyanmic to images but they seem
        #Consistently sized and I don't know of a way to do it that isn't stupid
        
        w = 930
        h = 462
    
        filePoints = []
        currentFiles = os.listdir(DETECTION_DIR)
        peakCount = 0
        finalTimes.append(convert(file))
        os.chdir(CWD_DIR)
        detectionCode = r'python yolov5\detect.py --weights ' + weights +  r' --source DETECTION_IMAGES --agnostic --data yolov5\data\Peak_Detection.yaml  --save-txt'
        os.system(detectionCode)
        detectionOut = np.setdiff1d(os.listdir(DETECTION_DIR), currentFiles)
        theDir = os.path.join(DETECTION_DIR, detectionOut[0], 'labels')
        firstPeak = True
        for countingFile in os.listdir(theDir):
            currentPoints = []
            with open(os.path.join(theDir, countingFile), "r") as filed:
               boxes = filed.readlines()
            open(countingFile, 'w').close()
            for row in boxes:
                tempBox = row.replace('\n', '').split(' ')
                box = [int(tempBox[0]), int(float(tempBox[1])*w), int(float(tempBox[2])*h), int(float(tempBox[3])*w), int(float(tempBox[4])*h)]
                peakCount += box[0]
                currentPoints.append((box[1], box[2]-(box[4]/2), box[0]))
                if firstPeak:
                    firstPeak = False
                    print(tempBox[1], sum(finalTimes[-1]))
                    startTime = (float(tempBox[1]) * sum(finalTimes[-1]))
                    print(startTime)
            filePoints.append(currentPoints)
        countingResults.append(peakCount)
    
        particleRates.append((peakCount * 60000) / (finalTimes[-1][0] - startTime))
        
        numSplits = len([name for name in os.listdir(TEMP_DIR)])
        
        outputImage = Image.new('RGB', (numSplits * w, h), (250, 250, 250))
        draw = ImageDraw.Draw(outputImage)
    
        shutil.rmtree(os.path.join(DETECTION_DIR, detectionOut[0]))
        imgNumber = 0
        
        images = os.listdir(TEMP_DIR)
        image = images.sort()
        
        print(images)
        
        for image in images:
            
            with Image.open(os.path.join(TEMP_DIR, image)) as im:
                outputImage.paste(im, (imgNumber*w, 0))
            #os.remove(os.path.join(TEMP_DIR, image))
            imgNumber += 1
        for i in range(len(filePoints)):
            for point in filePoints[i]:
                if point[2] == 0:
                    draw.ellipse(((point[0])+(w*i)-r, point[1]-r, (point[0])+(w*i)+r, point[1] + r), fill = 'blue', outline = 'blue')
                elif point[2] == 1:
                    draw.ellipse(((point[0])+(w*i)-r, point[1]-r, (point[0])+(w*i)+r, point[1] + r), fill = 'red', outline = 'red')
                else:
                    draw.ellipse(((point[0])+(w*i)-r, point[1]-r, (point[0])+(w*i)+r, point[1] + r), fill = 'green', outline = 'green')
    
    
    
        outputImage.save(os.path.join(IMG_OUT_DIR, file.replace(".csv", ".png")), "PNG")
    
    for file, count, finalTime, rate in zip(files, countingResults, finalTimes, particleRates):
        
        print(file, count, rate, finalTime)
    
    for item in os.listdir(CWD_DIR):
        if "TEMP" in item and ".txt" in item:
            os.remove(os.path.join(CWD_DIR, item))

