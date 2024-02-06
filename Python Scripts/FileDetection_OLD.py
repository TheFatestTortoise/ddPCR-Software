"""
Converts csv files to graphed png files

This uses a system of plotting smaller sections and then stitching them together
These large images are useful for tagging since it can all be done in one push
which is nice

For inference save the temp images instead of the whole images

Created on Tue Jun  6 16:08:44 2023

@author: Mason
"""
import argparse
import sys
import numpy as np
import pandas as pd

import matplotlib
from matplotlib import pyplot as plt
from matplotlib import transforms
matplotlib.use('Agg')
import os

#Setup variables
#Number of points per graph
SPLIT_NUMBER = 5000

countingResults = {}

global ROOT_DIR, TEMP_DIR, OUT_DIR

#Directories to pull and save data
#CSV location
ROOT_DIR = r"C:\Users\Mason\Desktop\flowCytometerCounter\DETECTION_DATA"
#Save temporary png files generated before stitching
TEMP_DIR = r"C:\Users\Mason\Desktop\flowCytometerCounter\DETECTION_IMAGES"

#A list of temporary file names to save each axis to
TEMP_FILE_NAMES = []
for m in range(60):
    TEMP_FILE_NAMES.append(os.path.join(TEMP_DIR, "TEMP" + str(m) + ".png"))

#Prompt user for directories if left blank, useful for sharing the code
if ROOT_DIR == "":
    ROOT_DIR = input("LOCATION OF CSV FILES: ")
if TEMP_DIR == "":
    TEMP_DIR = input("LOCATION TO SAVE TEMP FILE: ")
#The big man himself
def convert(filename):
    #Creates full dataframe from csv
    
    df = pd.read_csv(os.path.join(ROOT_DIR, filename),names = ["Time", "Amps"])
    if("--truncate" in sys.argv):
        numTruncate = int(sys.argv[sys.argv.index("--truncate") + 1])
        print("Truncating to", numTruncate)
        df = df.iloc[:numTruncate, :]
    dfSize = len(df)    
    #Splits into chunks based on SPLIT_NUMBER 
    splitDFs = []
    #Appends split dataframes to a list of the dataframes for easy access to each
    if dfSize % SPLIT_NUMBER != 0:
        numSplits = dfSize//SPLIT_NUMBER + 1
        for i in range(numSplits - 1):
            splitDFs.append(df.iloc[i*SPLIT_NUMBER:(i+1)*SPLIT_NUMBER, :])
        print("BAD ROBOT")
        splitDFs.append(df.iloc[(numSplits-1)*SPLIT_NUMBER:, :])
    else:
        numSplits = dfSize//SPLIT_NUMBER
        
        for i in range(numSplits):
            splitDFs.append(df.iloc[i*SPLIT_NUMBER:(i+1)*SPLIT_NUMBER, :])
    print(numSplits, len(splitDFs))

    previousTime = int(splitDFs[-1]['Time'].iloc[-1])

    populateRows = []
    for k in range(SPLIT_NUMBER - len(splitDFs[-1])):
        previousTime += splitDFs[-1]['Time'].diff().mean()
        populateRows.append({'Time' : previousTime, 'Amps' : 0})

    splitDFs[-1] = pd.concat([splitDFs[-1], pd.DataFrame(populateRows)])
    #Create a figure of the appropriate size for the number of graphs
    
    for l in range(numSplits):
        fig, ax = plt.subplots(figsize=(12, 6))
        #removes the margins making it easier to stitch back together
        ax.margins(x=0)

        #Turns off the axis, we don't need them and it makes it impossible to stitch together, could probably keep it in but I can't be bothered
        ax.axis('off')
        
        plt.ylim([-4.5, 4.5])
        #Plots the first dataframe Time vs Amps(amplitude in volts not current) as a black line with 0.3 size
        ax.plot(splitDFs[l].Time, splitDFs[l].Amps, 'k', linewidth = 0.3)
        fig.canvas.draw()
        #Gets the bounding box of the plot in pixels
        axBoxT = ax.get_tightbbox(renderer = fig.canvas.get_renderer())
        #Converts the bounding box to inches using the defult DPI of matplotlib
        axBox = transforms.Bbox([[axBoxT.x0/100, axBoxT.y0/100],[axBoxT.x1/100, axBoxT.y1/100]])
        #Saves the bounding box to the temp name
        fig.savefig(TEMP_FILE_NAMES[l], bbox_inches=axBox)
        #Closes the fucking plot thank god I don't have to keep doing this manually
        plt.close()

    
#Does the loop


for file in os.listdir(ROOT_DIR):
    currentFiles = os.listdir(r'C:\Users\Mason\Desktop\flowCytometerCounter\yolov5\runs\detect')
    peakCount = 0
    convert(file)
    os.chdir(r'C:\Users\Mason\Desktop\flowCytometerCounter')
    os.system(r'python yolov5\detect.py --weights yolov5\runs\train\PeakDetection-6-28-234\weights\best.pt --source C:\Users\Mason\Desktop\flowCytometerCounter\DETECTION_IMAGES --agnostic --data yolov5\data\Peak_Detection.yaml  --save-txt')
    print(set(currentFiles), set(os.listdir(r'C:\Users\Mason\Desktop\flowCytometerCounter\yolov5\runs\detect')))
    detectionOut = np.setdiff1d(os.listdir(r'C:\Users\Mason\Desktop\flowCytometerCounter\yolov5\runs\detect'), currentFiles)
    print(detectionOut)
    
    theDir = os.path.join(r'C:\Users\Mason\Desktop\flowCytometerCounter\yolov5\runs\detect', detectionOut[0], 'labels')
    
    for countingFile in os.listdir(theDir):
        with open(os.path.join(theDir, countingFile), "r") as filed:
           boxes = filed.readlines()
        open(countingFile, 'w').close()
        for box in boxes:
            peakCount += int(box[0])
    countingResults[file] = peakCount
    for image in os.listdir(TEMP_DIR):
        os.remove(os.path.join(TEMP_DIR, image))

for file, count in countingResults.items():
    print(file, count)